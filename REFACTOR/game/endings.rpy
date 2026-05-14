################################################################################
## REFACTOR - All Endings
## Ported verbatim from game_endings.py
################################################################################

## ---------------------------------------------------------------------------
## HATRED COLLAPSE ENDING
## Triggered when PCR Hatred >= 100. Day-branched flavor:
##   < 25  → pre-fight institutionalised breakdown
##   >= 25 → post-fight flat-acceptance burnout
## ---------------------------------------------------------------------------

label hatred_collapse_ending:

    play music "audio/breakdown_theme.mp3" fadein 1.0
    scene bg_police_interior

    if day_cycle.current_day < 25:
        "It happens during a routine briefing."
        "The Colonel is talking about 'Uniform Standards'."
        "The sound of his voice turns into a high-pitched screeching noise."
        "You stand up. You aren't in control anymore. You scream. You flip the table."
    else:
        "It doesn't happen dramatically."
        "You don't flip a table. You don't scream. You just... stop."
        "Mid-briefing, you stand up. You walk to your locker. You take off your uniform."
        "You leave your badge on top of it like a paperweight. Nobody stops you."

    "You don't have a plan. You don't have a future. You just have an exit."
    "The hatred has been louder than your own thoughts for weeks now."
    "When you finally stop fighting it, it stops talking."
    "What's left is quieter than you expected. Quieter than peace. Just absence."
    "You were going to be a developer. You were going to be free."
    "Instead the cost of carrying him broke you before he could."

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "BAD ENDING",
        "HATRED COLLAPSE",
        "You needed peace. You got it. Not the way you planned.",
        "bad"
    )

    $ renpy.full_restart()


## ---------------------------------------------------------------------------
## HOMELESS ENDING
## Triggered when Money <= 0
## ---------------------------------------------------------------------------

label homeless_ending:

    play music "audio/coding_in_snow_theme.mp3" fadein 1.0
    scene bg_black

    "Your card is declined at the grocery store. For a rohlík."
    "Your landlord calls. Eviction notice."
    "You sell your laptop. Then your monitor. Then your phone."

    "But it's not enough."
    "You end up sleeping in your car. Then you lose the car."
    "You cannot code on paper crates in the snow."

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "BAD ENDING",
        "THE STREETS",
        "You cannot code on paper crates in the snow.",
        "bad"
    )

    $ renpy.full_restart()


## ---------------------------------------------------------------------------
## GOOD ENDING
## Triggered from colonel_glitch_phase via [sys.exit()] WAKE UP
## ---------------------------------------------------------------------------

label good_ending:

    python:
        ## "I Don't Need IT" — escape ending reached without signing the
        ## bootcamp contract (python_bootcamp flag, set only by coding_bootcamp /
        ## coding_bootcamp_de). Free work / fiverr / random-event coding skill
        ## doesn't disqualify — only signing for the bootcamp does.
        if not python_bootcamp:
            unlock_achievement("i_dont_need_it")

    scene bg_police_office
    show colonel shaken at char_right
    show jb smirk at char_left

    "You start to laugh. Quiet at first. Then not."

    show colonel angry at char_right with dissolve

    colonel "'YOU THINK THIS IS FUNNY?! YOUR LIFE IS OVER!'"

    jb "'No, Colonel.'"

    pause 1.0

    jb "'It's just {stshl=compiling}.'"

    pause 1.5

    "You turn your back on him and walk to the door."
    "The heavy metal door of the station. Supposed to be locked. Supposed to be hard to leave."

    pause 0.6

    "You push it open with one hand."

    $ renpy.movie_cutscene("video/jb_good_ending.webm")

    play music "audio/road_to_freedom.wav" fadein 2.0

    scene bg_cafe with slow_dissolve
    show jb developer_happy at char_left with dissolve

    ## The cinematic already showed JB walking out + the time-jump to
    ## "after." Holding silent on the cafe scene lets the player register
    ## the new outfit / new posture before the epilogue text starts.
    pause 1.3

    "SYSTEM: BUILD SUCCESSFUL."
    "WELCOME TO PRODUCTION, JB."

    python:
        _ep_class = stats.player_class

    if _ep_class == "bodybuilder":
        "Three years later, you run a fitness app with 40,000 active users."
        "You wrote the backend yourself. Ugly at first. Then clean. Then elegant."
        "You still lift on Tuesdays. Your home office has a pull-up bar over the door."
        "You look happier than any cop ever looked. That's not luck. That's a choice you made and kept making."
    elif _ep_class == "dark_empath":
        if getattr(store, '_de_kovar_exposed', False):
            "Two journalists win a Pulitzer-equivalent for the Kovář investigation. Your name never appears."
            "You take a UX research role at a product company. You read users the way you read him."
            "The trafficking case from his file leads to seven arrests. You watch the news in a bar in Brno."
            "You order another drink. You don't talk about it. Some kinds of leverage don't compound — they discharge."
        elif getattr(store, '_de_kovar_complicit', False):
            "The 25,000 CZK pays your rent for six months. You don't spend it on anything you can name."
            "You take a UX research role at a product company. You read users professionally now."
            "Sometimes a face on a screen reminds you of a folder you once deleted. You close the tab."
            "Some leverage stays in the body. You learn to live with the weight."
        else:
            "You end up in UX research at a product company."
            "You read users the way you used to read suspects. Every session reveals what people can't articulate."
            "The products you touch ship cleaner. The teams you join argue less."
            "You still occasionally over-analyse waiters. Some habits are features, not bugs."
    elif _ep_class == "biohacker":
        if getattr(store, '_bh_trial_subject', False):
            "The compound has a name now. Two papers on PubMed. Your data set is in the appendix as 'Subject 0'."
            "You join a biotech startup. You bring three months of HRV, sleep, cognitive battery."
            "The CTO offers you principal scientist after looking at your spreadsheet."
            "Some days you can feel the dependency under everything else. You log it. You continue."
        elif getattr(store, '_bh_taught_synth', False):
            "You join a biotech startup as their first research engineer. The synthesis notes are still in your safe."
            "You publish two papers in your first year. One is on cognitive enhancement methodology. The other is on protocol design."
            "You never make compounds at home. Some lines hold."
        else:
            "You join a biotech startup as their first engineering hire."
            "You optimize their deployment pipeline on day two. The CTO stares."
            "On day three you give him your cognitive protocol, formatted as a Notion doc."
            "Six months later it's company policy. You were a cop twelve months ago."
            "The system has no category for you. You prefer it that way."

    python:
        _base_score  = (stats.available_money / 100) + (stats.coding_skill * 100)
        _diff_mult   = {"easy": 1.0, "hard": 2.5, "insane": 5.0}.get(stats.difficulty, 1.0)
        _final_score = int(_base_score * _diff_mult)
        _diff_name   = (stats.difficulty or "unknown").capitalize()

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "GOOD ENDING",
        "YOU ESCAPED THE SIMULATION",
        "SYSTEM: BUILD SUCCESSFUL. WELCOME TO PRODUCTION, JB.",
        "good",
        score=_final_score,
        score_note="x{} difficulty multiplier".format(_diff_mult),
        money=stats.available_money,
        coding=stats.coding_skill,
        diff_name=_diff_name
    )

    call post_credits_singapore

    $ renpy.full_restart()


## ---------------------------------------------------------------------------
## REUNION ENDING — defeated the Colonel, but coding/money too low to make it
## as a developer. Six months later, JB walks back to the station.
## ---------------------------------------------------------------------------

label reunion_ending:

    python:
        unlock_achievement("the_return")

    if getattr(store, '_reunion_via_defeat', False):
        ## Defeat path — JB lost the argument but walked out anyway.
        scene bg_police_office
        show colonel smug at char_right

        "You stand up."
        "Your hands are shaking. Your voice isn't."

        jb "'I'm doing it anyway.'"

        "He doesn't answer. The faint smile doesn't move. He's already proven his point — to himself, anyway."
        "You walk to the door. You don't look back."

        stop music fadeout 2.0
        scene bg_black with slow_dissolve
        pause 1.5
    else:
        ## Victory path — JB beat the Colonel (close / pyrrhic / stat-starved perfect).
        stop music fadeout 2.0
        scene bg_black
        pause 1.5

        "You did it."
        "You walked out of his office."
        "You felt the air outside the station."

    pause 1.0

    "You drove home with the windows down."
    "You slept for fourteen hours."

    pause 1.0

    scene bg_black

    "Three weeks later."

    pause 1.0

    "Your CV is on every job board in the country. 'Junior Python Developer. Self-taught. Career changer.'"
    "The replies that come back are polite. None of them are interviews."

    pause 1.0

    scene bg_black

    "Three months later."

    pause 1.0

    "Your savings ran out in month two."
    "Your parents helped for a while. Then they stopped helping. They didn't say why."
    "You took a delivery job. Then you stopped taking that job because the bike broke."
    "You started reading job listings that said 'security personnel — clean record required.'"

    pause 1.0

    scene bg_black

    "Six months later."

    pause 1.5

    play music "audio/coding_in_snow_theme.mp3" fadein 2.0

    $ renpy.movie_cutscene("video/refactor_true_ending.webm")

    python:
        _base_score  = (stats.available_money / 100) + (stats.coding_skill * 60)
        _diff_mult   = diff_setting("score_mult", 1.0)
        _final_score = int(_base_score * _diff_mult * 0.3)
        _diff_name   = (stats.difficulty or "unknown").capitalize()

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "BITTERSWEET ENDING",
        "THE RETURN",
        "You beat him. The world beat you. Both can be true.",
        "neutral",
        score=_final_score,
        score_note="x0.3 — You won the fight. You lost the after.",
        money=stats.available_money,
        coding=stats.coding_skill,
        diff_name=_diff_name
    )

    $ renpy.full_restart()

