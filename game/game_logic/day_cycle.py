"""A simple day calculator, accessible from main menu."""


class DayCycle:
    """Creates day counter, accessible from Game class's menu method."""
    def __init__(self, current_day = 1):
        """Initialises itself, starting from day 1"""
        self.current_day = current_day

    def report_current_day(self):
        """Tells what day is it in neat format."""
        print(self.current_day)

    def next_day(self):
        """Skips to the next day."""
        self.current_day += 1

    def day_start_message(self):
        """Prints message about starting a new day."""
        yellow = "\033[93m"
        reset = "\033[0m"
        print(f"\n{yellow}Starting day #{self.current_day}/30{reset}")

    def day_end_message(self):
        """Prints message about ending the current day."""
        yellow = "\033[93m"
        reset = "\033[0m"
        print(f"\n{yellow}Ending day #{self.current_day}/30{reset}")