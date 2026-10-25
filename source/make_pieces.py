"""Retro 1980s broadcast-style chess pieces -> transparent PNGs.

Original shapes, styled after the soft cream / glowing-red look of early
TV chess graphics. Produces a crisp set and a CRT-smeared set.
"""
import os, io
import numpy as np
import cairosvg
from PIL import Image, ImageFilter

OUT = os.path.dirname(os.path.abspath(__file__))
SIZE = 512

STYLES = {
    "white": dict(hi="#fffaf0", mid="#fdebd4", lo="#f0b493",
                  outline="#eab79c", detail="#cf8d70", slot="#6e2c1c", inset="#5e2414", ring="#e2a98a", rim="#fff6ea", ow=2.0, dw=1.8),
    "red": dict(hi="#f8875c", mid="#e2553a", lo="#ab2a1b",
                  outline="#ffdcc4", detail="#ffd6b8", slot="#4a0f0a", inset="#ffe2cc", ring="#5a140c", rim="#ffe8d2", ow=3.0, dw=2.2),
    "black": dict(hi="#4a4a50", mid="#1e1e22", lo="#050507",
                  outline="#efe3cf", detail="#e6d8c2", slot="#000000", inset="#efe3cf", ring="#000000", rim="#f6ecdc", ow=3.0, dw=2.2),
    "brown": dict(hi="#5e3e28", mid="#341f12", lo="#120804",
                  outline="#f0d6b4", detail="#ecd0aa", slot="#0a0503", inset="#f0d6b4", ring="#0a0503", rim="#f6e2c6", ow=3.0, dw=2.2),
}

# ---- shapes (viewBox 0 0 100 100), traced from enhanced broadcast frames.
# Each shape returns a list of parts drawn back-to-front: (kind, path)
# kind: "body" = filled + outlined, "slot" = dark recess, "line" = detail stroke

def rr(x0, y0, x1, y1, r):
    return (f"M{x0+r},{y0} L{x1-r},{y0} Q{x1},{y0} {x1},{y0+r} L{x1},{y1-r} Q{x1},{y1} {x1-r},{y1} "
            f"L{x0+r},{y1} Q{x0},{y1} {x0},{y1-r} L{x0},{y0+r} Q{x0},{y0} {x0+r},{y0} Z")

def circ(cx, cy, r):
    return f"M{cx-r},{cy} A{r},{r} 0 1 0 {cx+r},{cy} A{r},{r} 0 1 0 {cx-r},{cy} Z"

def ell(cx, cy, rx, ry):
    return f"M{cx-rx},{cy} A{rx},{ry} 0 1 0 {cx+rx},{cy} A{rx},{ry} 0 1 0 {cx-rx},{cy} Z"

def plate(x0, x1, y0=88, y1=94):
    return ("body", rr(x0, y0, x1, y1, 2.5))

def pawn():
    # first-version pawn: merged silhouette, round head
    body = [
        "M22,86 L22,80 Q22,74 30,73 L70,73 Q78,74 78,80 L78,86 Z",
        "M38,73 C40,62 43,52 44,44 L56,44 C57,52 60,62 62,73 Z",
        "M34,42 Q34,37 40,37 L60,37 Q66,37 66,42 Q66,46 60,46 L40,46 Q34,46 34,42 Z",
        "M50,13 A11,11 0 1 1 49.99,13 Z",
    ]
    parts = [("stroke", p) for p in body] + [("fill", p) for p in body]
    parts += [("line", "M24,80.5 L76,80.5"), ("line", "M41,64 L59,64"), ("rim", "M24,85 L76,85")]
    return parts, "translate(0,3)"

def rook():
    sil = ("M18,8 L35,8 L35,11 L44,11 L44,8 L56,8 L56,11 L65,11 L65,8 L82,8 "
           "L82,29 L72,35 L72,63 L82,69 L82,86 L18,86 L18,69 L28,63 L28,35 L18,29 Z")
    return [
        plate(16, 84, 86, 92),
        ("body", sil),
    ]

def bishop():
    skirt = ("M20,89 C20,83 27,79 34,79 L66,79 C73,79 80,83 80,89 "
             "C76,93 71,90 66,92 C61,94 55,90 50,92 C45,90 39,94 34,92 C29,90 24,93 20,89 Z")
    return [
        ("body", skirt),
        ("slot", rr(35, 67, 65, 73, 1.5)),
        ("body", rr(31, 72, 69, 80, 2.5)),
        # mitre: pointed teardrop with the customary diagonal slit
        ("body", "M50,13 C58,19 75,33 75,49 C75,61 68,67 61,69 L39,69 C32,67 25,61 25,49 C25,33 42,19 50,13 Z"),
        ("cut", "M82.6,22.8 L81.4,21.2 L48.4,43.9 Q47.6,45.6 49.5,45.4 Z"),                  # diagonal slit cut in from the edge
        ("body", circ(50, 9, 5)),                                   # small ball finial
    ]

def knight():
    # Traced from the user's pencil sketch (pixel coords), mapped into the 100-unit square.
    X0, Y0, SX, SY = 340, 630, 0.108, 76 / 1110
    xoff = 50 - (1120 - 340) * SX / 2
    YT = 12
    def P(*pts):
        return " ".join(f"{xoff + (x - X0) * SX:.1f},{YT + (y - Y0) * SY:.1f}" for x, y in pts)
    head = (f"M{P((382,1736))} "
            f"C{P((360,1500),(380,1150),(470,960))} "        # back, lower
            f"C{P((560,800),(680,700),(790,668))} "          # back, upper
            f"C{P((830,652),(862,634),(890,626))} "          # rear ear, rising straight off the back
            f"L{P((903,694))} "                              # notch between ears
            f"C{P((925,672),(946,656),(978,650))} "          # front ear, curving forward
            f"C{P((952,690),(922,730),(910,776))} "          # front edge of ear
            f"C{P((902,830),(906,872),(928,898))} "          # concave forehead
            f"C{P((1002,1014),(1088,1196),(1129,1338))} "      # long nose bridge
            f"C{P((1139,1366),(1140,1392),(1123,1406))} "      # subtly rounded nose tip
            f"L{P((1011,1564))} "                             # angled nose end
            f"L{P((846,1392))} "                             # under the chin
            f"C{P((876,1500),(902,1610),(914,1736))} Z")                           # throat to base
    ex, ey = xoff + (868 - X0) * SX, YT + (1065 - Y0) * SY
    nx, ny = xoff + (1049 - X0) * SX, YT + (1404 - Y0) * SY
    return [
        plate(xoff + (330 - X0) * SX, xoff + (940 - X0) * SX, 88, 94),
        ("body", head),
        ("slot", circ(ex, ey, 2.8)),                                          # eye
        ("slot", circ(nx, ny, 1.6)),                                          # nostril
    ]

def squeeze_x(path, k, cx=50):
    """Scale a path's x coordinates about cx (paths here use absolute M/L/C/Q commands only)."""
    import re
    def f(m):
        x, y = float(m.group(1)), m.group(2)
        return f"{cx + (x - cx) * k:.2f},{y}"
    return re.sub(r"(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)", f, path)

def king():
    # classic king: cross, dome peeking between two broad lobes, short solid band underneath
    K = 0.86
    body = ("M50,46 C46,36 34,31 22,33 C9,36 4,49 10,59 C13,64 16,67 17,71 L17,79 "
            "Q17,84 22,84 L78,84 Q83,84 83,79 L83,71 C84,67 87,64 90,59 "
            "C96,49 91,36 78,33 C66,31 54,36 50,46 Z")
    return [
        ("body", "M47,6 L53,6 L53,12 L59,12 L59,18 L53,18 L53,28 L47,28 L47,18 L41,18 L41,12 L47,12 Z"),  # cross
        ("body", ell(50, 37, 9, 9.5)),                                                  # dome
        ("body", squeeze_x(body, K)),
        ("line", squeeze_x("M17,70 Q50,63 83,70", K)),                                # top of the band
        ("slot", squeeze_x("M29,76 Q50,79.5 71,76 Q71,80.5 50,81.5 Q29,80.5 29,76 Z", K)),  # dark slot
    ]

def queen():
    # one continuous silhouette: curved rim -> gently waisted cup -> flared foot
    sil = ("M15,28.5 C35,19.5 65,19.5 85,28.5 Q90,28.5 90,32 L88,38 Q87,40 84,40 L82,40 "
           "C76,48 71,57 70,65 C69,74 78,79 81,86 Q82,92 73,92 L27,92 Q18,92 19,86 "
           "C22,79 31,74 30,65 C29,57 24,48 18,40 L16,40 Q13,40 12,38 L10,32 Q10,28.5 15,28.5 Z")
    parts = [("body", sil),
             ("line", "M14,37.5 C34,28.5 66,28.5 86,37.5"),         # lip under the crown's top edge
             ("line", "M27,77 Q50,81 73,77")]                       # single ring on the lower portion
    # four balls floating just above the crown rim, with a small gap
    parts += [("body", circ(x, y, 7)) for x, y in [(17, 16), (38, 10), (62, 10), (83, 16)]]
    return parts

FIT = {}

SHAPES = dict(pawn=pawn, rook=rook, knight=knight, bishop=bishop, queen=queen, king=king)


def svg_for(shape, color, mask=False):
    st = STYLES[color]
    defs = f"""
  <defs>
    <radialGradient id="f" cx="0.38" cy="0.35" r="0.75">
      <stop offset="0" stop-color="{st['hi']}"/>
      <stop offset="0.5" stop-color="{st['mid']}"/>
      <stop offset="1" stop-color="{st['lo']}"/>
    </radialGradient>
  </defs>"""
    res = SHAPES[shape]()
    parts, tf = res if isinstance(res, tuple) else (res, "translate(0,0)")
    tf = (FIT.get(shape, "") + " " + tf).strip()
    out = []
    cuts = [d for k, d in parts if k == "cut"]
    for kind, d in parts:
        if kind == "cut":
            continue
        if kind == "body":
            out.append(f'<path d="{d}" fill="url(#f)" stroke="{st["outline"]}" stroke-width="{st["ow"]}" stroke-linejoin="round"/>')
        elif kind == "slot":
            out.append(f'<path d="{d}" fill="{st["slot"]}" stroke="{st["outline"]}" stroke-width="{st["ow"]*0.6}" stroke-linejoin="round"/>')
        elif kind == "stroke":
            out.append(f'<path d="{d}" fill="url(#f)" stroke="{st["outline"]}" stroke-width="{st["ow"]}" stroke-linejoin="round"/>')
        elif kind == "fill":
            out.append(f'<path d="{d}" fill="url(#f)"/>')
        elif kind == "inset":
            out.append(f'<path d="{d}" fill="{st["inset"]}" stroke="{st["ring"]}" stroke-width="{st["ow"]}"/>')
        elif kind == "rim":
            out.append(f'<path d="{d}" fill="none" stroke="{st["rim"]}" stroke-width="2.4" stroke-linecap="round"/>')
        else:
            out.append(f'<path d="{d}" fill="none" stroke="{st["detail"]}" stroke-width="{st["dw"]}" stroke-linecap="round"/>')
    group = "".join(out)
    if cuts:
        ow = st["ow"]
        edge = "".join(f'<path d="{d}" fill="none" stroke="{st["outline"]}" stroke-width="{ow * 1.2}" stroke-linejoin="round"/>' for d in cuts)
        # outline along the cut, clipped to the piece so it only shows inside the body
        defs = defs.replace("</defs>", '<clipPath id="c">' + "".join(
            f'<path d="{d}"/>' for k, d in parts if k == "body") + '</clipPath></defs>')
        group = f'{group}<g clip-path="url(#c)">{edge}</g>'
        if mask:
            hole = "".join(f'<path d="{d}" fill="black"/>' for d in cuts)
            defs = defs.replace("</defs>", '<mask id="m" maskUnits="userSpaceOnUse" x="-10" y="-10" width="120" height="120">'
                                            f'<rect x="-10" y="-10" width="120" height="120" fill="white"/>{hole}</mask></defs>')
            group = f'<g mask="url(#m)">{group}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{SIZE}" height="{SIZE}">'
            f'{defs}<g transform="{tf}">{group}</g></svg>')


def cut_out(img, shape):
    res = SHAPES[shape]()
    parts, tf = res if isinstance(res, tuple) else (res, "translate(0,0)")
    tf = (FIT.get(shape, "") + " " + tf).strip()
    cuts = [d for k, d in parts if k == "cut"]
    if not cuts:
        return img
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{SIZE}" height="{SIZE}">'
           f'<g transform="{tf}">' + "".join(f'<path d="{d}" fill="black"/>' for d in cuts) + '</g></svg>')
    m = np.asarray(render(svg))[..., 3].astype(np.float32) / 255
    a = np.asarray(img).copy()
    a[..., 3] = (a[..., 3] * (1 - m)).astype(np.uint8)
    return Image.fromarray(a)


def wood_grain(img, seed=7):
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # long, gently wavy vertical grain lines
    warp = 9 * np.sin(yy / 61 + 1.3) + 5 * np.sin(yy / 23 + xx / 140)
    phase = rng.uniform(0, 6.28, 3)
    g = (0.55 * np.sin((xx + warp) / 5.5 + phase[0])
         + 0.30 * np.sin((xx + 1.7 * warp) / 13 + phase[1])
         + 0.15 * np.sin((xx + 0.6 * warp) / 2.6 + phase[2]))
    lum = a[..., :3].mean(-1)
    body = np.clip((175 - lum) / 60, 0, 1) * (a[..., 3] / 255)   # only darker body pixels, not the cream outline
    a[..., :3] *= (1 + 0.16 * g * body)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def render(svg):
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=SIZE, output_height=SIZE)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def crt(img):
    """Soft NTSC/VHS look: horizontal smear, chroma offset, glow, scanlines."""
    a = np.asarray(img).astype(np.float32) / 255.0
    rgb, al = a[..., :3] * a[..., 3:4], a[..., 3]          # premultiply

    def hblur(x, n):
        k = np.ones(n) / n
        return np.apply_along_axis(lambda r: np.convolve(r, k, mode="same"), 1, x)

    # horizontal smear with a trailing streak to the right
    def smear(ch):
        base = hblur(ch, 9)
        trail = np.roll(hblur(ch, 31), 10, axis=1)
        return np.maximum(base, trail * 0.55)

    r = smear(np.roll(rgb[..., 0], 4, axis=1))
    g = smear(rgb[..., 1])
    b = smear(np.roll(rgb[..., 2], -3, axis=1))
    al2 = np.maximum(np.maximum(smear(np.roll(al, 4, axis=1)), smear(al)), smear(np.roll(al, -3, axis=1)))

    out = np.stack([r, g, b], -1)
    # glow
    glow_img = Image.fromarray((np.dstack([out, al2]).clip(0, 1) * 255).astype(np.uint8))
    glow = np.asarray(glow_img.filter(ImageFilter.GaussianBlur(10))).astype(np.float32) / 255
    out = out + glow[..., :3] * 0.35
    al2 = np.maximum(al2, glow[..., 3] * 0.45)

    # scanlines (every 4px at 512 ~ a TV line)
    rows = np.arange(out.shape[0])
    scan = np.where((rows // 2) % 2 == 0, 1.0, 0.82)[:, None]
    out *= scan[..., None]
    al2 = al2 * (0.88 + 0.12 * scan)

    # un-premultiply
    safe = np.where(al2 > 1e-4, al2, 1)
    col = (out / safe[..., None]).clip(0, 1)
    res = np.dstack([col, al2.clip(0, 1)])
    return Image.fromarray((res * 255).astype(np.uint8))


def board_preview(tiles, path, cell=160):
    order = ["king", "queen", "rook", "bishop", "knight", "pawn"]
    W, H = cell * 6, cell * 2
    sheet = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    green, dark = (34, 112, 82, 255), (50, 52, 56, 255)
    for row, color in enumerate(["white", "black"]):
        for col, name in enumerate(order):
            sq = Image.new("RGBA", (cell, cell), green if (row + col) % 2 == 0 else dark)
            p = tiles[(color, name)].resize((cell, cell), Image.LANCZOS)
            sq.alpha_composite(p)
            sheet.paste(sq, (col * cell, row * cell))
    sheet.convert("RGB").save(path)


TOP, BASE = 6.5, 94.5          # shared top line and baseline (viewBox units)


def fit_all():
    """Scale back-rank pieces to one uniform height on a shared baseline; drop pawns onto the baseline."""
    FIT.clear()
    for name in SHAPES:
        bb = render(svg_for(name, "black")).getbbox()
        x0, y0, x1, y1 = (v * 100 / SIZE for v in bb)
        cx = (x0 + x1) / 2
        s = 1.0 if name == "pawn" else (BASE - TOP) / (y1 - y0)
        FIT[name] = f"translate(50,{BASE}) scale({s:.4f}) translate({-cx:.2f},{-y1:.2f})"


if __name__ == "__main__":
    fit_all()
    for d in ("clean", "crt"):
        os.makedirs(os.path.join(OUT, "retro-chess-pieces", d), exist_ok=True)
    clean, soft = {}, {}
    for color in STYLES:
        for name in SHAPES:
            img = cut_out(render(svg_for(name, color)), name)
            if color == "brown":
                img = wood_grain(img)
            clean[(color, name)] = img
            soft[(color, name)] = crt(img)
            fn = f"{color}_{name}.png"
            img.save(os.path.join(OUT, "retro-chess-pieces", "clean", fn))
            soft[(color, name)].save(os.path.join(OUT, "retro-chess-pieces", "crt", fn))
    board_preview(clean, os.path.join(OUT, "preview_clean.png"))
    board_preview(soft, os.path.join(OUT, "preview_crt.png"))
    print("done")
