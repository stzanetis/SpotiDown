from rich.console import Console

console = Console()

# Signal handler for keyboard interrupt
def signal_handler(sig, frame):
    console.print("\n[bold red]Process terminated by user. Exiting...[/bold red]")
    exit(0)
