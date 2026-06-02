################################################################################
## REFACTOR — Bodybuilder Class Arc: THE TRAINER (Iron Garden)
##
## The BB-only 3-stage arc. JB is the only playable class and previously had NO
## arc (class_arc_check returned None for bodybuilder). This fills that hole in
## the polished StS event_screen style (not the old menu style the DE/BH arcs
## use).
##
## Premise: a real competitor-turned-coach at Iron Garden clocks JB's frame and
## starts pulling him toward an amateur strongman meet — a SECOND exit door that
## competes with the tech door, the way Martin's offer does, but through iron.
## The thematic payoff: the platform was never the escape; it was proof he could
## become something — which is exactly what he needs for the keyboard, or the
## Colonel, on day thirty.
##
## Fired by class_arc_check() (events/class_arcs.rpy) on the random-event days
## inside each stage's window: Stage 1 days 6-12, Stage 2 13-18, Stage 3 19-27.
## Stages advance store.bb_arc_stage (1/2/3, or -1 if the player closes it).
## Trades in SOMA / cards / HP / CZK / hatred / coding.
################################################################################

label bb_trainer_eye:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _te_art = "images/events/bb_trainer_eye.jpg"
        _te_body = [
            "Iron Garden, the deadlift platform in the back where the chalk hangs in the air. You pull a heavy single, drop it, and when you straighten up there is a man watching you who wasn't there before.",
            "Older. Built the way men are built who competed once and never quite stopped — thick through the back, a knee that doesn't bend right. He waited for you to finish before he spoke. That alone tells you what he is.",
            "'You're strong off the floor and you don't know what to do with it,' he says. 'I coach. Regional meet's in three weeks. I could have you ready. You'd surprise yourself.'",
        ]
        _te_choices = [
            {
                "id": "commit",
                "label": "[ LET HIM PROGRAM YOU ]",
                "desc": eg("+ 2 SOMA") + ".  A second door out — through the platform, not the keyboard.",
            },
            {
                "id": "decline",
                "label": "[ THE IRON STAYS MINE ]",
                "desc": eg("- 6 Hatred") + ".  You don't lift to be looked at. You lift so the week can't reach you.",
            },
        ]

    call screen event_screen(title="THE EYE", art=_te_art, body=_te_body, choices=_te_choices)

    python:
        _te_pick = _return
        if _te_pick == "commit":
            store.bb_arc_stage = 1
            add_soma(2)
            _te_res = [
                "You give him your number. He doesn't smile — he writes a program on the back of a receipt, four days, percentages off your single, and tells you to stop dropping the bar like you're ashamed of it.",
                "You train it that night. It's the first thing in weeks that asked something of you and gave a straight answer back.",
                eg("+ 2 SOMA.") + "   The line is open.",
            ]
        else:
            store.bb_arc_stage = -1
            stats.increment_stats_pcr_hatred(-6)
            _te_res = [
                "'No,' you say. 'I'm not training for a room full of people.' He nods like he's heard it before and goes back to chalking his hands.",
                "You finish your session alone, the way you came. The iron doesn't owe anyone a performance, and neither, tonight, do you.",
                eg("- 6 Hatred."),
            ]

    call screen event_outcome(title="THE EYE", art=_te_art, result=_te_res)
    return


label bb_trainer_meet:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _tm_art = "images/events/bb_trainer_meet.jpg"
        _tm_body = [
            "Three weeks out. The coach slides a registration form across the bench like it's already decided. 'Sign it. Entry's paid — consider it mine. You just have to show up and pull.'",
            "The meet is the same week you'd blocked out for the screens and the studying, the other door, the one with a keyboard behind it. You can feel both pulling at the same forty-eight hours.",
            "He sees you do the arithmetic. 'A man can only walk through one door at a time,' he says. 'But you can train for one with everything, or both with half.'",
        ]
        _tm_choices = [
            {
                "id": "train",
                "label": "[ TRAIN THROUGH IT — EVERYTHING ON THE PLATFORM ]",
                "desc": eg("+ 3 SOMA") + ", " + eg("a strong card") + ".  " + ec("+ 10 Hatred") + ".  The other door goes dark for a while.",
                "preview_card": "heavy_set",
            },
            {
                "id": "split",
                "label": "[ SPLIT THE FORTY-EIGHT HOURS ]",
                "desc": eg("+ 1 SOMA") + ", " + eg("+ 8 Coding") + ".  " + ec("+ 4 Hatred") + ".  Both doors, half of you in each.",
            },
            {
                "id": "pull",
                "label": "[ PULL OUT OF THE MEET ]",
                "desc": eg("+ 15 HP") + ", " + eg("- 8 Hatred") + ".  Hand the form back. Rest the body. Keep the week for yourself.",
            },
        ]

    call screen event_screen(title="THE MEET DATE", art=_tm_art, body=_tm_body, choices=_tm_choices)

    python:
        _tm_pick = _return

    if _tm_pick == "train":
        python:
            store.bb_arc_stage = 2
            add_soma(3)
            stats.increment_stats_pcr_hatred(10)
            _tm_card = can_offer_card("heavy_set")
        if _tm_card:
            call screen card_offer_screen(card=_tm_card, source_label="THE COACH'S PROGRAM")
            $ commit_card("heavy_set", _return == "take")
        python:
            _tm_res = [
                "You sign. For three weeks the meet is the only thing that's real — every set a rehearsal, the keyboard a thing you'll get back to after, when you've proven you can finish something you started.",
                "The coach works you like he means it. Your numbers move. So does the clock you're not looking at.",
                eg("+ 3 SOMA.") + "   " + ec("+ 10 Hatred.") + "   The program is in your hands.",
            ]
    elif _tm_pick == "split":
        python:
            store.bb_arc_stage = 2
            add_soma(1)
            stats.increment_stats_coding_skill(8)
            stats.increment_stats_pcr_hatred(4)
            _tm_res = [
                "You try to carry both. Mornings on the platform, nights behind the screen, neither getting the version of you that isn't already spent on the other.",
                "It half-works, which is its own specific exhaustion. But you're still standing in both doorways, and some weeks that's the whole victory.",
                eg("+ 1 SOMA.") + "   " + eg("+ 8 Coding.") + "   " + ec("+ 4 Hatred."),
            ]
    else:
        python:
            store.bb_arc_stage = -1
            _tm_healed = event_heal(15)
            stats.increment_stats_pcr_hatred(-8)
            _tm_res = [
                "You hand the form back. He takes it without a word, folds it once, and you understand the line is closed — not unkindly, just closed.",
                "You sleep eight hours for the first time in a month. The body, given nothing to prove, simply repairs. Some weeks that's the smarter lift.",
                eg("+ {} HP.".format(_tm_healed)) + "   " + eg("- 8 Hatred."),
            ]

    call screen event_outcome(title="THE MEET DATE", art=_tm_art, result=_tm_res)
    return


label bb_trainer_platform:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _tp_art = "images/events/bb_trainer_platform.jpg"
        _tp_body = [
            "Meet day. A municipal sports hall that smells of ammonia and old varnish, forty lifters and their families on plastic chairs, a platform under hard white light. Your name is on the board, spelled right.",
            "The coach tapes your thumbs and says nothing useful, which is the most useful thing. 'Last attempt's the one that counts,' is all. 'The rest is just earning the right to take it.'",
            "Out past the chalk, your phone has the other door in it — the screens, the keyboard, the week you traded for this. You could still walk. Nobody out there knows you're entered.",
        ]
        _tp_choices = [
            {
                "id": "platform",
                "label": "[ STEP ONTO THE PLATFORM ]",
                "desc": eg("+ 3 SOMA") + ", " + eg("a finisher card") + ".  " + ec("+ 8 Hatred") + ".  Take the last attempt. Find out.",
                "preview_card": "the_final_set",
            },
            {
                "id": "walk",
                "label": "[ WALK — SPEND IT ON THE REAL DOOR ]",
                "desc": eg("- 10 Hatred") + ", " + eg("+ 12 Coding") + ".  The platform was the proof. Now go use it.",
            },
        ]

    call screen event_screen(title="THE PLATFORM", art=_tp_art, body=_tp_body, choices=_tp_choices)

    python:
        _tp_pick = _return

    if _tp_pick == "platform":
        python:
            store.bb_arc_stage = 3
            add_soma(3)
            stats.increment_stats_pcr_hatred(8)
            _tp_card = can_offer_card("the_final_set")
        if _tp_card:
            call screen card_offer_screen(card=_tp_card, source_label="THE LAST ATTEMPT")
            $ commit_card("the_final_set", _return == "take")
        python:
            unlock_achievement("iron_platform")
            _tp_res = [
                "You take the last attempt. The bar is heavier than anything you've owned and for one second nothing in your life moves — then it does, all of it, slow and total and entirely yours.",
                "You don't remember locking it out. You remember the down command, and the coach's hand on the back of your neck, and the specific knowledge, new and permanent, that you can become something if you decide to.",
                "You'll need that knowledge on day thirty. You earned it where they couldn't see.",
                eg("+ 3 SOMA.") + "   " + ec("+ 8 Hatred.") + "   The platform was real.",
            ]
    else:
        python:
            store.bb_arc_stage = 3
            stats.increment_stats_pcr_hatred(-10)
            stats.increment_stats_coding_skill(12)
            _tp_res = [
                "You don't lift. You stand in the doorway of the hall long enough for the coach to find you and read your face, and he nods — no anger, just a man who's seen people choose the harder door before.",
                "The platform did its work without the bar ever leaving the floor. You came to find out if you could become something. You already know. Now you go spend it on the door that actually leads out.",
                eg("- 10 Hatred.") + "   " + eg("+ 12 Coding.") + "   You walk out lighter than you came in.",
            ]

    call screen event_outcome(title="THE PLATFORM", art=_tp_art, result=_tp_res)
    return
