"""Starting position on a traditional wooden board (maple & walnut squares, walnut frame)."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

variant = sys.argv[1] if len(sys.argv) > 1 else "clean"
light_set = sys.argv[2] if len(sys.argv) > 2 else "white"
dark_set = sys.argv[3] if len(sys.argv) > 3 else "brown"
P = f"retro-chess-pieces/{variant}/"
cell, frame = 120, 76
B = cell * 8
W = B + frame * 2
rng = np.random.default_rng(3)


def wood(w, h, base, dark, scale=1.0, seed=0, angle=0.0):
    """Procedural wood texture: wavy grain bands + fine fibres + slight figure."""
    r = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    if angle:
        xx, yy = xx * np.cos(angle) - yy * np.sin(angle), xx * np.sin(angle) + yy * np.cos(angle)
    warp = (7 * np.sin(yy / (47 * scale) + r.uniform(0, 6)) + 4 * np.sin(yy / (17 * scale) + xx / 90 + r.uniform(0, 6)))
    bands = (0.55 * np.sin((xx + warp) / (6.5 * scale) + r.uniform(0, 6))
             + 0.30 * np.sin((xx + 1.8 * warp) / (15 * scale) + r.uniform(0, 6)))
    fibres = r.normal(0, 1, (h, w)).astype(np.float32)
    fibres = np.asarray(Image.fromarray(((fibres * 30) + 128).clip(0, 255).astype(np.uint8))
                        .resize((w, h)).filter(ImageFilter.BoxBlur(0)), dtype=np.float32)
    fib = np.asarray(Image.fromarray(fibres.astype(np.uint8)).resize((max(1, w // 6), h)).resize((w, h), Image.BILINEAR),
                     dtype=np.float32)
    t = 0.5 + 0.38 * bands + 0.10 * (fib - 128) / 30
    t = t.clip(0, 1)[..., None]
    base, dark = np.array(base, np.float32), np.array(dark, np.float32)
    return Image.fromarray((base * (1 - t) + dark * t).clip(0, 255).astype(np.uint8))


img = Image.new("RGB", (W, W))
# frame: walnut, grain running along each side
img.paste(wood(W, W, (92, 52, 28), (52, 26, 12), 1.6, seed=11), (0, 0))
d = ImageDraw.Draw(img)
# bevel + inlay line
d.rectangle([4, 4, W - 5, W - 5], outline=(120, 74, 42), width=3)
d.rectangle([frame - 14, frame - 14, frame + B + 13, frame + B + 13], outline=(214, 180, 128), width=3)
d.rectangle([frame - 6, frame - 6, frame + B + 5, frame + B + 5], fill=(40, 20, 9))

maple = ((226, 192, 142), (196, 154, 102))
walnut = ((128, 80, 44), (88, 50, 24))
back = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
board = {}
for f in range(8):
    board[(f, 0)] = (light_set, back[f]); board[(f, 1)] = (light_set, "pawn")
    board[(f, 7)] = (dark_set, back[f]); board[(f, 6)] = (dark_set, "pawn")
cache = {}
for f in range(8):
    for r in range(8):
        light = (f + r) % 2 == 1
        base, dk = maple if light else walnut
        sq = wood(cell, cell, base, dk, 1.0, seed=f * 8 + r + 100).convert("RGBA")
        if (f, r) in board:
            key = board[(f, r)]
            if key not in cache:
                pc = Image.open(f"{P}{key[0]}_{key[1]}.png").resize((cell, cell), Image.LANCZOS)
                # soft contact shadow under each piece
                a = np.asarray(pc)[..., 3].astype(np.float32)
                sh = Image.fromarray((a * 0.45).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4))
                shadow = Image.new("RGBA", (cell, cell), (20, 10, 4, 0))
                shadow.putalpha(sh)
                layer = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
                layer.alpha_composite(shadow, (3, 4))
                layer.alpha_composite(pc)
                cache[key] = layer
            sq.alpha_composite(cache[key])
        img.paste(sq.convert("RGB"), (frame + f * cell, frame + (7 - r) * cell))

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 30)
ink = (232, 206, 160)
for f in range(8):
    x = frame + f * cell + cell / 2
    d.text((x, frame / 2 - 8), "abcdefgh"[f], font=font, fill=ink, anchor="mm")
    d.text((x, W - frame / 2 + 8), "abcdefgh"[f], font=font, fill=ink, anchor="mm")
for r in range(8):
    y = frame + (7 - r) * cell + cell / 2
    d.text((frame / 2 - 8, y), str(r + 1), font=font, fill=ink, anchor="mm")
    d.text((W - frame / 2 + 8, y), str(r + 1), font=font, fill=ink, anchor="mm")
img.save(f"wood_board_{variant}_{light_set}_{dark_set}.png")
print("ok")
