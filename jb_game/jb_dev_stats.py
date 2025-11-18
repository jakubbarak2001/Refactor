"""Define most important stats for JB."""
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


    def stats_description_money(self):
        """Stats description message, describing the value of available money stat in plain language."""
        current_money_status = None

        if self.available_money > 200000:
            current_money_status = "Your reserves are INSANE! How did you even manage to save this much at police?"
        elif 200000 > self.available_money > 99999:
            current_money_status = "If you don't spend unwisely, you probably don't have to worry about money for some time."
        elif 100000 > self.available_money > 74999:
            current_money_status = "Your money pillow is somewhat safe...for now."
        elif 75000 > self.available_money > 49999:
            current_money_status = "You still have some reserves saved, but they are getting thinner."
        elif 50000 > self.available_money > 29999:
            current_money_status = "Your situation regarding reserves is getting worse."
        elif 30000 > self.available_money > 19999:
            current_money_status = "You should really start thinking about your reserves."
        elif 20000 > self.available_money > 9999:
            current_money_status = "You are running out of money!"
        elif 10000 > self.available_money > 4999:
            current_money_status = "SOON YOU WILL HAVE NO MONEY LEFT!"
        elif 5000 > self.available_money > 0:
            current_money_status = "YOU HAVE YOUR LAST RESERVES!"
        elif self.available_money <= 0:
            current_money_status = "YOU HAVE NO MONEY LEFT."
        return current_money_status

    def stats_description_coding_experience(self):
        """Stats description message, describing the value of coding experience stat in plain language."""
        current_coding_experience_status = None

        if self.coding_experience == 100:  # 100
            current_coding_experience_status = " MAXIMUM SKILL - You cannot progress anymore at this point."
        elif 100 > self.coding_experience > 84:  # 99-85
            current_coding_experience_status = ("Your coding skills are very high, "
                                                "you are on a level of a junior developer!, good job!")
        elif 85 > self.coding_experience > 64:  # 84-65
            current_coding_experience_status = ("Your coding skills are pretty good, you are almost on a level of a "
                                                "new junior developer.")
        elif 65 > self.coding_experience > 49:  # 64-50
            current_coding_experience_status = ("Your coding skills are getting better, you understand the basics "
                                                "of OOP, you can make a simple website or a text game.")
        elif 50 > self.coding_experience > 29:  # 49-30
            current_coding_experience_status = ("Your coding skills are very basic at best, "
                                                "you still have a lot of blind spots left, there is a lot to study.")
        elif 30 > self.coding_experience > 9:  # 29-10
            current_coding_experience_status = ("Your coding skills are completely basic, you are able to write "
                                                "extremely simple programs like calculator and some statements.")
        elif 10 > self.coding_experience > 0:  # 9-1:
            current_coding_experience_status = ("Your coding skills are very lacking, you can barely write "
                                                'Hello world!'"")
        elif self.coding_experience == 0:  # 0
            current_coding_experience_status = ("Your coding skills are non-existent, you are glad, that you are able "
                                                "to open up your PC.")
        return current_coding_experience_status

    def stats_description_police_hatred(self):
        """Stats description message, describing the value of police hatred stat in plain language."""
        current_police_hatred_status = None

        if 100 > self.pcr_hatred > 84:  # 99-85
            current_police_hatred_status = ("HAHAHAHAHDAHHAHAHAHAHHHHIHIHIAHAHAHAHHHHAAHGGGAGAGAG FUCKING HELP MEE!!!!"
                                            "THIS JOB IS DEVOURING ME ALIVE I HAD ENOUGH.")
        elif 85 > self.pcr_hatred > 64:  # 84-65
            current_police_hatred_status = "I CANNOT TAKE THIS ANYMORE... IT HAS TO END SOON, FUCK THIS BULLSHIT!!!."
        elif 65 > self.pcr_hatred > 49:  # 64-50
            current_police_hatred_status = "FUCK THIS... just few more months... I promise..."
        elif 50 > self.pcr_hatred > 25:  # 49-26
            current_police_hatred_status = "I'm only prolonging my suffering here, it's getting worse day by day..."
        elif self.pcr_hatred == 25: # 25
            current_police_hatred_status = "I know I have to leave... this is going to get much worse."
        elif 25 > self.pcr_hatred > 9:  # 24-10
            current_police_hatred_status = "The cracks are starting to show, yet you ignore them for now..."
        elif 10 > self.pcr_hatred > 0:  # 9-1:
            current_police_hatred_status = ("There are some things you don't really like about PCR, but you still "
                                            "overall like your job a lot.")
        elif self.pcr_hatred== 0:  # 0
            current_police_hatred_status = "You love your job so much, you are grateful for it. :)."
        return current_police_hatred_status

    def get_stats_command(self):
        """Input command for getting current stats of the main character."""
        print(
            f"\nYour stats are: "
            f"\n\nMoney amount: {self.available_money} - {JBStats.stats_description_money(self)}"
            f"\nCoding skill: {self.coding_experience} - {JBStats.stats_description_coding_experience(self)}"
            f"\nPolice hatred: {self.pcr_hatred} - {JBStats.stats_description_police_hatred(self)}"
        )
        red = "\033[91m"
        reset = "\033[0m"

        if self.pcr_hatred > 90:
            print(
                f"\n{red}WARNING: YOUR PCR HATRED IS {self.pcr_hatred}! "
                f"IF YOU REACH 100, YOU WILL LOSE!{reset}"
            )

        if self.available_money < 5000:
            print(
                f"\n{red}WARNING: YOUR MONEY IS {self.available_money}! "
                f"IF YOU REACH 0, YOU WILL LOSE!{reset}"
            )

    def change_stats_value_money(self, set_money_value):
        """Change the value of stats available money to different number."""
        self.available_money = set_money_value

    def change_stats_coding_skill(self, set_coding_skill_value):
        """Change the value of stats coding skill to different number."""
        self.coding_experience= set_coding_skill_value

    def change_stats_pcr_hatred(self, set_pcr_hatred):
        """Change the value of stats pcr hatred to different number."""
        self.pcr_hatred = set_pcr_hatred

    def increment_stats_value_money(self, increment_money_value):
        """Change the value of stats available money to different number."""
        self.available_money += increment_money_value

    def increment_stats_coding_skill(self, increment_coding_skill_value):
        """Change the value of stats coding skill to different number."""
        self.coding_experience += increment_coding_skill_value
        if self.coding_experience > 100:
            print("\nYOUR MAXIMUM CODING EXPERIENCE IS SET TO 100, YOU WILL NOT GET ANY FURTHER SKILL!")
            self.coding_experience = 100

    def increment_stats_pcr_hatred(self, increment_pcr_hatred):
        """Change the value of stats pcr hatred to different number."""
        self.pcr_hatred += increment_pcr_hatred

    def coding_experience_limit(self): #how do I make it so the function runs literally forever in the background like a background loose/win check?
        """Coding experience is limited to 100 in ARC1."""
        while self.coding_experience > 100:  # coding experience is limited to 100 in ARC I.
            print("\nYOUR MAXIMUM CODING EXPERIENCE IS SET TO 100, YOU WILL NOT GET ANY FURTHER SKILL!")
            self.coding_experience = 100
            break