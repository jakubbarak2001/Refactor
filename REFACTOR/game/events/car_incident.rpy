################################################################################
## REFACTOR - Arc I: The Car Incident
## Ported verbatim from car_incident_event.py
################################################################################

label car_incident:

    play music "audio/enter_the_code_theme.mp3" fadein 1.0

    call screen arc_title_card("I", "THE INCIDENT") with arc_fade
    scene bg_parking_lot with compile_flash
    show jb neutral at char_left

    "It is 06:45 AM. The sun is technically rising, but in this part of Bohemia, it just looks like the sky is slowly bruising purple."
    "You just parked your private car. You are already late for the overtime shift at the other station."
    "Your brain is running on 3 hours of sleep and a protein bar that tasted like chalk."

    "You rush to the service vehicle — a battered Octavia that smells permanently of wet dog and criminals."
    "You throw it into reverse, trusting your muscle memory more than your eyes."
    "You are a professional driver, right? You did the course."

    show jb worried at char_left

    "It wasn't a loud noise. It was a sickeningly polite {i}crunch{/i}."
    "Like stepping on a very large, very expensive beetle."
    "You freeze. You look in the mirror. You see nothing."

    "You get out. You look."

    "Your bumper is intimately kissing the door of the Commandant's brand new Superb."
    "It's not just a scratch. It's a statement."

    ## Decision
    "You stand between the cars. The silence of the parking lot is heavy."
    "You have a split second decision to make before a colleague walks out with a cigarette."

    menu:
        "[[BIOHACKER]] CALCULATE FIRST — Run probability. Check blind spots. Execute optimal sequence. (78%% success)" if stats.player_class == "biohacker":
            jump car_incident_biohacker_calc

        "THE 'MACGYVER' MANEUVER — Try to buff out the scratch with spit and your sleeve. If it works, you saw nothing. (50%% chance)":
            jump car_incident_cover_up

        "THE 'GOOD SOLDIER' — Go inside, report it, fill out the forms, and accept the humiliation.":
            jump car_incident_confess


## ---------------------------------------------------------------------------
## PATH: CONFESSION (safe path)
## ---------------------------------------------------------------------------

label car_incident_confess:

    scene bg_police_interior
    show jb bored at char_left

    "You sigh. You are an adult. You take responsibility."
    "You walk inside, find the shift commander, and tell him."

    "He looks at you over his glasses. Then at the clock. Then back at you."
    "'Great start to the morning, JB. Really stellar performance.'"

    "He hands you a stack of papers thick enough to kill a rat."
    "'Fill these out. Insurance will cover most of it, but you're paying the deductible.'"
    "'And don't expect a Christmas bonus.'"

    python:
        stats.increment_stats_pcr_hatred(10)
        stats.increment_stats_value_money(-2000)

    show screen outcome_panel("-2,000 CZK (Deductible), +10 PCR HATRED (Humiliation).")
    pause
    hide screen outcome_panel

    "At least it's over. No lawyers. No Colonel. Just pure, unadulterated bureaucracy."

    jump car_incident_end


## ---------------------------------------------------------------------------
## PATH: COVER UP (risky path — 50/50)
## ---------------------------------------------------------------------------

label car_incident_cover_up:

    scene bg_parking_lot
    show jb worried at char_left

    "You lick your thumb and furiously rub the scratch on the Superb."
    "It's not working. In fact, you're pretty sure you just made it shinier."

    python:
        _roll = __import__('random').randint(1, 100)

    python:
        if _roll <= 50:
            renpy.jump("car_incident_cover_up_success")
        else:
            renpy.jump("car_incident_caught")


label car_incident_cover_up_success:

    show jb determined at char_left

    "You spit on your sleeve and scrub harder."
    "The white mark disappears."
    "There is a tiny dent left, but you'd have to look for it with a microscope."

    "You jump into your car and drive away, heart pounding."
    "You got away with it. You magnificent bastard."

    python:
        stats.increment_stats_pcr_hatred(-5)

    show screen outcome_panel("0 CZK LOST, -5 PCR HATRED (The thrill of crime).")
    pause
    hide screen outcome_panel

    jump car_incident_end


## ---------------------------------------------------------------------------
## CAUGHT — leads to Paul Goodman sub-path
## ---------------------------------------------------------------------------

label car_incident_caught:

    show jb worried at char_left

    "'HEY! WHAT ARE YOU DOING?!'"

    "You freeze. You turn around."
    "It's not a colleague. It's the traffic camera you completely forgot about."
    "And standing right under it is the Shift Commander, holding his morning coffee, watching you."

    ## Stop music and play the colonel car incident cutscene
    stop music fadeout 1.5
    scene bg_black with fade
    hide jb worried

    $ renpy.movie_cutscene("video/colonel_car_incident.webm")

    scene bg_police_office with fade
    show colonel omniman think at colonel_think_pos

    "Fast forward 2 hours. The Colonel has arrived at the station and is waiting for you in his office."

    colonel "JB, you are a disgrace to the badge. You are a disgrace to the department. What were you thinking?"

    show colonel angry at char_right

    "They aren't calling it an accident. They are calling it 'Leaving the scene of a traffic incident'."
    "That's a crime. That's 'Lose your badge' territory."

    colonel "Sign this admission of guilt. Pay the full damages and we forget the disciplinary charge."

    python:
        _is_bodybuilder = (stats.player_class == "bodybuilder")

    menu:
        "SUBMIT — Pay the money. Eat the dirt. Keep your job.":
            jump car_incident_submit

        "CALL PAUL GOODMAN — Sue the department. Burn the bridge. (50%% chance)":
            jump car_incident_paul_goodman

        "[[BODYBUILDER PERK]] INTIMIDATE — Flex on the Colonel. Literally." if _is_bodybuilder:
            jump car_incident_bodybuilder_flex

        "[[DARK EMPATH]] READ HIM — Give him the outcome he already wants." if stats.player_class == "dark_empath":
            jump car_incident_dark_empath_read


label car_incident_submit:

    scene bg_police_office
    show jb bored at char_left

    "You sign the paper."
    "Your hand is shaking."
    "You walk out 8,000 CZK poorer and with a hatred for this place that burns like acid."

    python:
        stats.increment_stats_pcr_hatred(25)
        stats.increment_stats_value_money(-8000)

    show screen outcome_panel("-8,000 CZK, +25 PCR HATRED.")
    pause
    hide screen outcome_panel

    jump car_incident_end


label car_incident_paul_goodman:
    python:
        unlock_achievement("paul_fan")

    scene bg_police_office
    show jb determined at char_left

    "'No. I'm calling my lawyer.'"

    colonel "Lawyer? JB, you can't afford a lawyer."

    jb "'You clearly have not heard of Paul Goodman.'"

    "You call Paul. He answers on the first ring."
    "'Did you say Police Department? Discrimination? Emotional distress? Say no more.'"
    "'I'll take the case Pro Bono. We go to war.'"

    python:
        _win_roll = __import__('random').randint(1, 100)

    python:
        if _win_roll <= 50:
            renpy.jump("car_incident_paul_wins")
        else:
            renpy.jump("car_incident_paul_loses")


label car_incident_paul_wins:

    show jb determined at char_left

    "Paul Goodman is a shark in a cheap suit."
    "He found a loophole in the parking lot regulations."
    "He threatened to sue the Colonel for 'Unsafe Workplace Environment'."
    "The Department settled to make him go away."

    python:
        stats.increment_stats_value_money(15000)
        stats.increment_stats_pcr_hatred(-30)

    "[[CRITICAL SUCCESS]]: You received a settlement of 15,000 CZK!\nYour boss refuses to make eye contact with you."

    show screen outcome_panel("+15,000 CZK, -30 PCR HATRED (Justice tastes sweet).")
    pause
    hide screen outcome_panel

    jump car_incident_end


label car_incident_paul_loses:

    scene bg_police_office
    show colonel angry at char_right

    "The Colonel called in a favor."
    "The judge was his old drinking buddy."
    "Paul Goodman got held in contempt of court for wearing a neon tie."
    "You lost. Badly."

    python:
        stats.increment_stats_value_money(-12000)
        stats.increment_stats_pcr_hatred(50)

    "[[CRITICAL FAILURE]]: You have to pay court fees of 12,000 CZK.\nThe entire station is laughing at you. The Colonel sends you a 'Get Well Soon' card."

    show screen outcome_panel("-12,000 CZK, +50 PCR HATRED (Maximum Salt).")
    pause
    hide screen outcome_panel

    jump car_incident_end


## ---------------------------------------------------------------------------
## PATH: BODYBUILDER FLEX (Bodybuilder-exclusive)
## ---------------------------------------------------------------------------

label car_incident_bodybuilder_flex:

    python:
        unlock_achievement("bodybuilder_flex")

    scene bg_police_office
    show jb determined at char_left
    show colonel angry at char_right

    "You stand up. Very slowly."
    "The Colonel stops talking."
    "You are not a small man. You are not a tired man. You are a man who squats 200 kilos on Tuesdays."

    jb "'Colonel. With all due respect... I could pick up your car with my bare hands. And put it back exactly where I found it.'"

    "There is a long silence."
    "The Colonel looks at your neck. Then your shoulders. Then at the paperwork on his desk."
    "He makes a decision."

    colonel "'...I never saw anything. Get out of my office.'"

    "You walk out."
    "Nobody says anything."
    "The Shift Commander offers you a coffee. You decline. You already have the biggest pump of your life."

    python:
        stats.increment_stats_pcr_hatred(-10)
        stats.increment_stats_value_money(-1000)

    show screen outcome_panel("-1,000 CZK (coffee money), -10 PCR HATRED. [[BODYBUILDER PERK]] Colonel scared.")
    pause 2.5
    hide screen outcome_panel

    jump car_incident_end


## ---------------------------------------------------------------------------
## PATH: BIOHACKER CALCULATION (Biohacker-exclusive)
## ---------------------------------------------------------------------------

label car_incident_biohacker_calc:

    scene bg_parking_lot
    show jb determined at char_left

    "You don't panic. You calculate."
    "You check your watch. 3 minutes before the Shift Commander's coffee break ends."
    "You assess the camera — parking lot mount, 40° angle, blind spot on the east side."
    "You read the scratch. Superficial. 3mm depth. Polish-able in under 60 seconds."
    "You estimate: 78%% successful cover-up if you start immediately. 22%% if you hesitate."

    jb "'Execute.'"

    python:
        _bh_calc_roll = __import__('random').randint(1, 100)

    python:
        if _bh_calc_roll <= 78:
            renpy.jump("car_incident_biohacker_success")
        else:
            renpy.jump("car_incident_biohacker_fail")


label car_incident_biohacker_success:

    show jb determined at char_left

    "Spit. Sleeve. Circular motion. 45 seconds."
    "The mark fades. You're back in your car before the Commander exits the building."
    "You ran the probability. The probability held."

    python:
        stats.increment_stats_pcr_hatred(-8)

    show screen outcome_panel("-8 PCR HATRED [BIOHACKER: probability-optimized escape. 78%% confirmed].")
    pause
    hide screen outcome_panel

    jump car_incident_end


label car_incident_biohacker_fail:

    show jb worried at char_left

    "'HEY! WHAT ARE YOU DOING?!'"
    "The 22%% materialized."
    "There was a backup recording on the second camera. Angle you didn't account for."
    "The Shift Commander is watching you scrub the Colonel's car."
    "You failed to calculate the unknown unknowns."

    jump car_incident_caught


## ---------------------------------------------------------------------------
## PATH: DARK EMPATH READ (Dark Empath-exclusive)
## ---------------------------------------------------------------------------

label car_incident_dark_empath_read:

    python:
        unlock_achievement("dark_empath_read")

    scene bg_police_office
    show jb neutral at char_left
    show colonel angry at char_right

    "You look at the Colonel. Not at his rank. At him."
    "He is not angry. He is disappointed. And underneath the disappointment — territorial."
    "He recruited you. He personally sponsored your academy entry. You are his project, his validation."
    "He doesn't want 8,000 CZK. He wants to feel like he still controls the narrative."
    "Give him that. It costs you nothing."

    jb "'Colonel. With respect — I made a mistake. But the real question is what you want this to {i}mean{/i}.'"
    jb "'You can write me up. Make an example. Remind everyone who runs this station.'"
    jb "'Or you let it go, keep a capable officer who knows he owes you one, and nobody questions your judgment.'"
    jb "'Which version of the Colonel do you want them to remember?'"

    "Silence. A very long silence."
    "He looks at you the way a chess player looks at an unexpected move."

    show colonel disappointed at char_right

    colonel "'...Get out of my sight, JB.'"

    python:
        stats.increment_stats_pcr_hatred(-5)

    show screen outcome_panel("-5 PCR HATRED, 0 CZK [DARK EMPATH: gave him the authority he wanted].")
    pause
    hide screen outcome_panel

    jump car_incident_end


## ---------------------------------------------------------------------------
## CLOSING — grind objective
## ---------------------------------------------------------------------------

label car_incident_end:

    scene bg_police_interior
    show jb determined at char_left

    "FROM THIS MOMENT, THE GRIND BEGINS"
    "DEBUFF: You will gain +5 PCR HATRED daily."
    "MAIN OBJECTIVE: In the next 30 days, you need to become a FULLSTACK DEVELOPER."

    return
