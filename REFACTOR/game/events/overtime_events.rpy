################################################################################
## REFACTOR — Overtime Shift Events ("?" pool)
##
## Slay-the-Spire-style "?" encounters bound to the night-shift activity.
## You opt into uncertainty by volunteering for the extra shift; the night
## resolves into one of these 2-option encounters, or the flat roll once the
## pool drains. The pool drains per run — encounters never repeat.
##
## Wired from activity_night_shift (script.rpy) via _roll_overtime_event().
## The +5,000 CZK / +15 Hatred base shift cost is already paid before any of
## these fire — every delta below stacks on top of that.
################################################################################

init python:

    def _roll_overtime_event():
        """Decide whether tonight's overtime is a '?' encounter.

        Returns an ot_* label name (and drains it from the pool), or None to
        fall through to the flat night-shift roll. The first overtime of a run
        is always an encounter; after that it is a 60% chance.
        """
        import random
        if not hasattr(store, 'overtime_event_pool'):
            store.overtime_event_pool = [
                "ot_long_quiet",
                "ot_the_envelope",
                "ot_the_call",
                "ot_holding_cell",
                "ot_factory_fence",
            ]
        if not hasattr(store, '_overtime_taken'):
            store._overtime_taken = 0
        store._overtime_taken += 1
        if not store.overtime_event_pool:
            return None
        if store._overtime_taken == 1 or random.randint(1, 100) <= 60:
            ev = random.choice(store.overtime_event_pool)
            store.overtime_event_pool.remove(ev)
            return ev
        return None


## ---------------------------------------------------------------------------
## THE LONG QUIET — dead-time decision (coding vs. rest)
## ---------------------------------------------------------------------------

label ot_long_quiet:

    scene bg_random_event

    "Three in the morning. The radio has been silent for two hours."
    "Your partner is asleep against the window. The town is a row of dark windows and one buzzing streetlight."
    "Dead time. Hours of it, and you are being paid for all of them."

    menu:
        "Open the laptop. Study while it's quiet. [[+12 Coding, +6 Hatred]":
            python:
                stats.increment_stats_coding_skill(12)
                stats.increment_stats_pcr_hatred(6)
            "You prop the screen below the dashboard so the light doesn't carry."
            "Python until the sky goes grey. If a sergeant walked past you'd be writing a report instead — but no one walks past out here."
            "You learned something. You also spent the whole night hiding it."
            window hide
            show screen outcome_panel("+12 CODING, +6 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Recline the seat. Sleep. [[-10 Hatred]":
            $ stats.increment_stats_pcr_hatred(-10)
            "You drop the radio to a whisper and close your eyes."
            "Four hours of nobody needing anything from you. It is the closest thing to peace the uniform has ever given you."
            window hide
            show screen outcome_panel("-10 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## THE ENVELOPE — dirty cash + a Hatred card, or walk away
## ---------------------------------------------------------------------------

label ot_the_envelope:

    scene bg_police_interior

    "End of the shift. A senior officer you know by face, not name, stops at your desk."
    "He sets a padded envelope on the keyboard. Doesn't let go of it yet."
    "'Quiet job tonight. A few of us split it. You were on shift, so — you were part of it. That's how it works.'"

    menu:
        "Take the cut. [[+3,000 CZK, +12 Hatred] [[CARD: RED MIST]":
            python:
                stats.increment_stats_value_money(3000)
                stats.increment_stats_pcr_hatred(12)
            "You take the envelope. He nods, like you've passed a test you never signed up for."
            "Three thousand crowns you didn't earn, for a job you didn't do, that you can never ask about."
            "Something tightens in your chest and stays tight."
            window hide
            show screen outcome_panel("+3,000 CZK, +12 PCR HATRED.")
            pause
            hide screen outcome_panel
            python:
                offer_card("red_mist", "NIGHT SHIFT")

        "Leave it on the desk. [[-6 Hatred]":
            $ stats.increment_stats_pcr_hatred(-6)
            "'Not part of it,' you say, and you're out the door before he can answer."
            "You'll be the cop who left the envelope now. That has a cost too — but it's one you can carry."
            window hide
            show screen outcome_panel("-6 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## THE CALL — effort for callout pay + a card, or clock out on time
## ---------------------------------------------------------------------------

label ot_the_call:

    scene bg_random_event

    "Last hour of the shift. Dispatch crackles: a drunk causing a scene outside the herna on the square."
    "Your car is the closest. Dispatch knows it. The other unit is twenty minutes out and in no hurry to close the gap."
    "It is the kind of call that is either five minutes or the whole rest of your night."

    menu:
        "Take it. [[+1,500 CZK, +8 Hatred] [[CARD: CUFF 'EM]":
            python:
                stats.increment_stats_value_money(1500)
                stats.increment_stats_pcr_hatred(8)
            "It's the whole rest of your night. He swings, he misses, he cries, he swings again."
            "By the time the wagon takes him you've earned the callout pay twice over and slept none of it."
            window hide
            show screen outcome_panel("+1,500 CZK, +8 PCR HATRED.")
            pause
            hide screen outcome_panel
            python:
                offer_card("cuff_em", "NIGHT SHIFT")

        "Let dispatch reroute it. [[-5 Hatred]":
            $ stats.increment_stats_pcr_hatred(-5)
            "'Show me unavailable,' you tell the radio. The drunk is the other unit's problem now."
            "You clock out on time for once. Small mercy. You take them where the job allows."
            window hide
            show screen outcome_panel("-5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## THE HOLDING CELL — humane release, or process by the book for overtime pay
## ---------------------------------------------------------------------------

label ot_holding_cell:

    scene bg_police_interior

    "The holding cell has one occupant tonight — a teenager, maybe sixteen, picked up for spraying tags on the shutter of the closed culture house."
    "He's already done the maths on his own face: bored, scared, pretending neither."
    "The arresting officer went home an hour ago. The paperwork is yours if you want it. So is the kid."

    menu:
        "Lose the paperwork. Send him home. [[-10 Hatred]":
            $ stats.increment_stats_pcr_hatred(-10)
            "You walk him to the door at 4 AM. 'I never saw you. Go home the long way.'"
            "He doesn't thank you. He just goes, fast, before you change your mind."
            "You spent ten years becoming someone who could do that quietly. Tonight it was {stshl=worth it}."
            window hide
            show screen outcome_panel("-10 PCR HATRED.")
            pause
            hide screen outcome_panel

        "Process him. By the book. [[+1,200 CZK, +8 Hatred]":
            python:
                stats.increment_stats_value_money(1200)
                stats.increment_stats_pcr_hatred(8)
            "Prints, photo, a charge sheet for a can of paint and a dead building nobody has loved in years."
            "The overtime pays for the hour it takes. The kid gets a record. The system gets fed."
            window hide
            show screen outcome_panel("+1,200 CZK, +8 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## THE FACTORY FENCE — chase for recovered-goods pay + a card, or let it go
## ---------------------------------------------------------------------------

label ot_factory_fence:

    scene bg_random_event

    "Three in the morning, the industrial road. Your headlights catch a hatchback parked at the fence of the old chemical works."
    "Two men, bolt cutters, a coil of copper cable already half in the boot. The plant has been dead fifteen years. The copper hasn't."
    "One of them sees the car. He runs."

    menu:
        "Run him down. [[+2,000 CZK, +6 Hatred] [[CARD: GUT PUNCH]":
            python:
                stats.increment_stats_value_money(2000)
                stats.increment_stats_pcr_hatred(6)
            "You catch him at the treeline. He's faster than you'd like and softer than he thinks."
            "Recovered-goods bonus on the cable, and a body that remembers exactly how it brought a man down."
            window hide
            show screen outcome_panel("+2,000 CZK, +6 PCR HATRED.")
            pause
            hide screen outcome_panel
            python:
                offer_card("gut_punch", "NIGHT SHIFT")

        "Note the plate. Call it in. [[-6 Hatred]":
            $ stats.increment_stats_pcr_hatred(-6)
            "You read the registration into the radio and let him have his head start."
            "Copper off the corpse of a factory. At 3 AM you cannot make yourself care who carries it away."
            window hide
            show screen outcome_panel("-6 PCR HATRED.")
            pause
            hide screen outcome_panel

    return
