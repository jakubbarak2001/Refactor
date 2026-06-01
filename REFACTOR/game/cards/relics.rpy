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
                       rarity="common", hook="", art=None, shop_price=None):
        RELIC_LIBRARY[rid] = {
            "id": rid,
            "name": name,
            "flavor": flavor,
            "archetype": archetype,   ## generic / iron / wrath / stack
            "rarity": rarity,         ## common / uncommon / rare
            "hook": hook,             ## one-line mechanic text (UI)
            "art": art or "images/relics/{}.png".format(rid),
            "shop_price": shop_price, ## per-relic override; None = rarity price
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
        archetype="iron", rarity="uncommon",
        hook="Heal 10 HP at the start of each fight.",
        flavor="Cracked leather, set in a permanent bend. It holds you together when nothing else does.",
    )
    register_relic(
        "gym_keycard",
        name="24/7 Gym Keycard",
        archetype="iron", rarity="uncommon",
        hook="SOMA grants block every 2 stacks instead of 3.",
        flavor="The night desk stopped checking the photo years ago.",
    )
    register_relic(
        "barbell",
        name="Olympic Barbell (20kg)",
        archetype="iron", rarity="rare",
        hook="Keep half your remaining block each turn.",
        flavor="Twenty kilos of knurled steel. It has never once lied to you.",
    )

    ## --- WRATH (Hatred engine) ---------------------------------------------
    register_relic(
        "the_dartboard",
        name="Office Dartboard",
        archetype="wrath", rarity="common",
        hook="Whenever you gain Hatred in a fight, gain 2 block.",
        flavor="Regulation-issue, break-room corner. You know the wall behind it by heart.",
    )
    register_relic(
        "brass_knuckles",
        name="Brass Knuckles (Evidence)",
        archetype="wrath", rarity="uncommon",
        hook="Whenever you gain Hatred in a fight, deal 3 damage to the enemy.",
        flavor="Logged, bagged, never filed. The drawer doesn't close all the way.",
    )
    register_relic(
        "colonel_mugshot",
        name="Colonel's Mugshot",
        archetype="wrath", rarity="uncommon",
        hook="Start each fight with +5 Hatred.",
        flavor="Pinned to the dartboard. You stopped throwing darts. You just look.",
    )
    register_relic(
        "confiscated_vial",
        name="Confiscated Vial (Evidence)",
        archetype="wrath", rarity="rare",
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

    def random_unowned_relic(weights=None):
        """A random relic id the player doesn't own yet, or None if they own
        them all. With `weights` ({rarity: int}), bias the roll by rarity."""
        _owned = set(getattr(store, "player_relics", None) or [])
        _pool = [rid for rid in RELIC_LIBRARY if rid not in _owned]
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

    def build_relic_shop_offers(n=3):
        """Roll up to n unowned relics for the shop, each priced by rarity.
        Returns a list of {'relic_id': str, 'price': int} dicts. Prices run
        through adjusted_cost so difficulty purchase_mult applies (parity with
        gym / coding / bootcamp spending)."""
        _owned = set(getattr(store, "player_relics", None) or [])
        _pool = [rid for rid in RELIC_LIBRARY if rid not in _owned]
        __import__("random").shuffle(_pool)
        offers = []
        for rid in _pool[:n]:
            offers.append({"relic_id": rid, "price": adjusted_cost(relic_shop_price(rid))})
        return offers

    def relic_on_victory():
        """Between-fight relic effects. Called from battle_with after a win
        (battle_finish has already written run_hp). Mutates run_hp directly."""
        if has_relic("lucky_koruna"):
            _max = getattr(store, "run_hp_max", None)
            _cur = getattr(store, "run_hp", None)
            if _cur is not None and _max:
                store.run_hp = min(_max, _cur + 8)


## ---------------------------------------------------------------------------
## relic_tray — horizontal strip of owned-relic chips. Reused in battle
## (top-left) and the deck viewer (under the header). Each chip is a
## tooltip button: name + rarity + mechanic surface on hover via the host
## screen's GetTooltip() consumer. Glyph-only so it stays compact; safe initial
## letter instead of emoji (render bug). The chip border reads archetype; a
## thin top rule reads rarity (gold = rare).
## ---------------------------------------------------------------------------
screen relic_tray(size=44):
    $ _relics = owned_relics()
    if _relics:
        ## Wrap into rows of at most 5 chips so a long collection stacks
        ## downward (left-to-right) instead of overflowing off the screen edge.
        $ _relic_rows = [_relics[_i:_i + 5] for _i in range(0, len(_relics), 5)]
        vbox:
            spacing 6
            for _row in _relic_rows:
                hbox:
                    spacing 6
                    for _rl in _row:
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
                            tooltip _rtip
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
