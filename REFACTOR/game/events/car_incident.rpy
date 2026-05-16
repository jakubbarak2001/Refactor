################################################################################
## REFACTOR - Arc I: The Car Incident
## Trimmed to ~80 lines (from 212) per playtest report — prologue ran 3-4 min
## with playtester saying "nothing is happening". Single path: Admit. JB
## reports up the chain, the Colonel arrives, mentor lecture. Sets
## colonel_attitude for downstream events.
################################################################################

label car_incident:

    ## Intro cutscene plays before dossier chrome — opening title moment
    ## owns the screen alone, no UI bleed.
    $ renpy.movie_cutscene("video/car_incident_intro.webm")

    ## Force the swap. The daily-pool track is on the music channel from
    ## `start`; a plain `play music` after a movie cutscene has been flaky on
    ## Windows (channel state sometimes held by the movie). Hard-stop first.
    stop music
    play music "audio/car_incident_dawn.mp3" fadein 1.0

    scene bg_parking_lot
    call screen arc_title_card("I", "THE INCIDENT") with arc_fade

    ## The dossier say-window is global now; this label only opts in to
    ## the persistent HUD strips + per-beat metadata.
    $ set_dossier_beat("06:30", "FILE I/01 · INTAKE")
    show screen dossier_hud

    show jb neutral at char_left with dissolve
    pause 0.6

    "06:30 AM. Late shift. Two hours of sleep."
    "You reverse out of the bay you've used four hundred times. Eyes half-closed. Muscle memory."

    stop music fadeout 0.3
    show jb worried at char_left
    play sound "audio/car_scrape.mp3" volume 0.5

    "..."

    play music "audio/car_incident_dawn.mp3" fadein 0.5

    "A polite crunch. You look in the mirror. You see grey."
    "You get out. A Kodiaq is parked diagonal across the back lane. Your bumper found his front grille at maybe four kph."
    "Nobody parks like that. Except the Commandant."

    ## Flashback — hard cut to the banner, then straight into the cutscene.
    ## No fade transition or padding pauses; the abrupt swap is the point.
    stop music fadeout 0.3
    scene bg_black
    hide screen dossier_hud

    "{size=+18}{color=#ffcc00}{b}FLASHBACK — THE COLONEL{/b}{/color}{/size}"

    $ renpy.movie_cutscene("video/colonel_car_incident.webm")

    scene bg_parking_lot with fade
    $ set_dossier_beat("06:34", "FILE I/02 · COLONEL'S CAR")
    show screen dossier_hud
    show jb worried at char_left
    play music "audio/car_incident_dawn.mp3" fadein 0.5

    "{cps=8}{b}{color=#ffcc00}{size=+12}AND THIS IS HIS CAR.{/size}{/color}{/b}{/cps}"
    "Cameras. Gossip. The Commandant's morning walk-around. He'll know by lunch."
    "You'd rather be the one who tells him."

    jump car_incident_admit


## ---------------------------------------------------------------------------
## RESOLUTION — JB reports up the chain. Colonel arrives. Lecture, signature.
## ---------------------------------------------------------------------------

label car_incident_admit:

    scene bg_police_interior
    $ set_dossier_beat("06:51", "FILE I/03 · REPORT")
    show jb determined at char_left

    "You write your name and badge number on a torn corner of paper. Wedge it under his wiper. Walk inside and tell the supervisor before the Commandant does."
    "He calls the Colonel. The Colonel gets in his car anyway."

    stop music fadeout 1.5
    hide screen dossier_hud
    play music "audio/you_failed_me_son.mp3" fadein 1.0

    scene bg_police_office with fade
    $ set_dossier_beat("09:47", "FILE I/04 · DEPOSITION")
    show screen dossier_hud

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

    show colonel smug at char_right with dissolve

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
    $ set_dossier_beat("10:15", "FILE I/05 · 30 DAYS")
    show jb determined at char_left

    "30 days. Pay him back. Become a developer. Don't break."
    "Every night you don't move forward, you gain HATRED."

    ## End of the prologue's HUD-strip window. The dossier say-window
    ## itself stays global — only the strips + per-beat metadata are
    ## prologue-scoped, so clear those before handing off to the
    ## tutorial and daily loop.
    hide screen dossier_hud
    $ set_dossier_beat("", "")

    ## Onboarding — 6-popup intro before the first daily menu. Persistent flag
    ## inside `tutorial_intro` early-returns on replay.
    call tutorial_intro from _call_tutorial_intro

    return
