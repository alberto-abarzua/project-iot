from rich import print
from rich.theme import Theme
from rich.console import Console
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "light_info": "dim white",
})
console = Console(theme = custom_theme)