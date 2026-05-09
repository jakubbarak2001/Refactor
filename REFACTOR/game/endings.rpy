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

    play music "audio/road_to_freedom.mp3" fadein 1.0
    scene bg_police_office
    show colonel angry at char_right

    "You start to chuckle."
    "The chuckle turns into a laugh."
    "A loud, liberating, uncontrollable laugh."

    colonel "'WHY ARE YOU LAUGHING?! YOU THINK THIS IS FUNNY? YOUR LIFE IS OVER!'"

    jb "'No, Colonel.'"
    jb "'My life isn't over.'"

    pause 1.0

    jb "'It's just {stshl=compiling}.'"

    pause 2.0

    "> EXECUTING: sys.exit(0) ..."
    "> TEARING DOWN: police_station_module.py ..."
    "> RELEASING RESOURCES ..."

    "You turn your back on him."
    "He is still screaming, his face red, veins popping."
    "But as you walk towards the exit door, his voice starts to fade."
    "Not because of distance. But because you lowered his volume slider."

    "You reach the heavy metal door of the station."
    "It's supposed to be locked. It's supposed to be hard to leave."
    "You simply push it open."

    $ renpy.movie_cutscene("video/jb_good_ending.webm")

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
        if getattr(store, '_bb_arc_won', False):
            "Vladek calls you a year later. He has a sponsorship deal lined up — fitness app on Czech TV."
            "You bring the backend code. He brings the audience. The app ships in nine months."
            "40,000 active users by year two. The competition platform is a poster on your office wall."
            "You still squat on Tuesdays. The body keeps score. The score is good now."
        else:
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
        show colonel normal at char_right

        "You stand up."
        "Your hands are shaking. Your voice isn't."

        jb "'I'm doing it anyway.'"

        "He doesn't answer. He doesn't need to."
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


## ---------------------------------------------------------------------------
## HAPPY NATION ENDING
## Triggers after defeating the Colonel IF corrupt_chain_3_completed is True.
## URNA raids your home. The game ends in handcuffs.
## ---------------------------------------------------------------------------

label happy_nation_ending:

    stop music fadeout 2.0
    scene bg_black
    pause 2.0

    "You did it."
    "You beat the Colonel. You walked out of his office. You felt the air outside the station."
    "You drove home with the windows down."
    "For the first time in thirty days, you felt free."

    pause 1.0

    scene bg_black

    "Three weeks later."

    pause 1.5

    scene bg_jb_bedroom with slow_dissolve

    "2:47 AM."

    pause 1.5

    "The new job starts Monday."
    "You're dreaming about something ordinary. A grocery store, maybe. A parking lot."

    pause 1.0

    scene bg_black with Dissolve(0.3)
    play music "audio/happy_nation.mp3" fadein 1.0
    pause 1.0

    "The front door comes off its hinges."

    pause 0.5

    "'POLICIE! LEHNI SI NA ZEM!'"

    "You are not awake yet when the first pair of hands reaches you."
    "You are not awake yet when your face hits the mattress."
    "You are not awake yet when the zip ties close around your wrists."

    scene bg_jb_bedroom_raid with Dissolve(0.5)

    "ÚRNA. Útvar rychlého nasazení."



    "They pull you off the bed. You're in underwear and a t-shirt."
    "The hallway is full of men in black. Balaclavas. Tactical gloves. Automatic weapons pointed at the floor."
    "One of them is already at your laptop."
    "Another is going through the box of books."

    show inspector neutral at char_right with dissolve

    "A figure steps through the wreckage of your front door."
    "Black tactical jacket. Black balaclava. Black gloves clasped in front of him like he's at a funeral."
    "The yellow armband on his left sleeve reads: GENERÁLNÍ INSPEKCE."
    "He's holding a folder. He doesn't introduce himself. He doesn't need to."

    inspector "'JB.'"

    "His voice is flat. Not angry. Not cold. Just... final."

    inspector "'We have a warrant for your arrest in connection with unauthorized access to the police information system.'"
    inspector "'Specifically: disclosure of classified personal data from the vehicle registration database to an unauthorized civilian on—'"

    "He reads the date. Day 18. The kitchen. The glass of water. The folded note."

    "You close your eyes."

    inspector "'The civilian in question used the information you provided to locate and threaten a protected witness in an ongoing organized crime investigation.'"

    "Your legs stop working. Two officers hold you upright."

    inspector "'The witness is alive. But the case is compromised. Eighteen months of surveillance. Gone.'"

    "He closes the folder. He doesn't put it away. He holds it at his side like a verdict."

    inspector "'You are being charged under Section 329 of the Criminal Code. Abuse of power by a public official.'"
    inspector "'Additional charges pending: obstruction of justice, unauthorized database access, and accessory to witness intimidation.'"

    "He tilts his head. Just slightly. Behind the balaclava, you can't read his expression."
    "But his eyes — the only thing visible — are steady. Unblinking."

    inspector "'The investigation was opened eleven days before your resignation. You were under surveillance for the final week of your service.'"
    inspector "'Your resignation changed nothing. The crime was committed while you wore the badge. Our jurisdiction doesn't end when yours did.'"

    "He's seen this before. A hundred times. You are not special to him."

    pause 1.0

    hide inspector with dissolve

    "They walk you out of the apartment."
    "Past the broken door. Past the neighbours standing in the corridor in their bathrobes."
    "Past the packed suitcases that will never move."
    "Past the laptop with the resignation letter that will never be sent."
    "Past the life you built. Line by line. Night by night."

    "The unmarked van is parked outside. Engine running."
    "They put you in the back. The doors close."

    pause 2.0

    scene bg_black

    "You think about the BMW driver. The steady hands. The recording."
    "You think about the kitchen. The folded note. The name you didn't recognize."
    "You think about Day 6. The Litoměřice stretch. The moment your hand closed around the banknotes."
    "Seven thousand, five hundred crowns."
    "That's what your life cost."

    pause 2.0

    "You beat the Colonel."
    "You learned to code."
    "You were going to be free."

    pause 1.0

    "But some debts compile at runtime."

    pause 3.0

    stop music fadeout 2.0
    scene bg_black
    pause 1.0

    $ renpy.movie_cutscene("video/colonel_laughter.webm")

    python:
        _base_score  = (stats.available_money / 100) + (stats.coding_skill * 120)
        _diff_mult   = {"easy": 1.0, "hard": 2.5, "insane": 5.0}.get(stats.difficulty, 1.0)
        _final_score = int(_base_score * _diff_mult * 0.1)
        _diff_name   = (stats.difficulty or "unknown").capitalize()

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "HIDDEN ENDING",
        "HAPPY NATION",
        "You escaped the system. The system didn't escape you.",
        "bad",
        score=_final_score,
        score_note="x0.1 CORRUPTION PENALTY",
        money=stats.available_money,
        coding=stats.coding_skill,
        diff_name=_diff_name
    )

    $ renpy.full_restart()
