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
        ## escalates 6/8/11 so tier 3 isn't strictly worse ROI than tier 1 —
        ## press-your-luck needs reward-for-risk, not just cost-for-risk.
        _vm_ladder = [
            (1500, 6, 0),
            (3500, 8, 5),
            (7000, 11, 12),
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
                ## Route the bonus through the persistent accumulator that
                ## class_max_hp folds in — writing run_hp_max directly let
                ## battle_init's max-HP resync wipe it. Recompute, then heal.
                store.run_max_hp_bonus = getattr(store, 'run_max_hp_bonus', 0) + _vm_hp
                store.run_hp_max = class_max_hp()
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
                "desc": ek("A gamble.") + "  " + eg("Best case: - 6 Hatred.") + "  " + ec("Worst: + 18 Hatred, gain a card.") + "  Even odds.",  ## roll <= 50 below = truly even
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
        if _sm_roll <= 50:
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
                ec("- {} HP.".format(_sm_lost)) + "   " + eg("+ {:,} CZK.".format(stats.money_gain_preview(2000))),
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
                "desc": ec("+ 12 Hatred") + ".  " + eg("Gain a piece of gear.") + "  Someone, somewhere, is still looking for it.",
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
            ## The box is a piece of gear — relics get an event acquisition path
            ## here, the way they should: pocketed off the books. Class-filtered
            ## (random_unowned_relic respects class_lock). If you somehow already
            ## carry every eligible relic, the box still isn't empty — a card.
            _lf_relic = random_unowned_relic()
            _lf_gain_line = ""
        if _lf_relic:
            python:
                grant_relic(_lf_relic, silent=True)
                _lf_gain_line = eg("Gained gear: {}.".format(RELIC_LIBRARY.get(_lf_relic, {}).get("name", "a piece of gear")))
        else:
            python:
                _lf_trio = pick_battle_rewards(_lf_tier)
            call screen card_reward_trio_screen(_lf_trio)
            python:
                _lf_card = _return
                if _lf_card and _lf_card != "skip":
                    grant_card(_lf_card, silent=True)
                    _lf_gain_line = eg("Gained a card.")
        python:
            _lf_res = [
                "She watches you lift the box and says nothing, which is its own kind of saying something.",
                "It is good. It is useful. It belonged to someone who came in once, frightened, and never came back for it.",
                "You carry it out. It is yours now, the way most things become yours: by nobody stopping you.",
                ec("+ 12 Hatred.") + ("   " + _lf_gain_line if _lf_gain_line else ""),
            ]

    call screen event_outcome(title="THE LOST & FOUND", art=_lf_art, result=_lf_res)
    return


## ---------------------------------------------------------------------------
## THE COLONEL SENDS HIS REGARDS [surreal] — a Faustian deal. KEEP grants
## Colonel's Gift (1E / 14 dmg, -2 HP) AND adds +50 HP to the Colonel at the
## boss. BURN: -10 HP, grant Ashes (0E / 6 dmg / exhaust). RETURN: 7,000 CZK, -15
## Hatred. Only KEEP touches day 30; the other two are refusals at cost.
## ---------------------------------------------------------------------------

label ev_colonel_regards:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _cr_art      = "images/events/ev_colonel_regards.jpg"
        _cr_art_keep = "images/events/ev_colonel_regards_keep.jpg"
        _cr_art_burn = "images/events/ev_colonel_regards_burn.jpg"
        _cr_art_ret  = "images/events/ev_colonel_regards_return.jpg"
        _cr_body = [
            "There is a box outside your door. No courier waited. No label, no stamp — just your name, in handwriting you have spent ten years learning to read upside down across a desk.",
            "Inside: one card, face-down. And a note.",
            ek("\"Thought of you. Wear it well.  — K.\""),
        ]
        _cr_choices = [
            {
                "id": "keep",
                "label": "[ KEEP IT ]",
                "desc": eg("Gain Colonel's Gift.") + "   " + ec("The Colonel: + 50 HP at day 30."),
                "preview_card": "colonel_gift",
            },
            {
                "id": "burn",
                "label": "[ BURN IT IN THE SINK ]",
                "desc": ec("- 10 HP.") + "   " + ec("Gain Ashes."),
                "preview_card": "ashes",
            },
            {
                "id": "return",
                "label": "[ COURIER IT BACK, UNOPENED ]",
                "desc": ec("- 7,000 CZK.") + "   " + eg("- 15 Hatred.") + "   A clean refusal.",
                "enabled": (stats.available_money >= 7000),
                "locked": "A courier across the country costs 7,000 CZK. You do not have it.",
            },
        ]

    call screen event_screen(title="THE COLONEL SENDS HIS REGARDS", art=_cr_art, body=_cr_body, choices=_cr_choices)

    python:
        _cr_pick    = _return
        _cr_res     = []
        _cr_art_out = _cr_art

    if _cr_pick == "keep":
        python:
            grant_card("colonel_gift", silent=True)
            store._colonel_gift_taken = True
            _cr_art_out = _cr_art_keep
            _cr_res = [
                "You take it out of the box. It is good — better than good. It is exactly the thing you would have chosen for yourself, which is the part that makes your hands cold.",
                "He knows what you are building. He has always known.",
                "Somewhere, a file with your name on it gets a note added to it. When he comes for you on day thirty, he will come wearing what you accepted.",
                eg("Gained Colonel's Gift.") + "   " + ec("The Colonel: + 50 HP at day 30."),
            ]

    elif _cr_pick == "burn":
        python:
            _cr_lost = event_hurt(10)
            grant_card("ashes", silent=True)
            _cr_art_out = _cr_art_burn
            _cr_res = [
                "You hold it under the tap, strike a match, and watch. It does not burn like paper. It takes its time.",
                "You do not sleep. You sit with the smell of it until the window goes grey, turning over every reason a man like that sends a gift, and finding the same answer each time.",
                "The ash is yours now. You scrape it into an envelope. You keep it.",
                ec("- {} HP.".format(_cr_lost)) + "   " + ec("Gained Ashes."),
            ]

    else:
        python:
            stats.try_spend_money(7000)
            stats.increment_stats_pcr_hatred(-15)
            _cr_art_out = _cr_art_ret
            _cr_res = [
                "You do not open it. You pay a courier the better part of a week's wage to drive it back across the country and put it in his hands exactly as it came.",
                "He will understand the message. It cost you to send it. That is the message.",
                "Your spine, for once, is the straightest thing in the room.",
                ec("- 7,000 CZK.") + "   " + eg("- 15 Hatred."),
            ]

    call screen event_outcome(title="THE COLONEL SENDS HIS REGARDS", art=_cr_art_out, result=_cr_res)
    return


## ---------------------------------------------------------------------------
## PILLS, PROBABLY — three verbs on a found bag of unmarked pills:
##   CONFISCATE: pocket the bag off the books — one a night until they're
##               gone. +8 Max HP (Biohacker +10: he reads the compound and
##               doses it properly). Routed through run_max_hp_bonus so
##               battle_init's max-HP resync keeps it.
##   LEAVE:      shut the bag back in the seat well, walk away. -6 Hatred.
##   REPORT:     book the driver by the book. +3,000 CZK, +8 Hatred. Doing
##               your job inside a rotten precinct grinds you, not heals you.
## ---------------------------------------------------------------------------

label ev_pills:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _pl_art = "images/events/ev_pills.jpg"
        _pl_body = [
            "Vehicle search, routine, one in the morning. Under the passenger seat: a sandwich bag of pills. No markings. No two of them quite the same.",
            "The driver swears they aren't his. They are never anyone's.",
            "Your hand hovers over the bag. The shift has six hours left in it and you have not slept properly since March.",
        ]
        _pl_hp = 10 if stats.player_class == "biohacker" else 8
        _pl_choices = [
            {
                "id": "confiscate",
                "label": "[ CONFISCATE THE PILLS ]",
                "desc": eg("+ {} Max HP.".format(_pl_hp)) + "  Evidence collected. Off the books.",
            },
            {
                "id": "leave",
                "label": "[ LEAVE IT ]",
                "desc": eg("- 6 Hatred.") + "  Shut the bag back in the seat well. Pretend you didn't see it.",
            },
            {
                "id": "report",
                "label": "[ REPORT IT ]",
                "desc": eg("+ {:,} CZK.".format(stats.money_gain_preview(3000))) + "   " + ec("+ 8 Hatred.") + "  Bench duty until dawn, filling forms while the Colonel reads.",
            },
        ]

    call screen event_screen(title="PILLS, PROBABLY", art=_pl_art, body=_pl_body, choices=_pl_choices)

    python:
        _pl_pick = _return
        _pl_res = []

    if _pl_pick == "confiscate":
        python:
            _event_ensure_run_hp()
            ## Same accumulator the vitamin man uses — battle_init's max-HP
            ## resync folds run_max_hp_bonus in, a raw run_hp_max write dies.
            store.run_max_hp_bonus = getattr(store, 'run_max_hp_bonus', 0) + _pl_hp
            store.run_hp_max = class_max_hp()
            store.run_hp = min(store.run_hp_max, store.run_hp + _pl_hp)
            if stats.player_class == "biohacker":
                _pl_res = [
                    "You don't need the test kit. One look at the pressing, the binder, the faint bitter edge — you know exactly what these are, and they are not random. Someone with a real lab made these.",
                    "You pocket the bag the way you'd pocket your own prescription and dose it like one — measured, spaced, logged. Every one of them does something you want.",
                    eg("+ {} Max HP.".format(_pl_hp)),
                ]
            else:
                _pl_res = [
                    "You slide the bag into the inside pocket of your jacket and finish the shift like a man who has just decided something. You do not write up the search.",
                    "One a night, after the shift, washed down at the kitchen sink. By the time the bag is empty the mirror has stopped arguing: whatever they were, they worked.",
                    eg("+ {} Max HP.".format(_pl_hp)),
                ]

    elif _pl_pick == "leave":
        python:
            stats.increment_stats_pcr_hatred(-6)
            _pl_res = [
                "You shut the bag back in the well under the seat, close the door, and tell the driver his offside tire is low. He nods, the panic going out of his face by degrees, and you watch him drive away under the speed limit all the way to the next streetlight and past it.",
                "Walking back to your car you find that some old, tight thing in your chest has slipped a notch. The bag was never going to be yours. You made the absence of a choice into a choice.",
                eg("- 6 Hatred."),
            ]

    else:
        python:
            stats.increment_stats_value_money(3000)
            stats.increment_stats_pcr_hatred(8)
            _pl_res = [
                "You bring him in. The paperwork eats the rest of the shift and most of the morning, and a slow rotation of older men come to the bench you are sitting on to ask the same three questions in slightly different shapes.",
                "At the end of it: a stamped commendation slip, a small bonus, and a quiet certainty that the Colonel has read the file before lunch.",
                "You did your job. The job, today, was the wrong shape for a man like you, and you can feel where it bent you.",
                eg("+ {:,} CZK.".format(stats.money_gain_preview(3000))) + "   " + ec("+ 8 Hatred."),
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
                eg("+ {:,} CZK.".format(stats.money_gain_preview(8000))) + "   " + ec("Removed a Police card."),
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
                eg("+ {:,} CZK.".format(stats.money_gain_preview(3000))) + "   " + eg("Transformed a card."),
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
                eg("+ {:,} CZK.".format(stats.money_gain_preview(3000))) + "   " + ec("+ 10 Hatred."),
            ]

    call screen event_outcome(title="KARAOKE NIGHT AT U SLUNCE", art=_kk_art, result=_kk_res)
    return


## ---------------------------------------------------------------------------
## THE INTERVIEW — coding-skill check (no puzzle minigame). Pass rate scales
## with stats.coding_skill: 15% floor at skill 0, 95% ceiling at skill ≥ 80.
##   TAKE THE CALL — roll. Pass: +20 HP, -12 Hatred, gain Job Offer card.
##                          Fail: +15 Hatred, gain Compromise.
##   HANG UP        — -10 HP, +10 Hatred. The bail-out costs you both ways.
## ---------------------------------------------------------------------------

label ev_the_interview:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _iv_art = "images/events/ev_the_interview.jpg"
        ## Linear roll: 15% base + 1% per coding_skill point, capped at 95%.
        ## Skill 0 → 15% (cold-start gamble); skill 50 → 65%; skill 80+ → 95%.
        _iv_pass_chance = max(15, min(95, 15 + stats.coding_skill))
        _iv_body = [
            "A number you applied to three weeks ago, calling back now, nine in the evening, while you are parked behind the Albert with the engine off.",
            "'Quick technical screen. Thirty minutes. Is now bad?'",
            "Now is bad. Now is always bad. The laptop is waiting for you.",
        ]
        _iv_choices = [
            {
                "id": "take",
                "label": "[ TAKE THE CALL ]",
                "desc": ek("Coding-skill check ({}%).".format(_iv_pass_chance)) + "  " + eg("Pass: + 20 HP, - 12 Hatred, gain Job Offer.") + "  " + ec("Fail: + 15 Hatred, gain Compromise."),
                "preview_card": "job_offer",
            },
            {
                "id": "hang",
                "label": "[ HANG UP ]",
                "desc": ec("- 10 HP.") + "   " + ec("+ 10 Hatred.") + "  Sit in the dark behind the supermarket a while.",
            },
        ]

    call screen event_screen(title="THE INTERVIEW", art=_iv_art, body=_iv_body, choices=_iv_choices)

    python:
        _iv_pick = _return
        _iv_res = []

    if _iv_pick == "take":
        python:
            _iv_roll = __import__('random').randint(1, 100)
            _iv_pass = _iv_roll <= _iv_pass_chance

        if _iv_pass:
            python:
                store.coding_interview_passed = True
                _iv_healed = event_heal(20)
                stats.increment_stats_pcr_hatred(-12)
                grant_card("job_offer", silent=True)
                _iv_res = [
                    "You answer the question. Then the follow-up. Then the one underneath that, the one they ask to see what you do when you don't know.",
                    "A pause on the line — the good kind. 'That's... yeah. Can you come in properly next week?'",
                    "For thirty minutes you were not a cop. You were a person being asked what you could do.",
                    eg("+ {} HP.".format(_iv_healed)) + "   " + eg("- 12 Hatred.") + "   " + eg("Gained Job Offer."),
                ]
        else:
            python:
                stats.increment_stats_pcr_hatred(15)
                grant_card("compromise", silent=True)
                _iv_res = [
                    "Generators. Decorators. A thing about the global interpreter lock. You hear yourself put words in a confident order that do not, in the end, add up to an answer.",
                    "'We'll let you know.' They will not let you know.",
                    "The impostor in the car was you the whole time. He rides home with you and does not get out.",
                    ec("+ 15 Hatred.") + "   " + ec("Gained Compromise."),
                ]

    else:
        python:
            _iv_lost = event_hurt(10)
            stats.increment_stats_pcr_hatred(10)
            _iv_res = [
                "You end the call before the first question. The screen says 00:00 and then goes dark.",
                "You sit behind the supermarket with the engine off until the cold gets all the way into your hands, thinking about the version of the evening where you were brave.",
                ec("- {} HP.".format(_iv_lost)) + "   " + ec("+ 10 Hatred."),
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
                "desc": eg("+ 2 SOMA") + ".  " + ec("Lose 12 HP") + ".  The cheap demo dose — the efficient buy.",
            },
            {
                "id": "full",
                "label": "[ THE FULL STACK ]",
                "desc": eg("+ 5 SOMA") + ".  " + ec("Lose 20 HP") + ", " + ec("gain a dead card") + ".  The big batch costs the body.",
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
            _sb_lost = event_hurt(12)
            add_soma(2)
            _sb_res = [
                "He hits the deltoid, fast, the way someone who has done this two hundred times hits it. You barely feel the needle. You feel the rest.",
                "By the time you reach the car your shoulder is hot, then cold, then a temperature your shoulder is not meant to be. You sleep on your other side for a week.",
                "But the mirror does not argue. The shirt sits differently. You are bigger. Cheaper, in some way you cannot point at — but bigger.",
                eg("+ 2 SOMA.") + "   " + ec("- {} HP.".format(_sb_lost)),
            ]

    elif _sb_pick == "full":
        python:
            _sb_lost = event_hurt(20)
            add_soma(5)
            grant_card("compromise", silent=True)
            _sb_res = [
                "The younger one warms the vial in his palm like a sommelier. The older one talks the whole time — about discipline, about heritage, about how the body is a project, and a project deserves a budget.",
                "Four sites. Four needles. You walk out of Iron Garden three centimetres bigger across the chest and a different person inside the shirt — and a temperature your body is not meant to be.",
                "Something settled in with the oil. It does not show in the mirror. It shows in the deck, and in the week your shoulders spend on fire.",
                eg("+ 5 SOMA.") + "   " + ec("- {} HP.".format(_sb_lost)) + "   " + ec("Gained a dead card."),
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
    ## SOMA 10/10 capstone — guarded no-op when sub-10 or already given.
    ## Mirrors the gym/heavy-session calls so synthol-pumped runs don't have
    ## to detour through the gym to claim the capstone card.
    call soma_ten_reward from _call_soma_ten_reward_synthol
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


## ---------------------------------------------------------------------------
## THE COLLECTOR [press-your-luck relic] — a debt enforcer with a bag of other
## men's collateral. Pay in cash (5,000 CZK) OR in blood (25 HP) for a 50% pull
## at a piece of gear; miss and you can pay again or walk. Walking away costs
## +20 Hatred — a man like this knowing your door does not leave you. The prize
## relic is rolled once (medium weights) and stays blind until won. The HP lane
## is gated to run_hp > 25 so a 1-HP floor can never become a free reroll.
## ---------------------------------------------------------------------------

label ev_the_collector:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _co_art = "images/events/ev_the_collector.jpg"
        _co_relic = random_unowned_relic(relic_drop_weights("medium"))
        _co_tries = 0

    if not _co_relic:
        python:
            stats.increment_stats_pcr_hatred(-3)
            _co_res = [
                "Past midnight, a man on the landing with a bag of other men's collateral. He looks at you, then the bag, and almost laughs. 'You've got better than anything in here already.'",
                "He shoulders it and goes back down into the dark. Nothing here you need — and, strange thing, that helps.",
                eg("- 3 Hatred."),
            ]
        call screen event_outcome(title="THE COLLECTOR", art=_co_art, result=_co_res)
        return

    label .offer:

        python:
            _event_ensure_run_hp()
            _co_can_hp  = store.run_hp > 25
            _co_can_czk = stats.available_money >= 5000
            if _co_tries == 0:
                _co_body = [
                    "Past midnight, a man on the landing. Not police — police knock differently. He says your name, a number, and a debt you'd half-forgotten you owed.",
                    "At his feet, a bag of other men's collateral — the good gear, taken off people who paid the hard way. 'Settle up and reach in,' he says. 'Cash, or I take it out of your hide. Fifty-fifty you pull something worth keeping.'",
                ]
            else:
                _co_body = [
                    "The bag stays open. He waited while you came up empty, patient as a clock.",
                    "'Again?' he says. 'Or shut the door and live with it.'",
                ]
            _co_choices = [
                {
                    "id": "hp",
                    "label": "[ TAKE IT OUT OF YOUR HIDE ]",
                    "desc": ec("- 25 HP") + "  " + ek("50%: a piece of his gear."),
                    "enabled": _co_can_hp,
                    "locked": ec("- 25 HP") + "  You haven't 25 left to give him.",
                },
                {
                    "id": "czk",
                    "label": "[ SETTLE IN CASH ]",
                    "desc": ec("- 5,000 CZK") + "  " + ek("50%: a piece of his gear."),
                    "enabled": _co_can_czk,
                    "locked": ec("- 5,000 CZK") + "  Not on you tonight.",
                },
                {
                    "id": "leave",
                    "label": "[ SHUT THE DOOR ]",
                    "desc": ec("+ 20 Hatred") + ".  Walk away with nothing but knowing he knows the door.",
                },
            ]

        call screen event_screen(title="THE COLLECTOR", art=_co_art, body=_co_body, choices=_co_choices)

        python:
            _co_pick = _return

        if _co_pick == "leave":
            python:
                stats.increment_stats_pcr_hatred(20)
                _co_res = [
                    "You shut the door on him and the bag both. He doesn't knock again — he doesn't have to.",
                    "He knows the door now. The knowing moves in for good, and it does not pay rent.",
                    ec("+ 20 Hatred."),
                ]
            call screen event_outcome(title="THE COLLECTOR", art=_co_art, result=_co_res)
            return

        python:
            if _co_pick == "hp":
                _co_lost = event_hurt(25)
                _co_paid = ec("- {} HP.".format(_co_lost))
            else:
                stats.try_spend_money(5000)
                _co_paid = ec("- 5,000 CZK.")
            _co_tries += 1
            _co_win = __import__('random').randint(1, 100) <= 50

        if _co_win:
            python:
                grant_relic(_co_relic, silent=True)
                _co_nm = RELIC_LIBRARY.get(_co_relic, {}).get("name", "a piece of kit")
                _co_res = [
                    "Your hand closes on something solid and he lets you keep it — a deal's a deal, even his kind.",
                    "You come up out of the bag with more than the debt was ever worth. He's already gone.",
                    _co_paid + "   " + eg("Gear: {}.".format(_co_nm)),
                ]
            call screen event_outcome(title="THE COLLECTOR", art=_co_art, result=_co_res)
            return

        jump ev_the_collector.offer


## ---------------------------------------------------------------------------
## THE QUARTERMASTER [relic choice] — an off-the-books surplus lock-up. Up to
## three SEEN relics, one per currency lane: pocket the hot one (+Hatred), buy
## the clean one (its real shop price), or haul the heavy one (HP). The choose-
## one-of-three gear shelf — distinct from lost_and_found's blind box.
## Hovering a lane previews the actual gear (sprite + mechanic) via the
## event_screen preview_relic panel. No walk-away consolation: once you're
## in the lock-up, you leave with something — the only exit choice appears
## when the bench is bare.
## ---------------------------------------------------------------------------

label ev_the_quartermaster:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _qm_art = "images/events/ev_the_quartermaster.jpg"
        ## One relic per currency lane, rarity-biased so the trip is worth it.
        _qm_picks = roll_relic_choices(3, relic_drop_weights("hard"))
        _qm_r_hat = _qm_picks[0] if len(_qm_picks) >= 1 else None
        _qm_r_czk = _qm_picks[1] if len(_qm_picks) >= 2 else None
        _qm_r_hp  = _qm_picks[2] if len(_qm_picks) >= 3 else None
        _qm_czk_price = relic_shop_price(_qm_r_czk) if _qm_r_czk else 0

        if not _qm_picks:
            _qm_body = [
                "A lock-up off the ring road. The Quartermaster looks up from his crossword at the bare bench. 'Cleaned you out already. You've taken everything off me worth taking.'",
                "Nothing here tonight. Just the door, the ring road, and the long drive back.",
            ]
        else:
            _qm_body = [
                "A lock-up off the ring road, rented in cash under a name that was never anyone's. The Quartermaster deals what the job throws away — surplus, decommissioned, and the third kind nobody got around to decommissioning.",
                "Tonight's pieces are out on the bench under a work-lamp. He won't say which is which kind. He lights a cigarette, leans on the roller door, and lets you look.",
            ]

        _qm_choices = []
        if _qm_r_hat:
            _qm_m = RELIC_LIBRARY.get(_qm_r_hat, {})
            _qm_choices.append({
                "id": "slot_hatred",
                "label": "[ POCKET THE HOT ONE ]",
                "desc": ek(_qm_m.get("name", "a piece of kit")) + " — " + _qm_m.get("hook", "") + "  " + ec("+ 12 Hatred") + ".",
                "preview_relic": _qm_r_hat,
            })
        if _qm_r_czk:
            _qm_m = RELIC_LIBRARY.get(_qm_r_czk, {})
            _qm_choices.append({
                "id": "slot_czk",
                "label": "[ BUY THE CLEAN ONE ]",
                "desc": ek(_qm_m.get("name", "a piece of kit")) + " — " + _qm_m.get("hook", "") + "  " + ec("- {:,} CZK".format(_qm_czk_price)) + ".",
                "enabled": stats.available_money >= _qm_czk_price,
                "locked": ek(_qm_m.get("name", "a piece of kit")) + " — you're {:,} CZK short of a clean buy.".format(max(0, _qm_czk_price - stats.available_money)),
                "preview_relic": _qm_r_czk,
            })
        if _qm_r_hp:
            _qm_m = RELIC_LIBRARY.get(_qm_r_hp, {})
            _qm_choices.append({
                "id": "slot_hp",
                "label": "[ HAUL THE HEAVY ONE ]",
                "desc": ek(_qm_m.get("name", "a piece of kit")) + " — " + _qm_m.get("hook", "") + "  " + ec("- 15 HP") + ".",
                "preview_relic": _qm_r_hp,
            })
        if not _qm_choices:
            ## Bare bench (pool drained) — the only thing left is the door.
            _qm_choices.append({
                "id": "walk",
                "label": "[ ROLL THE DOOR DOWN ]",
                "desc": "Nothing on the bench tonight. The drive back is all there is.",
            })

    call screen event_screen(title="THE QUARTERMASTER", art=_qm_art, body=_qm_body, choices=_qm_choices)

    python:
        _qm_pick = _return
        _qm_res = []
        if _qm_pick == "slot_hatred":
            grant_relic(_qm_r_hat, silent=True)
            stats.increment_stats_pcr_hatred(12)
            _qm_nm = RELIC_LIBRARY.get(_qm_r_hat, {}).get("name", "the piece")
            _qm_res = [
                "You lift it off the bench and no money moves and nothing gets written, which is the whole transaction. The Quartermaster doesn't watch you do it; a thing that was never sold was never here.",
                "It rides home in your jacket the whole way, warm and certain and not yours — and you know, the way you always know, exactly whose worst night it fell out of.",
                eg("Gear: {}.".format(_qm_nm)) + "   " + ec("+ 12 Hatred."),
            ]
        elif _qm_pick == "slot_czk":
            stats.try_spend_money(_qm_czk_price)
            grant_relic(_qm_r_czk, silent=True)
            _qm_nm = RELIC_LIBRARY.get(_qm_r_czk, {}).get("name", "the piece")
            _qm_res = [
                "You count it into his hand and he counts it again, and the number is fair because a fair number is the only thing he sells honestly.",
                "Clean — or as clean as a garage off the ring road gets. The gear is yours and your name is on nothing. That, tonight, is worth the money.",
                eg("Gear: {}.".format(_qm_nm)) + "   " + ec("- {:,} CZK.".format(_qm_czk_price)),
            ]
        elif _qm_pick == "slot_hp":
            _qm_lost = event_hurt(15)
            grant_relic(_qm_r_hp, silent=True)
            _qm_nm = RELIC_LIBRARY.get(_qm_r_hp, {}).get("name", "the piece")
            _qm_res = [
                "It doesn't fit the boot, then it doesn't fit the back seat, then it's the long haul across the lot with the thing trying to take your spine the whole way.",
                "By the car you're breathing through your teeth — but nobody bankrolled it and nobody logged it. You hauled it out the one honest way left to you.",
                eg("Gear: {}.".format(_qm_nm)) + "   " + ec("- {} HP.".format(_qm_lost)),
            ]
        else:
            ## Bare-bench exit — no consolation prize, just the drive home.
            _qm_res = [
                "He's back at the crossword before the door is half down. A bare bench is nobody's fault.",
                "The ring road takes you home the long way it always does.",
            ]

    call screen event_outcome(title="THE QUARTERMASTER", art=_qm_art, result=_qm_res)
    return


## ---------------------------------------------------------------------------
## THE RANGE INSTRUCTOR [deck-craft] — trades in HP, not CZK (distinct from
## designer_of_forms). DRILL: remove 1 chosen card, -8 HP. SHARPEN: upgrade 1
## chosen card, -8 HP. LEAVE: -6 Hatred. Both deck-ops cost the same, so the
## pick is "thin vs upgrade vs rest" — no dominant option.
## ---------------------------------------------------------------------------

label ev_the_range:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _rg_art = "images/events/ev_the_range.jpg"
        _rg_removable = [c for c in player_deck.cards if c not in CLASS_SIGNATURE_CARDS]
        _rg_upgradeable = [c for c in player_deck.cards if is_upgradeable(c)]
        _rg_body = [
            "The police range, late and empty. The old instructor who drilled half the district is still at the back bench, the way he always is. He's watched you shoot, and work, and he's unimpressed in the specific, fond way of a man who gave up on surprise years ago.",
            "'Too much hand,' he says, not looking up from the slide. 'I can fix one thing tonight. But I take before I give — that's the trade.'",
        ]
        _rg_choices = [
            {
                "id": "drill",
                "label": "[ DRILL OUT A HABIT ]",
                "desc": ec("- 8 HP") + ".  " + eg("Remove a card.") + "  One bad habit, gone for good.",
                "enabled": len(_rg_removable) >= 1,
                "locked": "Nothing of yours is sloppy enough for him to bother with.",
            },
            {
                "id": "sharpen",
                "label": "[ SHARPEN ONE ]",
                "desc": ec("- 8 HP") + ".  " + eg("Upgrade a card.") + "  Same move, half the flinch.",
                "enabled": len(_rg_upgradeable) >= 1,
                "locked": "Nothing you carry can be filed any sharper.",
            },
            {
                "id": "leave",
                "label": "[ NOT TONIGHT ]",
                "desc": eg("- 6 Hatred") + ".  Rack it, sign out, leave the quiet to him.",
            },
        ]

    call screen event_screen(title="THE RANGE INSTRUCTOR", art=_rg_art, body=_rg_body, choices=_rg_choices)

    python:
        _rg_pick = _return

    if _rg_pick == "drill":
        python:
            _rg_lost = event_hurt(8)
            _rg_removable = [c for c in player_deck.cards if c not in CLASS_SIGNATURE_CARDS]
        call screen event_card_picker("DRILL OUT A HABIT", _rg_removable)
        python:
            player_deck.remove(_return)
            _rg_res = [
                "He makes you fire the bad way until your hand stops wanting it, then the right way — which is so much less work it's almost insulting.",
                ec("- {} HP.".format(_rg_lost)) + "   " + eg("Removed a card."),
            ]
        call screen event_outcome(title="THE RANGE INSTRUCTOR", art=_rg_art, result=_rg_res)
        return

    elif _rg_pick == "sharpen":
        python:
            _rg_lost = event_hurt(8)
            _rg_upgradeable = [c for c in player_deck.cards if is_upgradeable(c)]
        call screen event_card_picker("SHARPEN ONE TECHNIQUE", _rg_upgradeable)
        python:
            upgrade_card_in_deck(_return)
            _rg_res = [
                "He runs you on the one move until it's clean: the same move, half the flinch. He nods once, which from him is a parade.",
                ec("- {} HP.".format(_rg_lost)) + "   " + eg("Upgraded a card."),
            ]
        call screen event_outcome(title="THE RANGE INSTRUCTOR", art=_rg_art, result=_rg_res)
        return

    else:
        python:
            stats.increment_stats_pcr_hatred(-6)
            _rg_res = [
                "You rack the pistol, sign the book, and leave him to the strip light and the unswept brass. Out in the lot the thing in your chest stops counting down and just goes quiet.",
                eg("- 6 Hatred."),
            ]
        call screen event_outcome(title="THE RANGE INSTRUCTOR", art=_rg_art, result=_rg_res)
        return


## ---------------------------------------------------------------------------
## THE TAIL [fight] — the Colonel's reach made flesh, late band. CORNER THEM
## (event_fight, hard) for rare gear + a card + 7,500 CZK; LOSE THEM (-4,000 CZK,
## -4 Hatred, no fight); or LET THEM FOLLOW (+8 Hatred, the free non-violent
## option). Loss routes through forced_detour("colonel_tail", "hard").
## ---------------------------------------------------------------------------

label ev_the_tail:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _tl_art = "images/events/ev_the_tail.jpg"
        _tl_can_lose = stats.available_money >= 4000
        _tl_body = [
            "Three days now, the same face in your wake — the petrol-station mirror, two cars back on the road home, across the tram aisle behind a newspaper nobody's read since the war. One of the Colonel's, sent to be noticed. The leash, before the thirtieth.",
            "Tonight you walk past your turn, out to where the lamps give up and the road ends. The footsteps follow, patient. At the dead end you stop. So do they. You turn around.",
        ]
        _tl_choices = [
            {
                "id": "fight",
                "label": "[ CORNER THEM ]",
                "desc": ek("A hard fight.") + "  " + eg("Win: rare gear, a card, + {:,} CZK.".format(stats.money_gain_preview(7500))) + "  " + ec("Lose: they put you down hard."),
            },
            {
                "id": "lose",
                "label": "[ LOSE THEM IN THE PANELAKS ]",
                "desc": ec("- 4,000 CZK") + "  " + eg("- 4 Hatred") + ".  A burner, back-doubles, a taxi you abandon two districts over. He loses you a while.",
                "enabled": _tl_can_lose,
                "locked": "Shaking a professional costs money you don't have on you tonight.",
            },
            {
                "id": "ignore",
                "label": "[ LET THEM WALK YOU HOME ]",
                "desc": ec("+ 8 Hatred") + ".  Eyes forward, jaw shut, carry the stone the rest of the way to thirty.",
            },
        ]

    call screen event_screen(title="THE TAIL", art=_tl_art, body=_tl_body, choices=_tl_choices)

    python:
        _tl_pick = _return

    if _tl_pick == "fight":
        call event_fight("colonel_tail", "hard") from _call_tail_fight
        if _return == "defeat":
            return
        python:
            _tl_cash = 7500
            _tl_cash_disp = stats.money_gain_preview(_tl_cash)
            stats.increment_stats_value_money(_tl_cash)
            _tl_relic = random_unowned_relic(relic_drop_weights("hard", True))   ## boss weights — rare lean
            _tl_relic_line = ""
            if _tl_relic:
                grant_relic(_tl_relic, silent=True)
                _tl_relic_line = eg("Gear: {}.".format(RELIC_LIBRARY.get(_tl_relic, {}).get("name", "his kit")))
            _tl_trio = pick_battle_rewards("hard")
        call screen card_reward_trio_screen(cards=_tl_trio)
        python:
            _tl_got = _return
            if _tl_got and _tl_got not in ("skip", None):
                grant_card(_tl_got, silent=True)
            _tl_res = [
                "You turn before he's decided, and the half-second is the whole fight. He reaches into his jacket the way men reach when the desk job scared them and this never did — too slow.",
                "You go through his pockets the way the job taught you: off-the-books cash, a piece of kit too good for a man this expendable. The Colonel will hear about this differently than he planned.",
                eg("+ {:,} CZK.".format(_tl_cash_disp)) + "   " + (_tl_relic_line + "   " if _tl_relic_line else "") + (eg("Drafted a card.") if (_tl_got and _tl_got not in ("skip", None)) else ""),
            ]
        play music "audio/random_event_bed.wav" fadein 1.0
        call screen event_outcome(title="THE TAIL", art=_tl_art, result=_tl_res)
        return

    elif _tl_pick == "lose":
        python:
            stats.try_spend_money(4000)
            stats.increment_stats_pcr_hatred(-4)
            _tl_res = [
                "Two hours making yourself expensive to follow — a burner dumped, back-doubles through courtyards you grew up in, a taxi ditched two districts over. Somewhere in there his headlights come unstuck from yours.",
                ec("- 4,000 CZK.") + "   " + eg("- 4 Hatred."),
            ]
        call screen event_outcome(title="THE TAIL", art=_tl_art, result=_tl_res)
        return

    else:
        python:
            stats.increment_stats_pcr_hatred(8)
            _tl_res = [
                "You keep the same pace — changing it would tell him something — and let him walk you home, still across the road when your light comes on. He'll be there tomorrow, and every day to the thirtieth, sanding you down a grain at a time.",
                ec("+ 8 Hatred."),
            ]
        call screen event_outcome(title="THE TAIL", art=_tl_art, result=_tl_res)
        return


## ---------------------------------------------------------------------------
## THE SIDE GIG [coding] — a freelance ticket due by morning, and the first
## place the run reads your Coding skill back at you. FIX IT PROPERLY is the
## skill check: at 100+ Coding the same ticket is two clean hours at full
## rate (+12k, +10 Coding, no cost) — below that it stays on the screen,
## locked, so the player sees exactly what the skill buys. The all-nighter
## brute-forces Coding for HP; ship-it-half-done is small clean cash; sleep
## is Hatred relief at the cost of the gig.
## ---------------------------------------------------------------------------

label ev_the_side_gig:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _sg_art = "images/events/ev_the_side_gig.jpg"
        _sg_pro = (stats.coding_skill >= 100)
        _sg_body = [
            "A message from a guy who knows a guy: a real freelance ticket, due by morning, off the books — the only kind your name can take right now.",
            "The laptop's open on the kitchen table. The shift starts in six hours. The bug doesn't care about either.",
        ]
        _sg_choices = [
            {
                "id": "pro",
                "label": "[ FIX IT PROPERLY ]",
                "enabled": _sg_pro,
                "desc": eg("+ {:,} CZK".format(stats.money_gain_preview(12000))) + ".  " + eg("+ 10 Coding") + ".  Two hours, clean diff, full rate.",
                "locked": "You open the repo and the bug looks back from three layers deeper than you can read. Need 100+ Coding.",
            },
            {
                "id": "grind",
                "label": "[ PULL THE ALL-NIGHTER ]",
                "desc": ec("- 15 HP") + ".  " + eg("+ 25 Coding") + ".  Burn the night, ship it clean.",
            },
            {
                "id": "ship",
                "label": "[ SHIP IT HALF-DONE ]",
                "desc": eg("+ {:,} CZK".format(stats.money_gain_preview(5000))) + ".  " + eg("+ 8 Coding") + ".  Good enough is a paid invoice.",
            },
            {
                "id": "sleep",
                "label": "[ SLEEP ]",
                "desc": eg("- 8 Hatred") + ".  The bug'll keep. So will you, barely.",
            },
        ]

    call screen event_screen(title="THE SIDE GIG", art=_sg_art, body=_sg_body, choices=_sg_choices)

    python:
        _sg_pick = _return
        _sg_res = []
        if _sg_pick == "pro":
            _sg_gain = stats.money_gain_preview(12000)
            stats.increment_stats_value_money(12000)
            stats.increment_stats_coding_skill(10)
            _sg_res = [
                "You read the stack trace like a gas bill. Two hours, one clean diff, tests green — you bill the whole night anyway, because that's what the rate card says.",
                "The guy who knows a guy saves your number under a real name. Somewhere out there your future CV grew a line nobody at the precinct will ever see.",
                eg("+ {:,} CZK.".format(_sg_gain)) + "   " + eg("+ 10 Coding."),
            ]
        elif _sg_pick == "grind":
            _sg_lost = event_hurt(15)
            stats.increment_stats_coding_skill(25)
            _sg_res = [
                "You don't sleep. You ship at 06:40, twenty minutes before the alarm, and the thing actually runs. You learned more in one night than in a month of the academy.",
                ec("- {} HP.".format(_sg_lost)) + "   " + eg("+ 25 Coding."),
            ]
        elif _sg_pick == "ship":
            _sg_gain = stats.money_gain_preview(5000)
            stats.increment_stats_value_money(5000)
            stats.increment_stats_coding_skill(8)
            _sg_res = [
                "You ship what works and flag the rest as 'known issues.' It clears, the invoice is real, and a little of the night stuck to your hands as skill.",
                eg("+ {:,} CZK.".format(_sg_gain)) + "   " + eg("+ 8 Coding."),
            ]
        else:
            stats.increment_stats_pcr_hatred(-8)
            _sg_res = [
                "You shut the laptop and sleep like a man with a clear conscience he hasn't earned. The gig goes to someone hungrier; morning comes a little softer for it.",
                eg("- 8 Hatred."),
            ]

    call screen event_outcome(title="THE SIDE GIG", art=_sg_art, result=_sg_res)
    return


## ---------------------------------------------------------------------------
## THE CONTRACT [coding] — the recruiter's paid trial, the real way out. GRIND
## buys big Coding for HP; PAIR buys Coding for CZK (a contractor carries you);
## TURN IT DOWN costs Hatred (refusing the door out). The run's biggest single
## Coding score, late band.
## ---------------------------------------------------------------------------

label ev_the_contract:

    scene bg_random_event
    play music "audio/random_event_bed.wav" fadein 1.0

    python:
        _ct_art = "images/events/ev_the_contract.jpg"
        _ct_can_pair = stats.available_money >= 12000
        _ct_body = [
            "The recruiter from the interview didn't ghost you. A paid trial — a real company, the kind of salary that ends the countdown early, if the thirtieth doesn't end it first.",
            "It's a take-home, due in two days, and it's beyond you right now — unless you make it not beyond you tonight.",
        ]
        _ct_choices = [
            {
                "id": "grind",
                "label": "[ GRIND IT OUT ]",
                "desc": ec("- 18 HP") + ".  " + eg("+ 30 Coding") + ".  Two days, no sleep, pure focus.",
            },
            {
                "id": "pair",
                "label": "[ PAIR WITH A PRO ]",
                "desc": ec("- 12,000 CZK") + ".  " + eg("+ 18 Coding") + ".  Pay a contractor to carry you. You still learn, just less.",
                "enabled": _ct_can_pair,
                "locked": "A pro's day rate is 12,000 CZK. Not on you tonight.",
            },
            {
                "id": "decline",
                "label": "[ TURN IT DOWN ]",
                "desc": ec("+ 10 Hatred") + ".  Not ready. Tell yourself it's the timing.",
            },
        ]

    call screen event_screen(title="THE CONTRACT", art=_ct_art, body=_ct_body, choices=_ct_choices)

    python:
        _ct_pick = _return
        _ct_res = []
        if _ct_pick == "grind":
            _ct_lost = event_hurt(18)
            stats.increment_stats_coding_skill(30)
            _ct_res = [
                "You don't leave the flat for two days. You submit on fumes and cold coffee, and the reply comes back fast: they want to talk. For the first time the door out has your name on it.",
                ec("- {} HP.".format(_ct_lost)) + "   " + eg("+ 30 Coding."),
            ]
        elif _ct_pick == "pair":
            stats.try_spend_money(12000)
            stats.increment_stats_coding_skill(18)
            _ct_res = [
                "A contractor off a dodgy Telegram channel walks you through it line by line for a fee that hurts. You submit clean — couldn't have written it alone, but you understand every line now.",
                ec("- 12,000 CZK.") + "   " + eg("+ 18 Coding."),
            ]
        else:
            stats.increment_stats_pcr_hatred(10)
            _ct_res = [
                "You write the polite email — bad timing, maybe later. You know there's no later. The Colonel's clock doesn't pause for the version of you that wasn't ready.",
                ec("+ 10 Hatred."),
            ]

    call screen event_outcome(title="THE CONTRACT", art=_ct_art, result=_ct_res)
    return
