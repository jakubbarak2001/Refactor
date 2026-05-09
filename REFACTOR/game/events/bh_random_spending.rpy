################################################################################
## REFACTOR — Biohacker Random Spending Events
##
## BH-only "the cost of optimizing" pool. Fires on non-event days at ~30%.
## Each event is a small CZK drain with a "skip → take a stat hit" alternative.
## Pool reshuffles when exhausted so the same event can recur over a long run.
##
## Wired from day_start in script.rpy via `call bh_spending_check`.
################################################################################

init python:

    def check_bh_spending_event():
        """Roll for a BH-only spending event on non-event days.
        Returns a label name to call, or None.
        """
        _rand = __import__('random')

        if not hasattr(store, '_bh_spending_pool') or not store._bh_spending_pool:
            store._bh_spending_pool = [
                "bh_spend_red_light",
                "bh_spend_bacopa",
                "bh_spend_new_paper",
                "bh_spend_hrv_battery",
                "bh_spend_vendor_markup",
            ]
            _rand.shuffle(store._bh_spending_pool)

        if _rand.randint(1, 100) <= 30:
            return store._bh_spending_pool.pop(0)

        return None


## ---------------------------------------------------------------------------
## DISPATCHER — called from day_start on non-event days for BH players.
## ---------------------------------------------------------------------------

label bh_spending_check:

    python:
        _bh_label = None
        if stats and stats.player_class == "biohacker":
            _bh_label = check_bh_spending_event()

    if _bh_label is not None:
        call expression _bh_label from _call_bh_spend_dynamic
    else:
        pass

    return


## ---------------------------------------------------------------------------
## 1. RED LIGHT PANEL BURNOUT
## ---------------------------------------------------------------------------

label bh_spend_red_light:

    scene bg_police_interior
    play sound "audio/police_siren.mp3"

    "RED LIGHT PANEL BURNOUT"

    "21:00. You walk into the bedroom for your nightly red-light therapy. The panel is dark."
    "You poke it. Unplug, replug. Internal capacitor fried — you can hear the dead silence where the fan should be."
    "Replacement: 3,500 CZK plus shipping. Or skip the recovery protocol and pay in cortisol."

    menu:
        "Replace.":
            python:
                _cost = adjusted_cost(3500)
                _spent = stats.try_spend_money(_cost)
                if _spent:
                    _outcome = "- {:,} CZK. Panel back online tomorrow.".format(_cost)
                else:
                    stats.increment_stats_pcr_hatred(8)
                    _outcome = "+8 PCR HATRED. The recovery deficit lands."
            if not _spent:
                "[[INSUFFICIENT FUNDS] You can't afford it. The cortisol option picks itself."
            show screen outcome_panel(_outcome)
            pause
            hide screen outcome_panel

        "Skip. (+5 Hatred from disrupted recovery)":
            $ stats.increment_stats_pcr_hatred(5)
            "You sleep poorly. The data shows it. You log the regression and move on."
            show screen outcome_panel("+5 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## 2. BACOPA RUN-OUT
## ---------------------------------------------------------------------------

label bh_spend_bacopa:

    scene bg_police_interior
    play sound "audio/police_siren.mp3"

    "STACK GAP — BACOPA"

    "You shake the bottle. Empty. The Bacopa monnieri is the slow-acting one — you only notice it's been working when you stop."
    "You feel a paragraph slip out of your working memory while you're reading the morning news. That's it. That's the gap."
    "Restock: 1,200 CZK from the usual vendor. Or skip and feel it for a week."

    menu:
        "Restock.":
            python:
                _cost = adjusted_cost(1200)
                _spent = stats.try_spend_money(_cost)
                if _spent:
                    _outcome = "- {:,} CZK. Two pills daily. Back to baseline in two weeks.".format(_cost)
                else:
                    stats.increment_stats_coding_skill(-3)
                    _outcome = "-3 CODING SKILL. Memory dips this week."
            if not _spent:
                "[[INSUFFICIENT FUNDS] Wallet says no. You'll feel it."
            show screen outcome_panel(_outcome)
            pause
            hide screen outcome_panel

        "Skip. (-3 Coding from memory dip)":
            $ stats.increment_stats_coding_skill(-3)
            "You read the same paragraph three times. You log it. You move on."
            show screen outcome_panel("-3 CODING SKILL.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## 3. NEW PAPER DROP
## ---------------------------------------------------------------------------

label bh_spend_new_paper:

    scene bg_police_interior
    play sound "audio/police_siren.mp3"

    "NEW PAPER DROP"

    "Discord ping at 23:14. Someone in the cognitive-enhancement channel just shared a preprint."
    "Acetyl-L-carnitine + Alpha-GPC, 12-week trial, n=84, statistically significant on working-memory benchmarks."
    "You've never felt this much FOMO from a footnote. The compound stack is 4,500 CZK on the gray market."

    menu:
        "Buy. (+6 Coding from new compound)":
            python:
                _cost = adjusted_cost(4500)
                _spent = stats.try_spend_money(_cost)
                if _spent:
                    stats.increment_stats_coding_skill(6)
                    _outcome = "- {:,} CZK, +6 CODING SKILL. Two-week ramp-up. Curve looks good already.".format(_cost)
                else:
                    _outcome = "Bookmarked. The wallet has limits."
            if not _spent:
                "[[INSUFFICIENT FUNDS] You bookmark the paper. You'll come back to it. You won't."
            show screen outcome_panel(_outcome)
            pause
            hide screen outcome_panel

        "Skip.":
            "You close the tab. You will think about it for the next four nights."
            "Actually it's fine. Discipline is a stack input too."
            show screen outcome_panel("No change. (Discipline +0, FOMO undocumented.)")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## 4. HRV STRAP BATTERY FAILURE
## ---------------------------------------------------------------------------

label bh_spend_hrv_battery:

    scene bg_police_interior
    play sound "audio/police_siren.mp3"

    "HRV STRAP — BATTERY DEAD"

    "Morning HRV reading: ERROR. Not low. Not high. ERROR."
    "Strap battery is a CR2032. Hardware store has them for 90 CZK but the strap also needs a calibration session at the clinic."
    "Total: 1,500 CZK. Or sleep blind for a week."

    menu:
        "Replace.":
            python:
                _cost = adjusted_cost(1500)
                _spent = stats.try_spend_money(_cost)
                if _spent:
                    _outcome = "- {:,} CZK. Strap back online. Recovery score visible again.".format(_cost)
                else:
                    stats.increment_stats_pcr_hatred(6)
                    _outcome = "+6 PCR HATRED. Sleeping blind is sleeping anxious."
            if not _spent:
                "[[INSUFFICIENT FUNDS] Can't afford the calibration. Anxiety spike."
            show screen outcome_panel(_outcome)
            pause
            hide screen outcome_panel

        "Skip. (+4 Hatred from data anxiety)":
            $ stats.increment_stats_pcr_hatred(4)
            "You sleep without the strap. You wake up at 03:14 wondering what the deep-sleep score is."
            "There's no number. The number is not the night. You repeat that to yourself."
            show screen outcome_panel("+4 PCR HATRED.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## 5. VENDOR MARKUP
## ---------------------------------------------------------------------------

label bh_spend_vendor_markup:

    scene bg_police_interior
    play sound "audio/police_siren.mp3"

    "VENDOR MARKUP — TELEGRAM"

    "Your usual nootropic vendor pings on Telegram. 'Supply chain. EU customs. Prices up 35%% effective Friday.'"
    "He has a 200-piece stockpile at the old price if you commit before midnight. 2,000 CZK secures the buffer."
    "Pay now, or pay more later. Or — third option — start cycling off."

    menu:
        "Stockpile.":
            python:
                _cost = adjusted_cost(2000)
                _spent = stats.try_spend_money(_cost)
                if _spent:
                    _outcome = "- {:,} CZK. Buffer secured. The system holds.".format(_cost)
                else:
                    stats.increment_stats_pcr_hatred(3)
                    _outcome = "+3 PCR HATRED. Future-self pays the markup."
            if not _spent:
                "[[INSUFFICIENT FUNDS] He marks you down on the no-stockpile list. Cold."
            show screen outcome_panel(_outcome)
            pause
            hide screen outcome_panel

        "Decline. (+5 Hatred — withdrawal flavor)":
            $ stats.increment_stats_pcr_hatred(5)
            "You tell him you're cycling off. He says 'Sure' in the way that means 'see you next month.'"
            "Three nights later you reach for the bottle that isn't there. The hand remembers before the brain."
            show screen outcome_panel("+5 PCR HATRED. Tapering is also a stack input.")
            pause
            hide screen outcome_panel

    return
