################################################################################
## REFACTOR — Relics (personal effects / gear)
##
## Build-defining passive objects JB carries through a run (StS-relic role).
## Acquired via battle rewards / events / (future) shop. Reset each run in
## init_game (store.player_relics = []).
##
## Effects hook the battle engine at four clean points:
##   battle_init                 -> relic_apply_battle_init(bs)  [per-fight]
##   battle_start_player_turn    -> reads buffs["relic_extra_draw"] in draw step
##   battle_with (victory)       -> relic_on_victory()           [between-fight]
##
## Most relics simply write a buff key the turn loop ALREADY reads
## (starting_block / max_energy / roid_rage / lab_first_free_per_turn /
## soma_starting_block), so the engine surface stays tiny.
################################################################################

init python:

    RELIC_LIBRARY = {}

    def register_relic(rid, name="", flavor="", archetype="generic",
                       rarity="common", hook="", art=None):
        RELIC_LIBRARY[rid] = {
            "id": rid,
            "name": name,
            "flavor": flavor,
            "archetype": archetype,   ## generic / iron / wrath / stack
            "rarity": rarity,
            "hook": hook,             ## one-line mechanic text (UI)
            "art": art or "images/relics/{}.png".format(rid),
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

    def relic_hex(rid):
        _r = RELIC_LIBRARY.get(rid, {})
        return RELIC_ARCHETYPE_HEX.get(_r.get("archetype", "generic"), "#b8a888")

    def relic_glyph(rid):
        ## Emoji render as '?' in-game (recurring bug) — use a safe initial.
        _r = RELIC_LIBRARY.get(rid, {})
        _name = _r.get("name", rid)
        return _name[0].upper() if _name else "*"

    ## ── Relic definitions ──────────────────────────────────────────────────

    register_relic(
        "protein_tub",
        name="Protein Tub (5kg)",
        archetype="iron", rarity="common",
        hook="+3 block at the start of each turn.",
        flavor="Half-empty. Scoop's gone missing. Still does the job.",
    )
    register_relic(
        "gym_keycard",
        name="24/7 Gym Keycard",
        archetype="iron", rarity="uncommon",
        hook="SOMA gives block every 2 stacks instead of 3.",
        flavor="The night desk stopped checking the photo years ago.",
    )
    register_relic(
        "colonel_mugshot",
        name="Colonel's Mugshot",
        archetype="wrath", rarity="uncommon",
        hook="Start each fight with +5 Hatred.",
        flavor="Pinned to the dartboard. You stopped throwing darts. You just look.",
    )
    register_relic(
        "brass_knuckles",
        name="Brass Knuckles (Evidence)",
        archetype="wrath", rarity="uncommon",
        hook="Whenever you gain Hatred in a fight, deal 3 damage to the enemy.",
        flavor="Logged, bagged, never filed. The drawer doesn't close all the way.",
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
        "red_bull_crate",
        name="Red Bull Crate (24-pack)",
        archetype="generic", rarity="rare",
        hook="+1 max energy every fight.",
        flavor="Warm. Flat. Load-bearing.",
    )
    register_relic(
        "service_pistol",
        name="Service Pistol (Unloaded)",
        archetype="generic", rarity="common",
        hook="At the start of each fight, deal 8 damage to the enemy.",
        flavor="Off-duty it stays unloaded. It stays unloaded.",
    )
    register_relic(
        "lucky_koruna",
        name="Lucky Koruna",
        archetype="generic", rarity="common",
        hook="Heal 6 HP after each victory.",
        flavor="Bent. Pre-1993. Your dad's. You don't spend it.",
    )

    ## ── Engine hooks ───────────────────────────────────────────────────────

    def relic_apply_battle_init(bs):
        """Apply per-fight relic setup. Called from battle_init AFTER class
        setup and enemy HP are established. Writes buff keys the turn loop
        already reads, so most relics need no other engine change."""
        if bs is None:
            return
        for rid in (getattr(store, "player_relics", None) or []):
            if rid == "protein_tub":
                bs.starting_block += 3
            elif rid == "red_bull_crate":
                bs.max_energy += 1
            elif rid == "brass_knuckles":
                ## Reuse the roid_rage buff the engine already reads in
                ## gain_hatred — chip the enemy 3 on every Hatred gain. No new
                ## engine hook. Idempotent with the Roid Rage Power (shared
                ## boolean key) — owning both does NOT double the chip.
                bs.buffs["roid_rage"] = True
            elif rid == "evidence_bag":
                bs.buffs["lab_first_free_per_turn"] = True
            elif rid == "cold_case_file":
                bs.buffs["relic_extra_draw"] = bs.buffs.get("relic_extra_draw", 0) + 1
            elif rid == "gym_keycard":
                ## Recompute SOMA block at per-2 (overrides the per-3 the engine
                ## set above). SOMA>=2 so a single stack still does nothing.
                _soma = getattr(store, "bb_soma", 0)
                if _soma >= 2:
                    bs.buffs["soma_starting_block"] = _soma // 2
            elif rid == "colonel_mugshot":
                ## Pre-fight Hatred surge, routed through the run stat so the
                ## scalers (heavy_set etc.) and See Red / Roid Rage all see it.
                ## +5 (not +10): at +10/fight the involuntary climb shoved the
                ## player across the 60/80 rage-injection thresholds early,
                ## flooding a non-Wrath deck with permanent Rage cards it can't
                ## unequip. +5 keeps it a Wrath payoff, not a brick.
                if stats is not None:
                    stats.increment_stats_pcr_hatred(5)
                    bs.add_log("[[Colonel's Mugshot]: the face on the board. +5 Hatred.")
            elif rid == "service_pistol":
                ## Opening shot — chip the enemy before turn 1. Direct HP touch
                ## (not deal_damage) to avoid firing combat popups during init.
                bs.enemy_hp = max(0, bs.enemy_hp - 8)
                bs.add_log("[[Service Pistol]: opening shot — 8 damage.")
                ## Register the kill if the chip drops a (future) <=8 HP enemy,
                ## so the fight doesn't open in a zombie state (enemy at 0, alive).
                if bs.enemy_hp <= 0:
                    bs.over = "victory"

    def random_unowned_relic():
        """A random relic id the player doesn't own yet, or None if they own
        them all. Used by the hard-tier ladder 'elite drops gear' grant."""
        _owned = set(getattr(store, "player_relics", None) or [])
        _pool = [rid for rid in RELIC_LIBRARY if rid not in _owned]
        if not _pool:
            return None
        return __import__("random").choice(_pool)

    ## Relic shop pricing by rarity. Relics are build-defining, so they cost
    ## well above a card (a great bouncer night ~10k). Priced so a run can
    ## afford ~1-2 bought relics on top of what bosses/ladder drop — money
    ## buys INTO a build, never the whole shelf.
    RELIC_SHOP_PRICES = {"common": 7000, "uncommon": 11000, "rare": 16000}

    def build_relic_shop_offers(n=2):
        """Roll up to n unowned relics for the shop, each priced by rarity.
        Returns a list of {'relic_id': str, 'price': int} dicts."""
        _owned = set(getattr(store, "player_relics", None) or [])
        _pool = [rid for rid in RELIC_LIBRARY if rid not in _owned]
        __import__("random").shuffle(_pool)
        offers = []
        for rid in _pool[:n]:
            _rarity = RELIC_LIBRARY[rid].get("rarity", "common")
            offers.append({"relic_id": rid, "price": RELIC_SHOP_PRICES.get(_rarity, 11000)})
        return offers

    def relic_on_victory():
        """Between-fight relic effects. Called from battle_with after a win
        (battle_finish has already written run_hp). Mutates run_hp directly."""
        if has_relic("lucky_koruna"):
            _max = getattr(store, "run_hp_max", None)
            _cur = getattr(store, "run_hp", None)
            if _cur is not None and _max:
                store.run_hp = min(_max, _cur + 6)


## ---------------------------------------------------------------------------
## relic_tray — horizontal strip of owned-relic chips. Reused in battle
## (top-left) and the deck viewer (under the header). Each chip is a
## tooltip button: name + mechanic surface on hover via the host screen's
## GetTooltip() consumer. Glyph-only so it stays compact; safe initial
## letter instead of emoji (render bug).
## ---------------------------------------------------------------------------
screen relic_tray(size=44):
    $ _relics = owned_relics()
    if _relics:
        hbox:
            spacing 6
            for _rl in _relics:
                $ _rhex = relic_hex(_rl["id"])
                $ _rtip = "{} — {}".format(_rl["name"], _rl.get("hook", ""))
                button:
                    xysize (size, size)
                    background Frame(Solid(_rhex), 3, 3)
                    padding (3, 3)
                    action NullAction()
                    tooltip _rtip
                    frame:
                        xfill True
                        yfill True
                        background "#11110caa"
                        text relic_glyph(_rl["id"]):
                            xalign 0.5
                            yalign 0.5
                            color _rhex
                            size int(size * 0.5)
                            bold True
                            font "fonts/RobotoMono-Regular.ttf"
