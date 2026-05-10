################################################################################
## REFACTOR - Opportunity Events (Micro-Events)
## ~30% chance on non-event days. Appear before daily activity menu.
## Bonus encounters — do NOT consume the daily activity slot.
## Pool-based: each event fires at most once per run.
################################################################################

init python:

    def check_opportunity_event():
        """
        Roll for an opportunity event on non-event days.
        Returns a label name to call, or None.
        ~30% chance to trigger. Pulls from a shuffled pool (no repeats).
        """
        _rand = __import__('random')

        if not hasattr(store, '_opportunity_pool'):
            store._opportunity_pool = [
                "opp_laptop_deal",
                "opp_free_webinar",
                "opp_overtime_slip",
                "opp_old_friend",
                "opp_garage_sale",
                "opp_the_snitch",
                "opp_night_run",
                "opp_freelance_ping",
            ]
            _rand.shuffle(store._opportunity_pool)

        if not store._opportunity_pool:
            return None

        if _rand.randint(1, 100) <= 30:
            return store._opportunity_pool.pop(0)

        return None


## ---------------------------------------------------------------------------
## OPPORTUNITY EVENT DISPATCHER
## ---------------------------------------------------------------------------

label opportunity_event_check:

    python:
        _opp_label = check_opportunity_event()

    if _opp_label is not None:
        call expression _opp_label from _call_expression
    else:
        pass

    return


## ---------------------------------------------------------------------------
## 1. THE LAPTOP DEAL
## -4,000 CZK, +2 coding/night for 5 days
## ---------------------------------------------------------------------------

label opp_laptop_deal:

    scene bg_police_interior

    python:
        _lap_cost = adjusted_cost(4000)
        _lap_cost_str = "{:,}".format(_lap_cost)

    "A colleague catches you in the corridor before shift."
    "'Hey JB — I'm selling my old ThinkPad. X230, runs Linux, still solid. [_lap_cost_str] CZK. Interested?'"
    "It's not a gaming rig. But it's a second machine you could code on at home without borrowing the station laptop."

    menu:
        "[[OPPORTUNITY] Buy the ThinkPad. (-[_lap_cost_str] CZK, +2 Coding/night for 5 days)":
            python:
                if not stats.try_spend_money(_lap_cost):
                    renpy.say(None, "[[INSUFFICIENT FUNDS] You check your wallet. You can't swing {:,} right now.".format(_lap_cost))
                    renpy.jump("opp_laptop_deal_pass")
                store._laptop_buff_days = 5

            "You hand him the cash. He hands you a ThinkPad with three stickers on it and a missing key."
            "'The 'E' key sticks sometimes,' he says. 'Just hit it harder.'"
            "You don't care. You have a machine now. Tonight, you code."

            window hide
            show screen outcome_panel("- {} CZK. [LAPTOP BUFF] +2 Coding/night for 5 days.".format(_lap_cost))
            pause
            hide screen outcome_panel

            return

        "Pass. Too expensive right now.":
            jump opp_laptop_deal_pass

label opp_laptop_deal_pass:
    "You shake your head. 'Not this month.' He shrugs and walks away."
    "Someone else will buy it by lunch."
    return


## ---------------------------------------------------------------------------
## 2. FREE WEBINAR TONIGHT
## +8 coding, skip activity
## ---------------------------------------------------------------------------

label opp_free_webinar:

    scene bg_police_interior

    "You spot a link in a coding Discord while checking your phone on break."
    "'FREE WEBINAR: Intro to Flask — Build Your First API in 90 Minutes. Tonight 6PM.'"
    "It's free. It's tonight. But it'll take your whole evening."

    menu:
        "[[OPPORTUNITY] Attend the webinar. (+8 Coding)":
            python:
                stats.increment_stats_coding_skill(8)

            "You spend the evening glued to your screen."
            "The instructor types faster than you can think. But by the end, you have a working API that returns 'Hello World' in JSON."
            "It's not much. But you built it. With your hands. On purpose."

            window hide
            show screen outcome_panel("+8 CODING SKILL. Your evening is gone but your brain is fuller.")
            pause
            hide screen outcome_panel

            return

        "Pass. I have other plans tonight.":
            "You bookmark the link. You will never open it again."
            return


## ---------------------------------------------------------------------------
## 3. OVERTIME SLIP
## +5,000 CZK, +10 hatred
## ---------------------------------------------------------------------------

label opp_overtime_slip:

    scene bg_police_interior

    "The shift supervisor drops a form on your desk."
    "'Need someone for a double. Cash in hand, no questions. 5,000 CZK.'"
    "He's already walking away. He assumes you'll say yes. Everyone always says yes."

    menu:
        "[[OPPORTUNITY] Take the overtime. (+5,000 CZK, +10 Hatred)":
            python:
                stats.increment_stats_value_money(5000)
                stats.increment_stats_pcr_hatred(10)

            "You work sixteen hours straight."
            "By hour twelve you stop being a person and start being a function. Input: crime. Output: paperwork."
            "At the end he hands you the cash in an envelope. No receipt. No record."
            "This is how the system keeps you. One envelope at a time."

            window hide
            show screen outcome_panel("+5,000 CZK, +10 PCR HATRED. Another day sold.")
            pause
            hide screen outcome_panel

            return

        "Pass. My time is worth more than that.":
            "'Not today,' you say. He blinks. Nobody says no."
            "'Alright,' he mutters. 'Your loss.'"
            "It's not a loss. But try explaining that to a man who measures everything in overtime slips."
            return


## ---------------------------------------------------------------------------
## 4. THE OLD FRIEND
## -15 hatred, -1,500 CZK (tab)
## ---------------------------------------------------------------------------

label opp_old_friend:

    scene bg_police_interior

    python:
        _beers_cost = adjusted_cost(1500)
        _beers_cost_str = "{:,}".format(_beers_cost)

    "Your phone buzzes. A name you haven't seen in months."
    "'JB! I'm in town. Beers tonight? My treat — well, until I run out, then it's yours.'"
    "It's Tomáš. You grew up together. He has no idea what your job is doing to you, and that's exactly why this might help."

    menu:
        "[[OPPORTUNITY] Go for beers. (-[_beers_cost_str] CZK, -15 Hatred)":
            python:
                if not stats.try_spend_money(_beers_cost):
                    renpy.say(None, "[[INSUFFICIENT FUNDS] You'd love to, but you're counting coins for groceries. Not tonight.")
                    renpy.jump("opp_old_friend_pass")
                stats.increment_stats_pcr_hatred(-15)

            "You meet at a bar that hasn't changed its menu since 2007."
            "He talks about his wife, his dog, his new car that makes a weird noise."
            "Normal things. Things that exist outside the station, outside the uniform, outside the rank structure."
            "You laugh. Actually laugh. The sound surprises you."
            "You pick up the tab. Worth every crown."

            window hide
            show screen outcome_panel("- {} CZK, -15 PCR HATRED. You remembered what normal feels like.".format(_beers_cost))
            pause
            hide screen outcome_panel

            return

        "Pass. Not tonight.":
            jump opp_old_friend_pass

label opp_old_friend_pass:
    "'Can't make it,' you type. 'Next time.'"
    "You both know there won't be a next time. Not while you're still here."
    return


## ---------------------------------------------------------------------------
## 5. GARAGE SALE FIND
## -200 CZK, +5 coding
## ---------------------------------------------------------------------------

label opp_garage_sale:

    scene bg_police_interior

    python:
        _book_cost = adjusted_cost(200)
        _book_cost_str = "{:,}".format(_book_cost)

    "On the way to work, you pass a garage sale. A cardboard box of books, [_book_cost_str] CZK each."
    "One of them catches your eye: 'Automate the Boring Stuff with Python.' Dog-eared, coffee-stained, annotated in pencil."
    "Someone else's notes are scribbled in the margins. Half of them are wrong. But you'll learn from the corrections."

    menu:
        "[[OPPORTUNITY] Buy the book. (-[_book_cost_str] CZK, +5 Coding)":
            python:
                if not stats.try_spend_money(_book_cost):
                    renpy.say(None, "[[INSUFFICIENT FUNDS] You don't have {:,} CZK to spare. You put the book back.".format(_book_cost))
                    renpy.jump("opp_garage_sale_pass")
                stats.increment_stats_coding_skill(5)

            "You read it during lunch. You read it during the afternoon briefing."
            "By the end of shift you've written a script that renames files in bulk. It's useless. It's beautiful."

            window hide
            show screen outcome_panel("- {} CZK, +5 CODING SKILL. The margins taught you more than the text.".format(_book_cost))
            pause
            hide screen outcome_panel

            return

        "Pass. I don't need another book I won't finish.":
            jump opp_garage_sale_pass

label opp_garage_sale_pass:
    "You walk past. The book will be gone by afternoon."
    return


## ---------------------------------------------------------------------------
## 6. THE SNITCH
## Store info — affects a future random event outcome
## ---------------------------------------------------------------------------

label opp_the_snitch:

    scene bg_police_interior

    "A colleague you barely know corners you by the coffee machine."
    "He looks left. He looks right. Then he leans in."
    "'I've got something on Lieutenant Kovář. Expense reports. Doctored. Want to know?'"
    "This is the kind of information that can be a shield or a grenade. Depending on when you use it."

    menu:
        "[[OPPORTUNITY] Listen. Store the information.":
            python:
                grant_card("snitch_info", silent=True)

            "He talks for twelve minutes. You memorize the dates, the amounts, the account numbers."
            "You don't write anything down. That would be evidence."
            "'You didn't hear this from me,' he says."
            "'Hear what?' you say."
            "He nods. He walks away. You pour your coffee."
            "The information sits in your head like a loaded gun in a drawer. You hope you never need it."

            window hide
            show screen outcome_panel("[INFO STORED] You know something about Lt. Kovář. [CARD] SNITCH INFO acquired.")
            pause
            hide screen outcome_panel

            return

        "Pass. I don't want to know.":
            "'Keep it,' you say. 'I've got enough problems.'"
            "He shrugs. 'Your call. But if Kovář comes for you, don't say I didn't offer.'"
            "You pour your coffee. You drink it. You don't think about Lieutenant Kovář."
            return


## ---------------------------------------------------------------------------
## 7. NIGHT RUN
## -8 hatred today, +3 hatred tomorrow (sore)
## ---------------------------------------------------------------------------

label opp_night_run:

    scene bg_police_interior

    "2 AM. You're staring at the ceiling."
    "Sleep isn't coming. The shift plays on repeat behind your eyelids."
    "You could lie here and marinate in it. Or you could run."

    menu:
        "[[OPPORTUNITY] Go for a run. (-8 Hatred now, +3 Hatred tomorrow)":
            python:
                stats.increment_stats_pcr_hatred(-8)
                store._night_run_penalty = True

            "You lace up and step outside. The city is empty. The streetlights are yours."
            "You run without music. Just your breathing and the sound of your shoes on wet pavement."
            "By kilometer three, the noise in your head starts to fade."
            "By kilometer five, there's nothing left but the rhythm."
            "You come home soaked in sweat. You sleep for four hours straight. No dreams."

            window hide
            show screen outcome_panel("-8 PCR HATRED. [WARNING] You'll feel the soreness tomorrow (+3 Hatred).")
            pause
            hide screen outcome_panel

            return

        "Pass. Stay in bed.":
            "You roll over. You stare at the wall instead of the ceiling."
            "Eventually something that resembles sleep arrives. It's not restful, but it's something."
            return


## ---------------------------------------------------------------------------
## 8. FREELANCE PING
## Coding >= 40: +3,000 CZK, +3 coding
## Coding < 40: +5 hatred (embarrassment)
## ---------------------------------------------------------------------------

label opp_freelance_ping:

    scene bg_police_interior

    "Your phone buzzes. Discord DM from a stranger."
    "'Hey, saw your GitHub. Need a quick Python script — CSV parser, nothing fancy. 3k CZK if you can do it by tonight.'"
    "3,000 CZK for a few hours of work. If you're good enough."

    menu:
        "[[OPPORTUNITY] Take the gig. (Requires Coding >= 40)":
            python:
                if stats.coding_skill >= 40:
                    stats.increment_stats_value_money(3000)
                    stats.increment_stats_coding_skill(3)
                    store._freelance_success = True
                else:
                    stats.increment_stats_pcr_hatred(5)
                    store._freelance_success = False

            if store._freelance_success:
                "You open your laptop. CSV parser. Pandas, read_csv, clean the headers, export."
                "It takes you two hours. You send it. He sends the money."
                "'Clean code,' he writes. 'I'll ping you again.'"
                "3,000 CZK for two hours of work you actually enjoyed. This is what the other side looks like."

                window hide
                show screen outcome_panel("+3,000 CZK, +3 CODING SKILL. Your first freelance client.")
                pause
                hide screen outcome_panel
            else:
                "You open your laptop. CSV parser. Should be simple."
                "It's not simple. You spend three hours fighting with pandas before realizing you imported the wrong library."
                "You send what you have. He doesn't respond."
                "An hour later: 'Sorry man, I found someone else. No hard feelings.'"
                "There are hard feelings."

                window hide
                show screen outcome_panel("+5 PCR HATRED. You weren't ready. That stings more than the lost money.")
                pause
                hide screen outcome_panel

            return

        "Pass. Not ready for freelance yet.":
            "You type 'sorry, busy tonight' and close Discord."
            "The message sits there. Read. No reply."
            return
