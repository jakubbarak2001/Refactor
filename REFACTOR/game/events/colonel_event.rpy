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
    play music "audio/dum_bez_dveri.mp3" fadein 1.0

    "He sits. He squares a deck of cards on the desk between you. The silence is heavy."
    "Then, he attacks."

    $ battle_start_player_turn()

    call screen battle_screen

    ## --- Resolve outcome ---
    python:
        _outcome = battle_outcome()
        battle_finish()

    ## Outcome routing — reunion_ending temporarily hidden.
    ## Any non-defeat outcome (perfect / pyrrhic / close) routes to good_ending
    ## via the glitch phase. Defeat also routes to good_ending as a stopgap until
    ## reunion is re-enabled. To restore the original split, uncomment the block
    ## below and remove the unconditional jump.
    ##
    ## if _outcome == "defeat":
    ##     $ store._reunion_via_defeat = True
    ##     jump reunion_ending
    ## if _outcome != "victory_perfect" or (stats.coding_skill < 70 and stats.available_money < 25000):
    ##     jump reunion_ending

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

    voice "audio/voice/col_04_out_of_your_mind.ogg"
    colonel "ARE YOU OUT OF YOUR FUCKING MIND?!"

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

    return


## ---------------------------------------------------------------------------
## GLITCH PHASE — fires only on a perfect victory (HP >= 70%)
## ---------------------------------------------------------------------------

label colonel_glitch_phase:

    stop music fadeout 1.5

    scene bg_colonel_office_shaken with glitch_transition
    show colonel shaken at char_right

    "[[SYSTEM]: Colonel HP = 0."

    pause 0.5

    "He stumbles. The deck slides off the desk and the sound arrives a second too late."
    "His mouth opens. Closes. No breath behind it."

    pause 0.8

    scene bg_black with glitch_transition

    "[[ERROR]: NPC_STATE.integrity = CRITICAL"
    "[[ERROR]: Rollback FAILED. Reverting to cached state — bureaucracy_protocol_v1.exe"

    pause 1.0

    scene bg_police_office with glitch_transition
    show colonel normal at char_right

    "The room reassembles. The desk slides back together. He stands up straight."
    "But the geometry is too clean. The light has no source. The air has stopped moving."

    pause 0.6

    "He is looping."
    "{i}police_bureaucracy.exe{/i} — runtime: 32 years."

    pause 0.6

    colonel "'You are a {b}COWARD{/b}, JB! You were never fit for this force!'"

    "The opening line. Word for word."

    pause 0.8

    "His eyes are already moving to the next one."
    "He isn't waiting for your answer."
    "He never was."

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

    pause 0.5

    "You take one breath."
    "It is yours. Not a line you have rehearsed answering with. Just air. Just a lung that is alive."

    pause 0.7

    "You stop performing for him."
    "The argument — every variant of it, every version, every if-then branch you have ever memorised — dissolves like smoke."
    "It never had any weight."
    "It was just noise."

    pause 1.0

    scene bg_police_office with dissolve
    ## Colonel restored to "normal" — the scripted, dead-certain version JB
    ## walked in on. JB on smirk: "I see through you, finally" — fits the
    ## "no volume, no anger" cue better than determined (which reads as
    ## committed-but-fighting). JB has TRANSCENDED the fight here.
    show colonel normal at char_right
    show jb smirk at char_left

    "The office is just an office again."
    "Concrete walls. Brass nameplate. A man behind a desk, mouth open mid-line, the rest of his speech still queued up behind his teeth."

    pause 0.5

    jb "'I'm done.'"

    "Two words."
    "No volume. No anger."

    pause 0.6

    "You take your resignation letter out of your jacket pocket. You unfold it. You smooth it once against the edge of his desk."
    "You place it in his hand."
    "His fingers close around it on muscle memory."
    "His eyes don't change. His mouth keeps moving."

    pause 0.6

    jump colonel_victory_resolution


label colonel_victory_resolution:

    ## Normal victory: escaped
    jump good_ending
