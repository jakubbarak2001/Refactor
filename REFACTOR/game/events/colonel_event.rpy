################################################################################
## REFACTOR — Arc III: The Colonel Event (Phase 1.7 — Deck Battle)
##
## Round 1 (Waiting) and Round 2 (Entrance) are pure narrative.
## The actual fight is the Slay-the-Spire-style deck battle (battle_screen).
## Glitch phase + victory resolution stay as scripted narrative.
################################################################################

label colonel_event:

    ## Autosave: pre-colonel-fight (Day 25 or 30 — last chance)
    $ renpy.save("auto-colonel", "Colonel Fight — Pre-Battle")

    ## Last-chance class arc — fire any unfinished stages.
    ## Calls hoisted to script level (renpy.call from a python: block raises
    ## CallException and unwinds, killing the second call).
    call colonel_pre_arc_check from _call_colonel_pre_arc_a
    call colonel_pre_arc_check from _call_colonel_pre_arc_b

    play music "audio/tension_theme.mp3" fadein 1.0

    call screen arc_title_card("III", "THE RECKONING") with arc_fade

    ## --- Round 1: The Waiting ---
    call colonel_round_one from _call_colonel_round_one

    ## --- Round 2: His Entrance ---
    call colonel_round_two from _call_colonel_round_two

    hide jb with dissolve
    show colonel normal at char_right with dissolve

    ## --- Initialize the deck battle ---
    python:
        battle_init()

        ## Biohacker compound state — same logic as before, applied to BattleState
        _bh_withdrawal = (stats.player_class == "biohacker" and nootropic_dependency and nootropic_last_tier == 0)
        _bh_flmod      = (stats.player_class == "biohacker" and nootropic_last_tier == 5)

        if _bh_withdrawal:
            battle_state.player_hp = max(1, battle_state.player_hp - 15)
            renpy.say(None, "[[WITHDRAWAL — BIOHACKER]: Tremors. Shallow breath. Walking in already compromised. -15 HP.")
        elif _bh_flmod:
            battle_state.player_max_hp += 15
            battle_state.player_hp += 15
            battle_state.max_energy += 1
            renpy.say(None, "[[FLModafinil — BIOHACKER]: Peak cognitive state. Dopamine locked. +15 HP, +1 max energy/turn (stacks with PROTOCOL).")

    ## --- Run the deck battle ---
    play music "audio/dum_bez_dveri.mp3" fadein 1.0

    "He sits. He squares a deck of cards on the desk between you. The silence is heavy."
    "Then, he attacks."

    $ battle_start_player_turn()

    call screen battle_screen

    ## --- Resolve outcome ---
    python:
        _outcome = battle_outcome()
        battle_finish()

    ## Defeat routes to its own ending; any victory routes through the glitch
    ## phase to good_ending.
    if _outcome == "defeat":
        jump colonel_defeat_ending

    jump colonel_glitch_phase


## ---------------------------------------------------------------------------
## Pre-colonel arc check — fires the next pending class-arc stage.
## Called twice from colonel_event so a player with both stage 2 and 3 pending
## sees both events before the fight begins.
## ---------------------------------------------------------------------------

label colonel_pre_arc_check:
    python:
        _pre_arc_label = class_arc_pre_colonel_check()
    if _pre_arc_label is not None:
        call expression _pre_arc_label from _call_pre_arc_dynamic
    return


## ---------------------------------------------------------------------------
## ROUND 1 — The Waiting (narrative only)
## ---------------------------------------------------------------------------

label colonel_round_one:

    scene bg_police_hallway with glitch_transition

    "You hand in the resignation. Three hours later the black Superb pulls into the lot."
    "He sits in it for five minutes. Watching nothing."
    "You stand at the window. Your deck is in your hand."

    return


## ---------------------------------------------------------------------------
## ROUND 2 — His Entrance (narrative only)
## ---------------------------------------------------------------------------

label colonel_round_two:

    $ renpy.music.set_volume(1.5, 0, channel="voice")

    scene bg_police_office with glitch_transition
    show colonel normal at char_right

    "The third-floor office. He's at the window, hands behind his back, watching the lot where his car is parked."

    show colonel smug at char_right with dissolve

    voice "audio/voice/col_01_so_you_really_did_it.ogg"
    colonel "So. You really did it."

    show jb neutral at char_left with dissolve

    voice "audio/voice/col_02_sit_down_jb.ogg"
    colonel "Sit down, JB."

    voice "audio/voice/jb_01_ill_stand.ogg"
    jb "I'll stand."

    voice "audio/voice/col_03_i_said_sit_down.ogg"
    colonel "I said. Sit. Down."

    show colonel angry at char_right with dissolve

    ## col_04 is loud enough at the base level — drop the +20% just for it.
    $ renpy.music.set_volume(1.25, 0, channel="voice")
    voice "audio/voice/col_04_out_of_your_mind.ogg"
    colonel "ARE YOU OUT OF YOUR FUCKING MIND?!"
    $ renpy.music.set_volume(1.5, 0, channel="voice")

    voice "audio/voice/col_05_six_thirty_morning.ogg"
    colonel "Six-thirty in the morning. A grown ass adult. And you put your bumper through MY grille — do you remember that, JB? Do you remember what should have happened to you that day?"

    voice "audio/voice/col_06_parking_tickets.ogg"
    colonel "You should have been writing parking tickets in some backwater village for the next five years. You should have been the joke at every briefing in this country."

    voice "audio/voice/col_07_made_that_go_away.ogg"
    colonel "I made that go away. I put my ass on the fucking LINE for you—"

    voice "audio/voice/col_08_get_from_you.ogg"
    colonel "AND THIS IS WHAT I GET FROM YOU?!"

    voice "audio/voice/col_09_computers_jb.ogg"
    colonel "This. A piece of paper. {i}Computers{/i}. {i}Computers{/i}, JB?"

    voice "audio/voice/col_10_matcha_prestige.ogg"
    colonel "You're going to throw all of that away to drink a fucking matcha latte in some office in Prague? Is that what you want? What about the PRESTIGE of this job? The badge? The uniform?"

    voice "audio/voice/col_11_think_jb_thirty_years.ogg"
    colonel "THINK, JB! What will you have in thirty years? A pension? Stability? The kind of respect you've earned in this uniform?"

    voice "audio/voice/col_12_youll_be_back.ogg"
    colonel "You'll be back. You hear me? One week. Two, tops. You'll come crawling back through that door and you'll {i}beg{/i} me to tear this letter up. And maybe — maybe — if I'm in a good mood, I will."

    show colonel disappointed at char_right with dissolve

    voice "audio/voice/col_13_got_you_this_job.ogg"
    colonel "I got you this job. I got you into the academy. I gave you the cases nobody else trusted you with. When half the squad wanted you transferred, I was the one who stood up for you."

    voice "audio/voice/col_14_resignation.ogg"
    colonel "And this is how you repay me. You walk in here with a fucking RESIGNATION."

    show colonel smug at char_right with dissolve

    voice "audio/voice/col_15_no_not_from_me.ogg"
    colonel "No. No, you don't get to leave like this. Not on paper. Not from me."

    voice "audio/voice/col_16_you_earn_it.ogg"
    colonel "You want out? You earn it. The way everything in this building gets earned."

    voice "audio/voice/col_17_sit_down_final.ogg"
    colonel "Sit. Down."

    show jb determined at char_left with dissolve

    voice "audio/voice/jb_02_get_this_over_with.ogg"
    jb "Let's get this over with."

    $ renpy.music.set_volume(1.0, 0, channel="voice")

    return


## ---------------------------------------------------------------------------
## GLITCH PHASE — post-Colonel resolution. He's revealed as a loop; JB stops
## performing and walks. Routes into colonel_victory_resolution -> good_ending.
## ---------------------------------------------------------------------------

label colonel_glitch_phase:

    stop music fadeout 1.5

    scene bg_colonel_office_shaken with glitch_transition
    show colonel shaken at char_right

    "[[SYSTEM]: Colonel HP = 0."

    pause 0.5

    scene bg_police_office with glitch_transition
    show colonel normal at char_right

    colonel "'You are a {b}COWARD{/b}, JB! You were never fit for this force!'"

    "Word for word. The opening line. {i}police_bureaucracy.exe{/i} — runtime: 32 years."

    $ unlock_achievement("wake_up_call")

    pause 0.6

    ## Coding gate — the TRUE ending. A real coder doesn't just notice the loop;
    ## he can read it, reach in, and kill the process. Tier 3 (Coding >= 100).
    ## This is the bar that makes the coding lane the route to the game's best
    ## outcome — without touching the gym. Tunable.
    if (stats.coding_skill or 0) >= 100:
        jump colonel_ghost_phase

    show jb smirk at char_left

    jb "'I'm done.'"

    "Some part of you knows the loop didn't stop — it just lost sight of you. Ending it would have taken something you never built in yourself. You let the door close instead, and you go."

    jump colonel_victory_resolution


## ---------------------------------------------------------------------------
## GHOST PHASE — the coding-gated TRUE-ENDING fight. You don't walk out; you
## follow the loop INTO the machine and kill the process. Win -> true ending.
## Lose -> you already beat the man, so it's not death: you couldn't hold the
## connection and take the normal escape (good_ending).
## ---------------------------------------------------------------------------

label colonel_ghost_phase:

    scene bg_colonel_office_shaken with glitch_transition
    show colonel shaken at char_right with dissolve

    "But you can read it now."
    "Thirty days of documentation tabs and broken builds, and the thing across the desk stops being a man. It is a process. A loop with a leak. You have killed a hundred of these."

    show jb determined at char_left with dissolve
    jb "'No. You don't get to keep running.'"

    "You stop reaching for the door and reach for the {i}stack{/i} instead."

    scene bg_colonel_ghost with glitch_transition
    show colonel_ghost neutral at char_right with dissolve
    "The office peels off the walls. The man peels off the office. Underneath, the loop runs on — wearing him like a stolen login, thirty-two years deep."

    play music "audio/tension_theme.mp3" fadein 1.0

    python:
        ## Steady before jacking in — the connection holds you up to ~60% so the
        ## climax is tense, not a coin-flip on leftover HP. Short HP bar (120),
        ## but its hits only survive if you out-code them (Coding reduces them).
        if store.run_hp_max is None:
            store.run_hp_max = class_max_hp()
        store.run_hp = max(getattr(store, 'run_hp', 0) or 0, int(store.run_hp_max * 0.6))
        battle_init("colonel_ghost")
        battle_start_player_turn()

    "[[SYSTEM]: process police_bureaucracy.exe — STILL RUNNING. attach debugger? [[Y/n]"

    call screen battle_screen

    python:
        _ghost_outcome = battle_outcome()
        battle_finish()

    if _ghost_outcome == "defeat":
        scene bg_police_office with glitch_transition
        show jb determined at char_left
        "The connection drops. The loop scatters back into the walls — still running, still his. You walk out anyway. Free. But it isn't dead."
        jump colonel_victory_resolution

    $ store._colonel_true_ending = True
    jump colonel_victory_resolution


label colonel_victory_resolution:

    ## Pacifist — reached and beat the Colonel having defeated no other enemy
    ## (every ladder/boss fight fled). The Colonel's own fight doesn't count.
    python:
        if getattr(store, '_run_kills', 0) == 0:
            unlock_achievement("pacifist")
        ## Peace Was Never An Option — reached and beat the Colonel having
        ## skipped no fight (every ladder rung + act boss engaged, none fled).
        if getattr(store, '_run_fled', 0) == 0:
            unlock_achievement("peace_never_option")

    ## True ending if you broke the loop inside the machine; otherwise the
    ## normal escape. The pacifist / peace checks above apply to BOTH paths.
    if getattr(store, '_colonel_true_ending', False):
        jump colonel_true_ending
    ## Normal victory: escaped
    jump good_ending
