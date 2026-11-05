from rich.console import Console
from rich.theme import Theme

class Logger:
    def __init__(self, console: Console):
        self.console = console
        self.theme = Theme({
            "error"  : "bold red",
            "warning": "magenta",
            "info"   : "cyan",
            "debug"  : "dim"
        })
        self.console.push_theme(self.theme)
        # We'll map level aliases to style names as lowercase for markup tags.
        self.level_map = {
            "error": "error",
            "ERR": "error",
            "ERROR": "error",

            "warning": "warning",
            "WARN": "warning",
            "WARNING": "warning",

            "info": "info",
            "INFO": "info",

            "debug": "debug",
            "DEBUG": "debug"
        }

    def log(self, level: str = "info", message: str = ""):
        style = self.level_map.get(level, "info")
        self.console.log(f"[{style}]{message}[/{style}]")

    def error(self, message: str):
        self.log("error", message)

    def warning(self, message: str):
        self.log("warning", message)

    def info(self, message: str):
        self.log("info", message)

    def debug(self, message: str):
        self.log("debug", message)
