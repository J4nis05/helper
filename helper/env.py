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
        """Read environment file and return raw content."""
        return FileHandler.read(self.path, mode="r")
    
    def parse_env(self) -> dict:
        """Parse environment file content into a dictionary."""
        parsed = {}
        lines = self.content.split("\n")
        
        for line in lines:
            if Util.starts_with_any(line, self.comments) or line == "":
                continue
            items = line.split(self.separator, 1)
            if len(items) == 2:
                parsed[items[0]] = items[1]

        return parsed
    
    def get(self, key: str) -> str | None:
        """Get value for the given key."""
        return self.env.get(key, None)

    def refresh(self):
        """Reload and reparse the environment file."""
        self.content = self.read_env()
        self.env = self.parse_env()
