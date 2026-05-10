################################################################################
## REFACTOR - Arc I: The Car Incident
## Single path: Admit. JB reports up the chain, Colonel arrives, mentor lecture.
## (Hide path removed — see git history. May return as a redesigned tradeoff.)
## Sets colonel_attitude for downstream events.
################################################################################

label car_incident:

    $ renpy.movie_cutscene("video/car_incident_intro.webm")

    play music "audio/enter_the_code_theme.mp3" fadein 1.0

    scene bg_parking_lot
    call screen arc_title_card("I", "THE INCIDENT") with arc_fade
    show jb neutral at char_left with dissolve
    pause 1.0

    "It is 06:30 AM. The sun is technically rising, but in this part of Bohemia, it just looks like the sky is slowly bruising purple."
    "You slept maybe two hours. Not by choice — your brain refused to clock out, and now it's punishing you for the disrespect."
    "You parked your private car ten minutes ago. You are already late for the overtime shift at the other station."

    if stats.player_class == "bodybuilder":
        "Your brain is running on two hours of sleep, a protein bar that tasted like chalk, and the dull ache of yesterday's deadlifts."
    elif stats.player_class == "dark_empath":
        "Your brain is running on two hours of sleep and the residue of a dream where you were reading the sergeant's face like a cheap paperback."
    elif stats.player_class == "biohacker":
        "Your brain is running on two hours of sleep, 200mg caffeine, 100mg L-theanine, and the precise regret of skipping the racetam stack."
    else:
        "Your brain is running on two hours of sleep and the leftover noise of yesterday."

    "You drop into the service vehicle — a battered Octavia that smells permanently of wet dog and criminals."
    "The back lane is always empty at this hour. Always. You've reversed out of this exact bay maybe four hundred times."
    "You don't check the mirror. You don't check the camera. You {i}know{/i} the lane."
    "You throw it into reverse and let muscle memory do the rest. Foot on the gas. Eyes half-closed against the morning."
    "You are a professional driver, {stshl=right?}"

    stop music fadeout 0.3

    show jb worried at char_left
    play sound "audio/car_scrape.mp3" volume 0.5

    "..."

    play music "audio/enter_the_code_theme.mp3" fadein 0.5

    "It wasn't a loud noise. It was a sickeningly polite {i}crunch{/i}."
    "Like stepping on a very large, very expensive beetle."
    "You freeze. You look in the mirror. You see grey."

    "You get out. You look."

    "The Kodiaq is parked sideways across the back lane. Diagonal. Front end jutting halfway into your reversing path. Like a dog that lost interest halfway through sitting down."
    "Nobody parks like that. Except the Commandant. Who parks where he wants."
    "Your rear bumper found his front grille at maybe four kilometres an hour. The geometry was inevitable."
    "The damage is barely there. A faint scuff on his bumper. A shadow of paint transfer on yours. You'd have to know it was there to find it."

    ## --- Flashback: this isn't the first time. JB has lived this script before. ---
    "You stand there. You stare at the paint transfer."
    "It's not the bumper that bothers you. It's the script."
    "You've heard this script before."
    "Six months ago. The expense reports."
    "Three months ago. The radio incident."
    "Last month. The thing with the keys."
    "And every {i}single{/i} time —"

    stop music fadeout 0.3
    scene bg_black with fade
    pause 0.4

    $ renpy.movie_cutscene("video/colonel_car_incident.webm")

    scene bg_parking_lot with fade
    show jb worried at char_left
    play music "audio/enter_the_code_theme.mp3" fadein 0.5

    "You snap back to the parking lot."
    "Your shirt is dry. Your ears are still ringing from a sound that technically ended six months ago."
    "The Colonel has had a documented mental breakdown over a filing cabinet that closed too loudly. What you just remembered was him on a {i}good{/i} day."
    "That was the small stuff. Misplaced keys. A radio left on during pursuit."
    "{cps=8}{b}{color=#ffcc00}{size=+12}THIS IS HIS CAR.{/size}{/color}{/b}{/cps}"

    "Above you, a window creaks open on the second floor. The Commandant's office."
    "He doesn't lean out. He doesn't say anything. He just sips his coffee and watches — the way a man watches a slow-motion car crash he has already filed the paperwork for."
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
        "The Commandant won't read this as damage. He'll read it as disrespect. The only variable is who tells him."
    elif stats.player_class == "biohacker":
        "One play. Lowest variance. You'd rather be the source of the report than the subject of it."

    "You'd rather be the one who tells them."

    jump car_incident_admit


## ---------------------------------------------------------------------------
## RESOLUTION — JB reports up the chain. Colonel arrives. Lecture, signature.
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

    "He picks up the phone. The Commandant already called the Colonel — this is just paperwork now."
    "Nobody is shouting. That is somehow worse."

    "The Colonel is 45 minutes away. He gets in his car anyway."

    ## Colonel arrives — quiet fade-through, no video here (already shown).
    stop music fadeout 1.5
    scene bg_black with fade
    pause 0.6
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
        grant_card("took_the_heat", silent=True)

    show screen outcome_panel("-3,500 CZK (your half of the deductible), +8 PCR HATRED, + card: TOOK THE HEAT (Skill, 1 cost, exhaust — gain 10 block, draw 1).")
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
## CLOSING — grind objective
## ---------------------------------------------------------------------------

label car_incident_end:

    scene bg_police_interior
    show jb determined at char_left

    "FROM THIS MOMENT, THE GRIND BEGINS."
    "DEBUFF: You will gain PCR HATRED every night."
    "MAIN OBJECTIVE: In the next 30 days, you need to become a FULLSTACK DEVELOPER."

    return
