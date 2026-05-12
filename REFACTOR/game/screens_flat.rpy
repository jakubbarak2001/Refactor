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
