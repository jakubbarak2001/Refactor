# screens_system.rpy -- Ren'Py shell UI: say / choice / input / navigation /
# main_menu / game_menu / save / load / preferences / history / help / confirm /
# skip, plus the dossier shell bars. Split out of screens.rpy to keep gameplay
# UI separate. The 'init offset = -1' below is carried verbatim from the
# original file so base styles still initialize before the gameplay screens.

################################################################################
## Initialization  (original screens.rpy content below)
################################################################################

init offset = -1


################################################################################
## Styles
################################################################################

style default:
    properties gui.text_properties()
    language gui.language

style input:
    properties gui.text_properties("input", accent=True)
    adjust_spacing False

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    hover_underline True

style gui_text:
    properties gui.text_properties("interface")


style button:
    properties gui.button_properties("button")

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5


style label_text is gui_text:
    properties gui.text_properties("label", accent=True)

style prompt_text is gui_text:
    properties gui.text_properties("prompt")


style bar:
    ysize gui.bar_size
    left_bar Frame("gui/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    ysize gui.slider_size
    base_bar Frame("gui/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/slider/horizontal_[prefix_]thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"


style frame:
    padding gui.frame_borders.padding
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)



################################################################################
## In-game screens
################################################################################


## Say screen ##################################################################
##
## The say screen is used to display dialogue to the player. It takes two
## parameters, who and what, which are the name of the speaking character and
## the text to be displayed, respectively. (The who parameter can be None if no
## name is given.)
##
## This screen must create a text displayable with id "what", as Ren'Py uses
## this to manage text display. It can also create displayables with id "who"
## and id "window" to apply style properties.
##
## https://www.renpy.org/doc/html/screen_special.html#say

screen say(who, what):

    ## Canonical Ren'Py say screen — `window id="window"` and
    ## `text what id="what"` are produced by `say_dossier` at the same
    ## screen-root depth they used to occupy here, preserving the
    ## widget-tree-shape invariant. The previous
    ## `if not renpy.get_screen("choice"):` conditional wrapping (since
    ## removed) changed that shape based on runtime state and caused
    ## modal-stack corruption (gym → card-offer → pause crash with
    ## "ui.interact called with non-empty widget/layer stack"). Do not
    ## re-introduce a conditional that omits the window wrapper.
    ##
    ## The dialogue window will visually overlap menu choices unless an
    ## explicit `window hide` runs before each `menu:` statement. That
    ## trade-off is accepted to keep play crash-free.
    use say_dossier(who, what)

    ## Idle click-to-continue nudge. The say screen re-shows per line, so
    ## the timer restarts each line — it only fires on genuine inactivity
    ## and resets the moment the player advances. Lives here (not in the
    ## use'd say_dossier) so SetScreenVariable hits this screen's own scope.
    default _ctc_idle = False
    timer 4.0 action SetScreenVariable("_ctc_idle", True)
    showif _ctc_idle:
        frame:
            background Frame("#000000bb", 6, 6)
            padding (18, 7)
            xalign 0.5
            yalign 1.0
            yoffset -300
            at ctc_idle_bob
            text "press space to continue":
                style "mm_status"
                size 18
                color "#eaeaea"
                outlines [(2, "#000000", 0, 0)]


## Make the namebox available for styling through the Character object.
init python:
    config.character_id_prefixes.append('namebox')

style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label


style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    yminimum gui.textbox_height
    ymaximum 320
    bottom_margin 50

    background Frame("#0d0d1aee", 8, 8)
    padding (60, 30, 60, 30)

style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height

    background Frame("gui/namebox.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding

style say_label:
    properties gui.text_properties("name", accent=True)
    xalign gui.name_xalign
    yalign 0.5

style say_dialogue:
    properties gui.text_properties("dialogue")

    xpos gui.dialogue_xpos
    xsize gui.dialogue_width

    adjust_spacing False


## ---------------------------------------------------------------------------
## Dossier HUD — top + bottom 36px case-file strips. Shown only during
## opted-in labels via `show screen dossier_hud`. Mirrors the main menu's
## top/bottom bars (mm_status font/size/color) so the player's eye
## recognizes the same chrome from the title screen.
## zorder 90 sits above stats_bar (100? — stats_bar is hidden in the
## prologue anyway) and below the choice overlay (250).
## ---------------------------------------------------------------------------
screen dossier_hud():
    zorder 90

    ## Top strip
    frame:
        xfill True
        ysize 36
        ypos 0
        background Solid(DOSSIER_BG_BAR)
        padding (0, 0)
        has fixed

        text "CASE FILE — JB  //  ARC I — THE INCIDENT":
            style "mm_status"
            xpos 28
            yalign 0.5

        if dossier_beat_time != "" or dossier_beat_slug != "":
            text "[dossier_beat_time]  //  [dossier_beat_slug]":
                style "mm_status"
                xalign 1.0
                xoffset -28
                yalign 0.5

    ## Bottom strip
    frame:
        xfill True
        ysize 36
        yalign 1.0
        background Solid(DOSSIER_BG_BAR)
        padding (0, 0)
        has fixed

        text "STATE POLICE  //  INTERNAL USE ONLY":
            style "mm_status"
            xpos 28
            yalign 0.5

        text "[[space] advance   [[esc] menu":
            style "mm_status"
            xalign 1.0
            xoffset -28
            yalign 0.5


## ---------------------------------------------------------------------------
## say_dossier — canonical dialogue window. `screen say` unconditionally
## delegates here, so this is what every Character() line in the game
## renders through. Preserves the load-bearing widget IDs ("window",
## "what") that the Ren'Py modal-stack bookkeeping relies on — see the
## comment in `screen say` above about the prior crash. Do not
## restructure without re-testing menu/choice interactions.
##
## Geometry: caps height at `ymaximum 230` (fits ~3 lines of dialogue,
## the soft writing constraint). 67% alpha backing lets the BG bleed
## through. Beat metadata lives in the top dossier_hud strip — NOT
## here — so it stays fixed when the strip is on screen, and is silent
## otherwise. Per-character namebox color comes from `Character(color=)`.
## ---------------------------------------------------------------------------
transform ctc_idle_bob:
    alpha 0.0 yoffset 0
    easein 0.45 alpha 0.9
    block:
        easeout 1.0 yoffset -5
        easein 1.0 yoffset 0
        repeat


screen say_dossier(who, what):
    ## Uppercase the speaker name in Python — text-widget [var!u]
    ## substitution doesn't apply to screen parameters reliably, which
    ## was rendering "[who!u]" as literal text.
    $ _dossier_who = who.upper() if who else ""

    window:
        id "window"
        background Frame(DOSSIER_BG_SOLID, 0, 0)
        padding (0, 0, 0, 0)
        xalign 0.5
        xfill True
        yalign gui.textbox_yalign
        ## Window auto-sizes to its content (1–3 body lines + reserved
        ## 28px name slot + padding). ymaximum 260 caps it so a runaway
        ## line can't blow past the quick_menu strip.
        yminimum 0
        ymaximum 260
        bottom_margin 44

        hbox:
            spacing 0
            xfill True

            ## 4px rust-red left spine — frame with yfill so it stretches
            ## to the hbox's natural height. (`add` doesn't accept yfill;
            ## a frame with a Solid background does.)
            frame:
                xsize 4
                yfill True
                background Solid(DOSSIER_RED)
                padding (0, 0)

            ## Inner content area. Tight vertical padding so the window
            ## stays short; horizontal padding mirrors the original say
            ## window (60) minus the 4px the spine ate.
            frame:
                background None
                padding (56, 14, 60, 16)
                xfill True

                vbox:
                    spacing 6
                    xfill True

                    ## Name slot — always 28px tall whether a speaker is
                    ## present or not. Reserving the slot keeps the body
                    ## text's Y position consistent between narrator and
                    ## character lines (the user-requested invariant).
                    ## When narrator: just blank space. When character:
                    ## name + 1px slate underline.
                    fixed:
                        xfill True
                        ysize 28

                        if who is not None:
                            vbox:
                                spacing 3
                                xalign 0.0
                                yalign 0.0

                                ## No inline `color` — let each Character(color=...)
                                ## drive the namebox tint (colonel blue, martin
                                ## green, inspector yellow, jb white). The slate
                                ## underline below + RobotoMono uppercase keep
                                ## the dossier vocabulary regardless of color.
                                text _dossier_who id "who":
                                    font DOSSIER_FONT
                                    size 20
                                    kerning 2
                                    outlines [(1, "#000000aa", 0, 0)]

                                frame:
                                    xsize 140
                                    ysize 1
                                    background Solid(DOSSIER_INK_DIM)
                                    padding (0, 0)

                    ## Body — preserve `id "what"` for Character() styling.
                    text what id "what"


## Input screen ################################################################
##
## This screen is used to display renpy.input. The prompt parameter is used to
## pass a text prompt in.
##
## This screen must create an input displayable with id "input" to accept the
## various input parameters.
##
## https://www.renpy.org/doc/html/screen_special.html#input

screen input(prompt):
    style_prefix "input"

    window:

        vbox:
            xanchor gui.dialogue_text_xalign
            xpos gui.dialogue_xpos
            xsize gui.dialogue_width
            ypos gui.dialogue_ypos

            text prompt style "input_prompt"
            input id "input"

style input_prompt is default

style input_prompt:
    xalign gui.dialogue_text_xalign
    properties gui.text_properties("input_prompt")

style input:
    xalign gui.dialogue_text_xalign
    xmaximum gui.dialogue_width


## Choice screen ###############################################################
##
## This screen is used to display the in-game choices presented by the menu
## statement. The one parameter, items, is a list of objects, each with caption
## and action fields.
##
## https://www.renpy.org/doc/html/screen_special.html#choice

screen choice(items):
    ## Each option = [class-color left strip | dark button with hover tint].
    ## The strip ties the choice into the rest of the game's visual system
    ## (stats bar underline, class-color frame in battle screen) so menus
    ## stop reading as bare default Ren'Py UI.
    ## zorder 250 keeps the menu above the lingering say-window. Combined
    ## with the conditional hide on the say screen below, the textbox stays
    ## out of the way during menus so choices have the full bottom band.
    zorder 250

    python:
        _choice_accent = class_accent_color(stats.player_class) if stats else "#888888"

    vbox:
        xalign 0.5
        yalign 0.88
        spacing 14

        for i in items:
            hbox:
                spacing 0
                xalign 0.5

                ## Left-edge accent strip — pulses class color on hover via a
                ## button's hover_background. Uses the textbutton's hover state
                ## by piggybacking the row layout rather than a separate widget.
                frame:
                    xsize 5
                    ysize 64
                    background Solid(_choice_accent)

                textbutton i.caption:
                    action i.action
                    style "choice_button"


style choice_button is button
style choice_button_text is button_text

style choice_button:
    properties gui.button_properties("choice_button")
    xminimum 900
    xmaximum 1200
    ysize 64
    background Frame("#0d0d11ee", 0, 0)
    hover_background Frame("#1a0000ee", 0, 0)
    padding (28, 16)

style choice_button_text:
    properties gui.text_properties("choice_button")
    color "#c8c8d8"
    hover_color "#ff6644"
    size 22
    bold True
    font "fonts/RobotoMono-Regular.ttf"
    xalign 0.0


## Quick Menu screen ###########################################################
##
## The quick menu is displayed in-game to provide easy access to the out-of-game
## menus.

screen quick_menu():

    ## Ensure this appears on top of other screens.
    zorder 100

    if quick_menu:

        frame:
            style "quick_menu_frame"

            hbox:
                style_prefix "quick"
                style "quick_menu"

                textbutton _("back") action Rollback()
                textbutton _("history") action ShowMenu('history')
                textbutton _("skip") action Skip() alternate Skip(fast=True, confirm=True)
                textbutton _("auto") action Preference("auto-forward", "toggle")
                textbutton _("save") action ShowMenu('save')
                textbutton _("q.save") action QuickSave()
                textbutton _("q.load") action QuickLoad()
                textbutton _("settings") action ShowMenu('preferences')


## This code ensures that the quick_menu screen is displayed in-game, whenever
## the player has not explicitly hidden the interface.
init python:
    config.overlay_screens.append("quick_menu")

default quick_menu = True

style quick_menu is hbox
style quick_menu_frame is frame
style quick_button is default
style quick_button_text is button_text

style quick_menu_frame:
    xalign 0.5
    yalign 1.0
    background Solid("#0a0a0acc")
    padding (16, 6)

style quick_menu:
    spacing 18

style quick_button:
    padding (8, 2)

style quick_button_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#667788"
    hover_color "#ff4422"
    selected_color "#cc2200"
    insensitive_color "#334455"
    size 18
    kerning 1


################################################################################
## Main and Game Menu Screens
################################################################################

## Navigation screen ###########################################################
##
## This screen is included in the main and game menus, and provides navigation
## to other menus, and to start the game.

screen navigation():

    vbox:
        style_prefix "navigation"

        xpos 90
        ## From the main menu the nav is a compact block tucked just under the
        ## title; in-game it stays high to fit the full pause list.
        ypos (350 if main_menu else 230)
        yanchor 0.0

        spacing gui.navigation_spacing

        ## Reached from the main menu, the main menu IS the navigation — so this
        ## sidebar only offers a way back, instead of re-listing every main-menu
        ## command under different labels. The full pause-menu sidebar below is
        ## the in-game case, where no other navigation is on screen.
        if main_menu:

            ## Help has no entry on the themed main menu, so surface it here —
            ## otherwise it is unreachable until the player starts a game.
            if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):

                textbutton _("►  help") action ShowMenu("help")

            textbutton _("►  back to main menu") action Return()

        else:

            textbutton _("►  history") action ShowMenu("history")

            textbutton _("►  save") action ShowMenu("save")

            textbutton _("►  load") action ShowMenu("load")

            textbutton _("►  settings") action ShowMenu("preferences")

            if stats is not None:

                textbutton _("►  trophies") action [Hide("phone_screen"), ShowMenu("trophies_menu")]

            if _in_replay:

                textbutton _("►  end replay") action EndReplay(confirm=True)

            else:

                textbutton _("►  main menu") action MainMenu()

            textbutton _("►  about") action ShowMenu("about")

            if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):

                ## Help isn't necessary or relevant to mobile devices.
                textbutton _("►  help") action ShowMenu("help")

            if renpy.variant("pc"):

                textbutton _("►  quit") action Quit(confirm=True)

            textbutton _("►  back to game") action Return()



style navigation_button is mm_button
style navigation_button_text is mm_button_text

style navigation_button:
    size_group "navigation"
    xsize 360

style navigation_button_text:
    size 26


## Main Menu screen ############################################################
##
## Used to display the main menu when Ren'Py starts.
##
## https://www.renpy.org/doc/html/screen_special.html#main-menu

screen main_menu():

    ## Replaces any other menu screen when shown.
    tag menu

    ## Full-bleed looping video stays the hero — chrome sits on top.
    add gui.main_menu_background

    ## Institutional case-file strips top and bottom.
    use main_menu_top_bar
    use main_menu_bottom_bar

    ## Vertical rust-red accent bar — case-file tab spine anchoring title + nav.
    ## Runs from title top (y=272) to just above the bottom status strip (y=1008).
    add Solid("#cc2200"):
        xpos 72
        ypos 310
        xsize 4
        ysize 566
        at mm_fade_in

    ## Title wordmark — pinned at y=272 to preserve the original placement.
    text "REKURZE":
        style "mm_title"
        xpos 90
        ypos 272
        at mm_fade_in

    ## Navigation column — case-file commands.
    use main_menu_navigation


screen dossier_top_bar(left_text="REKURZE  //  case-file-jb", right_text=None):
    frame:
        xfill True
        ysize 36
        ypos 0
        background Solid("#0a0a0acc")
        padding (0, 0)
        has fixed

        text left_text:
            style "mm_status"
            xpos 28
            yalign 0.5

        text (right_text if right_text is not None else "v[config.version]  //  northern bohemia"):
            style "mm_status"
            xalign 1.0
            xoffset -28
            yalign 0.5


screen dossier_bottom_bar(left_text="STATE POLICE  //  INTERNAL USE ONLY", right_text="[[esc] back   [[enter] confirm"):
    frame:
        xfill True
        ysize 36
        yalign 1.0
        background Solid("#0a0a0acc")
        padding (0, 0)
        has fixed

        text left_text:
            style "mm_status"
            xpos 28
            yalign 0.5

        text right_text:
            style "mm_status"
            xalign 1.0
            xoffset -28
            yalign 0.5


screen main_menu_top_bar():
    use dossier_top_bar


screen main_menu_bottom_bar():
    use dossier_bottom_bar(right_text="[[esc] exit   [[enter] go")


screen main_menu_navigation():
    ## Per-button hover sound — Play action fires reliably on every focus-enter,
    ## unlike style-level `hover_sound` which can be swallowed by mouse-hover paths.
    $ _mm_hover_sfx = Play("sound", "audio/sfx/ui_hover.wav")

    vbox:
        xpos 90
        ypos 470
        yanchor 0.0
        spacing 8
        at mm_fade_in

        textbutton _("►  new investigation") style "mm_button" action Start("mm_start_fade") hovered _mm_hover_sfx

        if renpy.newest_slot() is not None:
            textbutton _("►  continue") style "mm_button" action FileLoad(renpy.newest_slot()) hovered _mm_hover_sfx

        textbutton _("►  case archive") style "mm_button" action ShowMenu("load") hovered _mm_hover_sfx

        if stats is not None:
            textbutton _("►  trophies") style "mm_button" action [Hide("phone_screen"), ShowMenu("trophies_menu")] hovered _mm_hover_sfx

        textbutton _("►  settings") style "mm_button" action ShowMenu("preferences") hovered _mm_hover_sfx

        textbutton _("►  about") style "mm_button" action ShowMenu("about") hovered _mm_hover_sfx

        if renpy.variant("pc"):
            textbutton _("►  exit") style "mm_button" action Quit(confirm=True) hovered _mm_hover_sfx


transform mm_fade_in:
    alpha 0.0
    ease 0.6 alpha 1.0


## Polish entry point: brief freeze, music fadeout, fade-to-black, then hand off
## to the regular `start` label (which begins on bg_black + fades in its own music).
label mm_start_fade:
    pause 0.2
    stop music fadeout 1.0
    scene bg_black with Dissolve(0.6)
    pause 0.4
    jump start


style mm_title is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#e8e8e8"
    size 120
    kerning 4
    outlines [(3, "#000000cc", 0, 0)]

style mm_status is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#667788"
    size 16
    outlines [(1, "#000000aa", 0, 0)]

style mm_button is button:
    background None
    hover_background Frame("#1a0000dd", 8, 4)
    padding (12, 6)
    xsize 560
    activate_sound "audio/sfx/ui_click.mp3"

style mm_button_text is button_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    hover_color "#ff4422"
    insensitive_color "#334455"
    size 34
    outlines [(2, "#000000cc", 0, 0)]


style dossier_section_label is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#cc2200"
    size 22
    kerning 2

style dossier_subtitle is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#667788"
    size 18
    kerning 1

style dossier_body_text is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    size 22

style dossier_body_text_dim is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#667788"
    size 18

style dossier_pref_button is mm_button:
    background None
    hover_background Frame("#1a0000dd", 4, 4)
    selected_background Frame("#1a0000dd", 4, 4)
    padding (10, 4)
    xsize 320
    activate_sound "audio/sfx/ui_click.mp3"

style dossier_pref_button_text is mm_button_text:
    size 22
    color "#8899aa"
    hover_color "#ff4422"
    selected_color "#cc2200"
    insensitive_color "#334455"

style dossier_slot_button is button:
    background Frame("#0d0d11ee", 4, 4)
    hover_background Frame("#1a0000dd", 4, 4)
    padding (12, 12)
    activate_sound "audio/sfx/ui_click.mp3"

style dossier_slot_time_text is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#667788"
    size 16

style dossier_slot_name_text is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    size 18

style dossier_page_button is mm_button:
    background None
    hover_background Frame("#1a0000dd", 4, 4)
    selected_background Frame("#1a0000dd", 4, 4)
    padding (10, 4)
    xsize None
    activate_sound "audio/sfx/ui_click.mp3"

style dossier_page_button_text is mm_button_text:
    size 18
    color "#8899aa"
    hover_color "#ff4422"
    selected_color "#cc2200"

style dossier_help_label is gui_label:
    xsize 280
    right_padding 24

style dossier_help_label_text is gui_label_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#cc2200"
    size 22
    kerning 2
    xalign 1.0
    textalign 1.0

style dossier_help_text is gui_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    size 22
    xsize 1000


style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text

style main_menu_frame:
    xsize 420
    yfill True

style main_menu_vbox:
    xalign 1.0
    xoffset -30
    xmaximum 1200
    yalign 1.0
    yoffset -30

style main_menu_text:
    properties gui.text_properties("main_menu", accent=True)

style main_menu_title:
    properties gui.text_properties("title")

style main_menu_version:
    properties gui.text_properties("version")


## Game Menu screen ############################################################
##
## This lays out the basic common structure of a game menu screen. It's called
## with the screen title, and displays the background, title, and navigation.
##
## The scroll parameter can be None, or one of "viewport" or "vpgrid".
## This screen is intended to be used with one or more children, which are
## transcluded (placed) inside it.

screen game_menu(title, scroll=None, yinitial=0.0, spacing=0):

    style_prefix "game_menu"

    if main_menu:
        add gui.main_menu_background
    else:
        add Solid("#0a0a0aee")

    use dossier_top_bar(left_text="REKURZE  //  case-file: " + title.lower())
    use dossier_bottom_bar()

    ## From the main menu the spine frames just the title + compact nav block;
    ## in-game it runs long beside the full pause-menu sidebar.
    add Solid("#cc2200"):
        xpos 72
        ypos (260 if main_menu else 130)
        xsize 4
        ysize (200 if main_menu else 680)
        at mm_fade_in

    text title.upper():
        style "mm_title"
        size 64
        kerning 3
        xpos 90
        ypos (240 if main_menu else 120)
        at mm_fade_in

    use navigation

    frame:
        style "game_menu_outer_frame"

        if scroll == "viewport":

            viewport:
                yinitial yinitial
                scrollbars "vertical"
                mousewheel True
                draggable True
                pagekeys True

                side_yfill True

                vbox:
                    spacing spacing

                    transclude

        elif scroll == "vpgrid":

            vpgrid:
                cols 1
                yinitial yinitial

                scrollbars "vertical"
                mousewheel True
                draggable True
                pagekeys True

                side_yfill True

                spacing spacing

                transclude

        else:

            transclude

    if main_menu:
        key "game_menu" action ShowMenu("main_menu")


style game_menu_outer_frame is empty
style game_menu_navigation_frame is empty
style game_menu_content_frame is empty
style game_menu_viewport is gui_viewport
style game_menu_side is gui_side
style game_menu_scrollbar is gui_vscrollbar

style game_menu_label is gui_label
style game_menu_label_text is gui_label_text

style game_menu_outer_frame:
    xpos 480
    ypos 235
    xsize 1380
    ysize 800
    background None
    padding (0, 0)

style game_menu_navigation_frame:
    xsize 360
    yfill False

style game_menu_content_frame:
    padding (0, 0)

style game_menu_viewport:
    xsize 1380

style game_menu_vscrollbar:
    unscrollable gui.unscrollable
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")
    xsize 6

style game_menu_side:
    spacing 12

## About screen ################################################################
##
## This screen gives credit and copyright information about the game and Ren'Py.
##
## There's nothing special about this screen, and hence it also serves as an
## example of how to make a custom screen.

screen about():

    tag menu

    use game_menu(_("About"), scroll="viewport"):

        vbox:
            spacing 24
            xsize 1320

            frame:
                background Frame("#0d0d11ee", 4, 4)
                padding (28, 22)
                xfill True

                vbox:
                    spacing 8
                    text "CASE FILE //" style "dossier_section_label"
                    null height 6
                    text "[config.name!t]":
                        font "fonts/RobotoMono-Regular.ttf"
                        color "#e8e8e8"
                        size 44
                        kerning 2
                    text "Version [config.version!t]":
                        font "fonts/RobotoMono-Regular.ttf"
                        color "#c0d0e0"
                        size 22
                    text "Northern Bohemia  ·  State Police  ·  Internal Use Only":
                        font "fonts/RobotoMono-Regular.ttf"
                        color "#667788"
                        size 18

            if gui.about:

                frame:
                    background Frame("#0d0d11ee", 4, 4)
                    padding (28, 22)
                    xfill True

                    vbox:
                        spacing 8
                        text "SUBJECT //" style "dossier_section_label"
                        null height 6
                        text "[gui.about!t]":
                            font "fonts/RobotoMono-Regular.ttf"
                            color "#c0d0e0"
                            size 20

            frame:
                background Frame("#0d0d11ee", 4, 4)
                padding (28, 22)
                xfill True

                vbox:
                    spacing 8
                    text "TOOLING //" style "dossier_section_label"
                    null height 6
                    text _("Made with {a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only]"):
                        font "fonts/RobotoMono-Regular.ttf"
                        color "#c0d0e0"
                        size 20
                    text "[renpy.license!t]":
                        font "fonts/RobotoMono-Regular.ttf"
                        color "#667788"
                        size 16


style about_label is gui_label
style about_label_text is gui_label_text
style about_text is gui_text


## Load and Save screens #######################################################
##
## These screens are responsible for letting the player save the game and load
## it again. Since they share nearly everything in common, both are implemented
## in terms of a third screen, file_slots.
##
## https://www.renpy.org/doc/html/screen_special.html#save https://
## www.renpy.org/doc/html/screen_special.html#load

screen save():

    tag menu

    use file_slots(_("Save"))


screen load():

    tag menu

    use file_slots(_("Load"))


screen file_slots(title):

    default page_name_value = FilePageNameInputValue(pattern=_("FILE :: {}"), auto=_("AUTO-LOG"), quick=_("QUICK-CACHE"))

    use game_menu(title):

        fixed:

            ## This ensures the input will get the enter event before any of the
            ## buttons do.
            order_reverse True

            ## The page name, which can be edited by clicking on a button.
            button:
                style "page_label"

                key_events True
                xalign 0.5
                ypos 0
                action page_name_value.Toggle()

                input:
                    style "page_label_text"
                    value page_name_value

            ## The grid of file slots.
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                xalign 0.5
                ypos 56

                spacing gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):

                    $ slot = i + 1

                    button:
                        action FileAction(slot)

                        has vbox

                        add FileScreenshot(slot) xalign 0.5

                        null height 6

                        text FileTime(slot, format=_("%Y-%m-%d  //  %H:%M"), empty=_("[[ empty slot ]")):
                            style "slot_time_text"

                        text FileSaveName(slot):
                            style "slot_name_text"

                        key "save_delete" action FileDelete(slot)

            ## Buttons to access other pages.
            vbox:
                style_prefix "page"

                xalign 0.5
                yalign 1.0

                frame:
                    background Solid("#0a0a0a88")
                    padding (16, 8)
                    xalign 0.5

                    hbox:
                        xalign 0.5

                        spacing 6

                        textbutton _("[[ prev ]") action FilePagePrevious()
                        key "save_page_prev" action FilePagePrevious()

                        if config.has_autosave:
                            textbutton _("[[ A ]") action FilePage("auto")

                        if config.has_quicksave:
                            textbutton _("[[ Q ]") action FilePage("quick")

                        ## range(1, 10) gives the numbers from 1 to 9.
                        for page in range(1, 10):
                            textbutton "[[ [page] ]" action FilePage(page)

                        textbutton _("[[ next ]") action FilePageNext()
                        key "save_page_next" action FilePageNext()

                null height 8

                if config.has_sync:
                    if CurrentScreenName() == "save":
                        textbutton _("►  upload sync"):
                            action UploadSync()
                            xalign 0.5
                    else:
                        textbutton _("►  download sync"):
                            action DownloadSync()
                            xalign 0.5


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is dossier_page_button
style page_button_text is dossier_page_button_text

style slot_button is dossier_slot_button
style slot_button_text is dossier_slot_name_text
style slot_time_text is dossier_slot_time_text
style slot_name_text is dossier_slot_name_text

style page_label:
    xpadding 28
    ypadding 6
    xalign 0.5

style page_label_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    hover_color "#ff4422"
    size 22
    kerning 2
    textalign 0.5
    layout "subtitle"
    caret Solid("#cc2200")


## Preferences screen ##########################################################
##
## The preferences screen allows the player to configure the game to better suit
## themselves.
##
## https://www.renpy.org/doc/html/screen_special.html#preferences

screen preferences():

    tag menu

    use game_menu(_("Settings"), scroll="viewport"):

        vbox:
            spacing 14

            hbox:
                box_wrap True
                spacing 60

                if renpy.variant("pc") or renpy.variant("web"):

                    vbox:
                        style_prefix "radio"
                        spacing 4
                        text "DISPLAY //" style "dossier_section_label"
                        null height 6
                        textbutton _("Window") action Preference("display", "window")
                        textbutton _("Fullscreen") action Preference("display", "fullscreen")

                vbox:
                    style_prefix "check"
                    spacing 4
                    text "SKIP //" style "dossier_section_label"
                    null height 6
                    textbutton _("Unseen Text") action Preference("skip", "toggle")
                    textbutton _("After Choices") action Preference("after choices", "toggle")
                    textbutton _("Transitions") action InvertSelected(Preference("transitions", "toggle"))

            null height (3 * gui.pref_spacing)

            hbox:
                style_prefix "slider"
                box_wrap True
                spacing 60

                vbox:
                    spacing 6
                    text "PLAYBACK //" style "dossier_section_label"
                    null height 6

                    text "text speed" style "dossier_subtitle"
                    bar value Preference("text speed")

                    null height 8

                    text "auto-forward time" style "dossier_subtitle"
                    bar value Preference("auto-forward time")

                vbox:
                    spacing 6
                    text "AUDIO //" style "dossier_section_label"
                    null height 6

                    if config.has_music:
                        text "music volume" style "dossier_subtitle"

                        hbox:
                            bar value Preference("music volume")

                    if config.has_sound:

                        text "sound volume" style "dossier_subtitle"

                        hbox:
                            spacing 12
                            bar value Preference("sound volume")

                            if config.sample_sound:
                                textbutton _("[[ test ]") action Play("sound", config.sample_sound)


                    if config.has_voice:
                        text "voice volume" style "dossier_subtitle"

                        hbox:
                            spacing 12
                            bar value Preference("voice volume")

                            if config.sample_voice:
                                textbutton _("[[ test ]") action Play("voice", config.sample_voice)

                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing

                        textbutton _("►  mute all"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"


style pref_label is gui_label
style pref_label_text is gui_label_text
style pref_vbox is vbox

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is dossier_pref_button
style radio_button_text is dossier_pref_button_text
style radio_vbox is pref_vbox

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is dossier_pref_button
style check_button_text is dossier_pref_button_text
style check_vbox is pref_vbox

style slider_label is pref_label
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is dossier_pref_button
style slider_button_text is dossier_pref_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is dossier_pref_button
style mute_all_button_text is dossier_pref_button_text

style pref_label:
    top_margin gui.pref_spacing
    bottom_margin 3

style pref_label_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#667788"
    size 22
    yalign 1.0

style pref_vbox:
    xsize 360

style radio_vbox:
    spacing 4

style check_vbox:
    spacing 4

style slider_slider:
    xsize 480
    ysize 20
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")
    thumb_offset 0

style slider_button:
    yalign 0.5
    left_margin 12

style slider_vbox:
    xsize 580
    spacing 4

style bar:
    ysize 20
    left_bar Solid("#cc2200")
    right_bar Solid("#1a2a3a")
    thumb None
    bar_resizing True

style scrollbar:
    ysize 6
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")

style vscrollbar:
    xsize 6
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")


## History screen ##############################################################
##
## This is a screen that displays the dialogue history to the player. While
## there isn't anything special about this screen, it does have to access the
## dialogue history stored in _history_list.
##
## https://www.renpy.org/doc/html/history.html

screen history():

    tag menu

    ## Avoid predicting this screen, as it can be very large.
    predict False

    use game_menu(_("History"), scroll=("vpgrid" if gui.history_height else "viewport"), yinitial=1.0, spacing=gui.history_spacing):

        style_prefix "history"

        for h in _history_list:

            window:

                ## This lays things out properly if history_height is None.
                has fixed:
                    yfit True

                if h.who:

                    label h.who:
                        style "history_name"
                        substitute False

                        ## Take the color of the who text from the Character, if
                        ## set.
                        if "color" in h.who_args:
                            text_color h.who_args["color"]

                $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                text what:
                    substitute False

        if not _history_list:
            label _("The dialogue history is empty.")


## This determines what tags are allowed to be displayed on the history screen.

define gui.history_allow_tags = { "alt", "noalt", "rt", "rb", "art" }


style history_window is empty

style history_name is gui_label
style history_name_text is gui_label_text
style history_text is gui_text

style history_label is gui_label
style history_label_text is gui_label_text

style history_window:
    xfill True
    ysize gui.history_height

style history_name:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text:
    min_width gui.history_name_width
    textalign gui.history_name_xalign
    font "fonts/RobotoMono-Regular.ttf"
    color "#cc2200"
    size 20
    kerning 2

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    textalign gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    size 20

style history_label:
    xfill True

style history_label_text:
    xalign 0.5


## Help screen #################################################################
##
## A screen that gives information about key and mouse bindings. It uses other
## screens (keyboard_help, mouse_help, and gamepad_help) to display the actual
## help.

screen help():

    tag menu

    default device = "keyboard"

    use game_menu(_("Help"), scroll="viewport"):

        style_prefix "help"

        vbox:
            spacing 18

            text "INPUT DEVICE //" style "dossier_section_label"

            hbox:
                spacing 32

                textbutton ("▶  keyboard" if device == "keyboard" else "►  keyboard"):
                    action SetScreenVariable("device", "keyboard")
                textbutton ("▶  mouse" if device == "mouse" else "►  mouse"):
                    action SetScreenVariable("device", "mouse")

                if GamepadExists():
                    textbutton ("▶  gamepad" if device == "gamepad" else "►  gamepad"):
                        action SetScreenVariable("device", "gamepad")

            null height 12

            text "BINDINGS //" style "dossier_section_label"

            null height 4

            if device == "keyboard":
                use keyboard_help
            elif device == "mouse":
                use mouse_help
            elif device == "gamepad":
                use gamepad_help


screen keyboard_help():

    hbox:
        label _("Enter")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Space")
        text _("Advances dialogue without selecting choices.")

    hbox:
        label _("Arrow Keys")
        text _("Navigate the interface.")

    hbox:
        label _("Escape")
        text _("Accesses the game menu.")

    hbox:
        label _("Ctrl")
        text _("Skips dialogue while held down.")

    hbox:
        label _("Tab")
        text _("Toggles dialogue skipping.")

    hbox:
        label _("Page Up")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Page Down")
        text _("Rolls forward to later dialogue.")

    hbox:
        label "H"
        text _("Hides the user interface.")

    hbox:
        label "S"
        text _("Takes a screenshot.")

    hbox:
        label "V"
        text _("Toggles assistive {a=https://www.renpy.org/l/voicing}self-voicing{/a}.")

    hbox:
        label "Shift+A"
        text _("Opens the accessibility menu.")


screen mouse_help():

    hbox:
        label _("Left Click")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Middle Click")
        text _("Hides the user interface.")

    hbox:
        label _("Right Click")
        text _("Accesses the game menu.")

    hbox:
        label _("Mouse Wheel Up")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Mouse Wheel Down")
        text _("Rolls forward to later dialogue.")


screen gamepad_help():

    hbox:
        label _("Right Trigger\nA/Bottom Button")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Left Trigger\nLeft Shoulder")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Right Shoulder")
        text _("Rolls forward to later dialogue.")

    hbox:
        label _("D-Pad, Sticks")
        text _("Navigate the interface.")

    hbox:
        label _("Start, Guide, B/Right Button")
        text _("Accesses the game menu.")

    hbox:
        label _("Y/Top Button")
        text _("Hides the user interface.")

    textbutton _("Calibrate") action GamepadCalibrate()


style help_button is dossier_pref_button
style help_button_text is dossier_pref_button_text
style help_label is gui_label
style help_label_text is gui_label_text
style help_text is gui_text

style help_button:
    xmargin 0

style help_button_text:
    size 22

style help_label:
    xsize 280
    right_padding 24

style help_label_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#cc2200"
    size 22
    kerning 2
    xalign 1.0
    textalign 1.0

style help_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    size 22



################################################################################
## Additional screens
################################################################################


## Confirm screen ##############################################################
##
## The confirm screen is called when Ren'Py wants to ask the player a yes or no
## question.
##
## https://www.renpy.org/doc/html/screen_special.html#confirm

screen confirm(message, yes_action, no_action):

    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"

    add Solid("#000000bb")

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 28

            text "►  CONFIRMATION":
                style "confirm_header"
                xalign 0.5

            null height 8

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            null height 12

            hbox:
                xalign 0.5
                spacing 80

                textbutton _("►  yes") action yes_action
                textbutton _("►  no") action no_action

    ## Right-click and escape answer "no".
    key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is mm_button
style confirm_button_text is mm_button_text
style confirm_header is gui_text

style confirm_frame:
    background Frame("#0d0d11ee", 4, 4)
    padding (60, 48, 60, 48)
    xalign .5
    yalign .5

style confirm_header:
    font "fonts/RobotoMono-Regular.ttf"
    color "#cc2200"
    size 22
    kerning 3

style confirm_prompt_text:
    font "fonts/RobotoMono-Regular.ttf"
    color "#c0d0e0"
    size 26
    textalign 0.5
    layout "subtitle"

style confirm_button:
    xsize 240

style confirm_button_text:
    size 28


## Skip indicator screen #######################################################
##
## The skip_indicator screen is displayed to indicate that skipping is in
## progress.
##
## https://www.renpy.org/doc/html/screen_special.html#skip-indicator

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    frame:

        hbox:
            spacing 9

            text _("Skipping")

            text "►" at delayed_blink(0.0, 1.0) style "skip_triangle"
            text "►" at delayed_blink(0.2, 1.0) style "skip_triangle"
            text "►" at delayed_blink(0.4, 1.0) style "skip_triangle"


## This transform is used to blink the arrows one after another.
transform delayed_blink(delay, cycle):
    alpha .5

    pause delay

    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat


style skip_frame is empty
style skip_text is gui_text
style skip_triangle is skip_text

style skip_frame:
    ypos gui.skip_ypos
    background Frame("gui/skip.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding

style skip_text:
    size gui.notify_text_size

style skip_triangle:
    ## We have to use a font that has the BLACK RIGHT-POINTING SMALL TRIANGLE
    ## glyph in it.
    font "DejaVuSans.ttf"


## Notify screen ###############################################################
##
## The notify screen is used to show the player a message. (For example, when
## the game is quicksaved or a screenshot has been taken.)
##
## https://www.renpy.org/doc/html/screen_special.html#notify-screen

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        text "[message!tq]"

    timer 3.25 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        linear .25 alpha 1.0
    on hide:
        linear .5 alpha 0.0


style notify_frame is empty
style notify_text is gui_text

style notify_frame:
    ypos gui.notify_ypos

    background Frame("gui/notify.png", gui.notify_frame_borders, tile=gui.frame_tile)
    padding gui.notify_frame_borders.padding

style notify_text:
    properties gui.text_properties("notify")


## NVL screen ##################################################################
##
## This screen is used for NVL-mode dialogue and menus.
##
## https://www.renpy.org/doc/html/screen_special.html#nvl


screen nvl(dialogue, items=None):

    window:
        style "nvl_window"

        has vbox:
            spacing gui.nvl_spacing

        ## Displays dialogue in either a vpgrid or the vbox.
        if gui.nvl_height:

            vpgrid:
                cols 1
                yinitial 1.0

                use nvl_dialogue(dialogue)

        else:

            use nvl_dialogue(dialogue)

        ## Displays the menu, if given. The menu may be displayed incorrectly if
        ## config.narrator_menu is set to True.
        for i in items:

            textbutton i.caption:
                action i.action
                style "nvl_button"

    add SideImage() xalign 0.0 yalign 1.0


screen nvl_dialogue(dialogue):

    for d in dialogue:

        window:
            id d.window_id

            fixed:
                yfit gui.nvl_height is None

                if d.who is not None:

                    text d.who:
                        id d.who_id

                text d.what:
                    id d.what_id


## This controls the maximum number of NVL-mode entries that can be displayed at
## once.
define config.nvl_list_length = gui.nvl_list_length

style nvl_window is default
style nvl_entry is default

style nvl_label is say_label
style nvl_dialogue is say_dialogue

style nvl_button is button
style nvl_button_text is button_text

style nvl_window:
    xfill True
    yfill True

    background "gui/nvl.png"
    padding gui.nvl_borders.padding

style nvl_entry:
    xfill True
    ysize gui.nvl_height

style nvl_label:
    xpos gui.nvl_name_xpos
    xanchor gui.nvl_name_xalign
    ypos gui.nvl_name_ypos
    yanchor 0.0
    xsize gui.nvl_name_width
    min_width gui.nvl_name_width
    textalign gui.nvl_name_xalign

style nvl_dialogue:
    xpos gui.nvl_text_xpos
    xanchor gui.nvl_text_xalign
    ypos gui.nvl_text_ypos
    xsize gui.nvl_text_width
    min_width gui.nvl_text_width
    textalign gui.nvl_text_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_thought:
    xpos gui.nvl_thought_xpos
    xanchor gui.nvl_thought_xalign
    ypos gui.nvl_thought_ypos
    xsize gui.nvl_thought_width
    min_width gui.nvl_thought_width
    textalign gui.nvl_thought_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_button:
    properties gui.button_properties("nvl_button")
    xpos gui.nvl_button_xpos
    xanchor gui.nvl_button_xalign

style nvl_button_text:
    properties gui.text_properties("nvl_button")


## Bubble screen ###############################################################
##
## The bubble screen is used to display dialogue to the player when using speech
## bubbles. The bubble screen takes the same parameters as the say screen, must
## create a displayable with the id of "what", and can create displayables with
## the "namebox", "who", and "window" ids.
##
## https://www.renpy.org/doc/html/bubble.html#bubble-screen

screen bubble(who, what):
    style_prefix "bubble"

    window:
        id "window"

        if who is not None:

            window:
                id "namebox"
                style "bubble_namebox"

                text who:
                    id "who"

        text what:
            id "what"

        default ctc = None
        showif ctc:
            add ctc

style bubble_window is empty
style bubble_namebox is empty
style bubble_who is default
style bubble_what is default

style bubble_window:
    xpadding 30
    top_padding 5
    bottom_padding 5

style bubble_namebox:
    xalign 0.5

style bubble_who:
    xalign 0.5
    textalign 0.5
    color "#000"

style bubble_what:
    align (0.5, 0.5)
    text_align 0.5
    layout "subtitle"
    color "#000"

define bubble.frame = Frame("gui/bubble.png", 55, 55, 55, 95)
define bubble.thoughtframe = Frame("gui/thoughtbubble.png", 55, 55, 55, 55)

define bubble.properties = {
    "bottom_left" : {
        "window_background" : Transform(bubble.frame, xzoom=1, yzoom=1),
        "window_bottom_padding" : 27,
    },

    "bottom_right" : {
        "window_background" : Transform(bubble.frame, xzoom=-1, yzoom=1),
        "window_bottom_padding" : 27,
    },

    "top_left" : {
        "window_background" : Transform(bubble.frame, xzoom=1, yzoom=-1),
        "window_top_padding" : 27,
    },

    "top_right" : {
        "window_background" : Transform(bubble.frame, xzoom=-1, yzoom=-1),
        "window_top_padding" : 27,
    },

    "thought" : {
        "window_background" : bubble.thoughtframe,
    }
}

define bubble.expand_area = {
    "bottom_left" : (0, 0, 0, 22),
    "bottom_right" : (0, 0, 0, 22),
    "top_left" : (0, 22, 0, 0),
    "top_right" : (0, 22, 0, 0),
    "thought" : (0, 0, 0, 0),
}



################################################################################
## Mobile Variants
################################################################################

style pref_vbox:
    variant "medium"
    xsize 675

## Since a mouse may not be present, we replace the quick menu with a version
## that uses fewer and bigger buttons that are easier to touch.
screen quick_menu():
    variant "touch"

    zorder 100

    if quick_menu:

        hbox:
            style "quick_menu"
            style_prefix "quick"

            textbutton _("Back") action Rollback()
            textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("Auto") action Preference("auto-forward", "toggle")
            textbutton _("Menu") action ShowMenu()


style window:
    variant "small"
    background "gui/phone/textbox.png"

style nvl_window:
    variant "small"
    background "gui/phone/nvl.png"

style main_menu_frame:
    variant "small"
    background "gui/phone/overlay/main_menu.png"

style game_menu_outer_frame:
    variant "small"
    xpos 540
    xsize 1320
    background None

style game_menu_navigation_frame:
    variant "small"
    xsize 480

style game_menu_content_frame:
    variant "small"
    padding (0, 0)

style game_menu_viewport:
    variant "small"
    xsize 1320

style pref_vbox:
    variant "small"
    xsize 600

style bar:
    variant "small"
    ysize 28
    left_bar Solid("#cc2200")
    right_bar Solid("#1a2a3a")

style vbar:
    variant "small"
    xsize 28
    top_bar Solid("#cc2200")
    bottom_bar Solid("#1a2a3a")

style scrollbar:
    variant "small"
    ysize 12
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")

style vscrollbar:
    variant "small"
    xsize 12
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")

style slider:
    variant "small"
    ysize 28
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")

style vslider:
    variant "small"
    xsize 28
    base_bar Solid("#1a2a3a")
    thumb Solid("#cc2200")

style slider_vbox:
    variant "small"
    xsize None

style slider_slider:
    variant "small"
    xsize 900
