################################################################################
## REFACTOR - All Endings
## Ported verbatim from game_endings.py
################################################################################

## ---------------------------------------------------------------------------
## MENTAL BREAKDOWN ENDING
## Triggered when PCR Hatred >= 100
## ---------------------------------------------------------------------------

label mental_breakdown_ending:

    play music "audio/breakdown_theme.mp3" fadein 1.0
    scene bg_police_interior

    "It happens during a routine briefing."
    "The Colonel is talking about 'Uniform Standards'."
    "The sound of his voice turns into a high-pitched screeching noise."

    "You stand up. You aren't in control anymore."
    "You scream. You flip the table. You throw your chair through the window."

    "Three colleagues have to tackle you."
    "They sedate you. You wake up in a white room with soft walls."
    "The doctor says you need 'rest'. A lot of rest."
    "You lost your badge. You lost your gun. But finally... there is silence."

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "BAD ENDING",
        "INSTITUTIONALISED",
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
## COLONEL DEFEAT ENDING
## Triggered when JB HP <= 0 or loses the HP comparison at stalemate
## ---------------------------------------------------------------------------

label colonel_defeat_ending:

    play music "audio/breakdown_theme.mp3" fadein 1.0
    scene bg_police_office
    show colonel normal at char_right

    "You slowly sit back down in the chair."
    "The Colonel watches you. His face shows no emotion. No satisfaction. Just... emptiness."

    "You look at your hands. They're shaking."
    "The Colonel's words are still ringing in your ears."
    colonel "'You're nothing without this uniform, JB.'"
    colonel "'You're nothing without this badge.'"
    colonel "'You're nothing without {stshl=ME}.'"

    "You open your mouth. You want to argue. You want to fight back."
    "But... nothing comes out."

    "Instead, you hear your own voice. Soft. Broken. Apologetic."
    jb "'I... I'm sorry, Colonel.'"
    jb "'I was wrong.'"

    "The words feel foreign on your tongue. Like you're reading from a script."
    "But as you say them, something strange happens."
    "The weight on your chest... it starts to lift."

    jb "'You're right, Colonel.'"
    jb "'There is no better job than being a police officer.'"
    jb "'I... I realize that now.'"

    "The Colonel's expression doesn't change. But he nods slowly."
    colonel "'Good. I'm glad you understand.'"
    colonel "'You can go back to your duties now.'"

    "You stand up. Your legs feel heavy. But you stand."
    "You walk to the door. Your hand reaches for the handle."
    "And as you turn it, you feel... nothing."
    "No anger. No hatred. No dreams of coding or freedom."

    python:
        stats.coding_skill = -100
        stats.pcr_hatred   = -100

    "Just... acceptance."
    "This is your life now."
    "This has always been your life."
    "And you're okay with that."

    "You return to your desk."
    "You pick up a report."
    "You start filling it out."

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "BAD ENDING",
        "ACCEPTANCE",
        "War is peace. Freedom is slavery. Ignorance is strength.",
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

    $ renpy.movie_cutscene("video/jb_good_ending.mp4")

    scene bg_black

    "The blinding light hits you."

    pause 2.0

    "You step out. You expect the grey, dirty street of the city."
    "Instead..."

    "It is a field. A vast, golden wheat field under a perfect blue sky."
    "The sun is warm on your face. The air smells of summer and freedom."

    "You look back."
    "The Police Station isn't a building anymore."
    "It's just a small, grey, cardboard box sitting in the middle of the field."
    "You can still hear a tiny, squeaky voice inside yelling about regulations."

    scene bg_cafe with slow_dissolve
    show jb developer_happy at char_left with dissolve

    "You smile."
    "You reach out and touch the wheat. It feels real."
    "You take a deep breath."

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
## COLONEL PYRRHIC VICTORY
## Triggered when JB wins the fight but HP is 30-69 (scarred but standing)
## ---------------------------------------------------------------------------

label colonel_pyrrhic_victory:

    play music "audio/road_to_freedom.mp3" fadein 1.0
    scene bg_police_office
    show jb worried at char_left
    show colonel disappointed at char_right

    "The Colonel's voice has gone quiet."
    "Not because you won. Not because you broke him."
    "Because you {stshl=outlasted} him."

    "You are still standing. Barely."
    "Your hands are shaking. Your voice, if you tried to speak, would crack."
    "But you are still here."

    colonel "'JB... I...' He trails off."
    "He looks old. For the first time, he just looks old."

    jb "'I'm going to submit this resignation, Colonel.'"
    jb "'And I'm going to walk out. And you're not going to stop me.'"

    "He doesn't move."
    "He doesn't call you back."

    "You walk out."
    "The hallway is quiet."
    "You sit on a bench outside for 10 minutes before your legs stop shaking."
    "Then you call Martin."

    python:
        _ep_class = stats.player_class

    if _ep_class == "bodybuilder":
        "You don't look like someone who just won anything."
        "You look like someone who survived a fight by deciding halfway through that losing was worse."
        "Martin picks you up. He says nothing for the first ten minutes."
        "Then: 'You looked like that the first day at the academy too.'"
        "You find that funny. It takes you a while to figure out why."
    elif _ep_class == "dark_empath":
        "Martin asks how it went."
        "You give him the factual version. The emotional version you'll process in about three weeks, probably."
        "He nods. He knows your pattern."
        "'You read him, didn't you?' he asks."
        "'I always do,' you say."
        "'Did it help?'"
        "'It got me out.'"
    elif _ep_class == "biohacker":
        "Your hands have stopped shaking."
        "Your nootropic protocol held. The compound clarity carried you through the worst of it."
        "You open your phone and log the outcome. HRV. Decision quality. Stress response under fire."
        "Data point: survived. Classification: barely."
        "Martin sees you typing and shakes his head."
        "'Can you not optimize the traumatic experience for five minutes?'"
        "You log that too."

    python:
        _base_score  = (stats.available_money / 100) + (stats.coding_skill * 100)
        _diff_mult   = {"easy": 1.0, "hard": 2.5, "insane": 5.0}.get(stats.difficulty, 1.0)
        _final_score = int(_base_score * _diff_mult * 0.85)
        _diff_name   = (stats.difficulty or "unknown").capitalize()

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "BITTERSWEET ENDING",
        "SCARRED BUT FREE",
        "The freedom is real. The scars are real. Both can be true.",
        "bittersweet",
        score=_final_score,
        score_note="x0.85 multiplier — Scarred but Standing",
        money=stats.available_money,
        coding=stats.coding_skill,
        diff_name=_diff_name
    )

    $ renpy.full_restart()


## ---------------------------------------------------------------------------
## COLONEL CLOSE VICTORY
## Triggered when JB wins the fight but HP < 30 (barely survived)
## ---------------------------------------------------------------------------

label colonel_close_victory:

    play music "audio/road_to_freedom.mp3" fadein 1.0
    scene bg_black with glitch_transition

    "You don't remember walking out."
    "You find yourself outside the station. It's raining."
    "You're sitting on the curb. Your phone is in your hand."
    "You called Martin. You don't remember doing it."

    "He answers on the first ring."
    martin "'JB? Are you okay? What happened?'"

    jb "'...I'm out.'"

    "Silence."

    martin "'You did it?'"

    jb "'Yeah.'"

    scene bg_cafe with slow_dissolve
    show jb developer_happy at char_left with dissolve

    martin "'JB. You just survived the hardest thing you'll ever do.'"
    martin "'Now rest. Tomorrow, we build.'"

    python:
        _ep_class = stats.player_class

    if _ep_class == "bodybuilder":
        "You barely remember the last hour."
        "What you remember is deciding, somewhere in the middle of it, that you were not going to sit back down."
        "That was enough."
        "Martin doesn't ask questions. He drives."
        "You eat a full meal for the first time in days."
        "Your body already knows the rest."
    elif _ep_class == "dark_empath":
        "You ran out of empathy midway through."
        "What carried you the rest of the way wasn't feeling — it was pattern recognition."
        "You knew his next move before he did. You countered without needing to care."
        "You aren't sure how you feel about that."
        "Martin is. 'That's exactly what I did,' he says. 'And I'm fine.'"
    elif _ep_class == "biohacker":
        "The compound wore off somewhere in the last round."
        "You finished on raw stubbornness and three hours of sleep."
        "Not optimal. Not your best performance. But measurable."
        "Classification: success. Resources expended: most of them."
        "You make a note to redesign the protocol for next time."
        "Martin looks at you. 'There won't be a next time, JB.'"
        "Right."

    python:
        _base_score  = (stats.available_money / 100) + (stats.coding_skill * 100)
        _diff_mult   = {"easy": 1.0, "hard": 2.5, "insane": 5.0}.get(stats.difficulty, 1.0)
        _final_score = int(_base_score * _diff_mult * 0.75)
        _diff_name   = (stats.difficulty or "unknown").capitalize()

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "DIFFICULT ENDING",
        "BARELY ESCAPED",
        "Some victories look indistinguishable from defeat. This is one of them.",
        "difficult",
        score=_final_score,
        score_note="x0.75 multiplier — Cost everything, gained everything",
        money=stats.available_money,
        coding=stats.coding_skill,
        diff_name=_diff_name
    )

    $ renpy.full_restart()


## ---------------------------------------------------------------------------
## THE GOLDEN HANDCUFF ENDING
## Triggered when player accepts the Colonel's promotion offer
## ---------------------------------------------------------------------------

label golden_handcuff_ending:

    play music "audio/tension_theme.mp3" fadein 1.0
    scene bg_police_office
    show colonel normal at char_right
    show jb bored at char_left

    "The ceremony is brief."
    "They pin the new rank on your uniform. Shake your hand. Take a photo for the intranet."
    "Deputy Chief JB."

    "Martin texts you the next day. 'I heard. Is it what you wanted?'"
    "You don't reply for three days."
    "When you finally do, you type six words."
    jb "'The money is good. I'm fine.'"

    "He doesn't text back for two weeks."
    "When he does, it's just: 'I know.'"

    "You are 34 years old."
    "You still sometimes open a Python tutorial on your phone."
    "You never get past chapter 2."

    python:
        _base_score  = (stats.available_money / 200) + (stats.coding_skill * 50)
        _diff_mult   = {"easy": 1.0, "hard": 2.5, "insane": 5.0}.get(stats.difficulty, 1.0)
        _final_score = int(_base_score * _diff_mult * 0.4)
        _diff_name   = (stats.difficulty or "unknown").capitalize()

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "NEUTRAL ENDING",
        "THE GOLDEN HANDCUFF",
        "The cage got bigger. You got comfortable. Both can happen at the same time.",
        "neutral",
        score=_final_score,
        score_note="x0.4 multiplier — Security has a price",
        money=stats.available_money,
        coding=stats.coding_skill,
        diff_name=_diff_name
    )

    $ renpy.full_restart()


## ---------------------------------------------------------------------------
## THE BURNOUT ENDING
## Triggered when hatred reaches 100 but player is at day 25+
## ---------------------------------------------------------------------------

label burnout_ending:

    play music "audio/breakdown_theme.mp3" fadein 1.0
    scene bg_police_interior

    "It doesn't happen dramatically."
    "You don't flip a table. You don't scream."
    "You just... stop."

    "On a Tuesday morning, you are sitting in the briefing room."
    "The Shift Commander is talking about patrol allocations."
    "And you notice something."
    "You cannot hear him anymore."
    "Not because the sound has stopped."
    "But because you have decided, somewhere below conscious thought, that it no longer applies to you."

    "You stand up. Mid-sentence. His."
    "You walk to your locker. You take off your uniform."
    "You fold it. Neatly. You were always neat."
    "You leave your badge on the top of it like a paperweight."
    "You walk out in your civilian clothes."

    "Nobody stops you."
    "Apparently, you just look like someone who's done."

    "You drive home."
    "You sleep for 16 hours."
    "When you wake up, you eat a full meal for the first time in weeks."

    "You don't have a plan. You don't have savings. You don't have a degree."
    "But you have one thing you haven't had in years."
    "Your own time."

    "You open your laptop."
    "There's a Python tutorial bookmarked from 4 months ago."
    "You click it."
    "'Hello World,' says the screen."
    "'Hello World,' you reply."

    python:
        _base_score  = (stats.available_money / 100) + (stats.coding_skill * 80)
        _diff_mult   = {"easy": 1.0, "hard": 2.5, "insane": 5.0}.get(stats.difficulty, 1.0)
        _final_score = int(_base_score * _diff_mult * 0.6)
        _diff_name   = (stats.difficulty or "unknown").capitalize()

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "BURNOUT ENDING",
        "THE UNPLANNED EXIT",
        "Some people escape with a plan. Some just stop. Both count.",
        "burnout",
        score=_final_score,
        score_note="x0.6 — You got out. Messily. But out.",
        money=stats.available_money,
        coding=stats.coding_skill,
        diff_name=_diff_name
    )

    $ renpy.full_restart()


## ---------------------------------------------------------------------------
## THE ESCAPE ARTIST ENDING
## Perfect ending — achieve coding >= 150 AND money >= 150,000 AND hatred <= 30
## ---------------------------------------------------------------------------

label escape_artist_ending:

    python:
        unlock_achievement("escape_artist")

    play music "audio/road_to_freedom.mp3" fadein 1.0
    scene bg_police_office
    show jb determined at char_left

    "The resignation letter is two sentences long."
    "You wrote it in Python first — just to see what it looked like."
    "Then you translated it into Czech."
    "Clean. Professional. No emotion."

    "The Colonel reads it. He looks for the leverage. The desperation. The fear."
    "He finds none."

    colonel "'JB, I have to say... I didn't see this coming.'"

    jb "'I know. {stshl=That was the point}.'"

    "You shake his hand. He doesn't grip hard enough. That says everything."

    "Your last day is quiet."
    "Your colleagues don't know quite what to do."
    "Some are jealous. Most are just confused."
    "One of the rookies asks: 'What are you going to do?'"
    jb "'Build things.'"
    "'Like what?'"
    jb "'Anything I want.'"

    "You walk out at 14:00. Your shift ends at 22:00."
    "Nobody tries to stop you."

    "Martin is waiting outside with coffee."
    martin "'So. How does it feel?'"

    show jb developer_happy at char_left with dissolve

    jb "'Like compiling without errors for the first time.'"

    martin "'Welcome to production.'"

    python:
        _ep_class = stats.player_class

    if _ep_class == "bodybuilder":
        "You didn't just escape the job."
        "You came out the other side with money in the bank, a body that works, and a skillset nobody expected from you."
        "The Colonel bet you'd be too soft. Then he bet you'd be too dumb."
        "He was wrong twice."
        "You're going to build something that requires both."
    elif _ep_class == "dark_empath":
        "There was no emotional scene at the end."
        "No breakdown, no dramatic speech."
        "You read the Colonel's vulnerabilities, navigated every trap he set, and walked out before he understood what happened."
        "The Colonel is still at his desk, probably."
        "Still trying to figure out how to feel about it."
        "You figured that out about him on day one."
    elif _ep_class == "biohacker":
        "You planned this the way you planned everything."
        "Systematically. With redundancies."
        "The coding skill, the money buffer, the emotional baseline — all optimized."
        "The Colonel brought chaos. You brought a system."
        "Systems beat chaos. You knew that going in."
        "Martin doesn't say 'I told you so.' He doesn't need to."
        "The data speaks."

    python:
        _base_score  = (stats.available_money / 100) + (stats.coding_skill * 150)
        _diff_mult   = {"easy": 1.0, "hard": 2.5, "insane": 5.0}.get(stats.difficulty, 1.0)
        _final_score = int(_base_score * _diff_mult * 1.5)
        _diff_name   = (stats.difficulty or "unknown").capitalize()

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "PERFECT ENDING",
        "THE ESCAPE ARTIST",
        "You didn't just leave. You prepared to leave. And that makes all the difference.",
        "perfect",
        score=_final_score,
        score_note="x1.5 PERFECT ENDING BONUS",
        money=stats.available_money,
        coding=stats.coding_skill,
        diff_name=_diff_name
    )

    $ renpy.full_restart()


## ---------------------------------------------------------------------------
## THE JOURNALIST ENDING
## Secret ending — used bribe evidence AND high coding skill
## ---------------------------------------------------------------------------

label journalist_ending:

    python:
        unlock_achievement("journalist")

    play music "audio/coding_in_snow_theme.mp3" fadein 1.0
    scene bg_black with glitch_transition

    "THE JOURNALIST"
    "An unexpected ending."

    "You never intended this."
    "You were going to just leave. Quietly. Like Martin."
    "But then the USB found you."

    scene bg_police_interior

    "The data on that USB had names. Dates. Transaction records."
    "You are not an investigative journalist."
    "You are a cop who knows how to organize information."
    "And you know how to write clean, readable code."

    "You spend three nights building a simple static site."
    "HTML. CSS. One Python script to parse and format the data."
    "You host it on a free tier. Anonymous domain. VPN."

    "You submit the link to two journalists and one NGO."

    "Three weeks later, it's in a national newspaper."

    "One week after that, the Colonel is placed on administrative leave."

    "You are 200 kilometers away by then."
    "Working remotely. Junior dev. Company doesn't ask about your past."
    "Your GitHub has 47 stars on a utility library you built on a Tuesday evening."

    "You didn't set out to be a hero."
    "You set out to survive."
    "It turns out those aren't always different things."

    python:
        _base_score  = (stats.available_money / 100) + (stats.coding_skill * 120)
        _diff_mult   = {"easy": 1.0, "hard": 2.5, "insane": 5.0}.get(stats.difficulty, 1.0)
        _final_score = int(_base_score * _diff_mult * 1.3)
        _diff_name   = (stats.difficulty or "unknown").capitalize()

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "SECRET ENDING",
        "THE JOURNALIST",
        "You came to code. You stayed to expose. Not the ending anyone planned.",
        "secret",
        score=_final_score,
        score_note="x1.3 JOURNALIST BONUS",
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

    "You walk back to the station."
    "It's October. You wear civilian clothes — the same hoodie you used to wear off-shift."
    "You pause at the door for a long time."

    pause 1.0

    $ renpy.movie_cutscene("video/reunion.mp4")

    scene bg_police_interior with slow_dissolve

    "He sees you in the corridor."
    "You expected anger. Or vindication. Or a speech."

    show colonel normal at char_right with dissolve

    colonel "'JB.'"

    "His voice is flat. Not warm. Not cold."

    colonel "'I had a feeling.'"
    colonel "'There's a desk free in records. Eighteen months minimum if you want your old rank back.'"
    colonel "'Or you can stay civilian. I don't care which.'"

    "He walks away before you answer."

    pause 1.0

    "You sign the paperwork."
    "Your hands don't shake."
    "You knew you'd end up here. You knew it the whole time."

    "Some people can leave."
    "Some people leave and come back."
    "Some people come back {stshl=smaller}."

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
## JBDARK ENDING — the simulation breaks. Reality glitches before the
## confrontation can happen. JB falls into the looping police station.
## Trigger: 3+ days at 95+ hatred AND the nightmare-wolf event has fired.
## ---------------------------------------------------------------------------

label jbdark_ending:

    python:
        unlock_achievement("infinite_loop")

    stop music fadeout 1.0
    scene bg_black with Dissolve(0.8)
    pause 1.5

    "Day 25."
    "You are driving to the station."

    pause 1.0

    "Or you think you are."

    pause 1.0

    "The road keeps going. The exit numbers don't match. The radio plays a song you don't remember turning on."

    pause 1.0

    play music "audio/sevirra_lenoloc.mp3" fadein 2.0

    "You park."
    "The station is the same. The colour is wrong. The colour is the {i}same{/i}."
    "You walk inside."

    pause 1.0

    $ renpy.movie_cutscene("video/JBDARK.mp4")

    scene bg_black with Dissolve(0.5)

    "[[ERROR]]: scene_state.player_position = NULL"
    "[[ERROR]]: Cannot resolve corridor_id."
    "[[ERROR]]: Falling back to last_known_state..."

    pause 0.8

    "[[ERROR]]: last_known_state CORRUPTED."

    pause 1.0

    scene bg_police_interior with Dissolve(0.4)

    "The corridor is too long."
    "The lights flicker in a pattern that almost — almost — matches the rhythm of your breathing."
    "You walk for what feels like an hour. You don't pass any doors."

    pause 1.0

    "The PA crackles."
    colonel "'JB.'"
    colonel "'You can't quit a function with no exit clause.'"
    colonel "'You can't return from a recursive call you never finished.'"
    colonel "'You can't escape the loop you wrote yourself into.'"

    pause 1.0

    "You realise something."
    "Your hands are not your hands."
    "Your uniform is not your uniform — but it fits perfectly."
    "Your name tag says JB."
    "You don't remember your name being JB."
    "You don't remember your name."

    pause 1.5

    scene bg_black with Dissolve(1.0)

    "[[SYSTEM]]: Process did not exit cleanly."
    "[[SYSTEM]]: Restoring from autosave..."

    pause 1.0

    "[[SYSTEM]]: Autosave is the autosave is the autosave."
    "[[SYSTEM]]: Day 1."

    pause 2.0

    play music "audio/breakdown_theme.mp3" fadein 2.0

    scene bg_police_interior with Dissolve(0.5)

    "You wake up at your desk."
    "Your colleague says good morning."
    "You open your mouth."
    "You start your shift."

    pause 1.0

    "You do not feel the loop."
    "The loop is what you {stshl=are}."

    python:
        _base_score  = (stats.available_money / 100) + (stats.coding_skill * 60)
        _diff_mult   = diff_setting("score_mult", 1.0)
        _final_score = int(_base_score * _diff_mult * 0.05)
        _diff_name   = (stats.difficulty or "unknown").capitalize()

    scene bg_black with slow_dissolve

    call screen ending_screen(
        "HIDDEN ENDING",
        "INFINITE LOOP",
        "You compiled. The compiler was you. There was never an outside.",
        "secret",
        score=_final_score,
        score_note="x0.05 — Some games don't end. They restart.",
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
        _diff_mult   = {"easy": 1.0, "hard": 2.5, "insane": 5.0, "ultra": 10.0}.get(stats.difficulty, 1.0)
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
