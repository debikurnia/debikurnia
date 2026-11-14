#!/usr/bin/env python3
"""Builds the SVG cards that README.md shows, each in a light and a dark variant.

Run it from anywhere after changing a card's text or the colors:

    python3 scripts/build-readme-assets.py

It writes assets/readme/<card>-light.svg and <card>-dark.svg. README.md picks the
variant that matches the viewer's theme with <picture>. Only the standard library is used.

Text inside an SVG doesn't wrap, so every line is set by hand. Keep lines about as long
as they are now: GitHub draws them with the viewer's system font (San Francisco on a Mac,
Segoe UI on Windows), and widths differ a little between the two.
"""

import math
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "readme"

# Primer's colors, so the cards sit naturally on GitHub in either theme.
THEMES = {
    "light": {
        "card": "#f6f8fa", "raised": "#ffffff", "border": "#d0d7de", "fg": "#1f2328",
        "muted": "#59636e", "subtle": "#6e7781", "accent": "#6e40c9", "indigo": "#4338ca",
        "green": "#1a7f37", "blue": "#0969da", "red": "#cf222e", "grid": 0.055, "glow": 0.16,
        "tint": 0.08, "edge": 0.30, "skeleton": 0.13, "button": "#f6f8fa", "primary": "#6e40c9",
        "wall_a": "#e9e3ff", "wall_b": "#dcecff", "menubar": "#ffffff", "menubar_opacity": 0.6,
        "thumb_glyph": 0.75, "teal": "#0b7f72", "magenta": "#d6006f", "sidebar": 0.035, "line_art": 0.55,
        "icon_edge": 0,
    },
    "dark": {
        "card": "#161b22", "raised": "#0d1117", "border": "#30363d", "fg": "#e6edf3",
        "muted": "#9198a1", "subtle": "#7d8590", "accent": "#a371f7", "indigo": "#818cf8",
        "green": "#3fb950", "blue": "#4493f8", "red": "#f85149", "grid": 0.05, "glow": 0.22,
        "tint": 0.13, "edge": 0.38, "skeleton": 0.16, "button": "#21262d", "primary": "#8957e5",
        "wall_a": "#221a4d", "wall_b": "#0c1a33", "menubar": "#000000", "menubar_opacity": 0.35,
        "thumb_glyph": 0.45, "teal": "#22a897", "magenta": "#ff4d9e", "sidebar": 0.04, "line_art": 0.5,
        "icon_edge": 0.12,
    },
}

SANS = '-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif'
MONO = 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace'
BASE_CSS = (
    f"text{{font-family:{SANS}}}.mono{{font-family:{MONO}}}"
    ".grow{transform-box:fill-box;transform-origin:center}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)

# Helvetica/Arial advance widths (1/1000 em): a safe upper bound for the system fonts.
_W = dict(zip(" !\"#$%&'()*+,-./0123456789:;<=>?@", [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584,
          278, 333, 278, 278] + [556] * 10 + [278, 278, 584, 584, 584, 556, 1015]))
_W.update(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", [667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722,
          778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611]))
_W.update(zip("abcdefghijklmnopqrstuvwxyz", [556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556,
          556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500]))
_W.update({"[": 278, "\\": 278, "]": 278, "_": 556, "·": 278, "“": 333, "”": 333, "’": 222, "→": 1000, "≠": 584})


def width(text, size, *, bold=False, mono=False, spacing=0.0):
    """Estimated rendered width of a line of text, in SVG units."""
    if mono:
        base = 0.6 * size * len(text)
    else:
        base = sum(_W.get(ch, 556) for ch in text) / 1000 * size * (1.07 if bold else 1.0)
    return base + spacing * len(text)


def svg(w, h, label, body, defs="", css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>'
        f"<style>{BASE_CSS}{css}</style><defs>{defs}</defs>{body}</svg>\n"
    )


def text(x, y, content, *, size, fill, weight=None, mono=False, spacing=None, anchor=None, extra=""):
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'font-size="{size:g}"', f'fill="{fill}"']
    if mono:
        attrs.append('class="mono"')
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if spacing is not None:
        attrs.append(f'letter-spacing="{spacing:g}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    if extra:
        attrs.append(extra)
    return f'<text {" ".join(attrs)}>{content}</text>'


def frame(t, x, y, w, h, r=20):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{t["card"]}" '
            f'stroke="{t["border"]}" stroke-width="1.25"/>')


def eyebrow(x, y, label, color, anchor=None):
    return text(x, y, escape(label), size=12, fill=color, weight=600, mono=True, spacing=1.8, anchor=anchor)


def arrow(x, y, color):
    """A 12-unit "opens a link" arrow with its top-left corner at x, y."""
    return (f'<path d="M{x} {y + 12}L{x + 12} {y}M{x + 3.5} {y}H{x + 12}V{y + 8.5}" fill="none" stroke="{color}" '
            'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')


def chip(t, x, y, label, color, *, size=12.5, height=24, pad=11, mono=False, spacing=0.0, ink=None):
    """A rounded label; returns its markup and its width."""
    w = width(label, size, mono=mono, spacing=spacing, bold=True) + 2 * pad
    markup = (
        f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{height}" rx="{height / 2:g}" fill="{color}" '
        f'fill-opacity="{t["tint"]}" stroke="{color}" stroke-opacity="{t["edge"]}"/>'
        + text(x + w / 2 - spacing / 2, y + height / 2 + size * 0.35, escape(label), size=size, fill=ink or color,
               weight=600, mono=mono, spacing=spacing or None, anchor="middle")
    )
    return markup, w


def chips(t, x, y, labels, color, gap=8, **kw):
    out = []
    for label in labels:
        markup, w = chip(t, x, y, label, color, **kw)
        out.append(markup)
        x += w + gap
    return "".join(out), x - gap


def notch_path(cx, top, w, h, ear=10, radius=16):
    """The island: concave top corners that flow into the bezel, rounded bottom corners."""
    k = 0.5523
    x0, x1, yb = cx - w / 2, cx + w / 2, top + h
    return (
        f"M{x0 - ear:.1f} {top}C{x0 - ear + k * ear:.1f} {top} {x0:.1f} {top + ear - k * ear:.1f} {x0:.1f} {top + ear}"
        f"L{x0:.1f} {yb - radius}C{x0:.1f} {yb - radius + k * radius:.1f} {x0 + radius - k * radius:.1f} {yb} "
        f"{x0 + radius:.1f} {yb}L{x1 - radius:.1f} {yb}C{x1 - radius + k * radius:.1f} {yb} {x1:.1f} "
        f"{yb - radius + k * radius:.1f} {x1:.1f} {yb - radius}L{x1:.1f} {top + ear}C{x1:.1f} {top + ear - k * ear:.1f} "
        f"{x1 + ear - k * ear:.1f} {top} {x1 + ear:.1f} {top}Z"
    )


PULSE_CSS = (
    "@keyframes pulse{0%{transform:scale(1);opacity:.6}70%,100%{transform:scale(2.8);opacity:0}}"
    ".pulse{opacity:0;animation:pulse 2.4s ease-out infinite}"
)

# The rounded square that the Havus icon and the Nyetok logo share, on their 1024-unit grid (it spans 100 to 924).
SQUIRCLE = ("M396.64 100h230.72c103.83 0 155.75 0 195.41 20.21a185.4 185.4 0 0 1 81.02 81.02C924 240.89 924 292.81 924 "
            "396.64v230.72c0 103.83 0 155.75-20.21 195.41a185.4 185.4 0 0 1-81.02 81.02C783.11 924 731.19 924 627.36 "
            "924H396.64c-103.83 0-155.75 0-195.41-20.21a185.4 185.4 0 0 1-81.02-81.02C100 783.11 100 731.19 100 "
            "627.36V396.64c0-103.83 0-155.75 20.21-195.41a185.4 185.4 0 0 1 81.02-81.02C240.89 100 292.81 100 "
            "396.64 100Z")
# Havus: an H split by a 70° cut, white on ink (design/AppIcon.svg in XNyetok/Havus).
HAVUS_H = "M288 288H392V464H514.57L482.54 552H392V728H288ZM736 736H632V560H509.43L541.46 472H632V296H736Z"
HAVUS_INK = "#0b0b0c"
# Nyetok: an N split by the same cut, white on magenta (design/logo.svg in the Nyetok website).
NYETOK_N = ("M288 728V288h104l129.98 151.64-40.88 112.31L392 448v280ZM736 296v440H632L502.02 584.36l40.88-112.31L632 "
            "576V296Z")
NYETOK_MAGENTA = "#d6006f"
# Korupsi: a gold envelope with a red seal (public/favicon.svg in XNyetok/korupsi), drawn at its own size, 38 by 25.
KORUPSI_ENVELOPE = ('<rect width="38" height="25" rx="4" fill="#e3b04b"/><path d="M2 3.5L19 15.5L36 3.5" fill="none" '
                    'stroke="#a87b23" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
                    '<circle cx="19" cy="19" r="4.6" fill="#d9483b"/>')
# Jelajah Kerinci: Gunung Kerinci over green hills (icons/icon.svg in XNyetok/Kerinciku), on its 512-unit grid; the
# mountain's foot spans 36 to 476 at y 380.
KERINCI_MOUNTAIN = ('<path d="M36 380L228 150Q256 130 284 150L476 380z" fill="#5f7d8c"/>'
                    '<path d="M228 150Q256 130 284 150L326 200L294 186L268 218L240 182L194 206z" fill="#c9d6dc"/>'
                    '<path d="M36 380L136 260Q212 310 256 286Q336 332 396 284L476 380z" fill="#3f8f5f"/>')


def logo(t, x, y, size, tile, glyph, *, edge=False):
    """An app icon or logo on its rounded square, top-left corner at x, y. `edge` outlines a dark tile in dark mode."""
    k = size / 824
    stroke = (f' stroke="#fff" stroke-opacity="{t["icon_edge"]}" stroke-width="{1 / k:.1f}"'
              if edge and t["icon_edge"] else "")
    return (f'<g transform="translate({x:g} {y:g}) scale({k:.5f}) translate(-100 -100)">'
            f'<path d="{SQUIRCLE}" fill="{tile}"{stroke}/><path d="{glyph}" fill="#fff"/></g>')


def sparkle(cx, cy, r, color, extra=""):
    """A four-point star, like the ones on nyetok.id."""
    a = r * 0.16
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    ctl = [(cx + a, cy - a), (cx + a, cy + a), (cx - a, cy + a), (cx - a, cy - a)]
    d = f"M{pts[0][0]:g} {pts[0][1]:g}" + "".join(
        f"C{ctl[i][0]:g} {ctl[i][1]:g} {ctl[i][0]:g} {ctl[i][1]:g} {pts[(i + 1) % 4][0]:g} {pts[(i + 1) % 4][1]:g}"
        for i in range(4)
    )
    return f'<path d="{d}Z" fill="{color}"{extra}/>'


# ---------------------------------------------------------------------------------------------- cards


def hero(t):
    W, H, x, y, w, h = 1000, 280, 8, 8, 984, 264
    status = "Open to freelance & product work"
    island_w = 24 + 9 + 11 + width(status, 14, bold=True) + 26
    left = 500 - island_w / 2
    defs = (
        f'<clipPath id="c"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22"/></clipPath>'
        f'<pattern id="g" width="28" height="28" patternUnits="userSpaceOnUse" x="8" y="8">'
        f'<path d="M28 0H0V28" fill="none" stroke="{t["fg"]}" stroke-opacity="{t["grid"]}"/></pattern>'
        '<radialGradient id="f" cx=".8" cy=".2" r=".75"><stop offset="0" stop-color="#fff"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
        f'<mask id="m"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#f)"/></mask>'
        f'<radialGradient id="glow" cx=".82" cy=".05" r=".6"><stop offset="0" stop-color="{t["accent"]}" '
        f'stop-opacity="{t["glow"]}"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="n" x1="52" x2="392" y1="0" y2="0" gradientUnits="userSpaceOnUse">'
        f'<stop offset=".42" stop-color="{t["fg"]}"/><stop offset="1" stop-color="{t["accent"]}"/></linearGradient>'
    )
    island = (
        f'<path d="{notch_path(500, y, island_w, 40)}" fill="#000"'
        + (' stroke="#fff" stroke-opacity=".09"' if t is THEMES["dark"] else "") + "/>"
        f'<circle class="grow pulse" cx="{left + 24 + 4.5:.1f}" cy="{y + 20}" r="4.5" fill="#3fb950"/>'
        f'<circle cx="{left + 24 + 4.5:.1f}" cy="{y + 20}" r="4.5" fill="#3fb950"/>'
        + text(left + 24 + 9 + 11, y + 25, escape(status), size=14, fill="#fff", weight=600)
    )
    muted, fg = t["muted"], t["fg"]
    tagline = (
        f'<text x="52" y="172" font-size="21" fill="{muted}">I build <tspan fill="{fg}" font-weight="600">AI web '
        f'tools</tspan>, the <tspan fill="{fg}" font-weight="600">automation</tspan> behind them,</text>'
        f'<text x="52" y="201" font-size="21" fill="{muted}">and small <tspan fill="{fg}" font-weight="600">native '
        "macOS apps</tspan>.</text>"
    )
    services = ["LLM features & prompt pipelines", "Automation & internal tools", "Laravel apps, v1 to production",
                "Native macOS utilities in Swift"]
    rows = [eyebrow(662, 98, "HIRE ME FOR", t["accent"])]
    for i, label in enumerate(services):
        ry = 112 + i * 34
        rows.append(
            f'<rect x="662" y="{ry}" width="294" height="27" rx="8" fill="{t["raised"]}" stroke="{t["border"]}"/>'
            + text(676, ry + 18, f"0{i + 1}", size=11.5, fill=t["accent"], weight=600, mono=True)
            + text(702, ry + 18.5, escape(label), size=13.5, fill=fg, weight=500)
        )
    body = (
        frame(t, x, y, w, h, 22)
        + f'<g clip-path="url(#c)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#g)" mask="url(#m)"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#glow)"/></g>'
        + island
        + text(50, 132, "Debi Kurnia", size=58, fill="url(#n)", weight=700, spacing=-1.6)
        + tagline
        + eyebrow(52, 242, "FOUNDER OF OPUSTOCK · JAKARTA, INDONESIA", t["subtle"])
        + "".join(rows)
    )
    label = ("Debi Kurnia. I build AI web tools, the automation behind them, and small native macOS apps. "
             "Founder of Opustock, Jakarta, Indonesia. Open to freelance and product work: LLM features and prompt "
             "pipelines, automation and internal tools, Laravel apps from first version to production, and native "
             "macOS utilities in Swift.")
    return svg(W, H, label, body, defs, PULSE_CSS)


def opustock(t):
    W, H, x, y, w, h = 1000, 230, 8, 8, 984, 214
    ind = t["indigo"]
    defs = (
        f'<clipPath id="c"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20"/></clipPath>'
        f'<pattern id="g" width="24" height="24" patternUnits="userSpaceOnUse" x="8" y="8">'
        f'<path d="M24 0H0V24" fill="none" stroke="{t["fg"]}" stroke-opacity="{t["grid"]}"/></pattern>'
    )
    logo = "".join(
        f'<rect x="{44 + col * 11.5}" y="{72 + row * 11.5}" width="8" height="8" rx="2" '
        f'fill="{ind if (row, col) == (0, 2) else t["fg"]}"/>'
        for row in range(3) for col in range(3)
    )
    chip_row, _ = chips(t, 44, 182, ["XMETA", "XMOTION", "YOUR OWN AI KEY", "PROVIDER FAILOVER"], ind, size=11,
                        mono=True, spacing=1.2, pad=10)
    # A batch of thumbnails; the checks land one after another, like a run going through.
    hues = [(ind, t["accent"]), (t["blue"], ind), (t["accent"], t["blue"])]
    gradients, thumbs = [], []
    for i in range(12):
        row, col = divmod(i, 4)
        tx, ty = 640 + col * 71, 60 + row * 49
        a, b = hues[(row + col) % 3]
        gradients.append(
            f'<linearGradient id="t{i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}" '
            f'stop-opacity=".55"/><stop offset="1" stop-color="{b}" stop-opacity=".25"/></linearGradient>'
        )
        delay = 0.25 + i * 0.32
        thumbs.append(
            f'<rect x="{tx}" y="{ty}" width="62" height="40" rx="7" fill="url(#t{i})"/>'
            f'<circle cx="{tx + 47}" cy="{ty + 12}" r="4.5" fill="#fff" fill-opacity="{t["thumb_glyph"]}"/>'
            f'<path d="M{tx + 6} {ty + 34}L{tx + 22} {ty + 18}L{tx + 32} {ty + 27}L{tx + 40} {ty + 21}L{tx + 56} {ty + 34}Z" '
            f'fill="#fff" fill-opacity="{t["thumb_glyph"]}"/>'
            f'<g class="grow" style="animation:ok 6s {delay:.2f}s infinite both">'
            f'<circle cx="{tx + 59}" cy="{ty + 3}" r="7.5" fill="{t["green"]}" stroke="{t["card"]}" stroke-width="2"/>'
            f'<path d="M{tx + 55.6} {ty + 3.2}l2.3 2.3 4.2-4.6" fill="none" stroke="#fff" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round"/></g>'
        )
    defs += "".join(gradients)
    body = (
        frame(t, x, y, w, h)
        + f'<g clip-path="url(#c)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#g)"/></g>'
        + eyebrow(44, 50, "NOW BUILDING", ind)
        + text(930, 50, "OPUSTOCK.COM", size=12, fill=t["subtle"], weight=600, mono=True, spacing=1.8, anchor="end")
        + arrow(942, 39, t["subtle"])
        + logo
        + text(86, 98, "opustock", size=33, fill=t["fg"], weight=700, spacing=-0.8)
        + text(44, 140, "Batch work, made calm.", size=21, fill=t["fg"], weight=700)
        + text(44, 166, "Metadata and motion prompts for whole batches, on your own AI key.", size=15.5,
               fill=t["muted"])
        + chip_row
        + "".join(thumbs)
    )
    label = ("Now building: Opustock, batch AI tools for stock and video creators. Batch work, made calm: metadata "
             "and motion prompts for whole batches, on your own AI key. XMeta, XMotion, your own AI key in an "
             "encrypted vault, and automatic failover between providers. opustock.com")
    css = "@keyframes ok{0%,8%{opacity:0;transform:scale(.4)}14%,88%{opacity:1;transform:scale(1)}96%,100%{opacity:0}}"
    return svg(W, H, label, body, defs, css)


APP = (500, 310)  # half-width card with a picture on top
SLIM = (500, 160)  # half-width card with a few lines and a small glyph


def app_card(t, name, art, desc, stat, labels, *, kicker="OPEN SOURCE · MACOS · MIT", color=None, badge=None,
             mark=""):
    """`mark` is a 26-unit logo drawn left of the name; `badge` is a small green tag right of it."""
    color = color or t["accent"]
    name_x = 70 if mark else 35
    chip_row, _ = chips(t, 36, 258, labels, color, size=12, pad=10, ink=t["fg"])
    tag = ""
    if badge:
        tag, _ = chip(t, name_x + width(name, 28, bold=True, spacing=-0.4) + 10, 173, badge, t["green"], size=10.5,
                      height=20, pad=8, mono=True, spacing=1)
    return (
        frame(t, 8, 8, APP[0] - 16, APP[1] - 16)
        + art
        + eyebrow(36, 158, kicker, color)
        + arrow(452, 147, t["subtle"])
        + mark
        + text(name_x, 193, name, size=28, fill=t["fg"], weight=700, spacing=-0.4)
        + tag
        + text(36, 221, escape(desc), size=15.5, fill=t["fg"])
        + text(36, 244, escape(stat), size=14, fill=t["muted"])
        + chip_row
    )


def jambul(t):
    sx, sy, sw, sh = 36, 30, 428, 96
    cx = sx + sw / 2
    defs = (
        f'<linearGradient id="wall" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["wall_a"]}"/>'
        f'<stop offset="1" stop-color="{t["wall_b"]}"/></linearGradient>'
        f'<clipPath id="screen"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="10"/></clipPath>'
    )
    ring_r = 7
    circ = 2 * 3.14159 * ring_r  # the ring's length, which the countdown animates
    css = (
        f"@keyframes tick{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:{circ:.2f}}}}}"
        ".ring{animation:tick 9s linear infinite}"
        "@keyframes blink{0%,44%,52%,100%{transform:scaleY(1)}48%{transform:scaleY(.1)}}"
        ".eye{animation:blink 4.6s ease-in-out infinite}"
    )
    menu_items = "".join(
        f'<rect x="{x}" y="{sy + 6.5}" width="{w}" height="5" rx="2.5" fill="{t["fg"]}" fill-opacity=".32"/>'
        for x, w in [(sx + 12, 9), (sx + 28, 22), (sx + 57, 18), (sx + sw - 76, 12), (sx + sw - 57, 16),
                     (sx + sw - 34, 22)]
    )
    # Two soft shapes so the wallpaper reads as a Mac desktop rather than a flat panel.
    defs += "".join(
        f'<radialGradient id="{gid}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{color}" '
        f'stop-opacity="{opacity}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
        for gid, color, opacity in [("w1", t["accent"], 0.35), ("w2", t["blue"], 0.3)]
    )
    iw, ih = 222, 34
    il = cx - iw / 2
    island = (
        f'<path d="{notch_path(cx, sy, iw, ih, ear=7, radius=14)}" fill="#000"'
        + (' stroke="#fff" stroke-opacity=".08"' if t is THEMES["dark"] else "") + "/>"
        f'<circle cx="{il + 22}" cy="{sy + 17}" r="{ring_r}" fill="none" stroke="#fff" stroke-opacity=".2" '
        'stroke-width="2.6"/>'
        f'<circle class="ring" cx="{il + 22}" cy="{sy + 17}" r="{ring_r}" fill="none" stroke="{THEMES["dark"]["accent"]}" '
        f'stroke-width="2.6" stroke-linecap="round" stroke-dasharray="{circ:.2f}" stroke-dashoffset="{circ * 0.3:.2f}" '
        f'transform="rotate(-90 {il + 22} {sy + 17})"/>'
        + text(il + 35, sy + 21.5, "14:59", size=12, fill="#fff", weight=600, mono=True)
        + f'<circle cx="{cx}" cy="{sy + 9}" r="2.4" fill="#16161a" stroke="#26262c"/>'
        f'<g class="grow eye"><path d="M{il + iw - 34} {sy + 17}q9-8 18 0q-9 8-18 0Z" fill="#fff"/>'
        f'<circle cx="{il + iw - 25}" cy="{sy + 17}" r="2.6" fill="#000"/></g>'
    )
    art = (
        f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="10" fill="url(#wall)" stroke="{t["border"]}"/>'
        f'<g clip-path="url(#screen)"><ellipse cx="{sx + 92}" cy="{sy + 96}" rx="150" ry="70" fill="url(#w1)"/>'
        f'<ellipse cx="{sx + sw - 70}" cy="{sy + 70}" rx="170" ry="64" fill="url(#w2)"/>'
        f'<rect x="{sx}" y="{sy}" width="{sw}" height="18" fill="{t["menubar"]}" '
        f'fill-opacity="{t["menubar_opacity"]}"/>{menu_items}</g>'
        + island
    )
    body = app_card(t, "Jambul", art, "A Dynamic Island for the MacBook notch.",
                    "In my test: 0% CPU idle, about 14 MB.",
                    ["Timer", "Keep Awake", "AI usage limits", "Claude Code sessions"])
    label = ("Jambul, open source macOS app under the MIT license: a Dynamic Island for the MacBook notch, with a "
             "timer, Keep Awake, battery peeks, your AI usage limits and which Claude Code sessions are working, "
             "waiting for you or done. In my test it idled at 0% CPU and about 14 MB of memory.")
    return svg(*APP, label, body, defs, css)


def havus(t):
    """The app after a scan, as the Havus website draws it: sidebar, the total, checked rows with their sizes."""
    wx, wy, ww, wh = 36, 30, 428, 96
    sx = wx + 112  # the sidebar's right edge
    mx, mr = sx + 14, wx + ww - 14  # the main area's content edges
    fg, sk, teal = t["fg"], t["skeleton"], t["teal"]
    art = [
        f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="10" fill="{t["raised"]}" stroke="{t["border"]}"/>',
        f'<path d="M{sx} {wy}H{wx + 10}a10 10 0 0 0-10 10V{wy + wh - 10}a10 10 0 0 0 10 10H{sx}Z" fill="{fg}" '
        f'fill-opacity="{t["sidebar"]}"/>',
        f'<path d="M{sx} {wy}V{wy + wh}" stroke="{t["border"]}"/>',
    ]
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        art.append(f'<circle cx="{wx + 14 + i * 13}" cy="{wy + 11}" r="3.8" fill="{c}"/>')
    # Overview, system junk, developer junk (open), uninstaller, large files.
    for i, (tone, lw) in enumerate([(t["subtle"], 40), (t["blue"], 52), (teal, 58), (t["accent"], 46),
                                    (t["green"], 54)]):
        cy = wy + 29 + i * 14
        if i == 2:
            art.append(f'<rect x="{wx + 6}" y="{cy - 6.5}" width="{sx - wx - 12}" height="13" rx="4" '
                       f'fill="{t["raised"]}" stroke="{t["border"]}"/>')
        art.append(f'<rect x="{wx + 13}" y="{cy - 3.5}" width="7" height="7" rx="2" fill="{tone}"/>'
                   f'<rect x="{wx + 26}" y="{cy - 2.5}" width="{lw}" height="5" rx="2.5" fill="{fg}" '
                   f'fill-opacity="{sk * (2 if i == 2 else 1.2):.2f}"/>')
    total = "11.1 GB"
    art.append(text(mx, wy + 26, total, size=17, fill=fg, weight=700, spacing=-0.3)
               + f'<rect x="{mx + width(total, 17, bold=True, spacing=-0.3) + 8:.1f}" y="{wy + 17.5}" width="58" '
               f'height="6" rx="3" fill="{fg}" fill-opacity="{sk * 1.3:.2f}"/>')
    # The clean button: a trash glyph and its label.
    bx, by = mr - 48, wy + 10
    gx, gy = bx + 13, by + 9.5
    art.append(f'<rect x="{bx}" y="{by}" width="48" height="19" rx="6" fill="{fg}"/>'
               f'<path d="M{gx - 4.4} {gy - 2.8}H{gx + 4.4}M{gx - 1.5} {gy - 2.8}V{gy - 4.3}H{gx + 1.5}V{gy - 2.8}'
               f'M{gx - 3.2} {gy - 2.8}l.6 7h5.2l.6-7" fill="none" stroke="{t["raised"]}" stroke-width="1.3" '
               'stroke-linecap="round" stroke-linejoin="round"/>'
               f'<rect x="{gx + 8}" y="{gy - 2}" width="16" height="4" rx="2" fill="{t["raised"]}" '
               'fill-opacity=".75"/>')
    # The scan's progress bar, then a check lands on each row.
    art.append(f'<rect x="{mx}" y="{wy + 33}" width="{mr - mx}" height="3" rx="1.5" fill="{fg}" fill-opacity=".08"/>'
               f'<rect class="scan" x="{mx}" y="{wy + 33}" width="{mr - mx}" height="3" rx="1.5" fill="{teal}"/>')
    for i, (tone, lw, size) in enumerate([(t["blue"], 104, "8.4 GB"), (t["red"], 78, "2.1 GB"),
                                          (t["accent"], 60, "640 MB")]):
        cy = wy + 49 + i * 18
        if i:
            art.append(f'<path d="M{mx} {cy - 9}H{mr}" stroke="{t["border"]}" stroke-opacity=".7"/>')
        art.append(
            f'<rect x="{mx + 0.5}" y="{cy - 5}" width="10" height="10" rx="3" fill="none" stroke="{t["border"]}"/>'
            f'<g class="grow" style="animation:ok 7s {0.15 + i * 0.25:.2f}s infinite both">'
            f'<rect x="{mx}" y="{cy - 5.5}" width="11" height="11" rx="3.2" fill="{teal}"/>'
            f'<path d="M{mx + 3} {cy + 0.2}l2 2 3.5-4" fill="none" stroke="#fff" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round"/></g>'
            f'<rect x="{mx + 17}" y="{cy - 6}" width="12" height="12" rx="3.5" fill="{tone}" '
            f'fill-opacity="{t["tint"] * 2.2:.2f}"/>'
            f'<rect x="{mx + 20.5}" y="{cy - 2.5}" width="5" height="5" rx="1.5" fill="{tone}"/>'
            f'<rect x="{mx + 36}" y="{cy - 3}" width="{lw}" height="6" rx="3" fill="{fg}" fill-opacity="{sk * 2:.2f}"/>'
            + text(mr, cy + 3.6, size, size=10.5, fill=fg, weight=600, mono=True, anchor="end")
        )
    css = (
        "@keyframes scan{0%{transform:scaleX(0);opacity:1}30%,90%{transform:scaleX(1);opacity:1}"
        "97%,100%{transform:scaleX(1);opacity:0}}"
        ".scan{transform-box:fill-box;transform-origin:left center;"
        "animation:scan 7s cubic-bezier(.32,.72,0,1) infinite}"
        "@keyframes ok{0%,30%{opacity:0;transform:scale(.4)}36%,90%{opacity:1;transform:scale(1)}97%,100%{opacity:0}}"
    )
    body = app_card(t, "Havus", "".join(art), "A Mac cleaner that minds its own business.",
                    "In my test: 1.5 MB app, about 34 MB idle.",
                    ["Developer junk", "Uninstaller", "Disk map", "Trash first"])
    label = ("Havus, open source macOS app under the MIT license: a lightweight Mac cleaner that minds its own "
             "business. It clears caches, logs and developer junk, uninstalls apps with their leftovers, finds large "
             "files you rarely open, maps what fills your disk and turns off programs that start on their own, and "
             "everything goes to the Trash first. It goes online only to check for updates, and only if you turn "
             "that on. In my test it is a 1.5 MB app that idles at about 34 MB of memory.")
    return svg(*APP, label, body, css=css)


def nyetok(t):
    """Nyetok means stocking up: a shelf with a box per project and a glimpse of what's in each, Gunung Kerinci
    popping out of the newest, and an empty box for the next one."""
    ink, line = t["fg"], t["line_art"]
    # The shelf sits where the other cards' pictures end (y 126), so the text below lines up across a row.
    bw, bh, gap, floor = 74, 52, 9, 125.25
    top = floor - bh

    def stroke(dashed=False):
        return (f'stroke="{ink}" stroke-opacity="{line}" stroke-width="1.5" stroke-linejoin="round"'
                + (' stroke-dasharray="3 3.5"' if dashed else ""))

    def box(x, label, contents="", dashed=False):
        """An open box seen from a little above: its back rim, what sticks out of it, then the front."""
        rim = (f'<path d="M{x + 6} {top - 8}H{x + bw - 6}L{x + bw} {top}H{x}Z" fill="{ink}" '
               f'fill-opacity="{0 if dashed else 0.07}" {stroke(dashed)}/>')
        front = (f'<rect x="{x}" y="{top}" width="{bw}" height="{bh}" rx="3" '
                 f'fill="{"none" if dashed else t["raised"]}" {stroke(dashed)}/>')
        plate_dash = ' stroke-dasharray="3 3"' if dashed else ""
        plate = (f'<rect x="{x + 9}" y="{top + 15}" width="{bw - 18}" height="17" rx="3" fill="{t["card"]}" '
                 f'stroke="{t["border"]}"{plate_dash}/>'
                 + text(x + bw / 2 + 0.5, top + 26.9, label, size=9.5, fill=t["subtle"] if dashed else ink,
                        weight=700, mono=True, spacing=1, anchor="middle"))
        stamp = "" if dashed else logo(t, x + bw - 15, top + bh - 15, 10, NYETOK_MAGENTA, NYETOK_N)
        return rim + contents + front + plate + stamp

    xs = [250 - (5 * bw + 4 * gap) / 2 + i * (bw + gap) for i in range(5)]
    mid = [x + bw / 2 for x in xs]
    # Havus: its icon, leaning out of the box.
    havus_icon = (f'<g transform="rotate(-8 {mid[0]:g} {top - 11})">'
                  + logo(t, mid[0] - 15, top - 27, 30, HAVUS_INK, HAVUS_H, edge=True) + "</g>")
    # Jambul: the island.
    island = (f'<rect x="{mid[1] - 15:g}" y="{top - 9}" width="30" height="10" rx="5" fill="#000"'
              + (' stroke="#fff" stroke-opacity=".14"' if t is THEMES["dark"] else "") + "/>"
              f'<circle cx="{mid[1] + 8:g}" cy="{top - 4}" r="2" fill="#3fb950"/>')
    # Korupsi: the envelope from its icon, seal and all.
    envelope = (f'<g transform="rotate(9 {mid[2]:g} {top - 5}) translate({mid[2] - 14:g} {top - 14}) scale(.737)">'
                + KORUPSI_ENVELOPE + "</g>")
    # Jelajah Kerinci, the newest: Gunung Kerinci from its icon bobs out of the box, with a few sparkles.
    k = 56 / 440
    mountain = (f'<g class="bob"><g transform="translate({mid[3] - 256 * k:.2f} {top + 6 - 380 * k:.2f}) '
                f'scale({k:.4f})">{KERINCI_MOUNTAIN}</g></g>')
    sparkles = "".join(
        sparkle(cx, cy, r, t["magenta"], f' class="grow tw" style="animation-delay:{delay}s"')
        for cx, cy, r, delay in [(mid[3] + 25, top - 26, 5.2, 0), (mid[3] - 27, top - 16, 3.6, 0.9),
                                 (mid[3] + 33, top - 9, 2.8, 1.6)]
    )
    art = (
        f'<path d="M44 {floor + 0.75}H456" fill="none" {stroke()} stroke-linecap="round"/>'
        + box(xs[0], "HAVUS", havus_icon)
        + box(xs[1], "JAMBUL", island)
        + box(xs[2], "KORUPSI", envelope)
        + box(xs[3], "KERINCI", mountain)
        + sparkles
        + box(xs[4], "NEXT", dashed=True)
    )
    css = (
        "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}"
        ".bob{animation:bob 3.4s ease-in-out infinite}"
        "@keyframes tw{0%,100%{opacity:.3;transform:scale(.55)}50%{opacity:1;transform:scale(1)}}"
        ".tw{animation:tw 2.6s ease-in-out infinite both}"
    )
    body = app_card(t, "Nyetok", art, "Small apps that are actually useful.",
                    "Mac apps and browser games, made in Indonesia.", ["Free", "Open source", "No account"],
                    kicker="HOME OF MY APPS · NYETOK.ID", color=t["magenta"],
                    mark=logo(t, 36, 171, 26, NYETOK_MAGENTA, NYETOK_N))
    label = ("Nyetok, the home of my open source apps, at nyetok.id: small apps that are actually useful. Mac apps "
             "and browser games, MIT-licensed and made in Indonesia; free, with no account.")
    return svg(*APP, label, body, css=css)


# ------------------------------------------------------------------------------------------ game cards


def browser(t, url, page):
    """A browser window over the card's picture area, `url` in its address bar and `page` drawn inside it.
    Returns the window's clip path, for <defs>, and the window."""
    x, y, w, h, bar, pill = 36, 30, 428, 96, 18, 150
    clip = (f'<clipPath id="page"><path d="M{x} {y + bar}H{x + w}V{y + h - 10}a10 10 0 0 1-10 10H{x + 10}'
            f'a10 10 0 0 1-10-10Z"/></clipPath>')
    window = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{t["raised"]}"/>'
        f'<g clip-path="url(#page)">{page}</g>'
        f'<path d="M{x} {y + bar}H{x + w}" stroke="{t["border"]}"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="{t["border"]}"/>'
        + "".join(f'<circle cx="{x + 14 + i * 13}" cy="{y + bar / 2:g}" r="3.8" fill="{c}"/>'
                  for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))
        + f'<rect x="{x + (w - pill) / 2:g}" y="{y + 3.5:g}" width="{pill}" height="11" rx="5.5" fill="{t["card"]}" '
        f'stroke="{t["border"]}"/>'
        + text(x + w / 2, y + 12.1, escape(url), size=8.5, fill=t["muted"], mono=True, anchor="middle")
    )
    return clip, window


def pixels(x, y, rows, palette, p=2, outline=None):
    """Pixel art: one character per pixel ("." for none), drawn as runs of p-unit squares. `outline` rings the
    sprite one pixel wide in that color, just outside the given rows, as the game's own sprites are."""
    if outline:
        cells = {(i, j): ch for j, row in enumerate(rows) for i, ch in enumerate(row) if ch != "."}
        ring = {(i + di, j + dj) for i, j in cells for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))} - cells.keys()
        cells.update(dict.fromkeys(ring, "@"))
        cols = max(len(row) for row in rows)
        rows = ["".join(cells.get((i, j), ".") for i in range(-1, cols + 1)) for j in range(-1, len(rows) + 1)]
        palette, x, y = {**palette, "@": outline}, x - p, y - p
    runs = {}  # one path per color keeps the file small
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            k = i
            while k < len(row) and row[k] == row[i]:
                k += 1
            if row[i] != ".":
                runs.setdefault(row[i], []).append(f"M{x + i * p:g} {y + j * p:g}h{(k - i) * p:g}v{p:g}h-{(k - i) * p:g}z")
            i = k
    return "".join(f'<path d="{"".join(d)}" fill="{palette[ch]}"/>' for ch, d in runs.items())


def star(cx, cy, r, color, extra=""):
    """A five-point star with rounded tips, like the stars on Jelajah Kerinci's stamps."""
    points = " ".join(
        f"{cx + (r if i % 2 == 0 else r * 0.47) * math.cos(math.pi * (i / 5 - 0.5)):.2f},"
        f"{cy + (r if i % 2 == 0 else r * 0.47) * math.sin(math.pi * (i / 5 - 0.5)):.2f}"
        for i in range(10)
    )
    return (f'<polygon points="{points}" fill="{color}" stroke="{color}" stroke-width="{r * 0.25:.2f}" '
            f'stroke-linejoin="round"{extra}/>')


# Korupsi's own colors, from the game. Its page keeps them in both themes, as a screenshot would.
KR = {
    "wall": "#223238", "ink": "#0d1418", "lamp": "#eef5dd", "wood_hi": "#dba76a", "wood": "#b07a48",
    "wood_dk": "#7c5030", "paper": "#ece4cc", "gold": "#f2c14e", "gold_dk": "#a87b23", "red": "#d9483b",
    "white": "#e8ecef", "pad": "#f08a24", "rod": "#5b6e68", "blind": "#e57c61", "blind_dk": "#b8573f",
}
KR_SPRITE = {"p": "#34333f", "s": "#d9a577", "k": KR["ink"], "c": "#a8946a", "d": "#6a5a3e", "b": "#5a3a26",
             "h": "#1a1a1a", "w": KR["white"], "r": KR["red"], "n": KR["paper"], "g": KR["gold"],
             "f": KR["gold_dk"], "q": KR["wood"], "l": "#9fd3f0", "a": "#2b3446"}
OFFICIAL = (  # the player: a peci, a safari suit and a briefcase, mid-jump
    "...pppp...",
    "..pppppp..",
    "...ssss...",
    "...sssks..",
    "...ssss...",
    "..cccccc..",
    ".scccccccs",
    "...cccccbb",
    "...ddddbbb",
    "..dd..dd..",
    ".dd....dd.",
    ".kk....kk.",
)
AUDITOR = (  # the audit team: glasses, a white shirt with a red tie and ID card, and a clipboard
    "...hhhh..",
    "..hhhhhh.",
    "..lsssh..",
    "..ssss...",
    "...ss....",
    "..wwwwww.",
    ".nwwrwwww",
    "qnnwrwwws",
    "qqnwrrww.",
    "...wwww..",
    "...aaaa..",
    "...a..a..",
    "..kk.kk..",
)
ENVELOPE = (  # the game's own envelope: a gold body, a dark-gold border and flap, and a red ribbon
    ".fffffffff.",
    "fgggggggggf",
    "ffgggggggff",
    "fgffgrgffgf",
    "fgggfrfgggf",
    "fgggggggggf",
    ".fffffffff.",
)


def korupsi(t):
    """Korupsi in a browser: an official in a peci jumps from desk to desk for the envelopes, while a stamp comes
    down and an auditor waits on the top desk."""
    k = KR
    x0, y0, x1, y1 = 36, 48, 464, 126  # the page, below the address bar

    def desk(x, top, w):
        """A desk to land on: a two-tone top over a darker body with a drawer, outlined like the sprites."""
        mid = x + w / 2
        return (f'<rect x="{x - 1}" y="{top - 1}" width="{w + 2}" height="7" fill="{k["ink"]}"/>'
                f'<rect x="{x}" y="{top}" width="{w}" height="2" fill="{k["wood_hi"]}"/>'
                f'<rect x="{x}" y="{top + 2}" width="{w}" height="3" fill="{k["wood"]}"/>'
                f'<rect x="{x + 4}" y="{top + 6}" width="{w - 8}" height="{y1 - top}" fill="{k["ink"]}"/>'
                f'<rect x="{x + 5}" y="{top + 6}" width="{w - 10}" height="{y1 - top}" fill="{k["wood_dk"]}"/>'
                f'<rect x="{mid - 7:g}" y="{top + 10}" width="14" height="5" fill="{k["ink"]}"/>'
                f'<rect x="{mid - 6:g}" y="{top + 11}" width="12" height="3" fill="{k["paper"]}"/>'
                f'<rect x="{mid - 2:g}" y="{top + 12}" width="4" height="1" fill="{k["ink"]}"/>')

    def hud(x, label, color):
        w = 0.6 * 8 * len(label) + 12
        return (f'<rect x="{x:g}" y="{y0 + 5}" width="{w:g}" height="13" rx="2" fill="{k["ink"]}" fill-opacity=".9"/>'
                + text(x + 6, y0 + 14.4, label, size=8, fill=color, weight=700, mono=True)), w

    floor_chip, fw = hud(44, "01 KELURAHAN", k["white"])
    money_chip, _ = hud(44 + fw + 4, "RP 1.500.000", k["gold"])
    lamps = "".join(
        f'<path d="M{lx - 12} {y0 + 2.5}H{lx + 12}L{lx + 30} {y0 + 34}H{lx - 30}Z" fill="{k["lamp"]}" '
        f'fill-opacity=".05"/><rect x="{lx - 12}" y="{y0}" width="24" height="2.5" fill="{k["lamp"]}"/>'
        for lx in (236, 338))
    # A window with its blinds down, on the wall behind the top desk.
    blinds = (f'<rect x="{x1 - 124}" y="{y0 + 10}" width="30" height="26" fill="{k["ink"]}"/>'
              + "".join(f'<rect x="{x1 - 122}" y="{y0 + 12 + i * 4}" width="26" height="3" '
                        f'fill="{k["blind"] if i % 2 == 0 else k["blind_dk"]}"/>' for i in range(6)))
    # A proyek fiktif: the red-and-white ledge that gives way, tipping already.
    plank = (f'<g transform="rotate(7 328 90)"><rect x="313" y="87" width="30" height="6" fill="{k["ink"]}"/>'
             + "".join(f'<rect x="{314 + i * 4}" y="88" width="4" height="4" '
                       f'fill="{k["red"] if i % 2 == 0 else k["white"]}"/>' for i in range(7))
             + "</g>")
    # The stamp hangs over the middle desk and comes down on it every few seconds.
    sx = 271
    stamp = (f'<g class="slam"><rect x="{sx - 1}" y="{y0 - 30}" width="2" height="44" fill="{k["rod"]}"/>'
             f'<rect x="{sx - 5}" y="{y0 + 13}" width="10" height="7" fill="{k["ink"]}"/>'
             f'<rect x="{sx - 4}" y="{y0 + 14}" width="8" height="5" fill="{k["wood"]}"/>'
             f'<rect x="{sx - 9}" y="{y0 + 19}" width="18" height="8" fill="{k["ink"]}"/>'
             f'<rect x="{sx - 8}" y="{y0 + 20}" width="16" height="4" fill="{k["wood_dk"]}"/>'
             f'<rect x="{sx - 8}" y="{y0 + 24}" width="16" height="2" fill="{k["pad"]}"/></g>')
    page = (
        f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{k["wall"]}"/>'
        + lamps
        + f'<g shape-rendering="crispEdges">{blinds}'
        + desk(44, 108, 88) + desk(200, 96, 92) + desk(362, 82, 94)
        + plank
        + pixels(94, 94, ENVELOPE, KR_SPRITE) + pixels(220, 82, ENVELOPE, KR_SPRITE)
        + pixels(378, 68, ENVELOPE, KR_SPRITE)
        + pixels(418, 56, AUDITOR, KR_SPRITE, outline=k["ink"])
        + stamp
        + f'<g class="hop">{pixels(152, 68, OFFICIAL, KR_SPRITE, outline=k["ink"])}</g></g>'
        + f'<path d="M122 106Q134 84 150 88" fill="none" stroke="{k["white"]}" stroke-opacity=".35" stroke-width="1.5" '
        'stroke-dasharray="2 3" stroke-linecap="round"/>'
        + floor_chip + money_chip
    )
    clip, window = browser(t, "korupsi.web.id", page)
    css = (
        "@keyframes hop{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}"
        ".hop{animation:hop 1.5s ease-in-out infinite}"
        "@keyframes slam{0%,55%{transform:translateY(0)}62%,70%{transform:translateY(20px)}"
        "88%,100%{transform:translateY(0)}}"
        ".slam{animation:slam 3.2s ease-in-out infinite}"
    )
    body = app_card(t, "Korupsi", window, "Climb a bureaucracy, one office at a time.",
                    "Pixel art drawn in code, about 28 KB gzipped.",
                    ["Run, jump, dash", "Ten titles to earn", "Touch controls"],
                    kicker="OPEN SOURCE · BROWSER GAME · MIT")
    label = ("Korupsi, open source browser game under the MIT license: a pixel-art platformer about climbing a "
             "bureaucracy, one office at a time, with the audit team already in the lobby. Run, jump and dash past "
             "the auditors and the stamps, pick up envelopes on the way, and earn one of ten titles. The pixel art is "
             "drawn in code, the whole game is about 28 KB gzipped, and it plays on phones too.")
    return svg(*APP, label, body, clip, css)


# Jelajah Kerinci's own colors, from the game's map. Like Korupsi's, its page keeps them in both themes.
KK = {
    "grass": "#9ad97f", "forest": "#3aa565", "pine": "#1d6b43", "tea": "#63b65a", "tea_dk": "#4f9f4c",
    "water": "#4aa8e8", "water_lt": "#a5d4f4", "trail": "#f7f5d9", "star": "#f5a800", "ink": "#2b2118",
    "cloud": "#f0faec", "leaf": "#c6f38e", "fish": "#f5b942", "rock": "#5f7d8c",
}


def kerinci(t):
    """Jelajah Kerinci in a browser: the game's map of Kerinci, with the summit of Gunung Kerinci still locked, stamps
    earned at the tea gardens of Kayu Aro and at Danau Kerinci, and the trail between them."""
    k = KK
    x0, y0, x1, y1 = 36, 48, 464, 126

    def pin(cx, cy, inner, glyph, badge=""):
        return (f'<circle cx="{cx}" cy="{cy + 1.2}" r="9.5" fill="#000" fill-opacity=".14"/>'
                f'<circle cx="{cx}" cy="{cy}" r="9.5" fill="#fff"/><circle cx="{cx}" cy="{cy}" r="7" fill="{inner}"/>'
                + glyph + badge)

    def stamp_star(cx, cy, delay):
        return (f'<g class="grow pop" style="animation-delay:{delay}s"><circle cx="{cx}" cy="{cy}" r="5" fill="#fff"/>'
                + star(cx, cy, 3.6, k["star"]) + "</g>")

    forest = (f'<path d="M{x0} {y0}H70Q80 64 70 80T76 108Q80 118 72 {y1}H{x0}Z" fill="{k["forest"]}"/>'
              + "".join(f'<path d="M{px} {py - 10}L{px + 5} {py}H{px - 5}Z" fill="{k["pine"]}"/>'
                        for px, py in [(46, 62), (60, 74), (48, 88), (61, 100), (47, 113), (58, 124)]))
    km = 0.25  # Gunung Kerinci, from the icon, its foot below the page
    mountain = (f'<g transform="translate({150 - 256 * km:g} {132 - 380 * km:g}) scale({km})">{KERINCI_MOUNTAIN}</g>'
                f'<g class="drift"><ellipse cx="154" cy="64" rx="8.5" ry="4.2" fill="{k["cloud"]}" fill-opacity=".95"/>'
                f'<ellipse cx="163" cy="57.5" rx="6" ry="3.2" fill="{k["cloud"]}" fill-opacity=".75"/></g>')
    tea = (f'<ellipse cx="258" cy="110" rx="46" ry="18" fill="{k["tea"]}"/>'
           + "".join(f'<path d="M{258 - w} {cy}Q258 {cy - 8} {258 + w} {cy}" fill="none" stroke="{k["tea_dk"]}" '
                     'stroke-width="2.2" stroke-linecap="round"/>' for w, cy in [(30, 102), (40, 110), (36, 119)]))
    water = (f'<path d="M292 116C314 128 330 100 356 110" fill="none" stroke="{k["water"]}" stroke-width="4" '
             'stroke-linecap="round"/>'
             f'<ellipse cx="404" cy="112" rx="52" ry="16" fill="{k["water"]}"/>'
             f'<ellipse cx="394" cy="107" rx="22" ry="3.6" fill="{k["water_lt"]}" fill-opacity=".7"/>')
    trail = (f'<path class="trail" d="M150 92Q204 68 258 90T404 100" fill="none" stroke="{k["trail"]}" '
             'stroke-width="2.6" stroke-dasharray="0 6" stroke-linecap="round"/>')
    # Gunung Kerinci's pin is locked: the summit opens last.
    mx, my = 150, 92
    mountain_pin = pin(mx, my, k["rock"],
                       f'<path d="M{mx - 4.6} {my + 3}L{mx - 1} {my - 3.2}L{mx + 1} {my - 0.8}L{mx + 2.4} {my - 2.6}'
                       f'L{mx + 5} {my + 3}Z" fill="#fff"/>',
                       f'<circle cx="{mx + 7.5}" cy="{my - 7.5}" r="4.6" fill="#fff"/>'
                       f'<path d="M{mx + 6.3} {my - 8.4}v-1.3a1.2 1.2 0 0 1 2.4 0v1.3" fill="none" stroke="{k["rock"]}" '
                       'stroke-width="1"/>'
                       f'<rect x="{mx + 5.6}" y="{my - 8.4}" width="3.8" height="3.2" rx=".6" fill="{k["rock"]}"/>')
    tx, ty = 258, 90
    tea_pin = pin(tx, ty, k["forest"],
                  f'<path d="M{tx - 4} {ty + 3.6}Q{tx - 4.4} {ty - 4} {tx + 4} {ty - 4}Q{tx + 4.2} {ty + 3.6} {tx - 4} '
                  f'{ty + 3.6}Z" fill="{k["leaf"]}"/><path d="M{tx - 3} {ty + 2.6}L{tx + 2.6} {ty - 3}" '
                  f'stroke="{k["forest"]}" stroke-width=".9"/>',
                  stamp_star(tx + 7.5, ty - 7.5, 0))
    lx, ly = 404, 100
    lake_pin = pin(lx, ly, k["water"],
                   f'<ellipse cx="{lx - 0.8}" cy="{ly}" rx="3.6" ry="2.5" fill="{k["fish"]}"/>'
                   f'<path d="M{lx + 2} {ly}L{lx + 5} {ly - 2.6}V{ly + 2.6}Z" fill="{k["fish"]}"/>'
                   f'<circle cx="{lx - 2.4}" cy="{ly - 0.5}" r=".7" fill="{k["ink"]}"/>',
                   stamp_star(lx + 7.5, ly - 7.5, 1.6))
    hud = (f'<rect x="44" y="{y0 + 6.5}" width="84" height="16" rx="8" fill="#000" fill-opacity=".12"/>'
           f'<rect x="44" y="{y0 + 5}" width="84" height="16" rx="8" fill="#fff"/>'
           + star(54, y0 + 13, 4.4, k["star"])
           + text(62, y0 + 16.4, "Stempel 2/6", size=9.5, fill=k["ink"], weight=700))
    page = (f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{k["grass"]}"/>'
            + forest + mountain + tea + water + trail + mountain_pin + tea_pin + lake_pin + hud)
    clip, window = browser(t, "kerinciku.web.id", page)
    css = (
        "@keyframes walk{to{stroke-dashoffset:-12}}.trail{animation:walk 1.4s linear infinite}"
        "@keyframes pop{0%,74%,100%{transform:scale(1)}82%{transform:scale(1.35)}90%{transform:scale(.92)}}"
        ".pop{animation:pop 4.8s ease-in-out infinite}"
        "@keyframes drift{0%,100%{transform:translateX(0)}50%{transform:translateX(4px)}}"
        ".drift{animation:drift 6s ease-in-out infinite}"
    )
    body = app_card(t, "Jelajah Kerinci", window, "A map game for young kids about Kerinci, Sumatra.",
                    "About 150 KB, and it plays offline.", ["Five mini-games", "Stamps to collect", "Kerinci words"],
                    kicker="OPEN SOURCE · BROWSER GAME · MIT", badge="NEW")
    label = ("Jelajah Kerinci, new open source browser game under the MIT license: young children explore a map of "
             "Kerinci, Sumatra, play a short mini-game at each place and collect stamps, each opening a fact and a "
             "word in the Kerinci language. Five places are playable so far. About 150 KB, made for phones held "
             "upright, and it plays offline after one visit.")
    return svg(*APP, label, body, clip, css)


def slim_card(t, eyebrow_label, name, lines, art):
    """Lines may hold <tspan> markup, so escape plain text before passing it in."""
    return (
        frame(t, 8, 8, SLIM[0] - 16, SLIM[1] - 16)
        + eyebrow(36, 46, eyebrow_label, t["accent"])
        + arrow(452, 35, t["subtle"])
        + text(35, 78, name, size=22, fill=t["fg"], weight=700, spacing=-0.3)
        + "".join(text(36, 105 + i * 21, line, size=14, fill=t["muted"]) for i, line in enumerate(lines))
        + art
    )


def kiro(t):
    def keycap(kx, ch):
        return (
            f'<rect x="{kx}" y="74" width="34" height="34" rx="8" fill="{t["raised"]}" stroke="{t["border"]}"/>'
            f'<rect x="{kx + 3}" y="76" width="28" height="27" rx="6" fill="none" stroke="{t["border"]}" '
            'stroke-opacity=".6"/>'
            + text(kx + 17, 96, escape(ch), size=17, fill=t["fg"], weight=600, mono=True, anchor="middle")
        )

    art = (keycap(360, "\\") + text(413, 97, "≠", size=20, fill=t["red"], weight=700, anchor="middle")
           + keycap(430, "/") + text(413, 128, "#9507", size=11, fill=t["subtle"], mono=True, anchor="middle"))
    mono = f'<tspan class="mono" fill="{t["fg"]}">'
    body = slim_card(t, "CONTRIBUTION", "Kiro CLI", [
        "Traced the “Always allow” loop to its",
        f"policy compiler turning {mono}\\</tspan> into {mono}/</tspan>.",
    ], art)
    label = ("Contribution to Kiro CLI: traced the Always allow approval loop to its policy compiler turning "
             "backslashes into slashes in shell rules. Root cause and a fix in kirodotdev/Kiro#9507.")
    return svg(*SLIM, label, body)


def elysiumx(t):
    a, p = (372, 92), (440, 92)
    art = (
        f'<circle cx="{a[0]}" cy="{a[1]}" r="18" fill="{t["accent"]}" fill-opacity="{t["tint"] * 1.6:.2f}" '
        f'stroke="{t["accent"]}" stroke-opacity="{t["edge"]}"/>'
        f'<path d="M{a[0]} {a[1] - 9}C{a[0] + 1.4} {a[1] - 2} {a[0] + 2} {a[1] - 1.4} {a[0] + 9} {a[1]}'
        f'C{a[0] + 2} {a[1] + 1.4} {a[0] + 1.4} {a[1] + 2} {a[0]} {a[1] + 9}C{a[0] - 1.4} {a[1] + 2} {a[0] - 2} '
        f'{a[1] + 1.4} {a[0] - 9} {a[1]}C{a[0] - 2} {a[1] - 1.4} {a[0] - 1.4} {a[1] - 2} {a[0]} {a[1] - 9}Z" '
        f'fill="{t["accent"]}"/>'
        f'<path d="M{a[0] + 24} {a[1]}H{p[0] - 26}" stroke="{t["subtle"]}" stroke-width="1.6" '
        'stroke-dasharray="3 4" stroke-linecap="round"/>'
        f'<path d="M{p[0] - 30} {a[1] - 4}l4 4-4 4" fill="none" stroke="{t["subtle"]}" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{p[0]}" cy="{p[1]}" r="18" fill="{t["raised"]}" stroke="{t["border"]}"/>'
        f'<circle cx="{p[0]}" cy="{p[1] - 4.5}" r="4.6" fill="{t["muted"]}"/>'
        f'<path d="M{p[0] - 9} {p[1] + 10}a9 7.5 0 0 1 18 0Z" fill="{t["muted"]}"/>'
        f'<circle cx="{p[0] + 13}" cy="{p[1] - 13}" r="7" fill="{t["green"]}" stroke="{t["card"]}" stroke-width="2"/>'
        f'<path d="M{p[0] + 10} {p[1] - 13}l2 2 3.6-4" fill="none" stroke="#fff" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )
    body = slim_card(t, "SIDE PROJECT", "ElysiumX", [
        "A public experiment in letting AI agents",
        "run apps while people keep the final call.",
    ], art)
    label = ("Side project: ElysiumX, a public experiment in letting AI agents run apps while people keep the final "
             "call. elysiumx.org")
    return svg(*SLIM, label, body)


# --------------------------------------------------------------------------------------------- buttons


def button(t, label, icon, primary=False):
    # The same 10 units above and below the button keep the row evenly spaced between the hero and the cards.
    W, H = 184, 60
    bg = t["primary"] if primary else t["button"]
    ink = "#ffffff" if primary else t["fg"]
    content_w = 18 + 9 + width(label, 14.5, bold=True)
    start = W / 2 - content_w / 2
    body = (
        f'<rect x="4" y="10" width="176" height="40" rx="20" fill="{bg}"'
        + ("" if primary else f' stroke="{t["border"]}"') + "/>"
        + icon(start, 21, ink)
        + text(start + 27, 35, escape(label), size=14.5, fill=ink, weight=600)
    )
    return svg(W, H, label, body)


def globe(x, y, c):
    return (f'<g fill="none" stroke="{c}" stroke-width="1.5"><circle cx="{x + 9}" cy="{y + 9}" r="8"/>'
            f'<path d="M{x + 1} {y + 9}h16M{x + 9} {y + 1}c-4.5 4.5-4.5 11.5 0 16M{x + 9} {y + 1}c4.5 4.5 4.5 11.5 0 16"/>'
            "</g>")


def linkedin(x, y, c):
    return (f'<rect x="{x}" y="{y}" width="18" height="18" rx="4" fill="#0a66c2"/>'
            + text(x + 9.2, y + 13.6, "in", size=12, fill="#fff", weight=700, anchor="middle", spacing=-0.3))


def envelope(x, y, c):
    return (f'<g fill="none" stroke="{c}" stroke-width="1.6" stroke-linejoin="round">'
            f'<rect x="{x + 0.8}" y="{y + 2.8}" width="16.4" height="12.4" rx="2.2"/>'
            f'<path d="M{x + 1.5} {y + 4}l7.5 5.6 7.5-5.6"/></g>')


# Logos from Simple Icons (CC0), drawn on tiles that match skillicons.dev's neutral style.
OPENAI = "M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z"
ANTHROPIC = ("M17.3041 3.541h-3.6718l6.696 16.918H24Zm-10.6082 0L0 20.459h3.7442l1.3693-3.5527h7.0052l1.3693 3.5528h3.7442"
             "L10.5363 3.5409Zm-.3712 10.2232 2.2914-5.9456 2.2914 5.9456Z")


def ai_tiles(t):
    """OpenAI and Anthropic, to sit right after the skillicons row at the same height."""
    tile, ink = ("#242938", "#ffffff") if t is THEMES["dark"] else ("#F4F2ED", "#191919")
    tiles = "".join(
        f'<rect x="{44 + i * 300}" width="256" height="256" rx="60" fill="{tile}"/>'
        f'<path transform="translate({102 + i * 300} 58) scale(5.8333)" d="{path}" fill="{ink}"/>'
        for i, path in enumerate([OPENAI, ANTHROPIC])
    )
    return svg(600, 256, "OpenAI and Anthropic", tiles)


CARDS = {
    "hero": hero, "opustock": opustock, "nyetok": nyetok, "havus": havus, "jambul": jambul,
    "korupsi": korupsi, "kerinci": kerinci, "kiro": kiro, "elysiumx": elysiumx,
    "btn-website": lambda t: button(t, "debikurnia.id", globe),
    "btn-linkedin": lambda t: button(t, "LinkedIn", linkedin),
    "btn-email": lambda t: button(t, "Email me", envelope, primary=True),
    "stack-ai": ai_tiles,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, build in CARDS.items():
        for theme, tokens in THEMES.items():
            (OUT / f"{name}-{theme}.svg").write_text(build(tokens), encoding="utf-8")
    print(f"wrote {len(CARDS) * len(THEMES)} files to {OUT.relative_to(Path.cwd()) if OUT.is_relative_to(Path.cwd()) else OUT}")


if __name__ == "__main__":
    main()
