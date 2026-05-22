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
##    "enabled": bool = True, "locked": str = ""}
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

    add "#0a0a0aee"
    use class_color_frame(thickness=3, alpha_suffix="aa")

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
                    _ev_en  = _ev_c.get("enabled", True)
                    _ev_lbl = _ev_c.get("label", "")
                    _ev_dsc = _ev_c.get("desc", "") if _ev_en else _ev_c.get("locked", "")

                button:
                    xsize 1080
                    sensitive _ev_en
                    action Return(_ev_c["id"])
                    background Frame("#15151aee", 4, 4)
                    hover_background Frame("#24242eee", 4, 4)
                    insensitive_background Frame("#101012aa", 4, 4)
                    padding (22, 13)

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

    add "#0a0a0aee"
    use class_color_frame(thickness=3, alpha_suffix="aa")

    vbox:
        xalign 0.5
        yalign 0.5
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

        viewport:
            xsize 1520
            ysize 600
            scrollbars "vertical"
            mousewheel True
            draggable True

            vbox:
                spacing 8
                xalign 0.5

                python:
                    _ecp_rows = [entries[_i:_i + 4] for _i in range(0, len(entries), 4)]

                for _ecp_row in _ecp_rows:
                    hbox:
                        spacing 8
                        for _ecp_cid in _ecp_row:
                            python:
                                _ecp_c    = CARD_LIBRARY.get(_ecp_cid, {})
                                _ecp_name = _ecp_c.get("name", _ecp_cid)
                                _ecp_sub  = "{} · {} · {}".format(
                                    _ecp_c.get("type", ""), _ecp_c.get("rarity", ""),
                                    _ecp_c.get("color", "")).upper()
                                _ecp_eff  = effect_description(_ecp_c.get("effect", ""))
                                _ecp_cost = _ecp_c.get("cost", 0)

                            button:
                                xsize 366
                                ysize 138
                                background Frame("#0d0d0dee", 4, 4)
                                hover_background Frame("#241d15", 4, 4)
                                action Return(_ecp_cid)
                                padding (13, 11)

                                vbox:
                                    spacing 4

                                    hbox:
                                        spacing 7
                                        text "[ {} ]".format(_ecp_cost) substitute False:
                                            color "#e8c878"
                                            size 15
                                            bold True
                                            font DOSSIER_FONT
                                        text _ecp_name substitute False:
                                            color card_name_color(_ecp_c, "#ffffff")
                                            size 17
                                            bold True
                                            font DOSSIER_FONT

                                    text _ecp_sub substitute False:
                                        color "#666666"
                                        size 11
                                        font DOSSIER_FONT

                                    text _ecp_eff substitute False:
                                        color "#c0d0e0"
                                        size 13
                                        font DOSSIER_FONT
                                        xmaximum 338
