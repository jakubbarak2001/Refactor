################################################################################
## REFACTOR — Relics (personal effects / gear)
##
## Build-defining passive objects JB carries through a run (StS-relic role).
## Acquired via battle rewards / events / the Fixer shop. Reset each run in
## init_game (store.player_relics = []).
##
## Rarity is the POWER + PRICE tier, not the drop frequency:
##   common   — a modest, always-useful passive            (shop  5k).
##   uncommon — a stronger effect or a build-synergy piece  (shop 11k).
##   rare     — build-defining / snowball, usually a catch  (shop 20k).
##
## Effects hook the battle engine at clean points and there are NO decorative
## relics — every id below is consumed in exactly one of:
##   relic_apply_battle_init(bs)  [per-fight setup — block / energy / draw /
##                                 heal / opening shot / Hatred engine]
##   relic_on_victory()           [between-fight heal]
##   the coding-tier helper       [cracked_laptop, read in card_effects]
##
## Most relics simply write a buff key the turn loop ALREADY reads
## (starting_block / max_energy / soma_starting_block / relic_extra_draw /
## lab_first_free_per_turn / roid_rage / see_red / iron_posture /
## first_turn_bonus_draw / skip_attack_count), so the engine surface stays tiny.
################################################################################

init python:

    RELIC_LIBRARY = {}

    def register_relic(rid, name="", flavor="", archetype="generic",
                       rarity="common", hook="", art=None, shop_price=None,
                       class_lock=None):
        RELIC_LIBRARY[rid] = {
            "id": rid,
            "name": name,
            "flavor": flavor,
            "archetype": archetype,   ## generic / iron / wrath / stack
            "rarity": rarity,         ## common / uncommon / rare
            "hook": hook,             ## one-line mechanic text (UI)
            "art": art or "images/relics/{}.png".format(rid),
            "shop_price": shop_price, ## per-relic override; None = rarity price
            "class_lock": class_lock, ## None = neutral (all classes); else a class id
        }

    def has_relic(rid):
        return rid in (getattr(store, "player_relics", None) or [])

    def grant_relic(rid, silent=False):
        """Add a relic to the run. No-op if unknown or already owned."""
        if rid not in RELIC_LIBRARY:
            return False
        if getattr(store, "player_relics", None) is None:
            store.player_relics = []
        if rid in store.player_relics:
            return False
        store.player_relics.append(rid)
        if not silent:
            try:
                renpy.notify("Picked up: {}".format(RELIC_LIBRARY[rid]["name"]))
            except Exception:
                pass
        return True

    def owned_relics():
        _ids = getattr(store, "player_relics", None) or []
        return [RELIC_LIBRARY[r] for r in _ids if r in RELIC_LIBRARY]

    ## Archetype tint — matches the deck's synergy colors so a relic's border
    ## reads its build allegiance at a glance. Generic = warm grey.
    RELIC_ARCHETYPE_HEX = {
        "iron":    "#5b9bd5",   ## block/defense blue
        "wrath":   "#cc3322",   ## hatred red
        "stack":   "#4caf6a",   ## tech green
        "generic": "#b8a888",   ## neutral tan
    }

    ## Rarity tint — used by the shop + tray to communicate the price/power
    ## tier independent of the archetype border. Rare = gold.
    RELIC_RARITY_HEX = {
        "common":   "#9a9082",
        "uncommon": "#5b9bd5",
        "rare":     "#d8a13a",
    }

    def relic_hex(rid):
        _r = RELIC_LIBRARY.get(rid, {})
        return RELIC_ARCHETYPE_HEX.get(_r.get("archetype", "generic"), "#b8a888")

    def relic_rarity(rid):
        return RELIC_LIBRARY.get(rid, {}).get("rarity", "common")

    def relic_rarity_hex(rid):
        return RELIC_RARITY_HEX.get(relic_rarity(rid), "#9a9082")

    def relic_glyph(rid):
        ## Emoji render as '?' in-game (recurring bug) — use a safe initial.
        _r = RELIC_LIBRARY.get(rid, {})
        _name = _r.get("name", rid)
        return _name[0].upper() if _name else "*"

    def relic_art_disp(rid, px):
        ## Owned-relic icon fit into a `px` square, or None when the art file is
        ## missing so callers fall back to relic_glyph. Returns a Transform over
        ## the full-res 1024² source — NOT a baked im.Scale raster — so the GPU
        ## samples at the real device resolution and the icon stays crisp on a
        ## 4K display at any px. fit="contain" preserves the (square) aspect.
        _r = RELIC_LIBRARY.get(rid, {})
        _art = _r.get("art")
        if _art and renpy.loadable(_art):
            return Transform(_art, fit="contain", xysize=(px, px))
        return None

    ## ── Relic definitions ──────────────────────────────────────────────────
    ## Effects are grouped by archetype; rarity climbs within each group.

    ## --- GENERIC (build-agnostic) -----------------------------------------
    register_relic(
        "service_pistol",
        name="Service Pistol (Unloaded)",
        archetype="generic", rarity="common",
        hook="Start each fight by dealing 8 damage to the enemy.",
        flavor="Off-duty it stays unloaded. It stays unloaded.",
    )
    register_relic(
        "lucky_koruna",
        name="Lucky Koruna",
        archetype="generic", rarity="common",
        hook="Heal 8 HP after each victory.",
        flavor="Bent. Pre-1993. Your dad's. You don't spend it.",
    )
    register_relic(
        "taser",
        name="Taser (X26)",
        archetype="generic", rarity="uncommon",
        hook="Skip the enemy's first attack each fight.",
        flavor="Fifty thousand volts of conversation-ender. Standard issue, non-standard use.",
        shop_price=50000,
    )
    register_relic(
        "red_bull_crate",
        name="Red Bull Crate (24-pack)",
        archetype="generic", rarity="rare",
        hook="+1 max energy every fight.",
        flavor="Warm. Flat. Load-bearing.",
        shop_price=30000,
    )
    register_relic(
        "golden_handcuffs",
        name="Golden Handcuffs",
        archetype="generic", rarity="rare",
        hook="All money you gain is increased by 25% — from every source.",
        flavor="Gold plating, flaking already. The steel underneath is regulation. They never come off.",
    )

    ## --- IRON (block / survival) -------------------------------------------
    register_relic(
        "protein_tub",
        name="Protein Tub (5kg)",
        archetype="iron", rarity="common",
        hook="+3 block at the start of each turn.",
        flavor="Half-empty. Scoop's gone missing. Still does the job.",
        shop_price=15000,
    )
    register_relic(
        "weightlifting_belt",
        name="Lifting Belt",
        archetype="iron", rarity="uncommon", shop_price=15000,
        hook="Heal 10 HP at the start of each fight.",
        flavor="Cracked leather, set in a permanent bend. It holds you together when nothing else does.",
    )
    register_relic(
        "gym_keycard",
        name="24/7 Gym Keycard",
        archetype="iron", rarity="uncommon", shop_price=15000,
        class_lock="bodybuilder",
        hook="SOMA grants block every 2 stacks instead of 3.",
        flavor="The night desk stopped checking the photo years ago.",
    )
    register_relic(
        "barbell",
        name="Olympic Barbell (20kg)",
        archetype="iron", rarity="rare",
        hook="Keep half your remaining block each turn.",
        flavor="Twenty kilos of knurled steel. It has never once lied to you.",
        class_lock="bodybuilder",
    )

    ## --- WRATH (Hatred engine) ---------------------------------------------
    register_relic(
        "the_dartboard",
        name="Office Dartboard",
        archetype="wrath", rarity="common",
        class_lock="bodybuilder",
        hook="Whenever you gain Hatred in a fight, gain 2 block.",
        flavor="Regulation-issue, break-room corner. You know the wall behind it by heart.",
    )
    register_relic(
        "brass_knuckles",
        name="Brass Knuckles (Evidence)",
        archetype="wrath", rarity="uncommon",
        class_lock="bodybuilder",
        hook="Whenever you gain Hatred in a fight, deal 3 damage to the enemy.",
        flavor="Logged, bagged, never filed. The drawer doesn't close all the way.",
    )
    register_relic(
        "colonel_mugshot",
        name="Colonel's Mugshot",
        archetype="wrath", rarity="uncommon",
        class_lock="bodybuilder",
        hook="Start each fight with +5 Hatred.",
        flavor="Pinned to the dartboard. You stopped throwing darts. You just look.",
    )
    register_relic(
        "confiscated_vial",
        name="Confiscated Vial (Evidence)",
        archetype="wrath", rarity="rare",
        class_lock="bodybuilder",
        hook="Start each fight with +6 Hatred. Every Hatred gain also deals 3 damage and gains 2 block.",
        flavor="Seized off a kid in Most. Never logged. The label's worn to nothing; the contents aren't.",
    )

    ## --- STACK (cards / tech) ----------------------------------------------
    register_relic(
        "rubber_duck",
        name="Debugging Duck",
        archetype="stack", rarity="common",
        hook="Draw 2 extra cards on the first turn of each fight.",
        flavor="Yellow. Silent. Has closed more cases than half the station.",
        shop_price=15000,
    )
    register_relic(
        "evidence_bag",
        name="Sealed Evidence Bag",
        archetype="stack", rarity="uncommon",
        hook="The first card you play each turn costs 0.",
        flavor="Whatever was in it is your problem now.",
    )
    register_relic(
        "cold_case_file",
        name="Cold Case File",
        archetype="stack", rarity="uncommon",
        hook="Draw 1 extra card at the start of each turn.",
        flavor="Nobody else reopens it. You can't leave it shut.",
    )
    register_relic(
        "cracked_laptop",
        name="Cracked Laptop",
        archetype="stack", rarity="rare",
        hook="Your Coding counts as one tier higher (Git Blame, Refactor budget).",
        flavor="The screen's a spiderweb. The compiler doesn't care. Neither do you.",
    )

    ## ═══ EXPANSION POOL — NEUTRAL (all classes) ═══════════════════════════════
    register_relic(
        "turkish_coffee",
        name="Thermos of Turkish Coffee",
        archetype="generic", rarity="common",
        hook="+1 energy on the first turn of each fight.",
        flavor="Thick as tar, twice as black. The grounds settle; you don't.",
    )
    register_relic(
        "kevlar_surplus",
        name="Surplus Kevlar Vest",
        archetype="iron", rarity="uncommon",
        hook="+8 block on the first turn of each fight.",
        flavor="Stenciled with another man's blood type. Stops most of what the first minute throws.",
    )
    register_relic(
        "stab_vest",
        name="Stab Vest",
        archetype="iron", rarity="rare",
        hook="Every enemy attack deals 1 less (minimum 1).",
        flavor="Standard issue, never returned. The little nicks across the front were all headed somewhere worse.",
    )
    register_relic(
        "riot_shield",
        name="Riot Shield (Dented)",
        archetype="iron", rarity="rare",
        hook="Negate the first hit you would take each fight.",
        flavor="Lexan gone milky with scratches. Always one good hit left in it.",
    )
    register_relic(
        "police_flashlight",
        name="Maglite (4 D-cell)",
        archetype="generic", rarity="common",
        hook="The enemy's first attack each fight deals 50% less.",
        flavor="Aluminium, the length of a forearm. Issued for the dark; carried for the light.",
    )
    register_relic(
        "mini_fridge",
        name="Break-Room Mini-Fridge",
        archetype="generic", rarity="uncommon",
        hook="Heal 12 HP after each victory.",
        flavor="Someone's yogurt has been in there since spring. The energy drinks are colder for it.",
    )
    register_relic(
        "cop_pension",
        name="Beat Cop's Pension",
        archetype="generic", rarity="uncommon", shop_price=15000,
        hook="+2,500 CZK at the start of each day.",
        flavor="Fifteen years vested. The one thing the uniform pays whether you wear it or not.",
    )
    register_relic(
        "fixer_card",
        name="The Fixer's Business Card",
        archetype="generic", rarity="rare", shop_price=25000,
        hook="Everything the Fixer sells costs 25% less.",
        flavor="No name. No logo. One number, and the understanding that you're already a regular.",
    )
    register_relic(
        "spiral_notebook",
        name="Spiral Notebook",
        archetype="stack", rarity="common", shop_price=10000,
        hook="The first card you play each fight costs 1 less (minimum 0).",
        flavor="Margins full of plate numbers and half-thoughts. Shorthand only you can read.",
    )
    register_relic(
        "pawn_receipt",
        name="Pawn-Shop Receipt",
        archetype="stack", rarity="common",
        hook="Shredding a card at the Fixer pays you 3,000 CZK.",
        flavor="The man behind the counter never asks where it came from. That's the service.",
    )

    ## ═══ EXPANSION POOL — BODYBUILDER (class-locked) ══════════════════════════
    register_relic(
        "creatine",
        name="Creatine (Loading Phase)",
        archetype="iron", rarity="common", shop_price=15000,
        hook="Start each fight with +1 Strength.",
        flavor="Five grams, twice a day, water everywhere. The scale lies; the bar doesn't.",
        class_lock="bodybuilder",
    )
    register_relic(
        "chalk_bag",
        name="Chalk Bag",
        archetype="iron", rarity="rare", shop_price=35000,
        hook="Your first Attack each fight lands twice.",
        flavor="A fist of magnesium dust. Your grip holds the half-second longer than his does.",
        class_lock="bodybuilder",
    )
    register_relic(
        "resistance_bands",
        name="Resistance Bands",
        archetype="iron", rarity="common", shop_price=15000,
        hook="Gain +1 SOMA after each victory.",
        flavor="Looped over the door frame of every flat you've ever rented. They go where you go.",
        class_lock="bodybuilder",
    )
    register_relic(
        "posing_trunks",
        name="Competition Trunks",
        archetype="iron", rarity="uncommon", shop_price=20000,
        hook="While SOMA is 6 or higher, +3 block at the start of each turn.",
        flavor="Sequined, absurd, earned. You only wear them when the body has somewhere to be.",
        class_lock="bodybuilder",
    )
    register_relic(
        "pre_workout",
        name="Pre-Workout (Banned Formula)",
        archetype="wrath", rarity="uncommon", shop_price=25000,
        hook="+2 energy on the first turn of each fight, but start the fight with +4 Hatred.",
        flavor="The label's in Cyrillic and lying. Your ears ring before the first set. Worth it.",
        class_lock="bodybuilder",
    )
    register_relic(
        "punching_bag",
        name="Punching Bag (Re-Taped)",
        archetype="wrath", rarity="common",
        hook="The first time you gain Hatred each fight, draw 2 cards.",
        flavor="Split seam, leaking sand, mended in electrical tape. It has heard everything you can't say.",
        class_lock="bodybuilder",
    )
    register_relic(
        "knuckle_tape",
        name="Knuckle Tape",
        archetype="wrath", rarity="uncommon",
        hook="Each time you gain Hatred in a fight, gain +1 Strength (up to +5).",
        flavor="Wound tight enough to whiten the fingers. The anger has somewhere to go now.",
        class_lock="bodybuilder",
    )
    register_relic(
        "trenbolone",
        name="Trenbolone (Veterinary)",
        archetype="wrath", rarity="rare", shop_price=30000,
        hook="Start each fight with +3 Strength, but take +1 damage from every attack.",
        flavor="Meant for cattle. The vials don't pretend otherwise. Neither do the night sweats.",
        class_lock="bodybuilder",
    )
    register_relic(
        "weighted_vest",
        name="Weighted Vest (40 kg)",
        archetype="iron", rarity="rare",
        hook="+5 block at the start of each turn, but -1 energy on the first turn.",
        flavor="Forty kilos of sand sewn into a fishing jacket. You stopped noticing it. Nobody else did.",
        class_lock="bodybuilder",
    )
    register_relic(
        "service_photo",
        name="Old Service Photo",
        archetype="wrath", rarity="rare",
        hook="Start each fight with +10 Hatred. Heal 10 HP after a win if you ended above 60 Hatred.",
        flavor="Academy graduation, front row, certain of everything. You keep it face-down in the glovebox.",
        class_lock="bodybuilder",
    )

    ## ═══ EXPANSION POOL — BIOHACKER (class-locked) ═══════════════════════════
    ## BH had ZERO class relics vs BB's 15. These give each lane gear to snowball
    ## into, reusing engine buff keys the turn loop already reads (no new hooks
    ## beyond the elif / on-victory branches below). STIMULANT = energy, CODING =
    ## card flow, WETWARE = sustain (Peptide Vial pairs with Homeostasis).
    register_relic(
        "modafinil_bottle",
        name="Modafinil (Bulk Bottle)",
        archetype="wrath", rarity="common", shop_price=8000,
        hook="+1 energy on the first turn of each fight.",
        flavor="Two hundred tabs, blister-packed, shipped flat. You ration them like a man who won't.",
        class_lock="biohacker",
    )
    register_relic(
        "bulk_order",
        name="Wholesale Order",
        archetype="wrath", rarity="rare",
        hook="+1 max energy every fight.",
        flavor="You stopped buying doses and started buying inventory. The supplier calls you 'boss' now.",
        class_lock="biohacker",
    )
    register_relic(
        "standing_desk",
        name="Standing Desk",
        archetype="stack", rarity="common",
        hook="Draw 2 extra cards on the first turn of each fight.",
        flavor="You read it lowers all-cause mortality. You bought it for the focus. It does both.",
        class_lock="biohacker",
    )
    register_relic(
        "dual_monitors",
        name="Dual Monitors",
        archetype="stack", rarity="uncommon",
        hook="Draw 1 extra card at the start of each turn.",
        flavor="Twice the screen, twice the tabs open. The bottleneck was never the machine.",
        class_lock="biohacker",
    )
    register_relic(
        "recovery_ring",
        name="Recovery Ring",
        archetype="iron", rarity="uncommon",
        hook="Heal 12 HP after each victory.",
        flavor="Sleep score, HRV, readiness — a green number every morning. The body, quantified and coaxed.",
        class_lock="biohacker",
    )
    register_relic(
        "peptide_vial",
        name="Peptide Vial (BPC-157)",
        archetype="iron", rarity="rare",
        hook="Heal 4 HP at the end of each turn.",
        flavor="Reconstituted in the fridge door, drawn into an insulin pin. The tissue knits while you fight.",
        class_lock="biohacker",
    )

    ## ── Engine hooks ───────────────────────────────────────────────────────

    def relic_apply_battle_init(bs):
        """Apply per-fight relic setup. Called from battle_init AFTER class
        setup and enemy HP are established. Writes buff keys the turn loop
        already reads, so most relics need no other engine change.

        Every relic that affects combat is handled here EXCEPT:
          - cracked_laptop : read in the coding-tier helper (card_effects).
          - lucky_koruna   : between-fight heal, see relic_on_victory().
        """
        if bs is None:
            return
        for rid in (getattr(store, "player_relics", None) or []):

            ## --- GENERIC ---
            if rid == "service_pistol":
                ## Opening shot — chip the enemy before turn 1. Direct HP touch
                ## (not deal_damage) to avoid firing combat popups during init.
                bs.enemy_hp = max(0, bs.enemy_hp - 8)
                bs.add_log("[[Service Pistol]: opening shot — 8 damage.")
                if bs.enemy_hp <= 0:
                    bs.over = "victory"
            elif rid == "red_bull_crate":
                bs.max_energy += 1
            ## golden_handcuffs is now a pure economy relic (+25% money from any
            ## source) — applied in increment_stats_value_money, no battle effect.

            ## --- IRON ---
            elif rid == "protein_tub":
                bs.starting_block += 3
            elif rid == "weightlifting_belt":
                ## Per-fight top-up. Persists into run_hp via battle_finish on a
                ## win, so it doubles as light between-fight sustain.
                bs.player_hp = min(bs.player_max_hp, bs.player_hp + 10)
                bs.add_log("[[Lifting Belt]: +10 HP at the bell.")
            elif rid == "gym_keycard":
                ## Recompute SOMA block at per-2 (overrides the per-3 the engine
                ## set above). SOMA>=2 so a single stack still does nothing.
                _soma = getattr(store, "bb_soma", 0)
                if _soma >= 2:
                    bs.buffs["soma_starting_block"] = _soma // 2
            elif rid == "barbell":
                ## Iron Posture — keep half your standing block each turn. The
                ## block-build capstone: stacks the per-turn block from
                ## protein_tub / SOMA into a wall instead of letting it expire.
                bs.buffs["iron_posture"] = True

            ## --- WRATH ---
            elif rid == "the_dartboard":
                ## See Red — every in-fight Hatred gain walls up SEE_RED_BLOCK.
                bs.buffs["see_red"] = True
            elif rid == "brass_knuckles":
                ## Roid Rage — every in-fight Hatred gain chips the enemy
                ## ROID_RAGE_DMG. Shared boolean with the Roid Rage Power, so
                ## owning both does NOT double the chip.
                bs.buffs["roid_rage"] = True
            elif rid == "colonel_mugshot":
                ## Pre-fight Hatred surge, routed through the run stat so the
                ## scalers (heavy_set etc.) and See Red / Roid Rage all see it.
                if stats is not None:
                    stats.increment_stats_pcr_hatred(5)
                    bs.add_log("[[Colonel's Mugshot]: the face on the board. +5 Hatred.")
            elif rid == "confiscated_vial":
                ## The Wrath capstone — the whole engine in one object: opening
                ## Hatred + See Red (block) + Roid Rage (damage) on every gain.
                ## Replaces the_dartboard + brass_knuckles + (most of) mugshot.
                bs.buffs["see_red"] = True
                bs.buffs["roid_rage"] = True
                if stats is not None:
                    stats.increment_stats_pcr_hatred(6)
                    bs.add_log("[[Confiscated Vial]: it gets into your blood. +6 Hatred.")

            ## --- STACK ---
            elif rid == "evidence_bag":
                bs.buffs["lab_first_free_per_turn"] = True
            elif rid == "cold_case_file":
                bs.buffs["relic_extra_draw"] = bs.buffs.get("relic_extra_draw", 0) + 1
            elif rid == "rubber_duck":
                ## Opening-turn dig — read once on turn 1 in
                ## battle_start_player_turn, then irrelevant.
                bs.buffs["first_turn_bonus_draw"] = bs.buffs.get("first_turn_bonus_draw", 0) + 2

            ## --- EXPANSION: NEUTRAL ---
            elif rid == "turkish_coffee":
                bs.buffs["relic_turn1_energy"] = bs.buffs.get("relic_turn1_energy", 0) + 1
            elif rid == "kevlar_surplus":
                bs.buffs["relic_turn1_block"] = bs.buffs.get("relic_turn1_block", 0) + 8
            elif rid == "stab_vest":
                bs.buffs["flat_dr"] = bs.buffs.get("flat_dr", 0) + 1
            elif rid == "riot_shield":
                bs.buffs["negate_next_hit"] = True
            elif rid == "police_flashlight":
                bs.buffs["halve_next_hit"] = True
            elif rid == "spiral_notebook":
                bs.buffs["first_card_discount"] = True

            ## --- EXPANSION: BODYBUILDER ---
            elif rid == "creatine":
                bs.player_strength += 1
            elif rid == "chalk_bag":
                bs.buffs["first_attack_double"] = True
            elif rid == "posing_trunks":
                ## Read once at fight start — SOMA doesn't change mid-fight.
                if getattr(store, "bb_soma", 0) >= 6:
                    bs.starting_block += 3
            elif rid == "pre_workout":
                bs.buffs["relic_turn1_energy"] = bs.buffs.get("relic_turn1_energy", 0) + 2
                if stats is not None:
                    stats.increment_stats_pcr_hatred(4)
                    bs.add_log("[[Pre-Workout]: the formula hits. +4 Hatred.")
            elif rid == "punching_bag":
                bs.buffs["first_hatred_draw"] = True
            elif rid == "knuckle_tape":
                bs.buffs["hatred_strength"] = True
            elif rid == "trenbolone":
                bs.player_strength += 3
                bs.buffs["extra_dmg_taken"] = bs.buffs.get("extra_dmg_taken", 0) + 1
            elif rid == "weighted_vest":
                bs.starting_block += 5
                bs.buffs["relic_turn1_energy"] = bs.buffs.get("relic_turn1_energy", 0) - 1
            elif rid == "service_photo":
                if stats is not None:
                    stats.increment_stats_pcr_hatred(10)
                    bs.add_log("[[Old Service Photo]: the man you were. +10 Hatred.")

            ## --- EXPANSION: BIOHACKER ---
            elif rid == "modafinil_bottle":
                bs.buffs["relic_turn1_energy"] = bs.buffs.get("relic_turn1_energy", 0) + 1
            elif rid == "bulk_order":
                bs.max_energy += 1
            elif rid == "standing_desk":
                bs.buffs["first_turn_bonus_draw"] = bs.buffs.get("first_turn_bonus_draw", 0) + 2
            elif rid == "dual_monitors":
                bs.buffs["relic_extra_draw"] = bs.buffs.get("relic_extra_draw", 0) + 1
            elif rid == "peptide_vial":
                bs.buffs["telomere_heal"] = max(bs.buffs.get("telomere_heal", 0), 4)

            ## taser handled below (needs skip_attack_count, not a buff key)
            if rid == "taser":
                bs.skip_attack_count += 1

    ## Relic drop weighting — the rarity mix a victory rolls from. Bosses lean
    ## hard into rare gear (the reckoning pays out); routine hard wins are a
    ## fair spread; medium wins are mostly commons. Weights are crude integer
    ## copy-counts, not probabilities — only the ratios matter.
    def relic_drop_weights(tier, is_boss=False):
        if is_boss:
            return {"common": 1, "uncommon": 3, "rare": 4}
        if tier == "hard":
            return {"common": 2, "uncommon": 3, "rare": 2}
        return {"common": 4, "uncommon": 2, "rare": 1}

    def _relic_pool_eligible(rid):
        """Filter for the random-drop and shop offer pools: a class-locked relic
        is only eligible for its own class (mirrors cards' _ladder_pool_eligible).
        Explicit grant_relic() does NOT use this — scripted/event grants can
        still force any relic onto any class."""
        _lock = RELIC_LIBRARY.get(rid, {}).get("class_lock")
        if _lock:
            _pc = stats.player_class if stats is not None else None
            if _lock != _pc:
                return False
        return True

    def random_unowned_relic(weights=None):
        """A random relic id the player doesn't own yet, or None if they own
        them all. With `weights` ({rarity: int}), bias the roll by rarity."""
        _owned = set(getattr(store, "player_relics", None) or [])
        _pool = [rid for rid in RELIC_LIBRARY if rid not in _owned and _relic_pool_eligible(rid)]
        if not _pool:
            return None
        _rand = __import__("random")
        if not weights:
            return _rand.choice(_pool)
        _bag = []
        for rid in _pool:
            _w = max(1, int(weights.get(relic_rarity(rid), 1)))
            _bag.extend([rid] * _w)
        return _rand.choice(_bag) if _bag else _rand.choice(_pool)

    def roll_relic_choices(n=3, weights=None):
        """Up to n DISTINCT unowned, class-eligible relic ids, rarity-weighted —
        the choose-one-of-N gear shelf (the Quartermaster event). Returns [] when
        the player already owns the whole eligible pool."""
        _owned = set(getattr(store, "player_relics", None) or [])
        _pool = [rid for rid in RELIC_LIBRARY if rid not in _owned and _relic_pool_eligible(rid)]
        if not _pool:
            return []
        _rand = __import__("random")
        if not weights:
            _rand.shuffle(_pool)
            return _pool[:n]
        _bag = []
        for rid in _pool:
            _bag.extend([rid] * max(1, int(weights.get(relic_rarity(rid), 1))))
        _rand.shuffle(_bag)
        _picked = []
        for rid in _bag:
            if rid not in _picked:
                _picked.append(rid)
            if len(_picked) >= n:
                break
        return _picked

    ## Relic shop pricing by rarity. The spread is wide ON PURPOSE so the price
    ## reads the power tier at a glance: a common is half a great bouncer night,
    ## a rare is two of them. Relics also drop free off fights, so the shop is
    ## the path for a build that REFUSES fights (pacifist / low-Hatred) — it
    ## buys INTO a build with cash, never the whole shelf in one run.
    RELIC_SHOP_PRICES = {"common": 5000, "uncommon": 11000, "rare": 20000}

    def relic_shop_price(rid):
        _override = RELIC_LIBRARY.get(rid, {}).get("shop_price")
        if _override is not None:
            return _override
        return RELIC_SHOP_PRICES.get(relic_rarity(rid), 11000)

    def fixer_buy_price(base):
        """Fixer shop price after the Fixer's Business Card relic (25% off
        everything he sells). Applied LIVE at display + charge time — NOT baked
        into the per-day cached stock — so buying the card discounts the rest of
        the shelf the moment you own it, without re-rolling the offered items."""
        if has_relic("fixer_card"):
            return int(round(base * 0.75 / 50.0)) * 50
        return base

    def build_relic_shop_offers(n=3):
        """Roll up to n unowned relics for the shop, each priced by rarity.
        Returns a list of {'relic_id': str, 'price': int} dicts. Prices run
        through adjusted_cost so difficulty purchase_mult applies (parity with
        gym / coding / bootcamp spending)."""
        _owned = set(getattr(store, "player_relics", None) or [])
        _pool = [rid for rid in RELIC_LIBRARY if rid not in _owned and _relic_pool_eligible(rid)]
        __import__("random").shuffle(_pool)
        offers = []
        for rid in _pool[:n]:
            offers.append({"relic_id": rid, "price": adjusted_cost(relic_shop_price(rid))})
        return offers

    def relic_on_victory():
        """Between-fight relic effects. Called from battle_with after a win
        (battle_finish has already written run_hp). Mutates run_hp directly."""
        _max = getattr(store, "run_hp_max", None)
        _cur = getattr(store, "run_hp", None)
        _heal = 0
        if has_relic("lucky_koruna"):
            _heal += 8
        if has_relic("mini_fridge"):
            _heal += 12
        if has_relic("recovery_ring"):
            _heal += 12
        if has_relic("service_photo") and stats is not None and stats.pcr_hatred > 60:
            _heal += 10
        if _heal and _cur is not None and _max:
            store.run_hp = min(_max, _cur + _heal)
        ## Resistance Bands — the SOMA ramp also feeds off wins (BB-gated in add_soma).
        if has_relic("resistance_bands"):
            add_soma(1)


## ---------------------------------------------------------------------------
## relic_tray — horizontal strip of owned-relic chips. Reused in battle
## (top-left) and the deck viewer (under the header). Two hover surfaces:
##   inspect_panel=False (default) — classic tooltip; name + rarity + mechanic
##       surface via the host screen's GetTooltip() consumer (deck viewer).
##   inspect_panel=True — fixer-shop-style info panel anchored beside the
##       hovered chip, drawn by this screen itself (battle).
## Glyph-only so it stays compact; safe initial letter instead of emoji
## (render bug). The chip border reads archetype; a thin top rule reads
## rarity (gold = rare).
## ---------------------------------------------------------------------------
screen relic_tray(size=44, inspect_panel=False):
    ## (relic_id, row, col) under the cursor — drives the inspect panel.
    default _rt_hover = None
    $ _relics = owned_relics()
    if _relics:
        ## Wrap into rows of at most 5 chips so a long collection stacks
        ## downward (left-to-right) instead of overflowing off the screen edge.
        $ _relic_rows = [_relics[_i:_i + 5] for _i in range(0, len(_relics), 5)]
        vbox:
            spacing 6
            for _rt_ri, _row in enumerate(_relic_rows):
                hbox:
                    spacing 6
                    for _rt_ci, _rl in enumerate(_row):
                        $ _rhex = relic_hex(_rl["id"])
                        $ _rrhex = relic_rarity_hex(_rl["id"])
                        ## No square brackets in tooltip text — Ren'Py's Text engine
                        ## would try to interpolate '[RARE]' as a variable and NameError.
                        $ _rtip = "{}  ·  {}  ·  {}".format(_rl["name"], _rl.get("rarity", "common").upper(), _rl.get("hook", ""))
                        button:
                            xysize (size, size)
                            background Frame(Solid(_rhex), 3, 3)
                            padding (3, 3)
                            action NullAction()
                            tooltip (None if inspect_panel else _rtip)
                            ## SetLocalVariable, NOT SetScreenVariable: this
                            ## screen is `use`d with parameters, so it has its
                            ## own scope — SetScreenVariable would write to
                            ## the top-level screen and never reach _rt_hover.
                            hovered (SetLocalVariable("_rt_hover", (_rl["id"], _rt_ri, _rt_ci)) if inspect_panel else NullAction())
                            unhovered (SetLocalVariable("_rt_hover", None) if inspect_panel else NullAction())
                            vbox:
                                xfill True
                                yfill True
                                spacing 0
                                frame:
                                    xfill True
                                    ysize 3
                                    background Solid(_rrhex)
                                    padding (0, 0)
                                frame:
                                    xfill True
                                    yfill True
                                    background "#11110caa"
                                    padding (0, 0)
                                    $ _ricon = relic_art_disp(_rl["id"], int(size * 0.82))
                                    if _ricon is not None:
                                        add _ricon xalign 0.5 yalign 0.5
                                    else:
                                        text relic_glyph(_rl["id"]):
                                            xalign 0.5
                                            yalign 0.5
                                            color _rhex
                                            size int(size * 0.5)
                                            bold True
                                            font "fonts/RobotoMono-Regular.ttf"

        ## Hover-inspect panel — anchored beside the hovered chip, same look
        ## as the fixer shop's gear panel. Drawn after the grid so it layers
        ## on top; position math mirrors the chip stride (size + 6 spacing).
        if inspect_panel and _rt_hover is not None:
            $ _rt_meta = RELIC_LIBRARY.get(_rt_hover[0], {})
            $ _rt_hex  = relic_hex(_rt_hover[0])
            frame:
                xpos ((_rt_hover[2] + 1) * (size + 6) + 10)
                ypos (_rt_hover[1] * (size + 6))
                background Frame("#0d0a08f0", 4, 4)
                padding (18, 14)
                xmaximum 460
                at inspect_overlay_in
                vbox:
                    spacing 6
                    text _rt_meta.get("name", _rt_hover[0]):
                        color _rt_hex
                        size 22
                        bold True
                        font "fonts/RobotoMono-Regular.ttf"
                    text (_rt_meta.get("rarity", "common").upper()):
                        color "#8a7a64"
                        size 13
                        bold True
                        font "fonts/RobotoMono-Regular.ttf"
                    text _rt_meta.get("hook", ""):
                        color "#e2d8c4"
                        size 17
                        xmaximum 420
                        font "fonts/RobotoMono-Regular.ttf"
