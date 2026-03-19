################################################################################
## REFACTOR - Arc 1.5: The Midnight Call (Day 15)
## A phone call from the Colonel at 2AM that escalates in 6 phases
################################################################################

## ---------------------------------------------------------------------------
## COLONEL VOICE — used only during the phone call (we don't see him)
## ---------------------------------------------------------------------------

define colonel_voice = Character("Colonel (Phone)", color="#4a7aaa", what_color="#8aa8c8", substitute=False)


label midnight_call:

    stop music fadeout 1.0

    ## Play the midnight call cinematic
    $ renpy.movie_cutscene("video/midnight_call.webm")

    play music "audio/tension_theme.mp3" fadein 1.5

    call screen arc_title_card("INTERLUDE", "THE MIDNIGHT CALL") with arc_fade

    scene bg_black with fade
    show jb worried at char_center

    "02:17 AM."
    "You are asleep. Or trying to be."
    "Your phone buzzes."

    pause 0.5

    "You look at the screen."
    "COLONEL."
    "At 2 AM."

    "You stare at the name for three full seconds."
    "It's still ringing."

    menu:
        "ANSWER — 'This can't be good.'":
            jump midnight_answer

        "IGNORE — Let it ring out. He's your boss but it's 2AM.":
            jump midnight_ignore


label midnight_ignore:

    "You put the phone face-down."
    "It rings out."
    "Then immediately rings again."
    "Three times."

    "On the fourth call, something in your stomach says {i}this is different{/i}."

    jb "'What the hell...'"
    jump midnight_answer


label midnight_answer:

    "You answer."

    colonel_voice "'JB. You are awake.'"

    "It's not a question."

    jb "'I am now.'"

    colonel_voice "'Good. We need to talk.'"
    colonel_voice "'Not tomorrow. Now.'"

    "There is background noise. You hear traffic. He's outside, somewhere."
    "That's strange. He's always at home by 9."

    call midnight_phase1
    call midnight_phase2
    call midnight_phase3
    call midnight_phase4
    call midnight_phase5
    call midnight_phase6

    return


## ---------------------------------------------------------------------------
## Phase 1: The Setup
## ---------------------------------------------------------------------------

label midnight_phase1:

    colonel_voice "'I know about the resignation letter, JB.'"

    "Your blood turns to ice."

    jb "'I... haven't submitted anything—'"

    colonel_voice "'You've been drafting it. You left it in your sent items. Your department account.'"
    colonel_voice "'We have monitoring protocols. You should have known that.'"

    "Silence."

    "He let that sit for exactly the right amount of time."

    menu:
        "DENY — 'That was a personal letter. Not an official submission.'":
            python:
                stats.increment_stats_pcr_hatred(10)

            colonel_voice "'JB. I've been doing this for 32 years.'"
            colonel_voice "'Don't insult either of us.'"
            "You say nothing."
            show screen outcome_panel("+10 PCR HATRED (You denied it. He saw through it. Obviously).")
            pause
            hide screen outcome_panel

        "ADMIT — 'Yes. I've been thinking about it.'":
            python:
                stats.increment_stats_pcr_hatred(-5)

            jb "'Yes. I've been thinking about leaving.'"
            "A long pause."
            colonel_voice "'Finally. Honest.'"
            colonel_voice "'See, I can work with honest, JB.'"
            show screen outcome_panel("-5 PCR HATRED (Dignity in admitting it).")
            pause
            hide screen outcome_panel

        "SILENCE — Say nothing. Wait him out.":
            python:
                stats.increment_stats_pcr_hatred(5)

            "You don't answer."
            "He doesn't push."
            "Five seconds. Ten seconds. Fifteen."
            colonel_voice "'I'll take that as a yes.'"
            show screen outcome_panel("+5 PCR HATRED (Silence is still an answer).")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## Phase 2: The Offer
## ---------------------------------------------------------------------------

label midnight_phase2:

    colonel_voice "'I'm not calling to punish you, JB.'"
    colonel_voice "'I'm calling because... I need to understand.'"

    "That's unexpected."
    "He sounds almost human."

    colonel_voice "'I invested in you. From the beginning. You were the best candidate from your class.'"
    colonel_voice "'I trained you personally. I broke rules for you, once.'"
    colonel_voice "'You know what I'm referring to.'"

    "The car incident."
    "He knows you haven't forgotten."

    colonel_voice "'I want to offer you something before you make a decision you can't take back.'"

    menu:
        "LISTEN — 'What kind of offer?'":
            python:
                pass  ## Listening here is neutral — just getting info

            colonel_voice "'Deputy Chief of Department B. Starting in six months. Salary increase of 40%%. And I bury the resignation draft.'"
            colonel_voice "'Nobody ever knows this conversation happened.'"
            "You swallow."
            show screen outcome_panel("Colonel offers promotion. LISTEN FURTHER to understand the full price.")
            pause
            hide screen outcome_panel

        "SHUT IT DOWN — 'Colonel, no promotion will change this.'":
            python:
                stats.increment_stats_pcr_hatred(-10)
                stats.increment_stats_value_money(-0)

            colonel_voice "'...you haven't heard the full offer.'"
            jb "'I don't need to. My decision isn't about pay grade.'"
            colonel_voice "'Then what is it about.'"
            jb "'It's about who I want to be.'"
            "Long pause."
            colonel_voice "'...I see.'"
            show screen outcome_panel("-10 PCR HATRED (You held your line. That matters).")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## Phase 3: The Real Question
## ---------------------------------------------------------------------------

label midnight_phase3:

    colonel_voice "'Can I ask you something personal, JB? Off the record.'"

    "You don't trust 'off the record' from this man."
    "But something in his voice tonight is different. Less script. More person."

    jb "'Ask.'"

    colonel_voice "'Is it me?'"

    "A beat."

    colonel_voice "'I've been... difficult. I know that. My methods.'"
    colonel_voice "'Is this because of how I treated you?'"

    menu:
        "YES — 'Partly. The way you run this station is toxic.'" :
            python:
                stats.increment_stats_pcr_hatred(15)

            jb "'Yes, Colonel. You're part of it.'"
            jb "'The system is broken. But you're not trying to fix it. You're protecting it.'"
            "Silence."
            colonel_voice "'...that's fair.'"
            colonel_voice "'That is a fair thing to say.'"
            "You weren't expecting that."
            show screen outcome_panel("+15 PCR HATRED (The truth has a cost. Say it anyway).")
            pause
            hide screen outcome_panel

        "NO — 'This isn't about you, Colonel. It's bigger than that.'":
            python:
                stats.increment_stats_pcr_hatred(-15)

            jb "'It's not personal. It's structural.'"
            jb "'The institution doesn't fit who I'm becoming. That's not your fault.'"
            "Another pause. Longer this time."
            colonel_voice "'That's... a generous answer.'"
            "He sounds, for exactly one second, genuinely touched."
            show screen outcome_panel("-15 PCR HATRED (Clarity without cruelty).")
            pause
            hide screen outcome_panel

        "COMPLICATED ANSWER — 'It's both. And neither. And more than that.'":
            python:
                stats.increment_stats_pcr_hatred(-5)
                stats.increment_stats_coding_skill(2)

            jb "'You asked a simple question but the answer isn't simple, Colonel.'"
            jb "'I've been changing. Maybe you haven't. And that gap — that's the problem.'"
            colonel_voice "'...Go on.'"
            "You actually talk. For three minutes. Real talk."
            "He listens. He doesn't interrupt."
            "You feel heard for the first time in years."
            "It's the strangest thing."
            show screen outcome_panel("-5 PCR HATRED, +2 CODING SKILL (Articulating your thoughts is its own kind of skill).")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## Phase 4: The Threat (real Colonel re-emerging)
## ---------------------------------------------------------------------------

label midnight_phase4:

    "The brief warmth in his voice is gone."
    colonel_voice "'Regardless of your reasons — I need you to understand the practical reality.'"

    colonel_voice "'If you submit that letter formally, I am required to initiate a review.'"
    colonel_voice "'Your conduct over the past year. The car incident. The unauthorized moonlighting.'"
    colonel_voice "'There are things in your file, JB. Things I never escalated.'"
    colonel_voice "'Out of {i}loyalty{/i}. Out of my investment in you.'"

    "There it is."
    "The warmth was a setup."

    menu:
        "CALL IT OUT — 'So this is a threat.'":
            python:
                stats.increment_stats_pcr_hatred(-10)
                store._midnight_colonel_weakened = True

            jb "'Let me make sure I understand. You called me at 2AM to threaten me.'"
            colonel_voice "'I called you to give you an {i}opportunity{/i} to think clearly.'"
            jb "'You called me to intimidate me. At 2AM.'"
            "The distinction is doing a lot of work."
            "But you named it. And that changes the power dynamic permanently."
            show screen outcome_panel("-10 PCR HATRED (You named the manipulation. That's not nothing). [[MIDNIGHT_LEVERAGE ACQUIRED]]")
            pause
            hide screen outcome_panel

        "ABSORB IT — Sit with it. Don't react emotionally.":
            python:
                stats.increment_stats_pcr_hatred(5)

            "You say nothing. You breathe."
            "He's waiting for a reaction. Fear. Anger. Capitulation."
            "You give him nothing."
            colonel_voice "'JB.'"
            "Nothing."
            colonel_voice "'...JB, are you still there?'"
            jb "'I'm here, Colonel. I'm just thinking.'"
            show screen outcome_panel("+5 PCR HATRED (Absorbing threats costs you. But denying reactions takes practice).")
            pause
            hide screen outcome_panel

        "COUNTER — 'I have my own file on this station, Colonel.'" if stats.coding_skill >= 40:
            python:
                stats.increment_stats_pcr_hatred(-20)
                store._midnight_colonel_weakened = True

            jb "'Colonel, I have been taking notes for six months.'"
            jb "'The double shifts. The undocumented policy changes. The overtime violations.'"
            jb "'I've been building my case, too. I just never needed to use it.'"
            "A very long pause."
            colonel_voice "'...I see.'"
            colonel_voice "'Well. This is an interesting development.'"
            show screen outcome_panel("-20 PCR HATRED (Mutual assured documentation). [[MIDNIGHT_LEVERAGE ACQUIRED]]")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## Phase 5: The Silence / Turning Point
## ---------------------------------------------------------------------------

label midnight_phase5:

    "The call goes quiet for almost 30 seconds."
    "You don't break the silence."
    "You've learned: the first person to speak loses."

    colonel_voice "'JB.'"

    jb "'Yeah.'"

    colonel_voice "'Do you know how long I've been doing this job?'"

    jb "'32 years.'"

    colonel_voice "'33 next April.'"

    "Pause."

    colonel_voice "'I haven't taken a vacation in 6 years. My kids call me 'the Officer' sometimes. As a joke.'"
    colonel_voice "'It's not a joke anymore. I think they genuinely don't know what to call me.'"

    "You don't know what to do with this information."
    "You didn't ask for it."
    "But here it is."

    menu:
        "ACKNOWLEDGE — 'That sounds lonely, Colonel.'":
            python:
                stats.increment_stats_pcr_hatred(-20)

            "You say it quietly. No sarcasm. No agenda."
            colonel_voice "'...Yes. It is.'"
            "Another silence. Longer."
            colonel_voice "'Go back to sleep, JB.'"
            "The line goes dead."
            "You stare at the phone."
            "Something shifted tonight. You can't explain it. But something shifted."
            show screen outcome_panel("-20 PCR HATRED (You saw him as a person. That costs something too).")
            pause
            hide screen outcome_panel

        "REDIRECT — 'With respect, Colonel, this isn't why you called.'":
            python:
                stats.increment_stats_pcr_hatred(5)

            jb "'I hear you. But this isn't about your career. It's about mine.'"
            colonel_voice "'...You're right. I lost track.'"
            colonel_voice "'I... apologize for calling at this hour.'"
            "You have never heard him apologize before."
            "Not once. Not ever."
            "You aren't sure what to say."
            show screen outcome_panel("+5 PCR HATRED (But he apologized. Write that down. It won't happen again).")
            pause
            hide screen outcome_panel

    return


## ---------------------------------------------------------------------------
## Phase 6: The Ending of the Call
## ---------------------------------------------------------------------------

label midnight_phase6:

    colonel_voice "'Think about it tonight. Sleep on it. Call me before you file anything officially.'"

    python:
        _weakened = getattr(store, '_midnight_colonel_weakened', False)

    menu:
        "AGREE TO THINK — 'I'll consider it, Colonel.'":
            python:
                stats.increment_stats_pcr_hatred(10)

            colonel_voice "'Good.'"
            "He hangs up."
            "You sit in the dark for a while."
            "You consider it. You already know the answer."
            "But agreeing to think cost you more than it was worth."
            show screen outcome_panel("+10 PCR HATRED (You gave ground you didn't need to give).")
            pause
            hide screen outcome_panel

        "DECLINE DIRECTLY — 'I've already thought about it. The letter stands.'":
            python:
                stats.increment_stats_pcr_hatred(-15)

            jb "'I've thought about nothing else for six months, Colonel.'"
            jb "'The answer is yes. I'm leaving.'"
            "Silence."
            colonel_voice "'Then I'll see you at the end of the month.'"
            "Click."
            "You put the phone down."
            "It's 02:54 AM."
            "You won't sleep tonight. But you don't feel tired."
            show screen outcome_panel("-15 PCR HATRED (Said it out loud. To HIM. That is a different kind of clarity).")
            pause
            hide screen outcome_panel

        "[[LEVERAGE]] 'I'll file through my lawyer. We'll make sure everything's documented.' [[+COMBAT ADVANTAGE]]" if _weakened:
            python:
                stats.increment_stats_pcr_hatred(-25)
                stats.final_boss_buff = "STOIC_ANCHOR"

            jb "'Actually, Colonel — I'll be filing through legal counsel.'"
            jb "'Everything I have is documented. I hope yours is too.'"
            colonel_voice "'...'"
            "He hangs up."
            "Immediately."
            "That's as close to 'you win' as he'll ever say."
            show screen outcome_panel("-25 PCR HATRED. [[MIDNIGHT LEVERAGE ACTIVATED]] STOIC_ANCHOR buff applied for final battle!")
            pause 2.5
            hide screen outcome_panel

    "03:00 AM."
    "The room is very quiet."
    "You open your laptop."
    "You code until sunrise."
    python:
        unlock_achievement("dark_night")

    python:
        stats.increment_stats_coding_skill(5)

    show screen outcome_panel("+5 CODING SKILL (Midnight clarity session).")
    pause
    hide screen outcome_panel

    return
