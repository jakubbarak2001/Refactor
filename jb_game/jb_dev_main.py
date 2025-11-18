from jb_dev_car_incident import car_incident
from jb_game.jb_dev_stats import JBStats
from jb_dev_day_cycle import DayCycle
from jb_dev_game import Game

def main():
    stats = JBStats()
    day_cycle = DayCycle()
    game = Game(stats, day_cycle)

    # 1. Welcome message
    game.start_game_message()

    # 2. Difficulty selection
    game.set_difficulty_level()

    # 3. Car incident (event requires stats passed in)
    car_incident(game.stats)

    # 4. Start main menu
    game.main_menu()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    main()

# 15.11.2025 - State of the game.

# DONE:

# CAR INCIDENT EVENT, MULTIPLE DECISIONS.
# 5-10 MINS OF GAMEPLAY
# 3 FULLY WORKING STATS: CODING, MONEY, HATRED
# DAYS CALCULATOR
# GAME MENU:
# 1. SELECT ACTIVITY (ONLY ONE ACTIVITY DAILY: 1. GYM, 2. READ, 3. STUDY PYTHON, 4. BOUNCER NIGHT SHIFT)
# 2. STATS REPORT
# 3. CALL SOMEONE (5 CONTACTS: MM, MK, PAUL GOODMAN, COLONEL, PS)
# 4. SHOP
# 5. END THE DAY.

# TO BE DONE:

# HIGH PRIORITY:

# ADD STATES, AFTER MAJOR DECISIONS (I.E. COLONEL BECOMES HOSTILE AFTER YOU GAIN LAWYER...)
# STATS - 0 MONEY BACKGROUND CHECK, 100 HATRED BACKGROUND CHECK, 100 CODING BACKGROUND CHECK
# MM Event, Retirement Event (biggest one, long dialogue, multiple choices and rolls based on your skills)
# DEBUFFS AND BUFFS (AFFECTING STATS)
# GAME MENU:
# 4. SHOP


# MEDIUM PRIORITY:

# PERKS GAINED AFTER DOING ANY ACTIVITY X TIMES (I.E. BRAWLER - GO TO GYM 20 TIMES)
# PERKS WILL ALLOW SECRET OPTIONS IN DECISIONS THAT WOULD BE HIDDEN OTHERWISE...
# PS EASTER EGG

# LOW PRIORITY:

# ADD NIGHTMARE DIFFICULTY




