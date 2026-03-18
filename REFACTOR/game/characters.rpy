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

## Black screen used for title cards, glitch moments, etc.
image bg_black = "#000000"

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
image jb developer_happy = im.Scale("images/sprites/jb_developer_happy.png", 600, 900)

## Colonel sprites
image colonel normal        = im.Scale("images/sprites/colonel_normal.png",        600, 900)
image colonel angry         = im.Scale("images/sprites/colonel_angry.png",         600, 900)
image colonel disappointed  = im.Scale("images/sprites/colonel_dissapointed.png",  600, 900)
image colonel omniman think = im.Scale("images/sprites/colonel_omniman_think.png", 600, 900)

transform colonel_think_pos:
    zoom 1.1
    xalign 0.5
    yalign 1.0

## Martin sprites
image martin normal  = im.Scale("images/sprites/martin_normal.png", 600, 900)
image martin default = im.Scale("images/sprites/martin_normal.png", 600, 900)
image martin smiling = im.Scale("images/sprites/martin_normal.png", 600, 900)
image martin serious = im.Scale("images/sprites/martin_normal.png", 600, 900)
