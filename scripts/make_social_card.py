#!/usr/bin/env python
"""Generate the 1200x630 Open Graph social card for the biopb landing pages."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
INK = (20, 24, 31)
INK_SOFT = (75, 85, 99)
ACCENT = (37, 99, 214)
BG = (255, 255, 255)
BG_SOFT = (246, 248, 250)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
def f(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{name}", size)

bold = lambda s: f("DejaVuSans-Bold.ttf", s)
reg  = lambda s: f("DejaVuSans.ttf", s)
mono = lambda s: f("DejaVuSansMono.ttf", s)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# Accent bar down the left edge
d.rectangle([0, 0, 14, H], fill=ACCENT)

pad = 80
# Logo + wordmark, top-left
logo = Image.open("assets/logo.png").convert("RGBA")
lh = 64
logo = logo.resize((round(logo.width * lh / logo.height), lh))
img.paste(logo, (pad, 70), logo)
d.text((pad + logo.width + 18, 74), "biopb", font=bold(46), fill=INK)

# Headline
d.text((pad, 210), "Bioimage analysis,", font=bold(76), fill=INK)
d.text((pad, 300), "driven by your ", font=bold(76), fill=INK)
w = d.textlength("driven by your ", font=bold(76))
d.text((pad + w, 300), "agent.", font=bold(76), fill=ACCENT)

# Subline
d.text((pad, 430),
       "An open protocol & toolchain for AI-assisted microscopy.",
       font=reg(30), fill=INK_SOFT)

# Terminal-style footer chip (auto-sized to text)
chip_y = 500
cmd = "stream images larger than memory  ·  napari"
cmd_w = d.textlength(cmd, font=mono(24))
chip_w = 52 + cmd_w + 28
d.rounded_rectangle([pad, chip_y, pad + chip_w, chip_y + 60], radius=10, fill=(15, 23, 34))
d.text((pad + 24, chip_y + 16), "$", font=mono(26), fill=(40, 200, 64))
d.text((pad + 52, chip_y + 16), cmd, font=mono(24), fill=(231, 237, 245))

# URL bottom-right
url = "biopb.org"
uw = d.textlength(url, font=bold(30))
d.text((W - pad - uw, H - 70), url, font=bold(30), fill=ACCENT)

img.save("assets/social-card.png", optimize=True)
print("wrote assets/social-card.png", img.size)
