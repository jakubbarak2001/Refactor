from jb_game.jb_dev_car_incident import CarIncident
from jb_game.jb_dev_stats import JBStats
from jb_dev_day_cycle import DayCycle
from jb_dev_game import Game
from jb_game.jb_dev_story import Story


def main():
    stats = JBStats()
    day_cycle = DayCycle()
    game = Game(stats, day_cycle)

    story = Story(stats)
    story.start_game_message()

    game.set_difficulty_level()

    CarIncident.car_incident_event(stats)

    game.main_menu()


if __name__ == "__main__":
    main()


# 18.11.2025 - State of the game.

# DONE:

# CAR INCIDENT EVENT, MULTIPLE DECISIONS.
# 20-30 MINS OF GAMEPLAY
# 3 FULLY WORKING STATS: CODING, MONEY, HATRED
# 100 CODING CHECK
# DAYS CALCULATOR
# GAME MENU:
# 1. SELECT ACTIVITY (ONLY ONE ACTIVITY DAILY: 1. GYM, 2. READ, 3. STUDY PYTHON, 4. BOUNCER NIGHT SHIFT)
# 2. STATS REPORT
# 5. END THE DAY.

# TO BE DONE:

# HIGH PRIORITY:

# ADD STATES, AFTER MAJOR DECISIONS (I.E. COLONEL BECOMES HOSTILE AFTER YOU GAIN LAWYER...)
# STATS - 0 MONEY BACKGROUND CHECK, 100 HATRED BACKGROUND CHECK, 100 CODING BACKGROUND CHECK
# MM Event, Retirement Event (biggest one, long dialogue, multiple choices and rolls based on your skills)
# DEBUFFS AND BUFFS (AFFECTING STATS)
# GAME MENU:
# SIMPLIFY GAME MENU, MAKE SEPARATE MODULES FROM THE LORE AND GAME LOGIC
# ADD 4. SHOP
# ADD WORKING CONTACTS
# ADD 8 RANDOM EVENTS THAT HAPPEN EVERY THIRD DAY, SKIPPING THE DAY ENTIRELY.
# FIX BETTER CALL PAUL EVENT


# MEDIUM PRIORITY:

# PERKS GAINED AFTER DOING ANY ACTIVITY X TIMES (I.E. BRAWLER - GO TO GYM 10 TIMES...)
# PERKS WILL ALLOW SECRET OPTIONS IN THE LAST MAIN EVENT OF THE GAME.

# LOW PRIORITY:

# ADD NIGHTMARE DIFFICULTY
# PS EASTER EGG




