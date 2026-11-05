import os
import json
import shutil
import mimetypes
import hashlib
import zipfile

from enum import Enum
from pathlib import Path

PathLike = str | os.PathLike

class FileTypes(Enum):
    """Shorthand for Filetypes"""
    DIR = "directory"
    TXT = "plaintext"
    BIN = "binary"


TEXT_EXTENSIONS = frozenset({
    '.txt' , '.py'   , '.js'    , '.html'  , '.css' , '.md'        , '.json'    , '.xml'  ,
    '.yml' , '.yaml' , '.ini'   , '.cfg'   , '.log' , '.csv'       , '.sql'     , '.sh'   ,
    '.bat' , '.ps1'  , '.r'     , '.rb'    , '.php' , '.pl'        , '.go'      , '.rs'   ,
    '.kt'  , '.scala', '.clj'   , '.hs'    , '.elm' , '.dart'      , '.ts'      , '.jsx'  ,
    '.tsx' , '.vue'  , '.svelte', '.coffee', '.sass', '.scss'      , '.less'    , '.swift',
    '.styl', '.pug'  , '.jade'  , '.haml'  , '.erb' , '.handlebars', '.mustache'
})

TEXT_MIMETYPES = frozenset({
    'application/json'        , 'application/xml'        , 'application/javascript',
    'application/x-javascript', 'application/x-sh'       , 'application/x-python-code',
    'application/x-perl'      , 'application/x-ruby'     , 'application/x-php',
    'application/sql'         , 'application/x-sql'      , 'application/x-yaml',
    'application/yaml'        , 'application/x-httpd-php', 'application/x-tex',
    'application/x-latex'     , 'application/rtf'
})

_OOXML = "application/vnd.openxmlformats-officedocument"
OFFICE_MIMETYPES = {
    # Word
    ".doc" : "application/msword",
    ".dot" : "application/msword",
    ".docx": f"{_OOXML}.wordprocessingml.document",
    ".dotx": f"{_OOXML}.wordprocessingml.template",
    ".docm": "application/vnd.ms-word.document.macroEnabled.12",
    ".dotm": "application/vnd.ms-word.template.macroEnabled.12",
    # Excel
    ".xls" : "application/vnd.ms-excel",
    ".xlt" : "application/vnd.ms-excel",
    ".xlsx": f"{_OOXML}.spreadsheetml.sheet",
    ".xltx": f"{_OOXML}.spreadsheetml.template",
    ".xlsm": "application/vnd.ms-excel.sheet.macroEnabled.12",
    ".xltm": "application/vnd.ms-excel.template.macroEnabled.12",
    ".xlsb": "application/vnd.ms-excel.sheet.binary.macroEnabled.12",
    # PowerPoint
    ".ppt" : "application/vnd.ms-powerpoint",
    ".pot" : "application/vnd.ms-powerpoint",
    ".pps" : "application/vnd.ms-powerpoint",
    ".pptx": f"{_OOXML}.presentationml.presentation",
    ".potx": f"{_OOXML}.presentationml.template",
    ".ppsx": f"{_OOXML}.presentationml.slideshow",
    ".pptm": "application/vnd.ms-powerpoint.presentation.macroEnabled.12",
    ".potm": "application/vnd.ms-powerpoint.template.macroEnabled.12",
    ".ppsm": "application/vnd.ms-powerpoint.slideshow.macroEnabled.12",
    # Other
    ".msg" : "application/vnd.ms-outlook",
    ".vsd" : "application/vnd.visio",
    ".vsdx": "application/vnd.ms-visio.drawing",
}

# Top-level folder inside an OOXML zip -> (default mimetype, extensions of that family)
_OOXML_FAMILIES = {
    "word/" : (OFFICE_MIMETYPES[".docx"], {".docx", ".dotx", ".docm", ".dotm"}),
    "xl/"   : (OFFICE_MIMETYPES[".xlsx"], {".xlsx", ".xltx", ".xlsm", ".xltm", ".xlsb"}),
    "ppt/"  : (OFFICE_MIMETYPES[".pptx"], {".pptx", ".potx", ".ppsx", ".pptm", ".potm", ".ppsm"}),
    "visio/": (OFFICE_MIMETYPES[".vsdx"], {".vsdx"}),
}

# Legacy Office files share one container format (OLE2), so the extension decides
_OLE_EXTENSIONS = {".doc", ".dot", ".xls", ".xlt", ".ppt", ".pot", ".pps", ".msg", ".vsd"}

# (offset, signature, mimetype)
_MAGIC_NUMBERS = [
    (0, b"%PDF-"                   , "application/pdf"),
    (0, b"\x89PNG\r\n\x1a\n"       , "image/png"),
    (0, b"\xff\xd8\xff"            , "image/jpeg"),
    (0, b"GIF87a"                  , "image/gif"),
    (0, b"GIF89a"                  , "image/gif"),
    (0, b"II*\x00"                 , "image/tiff"),
    (0, b"MM\x00*"                 , "image/tiff"),
    (0, b"{\\rtf"                  , "application/rtf"),
    (0, b"\x1f\x8b"                , "application/gzip"),
    (0, b"7z\xbc\xaf\x27\x1c"      , "application/x-7z-compressed"),
    (0, b"Rar!\x1a\x07"            , "application/vnd.rar"),
    (0, b"SQLite format 3\x00"     , "application/vnd.sqlite3"),
    (0, b"%!PS"                    , "application/postscript"),
    (0, b"OggS"                    , "application/ogg"),
    (0, b"fLaC"                    , "audio/flac"),
    (0, b"ID3"                     , "audio/mpeg"),
    (8, b"WEBP"                    , "image/webp"),
    (8, b"WAVE"                    , "audio/wav"),
    (8, b"AVI "                    , "video/x-msvideo"),
]
_ZIP_MAGIC = b"PK\x03\x04"
_OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

# Built-in table only: the module-level functions also read the Windows registry, which differs per machine
_BUILTIN_MIMETYPES = mimetypes.MimeTypes()

# Many formats are built on these (.apk, .msi, ...), so a more specific Extension wins over them
_GENERIC_CONTAINERS = {"application/zip", "application/x-ole-storage", "application/java-archive"}


def _check_path(path: PathLike, func: str, name: str = "Path") -> None:
    if not isinstance(path, (str, os.PathLike)):
        raise TypeError(f"[FileHandler.{func}()] {name} must be a String or PathLike, got {type(path).__name__}")


def _require_file(path: PathLike, func: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(f"[FileHandler.{func}()] Path does not exist at {path}")
    if not os.path.isfile(path):
        raise IsADirectoryError(f"[FileHandler.{func}()] Path must point to a File: {path}")


class FileHandler:
    """File and Directory Manipulation"""

    #region File Manipulation
    def read(path: PathLike, encoding: str = "utf-8", mode: str = "") -> str | bytes:
        """Read and return the Contents of a File

        Args:
            path (PathLike): Path to the File
            encoding (str, optional): Encoding to Use in Text Mode, defaults to utf-8
            mode (str, optional): Mode to use. Detected via FileHandler.filetype() if empty

        Returns:
            (str | bytes): File Content

        Raises:
            FileNotFoundError: The Path does not exist
            IsADirectoryError: The Path is a Directory
        """

        _check_path(path, "read")

        if not mode:
            match FileHandler.filetype(path):
                case FileTypes.DIR: raise IsADirectoryError(f"[FileHandler.read()] Path must point to a File: {path}")
                case FileTypes.TXT: mode = "r"
                case _:             mode = "rb"

        with open(path, mode, encoding=None if "b" in mode else encoding) as file:
            return file.read()


    def read_json(path: PathLike, encoding: str = "utf-8") -> dict:
        """Read a JSON File and return the Contents

        Args:
            path (PathLike): Path to the JSON File
            encoding (str, optional): Encoding to Use, defaults to utf-8

        Returns:
            dict: JSON Contents
        """

        _check_path(path, "read_json")

        with open(path, "r", encoding=encoding) as file:
            return json.load(file)


    def write(path: PathLike, content: str | bytes, encoding: str = "utf-8") -> None:
        """Write to a File. Overwrite if it exists

        Args:
            path (PathLike): Path to the File
            content (str | bytes): Content that should be written
            encoding (str, optional): Encoding to Use for Strings, defaults to utf-8
        """

        _check_path(path, "write")
        if not isinstance(content, (str, bytes)):
            raise TypeError("[FileHandler.write()] Content must be a String or Bytes")

        if isinstance(content, str):
            with open(path, "w", encoding=encoding) as file:
                file.write(content)
        else:
            with open(path, "wb") as file:
                file.write(content)


    def write_json(path: PathLike, content: dict, encoding: str = "utf-8") -> None:
        """Write a Dictionary to a JSON File. Overwrite if it exists

        Args:
            path (PathLike): Path to the JSON File
            content (dict): Content that should be written
            encoding (str, optional): Encoding to Use, defaults to utf-8
        """

        _check_path(path, "write_json")
        if not isinstance(content, dict):
            raise TypeError("[FileHandler.write_json()] Content must be a Dictionary")

        with open(path, "w", encoding=encoding) as file:
            json.dump(content, file, indent=4)


    def append(path: PathLike, content: str | bytes, encoding: str = "utf-8") -> None:
        """(Create and) Append a given file

        Args:
            path (PathLike): Path to the File
            content (str | bytes): Content that should be written
            encoding (str, optional): Encoding to Use for Strings, defaults to utf-8
        """

        _check_path(path, "append")
        if not isinstance(content, (str, bytes)):
            raise TypeError("[FileHandler.append()] Content must be a String or Bytes")

        if isinstance(content, str):
            with open(path, "a", encoding=encoding) as file:
                file.write(content)
        else:
            with open(path, "ab") as file:
                file.write(content)


    def mkdir(path: PathLike) -> None:
        """Creates a Directory and its Parents. Does nothing if it already exists

        Args:
            path (PathLike): Path of the Directory

        Raises:
            FileExistsError: The Path exists but is not a Directory
        """

        _check_path(path, "mkdir")

        os.makedirs(path, exist_ok=True)


    def delete(path: PathLike) -> None:
        """Delete a File or Directory. Does nothing if it doesn't exist

        Args:
            path (PathLike): Path of the File or Directory
        """

        _check_path(path, "delete")

        if not os.path.exists(path):
            return
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


    def copy(source: PathLike, dest: PathLike, exist_ok: bool = False) -> None:
        """Copy a File or a Directory

        Files are copied to dest, or into it if dest is an existing Directory.
        Directories are copied so that dest becomes the copy.
        Missing parent Directories of dest are created.

        Args:
            source (PathLike): Source Path
            dest (PathLike): Destination Path
            exist_ok (bool, optional): Merge into dest if the target Directory already exists. Defaults to False.

        Raises:
            FileNotFoundError: The Source does not exist
            FileExistsError: Source is a Directory, dest exists and exist_ok is False
        """

        _check_path(source, "copy", "Source Path")
        _check_path(dest, "copy", "Destination Path")

        if not os.path.exists(source):
            raise FileNotFoundError(f"[FileHandler.copy()] Source does not exist at {source}")

        if os.path.isdir(source):
            shutil.copytree(source, dest, dirs_exist_ok=exist_ok)
        else:
            parent = os.path.dirname(dest)
            if parent:
                os.makedirs(parent, exist_ok=True)
            shutil.copy2(source, dest)


    def move(source: PathLike, dest: PathLike) -> None:
        """Move a File or Directory

        Args:
            source (PathLike): Source Path
            dest (PathLike): Destination Path
        """

        _check_path(source, "move", "Source Path")
        _check_path(dest, "move", "Destination Path")

        shutil.move(source, dest)


    def rename(source: PathLike, dest: PathLike) -> None:
        """Rename a File or Directory

        Args:
            source (PathLike): Old Name
            dest (PathLike): New Name
        """

        _check_path(source, "rename", "Source Path")
        _check_path(dest, "rename", "Destination Path")

        os.rename(source, dest)
    #endregion


    #region Metadata
    def scan(path: PathLike, recursive: bool = True, exclude_dirs: list[str] | None = None) -> list[str]:
        """Scans a Directory either only on surface or recursive

        Args:
            path (PathLike): Relative or Absolute Path to the Directory
            recursive (bool, optional): Scan Subdirectories if True. Defaults to True.
            exclude_dirs (list[str], optional): Directory names to exclude. Defaults to None.

        Returns:
            list[str]: A non sorted List of all Files in the Directory
        """

        _check_path(path, "scan")
        exclude_dirs = exclude_dirs or []

        files = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                files.append(item_path)
            elif os.path.isdir(item_path) and recursive and item not in exclude_dirs:
                files.extend(FileHandler.scan(item_path, recursive=True, exclude_dirs=exclude_dirs))

        return files


    def size(path: PathLike) -> int:
        """Returns the Filesize of a given path

        Args:
            path (PathLike): Path to the File

        Returns:
            int: Filesize in Bytes
        """

        _check_path(path, "size")
        _require_file(path, "size")

        return os.path.getsize(path)


    def isfile(path: PathLike) -> bool:
        """Checks if the given path is an existing File

        Args:
            path (PathLike): Path to the File

        Returns:
            bool: True if a File, False if a Directory or missing
        """

        _check_path(path, "isfile")

        return os.path.isfile(path)


    def verify(path: PathLike) -> bool:
        """Verify if a given path exists

        Args:
            path (PathLike): The File Path to check

        Returns:
            bool: True if the Path exists, false if not
        """

        _check_path(path, "verify")

        return os.path.exists(path)


    def filetype(path: PathLike, sniff: bool = True) -> FileTypes:
        """Check the Filetype of a given Path

        Args:
            path (PathLike): Path to the File / Directory
            sniff (bool, optional): Inspect the File Content if Extension and MIME type are inconclusive. Defaults to True.

        Returns:
            FileTypes: File Type. Either Plaintext, Binary, or Directory

        Raises:
            FileNotFoundError: The Path does not exist
        """

        _check_path(path, "filetype")

        path_obj = Path(path)
        if path_obj.is_dir():
            return FileTypes.DIR
        if not path_obj.exists():
            raise FileNotFoundError(f"[FileHandler.filetype()] Path does not exist at {path}")

        if path_obj.suffix.lower() in TEXT_EXTENSIONS:
            return FileTypes.TXT

        mime_type, _ = mimetypes.guess_type(path_obj)
        if mime_type is not None:
            if mime_type.startswith("text/") or mime_type in TEXT_MIMETYPES:
                return FileTypes.TXT
            return FileTypes.BIN

        return FileHandler._sniff_text(path_obj) if sniff else FileTypes.BIN


    def mimetype(path: PathLike, sniff: bool = True) -> str:
        """Get the MIME type of a File, e.g. to tell Word, Excel and PowerPoint Files apart

        The File Content is checked first, so renamed or extensionless Files are still recognised.
        Falls back to the Extension, then to text/plain or application/octet-stream.

        Args:
            path (PathLike): Path to the File / Directory
            sniff (bool, optional): Inspect the File Content. Only the Extension is used if False. Defaults to True.

        Returns:
            str: MIME type, e.g. "application/pdf". "inode/directory" for Directories

        Raises:
            FileNotFoundError: The Path does not exist
        """

        _check_path(path, "mimetype")

        path_obj = Path(path)
        if path_obj.is_dir():
            return "inode/directory"
        if not path_obj.exists():
            raise FileNotFoundError(f"[FileHandler.mimetype()] Path does not exist at {path}")

        suffix = path_obj.suffix.lower()
        by_extension = OFFICE_MIMETYPES.get(suffix) or _BUILTIN_MIMETYPES.guess_type(path_obj)[0]

        if sniff:
            by_content = FileHandler._sniff_mimetype(path_obj, suffix)
            if by_content in _GENERIC_CONTAINERS and by_extension and not by_extension.startswith("text/"):
                return by_extension
            if by_content:
                return by_content

        if by_extension:
            return by_extension
        if FileHandler.filetype(path_obj, sniff=sniff) is FileTypes.TXT:
            return "text/plain"
        return "application/octet-stream"


    def _sniff_mimetype(path: Path, suffix: str) -> str | None:
        """Detect the MIME type from the File's Magic Number

        Args:
            path (Path): Path to the File
            suffix (str): Lowercase File Extension, used to pick the exact type inside a Container Format

        Returns:
            str | None: MIME type, or None if the Content is not recognised
        """

        with open(path, "rb") as file:
            header = file.read(64)

        if header.startswith(_ZIP_MAGIC):
            return FileHandler._sniff_zip(path, suffix)
        if header.startswith(_OLE_MAGIC):
            return OFFICE_MIMETYPES[suffix] if suffix in _OLE_EXTENSIONS else "application/x-ole-storage"

        if header[4:8] == b"ftyp":
            brand = header[8:12]
            if brand == b"qt  ":
                return "video/quicktime"
            if brand == b"M4A ":
                return "audio/mp4"
            if brand in (b"heic", b"heix", b"mif1"):
                return "image/heic"
            return "video/mp4"

        for offset, signature, mime_type in _MAGIC_NUMBERS:
            if offset == 8 and not header.startswith(b"RIFF"):
                continue
            if header[offset:offset + len(signature)] == signature:
                return mime_type
        return None


    def _sniff_zip(path: Path, suffix: str) -> str:
        """Tell apart the Formats that are Zip Archives underneath (OOXML, OpenDocument, EPUB, JAR)

        Args:
            path (Path): Path to the Zip File
            suffix (str): Lowercase File Extension

        Returns:
            str: MIME type. application/zip if no known Format matches
        """

        try:
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                # OpenDocument and EPUB store their exact type in a "mimetype" entry
                if "mimetype" in names:
                    declared = archive.read("mimetype").decode("ascii", errors="ignore").strip()
                    if declared:
                        return declared
        except zipfile.BadZipFile:
            return "application/zip"

        if "[Content_Types].xml" in names:
            for folder, (default, extensions) in _OOXML_FAMILIES.items():
                if any(name.startswith(folder) for name in names):
                    return OFFICE_MIMETYPES[suffix] if suffix in extensions else default
        if "META-INF/MANIFEST.MF" in names:
            return "application/java-archive"
        return "application/zip"


    def _sniff_text(path: Path, blocksize: int = 8192) -> FileTypes:
        """Guess the Filetype by inspecting the first Block of the File

        Args:
            path (Path): Path to the File
            blocksize (int, optional): Number of Bytes to inspect. Defaults to 8192.

        Returns:
            FileTypes: Plaintext or Binary
        """

        with open(path, "rb") as file:
            chunk = file.read(blocksize)

        if not chunk:
            return FileTypes.TXT
        if b"\x00" in chunk:
            return FileTypes.BIN

        try:
            chunk.decode("utf-8")
        except UnicodeDecodeError as e:
            # the block may have cut a multi-byte character in half
            return FileTypes.TXT if e.start >= len(chunk) - 3 else FileTypes.BIN
        return FileTypes.TXT


    def hash(path: PathLike) -> str:
        """Returns the SHA256 Hash of a File

        Args:
            path (PathLike): Path to the file

        Returns:
            str: SHA256 hash
        """

        _check_path(path, "hash")
        _require_file(path, "hash")

        with open(path, "rb", buffering=0) as file:
            return hashlib.file_digest(file, "sha256").hexdigest()


    def stats(path: PathLike) -> dict:
        """Returns the Statistics of a File or Directory

        Parts that cannot be read (e.g. no permission, file locked by another process)
        are set to None and their error is reported in "error" instead of raising.

        Args:
            path (PathLike): Path to the File or Directory

        Returns:
            dict: Statistics of the File. "error" is None, or a dict of the failed part
                  ("stat", "type", "permissions", "sha256") to its error message

        Raises:
            FileNotFoundError: The Path does not exist
        """

        _check_path(path, "stats")
        if not os.path.exists(path):
            raise FileNotFoundError(f"[FileHandler.stats()] Path does not exist at {path}")

        errors = {}

        def attempt(part: str, func):
            try:
                return func()
            except FileNotFoundError:
                raise
            except Exception as e:
                errors[part] = f"{type(e).__name__}: {e}"
                return None

        def get_permissions() -> dict:
            # pywin32 is Windows-only, so importing it at module level would break the package elsewhere
            from .win import Windows
            return Windows.get_permissions(os.fspath(path))

        stats       = attempt("stat", lambda: os.stat(path))
        mime_type   = attempt("type", lambda: FileHandler.mimetype(path))
        permissions = attempt("permissions", get_permissions) or {}
        sha256      = attempt("sha256", lambda: FileHandler.hash(path)) if os.path.isfile(path) else None

        return {
            "type"        : mime_type,
            "size"        : stats.st_size if stats else None,
            "blocks"      : getattr(stats, "st_blocks", None),
            "device"      : stats.st_dev if stats else None,
            "inode"       : stats.st_ino if stats else None,
            "mode"        : stats.st_mode if stats else None,
            "owner"       : permissions.get("owner"       , None),
            "read"        : permissions.get("read"        , None),
            "write"       : permissions.get("write"       , None),
            "execute"     : permissions.get("execute"     , None),
            "deny_read"   : permissions.get("deny_read"   , None),
            "deny_write"  : permissions.get("deny_write"  , None),
            "deny_execute": permissions.get("deny_execute", None),
            "deny_other"  : permissions.get("deny_other"  , None),
            "no_access"   : permissions.get("no_access"   , None),
            "unsupported" : permissions.get("unsupported" , None),
            "sha256"      : sha256,
            "error"       : errors or None,
        }
    #endregion


    #region Path Manipulation
    def split(path: PathLike) -> tuple[str, str, str]:
        """Split a given Path into Directory, Filename, Extension

        Args:
            path (PathLike): Path to be split

        Returns:
            tuple[str, str, str]: Directory, Filename, Extension. Either part may be Empty
        """

        _check_path(path, "split")

        directory, file = os.path.split(os.fspath(path))
        filename, extension = os.path.splitext(file)

        return directory, filename, extension


    def dirpath(path: PathLike) -> str:
        """Split a given Path and Return the Directory

        Args:
            path (PathLike): Path to be split

        Returns:
            str: Directory Path. May be Empty
        """

        _check_path(path, "dirpath")

        directory, _, _ = FileHandler.split(path)
        return directory


    def filename(path: PathLike) -> str:
        """Split a given Path and Return the Filename

        Args:
            path (PathLike): Path to be split

        Returns:
            str: Filename. May be Empty
        """

        _check_path(path, "filename")

        _, filename, _ = FileHandler.split(path)
        return filename


    def extension(path: PathLike) -> str:
        """Split a given Path and Return the File Extension

        Args:
            path (PathLike): Path to be split

        Returns:
            str: Extension. May be Empty
        """

        _check_path(path, "extension")

        _, _, extension = FileHandler.split(path)
        return extension


    def join(elements: list[PathLike]) -> str:
        """Merge a List of Path-parts into a single Path

        Args:
            elements (list[PathLike]): List of Path-parts that should be Merged

        Returns:
            str: Merged File Path
        """

        if not isinstance(elements, list) or not elements:
            raise TypeError("[FileHandler.join()] Elements must be a non-empty List")
        for element in elements:
            _check_path(element, "join", "Element")

        return os.path.join(*elements)


    def abspath(path: PathLike) -> str:
        """Returns the Absolute Path

        Args:
            path (PathLike): Relative Path

        Returns:
            str: Absolute Path
        """

        _check_path(path, "abspath")

        return os.path.abspath(path)
    #endregion
