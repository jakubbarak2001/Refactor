class Decision:
    """Helper class for handling user input and decisions."""

    @staticmethod
    def ask(options: tuple) -> str:
        """
        Prompts the user until they enter a valid option from the provided tuple.
        Returns the valid choice as a string.
        """
        while True:
            choice = input("> ").strip()
            if choice in options:
                return choice

            print(f"Invalid choice. Please enter one of: {', '.join(options)}")