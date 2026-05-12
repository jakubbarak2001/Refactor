# Dynamic JB flat — layered home location that reacts to progression.
# Slice 1: calendar X-marks over elapsed days. (Dartboard / monitors / shrine = later slices.)
# All tunable geometry lives here at the top — re-tune if the base BG is re-framed.
#
# >>> HOW TO TUNE THE CALENDAR <<<
# Every row of the month grid has its OWN anchor below in CAL_ROW_ANCHORS — the
# (x, y) position of that row's LEFTMOST cross (the "Pondělí"/Monday column).
# Tune each row on its own:
#   - cross too far LEFT  in a row  -> increase that row's first number (x)
#   - cross too far RIGHT in a row  -> decrease that row's first number (x)
#   - whole row too LOW            -> decrease that row's second number (y)
#   - whole row too HIGH           -> increase that row's second number (y)
# Crosses within a row march rightward by CAL_COL each column (x = spacing,
# y = downward tilt across the row). CAL_X_SIZE / CAL_X_ROT = size & rotation.
# After editing: save, then in-game press Shift+R. If nothing changes, fully
# quit the game and relaunch (init-python constants sometimes need a cold start).

init python:
    # row anchors — col-0 cross position, top row to bottom row. 6 rows total:
    #   row 0 = days 1-2     (only the Sat/Sun columns are used)
    #   row 1 = days 3-9
    #   row 2 = days 10-16
    #   row 3 = days 17-23
    #   row 4 = days 24-30
    #   row 5 = day 31
    CAL_ROW_ANCHORS = [
        (160, 315),   # row 0
        (140, 332),   # row 1
        (155, 385),   # row 2
        (151, 418),   # row 3
        (147, 451),   # row 4
        (143, 484),   # row 5
    ]
    CAL_COL    = (27, 2)         # per-column step: x = spacing between crosses, y = tilt down across the row
    CAL_X_SIZE = 32              # base rendered px size of an x_mark — bigger = chunkier
    CAL_X_ROT  = 6               # base rotation in degrees

    # x_mark variants — list whichever PNGs actually exist in images/jb_flat/.
    FLAT_X_VARIANTS = [
        "images/jb_flat/x_mark.png",
        "images/jb_flat/x_mark_2.png",
        "images/jb_flat/x_mark_3.png",
    ]
    # set to an index to force EVERY cross to that one variant; None = cycle through all.
    FLAT_X_FORCE = 1   # 1 = the variant used for day 1
    # per-variant size multiplier (1.0 = use CAL_X_SIZE as-is). Shrink a specific cross here.
    FLAT_X_SCALE = {
        "images/jb_flat/x_mark.png":   1.0,
        "images/jb_flat/x_mark_2.png": 0.78,
        "images/jb_flat/x_mark_3.png": 1.0,
    }

    def _flat_day_slot(d):
        # This month: day 1 sits in column 5 of row 0 (Sat-start). Adjust the +4
        # if the calendar art uses a different month layout.
        idx = d + 4
        return idx % 7, idx // 7

    def calendar_cell(d):
        col, row = _flat_day_slot(d)
        row = min(row, len(CAL_ROW_ANCHORS) - 1)
        ax, ay = CAL_ROW_ANCHORS[row]
        return (int(ax + col * CAL_COL[0]), int(ay + col * CAL_COL[1]))

    def _flat_x_for_day(d):
        rng = renpy.random.Random(d * 2654435761)
        idx = FLAT_X_FORCE if FLAT_X_FORCE is not None else (d % len(FLAT_X_VARIANTS))
        img = FLAT_X_VARIANTS[idx % len(FLAT_X_VARIANTS)]
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
            off = (CAL_X_SIZE - size) // 2          # keep a smaller variant centred on the cell
            parts.append((cx + off, cy + off))
            parts.append(Transform(img, size=(size, size), rotate=rot))
        return Composite(*parts), 1.0

image bg_jb_flat = DynamicDisplayable(_jb_flat_displayable)
