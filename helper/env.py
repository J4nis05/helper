from helper import Util, FileHandler

class Dotenv:
    """Environment variable file parser."""
    
    def __init__(self, path: str = ".env"):
        """Initialize Dotenv with path to environment file."""
        self.path = path
        self.separator = "="
        self.comments = ["//", "#"]
        self.content = self.read_env()
        self.env = self.parse_env()
    
    def read_env(self) -> str:
        """Read environment file and return raw content. Empty if the file is missing."""
        try:
            return FileHandler.read(self.path, encoding="utf-8-sig", mode="r")
        except FileNotFoundError:
            print(f"WARNING: File does not exist at path {self.path}")
            return ""
    
    def parse_env(self) -> dict:
        """Parse environment file content into a dictionary.

        Whitespace around keys and values is ignored. Values wrapped in matching
        single or double quotes are unquoted, keeping whitespace inside the quotes.
        """
        parsed = {}

        for line in self.content.splitlines():
            line = line.strip()
            if line == "" or Util.starts_with_any(line, self.comments):
                continue

            key, separator, value = line.partition(self.separator)
            key, value = key.strip(), value.strip()
            if not separator or not key:
                continue

            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            parsed[key] = value

        return parsed
    
    def get(self, key: str) -> str | None:
        """Get value for the given key."""
        return self.env.get(key, None)

    def refresh(self):
        """Reload and reparse the environment file."""
        self.content = self.read_env()
        self.env = self.parse_env()
