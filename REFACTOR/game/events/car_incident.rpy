################################################################################
## REFACTOR - Arc I: The Car Incident
## Two paths: Admit / Hide. Both end with the Colonel arriving on Day 1.
## Trade-off: Admit pays small but earns the Colonel's attention (paternal).
##            Hide pays big and gets written off (hostile, lower oversight).
## Sets colonel_attitude for downstream events.
################################################################################

label car_incident:

    $ renpy.movie_cutscene("video/car_incident_intro.webm")

    play music "audio/enter_the_code_theme.mp3" fadein 1.0

    call screen arc_title_card("I", "THE INCIDENT") with arc_fade
    scene bg_parking_lot with arc_fade
    show jb neutral at char_left with dissolve

    "It is 06:45 AM. The sun is technically rising, but in this part of Bohemia, it just looks like the sky is slowly bruising purple."
    "You just parked your private car. You are already late for the overtime shift at the other station."

    if stats.player_class == "bodybuilder":
        "Your brain is running on 3 hours of sleep, a protein bar that tasted like chalk, and the dull ache of yesterday's deadlifts."
    elif stats.player_class == "dark_empath":
        "Your brain is running on 3 hours of sleep and the residue of a dream where you were reading the sergeant's face like a cheap paperback."
    elif stats.player_class == "biohacker":
        "Your brain is running on 3 hours of sleep, 200mg caffeine, 100mg L-theanine, and the precise regret of skipping the racetam stack."
    else:
        "Your brain is running on 3 hours of sleep and the leftover noise of yesterday."

    "You rush to the service vehicle — a battered Octavia that smells permanently of wet dog and criminals."
    "You throw it into reverse, trusting your muscle memory more than your eyes."
    "You are a professional driver, {stshl=right?}"

    stop music fadeout 0.3

    show jb worried at char_left
    play sound "audio/car_scrape.mp3" volume 0.5

    "..."

    play music "audio/enter_the_code_theme.mp3" fadein 0.5

    "It wasn't a loud noise. It was a sickeningly polite {i}crunch{/i}."
    "Like stepping on a very large, very expensive beetle."
    "You freeze. You look in the mirror. You see nothing."

    "You get out. You look."

    "Your bumper is intimately kissing the door of the Commandant's brand new Superb."
    "The damage is barely there. A faint scuff. A shadow of paint transfer. You'd have to know it was there to find it."

    ## Decision frame — both paths converge on the Colonel.
    "You stand between the cars. The parking lot is dead quiet. Shift change is in three minutes."

    if stats.player_class == "bodybuilder":
        "Your pulse is doing things that would concern a cardiologist. You hit 180 on the bike yesterday. This feels worse."
    elif stats.player_class == "dark_empath":
        "Your pulse is doing things you would, in any other context, find fascinating to study."
    elif stats.player_class == "biohacker":
        "Your pulse is doing things that would concern a cardiologist. HRV is going to be garbage tomorrow."
    else:
        "Your pulse is doing things that would concern a cardiologist."

    "Two facts settle into focus."
    "First: in a station this small, the Commandant {i}will{/i} find out by lunch. Cameras, gossip, his own paranoid morning walk-around — pick one."
    "Second: he will call the Colonel either way. That's how this place works. You are not getting out of a meeting today."

    if stats.player_class == "bodybuilder":
        "It's a scratch. The math is simple. The damage isn't the damage — the damage is who has to know."
    elif stats.player_class == "dark_empath":
        "The Commandant won't read this as damage. He'll read it as disrespect. That's the only variable."
    elif stats.player_class == "biohacker":
        "Two paths. One has known cost, low variance. The other is a coin flip with a long tail. Run the EV."

    menu:
        "ADMIT — Note on the windshield. Tell the supervisor. He files you as salvageable. (Pay small. He watches you closely from now on.)":
            jump car_incident_admit

        "HIDE — Spit, scrub, shuffle the Octavia. Pretend it didn't happen. He files you as a lost cause. (Pay big. He stops expecting anything from you.)":
            jump car_incident_hide


## ---------------------------------------------------------------------------
## PATH A: ADMIT — small cost, paternal Colonel (he's watching you now)
## ---------------------------------------------------------------------------

label car_incident_admit:

    scene bg_parking_lot
    show jb determined at char_left

    "You pull out a pen. You don't have paper."
    "You tear the corner off your overtime slip and write your name and badge number on the back."
    "Your handwriting looks like a seismograph during an earthquake, but it's legible."

    "You wedge the note under the Commandant's wiper blade."
    "Then you walk inside and find the shift supervisor."

    scene bg_police_interior
    show jb neutral at char_left

    "He looks at you over his glasses. Then at the clock. Then back at you."
    "'You're telling me this at 06:48 in the morning, JB. Before I've even had coffee.'"
    "'Great. Really stellar start to the day.'"

    "He picks up the phone. He calls the Commandant. The Commandant calls the Colonel."
    "Nobody is shouting. That is somehow worse."

    "The Colonel is 45 minutes away. He gets in his car anyway."

    ## Colonel arrives — video plays
    stop music fadeout 1.5
    scene bg_black with fade

    $ renpy.movie_cutscene("video/colonel_car_incident.webm")

    play music "audio/you_failed_me_son.mp3" fadein 1.0

    scene bg_police_office with fade
    show colonel omniman think at colonel_think_pos

    "By 09:00 he is sitting in the Commandant's chair. The Commandant is standing in the corner of his own office, which is its own kind of message."

    show colonel disappointed at char_right with dissolve
    show jb neutral at char_left with dissolve
    pause 0.5

    colonel "Sit down, JB."

    "You sit."

    colonel "You damaged a department vehicle. You reported it within three minutes. You wrote a note in your own handwriting and signed it with your badge number."
    colonel "That is the only reason this is a conversation and not a hearing."

    "He slides a single page across the desk. Insurance form. Deductible: 3,500 CZK. Out of your pocket. The Commandant 'forgot' to initial the line for splitting the cost."

    colonel "Sign it. Pay it by Friday. Don't make me come here again over a parking lot."

    show jb determined at char_left

    "You sign. He doesn't watch. He's already done with this part."

    colonel "JB."

    "You stop at the door."

    colonel "Honesty is the cheapest currency we have. Spend it before the expensive stuff."
    colonel "I'll be checking in on you. Often."

    "He lets that sit. Then he waves you out."

    python:
        stats.colonel_attitude = "paternal"
        stats.increment_stats_pcr_hatred(8)
        stats.increment_stats_value_money(-3500)

    show screen outcome_panel("-3,500 CZK (your half of the deductible), +8 PCR HATRED (he still drove 45 minutes to remind you who's watching).")
    pause
    hide screen outcome_panel

    if stats.player_class == "bodybuilder":
        "You did the work. The work was honesty. That counts for one rep."
    elif stats.player_class == "dark_empath":
        "You showed your hand on purpose. Now watch what they do with it."
    elif stats.player_class == "biohacker":
        "Lowest variance play. Floor is locked in. Now optimize from here."

    jump car_incident_end


## ---------------------------------------------------------------------------
## PATH B: HIDE — big cost, hostile Colonel (he writes you off)
## ---------------------------------------------------------------------------

label car_incident_hide:

    scene bg_parking_lot
    show jb worried at char_left

    "You crouch between the cars. Your knees crack like gunshots in the silence."
    "You spit on your sleeve. This is your life now. A grown man spitting on government property at dawn."
    "You scrub the white transfer paint in small circles. You reposition the Octavia six inches to the left to widen the gap. You kick gravel over the chips on the ground."

    "You step back. The scratch is still there if you look closely. But the angle is ambiguous now. The gravel looks undisturbed."

    "You walk inside like a man who has nothing to hide. Your face is a mask. Your armpits are a crime scene."
    "The shift supervisor nods at you. 'Morning, JB.' He suspects nothing. Yet."

    "You sit at your desk. You open a case file. You don't read a single word."
    "Your eyes keep drifting to the window. To the parking lot. To the Superb sitting there like evidence."

    scene bg_police_interior
    show jb neutral at char_left

    "14:00. The Commandant's door opens."

    stop music fadeout 0.1
    play sound "audio/metal-gear-alert-sound-effect.mp3"
    show screen alert_exclamation
    pause 1.2
    hide screen alert_exclamation

    play music "audio/enter_the_code_theme.mp3" fadein 1.0

    "He walks straight to your desk. He's holding a USB stick."
    "'JB. My office. Now.'"

    scene bg_police_office
    show jb neutral at char_left

    "He plugs the USB into his laptop and turns the screen toward you."
    "Parking lot camera. 06:45 AM. High angle, wide shot."
    "You watch yourself reverse into the Superb. You watch yourself crouch, scrub, kick gravel, walk away."
    "The footage is grainy, but it's enough."

    "'Every Tuesday,' the Commandant says. 'I review the footage every Tuesday.'"
    "'You forgot it was Tuesday, JB.'"

    "He picks up the phone and dials the Colonel's direct line."
    "You sit there and listen to him explain what you did."
    "The Colonel's voice is audible from across the desk. He doesn't raise it. That's worse."

    "The Colonel is 45 minutes away. He gets in his car anyway."

    ## Colonel arrives — video plays
    stop music fadeout 1.5
    scene bg_black with fade

    $ renpy.movie_cutscene("video/colonel_car_incident.webm")

    play music "audio/you_failed_me_son.mp3" fadein 1.0

    scene bg_police_office with fade
    show colonel omniman think at colonel_think_pos

    "He arrives at 15:30. He doesn't sign in at reception. Nobody asks him to."
    "He takes the Commandant's chair. The Commandant stands in the corner of his own office."

    show colonel angry at char_right with dissolve
    show jb neutral at char_left with dissolve
    pause 0.5

    colonel "I watched the footage in the car, JB. On my phone. While driving. That's how seriously I take this."

    "He lets that sit."

    colonel "You hit the car. Fine. Accidents happen. But you {i}walked away{/i}."

    jb "'It was a scratch, Colonel.'"

    colonel "It was a {i}choice{/i}. And you chose wrong."

    "He slides the repair bill across the desk. 7,000 CZK. Full repair plus a 'disciplinary processing fee.'"
    "You've never heard of a disciplinary processing fee. You're fairly certain he just invented it."

    colonel "Sign it."

    show jb neutral at char_left

    "You sign. There is no negotiation here. There never was."
    "This man drove 45 minutes to charge you a made-up fee for a parking lot scratch. That tells you everything you need to know about where you work."

    colonel "You can go."

    "You stand. You walk to the door."

    colonel "JB."

    "You stop."

    colonel "I'm not going to waste any more of my time on you."

    "You don't turn around. You know what his face looks like."
    "The face of a man who has just decided you are not worth saving."

    python:
        stats.colonel_attitude = "hostile"
        stats.increment_stats_pcr_hatred(20)
        stats.increment_stats_value_money(-7000)

    show screen outcome_panel("-7,000 CZK (repair + invented fee), +20 PCR HATRED (the system working exactly as designed).")
    pause
    hide screen outcome_panel

    if stats.player_class == "bodybuilder":
        "Seven thousand for a scuff. You can rep that out in a week of overtime. The bruise to your pride won't fade that fast."
    elif stats.player_class == "dark_empath":
        "He didn't want the money. He wanted the signature. He got both. File it under 'never again.'"
    elif stats.player_class == "biohacker":
        "Worst-case branch realized. Variance was the cost of admission. Update the model and move."

    "Somewhere in this building there are actual criminals. None of them got this much attention today."

    jump car_incident_end


## ---------------------------------------------------------------------------
## CLOSING — grind objective
## ---------------------------------------------------------------------------

label car_incident_end:

    scene bg_police_interior
    show jb determined at char_left

    "FROM THIS MOMENT, THE GRIND BEGINS."
    "DEBUFF: You will gain PCR HATRED every night."
    "MAIN OBJECTIVE: In the next 30 days, you need to become a FULLSTACK DEVELOPER."

    return
