from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.theme import Theme

from helper import Logo

class TUI:
    def __init__(self, console: Console = Console()):
        self.console = console
        self.layout = Layout()
        self.theme = Theme()
        self.text = Text()
        self.panel = Panel()

    def intro(self):
        self.console.print(Panel(Logo.print(console=self.console), title="Helper", border_style="bold blue"))
