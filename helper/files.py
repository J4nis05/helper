import os
import shutil
import mimetypes
import hashlib

from enum import Enum
from pathlib import Path


class FileTypes(Enum):
    """Shorthand for Filetypes"""
    DIR = "directory"
    TXT = "plaintext"
    BIN = "binary"
    NON = None


class FileHandler:
    """File and Directory Manipulation"""

    #region File Manipulation
    def read(path: str, encoding: str = "utf-8", mode: str = "") -> str | bytes:
        """Read and return the Contents of a File

        Args:
            path (str): Path to the File
            encoding (str, optional): Encoding to Use, defaults to utf-8
            mode (str, optional): Mode to use, defaults to None

        Returns:
            (str | bytes): File Content
        """
        
        assert type(path) == str, "[FileHandler.read()] Path must be a String"

        if not FileHandler.verify(path):
            print(f"WARNING: File does not exist at path {path}")
            return ""

        open_kwargs = {}
        if not mode:
            match FileHandler.filetype(path):
                case FileTypes.TXT: read_mode = "r"; open_kwargs = {"encoding": encoding}
                case FileTypes.BIN: read_mode = "rb"
                case FileTypes.DIR: return ""
        elif mode == "r":
            read_mode = "r"
            open_kwargs = {"encoding": encoding}
        else:
            read_mode = mode

        with open(path, read_mode, **open_kwargs) as file:
            content = file.read()

        return content


    def write(path: str, content: str | bytes, encoding: str = "utf-8") -> bool:
        """Write to a File. Overwrite if it exists

        Args:
            path (str): Path to the File
            content (str | bytes): Content that should be written
            encoding (str, optional): Encoding to Use, defaults to utf-8

        Returns:
            bool: True if Action was successful
        """

        assert type(path) == str, "[FileHandler.write()] Path must be a String"
        assert isinstance(content, (str, bytes)), "[FileHandler.write()] Content must be a String or Bytes"

        open_kwargs = {}
        if type(content) is str:
            write_mode = "w"
            open_kwargs = {"encoding": encoding}
        else:
            write_mode = "wb"

        try:
            with open(path, write_mode, **open_kwargs) as file:
                file.write(content)
        except Exception as e:
            print(f"[FileHandler.write()] Action Failed with Error:\n{e}")
            return False

        return True


    def append(path: str, content: str | bytes, encoding: str = "utf-8") -> bool:
        """(Create and) Append a given file

        Args:
            path (str): Path to the File
            content (str | bytes): Content that should be written
            encoding (str, optional): Encoding to Use, defaults to utf-8

        Returns:
            bool: True if Action was successful
        """

        assert type(path) == str, "[FileHandler.append()] Path must be a String"
        assert isinstance(content, (str, bytes)), "[FileHandler.append()] Content must be a String or Bytes"
        
        open_kwargs = {}
        if type(content) is str:
            append_mode = "a"
            open_kwargs = {"encoding": encoding}
        else:
            append_mode = "ab"

        try:
            with open(path, append_mode, **open_kwargs) as file:
                file.write(content)
        except Exception as e:
            print(f"[FileHandler.append()] Action Failed with Error:\n{e}")
            return False

        return True


    def mkdir(path: str) -> bool:
        """Creates a Directory if it doesn't exist

        Args:
            path (str): Path of the directory

        Returns:
            bool: False if the Creation Failed or the Directory exists
        """

        assert type(path) == str, "[FileHandler.mkdir()] Path must be a String"

        if FileHandler.verify(path): return False
        try:
            os.makedirs(path)
        except Exception as e:
            print(f"[FileHandler.mkdir()] Action Failed with Error:\n{e}")
            return False
        return True


    def delete(path: str) -> bool:
        """Attempts to delete a given Path

        Args:
            path (str): Path of the directory

        Returns:
            bool: False if the Creation Failed or the Directory exists
        """

        assert type(path) == str, "[FileHandler.delete()] Path must be a String"
        if not FileHandler.verify(path): return True

        try:
            match FileHandler.filetype(path):
                case FileTypes.DIR:
                    shutil.rmtree(path)
                case _:
                    Path.unlink(path)
        except Exception as e:
            print(f"[FileHandler.delete()] Action Failed with Error:\n{e}")
            return False

        return True


    def copy(source: str, dest: str, exist_ok: bool = False) -> bool:
        """Copy a File or a Directory

        Args:
            source (str): Soure Path
            dest (str): Destination Path
            exist_ok (bool, optional): Do not error if target Directory Exists

        Returns:
            bool: True if the Copy worked, False if not
        """

        assert type(source) == str, "[FileHandler.mkdir()] Source Path must be a String"
        assert type(dest) == str, "[FileHandler.mkdir()] Destination Path must be a String"
        
        if not FileHandler.verify(source): return False
        if not FileHandler.verify(dest): FileHandler.mkdir(dest)

        try:
            match FileHandler.filetype(source):
                case FileTypes.DIR:
                    shutil.copytree(source, dest, dirs_exist_ok=exist_ok)
                case _:
                    shutil.copy2(source, dest)
        except Exception as e:
            print(f"[FileHandler.copy()] Action Failed with Error:\n{e}")
            return False

        return True


    def move(source: str, dest: str) -> bool:
        """Move a File or Directory

        Args:
            source (str): Source Path
            dest (str): Destination Path

        Returns:
            bool: True if successful
        """
        
        assert type(source) == str, "[FileHandler.move()] Source Path must be a String"
        assert type(dest) == str, "[FileHandler.move()] Destination Path must be a String"
        
        try:
            shutil.move(source, dest)
        except Exception as e:
            print(f"[FileHandler.move()] Action Failed with Error:\n{e}")
            return False
        
        return True


    def rename(source: str, dest: str) -> bool:
        """Rename a File or directory

        Args:
            source (str): Old Name
            dest (str): New Name

        Returns:
            bool: True if successful
        """

        assert type(source) == str, "[FileHandler.rename()] Source Path must be a String"
        assert type(dest) == str, "[FileHandler.rename()] Destination Path must be a String"

        try:
            os.rename(source, dest)
        except Exception as e:
            print(f"[FileHandler.rename()] Action Failed with Error:\n{e}")
            return False

        return True
    #endregion


    #region Metadata
    def scan(path: str, recursive: bool = True, exclude_dirs: list = []) -> list:
        """Scans a Directory either only on surface or recursive

        Args:
            path (str): Relative or Absolute Path to the Directory
            recursive (bool, optional): Scan Subdirectories if True. Defaults to True.
            exclude_dirs (list, optional): List of directory names to exclude. Defaults to None.

        Returns:
            list: A non sorted List of all items in the directory
        """

        assert type(path) == str, "[FileHandler.scan()] Path must be a String"
        
        files = []
        all_items = os.listdir(path)

        for item in all_items:
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                files.append(item_path)
            elif os.path.isdir(item_path) and recursive:
                # Check if this directory should be excluded
                if item not in exclude_dirs:
                    files.extend(FileHandler.scan(item_path, recursive=True, exclude_dirs=exclude_dirs))

        return files


    def size(path: str) -> int:
        """Returns the Filesize of a given path

        Args:
            path (str): Path to the File

        Returns:
            int: Filesize
        """
        
        assert type(path) == str, "[FileHandler.size()] Path must be a String"
        assert FileHandler.isfile(path), "[FileHandler.size()] Path must point to a File"

        return os.path.getsize(path)


    def isfile(path: str) -> bool:
        """Checks if the given path is a File

        Args:
            path (str): Path to the File

        Returns:
            bool: True if a File, False if a Directory
        """

        assert type(path) == str, "[FileHandler.isfile()] Path must be a String"

        allowed = [FileTypes.BIN, FileTypes.TXT]
        if FileHandler.filetype(path) in allowed:
            if os.path.isdir(path): TypeError("[FileHandler.isfile()] Mismatch!!! Thought it was a File, but is actually a Dir")
            return True
        
        return False


    def verify(path: str) -> bool:
        """Verify if a given path exists

        Args:
            path (str): The File Path to check

        Returns:
            bool: True if the Path exists, false if not
        """

        assert type(path) == str, "[FileHandler.verify()] Path must be a String"

        if os.path.exists(path):
            return True
        
        return False


    def filetype(path: str) -> FileTypes:
        """Check the Filetype of a given Path

        Args:
            path (str): Path to the File / Directory

        Returns:
            FileTypes: File Type. Either Plaintext, Binary, or Directory
        """

        assert type(path) == str, "[FileHandler.filetype()] Path must be a String"
        assert FileHandler.verify(path), f"[FileHandler.filetype()] Path does not exist at {path}"

        text_extensions = [
            '.txt' , '.py'   , '.js'    , '.html'  , '.css' , '.md'        , '.json'    , '.xml'  ,
            '.yml' , '.yaml' , '.ini'   , '.cfg'   , '.log' , '.csv'       , '.sql'     , '.sh'   ,
            '.bat' , '.ps1'  , '.r'     , '.rb'    , '.php' , '.pl'        , '.go'      , '.rs'   ,
            '.kt'  , '.scala', '.clj'   , '.hs'    , '.elm' , '.dart'      , '.ts'      , '.jsx'  ,
            '.tsx' , '.vue'  , '.svelte', '.coffee', '.sass', '.scss'      , '.less'    , '.swift',
            '.styl', '.pug'  , '.jade'  , '.haml'  , '.erb' , '.handlebars', '.mustache'
        ]
        text_mimetypes = [
            'application/json'        , 'application/xml'        , 'application/javascript',
            'application/x-javascript', 'application/x-sh'       , 'application/x-python-code',
            'application/x-perl'      , 'application/x-ruby'     , 'application/x-php',
            'application/sql'         , 'application/x-sql'      , 'application/x-yaml',
            'application/yaml'        , 'application/x-httpd-php', 'application/x-tex',
            'application/x-latex'     , 'application/rtf'
        ]

        path_obj = Path(path)
        file_type = FileTypes.NON
        found = False

        mime_type, mime_encoding = mimetypes.guess_type(path)

        # Is the Path a Directory?
        if path_obj.is_dir():
            file_type = FileTypes.DIR
            found = True

        # No MIME type found, try to find based on extension
        if mime_type is None and not found:
            if path_obj.suffix.lower() in text_extensions:
                file_type = FileTypes.TXT
                found = True
            else:
                file_type = FileTypes.BIN
                found = True

        # Check if it's a text-based MIME type
        #if file_type is FileTypes.NON and mime_type.startswith('text/') or mime_type in text_mimetypes and not found:
        if (
                file_type is FileTypes.NON
                and mime_type is not None
                and (mime_type.startswith("text/") or mime_type in text_mimetypes)
                and not found
        ):
            file_type = FileTypes.TXT
            found = True

        # If nothing else has been caught, set it to BIN
        if file_type is FileTypes.NON and not found:
            file_type = FileTypes.BIN

        return file_type
    
    
    def hash(path: str) -> str:
        """Returns the SHA256 Hash of a File

        Args:
            path (str): Path to the file

        Returns:
            str: SHA256 hash
        """

        assert type(path) == str, "[FileHandler.hash()] Path must be a String"
        assert FileHandler.isfile(path), "[FileHandler.hash()] Path must point to a File"

        with open(path, "rb", buffering=0) as file:
            hash = hashlib.file_digest(file, "sha256").hexdigest()
        return hash
    #endregion


    #region Path Manipulation
    def split(path: str) -> tuple[str, str, str]:
        """Split a given Path into Directory, Filename, Extension

        Args:
            path (str): Path to be split

        Returns:
            tuple[str, str, str]: Directory, Filename, Extension. Either part may be Empty
        """

        assert type(path) == str, "[FileHandler.split()] Path must be a String"

        directory, file = os.path.split(path)
        filename, extension = os.path.splitext(file)

        return directory, filename, extension


    def dirpath(path: str) -> str:
        """Split a given Path and Return the Directory

        Args:
            path (str): Path to be split

        Returns:
            str: Directory Path. May be Empty
        """

        assert type(path) == str, "[FileHandler.dirpath()] Path must be a String"
        
        directory, _, _ = FileHandler.split(path)
        return directory


    def filename(path: str) -> str:
        """Split a given Path and Return the Filename

        Args:
            path (str): Path to be split

        Returns:
            str: Filename. May be Empty
        """

        assert type(path) == str, "[FileHandler.filename()] Path must be a String"
        
        _, filename, _ = FileHandler.split(path)
        return filename


    def extension(path: str) -> str:
        """Split a given Path and Return the File Extension

        Args:
            path (str): Path to be split

        Returns:
            str: Extension. May be Empty
        """

        assert type(path) == str, "[FileHandler.extension()] Path must be a String"
        
        _, _, extension = FileHandler.split(path)
        return extension


    def join(elements: list[str]) -> str:
        """Merge a List of Strings into a single Path

        Args:
            elements (list[str]): List of Path-parts that should be Merged

        Returns:
            str: Merged File Path
        """

        assert isinstance(elements, list) and all(isinstance(item, str) for item in elements), "[FileHandler.join()] Elements Must be a List of Strings"
        return os.path.join(*elements)


    def abspath(path: str):
        """Returns the Absolute Path

        Args:
            path (str): Relative Path

        Returns:
            str: Absolute Path
        """

        assert type(path) == str, "[FileHandler.abspath()] Path must be a String"

        return os.path.abspath(path)
    #endregion
