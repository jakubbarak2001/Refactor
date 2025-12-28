"""Define most important stats for JB."""
import sys
from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

# Use a consistent console instance
_stats_console = Console(force_terminal=True)
class Stats:
    """Creates stats for JB."""
    def __init__(self, available_money=0, coding_experience=0, pcr_hatred=0):
        """
        Initialises all important resources that matter for the gaming mechanics.
        Initialise the loose game conditions based on amount of those resources.
        """
        self.available_money = available_money
        self.coding_skill = coding_experience
        self.pcr_hatred = pcr_hatred
        self.daily_btc_income = 0
        self.ai_paperwork_buff = False
        self.colonel_day = 30
        self.final_boss_buff = None
        self.difficulty = None  # Stores selected difficulty: "easy", "hard", "insane"

    def try_spend_money(self, amount: int) -> bool:
        """
        Attempts to spend a specific amount of money.
        Returns True if successful (money deducted).
        Returns False if insufficient funds (no money deducted).
        """
        if self.available_money >= amount:
            self.increment_stats_value_money(-amount)
            return True
        else:
            return False

    def stats_description_money(self):
        """Stats description message, describing the value of available money stat in plain language."""
        # DATA: The thresholds and their corresponding messages
        money_levels = [
            (1000000, "YOU ARE A MILLIONAIRE! Why are you still working at the police?!"),
            (500000, "Half a million... you could actually buy a small garage in your city now."),
            (200000, "Your reserves are INSANE! You feel safer than you ever did carrying a gun."),
            (150000, "This is serious money. You breathe a little easier knowing you have this cushion."),
            (100000, "If you don't spend unwisely, you can survive for months without a salary."),
            (85000, "You have a solid financial foundation. Not rich, but not desperate."),
            (65000, "You have some savings, but a broken car or a lawyer could wipe it out."),
            (45000, "You are treading water. One big expense and you are in trouble."),
            (30000, "Your situation is getting tense. You're calculating the price of cheese in the supermarket."),
            (20000, "You are running out of money! The stress is starting to affect your sleep."),
            (10000, "DANGER ZONE. You have enough for rent, but not much else."),
            (5000, "SOON YOU WILL HAVE NO MONEY LEFT! Instant noodles are your new best friend."),
            (1000, "You are basically broke. You check your pockets for loose change."),
            (0, "YOU HAVE NO MONEY LEFT. You are one crisis away from homelessness."),
        ]

        # LOGIC: Iterate through the list to find the first match
        for limit, description in money_levels:
            if self.available_money >= limit:
                return description

        # Fallback for anything <= 0 (since the loop checks > 0)
        return "YOU HAVE NO MONEY LEFT."

    def stats_description_coding_experience(self):
        """Stats description message, describing the value of coding experience stat in plain language."""
        # DATA: The thresholds and their corresponding messages
        coding_levels = [
            (250,
             "S̵̟͚̐͘Č̸͕͌H̵̙̕I̸̟̐Z̷̮̈́O̶̝̐.̷͈̐ R̷E̷A̷L̷I̷T̷Y̷ ̷I̷S̷ ̷C̷O̷D̷E̷.̷ ̷I̷ ̷A̷M̷ ̷T̷H̷E̷ ̷C̷O̷M̷P̷I̷L̷E̷R̷.̷ ̷0̷1̷0̷1̷0̷1̷"),
            (225, "SINGULARITY. You no longer type. You stare at the screen and the code writes itself."),
            (200, "GOD TIER. You see the Matrix. You don't write code, you manifest logic."),
            (175, "Principal Engineer. You spend more time drawing boxes on whiteboards than typing."),
            (150, "Senior Developer. You delete more code than you write, and the system runs faster."),
            (125, "Medior Developer. You can build entire systems from scratch without tutorials."),
            (100, "HIREABLE (Junior Dev). You know enough to get paid. Escape is finally possible!"),
            (85, "Competent. You understand OOP, APIs, and databases. You are dangerous."),
            (65, "Advanced Learner. You can make simple websites and text games without crashing."),
            (45, "Intermediate. You finally understand what 'self' actually means."),
            (30, "Beginner. You spend 90% of your time debugging syntax errors."),
            (15, "Script Kiddie. You copy-paste from Stack Overflow and pray it works."),
            (5, "Hello World. You made the computer print text. You feel like a hacker."),
            (0, "Non-Existent. You think 'Python' is just a snake in the zoo."),
        ]

        for limit, description in coding_levels:
            if self.coding_skill > limit:
                return description

        return "You are just starting. Ideally, keep the computer turned on."

    def stats_description_police_hatred(self):
        """Stats description message, describing the value of police hatred stat in plain language."""
        hatred_levels = [
            (95, "PSYCHOTIC BREAK. HAHAHAHDAHHAHAHAHA! The siren sounds like music! The paperwork is confetti!"),
            (85, "CRITICAL MASS. You are physically shaking. One more stupid order and you will scream."),
            (75, "TOXIC. You look at civilians and wonder if they know how good they have it. You hate them for it."),
            (65, "BURNOUT. You don't patrol anymore; you just drive aimlessly to avoid the radio."),
            (50, "HOLLOW. The coffee tastes like bureaucracy and despair. You are only here for the money."),
            (40, "RESENTMENT. You stopped polishing your boots weeks ago. Why bother?"),
            (25, "The cracks are showing. You check the time every 5 minutes hoping the shift is over."),
            (15, "Skepticism. You realize the 'Protect and Serve' motto is mostly just branding."),
            (5, "Routine. There are things you dislike, but overall, it's a stable job."),
            (0, "FRESH MEAT. You love your job! You are going to save the world! (You fool)."),
        ]

        for limit, description in hatred_levels:
            if self.pcr_hatred > limit:
                return description

        return "You are suspiciously happy. Are you sure you work here?"
    def get_stats_command(self):
        """Display current stats of the main character in a beautiful Rich TUI panel."""
        # Flush stdout to ensure clean separation
        sys.stdout.flush()
        
        # Get descriptions
        money_desc = Stats.stats_description_money(self)
        coding_desc = Stats.stats_description_coding_experience(self)
        hatred_desc = Stats.stats_description_police_hatred(self)
        
        # Determine colors for descriptions
        if self.available_money >= 150000:
            money_color = "bright_green"
        elif self.available_money >= 50000:
            money_color = "white"
        elif self.available_money >= 20000:
            money_color = "yellow"
        else:
            money_color = "bright_red"
        
        if self.coding_skill >= 100:
            coding_color = "bright_green"
        elif self.coding_skill >= 50:
            coding_color = "green"
        elif self.coding_skill >= 20:
            coding_color = "yellow"
        else:
            coding_color = "dim white"
        
        if self.pcr_hatred >= 75:
            hatred_color = "bold bright_red"
        elif self.pcr_hatred >= 50:
            hatred_color = "bright_red"
        elif self.pcr_hatred >= 25:
            hatred_color = "yellow"
        else:
            hatred_color = "dim white"
        
        # Build content as Rich markup string - ensure clean content
        content = (
            f"[bold yellow]💰[/bold yellow] [bold cyan]Money:[/bold cyan] "
            f"[bold bright_white]{self.available_money:,} CZK[/bold bright_white]\n"
            f"   [{money_color}]{money_desc}[/{money_color}]\n\n"
            f"[bold blue]💻[/bold blue] [bold cyan]Coding Skill:[/bold cyan] "
            f"[bold bright_white]{self.coding_skill}[/bold bright_white]\n"
            f"   [{coding_color}]{coding_desc}[/{coding_color}]\n\n"
            f"[bold red]😡[/bold red] [bold cyan]Police Hatred:[/bold cyan] "
            f"[bold bright_white]{self.pcr_hatred}/100[/bold bright_white]\n"
            f"   [{hatred_color}]{hatred_desc}[/{hatred_color}]"
        )
        
        # Use console.print for consistent rendering
        _stats_console.print()  # Empty line before panel
        _stats_console.print(Panel(
            content,
            border_style="bold cyan",
            title="[bold white on cyan] > STATS < [/]",
            padding=(1, 3),
            expand=False
        ))
        _stats_console.print()  # Empty line after panel

    def change_stats_value_money(self, set_money_value):
        """Change the value of stats available money to different number."""
        self.available_money = set_money_value

    def change_stats_coding_skill(self, set_coding_skill_value):
        """Change the value of stats coding skill to different number."""
        self.coding_skill= set_coding_skill_value

    def change_stats_pcr_hatred(self, set_pcr_hatred):
        """Change the value of stats pcr hatred to different number."""
        self.pcr_hatred = set_pcr_hatred
        if self.pcr_hatred <= 0:
            self.pcr_hatred = 0
            print("Your hatred cannot be lower than 0!")

    def increment_stats_value_money(self, increment_money_value):
        """Change the value of stats available money to different number."""
        self.available_money += increment_money_value

    def increment_stats_coding_skill(self, increment_coding_skill_value):
        """Change the value of stats coding skill to different number."""
        self.coding_skill += increment_coding_skill_value

    def increment_stats_pcr_hatred(self, increment_pcr_hatred):
        """Change the value of stats pcr hatred to different number."""
        self.pcr_hatred += increment_pcr_hatred