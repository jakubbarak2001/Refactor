# Dynamic JB flat — layered home location that reacts to progression.
# Slice 1: calendar X-marks over elapsed days.
#
# >>> HOW TO PLACE THE X-MARKS — click each day, no math <<<
#   1. Launch the game, walk into the flat.
#   2. Open the console (Shift+O) and type:   show screen cal_place
#   3. The calendar is shown with a prompt "Click day 1 / 31". CLICK the spot on
#      the calendar where day 1's cross should sit (right on the printed "1").
#      A green dot drops there. Then it asks for day 2, and so on, up to 31.
#        - Backspace = undo the last click (step back one day)
#        - Esc      = stop early and save what you've got so far
#   4. After the 31st click it writes the coordinates to:
#         <project>/REFACTOR/game/cal_cells.txt
#      Open that file, copy the `CAL_CELLS = { ... }` block, and paste it over
#      the `CAL_CELLS = {}` line below. Save. Done — exact, forever.
#
# If CAL_CELLS is empty (or a day is missing from it), that day falls back to a
# rough 4-corner interpolation (CAL_*_DEF) so nothing ever crashes.

init python:
    # ---- the real data: explicit per-day cross centres in 1920x1080 space ----
    # Filled by the cal_place screen (see header). Empty {} = use the fallback.
    CAL_CELLS = {
        1: (308, 336),   2: (334, 339),
        3: (164, 358),   4: (199, 363),   5: (229, 365),   6: (259, 368),   7: (287, 371),   8: (314, 373),   9: (336, 374),
        10: (165, 394),  11: (198, 396),  12: (229, 398),  13: (259, 400),  14: (284, 400),  15: (314, 404),  16: (336, 404),
        17: (165, 428),  18: (199, 430),  19: (230, 431),  20: (259, 433),  21: (288, 432),  22: (315, 432),  23: (337, 431),
        24: (166, 464),  25: (200, 462),  26: (232, 463),  27: (260, 463),  28: (287, 464),  29: (312, 463),  30: (341, 468),
        31: (170, 500),
    }

    # ---- fallback only: 4 corners of the day-cell grid, used for any day not in CAL_CELLS ----
    CAL_TL_DEF = (179, 312)   # top-left day cell    (col 0, row 0)
    CAL_TR_DEF = (346, 338)   # top-right day cell   (col 6, row 0)
    CAL_BL_DEF = (181, 491)   # bottom-left day cell (col 0, row 5)
    CAL_BR_DEF = (350, 485)   # bottom-right day cell(col 6, row 5)
    CAL_COLS = 7
    CAL_ROWS = 6

    CAL_X_SIZE = 32           # rendered px size of an x_mark
    CAL_X_ROT  = 0            # base rotation in degrees (a small random wobble is added)

    FLAT_X_VARIANTS = [
        "images/jb_flat/x_mark.png",
        "images/jb_flat/x_mark_2.png",
        "images/jb_flat/x_mark_3.png",
    ]
    FLAT_X_FORCE = 1          # index to force EVERY cross to one variant; None = cycle
    FLAT_X_SCALE = {
        "images/jb_flat/x_mark.png":   1.0,
        "images/jb_flat/x_mark_2.png": 0.78,
        "images/jb_flat/x_mark_3.png": 1.0,
    }

    def _flat_day_slot(d):
        idx = d + 4
        return idx % CAL_COLS, idx // CAL_COLS

    def _cal_fallback_cell(d):
        col, row = _flat_day_slot(d)
        row = min(row, CAL_ROWS - 1)
        u = col / float(CAL_COLS - 1)
        v = row / float(CAL_ROWS - 1)
        tx = CAL_TL_DEF[0] + (CAL_TR_DEF[0] - CAL_TL_DEF[0]) * u
        ty = CAL_TL_DEF[1] + (CAL_TR_DEF[1] - CAL_TL_DEF[1]) * u
        bx = CAL_BL_DEF[0] + (CAL_BR_DEF[0] - CAL_BL_DEF[0]) * u
        by = CAL_BL_DEF[1] + (CAL_BR_DEF[1] - CAL_BL_DEF[1]) * u
        return (int(round(tx + (bx - tx) * v)), int(round(ty + (by - ty) * v)))

    def calendar_cell(d):
        if d in CAL_CELLS:
            return tuple(CAL_CELLS[d])
        return _cal_fallback_cell(d)

    def _flat_x_for_day(d):
        rng = renpy.random.Random(d * 2654435761)
        if FLAT_X_FORCE is not None:
            img = FLAT_X_VARIANTS[FLAT_X_FORCE % len(FLAT_X_VARIANTS)]
        else:
            img = FLAT_X_VARIANTS[d % len(FLAT_X_VARIANTS)]
        size = max(4, int(round(CAL_X_SIZE * FLAT_X_SCALE.get(img, 1.0))))
        return img, CAL_X_ROT + rng.randint(-4, 4), size

    # ---- Colonel mugshot escalation: pcr_hatred -> decals over the dartboard photo ----
    # Highest threshold <= hatred wins; below the first one = clean photo. Each tier is a
    # list of decals (image + box + rotation) and fully REPLACES the previous tier — it's a
    # state, not a stack. The bazooka tier is the punchline: the photo's just gone.
    # Re-tune placements with:  show screen colonel_marks   (drag corners, [ / ] rotate).
    import math

    _C_DART   = "images/jb_flat/colonel_dart1.png"
    _C_KNIFE  = "images/jb_flat/colonel_knife.png"
    _C_DEFACE = "images/jb_flat/colonel_deface.png"   # red-marker vandalism + ZRÁDCE over the photo
    _C_WALL   = "images/jb_flat/colonel_wall.png"     # "ALL COPS ARE BEAUTIFUL (:" etc. on the wall
    _C_SCHIZO = "images/jb_flat/colonel_schizo.png"   # manic "POLICIE POLICIE" cop-doodle scrawl, wall between calendar & photo
    _C_BAZ    = "images/jb_flat/colonel_bazooka.png"

    COLONEL_THRESHOLDS = [20, 35, 50, 70, 82, 90]
    # threshold -> [ (image, left, top, width, height, rotate_deg), ... ]
    # (left,top,w,h) is the box the decal is centred in; rotation pivots about that centre.
    # A tier fully REPLACES the previous one. Escalation: 1 dart -> 3 darts -> knife ->
    # photo defaced w/ marker -> graffiti spills onto the wall -> bazooka hole.
    COLONEL_DECALS = {
        20: [(_C_DART, 584, 294, 49, 18, -8)],
        35: [(_C_DART, 584, 294, 49, 18, -8),
             (_C_DART, 624, 364, 49, 18,   3),
             (_C_DART, 611, 406, 49, 18, -22)],
        50: [(_C_KNIFE, 621, 345, 100, 70, 0)],
        70: [(_C_DEFACE, 595, 341, 67, 41, 0)],
        82: [(_C_DEFACE, 595, 341, 67, 41, 0),
             (_C_WALL, 125, 10, 380, 200, 17),
             (_C_SCHIZO, 355, 255, 180, 100, 5)],
        90: [(_C_WALL, 125, 10, 380, 200, 17),
             (_C_SCHIZO, 355, 255, 180, 100, 5),
             (_C_BAZ, 241, 64, 482, 516, 0)],
    }
    # fallback colours used if a PNG is missing (so it never crashes)
    COLONEL_PLACEHOLDER = {_C_DART: "#ffcc00", _C_KNIFE: "#cccccc", _C_DEFACE: "#cc2222", _C_WALL: "#202020", _C_SCHIZO: "#303030", _C_BAZ: "#3a2a1a"}
    COLONEL_DECAL_DEFAULT = (495, 280, 120, 140, 0)

    # static props composited onto the flat: (image, left, top, width, height, rotate_deg, class_or_None).
    # class_or_None: if set, the prop only shows when stats.player_class == that string.
    _P_WHEY = "images/jb_flat/whey.png"
    JB_PROPS = [
        (_P_WHEY, 1500, 440, 95, 144, 0, "bodybuilder"),
    ]
    COLONEL_PLACEHOLDER[_P_WHEY] = "#e8e0d0"

    def _colonel_active_tier():
        st_ = getattr(store, "stats", None)
        h = getattr(st_, "pcr_hatred", 0) if st_ is not None else 0
        chosen = None
        for thr in COLONEL_THRESHOLDS:
            if h >= thr:
                chosen = thr
        return chosen

    def _colonel_decal_d(img):
        if renpy.loadable(img):
            return img
        return Solid(COLONEL_PLACEHOLDER.get(img, "#ff00ff"))

    def _colonel_place(decal):
        # decal = (img, l, t, w, h, rot). Returns (pos, displayable), keeping the decal centred
        # on the (l,t,w,h) box regardless of rotation (Ren'Py pads rotated renders, so compensate).
        img, l, t, w, h = decal[0], decal[1], decal[2], decal[3], decal[4]
        rot = decal[5] if len(decal) > 5 else 0
        r = math.radians(rot)
        c, s = abs(math.cos(r)), abs(math.sin(r))
        bw, bh = w * c + h * s, w * s + h * c
        pos = (int(round(l + (w - bw) / 2.0)), int(round(t + (h - bh) / 2.0)))
        return pos, Transform(_colonel_decal_d(img), size=(w, h), rotate=rot)

    def _jb_flat_displayable(st, at):
        parts = [
            (1920, 1080),
            (0, 0), im.Scale("images/backgrounds/jb_flat_empty_decin.jpg", 1920, 1080),
        ]
        cur = day_cycle.current_day if day_cycle is not None else 1
        for d in range(1, cur):
            img, rot, size = _flat_x_for_day(d)
            cx, cy = calendar_cell(d)
            parts.append((cx - size // 2, cy - size // 2))
            parts.append(Transform(img, size=(size, size), rotate=rot))

        _cls = getattr(getattr(store, "stats", None), "player_class", None)
        for prop in JB_PROPS:
            need = prop[6] if len(prop) > 6 else None
            if need is not None and need != _cls:
                continue
            pos, d = _colonel_place(prop)
            parts.append(pos)
            parts.append(d)

        tier = _colonel_active_tier()
        if tier is not None:
            for decal in COLONEL_DECALS.get(tier, []):
                pos, d = _colonel_place(decal)
                parts.append(pos)
                parts.append(d)
        return Composite(*parts), 1.0

    # ---------------- click-to-place tuner (dev only) ----------------
    cal_place_day = 1
    cal_placed = {}

    def _cal_place_click():
        x, y = renpy.get_mouse_pos()
        cal_placed[cal_place_day] = (int(x), int(y))
        _cal_place_advance()

    def _cal_place_advance():
        global cal_place_day
        if cal_place_day >= 31:
            _cal_place_save()
            renpy.hide_screen("cal_place")
            return
        cal_place_day += 1
        renpy.restart_interaction()

    def _cal_place_undo():
        global cal_place_day
        if cal_place_day > 1:
            cal_place_day -= 1
        cal_placed.pop(cal_place_day, None)
        renpy.restart_interaction()

    def _cal_place_save():
        import os
        path = os.path.join(config.gamedir, "cal_cells.txt")
        with open(path, "w") as f:
            f.write("CAL_CELLS = {\n")
            for d in range(1, 32):
                if d in cal_placed:
                    f.write("    %d: %r,\n" % (d, tuple(cal_placed[d])))
            f.write("}\n")
        renpy.notify("Uloženo %d bunek -> game/cal_cells.txt" % len(cal_placed))

image bg_jb_flat = DynamicDisplayable(_jb_flat_displayable)

screen cal_place():
    zorder 100
    modal True

    button:
        xfill True yfill True
        background None
        action Function(_cal_place_click)

    for d, (px, py) in cal_placed.items():
        add Solid("#00ff00", xysize=(8, 8)) xpos (px - 4) ypos (py - 4)
        text "[d]" xpos (px + 6) ypos (py - 8) size 12 color "#00ff00" outlines [(1, "#000", 0, 0)]

    frame:
        align (0.5, 0.0)
        padding (18, 12)
        background "#000000cc"
        text "Klikni na číslo dne  [cal_place_day] / 31     (Backspace = zpět · Esc = uložit a konec)" size 24 color "#ffffff"

    key "K_BACKSPACE" action Function(_cal_place_undo)
    key "K_ESCAPE"    action [Function(_cal_place_save), Hide("cal_place")]


# ---------------- Colonel decal placement tuner (dev only) ----------------
# show screen colonel_marks  -> walks every decal across all hatred tiers, one at a time:
#   click TOP-LEFT corner, then BOTTOM-RIGHT corner of where this decal sits over the photo;
#   [ / ] = rotate (Shift = x5);  Backspace = reset this decal to file value;
#   Enter = next decal;  Left arrow = previous decal;  Esc = save & quit.
# Writes game/colonel_overlay.txt -> paste the COLONEL_DECALS block over the one above.
init python:
    colonel_decals_tmp = {thr: [list(d) for d in lst] for thr, lst in COLONEL_DECALS.items()}
    colonel_flat = [(thr, i) for thr in COLONEL_THRESHOLDS for i in range(len(COLONEL_DECALS[thr]))]
    colonel_mark_idx = 0
    colonel_mark_step = 0     # 0 = need top-left click, 1 = need bottom-right click

    def _cm_cur():
        thr, i = colonel_flat[colonel_mark_idx]
        d = colonel_decals_tmp[thr][i]
        while len(d) < 6:
            d.append(0)
        return thr, i, d

    def _cm_click():
        global colonel_mark_step
        thr, i, d = _cm_cur()
        x, y = renpy.get_mouse_pos()
        x, y = int(x), int(y)
        if colonel_mark_step == 0:
            d[1], d[2], d[3], d[4] = x, y, 0, 0
            colonel_mark_step = 1
            renpy.restart_interaction()
        else:
            l, t = d[1], d[2]
            d[1], d[2], d[3], d[4] = min(l, x), min(t, y), abs(x - l), abs(y - t)
            colonel_mark_step = 0
            _cm_next()

    def _cm_rotate(delta):
        thr, i, d = _cm_cur()
        d[5] = (d[5] + delta) % 360
        renpy.restart_interaction()

    def _cm_reset():
        global colonel_mark_step
        thr, i, d = _cm_cur()
        d[:] = list(COLONEL_DECALS[thr][i])
        while len(d) < 6:
            d.append(0)
        colonel_mark_step = 0
        renpy.restart_interaction()

    def _cm_next():
        global colonel_mark_idx, colonel_mark_step
        colonel_mark_step = 0
        if colonel_mark_idx >= len(colonel_flat) - 1:
            _cm_save()
            renpy.hide_screen("colonel_marks")
            return
        colonel_mark_idx += 1
        renpy.restart_interaction()

    def _cm_prev():
        global colonel_mark_idx, colonel_mark_step
        colonel_mark_step = 0
        if colonel_mark_idx > 0:
            colonel_mark_idx -= 1
        renpy.restart_interaction()

    def _cm_save():
        import os
        names = {_C_DART: "_C_DART", _C_KNIFE: "_C_KNIFE", _C_BULL: "_C_BULL", _C_BAZ: "_C_BAZ"}
        path = os.path.join(config.gamedir, "colonel_overlay.txt")
        with open(path, "w") as f:
            f.write("    COLONEL_DECALS = {\n")
            for thr in COLONEL_THRESHOLDS:
                rows = []
                for d in colonel_decals_tmp[thr]:
                    while len(d) < 6:
                        d.append(0)
                    rows.append("(%s, %d, %d, %d, %d, %d)" % (names.get(d[0], repr(d[0])), d[1], d[2], d[3], d[4], d[5]))
                f.write("        %d: [%s],\n" % (thr, ", ".join(rows)))
            f.write("    }\n")
        renpy.notify("Uloženo -> game/colonel_overlay.txt")

screen colonel_marks():
    zorder 100
    modal True

    button:
        xfill True yfill True
        background None
        action Function(_cm_click)

    $ _thr, _di, _d = _cm_cur()
    for _dd in colonel_decals_tmp[_thr]:
        if len(_dd) >= 5 and _dd[3] > 0 and _dd[4] > 0:
            $ _pos, _disp = _colonel_place(_dd)
            add Transform(_disp, alpha=(0.95 if _dd is _d else 0.4)) xpos _pos[0] ypos _pos[1]
    if colonel_mark_step == 1:
        add Solid("#ff00ff", xysize=(10, 10)) xpos (_d[1] - 5) ypos (_d[2] - 5)

    $ _step_txt = "klikni LEVÝ HORNÍ roh" if colonel_mark_step == 0 else "klikni PRAVÝ DOLNÍ roh"
    frame:
        align (0.5, 0.0)
        padding (18, 12)
        background "#000000cc"
        text "Decal  [[[colonel_mark_idx]+1 / [len(colonel_flat)]]   ·   hatred ≥ [_thr]   ·   rot=[_d[5]]   —   [_step_txt]\n[_d[0]]    [ ] otoč (Shift x5) · Backspace reset · Enter další · ← zpět · Esc uložit a konec" size 22 color "#ffffff"

    key "K_LEFTBRACKET"        action Function(_cm_rotate, -1)
    key "K_RIGHTBRACKET"       action Function(_cm_rotate, 1)
    key "shift_K_LEFTBRACKET"  action Function(_cm_rotate, -5)
    key "shift_K_RIGHTBRACKET" action Function(_cm_rotate, 5)
    key "K_BACKSPACE" action Function(_cm_reset)
    key "K_RETURN"    action Function(_cm_next)
    key "K_KP_ENTER"  action Function(_cm_next)
    key "K_LEFT"      action Function(_cm_prev)
    key "K_ESCAPE"    action [Function(_cm_save), Hide("colonel_marks")]
