"""Talli Display: Barlow Condensed SemiBold (jpt/barlow, SIL Open Font License 1.1, no reserved name), renamed.

The face for the one big number on Home. Condensed, DIN-like and plain, so it can be drawn very tall and still look
like a sign, not a stretched photo. Same method as Coda's Quip Sans and Turing's Samantha Sans: pinned release,
renamed, OFL shipped beside the fonts, original copyright kept in the name table. Figures are respaced to be
proportional (Joshua, 2026-10-20). Latin only, every build the same bytes.

    uv run --with fonttools --with brotli python3 scripts/gen_font.py           # web/fonts/*.woff2, fonts/*.ttf, OFL.txt
    uv run --with fonttools --with brotli python3 scripts/gen_font.py --check   # named Talli Display, OFL present, proportional
"""
import io
import os
import sys
import urllib.request

from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB, APPLE = os.path.join(HERE, "web", "fonts"), os.path.join(HERE, "fonts")
SOURCE = "https://cdn.jsdelivr.net/npm/@fontsource/barlow-condensed@5.2.6/"
STYLE, WEIGHT = "Semibold", 600
NAME = "TalliDisplay-" + STYLE


def fetch(path):
    """Bytes of one file from the pinned Barlow Condensed release."""
    with urllib.request.urlopen(SOURCE + path, timeout=60) as r:
        return r.read()


def proportional_figures(font):
    """Barlow's figures are tabular (one width), so respace them: each digit keeps the 0's side bearings around
    its own ink. A 1 no longer sits in a 0-wide slot, which is the gap that made "$1" look loose."""
    glyf, hmtx, cmap = font["glyf"], font["hmtx"], font.getBestCmap()
    zero = glyf[cmap[ord("0")]]
    left, right = zero.xMin, hmtx[cmap[ord("0")]][0] - zero.xMax
    for d in "0123456789":
        name = cmap[ord(d)]
        g = glyf[name]
        g.coordinates.translate((left - g.xMin, 0))
        g.recalcBounds(glyf)
        hmtx[name] = (round(g.xMax - g.xMin + left + right), g.xMin)


def rename(font):
    """Give the outlines the Talli Display name; copyright (0) and license (13, 14) stay as the authors wrote them."""
    names = {1: "Talli Display", 2: STYLE, 3: NAME, 4: "Talli Display " + STYLE, 5: "Version 1.000",
             6: NAME, 16: "Talli Display", 17: STYLE}
    table = font["name"]
    table.names = [n for n in table.names if n.nameID in (0, 13, 14)]
    for nid, text in names.items():
        table.setName(text, nid, 3, 1, 0x409)
        table.setName(text, nid, 1, 0, 0)
    font["head"].created = font["head"].modified = 3_700_000_000   # fixed, so every build is the same bytes
    font["OS/2"].achVendID = "TALI"


def to_bytes(font, flavor):
    """The font as TTF (flavor None) or WOFF2 bytes."""
    font.flavor = flavor
    buf = io.BytesIO()
    font.save(buf, reorderTables=False)
    return buf.getvalue()


def check():
    """Self-check of the shipped files."""
    for d in (WEB, APPLE):
        assert os.path.exists(os.path.join(d, "OFL.txt")), "the OFL must ship with the fonts"
    for path in (os.path.join(WEB, NAME + ".woff2"), os.path.join(APPLE, NAME + ".ttf")):
        f = TTFont(path)
        assert f["name"].getDebugName(1) == "Talli Display" and f["name"].getDebugName(6) == NAME
        cmap, hmtx = f.getBestCmap(), f["hmtx"]
        assert hmtx[cmap[ord("1")]][0] < hmtx[cmap[ord("0")]][0], "figures are not proportional"
        assert all(ord(c) in cmap for c in "$0123456789,."), "the amount needs $, digits, comma and point"
    # the web hero lays the amount out from a copy of the advances; it must match the font
    import json, re
    html = open(os.path.join(HERE, "web", "unified.html")).read()
    table = json.loads(re.search(r"const TD_ADVANCE = (\{[^}]+\})", html).group(1).replace("'", '"'))
    f = TTFont(os.path.join(APPLE, NAME + ".ttf"))
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    assert table == {c: hmtx[cmap[ord(c)]][0] for c in table}, "TD_ADVANCE in web/unified.html drifted from the font"
    print("font ok: Talli Display (Barlow Condensed, OFL), proportional figures")


def main():
    """Fetch Barlow Condensed, respace its figures, rename it, write the web and Apple files and the license."""
    if "--check" in sys.argv:
        return check()
    font = TTFont(io.BytesIO(fetch(f"files/barlow-condensed-latin-{WEIGHT}-normal.woff2")))
    proportional_figures(font)
    rename(font)
    ofl = fetch("LICENSE")
    for d, ext, flavor in ((WEB, "woff2", "woff2"), (APPLE, "ttf", None)):
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "OFL.txt"), "wb") as f:
            f.write(ofl)
        with open(os.path.join(d, f"{NAME}.{ext}"), "wb") as f:
            f.write(to_bytes(font, flavor))
    print(f"{NAME}: Barlow Condensed {WEIGHT}")


if __name__ == "__main__":
    main()
