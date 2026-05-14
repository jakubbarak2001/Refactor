## Cold Wire — studio splash. Ren'Py's built-in `splashscreen` label
## runs once at game launch before the main menu loads. Replace the
## text-only render with proper artwork (PNG sequence, WebM, or single
## logo image) before ship — animation timing stays as-is.

image cw_mark = Text("CW", style="cw_mark_style")
image cw_wordmark = Text("COLD WIRE", style="cw_wordmark_style")

style cw_mark_style:
    font "fonts/RobotoMono-Regular.ttf"
    size 180
    bold True
    color "#ffffff"
    kerning 40
    outlines [(2, "#cc2200", 2, 2)]

style cw_wordmark_style:
    font "fonts/RobotoMono-Regular.ttf"
    size 28
    color "#cccccc"
    kerning 8

transform cw_mark_anim:
    alpha 0.0 xalign 0.5 yalign 0.42
    pause 0.05
    linear 0.22 alpha 1.0
    linear 0.04 yoffset -2
    linear 0.04 yoffset 0
    pause 0.55
    linear 0.25 alpha 0.0

transform cw_wordmark_anim:
    alpha 0.0 xalign 0.5 yalign 0.56
    pause 0.35
    linear 0.25 alpha 1.0
    pause 0.35
    linear 0.25 alpha 0.0

label splashscreen:
    scene black
    show cw_mark at cw_mark_anim
    show cw_wordmark at cw_wordmark_anim
    pause 1.35
    scene black
    return
