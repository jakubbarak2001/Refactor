"""Define most important stats for JB."""
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

class JBStats:
    """Creates stats for JB."""
    def __init__(self, available_money=0, coding_experience=0, pcr_hatred=0):
        """
        Initialises all important resources that matter for the gaming mechanics.
        Initialise the loose game conditions based on amount of those resources.
        """
        self.available_money = available_money
        self.coding_experience = coding_experience
        self.pcr_hatred = pcr_hatred
        self.daily_btc_income = 0
        self.ai_paperwork_buff = False

    def stats_description_money(self):
        """Stats description message, describing the value of available money stat in plain language."""
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
        for limit, description in money_levels:
            if self.available_money >= limit:
                return description
        return "YOU HAVE NO MONEY LEFT."

    def stats_description_coding_experience(self):
        """Stats description message, describing the value of coding experience stat in plain language."""
        coding_levels = [
            (250, "S̵̟͚̐͘Č̸͕͌H̵̙̕I̸̟̐Z̷̮̈́O̶̝̐.̷͈̐ R̷E̷A̷L̷I̷T̷Y̷ ̷I̷S̷ ̷C̷O̷D̷E̷.̷ ̷I̷ ̷A̷M̷ ̷T̷H̷E̷ ̷C̷O̷M̷P̷I̷L̷E̷R̷.̷ ̷0̷1̷0̷1̷0̷1̷"),
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
            if self.coding_experience > limit:
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
        """Input command for getting current stats using Rich Table."""

        # Create a table
        table = Table(title="[bold underline]CURRENT STATUS[/bold underline]", box=box.ROUNDED, show_lines=True)

        # FIX: Explicit width for Icon column fixes alignment
        table.add_column("Icon", justify="center", width=4)
        table.add_column("Stat Name", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta", justify="right")
        # FIX: Allow description to wrap naturally
        table.add_column("Status Description", style="green", overflow="fold")

        # Add Money Row
        table.add_row(
            "💰",
            "Money",
            f"[bold green]{self.available_money} CZK[/bold green]",
            self.stats_description_money()
        )

        # Add Coding Row
        table.add_row(
            "💻",
            "Coding Skill",
            f"[bold blue]{self.coding_experience}[/bold blue]",
            self.stats_description_coding_experience()
        )

        # Add Hatred Row
        hatred_style = "bold red" if self.pcr_hatred > 70 else "white"
        table.add_row(
            "🤬",
            "Police Hatred",
            f"[{hatred_style}]{self.pcr_hatred}%[/{hatred_style}]",
            self.stats_description_police_hatred()
        )

        print()
        console.print(table)

    # --- Setters and Incrementers (Kept same as before) ---
    def change_stats_value_money(self, set_money_value):
        self.available_money = set_money_value

    def change_stats_coding_skill(self, set_coding_skill_value):
        self.coding_experience= set_coding_skill_value

    def change_stats_pcr_hatred(self, set_pcr_hatred):
        self.pcr_hatred = set_pcr_hatred

    def increment_stats_value_money(self, increment_money_value):
        self.available_money += increment_money_value

    def increment_stats_coding_skill(self, increment_coding_skill_value):
        self.coding_experience += increment_coding_skill_value

    def try_spend_money(self, amount: int) -> bool:
        if self.available_money >= amount:
            self.increment_stats_value_money(-amount)
            return True
        return False

    def increment_stats_pcr_hatred(self, increment_pcr_hatred):
        self.pcr_hatred += increment_pcr_hatred