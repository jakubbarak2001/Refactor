################################################################################
## REFACTOR - Arc I: The Car Incident
## Three paths: Own It / Assess & Patch / Walk Away
## Sets colonel_attitude for downstream events
## Caught paths trigger Colonel arrival + video on Day 1
################################################################################

label car_incident:

    $ renpy.movie_cutscene("video/car_incident_intro.webm")

    play music "audio/enter_the_code_theme.mp3" fadein 1.0

    call screen arc_title_card("I", "THE INCIDENT") with arc_fade
    scene bg_parking_lot with arc_fade
    show jb neutral at char_left with dissolve

    "It is 06:45 AM. The sun is technically rising, but in this part of Bohemia, it just looks like the sky is slowly bruising purple."
    "You just parked your private car. You are already late for the overtime shift at the other station."
    "Your brain is running on 3 hours of sleep and a protein bar that tasted like chalk."

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
    "It's not just a scratch. It's a statement."

    ## Decision
    "You stand between the cars. The parking lot is dead quiet."
    "Nobody saw. Not yet. Shift change is in three minutes."
    "Your pulse is doing things that would concern a cardiologist."

    menu:
        "OWN IT — Leave a note. Tell the shift supervisor. Handle it like a professional.":
            jump car_incident_own_it

        "ASSESS & PATCH — Check the damage. Reposition the car. Minimize the evidence.":
            jump car_incident_patch

        "WALK AWAY — You were never here. The parking lot was empty. Nothing happened.":
            jump car_incident_ghost


## ---------------------------------------------------------------------------
## PATH A: OWN IT (safe, predictable — no Colonel, no video)
## colonel_attitude = "paternal"
## ---------------------------------------------------------------------------

label car_incident_own_it:

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

    "He hands you a stack of forms."
    "'Insurance will cover most of it. You're paying the deductible. And you owe the Commandant a very sincere apology.'"

    "You fill out the forms. Your pen runs out twice."
    "The Commandant arrives at 08:00, sees the note, inspects the damage, and walks inside without a word."

    "At 08:15 he finds you in the break room."
    "'JB. I appreciate the honesty. Most guys would have bolted.'"
    "He shakes your hand. His grip could crack a walnut."
    "'Deductible is 3,000. I'll cover half. You pay yours by Friday.'"

    show jb determined at char_left

    "That's it. No speech. No power play. Just two professionals handling a problem."
    "If only the rest of this place worked like that."

    "Word travels. It always does in a police station."
    "By noon, the story has reached two districts over."

    python:
        stats.colonel_attitude = "paternal"
        stats.increment_stats_pcr_hatred(5)
        stats.increment_stats_value_money(-3000)

    show screen outcome_panel("-3,000 CZK (deductible), +5 PCR HATRED (another form, another process, another day).")
    pause
    hide screen outcome_panel

    "You did the right thing. That should count for something around here."
    "It never does."

    jump car_incident_end


## ---------------------------------------------------------------------------
## PATH B: ASSESS & PATCH (calculated risk — 60/40)
## Success: colonel_attitude = "suspicious"
## Caught: Colonel arrives Day 1, video plays, colonel_attitude = "disgusted"
## ---------------------------------------------------------------------------

label car_incident_patch:

    scene bg_parking_lot
    show jb worried at char_left

    "You crouch between the cars. Your knees crack like gunshots in the silence."
    "You run your finger along the scratch. It's deep enough to catch your nail, but not deep enough to see bare metal."
    "The dent is subtle. A shadow, really. You'd have to know it was there."

    "You check your watch. Two minutes before the morning smokers come out."
    "You spit on your sleeve."
    "This is your life now. A grown man spitting on government property at dawn."

    "You scrub the white transfer paint in small circles. Some of it flakes off."
    "You reposition the Octavia six inches to the left, creating the illusion of a wider gap."
    "You kick some gravel over the paint chips on the ground."

    "Your heart is hammering so hard you can feel it in your teeth."

    python:
        _patch_roll = __import__('random').randint(1, 100)

    if _patch_roll <= 60:
        jump car_incident_patch_success
    else:
        jump car_incident_patch_caught


label car_incident_patch_success:

    scene bg_parking_lot
    show jb determined at char_left

    "You step back. You assess your work."
    "The scratch is still there if you look closely. But the transfer paint is gone, and the angle of the Octavia makes it ambiguous."
    "Did someone hit the Superb? Or was it always like that? The gravel certainly looks undisturbed."

    "You walk inside. Your hands are still shaking. You shove them in your pockets."
    "The shift supervisor nods at you. 'Morning, JB.' He suspects nothing."

    "You sit down at your desk. You open a case file. You don't read a single word."
    "Your eyes keep drifting to the window. To the parking lot. To the Superb sitting there like evidence."

    python:
        unlock_achievement("damage_control")
        stats.colonel_attitude = "suspicious"
        stats.increment_stats_pcr_hatred(8)

    show screen outcome_panel("+8 PCR HATRED (you patched the car — now patch the knot in your stomach).")
    pause
    hide screen outcome_panel

    "You got away with it. Probably."
    "The word {i}probably{/i} is going to keep you company for a while."

    jump car_incident_end


label car_incident_patch_caught:

    scene bg_parking_lot
    show jb worried at char_left

    stop music fadeout 0.1
    play sound "audio/metal-gear-alert-sound-effect.mp3"
    show screen alert_exclamation
    pause 1.2
    hide screen alert_exclamation

    play music "audio/enter_the_code_theme.mp3" fadein 1.0

    "'JB? What the hell are you doing down there?'"

    "You freeze. Your sleeve is still wet."
    "Sergeant Dvořák is standing three meters away, cigarette in one hand, coffee in the other."
    "He looks at the Superb. He looks at the Octavia. He looks at the gravel you kicked."
    "He looks at you, crouching like a man who just lost a contact lens and also his dignity."

    "'Is that... is that the Commandant's car?'"

    show jb neutral at char_left

    "There is no lie good enough for this moment."
    "'Yeah,' you say. 'Yeah, that's the Commandant's car.'"

    "Dvořák takes a long drag of his cigarette."
    "'You know I have to report this.'"
    "'I know.'"
    "'The covering up part makes it worse.'"
    "'I also know that.'"

    scene bg_police_interior
    show jb neutral at char_left

    "By 09:00, the Commandant has a full incident report on his desk."
    "By 09:30, he's called the Colonel's office."
    "Not because of the scratch. Because you tried to hide it."

    "The Colonel is 45 minutes away. He gets in his car anyway."

    ## Colonel arrives — video plays
    stop music fadeout 1.5
    scene bg_black with fade

    $ renpy.movie_cutscene("video/colonel_car_incident.webm")

    play music "audio/you_failed_me_son.mp3" fadein 1.0

    scene bg_police_office with fade
    show colonel omniman think at colonel_think_pos

    "Fast forward two hours. The Colonel is sitting behind the Commandant's desk like he owns it. He does, technically."
    "He's been waiting for you. The whole station knows. Nobody warned you."

    show colonel angry at char_right with dissolve
    show jb neutral at char_left with dissolve
    pause 0.5

    colonel "Sit down, JB."

    "You sit. Not because he told you to. Because your legs are tired and this is going to take a while."

    colonel "You damaged a department vehicle. Then you attempted to conceal the damage. Is that correct?"

    jb "'It's a scratch, Colonel.'"

    colonel "It's a scratch on the Commandant's vehicle that you tried to cover with spit and your sleeve. In front of a witness."

    "He slides a piece of paper across the desk."
    "Full repair cost. 5,000 CZK. Out of your pocket. No insurance, because you failed to report it."

    colonel "Sign it."

    show jb determined at char_left

    "You look at the paper. You look at him."
    "5,000 CZK for a scratch you could polish out with a rag and ten minutes."
    "But that's not what this is about. This is about a man who drove 45 minutes to remind you who's in charge."

    "You pick up the pen."

    menu:
        "SIGN IT — Not worth the fight. Not today.":
            jump car_incident_patch_submit

        "CALL PAUL GOODMAN — 'Actually, Colonel, I think I'd like to speak to a lawyer first.'":
            jump car_incident_patch_paul

    ## --- Patch: Submit ---

label car_incident_patch_submit:

    show jb neutral at char_left

    "You sign the paper."
    "The Colonel takes it without looking at it. He was always going to get the signature."
    "This was never a negotiation. It was a demonstration."

    colonel "You can go."

    "You stand up. You walk to the door."

    colonel "JB."

    "You stop."

    colonel "Next time, just tell the truth. I would have respected that."

    "You don't turn around. You know exactly what his face looks like."
    "The face of a man who thinks he just taught you something."

    python:
        stats.colonel_attitude = "disgusted"
        stats.increment_stats_pcr_hatred(15)
        stats.increment_stats_value_money(-5000)

    show screen outcome_panel("-5,000 CZK (full repair), +15 PCR HATRED (45 minutes of driving for a power play).")
    pause
    hide screen outcome_panel

    "The scratch on the Superb will be fixed by Thursday."
    "The memory of a grown man driving 45 minutes to make you feel small will last longer."

    jump car_incident_end

    ## --- Patch: Paul Goodman ---

label car_incident_patch_paul:

    python:
        unlock_achievement("paul_fan")

    show jb determined at char_left

    jb "'Actually, Colonel — I think I'd like to speak to a lawyer first.'"

    "The room temperature drops three degrees."

    show colonel angry at char_right

    colonel "A lawyer. For a parking lot scratch."

    jb "'For a 5,000 CZK charge with no insurance assessment, no independent damage report, and no formal disciplinary hearing. Yeah. A lawyer.'"

    "You pull out your phone. You have Paul Goodman's number saved under 'Nuclear Option.'"
    "You call. He answers on the first ring."

    "'Did you say police department? Disproportionate penalty? Say no more.'"
    "'I'll take it pro bono. Tell the Colonel I said hello.'"

    "You put the phone on speaker. You set it on the desk between you and the Colonel."
    "Paul Goodman's voice fills the room like cheap cologne — aggressive, persistent, impossible to ignore."

    "The Colonel stares at the phone. Then at you. Then at the phone again."
    "You can see the calculation behind his eyes. Is this worth the paperwork? The scrutiny? The attention from upstairs?"

    show colonel disappointed at char_right

    colonel "...Forget the 5,000."

    "He tears the paper in half. Slowly. Making sure you watch."

    colonel "But understand something, JB. I drove here for {i}you{/i}. Because I thought you were worth the trip."

    "He stands up. He buttons his jacket."

    colonel "Don't make me reconsider."

    "He leaves. The room smells like his aftershave for the rest of the afternoon."
    "You sit there for a long time, holding your phone."
    "Paul Goodman is still on the line. 'So... we good? That was quick.'"

    python:
        stats.colonel_attitude = "disgusted"
        stats.increment_stats_pcr_hatred(5)

    show screen outcome_panel("0 CZK (Paul Goodman earned his reputation), +5 PCR HATRED (you won, so why does it feel like a warning?).")
    pause
    hide screen outcome_panel

    "You didn't pay a cent. But the look on the Colonel's face when he left —"
    "That's going on your tab. And he doesn't forget tabs."

    jump car_incident_end


## ---------------------------------------------------------------------------
## PATH C: WALK AWAY (the gamble — three outcomes)
## Camera (35%): Colonel arrives Day 1, video plays
## Slow burn (40%): No Colonel, paranoia
## Ghost clean (25%): Nothing happens
## ---------------------------------------------------------------------------

label car_incident_ghost:

    scene bg_parking_lot
    show jb worried at char_left

    "You look left. You look right."
    "The parking lot is empty. The cameras — you glance up — the nearest one is mounted on the east wall, pointed at the gate."
    "Maybe it covers this spot. Maybe it doesn't. You've never thought about camera angles before."
    "You are thinking about them now."

    "You straighten up. You brush off your pants."
    "You walk inside like a man who has absolutely nothing to hide."
    "Your face is a mask. Your armpits are a crime scene."

    show jb neutral at char_left

    "The shift supervisor nods at you. 'Morning, JB.'"
    "'Morning,' you say. Your voice sounds normal. You are astonished by this."

    "You sit down at your desk. You do not look out the window at the parking lot."
    "You absolutely do not think about the Commandant's Superb."
    "You think about it every four seconds for the next three hours."

    python:
        _ghost_roll = __import__('random').randint(1, 100)

    if _ghost_roll <= 35:
        jump car_incident_ghost_camera
    elif _ghost_roll <= 75:
        jump car_incident_ghost_slow_burn
    else:
        jump car_incident_ghost_clean


## --- GHOST OUTCOME 1: Camera catches you (35%) — Colonel arrives, video plays ---

label car_incident_ghost_camera:

    scene bg_police_interior
    show jb neutral at char_left

    "14:00. You're halfway through a shift report when the Commandant's door opens."

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
    "The parking lot camera. 06:45 AM. High angle, wide shot."
    "You watch yourself reverse into the Superb. You watch yourself get out, inspect the damage, and walk back inside."
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

    menu:
        "SIGN IT — Pick your battles. This isn't one of them.":
            jump car_incident_ghost_camera_submit

        "CALL PAUL GOODMAN — 'Disciplinary processing fee? That's not a real thing, Colonel.'":
            jump car_incident_ghost_camera_paul


label car_incident_ghost_camera_submit:

    show jb neutral at char_left

    "You sign. It's not surrender. It's resource management."
    "This man drove 45 minutes to charge you a made-up fee for a parking lot scratch."
    "That tells you everything you need to know about where you work."

    colonel "You can go."

    "You walk out. The Commandant won't look at you."
    "Not because he's angry. Because he's embarrassed — for both of you."

    python:
        stats.colonel_attitude = "hostile"
        stats.increment_stats_pcr_hatred(20)
        stats.increment_stats_value_money(-7000)

    show screen outcome_panel("-7,000 CZK (repair + invented fee), +20 PCR HATRED (the system working exactly as designed).")
    pause
    hide screen outcome_panel

    "7,000 CZK for a scratch and a man's ego."
    "Somewhere in this building there are actual criminals. None of them got this much attention today."

    jump car_incident_end


label car_incident_ghost_camera_paul:

    python:
        unlock_achievement("paul_fan")

    show jb determined at char_left

    jb "'Disciplinary processing fee.' That's not in any regulation I've seen, Colonel.'"

    colonel "Excuse me?"

    jb "'And I've read them. All of them. I had a lot of free time during night shifts.'"

    "You pull out your phone."

    jb "'I'm going to call my lawyer. His name is Paul Goodman. He specializes in exactly this kind of thing.'"

    show colonel angry at char_right

    colonel "You're calling a lawyer. Over a parking lot incident."

    jb "'I'm calling a lawyer over a made-up fee, a two-hour interrogation, and a 45-minute drive to intimidate a subordinate. His words, not mine. I texted him while you were parking.'"

    "Silence. The Commandant shifts his weight in the corner. He suddenly finds the ceiling very interesting."

    "The Colonel looks at your phone. He looks at your face."
    "He's doing the math. A lawyer means paperwork. Paperwork means oversight. Oversight means questions he doesn't want answered."

    show colonel disappointed at char_right

    colonel "...Drop the processing fee. Full repair cost only. 5,000."

    "He tears the original bill. Writes a new number."

    colonel "And JB — don't ever pull a stunt like this again. The walking away part. Or the lawyer part."

    "He leaves. The Commandant exhales for what seems like the first time in an hour."

    python:
        stats.colonel_attitude = "hostile"
        stats.increment_stats_pcr_hatred(12)
        stats.increment_stats_value_money(-5000)

    show screen outcome_panel("-5,000 CZK (repair only — Paul Goodman killed the fake fee), +12 PCR HATRED (you fought back, but he'll remember that).")
    pause
    hide screen outcome_panel

    "You saved 2,000 CZK and gained an enemy who outranks you by four pay grades."
    "Fair trade."

    jump car_incident_end


## --- GHOST OUTCOME 2: Slow burn — colleague gossip (40%) — no Colonel ---

label car_incident_ghost_slow_burn:

    scene bg_police_interior
    show jb neutral at char_left

    "The rest of the shift passes without incident."
    "Nobody walks up to your desk with a USB stick. Nobody calls you into an office."
    "The Commandant leaves at 16:00. He doesn't look at the parking lot."

    "You start to breathe again. Slowly."

    show jb determined at char_left

    "But you know how this place works."
    "Nothing stays secret in a police station. Secrets are currency here, and somebody always needs to make a deposit."

    "You glance out the window one more time before you leave."
    "The Superb is still sitting there. The scratch is still visible if you know where to look."
    "Someone will look. Eventually."

    python:
        stats.colonel_attitude = "cold"
        stats.increment_stats_pcr_hatred(10)

    show screen outcome_panel("+10 PCR HATRED (the scratch is still there — and so is the question of who's going to notice).")
    pause
    hide screen outcome_panel

    "You drive home in silence. No radio. No music."
    "Just you and the knowledge that you left something unfinished in that parking lot."

    jump car_incident_end


## --- GHOST OUTCOME 3: Ghost clean — rain washes evidence (25%) — no Colonel ---

label car_incident_ghost_clean:

    scene bg_parking_lot
    show jb neutral at char_left

    "It rains that afternoon."
    "Not a drizzle. A proper Bohemian downpour, the kind that turns parking lots into lakes and washes away the evidence of small crimes."

    "You watch it from the break room window."
    "The transfer paint dissolves. The gravel shifts. The white mark on the Superb fades into the general wear of a car that lives in a police parking lot."

    show jb determined at char_left

    "By end of shift, the scratch looks like it could have been there for months."
    "Nobody says anything. Nobody looks at you."

    "You walk to your car. You sit behind the wheel. Engine off."
    "You stare at the empty parking spot where the Superb was."

    "You got away with it."

    python:
        unlock_achievement("ghost_walker")
        stats.colonel_attitude = "unaware"

    show screen outcome_panel("0 CZK, 0 HATRED. The rain handled it. Sometimes the universe picks your side.")
    pause
    hide screen outcome_panel

    "You start the engine. You drive home."
    "The windshield wipers beat back and forth. The rain keeps coming."
    "You don't feel relieved. You feel something quieter. Something you'll think about later."

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
