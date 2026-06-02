################################################################################
## REFACTOR — Recurring "Station Texture" Events
##
## Short, low-stakes StS-style beats that do NOT drain from the run pool — they
## recur, filling the slots between the marquee ev_* events so the precinct
## keeps breathing across the 30 days. Listed in RECURRING_EVENTS
## (events/event_engine.rpy); fired by random_event_check / Overtime as the
## fallback when no unseen marquee event is queued.
##
## Design contract (same as the marquee layer, lighter numbers): trade in
## HP / CZK / hatred only, every choice costs something real, no "no change"
## branch. Two choices each, kept tight — these are seasoning, not set-pieces.
################################################################################

label evr_the_briefing:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _br_art = "images/events/evr_the_briefing.jpg"
        _br_body = [
            "Morning briefing. The duty board has one line nobody is looking at — a callout in the worst part of the district, the kind that eats a shift and pays in paperwork.",
            "The room has gone very interested in its own boots. The sergeant's pen hovers over the unassigned column.",
            "He could write any name there. He is waiting to see if he has to.",
        ]
        _br_choices = [
            {
                "id": "take",
                "label": "[ TAKE THE DETAIL ]",
                "desc": eg("+ {:,} CZK".format(stats.money_gain_preview(2000))) + ".  " + ec("+ 6 Hatred") + ".  The call nobody wanted, and now it's yours.",
            },
            {
                "id": "pass",
                "label": "[ STUDY YOUR BOOTS ]",
                "desc": eg("- 4 Hatred") + ".  Someone else's name goes up. You let the relief be enough.",
            },
        ]

    call screen event_screen(title="THE BRIEFING", art=_br_art, body=_br_body, choices=_br_choices)

    python:
        _br_pick = _return
        if _br_pick == "take":
            stats.increment_stats_value_money(2000)
            stats.increment_stats_pcr_hatred(6)
            _br_res = [
                "You put your hand up before the sergeant has to choose, and something in the room relaxes that you will resent later.",
                "The callout is exactly as long and as thankless as advertised. You log it clean and drive home in the grey.",
                eg("+ {:,} CZK.".format(stats.money_gain_preview(2000))) + "   " + ec("+ 6 Hatred."),
            ]
        else:
            stats.increment_stats_pcr_hatred(-4)
            _br_res = [
                "You hold very still and let the silence do its work. The pen moves to another column. Another name.",
                "It is a small cowardice and it costs you nothing you can name. You take the lightness of it out to the car.",
                eg("- 4 Hatred."),
            ]

    call screen event_outcome(title="THE BRIEFING", art=_br_art, result=_br_res)
    return


label evr_coffee_machine:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _cf_art = "images/events/evr_coffee_machine.jpg"
        _cf_afford = stats.available_money >= 500
        _cf_body = [
            "The coffee machine on the second floor is working today, which happens about as often as a clean Friday.",
            "It is bad coffee. It is the specific bad coffee you have been drinking for ten years, and right now your hands could use something warm to hold.",
        ]
        _cf_choices = [
            {
                "id": "buy",
                "label": "[ SHIFT FUEL ]",
                "desc": ec("- 500 CZK") + ".  " + eg("+ 7 HP") + ".  Burnt, too hot, exactly right.",
                "enabled": _cf_afford,
                "locked": "You count the coins in your pocket and come up short. Even this.",
            },
            {
                "id": "skip",
                "label": "[ BLACK, FROM THE THERMOS ]",
                "desc": eg("- 3 Hatred") + ".  The one ritual the building hasn't taken from you yet.",
            },
        ]

    call screen event_screen(title="THE COFFEE MACHINE", art=_cf_art, body=_cf_body, choices=_cf_choices)

    python:
        _cf_pick = _return
        if _cf_pick == "buy":
            stats.try_spend_money(500)
            _cf_healed = event_heal(7)
            _cf_res = [
                "You feed it the coins and it actually delivers, which feels like being owed something and getting it for once.",
                "You drink it standing at the window over the car park. For four minutes you are nobody's problem and nobody is yours.",
                ec("- 500 CZK.") + "   " + eg("+ {} HP.".format(_cf_healed)),
            ]
        else:
            stats.increment_stats_pcr_hatred(-3)
            _cf_res = [
                "You pour from the steel thermos your father carried before you, black, no sugar, the way the job is supposed to be taken.",
                "It is a small fixed point. You hold it a moment longer than the coffee needs holding.",
                eg("- 3 Hatred."),
            ]

    call screen event_outcome(title="THE COFFEE MACHINE", art=_cf_art, result=_cf_res)
    return


label evr_locker_room:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _lk_art = "images/events/evr_locker_room.jpg"
        _lk_body = [
            "The locker room, end of shift. A colleague two benches down is offering to swap his easy Sunday for your night rotation — he's got a kid's thing, he says, and he'd owe you.",
            "He's also holding the overtime slip he could sign over instead, if you'd rather have the money than the favour.",
            "He doesn't much care which. He just wants out of Sunday.",
        ]
        _lk_choices = [
            {
                "id": "swap",
                "label": "[ TAKE THE EASY SUNDAY ]",
                "desc": eg("- 5 Hatred") + ".  A soft shift, and a man who owes you one.",
            },
            {
                "id": "cash",
                "label": "[ TAKE HIS SLIP INSTEAD ]",
                "desc": eg("+ {:,} CZK".format(stats.money_gain_preview(2500))) + ".  " + ec("+ 5 Hatred") + ".  You'll work the night. You'll take the money.",
            },
        ]

    call screen event_screen(title="THE LOCKER ROOM", art=_lk_art, body=_lk_body, choices=_lk_choices)

    python:
        _lk_pick = _return
        if _lk_pick == "swap":
            stats.increment_stats_pcr_hatred(-5)
            _lk_res = [
                "You take the Sunday. He claps your shoulder too hard, grateful in the way men are when they don't want to say it.",
                "The soft shift is genuinely soft. You'd forgotten the job could be like this — slow, human, almost kind.",
                eg("- 5 Hatred."),
            ]
        else:
            stats.increment_stats_value_money(2500)
            stats.increment_stats_pcr_hatred(5)
            _lk_res = [
                "You take the slip. He blinks, recalculates you, signs it over anyway. You'll see the disappointment again somewhere down the line.",
                "The night rotation is the night rotation. But the money is real, and money is the only door out of here you can see.",
                eg("+ {:,} CZK.".format(stats.money_gain_preview(2500))) + "   " + ec("+ 5 Hatred."),
            ]

    call screen event_outcome(title="THE LOCKER ROOM", art=_lk_art, result=_lk_res)
    return


label evr_bad_call:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _bc_art = "images/events/evr_bad_call.jpg"
        _bc_body = [
            "Some calls don't leave when the shift does. This one rides home in the passenger seat — nothing you did wrong, nothing you could have done, which is the part that won't sit still.",
            "You're parked outside your building with the engine ticking as it cools. The flat upstairs is dark and quiet and yours.",
            "Or the station is still lit, and there is always more to do, and doing is easier than feeling.",
        ]
        _bc_choices = [
            {
                "id": "sit",
                "label": "[ SIT WITH IT ]",
                "desc": eg("- 6 Hatred") + ".  " + ec("- 4 HP") + ".  Let the night be heavy. Sleep badly. Carry less of it tomorrow.",
            },
            {
                "id": "bury",
                "label": "[ BURY IT IN WORK ]",
                "desc": eg("+ {:,} CZK".format(stats.money_gain_preview(2500))) + ".  " + ec("+ 7 Hatred") + ".  Turn the car around. Doing is easier than feeling.",
            },
        ]

    call screen event_screen(title="AFTER THE CALL", art=_bc_art, body=_bc_body, choices=_bc_choices)

    python:
        _bc_pick = _return
        if _bc_pick == "sit":
            stats.increment_stats_pcr_hatred(-6)
            _bc_lost = event_hurt(4)
            _bc_res = [
                "You go up. You don't turn the big light on. You sit at the kitchen table and let the call be exactly as bad as it was, no smaller.",
                "You sleep badly and wake hollow, but the thing has loosened its grip by a notch. You can put it down. That's the whole trick — you have to actually put it down.",
                eg("- 6 Hatred.") + "   " + ec("- {} HP.".format(_bc_lost)),
            ]
        else:
            stats.increment_stats_value_money(2500)
            stats.increment_stats_pcr_hatred(7)
            _bc_res = [
                "You turn the car around. There is always a form, a follow-up, a thing that pays. You work until the call is just one more line in a long night of lines.",
                "It works the way it always works: the money is real and the feeling waits. It is patient. It will be there when you finally stop moving.",
                eg("+ {:,} CZK.".format(stats.money_gain_preview(2500))) + "   " + ec("+ 7 Hatred."),
            ]

    call screen event_outcome(title="AFTER THE CALL", art=_bc_art, result=_bc_res)
    return
