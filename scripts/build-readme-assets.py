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
        "thumb_glyph": 0.75,
    },
    "dark": {
        "card": "#161b22", "raised": "#0d1117", "border": "#30363d", "fg": "#e6edf3",
        "muted": "#9198a1", "subtle": "#7d8590", "accent": "#a371f7", "indigo": "#818cf8",
        "green": "#3fb950", "blue": "#4493f8", "red": "#f85149", "grid": 0.05, "glow": 0.22,
        "tint": 0.13, "edge": 0.38, "skeleton": 0.16, "button": "#21262d", "primary": "#8957e5",
        "wall_a": "#221a4d", "wall_b": "#0c1a33", "menubar": "#000000", "menubar_opacity": 0.35,
        "thumb_glyph": 0.45,
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


def app_card(t, name, art, desc, stat, labels):
    chip_row, _ = chips(t, 36, 258, labels, t["accent"], size=12, pad=10, ink=t["fg"])
    return (
        frame(t, 8, 8, APP[0] - 16, APP[1] - 16)
        + art
        + eyebrow(36, 158, "OPEN SOURCE · MACOS · MIT", t["accent"])
        + arrow(452, 147, t["subtle"])
        + text(35, 193, name, size=28, fill=t["fg"], weight=700, spacing=-0.4)
        + text(36, 221, escape(desc), size=15.5, fill=t["fg"])
        + text(36, 244, escape(stat), size=14, fill=t["muted"])
        + chip_row
    )


def xspace(t):
    wx, wy, ww, wh = 36, 30, 428, 96
    pane = ww / 3
    colors = [t["accent"], t["blue"], t["green"]]
    art = [
        f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="10" fill="{t["raised"]}" stroke="{t["border"]}"/>',
        f'<path d="M{wx} {wy + 21}H{wx + ww}" stroke="{t["border"]}"/>',
    ]
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        art.append(f'<circle cx="{wx + 14 + i * 13}" cy="{wy + 10.5}" r="3.8" fill="{c}"/>')
    for i, c in enumerate(colors):
        px = wx + i * pane
        # Tint each pane; the outer two follow the window's rounded bottom corners.
        top, bottom, right = wy + 21, wy + wh, px + pane
        if i == 0:
            tint = f"M{px + 10:.1f} {bottom}a10 10 0 0 1-10-10V{top}H{right:.1f}V{bottom}Z"
        elif i == 2:
            tint = f"M{px:.1f} {top}H{right:.1f}V{bottom - 10}a10 10 0 0 1-10 10H{px:.1f}Z"
        else:
            tint = f"M{px:.1f} {top}H{right:.1f}V{bottom}H{px:.1f}Z"
        art.append(f'<path d="{tint}" fill="{c}" fill-opacity=".06"/>')
        if i:
            art.append(f'<path d="M{px:.1f} {wy + 21}V{wy + wh}" stroke="{t["border"]}"/>')
        art.append(f'<circle cx="{px + 20:.1f}" cy="{wy + 37}" r="7.5" fill="{c}"/>')
        art.append(f'<rect x="{px + 33:.1f}" y="{wy + 33.5}" width="58" height="7" rx="3.5" fill="{t["fg"]}" '
                   f'fill-opacity="{t["skeleton"] * 2:.2f}"/>')
        for j, lw in enumerate([108, 88, 100]):
            art.append(f'<rect x="{px + 14:.1f}" y="{wy + 54 + j * 13}" width="{lw}" height="6" rx="3" '
                       f'fill="{t["fg"]}" fill-opacity="{t["skeleton"]}"/>')
    body = app_card(t, "XSpace", "".join(art), "Isolated browser profiles in one window.",
                    "In my test: 536 MB vs 964 MB in Chrome.", ["Swift + WebKit", "App Sandbox", "No telemetry"])
    label = ("XSpace, open source macOS app under the MIT license: several isolated browser profiles in one window, "
             "each with its own cookies and logins. Native Swift and WebKit; in my test the same pages used 536 MB "
             "in XSpace versus 964 MB in Chrome. App Sandbox, no telemetry.")
    return svg(*APP, label, body)


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
                    "In my test: 0% CPU idle, about 14 MB.", ["Timer", "Keep Awake", "Battery peeks"])
    label = ("Jambul, open source macOS app under the MIT license: a Dynamic Island for the MacBook notch, with a "
             "timer, Keep Awake and battery peeks. In my test it idled at 0% CPU and about 14 MB of memory.")
    return svg(*APP, label, body, defs, css)


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
    "hero": hero, "opustock": opustock, "xspace": xspace, "jambul": jambul, "kiro": kiro, "elysiumx": elysiumx,
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
