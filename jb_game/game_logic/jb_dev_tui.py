# jb_game/game_logic/jb_dev_tui.py

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box  # Import box styles

# Initialize Console
console = Console()


class GameInterface:
    def __init__(self):
        self.layout = Layout()
        self.setup_layout()

    def setup_layout(self):
        """Defines the grid structure."""
        # Split into Header (Top), Body (Middle), Footer (Bottom)
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )

        # Split Body: Main Content (Ratio) vs Sidebar (Fixed Size for stability)
        self.layout["body"].split_row(
            Layout(name="main", ratio=2),
            Layout(name="sidebar", size=45)
        )

    def update_header(self, day, location="Police Station"):
        """Updates the top bar."""
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            f"[bold magenta]REFACTOR[/bold magenta] | [dim]{location}[/dim]",
            f"[bold cyan]Day {day}/30[/bold cyan]"
        )
        # Use box.SQUARE or box.ASCII if ROUNDED looks broken in your terminal
        self.layout["header"].update(Panel(grid, style="white on blue", box=box.SQUARE))

    def update_stats(self, money, coding, hatred):
        """Updates the sidebar. NOW CLEANER (No nested panels)."""

        # Create the table acting as the main container
        stats_table = Table(
            title="[bold underline]STATUS[/bold underline]",
            expand=True,
            box=box.ROUNDED,  # Change to box.ASCII if you see dashed lines
            border_style="cyan"
        )

        # Define columns with fixed widths to prevent jumping
        stats_table.add_column("Icon", justify="center", width=4)
        stats_table.add_column("Stat", style="cyan")
        stats_table.add_column("Value", justify="right", style="magenta")

        # Logic for Hatred Color
        hatred_color = "red" if hatred > 50 else "green"

        # Add Rows
        stats_table.add_row("💰", "Money", f"{money} CZK")
        stats_table.add_row("💻", "Code", f"{coding} XP")
        stats_table.add_row("🤬", "Hatred", f"[{hatred_color}]{hatred}%[/{hatred_color}]")

        # Add a spacer row
        stats_table.add_row("", "", "")

        # Add Buffs Section (Placeholder for future)
        stats_table.add_row("⚡", "Buffs", "[dim]None[/dim]")

        # Update the layout directly with the table (No extra Panel wrapper)
        self.layout["sidebar"].update(stats_table)

    def update_main_content(self, text_content):
        """Updates the main story area."""
        self.layout["main"].update(
            Panel(
                text_content,
                title="[bold]CURRENT EVENT[/bold]",
                border_style="green",
                padding=(1, 2)  # Add padding for readability
            )
        )

    def update_footer(self, prompt="Waiting for command..."):
        """Updates the bottom input area."""
        self.layout["footer"].update(
            Panel(Text(f"> {prompt}", style="bold blink white"), border_style="white", box=box.SQUARE)
        )

    def render(self):
        """Prints the layout."""
        console.clear()
        console.print(self.layout)