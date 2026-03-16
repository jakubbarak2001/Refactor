################################################################################
## REFACTOR - Arc III: The Colonel Event (Final Boss)
## Ported verbatim from colonel_event.py
## HP tracked as Python variables: jb_hp, colonel_hp
################################################################################

default jb_hp       = 100
default colonel_hp  = 100

label colonel_event:

    $ jb_hp      = 100
    $ colonel_hp = 100

    play music "audio/tension_theme.mp3" fadein 1.0

    call screen arc_title_card("III", "THE RECKONING") with arc_fade

    ## Initialization — apply pre-fight buffs/debuffs
    python:
        if stats.final_boss_buff == "LEGAL_NUKE":
            colonel_hp -= 35
            renpy.say(None, "[[PASSIVE]]: 'Legal Nuke' applied. Colonel starts with -35 HP.")
        elif stats.final_boss_buff == "FIRST_STRIKE":
            colonel_hp -= 20
            renpy.say(None, "[[PASSIVE]]: 'Aggressive Opening' applied. Colonel starts with -20 HP.")
        elif stats.final_boss_buff == "IMPOSTER_SYNDROME":
            renpy.say(None, "[[WARNING]]: You have Imposter Syndrome. You are vulnerable.")

    ## Biohacker — nootropic state at fight start
    python:
        _bh_withdrawal = (stats.player_class == "biohacker" and nootropic_dependency and nootropic_last_tier == 0)
        _bh_flmod      = (stats.player_class == "biohacker" and nootropic_last_tier == 5)
        store._bh_flmod = _bh_flmod

        if _bh_withdrawal:
            jb_hp -= 15
            renpy.say(None, "[[WITHDRAWAL — BIOHACKER]]: Your body is screaming for the compound.")
            renpy.say(None, "Tremors. Shallow breath. You walk in already compromised.")
            renpy.say(None, "JB starts with -15 HP.")
        elif _bh_flmod:
            jb_hp += 15
            renpy.say(None, "[[FLModafinil (CRL-40,940) — BIOHACKER]]: Peak cognitive state. Dopamine locked. Every micro-expression readable.")
            renpy.say(None, "JB starts with +15 HP from compound advantage.")

    ## Round 1
    call colonel_round_one

    ## Round 2
    call colonel_round_two

    ## Rounds 3-9: 7 shuffled attacks
    call colonel_round_three_logic

    return


## ---------------------------------------------------------------------------
## ROUND 1 — The Waiting
## ---------------------------------------------------------------------------

label colonel_round_one:

    scene bg_police_hallway with glitch_transition

    "BOSS COMBAT — Round 1 | JB: [jb_hp] HP | Colonel: [colonel_hp] HP"

    "It is early morning. You hand your superior the resignation."
    "'I need to call the Colonel.'"
    "Three hours later, the black Superb arrives. He sits inside for 5 minutes."

    python:
        good_buffs = [["STOIC_ANCHOR", "LEGAL_NUKE", "GHOST_SECRET", "JOB_OFFER", "STOIC_HEAL", "FIRST_STRIKE"]]
        if stats.final_boss_buff in good_buffs:
            renpy.say(None, "[[DEFENSE]]: You remember Martin's advice. You stay calm. (0 DMG)")
        else:
            jb_hp -= 10
            renpy.say(None, "[[ANXIETY HIT]]: The waiting is torture. (-10 HP)")

    return


## ---------------------------------------------------------------------------
## ROUND 2 — His Entrance
## ---------------------------------------------------------------------------

label colonel_round_two:

    scene bg_police_office with glitch_transition
    show colonel normal at char_right

    "BOSS COMBAT — Round 2 | JB: [jb_hp] HP | Colonel: [colonel_hp] HP"

    "He enters. The room goes silent. Your colleagues look down."

    python:
        if stats.final_boss_buff == "IMPOSTER_SYNDROME":
            jb_hp -= 10
            renpy.say(None, "[[DEBUFF]]: You feel like a fraud. (-10 HP)")
        else:
            renpy.say(None, "[[STOIC]]: You hold his gaze.")

    return


## ---------------------------------------------------------------------------
## ROUND 3+ LOGIC — 7 shuffled attacks
## ---------------------------------------------------------------------------

label colonel_round_three_logic:

    play music "audio/colonel_arrives.mp3" fadein 1.0

    scene bg_police_office with glitch_transition
    show colonel normal at char_right

    "He invites you upstairs. He makes coffee. The silence is heavy."
    colonel "'Black? Two sugars?' he asks."
    "Then, he attacks."

    ## We track which attacks remain using a store list
    python:
        store._colonel_attacks = [
            "colonel_attack_money",
            "colonel_attack_why_quit",
            "colonel_attack_civilian_void",
            "colonel_attack_brotherhood",
            "colonel_attack_safety_net",
            "colonel_attack_debt_of_honor",
            "colonel_attack_blacklist",
        ]
        __import__('random').shuffle(store._colonel_attacks)
        store._colonel_round = 3

    jump colonel_next_attack


label colonel_next_attack:

    python:
        if jb_hp <= 0:
            renpy.jump("colonel_defeat_ending")
        if colonel_hp <= 0:
            renpy.jump("colonel_glitch_phase")
        if not store._colonel_attacks:
            renpy.jump("colonel_check_stalemate")

    python:
        _next_atk = store._colonel_attacks.pop(0)
        store._colonel_round += 1
        _rnd = store._colonel_round

    show screen hp_bar_panel(jb_hp, colonel_hp, "Round {}".format(_rnd))
    pause 2.0
    hide screen hp_bar_panel

    python:
        renpy.call(_next_atk)

    jump colonel_next_attack


## ---------------------------------------------------------------------------
## ATTACK 1: Training Debt
## ---------------------------------------------------------------------------

label colonel_attack_money:

    show colonel angry at char_right

    colonel "'You know you have to return the money for your training, JB?'"

    python:
        if stats.final_boss_buff == "LEGAL_NUKE":
            renpy.say(None, "[[AUTO-COUNTER]]: You slap the file Martin gave you on the table.")
            renpy.say(jb, "'Paragraph 4B, Colonel. The debt is void.'")
            renpy.say(None, "The Colonel chokes on his coffee. He is furious.")
            colonel_hp -= 15
            renpy.say(None, "[[CRITICAL]]: Colonel takes -15 HP DMG!")
        elif stats.available_money < 200000:
            renpy.say(None, "[[PANIC]]: You don't have enough to feel safe (Need >200k).")

    python:
        if stats.final_boss_buff == "LEGAL_NUKE":
            renpy.jump("colonel_attack_money_done")

    colonel "He smiles coldly. '80,000 CZK. Immediately. Or I call the lawyers.'"
    "Your Savings: [stats.available_money] CZK"

    python:
        if stats.available_money < 200000:
            renpy.call("colonel_money_poor")
        else:
            renpy.call("colonel_money_rich")

label colonel_attack_money_done:

    return


label colonel_money_poor:
    menu:
        "[[STAMMER]] 'I... I will pay you later.'":
            python:
                jb_hp -= 10
            "[[FAILURE]]: He sees your fear. You take -10 HP DMG."
    return


label colonel_money_rich:
    menu:
        "[[PAY 80k]] 'Here. Keep the change.' (Deals 20 HP DMG)":
            python:
                stats.increment_stats_value_money(-80000)
                colonel_hp -= 20
            "[[DOMINANCE]]: You throw the money on the table. He is shocked."
            "Colonel takes -20 HP DMG."

        "[[SHOW BALANCE]] 'I have enough to bury you in court.' (Deals 10 HP DMG, save money)":
            python:
                colonel_hp -= 10
            "[[STOIC]]: You show him your account app. He realizes he can't threaten you."
            "Colonel takes -10 HP DMG."
    return


## ---------------------------------------------------------------------------
## ATTACK 2: Why Quit (Motivation Check)
## ---------------------------------------------------------------------------

label colonel_attack_why_quit:

    show colonel angry at char_right

    colonel "'Why, JB? After everything I did for you. Why are you quitting?'"

    python:
        _chance_hatred = int(stats.pcr_hatred * 0.5)
        _chance_coding = int(stats.coding_skill / 2)
        _chance_money  = int(stats.available_money / 3000)

    "Your answer will be tested against your stats."
    "HATRED chance: [_chance_hatred]%% | CODING chance: [_chance_coding]%% | MONEY chance: [_chance_money]%%"

    python:
        _has_job_offer  = (stats.final_boss_buff == "JOB_OFFER")
        _flmod_now      = getattr(store, '_bh_flmod', False)

    python:
        _de_mod = 2 if stats.player_class == "dark_empath" else 1  ## Dark Empath halves failure damage

    menu:
        "[[CRL-40,940]] 'Because I finally see things as they are.' (25 DMG, costs 10 HP)  [BIOHACKER]" if _flmod_now:
            python:
                colonel_hp -= 25
                jb_hp      -= 10
            "Your pupils are slightly dilated. Your voice is dead calm."
            jb "'You built this system to make men like me afraid to leave. I am not afraid anymore.'"
            jb "'I modelled the probability. The only losing move is staying.'"
            "He opens his mouth. He closes it."
            "For the first time in 30 years, the Colonel has nothing to say."
            "[[BIOHACKER — COMPOUND CLARITY]]: Colonel takes -25 HP DMG. You burn 10 HP maintaining the peak state."

        "[[HATRED]] 'I had enough of this sh*t.' (Success Chance: [_chance_hatred]%%)":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= _chance_hatred:
                    _bonus = max(0, _chance_hatred - 100)
                    _dmg = 20 + _bonus
                    colonel_hp -= _dmg
                    renpy.say(None, "[[SUCCESS]]: Your Pure Rage hits him hard! {} DMG!".format(_dmg))
                else:
                    _fail_dmg = 20 // _de_mod
                    jb_hp -= _fail_dmg
                    renpy.say(None, "[[FAILURE]]: Your voice cracks. He smells weakness. You take -{} HP DMG.{}".format(_fail_dmg, " [DARK EMPATH: halved]" if _de_mod == 2 else ""))

        "[[CODING]] 'I build worlds now. I don't need this.' (Success Chance: [_chance_coding]%%)":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= _chance_coding:
                    _bonus = max(0, _chance_coding - 100)
                    _dmg = 20 + _bonus
                    colonel_hp -= _dmg
                    renpy.say(None, "[[SUCCESS]]: Your Logic Bomb hits hard! {} DMG!".format(_dmg))
                else:
                    _fail_dmg = 20 // _de_mod
                    jb_hp -= _fail_dmg
                    renpy.say(None, "[[FAILURE]]: Your voice cracks. You take -{} HP DMG.{}".format(_fail_dmg, " [DARK EMPATH: halved]" if _de_mod == 2 else ""))

        "[[MONEY]] 'I can buy my own freedom.' (Success Chance: [_chance_money]%%)":
            python:
                _roll = __import__('random').randint(1, 100)
                if _roll <= _chance_money:
                    _bonus = max(0, _chance_money - 100)
                    _dmg = 20 + _bonus
                    colonel_hp -= _dmg
                    renpy.say(None, "[[SUCCESS]]: Financial Shield! {} DMG!".format(_dmg))
                else:
                    _fail_dmg = 20 // _de_mod
                    jb_hp -= _fail_dmg
                    renpy.say(None, "[[FAILURE]]: You bluff, he doesn't believe it. You take -{} HP DMG.{}".format(_fail_dmg, " [DARK EMPATH: halved]" if _de_mod == 2 else ""))

        "[[MM OFFER]] 'Martin has a job waiting for me.' (Guaranteed 20 DMG)" if _has_job_offer:
            python:
                colonel_hp -= 20
            "[[PERK]]: You mention the job offer. His control over you vanishes."
            "Colonel takes -20 HP DMG."

    return


## ---------------------------------------------------------------------------
## ATTACK 3: Civilian Void (Fear of Irrelevance)
## ---------------------------------------------------------------------------

label colonel_attack_civilian_void:

    show colonel angry at char_right

    colonel "'You think you can survive out there? Without the badge, you are nobody.'"
    colonel "'Here, people fear you. Respect you. Out there? You are just another civilian waiting in line.'"

    python:
        _de_half = 2 if stats.player_class == "dark_empath" else 1
        _de_fs   = (stats.player_class == "dark_empath")

    menu:
        "[[CODING]] 'I don't need their fear. I have skills that build the future.'":
            python:
                if stats.coding_skill >= 100:
                    colonel_hp -= 20
                    renpy.say(jb, "'I write the logic that runs your world.' He looks confused.")
                    renpy.say(None, "Colonel takes -20 HP DMG.")
                else:
                    _fail = 15 // _de_half
                    jb_hp -= _fail
                    renpy.say(None, "[[FAILURE]]: You stutter. You aren't good enough at coding yet to believe it.")
                    renpy.say(None, "You take -{} HP DMG.{}".format(_fail, " [DARK EMPATH: halved]" if _de_half == 2 else ""))

        "[[HATRED]] 'I'd rather be a nobody than a tyrant like you.'":
            python:
                if stats.pcr_hatred >= 60:
                    colonel_hp -= 15
                    renpy.say(None, "[[RAGE]]: Your hatred burns brighter than his rank. He steps back.")
                    renpy.say(None, "Colonel takes -15 HP DMG.")
                else:
                    _fail = 10 // _de_half
                    jb_hp -= _fail
                    renpy.say(None, "[[WEAKNESS]]: You don't sound convinced. You still crave the power.")
                    renpy.say(None, "You take -{} HP DMG.{}".format(_fail, " [DARK EMPATH: halved]" if _de_half == 2 else ""))

        "[[DARK EMPATH]] FATAL STRIKE — 'I see your real fear, Colonel.' (KILLS his argument)" if _de_fs:
            python:
                colonel_hp -= 35
                unlock_achievement("dark_empath_win")
            show colonel disappointed at char_right
            "You look straight through him."
            jb "'You aren't trying to keep me here. You are terrified of what happens to YOU when I leave.'"
            jb "'Who are you when you don't have someone to dominate?'"
            "His face goes white. His mask falls off for exactly 1.5 seconds."
            "Then he picks up his coffee and looks away."
            "[[DARK EMPATH PERK — FATAL STRIKE]]: Colonel takes -35 HP DMG."

        "[[DOUBT]] 'Maybe... maybe I will miss the authority.'":
            python:
                jb_hp -= 20
            "[[SUBMISSION]]: You admit it. He smiles predatorily."
            "You take -20 HP DMG."

    return


## ---------------------------------------------------------------------------
## ATTACK 4: Brotherhood (Guilt Trip)
## ---------------------------------------------------------------------------

label colonel_attack_brotherhood:

    show colonel angry at char_right

    colonel "'And what about your team? Lieutenant? The rookies?'"
    colonel "'You are abandoning them in the trenches. They will rot in overtime because YOU left.'"

    python:
        if stats.final_boss_buff == "STOIC_ANCHOR":
            renpy.say(None, "[[PASSIVE]]: Stoic Anchor active. You realize everyone is responsible for their own life.")
            renpy.say(jb, "'They have the same choice I do, Colonel.'")
            colonel_hp -= 10
            renpy.say(None, "Colonel takes -10 HP DMG.")
        elif stats.player_class == "bodybuilder":
            renpy.say(None, "[[BODYBUILDER PERK]]: Brotherhood guilt bounces off you like a feather off a boulder.")
            renpy.say(jb, "'Bro, I don't even remember most of their names.'")
            renpy.say(None, "The Colonel blinks. He has no follow-up. 0 HP DMG taken.")
            colonel_hp -= 5
        elif stats.final_boss_buff == "STOIC_HEAL":
            renpy.say(None, "[[STOIC REFACTOR]]: You recognize the emotional manipulation. The guilt barely registers.")
            renpy.call("colonel_brotherhood_menu")
            jb_hp += 5  ## STOIC_HEAL refunds 5 HP on emotional attacks
            renpy.say(None, "[[STOIC REFACTOR BONUS]]: Emotional resilience restored +5 HP.")
        else:
            renpy.call("colonel_brotherhood_menu")

    return


label colonel_brotherhood_menu:
    menu:
        "[[COLD]] 'They are colleagues, not family. It's just a job.'":
            python:
                if stats.pcr_hatred >= 50:
                    colonel_hp -= 15
                    renpy.say(jb, "'The system failed them, Colonel. Not me.'")
                    renpy.say(None, "Colonel takes -15 HP DMG.")
                else:
                    jb_hp -= 15
                    renpy.say(None, "[[GUILT]]: You lie. You will miss them. The guilt hits you.")
                    renpy.say(None, "You take -15 HP DMG.")

        "[[EMPATHY]] 'I... I feel bad for them. But I have to save myself.'":
            python:
                jb_hp -= 10
            "[[PAIN]]: It hurts to admit. He sees your hesitation."
            "You take -10 HP DMG."
    return


## ---------------------------------------------------------------------------
## ATTACK 5: Safety Net (Golden Handcuffs)
## ---------------------------------------------------------------------------

label colonel_attack_safety_net:

    show colonel angry at char_right

    colonel "'You are a fool. The pension! The benefits! The stability!'"
    colonel "'You are throwing away a guaranteed future for... what? Coding scripts?'"

    python:
        _is_biohacker = (stats.player_class == "biohacker")

    python:
        if _is_biohacker:
            unlock_achievement("biohacker_win")
            renpy.say(None, "[[BIOHACKER PERK]]: The concept of a 'safety net' is laughable to you.")
            renpy.say(jb, "'I have 500 CZK of passive BTC income daily. I optimized my savings. I hacked my own sleep cycle.'")
            renpy.say(jb, "'I don't need a pension, Colonel. I built mine already.'")
            colonel_hp -= 30
            renpy.say(None, "[[AUTO-COUNTER]]: His golden handcuffs cannot reach you. Colonel takes -30 HP DMG.")
            renpy.jump("colonel_safety_net_done")

    menu:
        "[[MONEY]] 'I have enough savings to be my own pension.'":
            python:
                if stats.available_money >= 150000:
                    colonel_hp -= 25
                    renpy.say(None, "[[WEALTH]]: You mention your savings. His jaw tightens. He can't buy you.")
                    renpy.say(None, "CRITICAL HIT: Colonel takes -25 HP DMG.")
                else:
                    jb_hp -= 15
                    renpy.say(None, "[[POOR]]: You bluff, but you know you'll be broke in 3 months.")
                    renpy.say(None, "You take -15 HP DMG.")

        "[[FREEDOM]] 'I'd rather starve free than eat well in a cage.'":
            python:
                colonel_hp -= 10
            "[[PHILOSOPHY]]: A bit dramatic, but effective. He hates your independence."
            "Colonel takes -10 HP DMG."

label colonel_safety_net_done:

    return


## ---------------------------------------------------------------------------
## ATTACK 6: Debt of Honor (Car Incident)
## ---------------------------------------------------------------------------

label colonel_attack_debt_of_honor:

    show colonel angry at char_right

    colonel "'Have you forgotten the car accident, JB?'"
    colonel "'I buried the internal investigation. I saved your badge. You OWE me.'"

    python:
        if stats.final_boss_buff == "GHOST_SECRET":
            renpy.call("colonel_debt_ghost")
        else:
            renpy.call("colonel_debt_normal")

    return


label colonel_debt_ghost:
    ">> [[OPPORTUNITY]]: USE 'GHOST OF THE PAST' SECRET <<"
    menu:
        "[[BLACKMAIL]] 'Like you buried your resignation 10 years ago?'":
            python:
                colonel_hp -= 40
            "[[DEVASTATION]]: You say it. The room drops to absolute zero."
            "He freezes. His deepest insecurity exposed. He looks old suddenly."
            "FATAL STRIKE: Colonel takes -40 HP DMG."

        "[[DEFENSIVE]] 'I repaid that debt with 3 years of service.'":
            python:
                colonel_hp -= 5
            "[[NEUTRAL]]: He grunts. He knows you worked hard, but he feels cheated."
            "Colonel takes -5 HP DMG."
    return


label colonel_debt_normal:
    menu:
        "[[DEFENSIVE]] 'I repaid that debt with 3 years of flawless service.'":
            python:
                colonel_hp -= 5
            "[[NEUTRAL]]: He grunts. He knows you worked hard, but he feels cheated."
            "Colonel takes -5 HP DMG."

        "[[SUBMIT]] 'I know... and I am grateful. But I have to go.'":
            python:
                jb_hp -= 20
            "[[GUILT]]: The emotional debt weighs you down."
            "You take -20 HP DMG."
    return


## ---------------------------------------------------------------------------
## ATTACK 7: Blacklist Threat
## ---------------------------------------------------------------------------

label colonel_attack_blacklist:

    show colonel angry at char_right

    colonel "'I will make calls. I will ruin you.'"
    colonel "'No security firm. No state agency. You will never work in this town again.'"

    python:
        if stats.final_boss_buff == "JOB_OFFER":
            renpy.say(None, "[[AUTO-COUNTER]]: You smile. 'Martin already hired me, Colonel.'")
            renpy.say(jb, "'Your threats don't work on the private sector.'")
            colonel_hp -= 30
            renpy.say(None, "CRITICAL HIT: Colonel takes -30 HP DMG.")
        else:
            renpy.call("colonel_blacklist_menu")

    return


label colonel_blacklist_menu:
    menu:
        "[[CONFIDENCE]] 'I'm not looking for security work. I'm a Developer.'":
            python:
                if stats.coding_skill >= 50:
                    colonel_hp -= 15
                    renpy.say(None, "[[PIVOT]]: You reject his entire premise. He has no power over IT.")
                    renpy.say(None, "Colonel takes -15 HP DMG.")
                else:
                    jb_hp -= 10
                    renpy.say(None, "[[DOUBT]]: You say it, but you don't fully believe it yourself yet.")
                    renpy.say(None, "You take -10 HP DMG.")

        "[[SCARE]] 'Are you threatening a civilian? Careful, Colonel.'":
            python:
                colonel_hp -= 10
                jb_hp -= 5
            "[[CLASH]]: A verbal spar. He respects the backbone but hates the tone."
            "Both take damage."
    return


## ---------------------------------------------------------------------------
## STALEMATE CHECK
## ---------------------------------------------------------------------------

label colonel_check_stalemate:

    "BOSS COMBAT — THE SILENCE | JB: [jb_hp] HP | Colonel: [colonel_hp] HP"

    "The Colonel stops. He has run out of threats."
    "He stares at you, breathing heavily. He has nothing left to say."

    python:
        if jb_hp >= colonel_hp:
            renpy.say(None, "YOU ARE STRONGER. You withstood the barrage. The Colonel realizes he cannot break you.")
            colonel_hp = 0
            renpy.jump("colonel_glitch_phase")
        else:
            renpy.say(None, "YOU ARE BROKEN. You survived the argument, but the stress was too much.")
            renpy.say(None, "You don't have the energy to fight anymore. You slowly sit back down.")
            renpy.jump("colonel_defeat_ending")


## ---------------------------------------------------------------------------
## GLITCH PHASE — System Reset
## ---------------------------------------------------------------------------

label colonel_glitch_phase:

    play music "audio/sevirra_lenoloc.mp3" fadein 1.0

    scene bg_police_office with glitch_transition

    "[[SYSTEM]]: Colonel HP = 0."
    "He stumbles back. His coffee cup hits the floor. The sound echoes wrong — too long, like a sound effect on a broken loop."
    "He looks at you. His mouth opens. Closes."

    pause 1.5

    scene bg_black with glitch_transition

    "[[ERROR]]: NPC_STATE.integrity = CRITICAL"
    "[[ERROR]]: Attempting rollback..."

    pause 0.8

    "[[ERROR]]: Rollback FAILED."
    "[[ERROR]]: Falling back to cached state — bureaucracy_protocol_v1.exe"

    pause 0.8

    ## THE RESET
    $ colonel_hp = 100
    scene bg_police_office with glitch_transition
    show colonel normal at char_right

    "He stands up straight."
    "His face rearranges itself into the exact expression from this morning. The same coffee mug. The same posture. The same dead certainty."

    "Your blood runs cold."
    "He is looping."
    "He can't see you. He cannot process what just happened because there is no line of code for it."
    "He is not a man. He is a script."
    "'police_bureaucracy.exe' — runtime: 32 years."

    "He opens his mouth."
    colonel "'You are a {b}COWARD{/b}, JB! You were never fit for this force!'"

    "You feel the familiar pull of the argument. The urge to prove yourself. To justify. To fight."
    "Every debate you have ever lost with him rises up at once."

    "But then you see it."
    "The loop."
    "His eyes are already moving to the next line of script."
    "He isn't waiting for your answer. He never was."

    jump colonel_glitch_loop


label colonel_glitch_loop:

    menu:
        "[[ARGUE]] 'That's not true! I gave everything to this job!' (Restart the loop)":
            scene bg_police_office with glitch_transition
            "You open your mouth. You say the words."
            "He pours another coffee."
            "His expression doesn't change."
            "The argument is already starting again from line 1."
            "{color=#ff2222}You are trapped in the argument forever.{/color}"
            "(You realize something. Fighting the loop only feeds the loop. Try something else.)"
            jump colonel_glitch_loop

        "[[OBSERVE]] Just... watch him. Don't react. (Restart the loop once more)":
            "You say nothing."
            "He continues his speech."
            "He reaches the end of his monologue."
            "He starts it again."
            "On the third loop, you notice something."
            "His tie has a stain on it. Small. Left side. You never noticed it before."
            "He is mortal. He is small. He is a man in a room who is afraid of being forgotten."
            "You almost feel sorry for him."
            "Almost."
            jump colonel_glitch_loop_exit

        "{color=#00ff41}sys.exit(){/color} WAKE UP — Step out of the script.":
            jump colonel_glitch_wake_up


label colonel_glitch_loop_exit:

    "You stop fighting."
    "You stop arguing."
    "You look at him with absolute clarity."
    jb "'...This isn't about me at all, is it.'"
    "He doesn't respond. He never will."
    "You turn around and walk toward the door."
    jump colonel_victory_resolution


label colonel_glitch_wake_up:

    scene bg_black with glitch_transition

    "You take one breath."
    "You stop performing for him."
    "The argument dissolves like smoke."
    "It never had any weight. It was just noise."

    pause 1.0

    scene bg_police_office with dissolve
    show jb determined at char_left

    jb "'I'm done.'"
    "Two words. No volume. No anger."
    "You pick up your resignation letter from the desk. You fold it. You put it in his hand."
    "He doesn't move. He can't process the action."
    "You walk to the door."

    jump colonel_victory_resolution


label colonel_victory_resolution:

    python:
        if jb_hp >= 70:
            renpy.jump("good_ending")
        elif jb_hp >= 30:
            renpy.jump("colonel_pyrrhic_victory")
        else:
            renpy.jump("colonel_close_victory")
