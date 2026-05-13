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
    show colonel normal at char_right

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
    play music "audio/colonel_arrives.mp3" fadein 1.0

    "He sits. He squares a deck of cards on the desk between you. The silence is heavy."
    "Then, he attacks."

    $ battle_start_player_turn()

    call screen battle_screen

    ## --- Resolve outcome ---
    python:
        _outcome = battle_outcome()
        battle_finish()

    ## Outcome routing.
    ## CORRUPT chain overrides everything: ÚRNA gets you regardless of fight quality.
    ## Only a perfect victory with sustainable stats earns the triumphant good_ending —
    ## the glitch phase confirms JB actually broke the loop. Everything else routes
    ## to reunion_ending, the "six months later you walked back to the station" coda:
    ##   - close/pyrrhic victory (any stats)
    ##   - perfect victory with stat-starved life
    ##   - defeat (lost the argument but walked out anyway — the "I'm doing it
    ##     anyway" defiance beat is gated on _reunion_via_defeat in reunion_ending)
    python:
        if getattr(store, 'corrupt_chain_3_completed', False):
            renpy.jump("happy_nation_ending")

    if _outcome == "defeat":
        $ store._reunion_via_defeat = True
        jump reunion_ending

    if _outcome != "victory_perfect" or (stats.coding_skill < 70 and stats.available_money < 25000):
        jump reunion_ending

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

    scene bg_police_office with glitch_transition
    show colonel normal at char_right

    "The third-floor office. He's at the window, hands behind his back, watching the lot where his car is parked."

    show colonel smug at char_right with dissolve

    if stats.player_class == "bodybuilder":
        colonel "'So you really did it.' He looks you over, unhurried. 'All that iron in the body. None of it in the spine.'"
    elif stats.player_class == "dark_empath":
        colonel "'So you really did it.' A thin smile. 'You walked in here reading the room like it owes you something. You always did mistake watching people for understanding them.'"
    elif stats.player_class == "biohacker":
        colonel "'So you really did it.' He almost laughs. 'Pupils like dinner plates. You optimized yourself right out of a pension. Cute.'"

    show colonel normal at char_right with dissolve
    show jb determined at char_left with dissolve

    jb "'Quit the chatter, Colonel. Sit down. Deal the cards.'"

    return


## ---------------------------------------------------------------------------
## GLITCH PHASE — fires only on a perfect victory (HP >= 70%)
## ---------------------------------------------------------------------------

label colonel_glitch_phase:

    play music "audio/sevirra_lenoloc.mp3" fadein 1.0

    scene bg_police_office with glitch_transition
    show colonel shaken at char_right

    "[[SYSTEM]: Colonel HP = 0."
    "He stumbles back. The deck slides off the desk, cards fanning across the floor. The sound echoes wrong — too long, like a sound effect on a broken loop."
    "He looks at you. His mouth opens. Closes."

    pause 1.5

    scene bg_black with glitch_transition

    "[[ERROR]: NPC_STATE.integrity = CRITICAL"
    "[[ERROR]: Attempting rollback..."

    pause 0.8

    "[[ERROR]: Rollback FAILED."
    "[[ERROR]: Falling back to cached state — bureaucracy_protocol_v1.exe"

    pause 0.8

    scene bg_police_office with glitch_transition
    show colonel normal at char_right

    "He stands up straight."
    "His face rearranges itself into the exact expression from when you walked in. The same squared deck. The same posture. The same dead certainty."

    "Your blood runs cold."
    "He is looping."
    "He can't see you. He cannot process what just happened because there is no line of code for it."
    "He is not a man. He is a script."
    "'police_bureaucracy.exe' — runtime: 32 years."

    "He opens his mouth."
    colonel "'You are a {b}COWARD{/b}, JB! You were never fit for this force!'"

    "You feel the familiar pull of the argument. The urge to prove yourself. To justify. To fight."
    "Every debate you have ever lost with him rises up at once."

    "But then you see it."
    "The loop."
    "His eyes are already moving to the next line of script."
    "He isn't waiting for your answer. He never was."

    jump colonel_glitch_loop


label colonel_glitch_loop:

    python:
        glitch_typing_init()

    call screen glitch_typing_screen

    ## Post-Phase-5D the screen only ever returns "wake_up" — typing the
    ## target string is the sole exit. ARGUE / OBSERVE buttons were stripped
    ## per playtest report (too much UI on the wake-up screen).
    jump colonel_glitch_wake_up


label colonel_glitch_wake_up:

    $ unlock_achievement("wake_up_call")

    scene bg_black with glitch_transition

    "You take one breath."
    "You stop performing for him."
    "The argument dissolves like smoke."
    "It never had any weight. It was just noise."

    pause 1.0

    scene bg_police_office with dissolve
    ## smirk reads as "I see through you, finally" — fits the
    ## "no volume, no anger" cue better than determined (which reads
    ## as committed-but-fighting). JB has TRANSCENDED the fight here.
    show jb smirk at char_left

    jb "'I'm done.'"
    "Two words. No volume. No anger."
    "You pick up your resignation letter from the desk. You fold it. You put it in his hand."
    "He doesn't move. He can't process the action."
    "You walk to the door."

    jump colonel_victory_resolution


label colonel_victory_resolution:

    ## Check if the corrupt cop chain was completed — overrides good ending
    python:
        if getattr(store, 'corrupt_chain_3_completed', False):
            renpy.jump("happy_nation_ending")

    ## Normal victory: escaped
    jump good_ending
