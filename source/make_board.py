"""Render the full set in the starting position on a broadcast-style board."""
import sys
from PIL import Image, ImageDraw, ImageFont

variant = sys.argv[1] if len(sys.argv) > 1 else "crt"
dark_set = sys.argv[2] if len(sys.argv) > 2 else "black"
P = f"retro-chess-pieces/{variant}/"
cell, margin = 120, 70
W = cell * 8 + margin * 2
img = Image.new("RGBA", (W, W + 20), (6, 6, 8, 255))
d = ImageDraw.Draw(img)
green, dark = (34, 112, 82, 255), (50, 52, 56, 255)
back = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
board = {}
for f in range(8):
    board[(f, 0)] = ("white", back[f]); board[(f, 1)] = ("white", "pawn")
    board[(f, 7)] = (dark_set, back[f]); board[(f, 6)] = (dark_set, "pawn")
cache = {}
d.rectangle([margin - 10, margin - 10, margin + cell * 8 + 9, margin + cell * 8 + 9],
            outline=(235, 235, 245), width=6)
for f in range(8):
    for r in range(8):
        x, y = margin + f * cell, margin + (7 - r) * cell
        sq = Image.new("RGBA", (cell, cell), dark if (f + r) % 2 == 0 else green)
        if (f, r) in board:
            key = board[(f, r)]
            if key not in cache:
                cache[key] = Image.open(f"{P}{key[0]}_{key[1]}.png").resize((cell, cell), Image.LANCZOS)
            sq.alpha_composite(cache[key])
        img.paste(sq, (x, y))
        d.line([x, y, x + cell, y], fill=(150, 175, 170), width=2)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
for f in range(8):
    d.text((margin + f * cell + cell / 2, margin / 2 - 6), "abcdefgh"[f], font=font, fill=(235, 235, 245), anchor="mm")
for r in range(8):
    d.text((margin / 2 - 8, margin + (7 - r) * cell + cell / 2), str(r + 1), font=font, fill=(235, 235, 245), anchor="mm")
img.convert("RGB").save(f"sample_board_{variant}_{dark_set}.png")
