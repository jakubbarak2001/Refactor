################################################################################
## REFACTOR — Event Screens
##
## The Slay-the-Spire-style choice surface for random events.
##
##   event_screen(title, art, body, choices)  -> returns the chosen choice id
##   event_outcome(title, art, result)        -> shows the consequence, dismiss
##
## Both share the left art panel (_event_art_panel): a real illustration when
## images/events/<id>.jpg exists, a styled placeholder until then. Driven from
## the ev_* labels in events/random_events.rpy.
##
## choices: list of dicts —
##   {"id": str, "label": str, "desc": str,
##    "enabled": bool = True, "locked": str = "",
##    "preview_card": str = ""}   ## card_id — floats a full card view on hover
## body / result: list of paragraph strings. All text is substitute-False —
## pass literal strings; {color=...}/{stshl=...} tags still render.
################################################################################

screen _event_art_panel(art, title):
    $ _ev_acc = class_accent_color()
    $ _ev_has_art = bool(art) and renpy.loadable(art)

    frame:
        xysize (560, 668)
        background Frame(_ev_acc + "cc", 4, 4)
        padding (5, 5)

        frame:
            xfill True
            yfill True
            background Frame("#0c0c0e", 0, 0)

            if _ev_has_art:
                add Transform(art, fit="cover", xysize=(550, 658)) xalign 0.5 yalign 0.5
            else:
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 4
                    text "?":
                        xalign 0.5
                        color _ev_acc
                        size 240
                        bold True
                        font DOSSIER_FONT
                        outlines [(3, "#000000", 0, 0)]
                    text title substitute False:
                        xalign 0.5
                        color DOSSIER_INK_DIM
                        size 20
                        bold True
                        font DOSSIER_FONT
                        xmaximum 500
                        text_align 0.5


screen event_screen(title, art, body, choices):
    modal True
    zorder 700

    ## Hover-inspect: the currently-hovered choice's preview_card / preview_relic,
    ## or None. Bound by hovered/unhovered actions on each choice button below.
    default _ev_hover_card = None
    default _ev_hover_relic = None

    add "#0a0a0aee"
    use class_color_frame(thickness=3, alpha_suffix="aa")

    ## Stats bar embedded so the player can see what they're trading off
    ## during a choice. `use` ignores the bar's own zorder/layer directives
    ## and renders the content at this screen's zorder (700), above the
    ## modal overlay.
    use stats_bar

    hbox:
        xalign 0.5
        yalign 0.5
        spacing 46

        use _event_art_panel(art, title)

        vbox:
            xsize 1080
            yalign 0.5
            spacing 13

            text title substitute False:
                color "#e8c878"
                size 40
                bold True
                font DOSSIER_FONT
                outlines [(2, "#000000", 0, 0)]

            text "──────────────────────────────────────":
                color "#2a2a2a"
                size 14

            for _ev_p in body:
                text _ev_p substitute False:
                    color DOSSIER_INK
                    size 20
                    font DOSSIER_FONT
                    xmaximum 1080
                    line_spacing 3

            null height 6

            for _ev_c in choices:
                python:
                    _ev_en   = _ev_c.get("enabled", True)
                    _ev_lbl  = _ev_c.get("label", "")
                    _ev_dsc  = _ev_c.get("desc", "") if _ev_en else _ev_c.get("locked", "")
                    _ev_prev = _ev_c.get("preview_card") or None
                    _ev_prev_r = _ev_c.get("preview_relic") or None

                button:
                    xsize 1080
                    ## Locked choices stay hoverable (NullAction, flat hover bg)
                    ## so their card/gear preview panel still works — an
                    ## insensitive button would swallow the hover events.
                    action (Return(_ev_c["id"]) if _ev_en else NullAction())
                    background (Frame("#15151aee", 4, 4) if _ev_en else Frame("#101012aa", 4, 4))
                    hover_background (Frame("#24242eee", 4, 4) if _ev_en else Frame("#101012aa", 4, 4))
                    padding (22, 13)
                    hovered [SetScreenVariable("_ev_hover_card", _ev_prev), SetScreenVariable("_ev_hover_relic", _ev_prev_r)]
                    unhovered [SetScreenVariable("_ev_hover_card", None), SetScreenVariable("_ev_hover_relic", None)]

                    vbox:
                        spacing 4

                        text _ev_lbl substitute False:
                            color ("#e8c878" if _ev_en else "#555555")
                            size 21
                            bold True
                            font DOSSIER_FONT

                        text _ev_dsc substitute False:
                            color ("#c0d0e0" if _ev_en else "#666666")
                            size 16
                            font DOSSIER_FONT
                            xmaximum 1030

    ## Floating card preview — when a choice with a `preview_card` is hovered,
    ## render the full StS card view pinned to the right margin of the screen,
    ## past the choice column. 400×572 (inspect mode) fits in the ~415px gutter
    ## between the choice column's right edge (~x=1505) and the screen edge.
    if _ev_hover_card:
        frame:
            xalign 1.0
            yalign 0.5
            xoffset -10
            background None
            padding (0, 0)
            use battle_card_view(cid=_ev_hover_card, mode="inspect", playable=True)

    ## Floating gear preview — same right-margin slot, for choices that hand
    ## out a relic (`preview_relic`): item sprite + rarity + the mechanic
    ## line, mirroring the relic tray's inspect panel.
    if _ev_hover_relic:
        python:
            _ev_rl    = RELIC_LIBRARY.get(_ev_hover_relic, {})
            _ev_rhex  = relic_hex(_ev_hover_relic)
            _ev_ricon = relic_art_disp(_ev_hover_relic, 180)
        frame:
            xalign 1.0
            yalign 0.5
            xoffset -24
            xsize 392
            background Frame("#0d0a08f0", 4, 4)
            padding (22, 20)
            vbox:
                spacing 10
                xfill True
                if _ev_ricon is not None:
                    frame:
                        xalign 0.5
                        xysize (196, 196)
                        background Frame(Solid(_ev_rhex), 3, 3)
                        padding (8, 8)
                        frame:
                            xfill True
                            yfill True
                            background "#11110caa"
                            padding (0, 0)
                            add _ev_ricon xalign 0.5 yalign 0.5
                text _ev_rl.get("name", _ev_hover_relic):
                    color _ev_rhex
                    size 24
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"
                text (_ev_rl.get("rarity", "common").upper()):
                    color "#8a7a64"
                    size 13
                    bold True
                    font "fonts/RobotoMono-Regular.ttf"
                text _ev_rl.get("hook", ""):
                    color "#e2d8c4"
                    size 18
                    xmaximum 348
                    font "fonts/RobotoMono-Regular.ttf"
                if _ev_rl.get("flavor"):
                    text _ev_rl.get("flavor"):
                        color "#9a8f78"
                        size 14
                        italic True
                        xmaximum 348
                        font "fonts/RobotoMono-Regular.ttf"

    ## Number-key shortcuts — one key bound per present, enabled choice.
    ## Built in a loop: a hardcoded key referencing choices[N] would eval that
    ## index at render time and IndexError on any event with fewer choices.
    for _ev_ki, _ev_kc in enumerate(choices):
        if _ev_ki < 9 and _ev_kc.get("enabled", True):
            $ _ev_keysym = "K_" + str(_ev_ki + 1)
            key _ev_keysym action Return(_ev_kc["id"])


screen event_outcome(title, art, result):
    modal True
    zorder 700

    add "#0a0a0aee"
    use class_color_frame(thickness=3, alpha_suffix="aa")
    use stats_bar

    hbox:
        xalign 0.5
        yalign 0.5
        spacing 46

        use _event_art_panel(art, title)

        vbox:
            xsize 1080
            yalign 0.5
            spacing 14

            text title substitute False:
                color "#e8c878"
                size 40
                bold True
                font DOSSIER_FONT
                outlines [(2, "#000000", 0, 0)]

            text "──────────────────────────────────────":
                color "#2a2a2a"
                size 14

            for _ev_r in result:
                text _ev_r substitute False:
                    color DOSSIER_INK
                    size 21
                    font DOSSIER_FONT
                    xmaximum 1080
                    line_spacing 3

            null height 16

            textbutton "[[ CONTINUE ]":
                xalign 0.0
                action Return(True)
                text_color "#ffffff"
                text_hover_color "#e8c878"
                text_size 23
                text_bold True
                text_font DOSSIER_FONT
                background Frame("#1a1a1aee", 4, 4)
                hover_background Frame("#2a2a2aee", 4, 4)
                padding (40, 14)

    key "K_RETURN" action Return(True)
    key "K_KP_ENTER" action Return(True)
    key "K_SPACE" action Return(True)


## ---------------------------------------------------------------------------
## event_card_picker — choose one card from a supplied list (the player's deck,
## filtered by the caller). Used by events that upgrade / transform / remove /
## duplicate a specific card. Returns the chosen card id. The caller guarantees
## `entries` is non-empty — deck-manip choices are gated otherwise.
## ---------------------------------------------------------------------------

screen event_card_picker(prompt, entries):
    modal True
    zorder 705

    ## Hovered card + its (row, col) grid slot — drives the anchored
    ## hover-inspect overlay (same pattern as fixer_removal_screen). The
    ## adjustment tracks the grid's vertical scroll so the anchor stays
    ## glued while scrolled.
    default _ecp_hover = None
    default _ecp_yadj  = ui.adjustment()

    add "#0a0a0aee"
    use class_color_frame(thickness=3, alpha_suffix="aa")

    ## Header — FIXED position (not centered-flow) so the grid below sits at
    ## known coordinates: the hover-inspect overlay anchors to the hovered
    ## card's slot, which needs deterministic grid geometry (fixer pattern).
    vbox:
        xalign 0.5
        ypos 40
        spacing 14

        text prompt substitute False:
            xalign 0.5
            color "#e8c878"
            size 32
            bold True
            font DOSSIER_FONT
            outlines [(2, "#000000", 0, 0)]

        text "── select a card ──":
            xalign 0.5
            color "#444444"
            size 14
            font DOSSIER_FONT

    ## Grid geometry constants — shared by the layout below AND the overlay
    ## anchor math. Slot stride = card (220/320) + gutter (16/28).
    python:
        _ECP_VX, _ECP_VY = 160, 180   ## viewport screen position
        _ECP_PAD         = 36         ## inner padding (gem overhang room)
        _ECP_SX, _ECP_SY = 236, 348   ## slot stride x/y

    ## ── Grid of full StS card visuals (same renderer as deck_viewer and
    ## deck_upgrade_picker). Click a card to pick it; hover for the
    ## full-size inspect overlay, same as the fixer. Six per row. The
    ## padded frame gives the cost gems (which overhang each card's
    ## top-left) room inside the viewport's clip area.
    viewport:
        xpos _ECP_VX
        ypos _ECP_VY
        xsize 1600
        ysize 700
        yadjustment _ecp_yadj
        scrollbars "vertical"
        mousewheel True
        draggable True

        $ _ecp_rows = [entries[_i:_i + 6] for _i in range(0, len(entries), 6)]
        frame:
            background None
            padding (_ECP_PAD, _ECP_PAD)
            vbox:
                spacing 28
                for _ecp_ri, _ecp_row in enumerate(_ecp_rows):
                    hbox:
                        spacing 16
                        for _ecp_ci, _ecp_cid in enumerate(_ecp_row):
                            fixed:
                                xysize (220, 320)
                                button:
                                    xsize 220
                                    ysize 316
                                    background None
                                    hover_background None
                                    action Return(_ecp_cid)
                                    hovered SetScreenVariable("_ecp_hover", (_ecp_cid, _ecp_ri, _ecp_ci))
                                    unhovered SetScreenVariable("_ecp_hover", None)
                                    at fixer_card_nudge
                                    use battle_card_view(cid=_ecp_cid, mode="hand", playable=True)

    ## Hover-inspect overlay — the full-size card, drawn after (= on top of)
    ## the grid so it's never clipped by the viewport or occluded by the
    ## neighbouring cards. Anchored to the hovered card's slot, flipping to
    ## the upper-left for the rightmost columns so it never runs offscreen.
    ## Vertical position is clamped to the screen and tracks the scroll.
    if _ecp_hover:
        python:
            _ecp_slot_x = _ECP_VX + _ECP_PAD + _ecp_hover[2] * _ECP_SX
            _ecp_slot_y = _ECP_VY + _ECP_PAD + _ecp_hover[1] * _ECP_SY - int(_ecp_yadj.value)
            _ecp_ins_x = (_ecp_slot_x - 414) if _ecp_hover[2] >= 4 else (_ecp_slot_x + 234)
            _ecp_ins_y = max(16, min(_ecp_slot_y - 200, 1080 - 588))
        fixed:
            xpos _ecp_ins_x
            ypos _ecp_ins_y
            xysize (400, 572)
            at inspect_overlay_in
            use battle_card_view(cid=_ecp_hover[0], mode="inspect", playable=True)
