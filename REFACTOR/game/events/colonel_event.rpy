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

    ## Outcome routing.
    ## CORRUPT chain overrides everything: ÚRNA gets you regardless of fight quality.
    ## Only a perfect victory with sustainable stats earns the triumphant good_ending —
    ## the glitch phase confirms JB actually broke the loop. Everything else routes
    ## to reunion_ending, the "six months later you walked back to the station" coda:
    ##   - close/pyrrhic victory (any stats)
    ##   - perfect victory with stat-starved life
    ##   - defeat (lost the argument but walked out anyway — the "I'm doing it
    ##     anyway" defiance beat is gated on _reunion_via_defeat in reunion_ending)
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

    stop music fadeout 1.5

    scene bg_colonel_office_shaken with glitch_transition
    show colonel shaken at char_right

    "[[SYSTEM]: Colonel HP = 0."

    pause 0.5

    "He stumbles. One step back. Then another."
    "The deck slides off the desk in a slow, painterly arc — fifty-two suits and ranks fanning across the parquet — and the sound of the cards hitting the floor arrives a full second too late, drawn out like a dragged audio file."
    "The Czech flag is on fire. Half the ceiling is gone. The wind through the empty window-frame has no temperature."

    pause 0.8

    "He looks at you."
    "His mouth opens. Closes. Opens. The shape of words but no breath behind them."
    "Thirty-two years of being the man in this room and his face cannot find a single expression that fits being beaten by his son."

    pause 1.0

    scene bg_black with glitch_transition

    "[[ERROR]: NPC_STATE.integrity = CRITICAL"
    "[[ERROR]: Attempting rollback..."

    pause 0.8

    "[[ERROR]: Rollback FAILED."
    "[[ERROR]: Reverting to cached state — bureaucracy_protocol_v1.exe"
    "[[ERROR]: Reloading scene_assets..."

    pause 1.2

    scene bg_police_office with glitch_transition
    show colonel normal at char_right

    "The room reassembles itself around him."
    "The plaster un-cracks. The flagpole un-bends. The framed certificates float back into their grid, glass un-shattering itself in a faint reverse-tinkle. The Czech flag re-knits itself out of its own ash."
    "The desk — split in two a moment ago — slides back together along its own seam."

    pause 0.5

    "He stands up straight."
    "His shoulders square."
    "His face rearranges itself into the exact expression he wore when you walked into this office for the first time, twenty years ago, as a recruit who didn't know any better."

    pause 0.6

    "But you can feel it — every detail of this room is wrong now in a way you cannot name. The geometry is too clean. The light has no source. The air has stopped moving."
    "Your blood runs cold."
    "He is looping."
    "He can't see you. He cannot process what just happened because there is no line of code for it."

    pause 0.6

    "He is not a man."
    "He is a script."
    "{i}police_bureaucracy.exe{/i} — runtime: 32 years."

    pause 0.6

    "He opens his mouth."
    colonel "'You are a {b}COWARD{/b}, JB! You were never fit for this force!'"

    "And there it is."
    "The opening line."
    "Word for word, syllable for syllable, the same gravel in the throat, the same fleck of spit on the last consonant."
    "Every fight you have ever lost with him rises up at once and pulls — pulls hard — at the front of your chest, the back of your throat, the muscle behind your jaw that wants to start talking."
    "Defend yourself. Justify. Argue. Win this time."

    pause 0.8

    "But then you look at his eyes."
    "They are already moving to the next line."
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
