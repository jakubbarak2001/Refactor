################################################################################
## REFACTOR - Characters and Image Definitions
## Reads from assets.json to map all sprites and backgrounds
################################################################################

## ---------------------------------------------------------------------------
## Characters
## ---------------------------------------------------------------------------

define jb = Character("JB", color="#e8e8e8", what_color="#e8e8e8")
define colonel = Character("Colonel", color="#4a7aaa", what_color="#c8d8e8")
define martin = Character("Martin", color="#4a8a4a", what_color="#c8e8c8")
define narrator = Character(None, what_color="#e8e8e8")
define system_voice = Character(None, what_color="#00ff41")
define inspector = Character("???", color="#ccaa00", what_color="#e8d878")


## ---------------------------------------------------------------------------
## Background image aliases
## Source paths relative to the Ren'Py project root
## Assets live at: C:\Users\USER\PycharmProjects\Refactor\assets\
## They should be copied (or symlinked) into REFACTOR\game\images\backgrounds\
## ---------------------------------------------------------------------------

image bg_parking_lot         = im.Scale("images/backgrounds/police_parking_lot.jpg", 1920, 1080)
image bg_police_office       = im.Scale("images/backgrounds/police_station_colonel_office.jpg", 1920, 1080)
image bg_police_interior     = im.Scale("images/backgrounds/police_station_interior.jpg", 1920, 1080)
image bg_cafe                = im.Scale("images/backgrounds/cafe.jpg", 1920, 1080)
image bg_random_event        = im.Scale("images/backgrounds/random_event.jpg", 1920, 1080)
image bg_class_intro         = im.Scale("images/backgrounds/class_intro.png", 1920, 1080)

## Black screen used for title cards, glitch moments, etc.
image bg_black = "#000000"

## JB's bedroom — Happy Nation ending
image bg_jb_bedroom      = im.Scale("images/backgrounds/jb_home.jpg", 1920, 1080)
image bg_jb_bedroom_raid = im.Scale("images/backgrounds/jb_home_raid.jpg", 1920, 1080)

## JB's flat — daily home base. Defined as a dynamic Screen in screens_flat.rpy
## (composes the base BG + progression-driven overlays). Keep using `scene bg_jb_flat`.

## BB-flavoured gym — used by activity_gym (universal) and activity_gym_heavy (BB-only)
image bg_bb_gym          = im.Scale("images/backgrounds/bb_gym.jpg", 1920, 1080)

## BH-flavoured grey-market supplier flat — used by activity_nootropics (BH-only)
image bg_bh_supplier     = im.Scale("images/backgrounds/bh_supplier_flat.jpg", 1920, 1080)

## DE-flavoured Czech pub — Kovář's hospoda, used by DE class arc + DE-flavoured social activities
image bg_de_kovar_pub    = im.Scale("images/backgrounds/de_kovar_pub.jpg", 1920, 1080)

## Havana Club — provincial Czech nightclub exterior (used by activity_bouncer → bouncer_night_club)
image bg_havana_club     = im.Scale("images/backgrounds/havana_club_night.jpg", 1920, 1080)

## Hallway — reuses interior until a dedicated asset is added
image bg_police_hallway   = im.Scale("images/backgrounds/police_station_interior.jpg", 1920, 1080)


## ---------------------------------------------------------------------------
## Character sprite aliases
## Sprites live in REFACTOR\game\images\sprites\
## ---------------------------------------------------------------------------

## Character transforms — scale sprites to fit 1920x1080 and position them
transform char_left:
    zoom 0.72
    xalign 0.18
    yalign 1.0

transform char_right:
    zoom 0.72
    xalign 0.82
    yalign 1.0

transform char_center:
    zoom 0.72
    xalign 0.5
    yalign 1.0

## JB sprites
image jb neutral        = im.Scale("images/sprites/jb_neutral.png",         600, 900)
image jb worried        = im.Scale("images/sprites/jb_worried.png",          600, 900)
image jb determined     = im.Scale("images/sprites/jb_determined.png",       600, 900)
image jb bored          = im.Scale("images/sprites/jb_bored.png",            600, 900)
image jb angry          = im.Scale("images/sprites/jb_angry.png",            600, 900)
image jb smirk          = im.Scale("images/sprites/jb_smirk.png",            600, 900)
image jb defeated       = im.Scale("images/sprites/jb_defeated.png",         600, 900)
image jb broken         = im.Scale("images/sprites/jb_broken.png",           600, 900)
image jb developer_happy = im.Scale("images/sprites/jb_developer_happy.png", 600, 900)

## Martin Meeting outfit sprites — wardrobe set by Phase 1 choice
image jb polo           = im.Scale("images/sprites/jb_polo.png",             600, 900)
image jb collar         = im.Scale("images/sprites/jb_collar_shirt.png",     600, 900)
image jb hoodie         = im.Scale("images/sprites/jb_hoodie.png",           600, 900)

## Class portraits — pre-scaled to fit the 500x750 portrait frame on the
## right panel of the class selection screen. Same aspect (~0.667) as the
## existing JB sprites so they can stand in until dedicated DE/BH portraits
## are drawn.
image jb_bb_portrait = im.Scale("images/sprites/jb_bodybuilder.jpg", 500, 750)
image jb_de_portrait = im.Scale("images/sprites/jb_dark_empath.jpg", 500, 750)
image jb_bh_portrait = im.Scale("images/sprites/jb_biohacker.jpg",   500, 750)

## Colonel sprites
image colonel normal        = im.Scale("images/sprites/colonel_normal.png",        600, 900)
image colonel angry         = im.Scale("images/sprites/colonel_angry.png",         600, 900)
image colonel disappointed  = im.Scale("images/sprites/colonel_dissapointed.png",  600, 900)
image colonel omniman think = im.Scale("images/sprites/colonel_omniman_think.png", 600, 900)

transform colonel_think_pos:
    zoom 1.1
    xalign 0.5
    yalign 1.0

## Difficulty selection portrait images — portrait orientation ~420x630
image diff_easy   = im.Scale("images/pictures/easy_difficulty_pic.png",   420, 630)
image diff_hard   = im.Scale("images/pictures/hard_difficulty_pic.png",   420, 630)
image diff_insane = im.Scale("images/pictures/insane_difficulty_pic.png", 420, 630)
image diff_ultra  = im.Scale("images/pictures/ultra_difficulty_pic.png",  420, 630)

## Martin sprites — source is square, scale proportionally to match 900px height
image martin normal  = im.Scale("images/sprites/martin_normal.png", 600, 900)
image martin default = im.Scale("images/sprites/martin_normal.png", 600, 900)
image martin smiling = im.Scale("images/sprites/martin_normal.png", 600, 900)
image martin serious = im.Scale("images/sprites/martin_normal.png", 600, 900)

## Inspector sprites (GIBS — Happy Nation ending)
image inspector neutral = im.Scale("images/sprites/inspector_neutral.png", 600, 900)
