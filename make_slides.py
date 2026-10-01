#!/usr/bin/env python3
"""Render CertTrack carousel slides from a JSON spec.

Usage: python3 make_slides.py spec.json out_dir
spec = {"slides": [{"kind": "hook"|"point"|"cta", "title": "...", "body": "...", "num": "1"}]}
Writes <out_dir>/ig_01.png ... (1080x1350, Instagram 4:5) and tt_01.png ... (1080x1920, TikTok 9:16).
"""
import json, sys, os, textwrap
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/usr/share/fonts/opentype/inter/"
def font(weight, size):
    for name in (f"InterDisplay-{weight}.otf", f"Inter-{weight}.otf"):
        p = os.path.join(FONT_DIR, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

NAVY = (31, 56, 138)  # CertTrack brand blue
HERE = os.path.dirname(os.path.abspath(__file__))
INK = (20, 24, 33)
PAPER = (247, 245, 239)
AMBER = (255, 176, 32)
GREEN = (46, 184, 114)
MUTED = (120, 128, 140)

def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_block(draw, lines, fnt, x, y, fill, gap):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += fnt.size + gap
    return y

# Optional per-spec brand: {"brand": "propertyalerts", "slides": [...]}. Default is CertTrack.
BRAND = {"name": "CertTrack", "icon": True}
BRANDS = {
    "propertyalerts": {"name": "Property Alerts USA", "icon": False,
                       "NAVY": (13, 74, 62), "AMBER": (126, 231, 176)},
}

def badge(img, draw, W, H, dark):
    if BRAND["icon"]:
        ic = Image.open(os.path.join(HERE, "icon_white.png" if dark else "icon_blue.png")).resize((48, 48), Image.LANCZOS)
        img.paste(ic, (88, H - 145), ic)
    else:
        draw.ellipse((92, H - 139, 132, H - 99), outline=AMBER, width=6)
        draw.ellipse((104, H - 127, 120, H - 111), fill=AMBER)
    draw.text((150, H - 141), BRAND["name"], font=font("Bold", 36), fill=PAPER if dark else INK)

def render(slide, idx, total, W, H):
    kind = slide.get("kind", "point")
    dark = kind in ("hook", "cta", "statement")
    img = Image.new("RGB", (W, H), NAVY if dark else PAPER)
    d = ImageDraw.Draw(img)
    pad = 90
    maxw = W - 2 * pad
    top = int(H * 0.22) if H < 1500 else int(H * 0.26)
    fb = 0 if H < 1500 else 300  # keep footer clear of TikTok caption overlay

    if kind == "hook":
        d.rectangle((pad, top - 40, pad + 120, top - 28), fill=AMBER)
        t = font("Bold", 92)
        y = draw_block(d, wrap(d, slide["title"], t, maxw), t, pad, top, PAPER, 14)
        if slide.get("body"):
            b = font("Medium", 44)
            draw_block(d, wrap(d, slide["body"], b, maxw), b, pad, y + 40, (214, 222, 240), 12)
        sw = font("SemiBold", 36)
        d.text((pad, H - 230 - fb), "swipe →", font=sw, fill=AMBER)
    elif kind == "cta":
        t = font("Bold", 80)
        y = draw_block(d, wrap(d, slide["title"], t, maxw), t, pad, top, PAPER, 14)
        if slide.get("body"):
            b = font("Medium", 44)
            y = draw_block(d, wrap(d, slide["body"], b, maxw), b, pad, y + 40, (214, 222, 240), 12)
        bt = font("Bold", 42)
        label = slide.get("button", "Link in bio")
        bw = d.textlength(label, font=bt) + 100
        d.rounded_rectangle((pad, y + 60, pad + bw, y + 160), radius=50, fill=AMBER)
        d.text((pad + 50, y + 85), label, font=bt, fill=NAVY)
    elif kind == "statement":
        # one big bold line on brand blue: hot takes, questions, "POV:" lines
        t = font("Bold", 100)
        lines = wrap(d, slide["title"], t, maxw)
        y0 = (H - fb) // 2 - len(lines) * (t.size + 16) // 2 - 60
        if slide.get("label"):
            d.text((pad, y0 - 90), slide["label"].upper(), font=font("Bold", 40), fill=AMBER)
        y = draw_block(d, lines, t, pad, y0, PAPER, 16)
        if slide.get("body"):
            b = font("Medium", 46)
            draw_block(d, wrap(d, slide["body"], b, maxw), b, pad, y + 40, (214, 222, 240), 12)
        if idx == 1 and total > 1:
            d.text((pad, H - 230 - fb), "swipe →", font=font("SemiBold", 36), fill=AMBER)
    elif kind == "myth":
        lab = font("Bold", 40)
        RED, GRN = (200, 60, 50), (30, 140, 90)
        d.rounded_rectangle((pad, top - 120, pad + 170, top - 50), radius=35, fill=RED)
        d.text((pad + 36, top - 109), "MYTH", font=lab, fill=PAPER)
        t = font("Bold", 62)
        y = draw_block(d, wrap(d, slide["myth"], t, maxw), t, pad, top, (110, 115, 125), 12)
        y += 70
        d.rounded_rectangle((pad, y, pad + 160, y + 70), radius=35, fill=GRN)
        d.text((pad + 38, y + 11), "FACT", font=lab, fill=PAPER)
        b = font("SemiBold", 52)
        draw_block(d, wrap(d, slide["fact"], b, maxw), b, pad, y + 120, INK, 14)
    elif kind == "checklist":
        t = font("Bold", 70)
        y = draw_block(d, wrap(d, slide["title"], t, maxw), t, pad, top - 60, INK, 12) + 50
        it = font("Medium", 46)
        for item in slide.get("items", []):
            d.rounded_rectangle((pad, y + 4, pad + 52, y + 56), radius=10, outline=NAVY, width=5)
            d.line((pad + 12, y + 30, pad + 24, y + 44, pad + 42, y + 16), fill=AMBER, width=7)
            ls = wrap(d, item, it, maxw - 90)
            y = draw_block(d, ls, it, pad + 90, y + 4, INK, 10) + 34
    elif kind == "compare":
        t = font("Bold", 66)
        y = draw_block(d, wrap(d, slide["title"], t, maxw), t, pad, top - 60, INK, 12) + 50
        colw = (maxw - 40) // 2
        hf, itf = font("Bold", 42), font("Medium", 36)
        for ci, (lbl, items, col) in enumerate(((slide["left_label"], slide["left"], (200, 60, 50)),
                                                (slide["right_label"], slide["right"], NAVY))):
            x = pad + ci * (colw + 40)
            d.rounded_rectangle((x, y, x + colw, y + 80), radius=16, fill=col)
            d.text((x + 28, y + 17), lbl, font=hf, fill=PAPER)
            yy = y + 120
            for item in items:
                if ci == 0:
                    d.line((x + 8, yy + 10, x + 34, yy + 36), fill=col, width=6)
                    d.line((x + 34, yy + 10, x + 8, yy + 36), fill=col, width=6)
                else:
                    d.line((x + 6, yy + 24, x + 16, yy + 36, x + 36, yy + 8), fill=col, width=6)
                yy = draw_block(d, wrap(d, item, itf, colw - 60), itf, x + 56, yy, INK, 8) + 28
    else:
        num = slide.get("num", str(idx))
        nf = font("Bold", 200)
        d.text((pad - 8, top - 200), num, font=nf, fill=NAVY)
        t = font("Bold", 70)
        y = draw_block(d, wrap(d, slide["title"], t, maxw), t, pad, top + 40, INK, 12)
        if slide.get("body"):
            b = font("Regular", 44)
            draw_block(d, wrap(d, slide["body"], b, maxw), b, pad, y + 36, (70, 78, 92), 14)

    # progress dots
    for i in range(total):
        cx = W - pad - (total - 1 - i) * 30
        d.ellipse((cx - 7, H - 127 - fb, cx + 7, H - 113 - fb),
                  fill=AMBER if i == idx - 1 else (MUTED if not dark else (110, 130, 190)))
    badge(img, d, W, H - fb, dark)
    return img

def main(spec_path, out_dir):
    spec = json.load(open(spec_path))
    b = BRANDS.get(spec.get("brand", ""))
    if b:
        global NAVY, AMBER
        BRAND.update(name=b["name"], icon=b["icon"])
        NAVY, AMBER = b["NAVY"], b["AMBER"]
    os.makedirs(out_dir, exist_ok=True)
    slides = spec["slides"]
    for i, s in enumerate(slides, 1):
        render(s, i, len(slides), 1080, 1350).save(f"{out_dir}/ig_{i:02d}.png")
        render(s, i, len(slides), 1080, 1920).save(f"{out_dir}/tt_{i:02d}.png")
    print(f"rendered {len(slides)} slides x2 formats to {out_dir}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
