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

    ## JBDARK trigger — sustained 95+ hatred AND nightmare wolf event triggered.
    ## The reality breaks before the fight can happen.
    python:
        _hp_days = getattr(store, '_hatred_peak_days', 0)
        _nw      = getattr(store, '_nightmare_wolf_triggered', False)
        if _hp_days >= 3 and _nw:
            renpy.jump("jbdark_ending")

    play music "audio/tension_theme.mp3" fadein 1.0

    call screen arc_title_card("III", "THE RECKONING") with arc_fade

    ## --- Round 1: The Waiting ---
    call colonel_round_one from _call_colonel_round_one

    ## --- Round 2: His Entrance ---
    call colonel_round_two from _call_colonel_round_two

    ## --- Initialize the deck battle ---
    python:
        battle_init()

        ## Apply pre-battle legacy debuff
        if stats.final_boss_buff == "IMPOSTER_SYNDROME":
            battle_state.player_hp = max(1, battle_state.player_hp - 10)
            renpy.say(None, "[[DEBUFF]]: You feel like a fraud. -10 HP at battle start.")

        ## Biohacker compound state — same logic as before, applied to BattleState
        _bh_withdrawal = (stats.player_class == "biohacker" and nootropic_dependency and nootropic_last_tier == 0)
        _bh_flmod      = (stats.player_class == "biohacker" and nootropic_last_tier == 5)

        if _bh_withdrawal:
            battle_state.player_hp = max(1, battle_state.player_hp - 15)
            renpy.say(None, "[[WITHDRAWAL — BIOHACKER]]: Tremors. Shallow breath. Walking in already compromised. -15 HP.")
        elif _bh_flmod:
            battle_state.player_max_hp += 15
            battle_state.player_hp += 15
            battle_state.max_energy += 1
            renpy.say(None, "[[FLModafinil — BIOHACKER]]: Peak cognitive state. Dopamine locked. +15 HP, +1 max energy/turn (stacks with PROTOCOL).")

    ## --- Run the deck battle ---
    play music "audio/colonel_arrives.mp3" fadein 1.0
    scene bg_police_office with glitch_transition
    show colonel normal at char_right

    "He invites you upstairs. He makes coffee. The silence is heavy."
    colonel "'Black? Two sugars?' he asks."
    "Then, he attacks."

    $ battle_start_player_turn()

    call screen battle_screen

    ## --- Resolve outcome ---
    python:
        _outcome = battle_outcome()
        battle_finish()

    if _outcome == "defeat":
        jump colonel_defeat_ending

    ## CORRUPT chain — overrides any victory type. ÚRNA gets you regardless of how clean the fight was.
    python:
        if getattr(store, 'corrupt_chain_3_completed', False):
            renpy.jump("happy_nation_ending")

    ## REUNION trigger — won the fight but stats can't sustain a dev career.
    ## Need BOTH unhireable coding AND insufficient runway — single-stat fail still
    ## allows a normal good ending, since the other stat covers the gap.
    python:
        if stats.coding_skill < 70 and stats.available_money < 25000:
            renpy.jump("reunion_ending")

    if _outcome == "victory_close":
        jump colonel_close_victory

    if _outcome == "victory_pyrrhic":
        jump colonel_pyrrhic_victory

    ## victory_perfect — earn the glitch phase
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

    "It is early morning. You hand your superior the resignation."
    "'I need to call the Colonel.'"
    "Three hours later, the black Superb arrives. He sits inside for 5 minutes."
    "Watching the building. Watching the parking lot. Watching nothing."
    "You stand at the window."
    "Your hands either steady themselves, or they don't."
    "The deck you spent 24 days building will tell you which."

    return


## ---------------------------------------------------------------------------
## ROUND 2 — His Entrance (narrative only)
## ---------------------------------------------------------------------------

label colonel_round_two:

    scene bg_police_office with glitch_transition
    show colonel normal at char_right

    "He enters. The room goes silent. Your colleagues look down."
    "He doesn't acknowledge them."
    "He invites you upstairs."
    "You follow."

    if stats.player_class == "bodybuilder":
        colonel "'You filled out.'"
        colonel "'You take up more of the doorway than you used to. The chair too.'"
        colonel "'Iron body. Iron will. {i}Limited vocabulary.{/i}'"
        "He sets his coffee down on the far side of the desk. Clearing the space between you."
    elif stats.player_class == "dark_empath":
        colonel "'You haven't blinked since you walked in.'"
        colonel "'Most men in your position look at the floor. Or the certificates on the wall. Something safe.'"
        colonel "'You're looking at me like you already know how this ends.'"
        "He starts to glance toward the window — and stops himself. Leans back in the chair instead."
    elif stats.player_class == "biohacker":
        colonel "'Your pupils are wide. Breathing's shallow. There's a sheen on your forehead the room doesn't justify.'"
        colonel "'Whatever you took, you took it about forty minutes ago. It's at the top of its curve right now.'"
        colonel "'Cute. We used to drink before a thing like this.'"
        "He fastens the top button he never fastens. Trimming a variable he can still control."

    return


## ---------------------------------------------------------------------------
## GLITCH PHASE — fires only on a perfect victory (HP >= 70%)
## ---------------------------------------------------------------------------

label colonel_glitch_phase:

    play music "audio/sevirra_lenoloc.mp3" fadein 1.0

    scene bg_police_office with glitch_transition

    "[[SYSTEM]]: Colonel HP = 0."
    "He stumbles back. His coffee cup hits the floor. The sound echoes wrong — too long, like a sound effect on a broken loop."
    "He looks at you. His mouth opens. Closes."

    pause 1.5

    scene bg_black with glitch_transition

    "[[ERROR]]: NPC_STATE.integrity = CRITICAL"
    "[[ERROR]]: Attempting rollback..."

    pause 0.8

    "[[ERROR]]: Rollback FAILED."
    "[[ERROR]]: Falling back to cached state — bureaucracy_protocol_v1.exe"

    pause 0.8

    scene bg_police_office with glitch_transition
    show colonel normal at char_right

    "He stands up straight."
    "His face rearranges itself into the exact expression from this morning. The same coffee mug. The same posture. The same dead certainty."

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

    if _return == "wake_up":
        jump colonel_glitch_wake_up

    if _return == "observe":
        "You say nothing."
        "He continues his speech."
        "He reaches the end of his monologue."
        "He starts it again."
        "On the third loop, you notice something."
        "His tie has a stain on it. Small. Left side. You never noticed it before."
        "He is mortal. He is small. He is a man in a room who is afraid of being forgotten."
        "You almost feel sorry for him."
        "Almost."
        jump colonel_glitch_loop_exit

    ## _return == "argue" (or anything else) — restart the loop
    scene bg_police_office with glitch_transition
    "You open your mouth. You say the words."
    "He pours another coffee."
    "His expression doesn't change."
    "The argument is already starting again from line 1."
    "{color=#ff2222}You are trapped in the argument forever.{/color}"
    "(You realize something. Fighting the loop only feeds the loop. Type a way out.)"
    jump colonel_glitch_loop


label colonel_glitch_loop_exit:

    "You stop fighting."
    "You stop arguing."
    "You look at him with absolute clarity."
    jb "'...This isn't about me at all, is it.'"
    "He doesn't respond. He never will."
    "You turn around and walk toward the door."
    jump colonel_victory_resolution


label colonel_glitch_wake_up:

    $ unlock_achievement("wake_up_call")

    scene bg_black with glitch_transition

    "You take one breath."
    "You stop performing for him."
    "The argument dissolves like smoke."
    "It never had any weight. It was just noise."

    pause 1.0

    scene bg_police_office with dissolve
    show jb determined at char_left

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
        ## Perfect-ending check: only reached AFTER beating the colonel
        if stats.coding_skill >= 150 and stats.available_money >= 150000 and stats.pcr_hatred <= 30:
            renpy.jump("escape_artist_ending")

    ## Normal victory: escaped
    jump good_ending
