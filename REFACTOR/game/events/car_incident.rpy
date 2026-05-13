################################################################################
## REFACTOR - Arc I: The Car Incident
## Trimmed to ~80 lines (from 212) per playtest report — prologue ran 3-4 min
## with playtester saying "nothing is happening". Single path: Admit. JB
## reports up the chain, the Colonel arrives, mentor lecture. Sets
## colonel_attitude for downstream events.
################################################################################

label car_incident:

    $ renpy.movie_cutscene("video/car_incident_intro.webm")

    play music "audio/enter_the_code_theme.mp3" fadein 1.0

    scene bg_parking_lot
    call screen arc_title_card("I", "THE INCIDENT") with arc_fade
    show jb neutral at char_left with dissolve
    pause 0.6

    "06:30 AM. Late shift. Two hours of sleep."
    "You reverse out of the bay you've used four hundred times. Eyes half-closed. Muscle memory."

    stop music fadeout 0.3
    show jb worried at char_left
    play sound "audio/car_scrape.mp3" volume 0.5

    "..."

    play music "audio/enter_the_code_theme.mp3" fadein 0.5

    "A polite crunch. You look in the mirror. You see grey."
    "You get out. A Kodiaq is parked diagonal across the back lane. Your bumper found his front grille at maybe four kph."
    "Nobody parks like that. Except the Commandant."

    ## Flashback — make the Colonel identity unmissable. Banner first, then
    ## the cutscene, so the playtester knows WHO they're about to meet.
    stop music fadeout 0.3
    scene bg_black with fade
    pause 0.3

    "{size=+18}{color=#ffcc00}{b}FLASHBACK — THE COLONEL{/b}{/color}{/size}"

    pause 0.3
    $ renpy.movie_cutscene("video/colonel_car_incident.webm")

    scene bg_parking_lot with fade
    show jb worried at char_left
    play music "audio/enter_the_code_theme.mp3" fadein 0.5

    "{cps=8}{b}{color=#ffcc00}{size=+12}AND THIS IS HIS CAR.{/size}{/color}{/b}{/cps}"
    "Cameras. Gossip. The Commandant's morning walk-around. He'll know by lunch."
    "You'd rather be the one who tells him."

    jump car_incident_admit


## ---------------------------------------------------------------------------
## RESOLUTION — JB reports up the chain. Colonel arrives. Lecture, signature.
## ---------------------------------------------------------------------------

label car_incident_admit:

    scene bg_police_interior
    show jb determined at char_left

    "You write your name and badge number on a torn corner of paper. Wedge it under his wiper. Walk inside and tell the supervisor before the Commandant does."
    "He calls the Colonel. The Colonel gets in his car anyway."

    stop music fadeout 1.5
    scene bg_black with fade
    pause 0.4
    play music "audio/you_failed_me_son.mp3" fadein 1.0

    scene bg_police_office with fade

    "Three hours later the Colonel is sitting in the Commandant's chair. The Commandant is standing in the corner of his own office."

    show colonel disappointed at char_right with dissolve
    show jb neutral at char_left with dissolve
    pause 0.4

    colonel "Sit down, JB."

    "You sit."

    colonel "You damaged a department vehicle. You reported it within three minutes. That is the only reason this is a conversation and not a hearing."
    colonel "Insurance deductible: 3,500 CZK. Out of your pocket. By Friday."

    show jb determined at char_left

    "You sign."

    colonel "Honesty is the cheapest currency we have. Spend it before the expensive stuff."
    colonel "I'll be checking in on you."

    python:
        stats.colonel_attitude = "paternal"
        stats.increment_stats_pcr_hatred(8)
        stats.increment_stats_value_money(-3500)
        grant_card("took_the_heat", silent=True)

    window hide
    show screen outcome_panel("-3,500 CZK, +8 HATRED, + card: TOOK THE HEAT (1E, exhaust — gain 10 block, draw 1).")
    pause
    hide screen outcome_panel

    jump car_incident_end


## ---------------------------------------------------------------------------
## CLOSING — grind objective
## ---------------------------------------------------------------------------

label car_incident_end:

    scene bg_police_interior
    show jb determined at char_left

    "30 days. Pay him back. Become a developer. Don't break."
    "Every night you don't move forward, you gain HATRED."

    ## Onboarding — 6-popup intro before the first daily menu. Persistent flag
    ## inside `tutorial_intro` early-returns on replay.
    call tutorial_intro from _call_tutorial_intro

    return
