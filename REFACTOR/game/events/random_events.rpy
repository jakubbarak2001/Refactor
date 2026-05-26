################################################################################
## REFACTOR — Random Events
##
## Slay-the-Spire-style choice events. Each ev_* label drives the event_screen
## / event_outcome flow (events/event_screen.rpy); shared helpers live in
## events/event_engine.rpy. The events are pooled in random_event_pool
## (script.rpy) and fire from random_event_check when the day-band battle
## ladder is dry.
##
## Design contract:
##   - Trade in HP / cards / CZK / hatred only. No "+1 coding" noise.
##   - Every choice costs something real. No "no change" branch.
##   - Outcomes can be hidden (a real gamble) and permanent (deck changes).
##   - art = "images/events/<id>.jpg" — a styled placeholder renders until the
##     illustration exists; no label change needed when art lands.
################################################################################

## ---------------------------------------------------------------------------
## re_israeli_developer — LEGACY KEEP. A pre-deckbuilder menu-style event, not
## in the event pool and currently unreferenced. It is the only setter of
## `flmodafinil_unlocked` (which gates the Biohacker arc + tier-5 nootropics).
## The Biohacker class is locked (BB-only scope), so this label is dormant —
## kept rather than deleted so that gate survives if BH is ever revived.
## ---------------------------------------------------------------------------

label re_israeli_developer:

    scene bg_random_event
    play sound "audio/police_siren.mp3"
    play music "audio/random_event_bed.wav" fadein 1.5

    "TEL AVIV PROFESSOR"

    "A fender-bender. The professor steps out of the damaged Mercedes, ignoring the chaos."
    "He looks at you, ignoring the uniform entirely."
    "'You have intelligent eyes. Tell me — do you write code?'"

    python:
        _can_code = stats.coding_skill >= 35 or stats.player_class == "biohacker"

    menu:
        "Talk code. [[+30 Coding, BH: FLMod source]" if _can_code:
            python:
                stats.increment_stats_coding_skill(30)
                _bh = (stats.player_class == "biohacker")
                if _bh:
                    flmodafinil_unlocked = True

            "Twenty minutes of pointers, GIL, scaling. He nods. Hands you his GitHub on a folded card."

            if stats.player_class == "biohacker":
                "Then, quieter: 'I notice things. You optimise everything — including yourself.'"
                "He slips you a Telegram handle. CRL-40,940 source. You pocket it."
                window hide
                show screen outcome_panel("+30 CODING  |  [CRL-40,940 SOURCE UNLOCKED]  [BIOHACKER]")
            else:
                window hide
                show screen outcome_panel("+30 CODING SKILL.")
            pause
            hide screen outcome_panel

        "Stay silent. [[+10 Coding]":
            $ stats.increment_stats_coding_skill(10)
            "He shrugs. Gives you sixty seconds on abstraction layers anyway."
            "You learn something. The fear chokes the rest."
            window hide
            show screen outcome_panel("+10 CODING SKILL.")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## THE VENDING MACHINE [surreal] — money or HP buys a card; the skip costs HP.
## ---------------------------------------------------------------------------

label ev_the_vending_machine:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _vm_art = "images/events/ev_the_vending_machine.jpg"
        ## Tier ladder: (cost CZK, +Max HP, +Hatred). Each take heals current
        ## HP by the same amount as the Max HP bump. After 3 takes the
        ## machine stops; the player can also kick out at any tier. HP gain
        ## escalates 6/8/10 so tier 3 isn't strictly worse ROI than tier 1 —
        ## press-your-luck needs reward-for-risk, not just cost-for-risk.
        _vm_ladder = [
            (1500, 6, 0),
            (3500, 8, 5),
            (7000, 10, 12),
        ]
        _vm_step = 0
        _vm_total_cost = 0
        _vm_total_hp = 0
        _vm_total_hat = 0

    label .vm_offer:

        python:
            _vm_cost, _vm_hp, _vm_hat = _vm_ladder[_vm_step]
            _vm_afford = (stats.available_money >= _vm_cost)

            if _vm_step == 0:
                _vm_body = [
                    "The drinks machine in the third-floor corridor has glowed the same dead green for as long as you have worked here.",
                    "Tonight the display has your name on it. Your badge number beneath it. Then, one character at a time: I HAVE WHAT YOU NEED.",
                    "The coin slot lights up. It is waiting.",
                ]
                _vm_label = "[ FEED IT ]"
            elif _vm_step == 1:
                _vm_body = [
                    "Something fell into the tray. You took it. It felt the way a thing feels when it was always going to be yours.",
                    "The display goes dark for one breath and then flickers back, brighter than before: I HAVE MORE.",
                    "The coin slot is warm now. The price has gone up.",
                ]
                _vm_label = "[ FEED IT AGAIN ]"
            else:
                _vm_body = [
                    "The second drop was heavier. You took that one too. The corridor has gone quiet in the way corridors do not normally go quiet.",
                    "The display, no fade this time: ONE MORE.",
                    "The machine is humming on a frequency you can feel in the back of your teeth.",
                ]
                _vm_label = "[ ONE MORE TIME ]"

            _vm_up_desc = ec("- {:,} CZK".format(_vm_cost)) + ".  " + eg("+ {} Max HP".format(_vm_hp)) + "."
            if _vm_hat > 0:
                _vm_up_desc += "  " + ec("+ {} Hatred".format(_vm_hat)) + "."

            _vm_choices = [
                {
                    "id": "upgrade",
                    "label": _vm_label,
                    "desc": _vm_up_desc,
                    "enabled": _vm_afford,
                    "locked": "The coin slot stays lit. You do not have {:,} CZK.".format(_vm_cost),
                },
                {
                    "id": "kick",
                    "label": "[ KICK IT AND WALK AWAY ]",
                    "desc": ec("Lose 5 HP") + ".  The glow follows you down the corridor.",
                },
            ]

        call screen event_screen(title="THE VENDING MACHINE", art=_vm_art, body=_vm_body, choices=_vm_choices)

        python:
            _vm_pick = _return

        if _vm_pick == "upgrade":
            python:
                stats.try_spend_money(_vm_cost)
                _event_ensure_run_hp()
                store.run_hp_max += _vm_hp
                store.run_hp = min(store.run_hp_max, store.run_hp + _vm_hp)
                if _vm_hat > 0:
                    stats.increment_stats_pcr_hatred(_vm_hat)
                _vm_total_cost += _vm_cost
                _vm_total_hp += _vm_hp
                _vm_total_hat += _vm_hat
                _vm_step += 1

            if _vm_step < 3:
                jump ev_the_vending_machine.vm_offer

            python:
                _vm_res = [
                    "The third drop is the heaviest. A glass thing, capped, that fits the palm of you that has been clenched for a week. It is still warm.",
                    "The display goes dark. The corridor goes dark. The hum stops. Whatever was in the machine is in you now.",
                    eg("+ {} Max HP".format(_vm_total_hp)) + "   " + ec("- {:,} CZK".format(_vm_total_cost)) + "   " + ec("+ {} Hatred.".format(_vm_total_hat)),
                ]
            call screen event_outcome(title="THE VENDING MACHINE", art=_vm_art, result=_vm_res)
            return

        python:
            _vm_lost = event_hurt(5)
            if _vm_total_hp > 0:
                _vm_kick_parts = [ec("- {} HP".format(_vm_lost))]
                _vm_kick_parts.append(eg("kept: + {} Max HP".format(_vm_total_hp)))
                _vm_kick_parts.append(ec("paid: {:,} CZK".format(_vm_total_cost)))
                if _vm_total_hat > 0:
                    _vm_kick_parts.append(ec("+ {} Hatred".format(_vm_total_hat)))
                _vm_res = [
                    "You walk past the slot. The display says nothing. You took what you came for and the machine knows it.",
                    "Somewhere behind you, in the dark corridor, the glow keeps your name a little longer than it should.",
                    "   ".join(_vm_kick_parts) + ".",
                ]
            else:
                _vm_res = [
                    "You kick it once, hard, in the place a person would keep a knee. Your foot tells you about it for the rest of the shift.",
                    "The machine glows. Your name is still on the display when you reach the stairs.",
                    ec("- {} HP.".format(_vm_lost)),
                ]

        call screen event_outcome(title="THE VENDING MACHINE", art=_vm_art, result=_vm_res)
        return


## ---------------------------------------------------------------------------
## THE SMELL ON THE THIRD FLOOR [surreal] — a hidden roll behind a warm door.
## ---------------------------------------------------------------------------

label ev_the_smell:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _sm_art = "images/events/ev_the_smell.jpg"
        _sm_body = [
            "Panelak, eighth floor. A neighbour called about the smell on the landing. Nobody has been reported missing. Nobody is ever reported missing here.",
            "The door is warm. You put your palm flat against it and it is warm, evenly, all over — as if something behind it is still running.",
            "The lock turns before you have finished deciding to turn it.",
        ]
        _sm_choices = [
            {
                "id": "open",
                "label": "[ OPEN THE DOOR ]",
                "desc": ek("A gamble.") + "  " + eg("Best case: - 6 Hatred.") + "  " + ec("Worst: + 18 Hatred, gain a card.") + "  Even odds.",
            },
            {
                "id": "seal",
                "label": "[ SEAL IT. LOSE THE ADDRESS. ]",
                "desc": eg("- 8 Hatred") + ".  " + ec("Gain an unplayable card (dead weight).") + "  The not-knowing stays.",
            },
            {
                "id": "call",
                "label": "[ WAIT FOR THE SPECIALISTS ]",
                "desc": ec("Lose 6 HP") + ".  " + eg("+ 2,000 CZK callout pay."),
            },
        ]

    call screen event_screen(title="THE SMELL ON THE THIRD FLOOR", art=_sm_art, body=_sm_body, choices=_sm_choices)

    python:
        _sm_pick = _return
        _sm_tier = _battle_ladder_band(day_cycle.current_day)
        _sm_res = []

    if _sm_pick == "open":
        python:
            _sm_roll = __import__('random').randint(1, 100)
        if _sm_roll <= 55:
            python:
                stats.increment_stats_pcr_hatred(-6)
                _sm_res = [
                    "It is a chest freezer. Unplugged a week ago when the power was cut for unpaid bills. Inside, a hunter's whole autumn — boar, venison — gone soft and loud with flies.",
                    "No one. Just meat, and a man somewhere too ashamed of the bills to come back for it.",
                    "You laugh, once, in the empty flat. The first time in days something turned out to be nothing.",
                    eg("- 6 Hatred."),
                ]
        else:
            python:
                stats.increment_stats_pcr_hatred(18)
                _sm_pool = pick_battle_rewards(_sm_tier)
                if _sm_pool:
                    grant_card(__import__('random').choice(_sm_pool), silent=True)
                _sm_res = [
                    "It is not a freezer.",
                    "You do the work. You document it the way the work is documented. It takes until morning and it does not leave when you do.",
                    "On the table, among the things that outlived their owner, there is one you keep. You tell yourself it is evidence. You do not log it.",
                    ec("+ 18 Hatred.") + "   " + eg("Gained a card."),
                ]

    elif _sm_pick == "seal":
        python:
            stats.increment_stats_pcr_hatred(-8)
            grant_card("compromise", silent=True)
            _sm_res = [
                "You write the address down wrong. A transposed digit, a tired hand — the kind of mistake nobody audits.",
                "By the time anyone notices, it will not be your shift, your district, your problem.",
                "You sleep fine. Something useless and heavy settles into the deck of you and does not leave.",
                eg("- 8 Hatred.") + "   " + ec("Gained a dead card."),
            ]

    else:
        python:
            _sm_lost = event_hurt(6)
            stats.increment_stats_value_money(2000)
            _sm_res = [
                "You call it up the chain and then do the part nobody trains you for: you wait. Four hours in a concrete corridor that smells of the thing behind the door.",
                "The specialists come at dawn, unhurried, gloved. You sign where they point and drive home with the windows down.",
                ec("- {} HP.".format(_sm_lost)) + "   " + eg("+ 2,000 CZK."),
            ]

    call screen event_outcome(title="THE SMELL ON THE THIRD FLOOR", art=_sm_art, result=_sm_res)
    return


## ---------------------------------------------------------------------------
## THE DESIGNER OF FORMS [grounded-absurd] — pay CZK to upgrade / transform /
## remove cards. The deck-craft event. Skip costs HP.
## ---------------------------------------------------------------------------

label ev_designer_of_forms:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _df_art = "images/events/ev_designer_of_forms.jpg"
        _df_up_pool   = [c for c in player_deck.cards if is_upgradeable(c)]
        _df_up_count  = len(_df_up_pool)

        _df_grieve_ok = _df_up_count >= 1
        _df_grieve_lock = "Nothing in your file can be sharpened further."

        _df_exp_ok = (stats.available_money >= 2500) and _df_up_count >= 1
        if stats.available_money < 2500:
            _df_exp_lock = "Expedited filing runs 2,500 CZK."
        else:
            _df_exp_lock = "Nothing in your file can be sharpened further."

        _df_full_ok = (stats.available_money >= 7500) and _df_up_count >= 1
        if stats.available_money < 7500:
            _df_full_lock = "Full reprocessing runs 7,500 CZK."
        else:
            _df_full_lock = "Nothing in your file can be sharpened further."

        _df_body = [
            "Records, sub-basement. The man behind the desk has been redrawing the same arrest form since 2007. Box 4b has moved nine times.",
            "The walls are papered with rejected drafts. He does not look up. 'You. Your paperwork. I have read it. It is structurally unsound.'",
            "'I can process it. Properly. There are tiers of service.'",
        ]
        _df_choices = [
            {
                "id": "grievance",
                "label": "[ FILE A GRIEVANCE ]",
                "desc": ec("FREE") + ".  " + eg("Pick 1 card. He sharpens it."),
                "enabled": _df_grieve_ok,
                "locked": _df_grieve_lock,
            },
            {
                "id": "expedited",
                "label": "[ EXPEDITED FILING ]",
                "desc": ec("2,500 CZK") + ".  " + eg("He sharpens 2 random cards."),
                "enabled": _df_exp_ok,
                "locked": _df_exp_lock,
            },
            {
                "id": "full",
                "label": "[ FULL REPROCESSING ]",
                "desc": ec("7,500 CZK") + ".  " + eg("He sharpens 3 random cards."),
                "enabled": _df_full_ok,
                "locked": _df_full_lock,
            },
        ]

    call screen event_screen(title="THE DESIGNER OF FORMS", art=_df_art, body=_df_body, choices=_df_choices)

    python:
        _df_pick = _return
        _df_res = []

    if _df_pick == "grievance":
        python:
            _df_up = [c for c in player_deck.cards if is_upgradeable(c)]
        call screen event_card_picker("CHOOSE A CARD TO SHARPEN", _df_up)
        python:
            upgrade_card_in_deck(_return)
            _df_res = [
                "He takes your file into the back. Machine sounds — a stapler, or teeth. He returns it warmer than paper should be.",
                "It came back sharper than it went in. He has already forgotten you.",
                eg("Upgraded a card."),
            ]

    elif _df_pick == "expedited":
        $ stats.try_spend_money(2500)
        python:
            _df_up = [c for c in player_deck.cards if is_upgradeable(c)]
            __import__('random').shuffle(_df_up)
            _df_done = 0
            for _df_cid in _df_up[:2]:
                if upgrade_card_in_deck(_df_cid):
                    _df_done += 1
            _df_res = [
                "He stamps the file twice without reading it. Two pages come out of the machine with serial numbers that did not exist five minutes ago.",
                "You do not get to choose what he sharpened. You get what he decides you need.",
                ec("- 2,500 CZK.") + "   " + eg("Upgraded {} card(s).".format(_df_done)),
            ]

    elif _df_pick == "full":
        $ stats.try_spend_money(7500)
        python:
            _df_up = [c for c in player_deck.cards if is_upgradeable(c)]
            __import__('random').shuffle(_df_up)
            _df_done = 0
            for _df_cid in _df_up[:3]:
                if upgrade_card_in_deck(_df_cid):
                    _df_done += 1
            _df_res = [
                "He reads the whole file this time. Every box. He pulls three pages, feeds them to the machine, and they come back warmer than paper should be.",
                "Three things made sharper. You did not pick which. You will live with all of them.",
                ec("- 7,500 CZK.") + "   " + eg("Upgraded {} card(s).".format(_df_done)),
            ]

    call screen event_outcome(title="THE DESIGNER OF FORMS", art=_df_art, result=_df_res)
    return


## ---------------------------------------------------------------------------
## THE LOST & FOUND [grounded-absurd] — remove a card (HP or CZK), or take one
## that was never yours (Hatred).
## ---------------------------------------------------------------------------

label ev_lost_and_found:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _lf_art = "images/events/ev_lost_and_found.jpg"
        _lf_rem_avail = any(c not in CLASS_SIGNATURE_CARDS for c in player_deck.cards)
        _lf_body = [
            "The property room. Mrs. Hajkova has run it for thirty years, and she knows, she says, what belongs to whom — and what was never anyone's to keep.",
            "She looks at you the way she looks at her shelves. 'You're carrying something that isn't doing you any good. I can take it off the books.'",
            "'Records get lost. It happens. The question is what you'll give me for the favour.'",
        ]
        _lf_choices = [
            {
                "id": "sidearm",
                "label": "[ HAND OVER YOUR SIDEARM FOR AN HOUR ]",
                "desc": ec("Lose 9 HP") + ".  " + eg("Remove a card.") + "  An hour unarmed is a long hour.",
                "enabled": _lf_rem_avail,
                "locked": "She looks through your deck and finds nothing she is willing to lose.",
            },
            {
                "id": "pay",
                "label": "[ PAY HER 5,000 CZK ]",
                "desc": ec("5,000 CZK") + ".  " + eg("Remove a card."),
                "enabled": (stats.available_money >= 5000) and _lf_rem_avail,
                "locked": ("Need 5,000 CZK." if stats.available_money < 5000 else "She finds nothing in your deck she will take."),
            },
            {
                "id": "take",
                "label": "[ TAKE A BOX THAT ISN'T YOURS ]",
                "desc": ec("+ 12 Hatred") + ".  " + eg("Gain a card.") + "  Someone, somewhere, is still looking for it.",
            },
        ]

    call screen event_screen(title="THE LOST & FOUND", art=_lf_art, body=_lf_body, choices=_lf_choices)

    python:
        _lf_pick = _return
        _lf_tier = _battle_ladder_band(day_cycle.current_day)
        _lf_res = []

    if _lf_pick == "sidearm":
        python:
            _lf_lost = event_hurt(9)
            _lf_rem = [c for c in player_deck.cards if c not in CLASS_SIGNATURE_CARDS]
        call screen event_card_picker("CHOOSE A CARD TO LOSE ON THE BOOKS", _lf_rem)
        python:
            player_deck.remove(_return)
            _lf_res = [
                "She locks your sidearm in a drawer and slides a claim ticket across. 'One hour.'",
                "You walk an hour of corridor without the weight on your hip, and your body spends the whole hour noticing.",
                "When you come back, the ticket is gone and so is the thing you wanted gone.",
                ec("- {} HP.".format(_lf_lost)) + "   " + eg("Removed a card."),
            ]

    elif _lf_pick == "pay":
        $ stats.try_spend_money(5000)
        python:
            _lf_rem = [c for c in player_deck.cards if c not in CLASS_SIGNATURE_CARDS]
        call screen event_card_picker("CHOOSE A CARD TO LOSE ON THE BOOKS", _lf_rem)
        python:
            player_deck.remove(_return)
            _lf_res = [
                "She counts the notes twice, slow, and does not write a receipt.",
                "'It was never here,' she says. 'Neither were you.' The shelf where it sat is already holding something else.",
                ec("- 5,000 CZK.") + "   " + eg("Removed a card."),
            ]

    else:
        python:
            stats.increment_stats_pcr_hatred(12)
            _lf_trio = pick_battle_rewards(_lf_tier)
        call screen card_reward_trio_screen(_lf_trio)
        python:
            _lf_card = _return
            if _lf_card and _lf_card != "skip":
                grant_card(_lf_card, silent=True)
            _lf_res = [
                "She watches you lift the box and says nothing, which is its own kind of saying something.",
                "It is good. It is useful. It belonged to someone who came in once, frightened, and never came back for it.",
                "You carry it out. It is yours now, the way most things become yours: by nobody stopping you.",
                ec("+ 12 Hatred.") + ("   " + eg("Gained a card.") if (_lf_card and _lf_card != "skip") else ""),
            ]

    call screen event_outcome(title="THE LOST & FOUND", art=_lf_art, result=_lf_res)
    return


## ---------------------------------------------------------------------------
## THE COLONEL SENDS HIS REGARDS [surreal] — a strong card now, the next fight
## harder; or burn it (HP); or refuse it (CZK + Hatred relief).
## ---------------------------------------------------------------------------

label ev_colonel_regards:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _cr_art = "images/events/ev_colonel_regards.jpg"
        _cr_body = [
            "There is a box outside your door. No courier waited. No label, no stamp — just your name, in handwriting you have spent ten years learning to read upside down across a desk.",
            "Inside: one card, face-down. And a note.",
            ek("\"Thought of you. Wear it well.  — K.\""),
        ]
        _cr_choices = [
            {
                "id": "keep",
                "label": "[ KEEP IT ]",
                "desc": eg("Gain a strong card") + ".  " + ec("Next enemy: + 3 Strength."),
            },
            {
                "id": "burn",
                "label": "[ BURN IT IN THE SINK ]",
                "desc": ec("Lose 10 HP") + ".  You will watch it the whole way down.",
            },
            {
                "id": "return",
                "label": "[ COURIER IT BACK, UNOPENED ]",
                "desc": ec("7,000 CZK") + ".  " + eg("- 15 Hatred") + ".  A clean refusal, and not a cheap one.",
                "enabled": (stats.available_money >= 7000),
                "locked": "A courier across the country costs 7,000 CZK. You do not have it.",
            },
        ]

    call screen event_screen(title="THE COLONEL SENDS HIS REGARDS", art=_cr_art, body=_cr_body, choices=_cr_choices)

    python:
        _cr_pick = _return
        _cr_res = []

    if _cr_pick == "keep":
        python:
            _cr_trio = pick_battle_rewards("hard")
        call screen card_reward_trio_screen(_cr_trio)
        python:
            _cr_card = _return
            if _cr_card and _cr_card != "skip":
                grant_card(_cr_card, silent=True)
            store._next_enemy_strength_bonus = 3
            _cr_res = [
                "You take it out of the box. It is good — better than good. It is exactly the thing you would have chosen for yourself, which is the part that makes your hands cold.",
                "He knows what you are building. He has always known.",
                "Somewhere, a file with your name on it gets a note added to it, and the next man he sends will have read that note.",
                (eg("Gained a card.") + "   " if (_cr_card and _cr_card != "skip") else "") + ec("The next fight: enemy +3 Strength."),
            ]

    elif _cr_pick == "burn":
        python:
            _cr_lost = event_hurt(10)
            _cr_res = [
                "You hold it under the tap, strike a match, and watch. It does not burn like paper. It takes its time.",
                "You do not sleep. You sit with the smell of it until the window goes grey, turning over every reason a man like that sends a gift, and finding the same answer each time.",
                ec("- {} HP.".format(_cr_lost)),
            ]

    else:
        python:
            stats.try_spend_money(7000)
            stats.increment_stats_pcr_hatred(-15)
            _cr_res = [
                "You do not open it. You pay a courier the better part of a week's wage to drive it back across the country and put it in his hands exactly as it came.",
                "He will understand the message. It cost you to send it. That is the message.",
                "Your spine, for once, is the straightest thing in the room.",
                ec("- 7,000 CZK.") + "   " + eg("- 15 Hatred."),
            ]

    call screen event_outcome(title="THE COLONEL SENDS HIS REGARDS", art=_cr_art, result=_cr_res)
    return


## ---------------------------------------------------------------------------
## PILLS, PROBABLY [grounded-absurd] — swallow one (hidden roll: heal or
## hurt + curse), sell them (CZK + Hatred), or flush them (HP).
## ---------------------------------------------------------------------------

label ev_pills:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _pl_art = "images/events/ev_pills.jpg"
        _pl_body = [
            "Vehicle search, routine, one in the morning. Under the passenger seat: a sandwich bag of pills. No markings. No two of them quite the same.",
            "The driver swears they aren't his. They are never anyone's.",
            "Your hand closes around the bag. The shift has six hours left in it and you have not slept properly since March.",
        ]
        _pl_choices = [
            {
                "id": "swallow",
                "label": "[ SWALLOW ONE ]",
                "desc": ek("A gamble.") + "  " + eg("Best case: + 30 HP.") + "  " + ec("Worst: - 14 HP, gain a dead card.") + "  Roughly even odds.",
            },
            {
                "id": "sell",
                "label": "[ SELL THEM ]",
                "desc": eg("+ 6,000 CZK") + ".  " + ec("+ 10 Hatred") + ".  You know a man. You wish you didn't.",
            },
            {
                "id": "flush",
                "label": "[ FLUSH THEM ]",
                "desc": ec("Lose 4 HP") + ".  You stand over the bowl longer than the act requires.",
            },
        ]

    call screen event_screen(title="PILLS, PROBABLY", art=_pl_art, body=_pl_body, choices=_pl_choices)

    python:
        _pl_pick = _return
        _pl_res = []

    if _pl_pick == "swallow":
        python:
            _pl_roll = __import__('random').randint(1, 100)
        if _pl_roll <= 55:
            python:
                _pl_healed = event_heal(30)
                _pl_res = [
                    "It is small and white and tastes of nothing. For twenty minutes nothing happens.",
                    "Then the night goes soft at the edges. The radio is far away. The cold is far away. You finish the shift like a man walking downhill, and you sleep like the dead and wake up repaired.",
                    eg("+ {} HP.".format(_pl_healed)),
                ]
        else:
            python:
                _pl_lost = event_hurt(14)
                grant_card("compromise", silent=True)
                _pl_res = [
                    "It is small and white and tastes of nothing. For twenty minutes nothing happens.",
                    "Then your heart does something a heart should not do, twice, and your hands stop being yours for a while. You finish the shift on a kind of autopilot you will not be able to account for later.",
                    "Something moves into you on the comeback down and does not pay rent.",
                    ec("- {} HP.".format(_pl_lost)) + "   " + ec("Gained a dead card."),
                ]

    elif _pl_pick == "sell":
        python:
            stats.increment_stats_value_money(6000)
            stats.increment_stats_pcr_hatred(10)
            _pl_res = [
                "You know a man who buys things with no markings and asks no questions, and the worst part is how easy his number was to find in your own phone.",
                "Six thousand crowns for a bag you logged as empty. The driver was right: they were never anyone's. Now they are someone's problem, and you chose who.",
                eg("+ 6,000 CZK.") + "   " + ec("+ 10 Hatred."),
            ]

    else:
        python:
            _pl_lost = event_hurt(4)
            _pl_res = [
                "You tip the bag into the bowl and flush, and then you stand there longer than the act requires, because some tired animal part of you wanted those, badly, and is not done being angry about it.",
                ec("- {} HP.".format(_pl_lost)),
            ]

    call screen event_outcome(title="PILLS, PROBABLY", art=_pl_art, result=_pl_res)
    return


## ---------------------------------------------------------------------------
## THE MAN WHO BUYS UNIFORMS [grounded-absurd] — sell a Police card for CZK,
## transform a card for CZK, or refuse and take the curse.
## ---------------------------------------------------------------------------

label ev_uniform_collector:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _uc_art = "images/events/ev_uniform_collector.jpg"
        _uc_police = [c for c in player_deck.cards
                      if CARD_LIBRARY.get(c, {}).get("color") == "Police"
                      and c not in CLASS_SIGNATURE_CARDS]
        _uc_body = [
            "A flat on the top floor, and a man who collects uniforms. Mannequins line the hallway — tram driver, postman, miner, police.",
            "'The costumes of people who were never asked what they wanted to be,' he says, fond. 'I would like a piece of yours. I pay well, and I pay strangely.'",
            "He is already holding a tape measure. He is already looking at your shoulders.",
        ]
        _uc_choices = [
            {
                "id": "badge",
                "label": "[ SELL HIM THE BADGE-WORK ]",
                "desc": eg("+ 8,000 CZK") + ".  " + ec("Remove a Police card.") + "  He buys a piece of the job itself.",
                "enabled": bool(_uc_police),
                "locked": "He wants the police in you, and finds you are not carrying it just now.",
            },
            {
                "id": "memory",
                "label": "[ SELL HIM A MEMORY ]",
                "desc": eg("+ 3,000 CZK") + ".  " + ec("You pick a card; it becomes a random card of the same rarity."),
            },
            {
                "id": "refuse",
                "label": "[ REFUSE, AND MEET HIS EYES ]",
                "desc": ec("Gain an unplayable card (dead weight).") + "  His stare follows you home.",
            },
        ]

    call screen event_screen(title="THE MAN WHO BUYS UNIFORMS", art=_uc_art, body=_uc_body, choices=_uc_choices)

    python:
        _uc_pick = _return
        _uc_res = []

    if _uc_pick == "badge":
        python:
            _uc_police = [c for c in player_deck.cards
                          if CARD_LIBRARY.get(c, {}).get("color") == "Police"
                          and c not in CLASS_SIGNATURE_CARDS]
        call screen event_card_picker("CHOOSE THE BADGE-WORK TO SELL", _uc_police)
        python:
            player_deck.remove(_return)
            stats.increment_stats_value_money(8000)
            _uc_res = [
                "He does not want the cloth. He wants the thing the cloth taught your hands to do, and somehow, with the tape measure, he takes it.",
                "Eight thousand crowns. A mannequin in his hallway stands a little straighter now, wearing a competence that used to be yours.",
                eg("+ 8,000 CZK.") + "   " + ec("Removed a Police card."),
            ]

    elif _uc_pick == "memory":
        python:
            _uc_deck = list(player_deck.cards)
        call screen event_card_picker("CHOOSE A MEMORY TO SELL", _uc_deck)
        python:
            event_transform_card(_return)
            stats.increment_stats_value_money(3000)
            _uc_res = [
                "He asks you to think of something while he measures. You do. He nods, satisfied, and the thought goes out of you and into a notebook you do not see him close.",
                "Where the memory was, there is now a different one. It works just as well. It was simply never yours.",
                eg("+ 3,000 CZK.") + "   " + eg("Transformed a card."),
            ]

    else:
        python:
            grant_card("compromise", silent=True)
            _uc_res = [
                "'No,' you say, and you hold his eyes while you say it, because you will not give him the flinch either.",
                "He smiles, untroubled, and goes back to his mannequins. But the stare does not stay in the flat. It rides the tram home with you. It is still there when you turn off the light.",
                ec("Gained a dead card."),
            ]

    call screen event_outcome(title="THE MAN WHO BUYS UNIFORMS", art=_uc_art, result=_uc_res)
    return


## ---------------------------------------------------------------------------
## KARAOKE NIGHT AT U SLUNCE [grounded-absurd] — peace (Hatred relief), power
## (a card + Hatred + curse), or profit (CZK + Hatred).
## ---------------------------------------------------------------------------

label ev_karaoke:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _kk_art = "images/events/ev_karaoke.jpg"
        _kk_body = [
            "Station karaoke night, back room of U Slunce. Someone has Nedved on. Someone always has Nedved on.",
            "Three beers in, the colleague next to you stops singing and tells you a thing. A real thing — with a date on it, and a name.",
            "Then he goes back to the chorus as if he hadn't. But you heard it. And he knows you heard it.",
        ]
        _kk_choices = [
            {
                "id": "forget",
                "label": "[ FORGET YOU HEARD IT ]",
                "desc": eg("- 12 Hatred") + ".  Some things weigh less the moment you decide not to carry them.",
            },
            {
                "id": "use",
                "label": "[ USE IT ]",
                "desc": eg("Gain a strong card") + ".  " + ec("+ 15 Hatred.") + "  " + ec("Gain 2 unplayable cards (dead weight)."),
            },
            {
                "id": "report",
                "label": "[ REPORT IT ]",
                "desc": eg("+ 3,000 CZK") + ".  " + ec("+ 10 Hatred") + ".  The room will go cold around you.",
            },
        ]

    call screen event_screen(title="KARAOKE NIGHT AT U SLUNCE", art=_kk_art, body=_kk_body, choices=_kk_choices)

    python:
        _kk_pick = _return
        _kk_res = []

    if _kk_pick == "forget":
        python:
            stats.increment_stats_pcr_hatred(-12)
            _kk_res = [
                "You let it go past you the way you let the chorus go past you. You buy him the next beer. You sing the Nedved badly, on purpose, and he laughs.",
                "There is a date and a name you could have kept. You decide, deliberately, not to know them. It is the lightest you have felt in weeks.",
                eg("- 12 Hatred."),
            ]

    elif _kk_pick == "use":
        python:
            _kk_trio = pick_battle_rewards("hard")
        call screen card_reward_trio_screen(_kk_trio)
        python:
            _kk_card = _return
            if _kk_card and _kk_card != "skip":
                grant_card(_kk_card, silent=True)
            stats.increment_stats_pcr_hatred(15)
            grant_card("compromise", silent=True)
            grant_card("compromise", silent=True)
            _kk_res = [
                "You wait until Monday. You let him see you waiting. By Wednesday he understands the arrangement without either of you naming it, and the arrangement is good for you.",
                "Leverage is just a thing you hold over a drop. It works. It always works.",
                "But now there is a man in your building who watches the back of your head — and there is the part of you that chose to do this to him. Two passengers you did not have on Friday.",
                (eg("Gained a card.") + "   " if (_kk_card and _kk_card != "skip") else "") + ec("+ 15 Hatred.") + "   " + ec("Gained 2 dead cards."),
            ]

    else:
        python:
            stats.increment_stats_value_money(3000)
            stats.increment_stats_pcr_hatred(10)
            _kk_res = [
                "You write it up clean and you hand it up the chain, the way the academy said, the way the posters in the corridor still say.",
                "There is an informant's fee. There is also a Thursday shift where nobody saves you a seat, and a Friday one, and the cold does not lift after that.",
                eg("+ 3,000 CZK.") + "   " + ec("+ 10 Hatred."),
            ]

    call screen event_outcome(title="KARAOKE NIGHT AT U SLUNCE", art=_kk_art, result=_kk_res)
    return


## ---------------------------------------------------------------------------
## THE INTERVIEW [grounded-absurd] — the coding puzzle minigame. Pass: heal +
## card + Hatred relief. Fail: Hatred + curse. Reschedule / hang up cost too.
## ---------------------------------------------------------------------------

label ev_the_interview:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _iv_art = "images/events/ev_the_interview.jpg"
        _iv_body = [
            "A number you applied to three weeks ago, calling back now, nine in the evening, while you are parked behind the Albert with the engine off.",
            "'Quick technical screen. Thirty minutes. Is now bad?'",
            "Now is bad. Now is always bad. The laptop is waiting for you.",
        ]
        _iv_choices = [
            {
                "id": "take",
                "label": "[ TAKE THE CALL ]",
                "desc": ek("Coding puzzle.") + "  " + eg("Pass: + 20 HP, - 12 Hatred, gain a card.") + "  " + ec("Fail: + 15 Hatred, gain a dead card."),
            },
            {
                "id": "resched",
                "label": "[ ASK TO RESCHEDULE ]",
                "desc": ec("+ 10 Hatred") + ".  They will offer you a day, and the day will be a shift.",
            },
            {
                "id": "hang",
                "label": "[ HANG UP ]",
                "desc": ec("Lose 6 HP") + ".  Sit in the dark behind the supermarket a while.",
            },
        ]

    call screen event_screen(title="THE INTERVIEW", art=_iv_art, body=_iv_body, choices=_iv_choices)

    python:
        _iv_pick = _return
        _iv_tier = _battle_ladder_band(day_cycle.current_day)
        _iv_res = []

    if _iv_pick == "take":
        python:
            if getattr(store, '_puzzles_solved', None) is None:
                store._puzzles_solved = []
            _iv_pid = pick_puzzle_for_skill(stats.coding_skill, exclude=store._puzzles_solved)
            if _iv_pid is None:
                _iv_pid = "p_medium_sum_even"
            puzzle_init(_iv_pid, max_attempts=1 + diff_setting("minigame_retries", 1))
        call screen coding_puzzle_screen
        python:
            _iv_pass = (_return == "pass")
        if _iv_pass:
            python:
                store._puzzles_solved.append(_iv_pid)
                store.coding_interview_passed = True
                _iv_healed = event_heal(20)
                stats.increment_stats_pcr_hatred(-12)
                _iv_trio = pick_battle_rewards(_iv_tier)
            call screen card_reward_trio_screen(_iv_trio)
            python:
                _iv_card = _return
                if _iv_card and _iv_card != "skip":
                    grant_card(_iv_card, silent=True)
                _iv_res = [
                    "You answer the question. Then the follow-up. Then the one underneath that, the one they ask to see what you do when you don't know.",
                    "A pause on the line — the good kind. 'That's... yeah. Can you come in properly next week?'",
                    "For thirty minutes you were not a cop. You were a person being asked what you could do.",
                    eg("+ {} HP.".format(_iv_healed)) + "   " + eg("- 12 Hatred.") + ("   " + eg("Gained a card.") if (_iv_card and _iv_card != "skip") else ""),
                ]
        else:
            python:
                stats.increment_stats_pcr_hatred(15)
                grant_card("compromise", silent=True)
                _iv_res = [
                    "Generators. Decorators. A thing about the global interpreter lock. You hear yourself put words in a confident order that do not, in the end, add up to an answer.",
                    "'We'll let you know.' They will not let you know.",
                    "The impostor in the car was you the whole time. He rides home with you and does not get out.",
                    ec("+ 15 Hatred.") + "   " + ec("Gained a dead card."),
                ]

    elif _iv_pick == "resched":
        python:
            stats.increment_stats_pcr_hatred(10)
            _iv_res = [
                "'Could we do Friday?' you ask. They can do Friday.",
                "Friday is a twelve-hour shift. You know this as the words leave your mouth. You say 'Friday is perfect' anyway, and you hang up, and you have rescheduled nothing — only postponed the same impossible evening.",
                ec("+ 10 Hatred."),
            ]

    else:
        python:
            _iv_lost = event_hurt(6)
            _iv_res = [
                "You end the call before the first question. The screen says 00:00 and then goes dark.",
                "You sit behind the supermarket with the engine off until the cold gets all the way into your hands, thinking about the version of the evening where you were brave.",
                ec("- {} HP.".format(_iv_lost)),
            ]

    call screen event_outcome(title="THE INTERVIEW", art=_iv_art, result=_iv_res)
    return


## ---------------------------------------------------------------------------
## THE PHOTOCOPIER [surreal] — a card from a curated fortune; a duplicate of a
## card you already carry; or refuse to know (Hatred).
## ---------------------------------------------------------------------------

label ev_photocopier:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _pc_art = "images/events/ev_photocopier.jpg"
        _pc_body = [
            "The big photocopier on the second floor has a quirk the day shift pretends not to know about. Feed it a blank page and it does not give you a blank page back.",
            "It gives you a sentence. About you. About what is coming. The toner it uses for this is not a toner the supplier sells.",
            "It is warm. It is humming. The feed tray is open like a waiting hand.",
        ]
        _pc_choices = [
            {
                "id": "blank",
                "label": "[ COPY A BLANK PAGE ]",
                "desc": ec("2,000 CZK in toner") + ".  " + eg("Pick a card from 3 offered."),
                "enabled": (stats.available_money >= 2000),
                "locked": "The toner cartridge is the kind you pay 2,000 CZK for. You can't.",
            },
            {
                "id": "hand",
                "label": "[ COPY YOUR OWN HAND ]",
                "desc": ec("Lose 8 HP") + ".  " + eg("It prints a card you already carry. Now you carry it twice."),
            },
            {
                "id": "unplug",
                "label": "[ PULL THE PLUG ]",
                "desc": ec("+ 5 Hatred") + ".  The not-knowing rides home and sits on your chest.",
            },
        ]

    call screen event_screen(title="THE PHOTOCOPIER", art=_pc_art, body=_pc_body, choices=_pc_choices)

    python:
        _pc_pick = _return
        _pc_tier = _battle_ladder_band(day_cycle.current_day)
        _pc_res = []

    if _pc_pick == "blank":
        $ stats.try_spend_money(2000)
        python:
            _pc_trio = pick_battle_rewards(_pc_tier)
        call screen card_reward_trio_screen(_pc_trio)
        python:
            _pc_card = _return
            if _pc_card and _pc_card != "skip":
                grant_card(_pc_card, silent=True)
                _pc_res = [
                    "You lay one blank page on the glass and press the green button. The light goes across, slow, the way light goes across a face.",
                    "The page that comes out is not blank. It describes, in a single warm sentence, a thing you will need before this is over — and then it stops being a sentence and is simply the thing, in your hand.",
                    ec("- 2,000 CZK.") + "   " + eg("Gained a card."),
                ]
            else:
                _pc_res = [
                    "You lay one blank page on the glass and press the green button. The light goes across, slow, the way light goes across a face.",
                    "The page that comes out is not blank — but you set it down without reading it to the end. Some fortunes you are not ready to be told. The machine keeps the toner money regardless.",
                    ec("- 2,000 CZK."),
                ]

    elif _pc_pick == "hand":
        python:
            _pc_lost = event_hurt(8)
            _pc_deck = list(player_deck.cards)
        call screen event_card_picker("CHOOSE A CARD TO COPY", _pc_deck)
        python:
            grant_card(_return, silent=True)
            _pc_res = [
                "You press your palm flat to the glass and hold the lid down on the back of your own hand. The light goes under your skin. It does not feel like nothing.",
                "The page it prints is a card you already carry, exact down to the wear on the corners. You have it twice now. You will not think too hard about where the second one came from.",
                ec("- {} HP.".format(_pc_lost)) + "   " + eg("Duplicated a card."),
            ]

    else:
        python:
            stats.increment_stats_pcr_hatred(5)
            _pc_res = [
                "You find the cable and pull it out of the wall. The hum dies. The screen forgets your name one character at a time.",
                "You did not read it. So now you carry the other thing instead — the not-knowing, which is heavier, and which follows you all the way home and sits on your chest in the dark.",
                ec("+ 5 Hatred."),
            ]

    call screen event_outcome(title="THE PHOTOCOPIER", art=_pc_art, result=_pc_res)
    return


## ---------------------------------------------------------------------------
## SYNTHOL BROTHERS [bodybuilder-only] — the shortcut. Demo dose buys +2 SOMA
## for HP; the full stack buys +5 SOMA for a Compromise card; walk away costs
## nothing but a little dignity. Pool-gated to BB in event_engine.rpy.
## ---------------------------------------------------------------------------

label ev_synthol_brothers:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _sb_art = "images/events/ev_synthol_brothers.jpg"
        _sb_body = [
            "Behind the squat-rack at Iron Garden, two brothers run a small business off a folding table. Vials, a syringe still in its wrapper, a roll of paper towel. Everything you would need, laid out the way a dentist lays out tools.",
            "'Brácho. Saw you on the rack. Good form. Slow tempo.' The older one tilts his head. 'You're working hard. We can make it easier.'",
            "His shoulders sit wrong — round, oiled, too high. Not muscle. Not all muscle. The younger one is already drawing the dose.",
        ]
        _sb_choices = [
            {
                "id": "demo",
                "label": "[ ONE SHOT ]",
                "desc": eg("+ 2 SOMA") + ".  " + ec("Lose 20 HP") + ".  The cheap demo dose. Your body will know.",
            },
            {
                "id": "full",
                "label": "[ THE FULL STACK ]",
                "desc": eg("+ 5 SOMA") + ".  " + ec("Gain an unplayable card (dead weight).") + "  They cook the bigger batch.",
            },
            {
                "id": "walk",
                "label": "[ WALK AWAY ]",
                "desc": "Nothing. They will let you go, and they will let you know what they think of it.",
            },
        ]

    call screen event_screen(title="THE SYNTHOL BROTHERS", art=_sb_art, body=_sb_body, choices=_sb_choices)

    python:
        _sb_pick = _return
        _sb_res = []

    if _sb_pick == "demo":
        python:
            _sb_lost = event_hurt(20)
            add_soma(2)
            _sb_res = [
                "He hits the deltoid, fast, the way someone who has done this two hundred times hits it. You barely feel the needle. You feel the rest.",
                "By the time you reach the car your shoulder is hot, then cold, then a temperature your shoulder is not meant to be. You sleep on your other side for a week.",
                "But the mirror does not argue. The shirt sits differently. You are bigger. Cheaper, in some way you cannot point at — but bigger.",
                eg("+ 2 SOMA.") + "   " + ec("- {} HP.".format(_sb_lost)),
            ]

    elif _sb_pick == "full":
        python:
            add_soma(5)
            grant_card("compromise", silent=True)
            _sb_res = [
                "The younger one warms the vial in his palm like a sommelier. The older one talks the whole time — about discipline, about heritage, about how the body is a project, and a project deserves a budget.",
                "Four sites. Four needles. You walk out of Iron Garden three centimetres bigger across the chest and a different person inside the shirt.",
                "Something settled in with the oil. It does not show in the mirror. It shows in the deck.",
                eg("+ 5 SOMA.") + "   " + ec("Gained an unplayable card (dead weight)."),
            ]

    else:
        python:
            _sb_res = [
                "'No,' you say. 'Not for me.'",
                "The older brother smiles, slow, the way men smile at boys. 'Sure, brácho. Stay natty. Twenty years of pressing and you'll look like me anyway.' He flexes once, just to make the point. The shoulder does not move like a shoulder.",
                "'You don't know what you're missing,' the younger one calls after you. 'You'll be back when the bench plateaus.'",
                "The door swings shut behind you. They are still laughing.",
                "No cost. No gain. Just the noise of it, riding home with you.",
            ]

    call screen event_outcome(title="THE SYNTHOL BROTHERS", art=_sb_art, result=_sb_res)
    return


## ---------------------------------------------------------------------------
## ACD856 OFFER [biohacker] — gray-market peptide gamble. 10k CZK, 50/50.
## REAL: + 20 max HP and a rare Wetware Power (acd856_regen).
## FAKE: - 25 HP, + 20 Hatred, next battle has a Diarrhea status card.
## EV is slightly negative — true gamble, not a free pull. The +20 Hatred on
## a bad roll is the real punishment. Pool-gated to BH in event_engine.rpy.
## ---------------------------------------------------------------------------

label ev_bh_acd856_offer:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _ac_art = "images/events/ev_bh_acd856_offer.jpg"
        _ac_body = [
            "Telegram, 02:14. An old contact from the longecity threads — three months silent — drops a single line: 'ACD856. Real batch. 10k. DM for address.'",
            "ACD856. Neuroregenerative peptide. Russian lab originally, then a couple of unverified European reshippers. The papers exist. So do the receipts of three people who got saline. He doesn't refund.",
            "You have ten thousand crowns and a body that hasn't been the same since Day One. The decision is roughly the size of a coin.",
        ]
        _ac_choices = [
            {
                "id": "pass",
                "label": "[ PASS ]",
                "desc": "Not worth the variance.  No effects.",
            },
            {
                "id": "buy",
                "label": "[ BUY (10,000 CZK) ]",
                "desc": ek("50/50 gamble.") + "  " + eg("Real: + 20 max HP + rare Power card.") + "  " + ec("Fake: - 25 HP, + 20 Hatred, status card next fight."),
                "enabled": stats.available_money >= 10000,
                "locked": "Ten thousand crowns. You don't have it on you.",
            },
        ]

    call screen event_screen(title="ACD856 OFFER", art=_ac_art, body=_ac_body, choices=_ac_choices)

    python:
        _ac_pick = _return
        _ac_res = []

    if _ac_pick == "buy":
        python:
            stats.increment_stats_value_money(-10000)
            _ac_roll = __import__('random').randint(1, 100)

        if _ac_roll <= 50:
            python:
                ## REAL — bump run_hp_max and current HP by 20, grant the
                ## rare regen Power.
                if getattr(store, 'run_hp_max', None) is None:
                    store.run_hp_max = _event_class_max_hp()
                if getattr(store, 'run_hp', None) is None:
                    store.run_hp = store.run_hp_max
                store.run_hp_max += 20
                store.run_hp = min(store.run_hp_max, store.run_hp + 20)
                grant_card("acd856_regen", silent=False)
                _ac_res = [
                    "The address is a flat above a pet-supply shop in Vršovice. The man who opens the door is wearing socks and a watch and nothing else worth mentioning. The vial is plain. The labelling is wrong on purpose.",
                    "Three days in you sleep eight hours and wake up rebuilt. Resting heart rate down four. Recovery numbers you didn't think your body had in it anymore. The protocol works.",
                    eg("- 10,000 CZK.") + "   " + eg("+ 20 max HP.") + "   " + eg("Gained: ACD856 (rare Power)."),
                ]
        else:
            python:
                _ac_lost = event_hurt(25)
                stats.increment_stats_pcr_hatred(20)
                store.bh_pending_diarrhea = True
                _ac_res = [
                    "The address is a flat above a pet-supply shop in Vršovice. The man who opens the door is wearing socks and a watch and nothing else worth mentioning. The vial is plain. The labelling is wrong on purpose.",
                    "Three hours in the bathroom. Six hours of cold sweat. By morning you know it was saline at best, contaminated saline at worst. You call the number. It rings out. You call it again. It rings out forever.",
                    "You memorize his face. The shop downstairs. The make of his watch. You memorize all of it, the way you memorize a license plate at a crash scene.",
                    ec("- 10,000 CZK.") + "   " + ec("- {} HP.".format(_ac_lost)) + "   " + ec("+ 20 Hatred.") + "   " + ec("Status card injected into next battle."),
                ]

    else:
        python:
            _ac_res = [
                "You don't reply. The Telegram bubble sits unread for twenty minutes. He doesn't follow up.",
                "Somewhere in the next forty-eight hours another three people will read his message and one of them will say yes. You won't know which one. You won't know whether they got the real thing.",
                "Probably for the best. The variance was too wide.",
            ]

    call screen event_outcome(title="ACD856 OFFER", art=_ac_art, result=_ac_res)
    return
