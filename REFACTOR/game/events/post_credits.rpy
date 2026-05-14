################################################################################
## REFACTOR — Post-Credits (Singapore)
##
## Slow-burn split-screen call from Martin on Lake Como after the good_ending
## score card. Single line — "How fast can you fly to Singapore?" — into a
## full-screen REFACTOR title slam. Sequel hook.
##
## Hook: called from good_ending right before `$ renpy.full_restart()`.
################################################################################

## ---------------------------------------------------------------------------
## Split-screen plates — each source bg is scaled to full-screen and then
## CROPPED to its half (jira's left half, como's right half). No stretch / no
## aspect-ratio distortion — just a literal mask of the relevant region.
## bg_post_credit_jira_only: left=jira, right=solid black (cold-open frame).
## bg_post_credit_split:     left=jira, right=como        (final composite).
## ---------------------------------------------------------------------------

image bg_post_credit_jira_only = Composite(
    (1920, 1080),
    (0,   0), Crop((0,   0, 960, 1080), Transform("images/backgrounds/bg_jira_meeting.jpg", xysize=(1920, 1080))),
    (960, 0), Solid("#000000", xysize=(960, 1080)),
)

image bg_post_credit_split = Composite(
    (1920, 1080),
    (0,   0), Crop((0,   0, 960, 1080), Transform("images/backgrounds/bg_jira_meeting.jpg", xysize=(1920, 1080))),
    (960, 0), Crop((960, 0, 960, 1080), Transform("images/backgrounds/bg_como_balcony.jpg", xysize=(1920, 1080))),
)

## Thin near-black hairline down the centre — the literal split edge.
image split_divider = Solid("#080808", xysize=(4, 1080))

## Title-card layer — near-opaque black wash + huge letter-spaced REFACTOR +
## small "will return." tease. Rendered as Text displayables so we drive timing
## without waiting on click.
image post_credits_vignette = Solid("#000000", xysize=(1920, 1080))
image post_credits_title    = Text("R E F A C T O R", size=240, color="#fafafa", outlines=[(5, "#000000", 0, 0)])
image post_credits_tease    = Text("will return.", size=56, color="#cccccc", italic=True)

## Dialogue-as-floating-text — bypass Ren'Py's say-screen to kill the black
## dialogue box. Restrained cinematic subtitle treatment: RobotoMono (ties to
## the programmer identity, Mr. Robot register), all lowercase, warm off-white,
## no outlines / bold / italic / scale-flourish. Emphasis on Singapore comes
## from TIMING (the line hangs trailing, then Singapore drops in below) — not
## from size acrobatics. Restraint reads as cinema; flourish reads as game UI.
image post_credits_line_jb       = Text("jb.",                           size=46, color="#f4ecdc", font="fonts/RobotoMono-Regular.ttf")
image post_credits_line_question = Text("how fast can you fly to",       size=46, color="#f4ecdc", font="fonts/RobotoMono-Regular.ttf")
image post_credits_line_singapore = Text("Singapore?",                    size=58, color="#f8efd9", font="fonts/RobotoMono-Regular.ttf")

## Subtitle backdrop — semi-opaque dark band across the lower-third. Guarantees
## readability on any bg (Martin's white shirt was the worst case). Bond /
## Better-Call-Saul convention: the band reads as cinema, not as game UI.
image post_credits_subtitle_band = Solid("#000000C8", xysize=(1920, 260))

transform subtitle_band_pos:
    xpos 0
    ypos 820

transform line_top_pos:
    xalign 0.5
    yalign 0.85

transform line_bottom_pos:
    xalign 0.5
    yalign 0.95

## Sprite transforms — characters sit at the quarter-points so each half-bg
## fully contains its sprite without crossing the divider.
transform split_left_sprite:
    zoom 0.82
    xalign 0.25
    yalign 1.0

transform split_right_sprite:
    zoom 0.82
    xalign 0.75
    yalign 1.0

transform split_divider_pos:
    xalign 0.5
    yalign 0.5


## ---------------------------------------------------------------------------
## Scene
## ---------------------------------------------------------------------------

label post_credits_singapore:

    ## --- Hand-off from the ending screen: drop to silence, hold the dark.
    ## Stats bar is also hidden — the HUD has no place in a cinematic coda. ---
    hide screen stats_bar
    stop music fadeout 2.2
    scene bg_black with Dissolve(1.0)
    pause 1.4

    ## --- JB at his stand-up, alone. Soft ambient. Right half stays black. ---
    play music "audio/coding_in_snow_theme.mp3" fadein 2.4 volume 0.45
    scene bg_post_credit_jira_only with Dissolve(1.6)
    show jb developer_happy at split_left_sprite with Dissolve(1.0)
    pause 2.6

    ## --- Phone vibrates on the table. He picks up. ---
    show jb developer_call at split_left_sprite with Dissolve(0.5)
    pause 1.0

    ## --- Slow burn: ambient fades, Martin's theme cues in over the dark. ---
    stop music fadeout 1.0
    play music "audio/martin_meeting_event_the_arrival.mp3" fadein 1.4 volume 0.85
    pause 0.8

    ## --- Como balcony slowly fades up on the right half. No Martin yet. ---
    ## Queue scene + JB re-show + divider BEFORE the `with` so the dissolve
    ## interpolates between (jira_only + JB call-pose) and (split + JB call
    ## + divider). JB exists in both states so he never fades or pops.
    scene bg_post_credit_split
    show jb developer_call at split_left_sprite
    show split_divider at split_divider_pos
    with Dissolve(2.5)

    ## --- Hold the empty balcony for a beat. Atmosphere lands. ---
    pause 2.0

    ## --- Martin fades in. ---
    show martin como at split_right_sprite with Dissolve(1.2)
    pause 1.6

    ## --- Lines as floating subtitle text over a semi-opaque dark band. No
    ## say-box, no name tag. The band guarantees readability on any bg —
    ## Martin's white shirt would otherwise wash out the text. The question
    ## hangs, then Singapore drops in beneath it — emphasis through timing
    ## and line break, not through size acrobatics. ---
    show post_credits_subtitle_band at subtitle_band_pos with Dissolve(0.45)

    show post_credits_line_jb at line_top_pos with Dissolve(0.5)
    pause 1.4
    hide post_credits_line_jb with Dissolve(0.45)
    pause 0.5

    show post_credits_line_question at line_top_pos with Dissolve(0.6)
    pause 1.7

    show post_credits_line_singapore at line_bottom_pos with Dissolve(0.5)
    pause 2.8

    ## --- Lines + band fade. Beat of silence before the title slam. ---
    hide post_credits_line_question with Dissolve(0.5)
    hide post_credits_line_singapore with Dissolve(0.5)
    hide post_credits_subtitle_band with Dissolve(0.6)
    pause 0.9

    ## --- TITLE SLAM. Near-opaque wash drops, huge REFACTOR lands. ---
    show post_credits_vignette with Dissolve(0.4)
    show post_credits_title at truecenter with Dissolve(0.5)
    pause 3.4

    hide post_credits_title with Dissolve(0.55)
    pause 0.35

    show post_credits_tease at truecenter with Dissolve(0.55)
    pause 2.4

    ## --- Out. Hide the tease first; vignette stays fully opaque on top so
    ## the underlying call scene never peeks through during the wind-down. ---
    hide post_credits_tease with Dissolve(0.7)
    pause 0.5

    ## Replace the master-layer scene with bg_black (clears JB / Martin /
    ## divider / split bg) AND restore the opaque vignette on top in the same
    ## interaction frame — Ren'Py commits both queued changes atomically when
    ## the next pause hits, so there's no single-frame leak of the call scene.
    scene bg_black
    show post_credits_vignette
    stop music fadeout 2.4
    pause 1.2

    ## Vignette stays in place through the return — good_ending's
    ## `$ renpy.full_restart()` hard-resets to main menu and clears it.
    ## No fade-out needed; bg_black sits below an identical opaque vignette.
    return
