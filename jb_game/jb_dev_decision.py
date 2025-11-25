class Decision:
    """Ruleset for efficient decision selection."""
    def __init__(self, decision_variable_name, decision_viable_options):
        """Initialise itself for keeping your choices throughout the game."""
        self.decision_variable_name = decision_variable_name
        self.viable_options = decision_viable_options

    def create_decision(self):
        """Creates the option to choose different paths in your decision branches."""
        while True:
            self.decision_variable_name = input("> ").strip()
            if self.decision_variable_name in self.viable_options:
                break
            print(f"Invalid choice. Please enter one of: {self.viable_options}.")
