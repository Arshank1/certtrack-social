#!/usr/bin/env python3
"""Render a vertical (1080x1920) TikTok/Reels/Shorts video with mood-matched music.

Usage: python3 make_video.py spec.json out_dir
Writes out_dir/video.mp4 and out_dir/cover.png (first frame, used for checking and as a thumbnail).

Spec (common keys):
  {"format": "kinetic"|"texts"|"countdown"|"notes"|"quiz"|"alerts",
   "mood": "chill"|"upbeat"|"tense"|"dramatic"|"playful"|"confident",
   "theme": "navy"|"paper"|"dark"|"amber",          (optional colour scheme)
   "seed": 0..999,                                  (optional, varies the music)
   "music": "library"|"synth",                      library (default) = sound effects only, a TikTok
                                                    commercial-library track is attached when posting;
                                                    synth = bake in our own generated track for that mood
   "brand": "propertyalerts",                       (optional; default CertTrack)
   "cta": {"title": "...", "body": "...", "button": "Link in bio"},
   ... format-specific keys, see each builder below ...}

Formats:
  kinetic   "lines": ["POV: the client wants your COI by *Monday*", ...]   big words pop in on the beat; *word* = highlight
  texts     "contact": "Client - Riverside Build", "messages": [{"from":"them"|"me","text":"..."}], "punchline": "..."
  countdown "title": "...", "items": [{"title":"...","body":"..."}]          shown N..1
  notes     "title": "...", "items": ["...", ...], "footer": "save this"      notes-app typing + checkmarks
  quiz      "title": "...", "questions": [{"q":"...","options":["..",".."],"answer":0,"why":"..."}]
  alerts    "setup": "...", "alerts": [{"title":"...","body":"...","when":"30 days before"}], "payoff": "..."
"""
import json, os, sys, math, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import music

W, H, FPS = 1080, 1920, 30
# TikTok safe area: keep text away from the top bar, right-hand buttons and bottom caption
SL, SR_, ST, SB = 90, W - 160, 250, H - 470
FONT_DIR = "/usr/share/fonts/opentype/inter/"

_fc = {}
def font(weight, size):
    k = (weight, size)
    if k not in _fc:
        f = None
        for name in (f"InterDisplay-{weight}.otf", f"Inter-{weight}.otf"):
            p = os.path.join(FONT_DIR, name)
            if os.path.exists(p):
                f = ImageFont.truetype(p, size); break
        _fc[k] = f or ImageFont.load_default()
    return _fc[k]

NAVY = (31, 56, 138); AMBER = (255, 176, 32); PAPER = (247, 245, 239); INK = (20, 24, 33)
RED = (214, 64, 52); GREEN = (34, 160, 100); MUTED = (120, 128, 140); DARK = (14, 17, 26)
BRAND = {"name": "CertTrack", "icon": True, "site": "certtracksecure.com"}
BRANDS = {"propertyalerts": {"name": "Property Alerts USA", "icon": False, "site": "propertyalertsusa.com",
                             "NAVY": (13, 74, 62), "AMBER": (126, 231, 176)}}
THEMES = {}
def set_themes():
    THEMES.update({
        "navy":  dict(bg=NAVY, fg=PAPER, accent=AMBER, sub=(214, 222, 240), card=(255, 255, 255)),
        "paper": dict(bg=PAPER, fg=INK, accent=NAVY, sub=(70, 78, 92), card=(255, 255, 255)),
        "dark":  dict(bg=DARK, fg=PAPER, accent=AMBER, sub=(170, 178, 195), card=(30, 35, 48)),
        "amber": dict(bg=AMBER, fg=INK, accent=NAVY, sub=(60, 50, 30), card=(255, 255, 255)),
    })
set_themes()

# ----------------------------------------------------------------- easing / text helpers
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, x): return a + (b - a) * x
def mix(c1, c2, x): return tuple(int(lerp(a, b, clamp(x))) for a, b in zip(c1, c2))

_measure = ImageDraw.Draw(Image.new("RGB", (10, 10)))
def wrap(text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if _measure.textlength(t.replace("*", ""), font=fnt) <= max_w: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def fit(text, weight, max_w, max_lines, start=120, min_size=44):
    size = start
    while size > min_size:
        f = font(weight, size)
        ls = wrap(text, f, max_w)
        if len(ls) <= max_lines and all(_measure.textlength(l.replace("*", ""), font=f) <= max_w for l in ls):
            return f, ls
        size -= 4
    f = font(weight, min_size)
    return f, wrap(text, f, max_w)

def text_block(d, lines, fnt, x, y, fill, gap=12, hl=None, alpha=1.0, bg=None):
    """Draw lines; *word* segments use the highlight colour. Returns bottom y."""
    for ln in lines:
        cx = x
        for i, w in enumerate(ln.split(" ")):
            col = fill
            if w.startswith("*") or w.endswith("*"):
                col = hl or fill
            w2 = w.replace("*", "")
            c = mix(bg, col, alpha) if bg is not None and alpha < 1 else col
            d.text((cx, y), w2, font=fnt, fill=c)
            cx += _measure.textlength(w2 + " ", font=fnt)
        y += fnt.size + gap
    return y

def brand_badge(img, d, dark=True, y=None):
    y = SB + 20 if y is None else y
    if BRAND["icon"]:
        ic = Image.open(os.path.join(HERE, "icon_white.png" if dark else "icon_blue.png")).convert("RGBA").resize((46, 46), Image.LANCZOS)
        img.paste(ic, (SL, y), ic)
    else:
        d.ellipse((SL + 3, y + 3, SL + 43, y + 43), outline=AMBER, width=6)
        d.ellipse((SL + 15, y + 15, SL + 31, y + 31), fill=AMBER)
    d.text((SL + 60, y + 3), BRAND["name"], font=font("Bold", 34), fill=PAPER if dark else INK)

def background(theme, t, seed=0):
    """Solid theme colour with two slow drifting soft circles for motion."""
    th = THEMES[theme]
    img = Image.new("RGB", (W, H), th["bg"])
    d = ImageDraw.Draw(img)
    base = th["bg"]
    tint = mix(base, th["accent"], 0.10)
    tint2 = mix(base, th["fg"], 0.05)
    r1 = 420
    x1 = 760 + 120 * math.sin(t * 0.35 + seed); y1 = 520 + 140 * math.cos(t * 0.3 + seed)
    d.ellipse((x1 - r1, y1 - r1, x1 + r1, y1 + r1), fill=tint)
    r2 = 300
    x2 = 200 + 100 * math.cos(t * 0.4 + seed * 2); y2 = 1500 + 90 * math.sin(t * 0.33 + seed)
    d.ellipse((x2 - r2, y2 - r2, x2 + r2, y2 + r2), fill=tint2)
    return img

# ----------------------------------------------------------------- scene model
class Scene:
    def __init__(self, dur, draw, sfx=None):
        self.dur, self.draw, self.sfx = dur, draw, sfx or []  # sfx: [(t_local, name)]

def beats(n, bpm): return n * 60.0 / bpm

# ----------------------------------------------------------------- CTA (shared)
def cta_scene(spec, bpm, theme):
    c = spec.get("cta", {})
    title = c.get("title", "Never miss a renewal again")
    body = c.get("body", f"{BRAND['name']} tracks your licenses, permits and policies and alerts you before they expire.")
    button = c.get("button", "Link in bio")
    th = "navy" if theme != "navy" else "dark"
    dur = max(3.6, beats(8, bpm))
    def draw(t, img, d):
        img.paste(background(th, t + 9))
        p = ease_back(t / 0.45)
        tf, tl = fit(title, "Bold", SR_ - SL, 3, 96)
        y = int(lerp(ST + 260, ST + 200, ease_out(t / 0.5)))
        y = text_block(d, tl, tf, SL, y, PAPER, 14, alpha=clamp(t / 0.3), bg=THEMES[th]["bg"])
        bf = font("Medium", 44)
        if t > 0.35:
            a = clamp((t - 0.35) / 0.4)
            y = text_block(d, wrap(body, bf, SR_ - SL), bf, SL, y + 40, THEMES[th]["sub"], 12, alpha=a, bg=THEMES[th]["bg"])
        if t > 0.8:
            s = ease_back((t - 0.8) / 0.4)
            btf = font("Bold", 46)
            bw = _measure.textlength(button, font=btf) + 110
            cx, cy = SL + bw / 2, y + 140
            ww, hh = bw * s, 110 * s
            d.rounded_rectangle((cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2), radius=int(55 * s) + 1, fill=AMBER)
            if s > 0.8:
                d.text((cx - (bw - 110) / 2, cy - 28), button, font=btf, fill=NAVY)
            # gentle pulse arrow
            if t > 1.3:
                ax = cx + bw / 2 + 30 + 12 * math.sin(t * 6)
                d.text((ax, cy - 34), "←", font=font("Bold", 60), fill=AMBER)
        d.text((SL, SB - 60), BRAND["site"], font=font("SemiBold", 38), fill=THEMES[th]["sub"])
        brand_badge(img, d, True)
    return Scene(dur, draw, [(0.0, "whoosh"), (0.8, "pop")])

# ----------------------------------------------------------------- KINETIC
def build_kinetic(spec, bpm):
    scenes = []
    themes = [spec.get("theme", "navy")]
    cycle = ["navy", "paper", "dark", "amber"]
    for i in range(1, len(spec["lines"])):
        nxt = cycle[(cycle.index(themes[-1]) + 1) % len(cycle)]
        themes.append(nxt)
    beat = 60.0 / bpm
    for li, line in enumerate(spec["lines"]):
        th = themes[li]
        label = None
        if isinstance(line, dict):
            label, line = line.get("label"), line["text"]
        words = line.split()
        step = beat / 2
        n_beats = max(4, math.ceil((len(words) * 0.5 + 3) / 2) * 2)
        dur = beats(n_beats, bpm)
        fnt, lines = fit(line, "Black", SR_ - SL, 6, 132, 64)
        # layout positions at full scale
        lh = fnt.size + 18
        total_h = len(lines) * lh
        y0 = (ST + SB) // 2 - total_h // 2
        layout, k = [], 0
        for r, ln in enumerate(lines):
            x = SL
            for w in ln.split(" "):
                hl = w.startswith("*") or w.endswith("*")
                w2 = w.replace("*", "")
                wd = _measure.textlength(w2, font=fnt)
                layout.append((k, w2, x, y0 + r * lh, hl, wd))
                x += wd + _measure.textlength(" ", font=fnt)
                k += 1
        first = li == 0
        def draw(t, img, d, layout=layout, th=th, fnt=fnt, step=step, first=first, label=label, y0=y0, li=li):
            img.paste(background(th, t + li * 3, li))
            T = THEMES[th]
            if label:
                d.text((SL, y0 - 100), label.upper(), font=font("Bold", 44), fill=T["accent"])
            for (k, w, x, y, hl, wd) in layout:
                ti = k * step - (step * 1.5 if first else 0)  # first frame of video already shows text
                if t < ti: continue
                p = clamp((t - ti) / 0.16)
                s = 0.6 + 0.4 * ease_back(p)
                col = T["accent"] if hl else T["fg"]
                if hl:  # highlighter bar behind emphasised words
                    bw = wd * ease_out(p)
                    d.rectangle((x - 8, y + fnt.size * 0.18, x - 8 + bw + 16, y + fnt.size * 1.08), fill=mix(T["bg"], T["accent"], 0.22))
                if s > 0.98:
                    d.text((x, y), w, font=fnt, fill=col)
                else:
                    fs = max(10, int(fnt.size * s))
                    f2 = font("Black", fs)
                    d.text((x + wd * (1 - s) / 2, y + fnt.size * (1 - s) / 2), w, font=f2, fill=col)
            brand_badge(img, d, th in ("navy", "dark"))
        sfx = [(max(0, i * step - (step * 1.5 if first else 0)), "pop") for i in range(0, k, 3)]
        scenes.append(Scene(dur, draw, ([(0, "whoosh")] if li else []) + sfx[: 4]))
    return scenes

# ----------------------------------------------------------------- TEXTS (chat)
def build_texts(spec, bpm):
    theme = spec.get("theme", "paper")
    msgs = spec["messages"]
    contact = spec.get("contact", "Client")
    bf = font("Medium", 50)
    maxbw = 700
    # pre-layout bubbles
    bubbles = []
    for m in msgs:
        ls = wrap(m["text"], bf, maxbw - 60)
        w = max(_measure.textlength(l, font=bf) for l in ls) + 60
        h = len(ls) * (bf.size + 10) + 44
        bubbles.append(dict(me=m.get("from") == "me", lines=ls, w=w, h=h))
    # timeline: typing indicator before "them" messages
    times, t, sfx = [], 0.3, []
    for b in bubbles:
        typing = 0 if b["me"] else 0.75
        times.append((t, t + typing))
        t += typing
        sfx.append((t, "send" if b["me"] else "receive"))
        t += 0.6 + sum(len(l) for l in b["lines"]) / 30
    times_end = t + 0.4
    head_h = 150
    dark_ui = theme in ("dark", "navy")
    bgc = (12, 12, 16) if dark_ui else (255, 255, 255)
    them_c = (44, 44, 52) if dark_ui else (233, 233, 238)
    them_t = PAPER if dark_ui else INK
    me_c = (10, 132, 255)

    def draw(tt, img, d):
        img.paste(Image.new("RGB", (W, H), bgc))
        # header
        d.rectangle((0, ST - 40, W, ST - 40 + head_h), fill=(28, 28, 34) if dark_ui else (247, 247, 249))
        d.ellipse((W // 2 - 42, ST - 30, W // 2 + 42, ST + 54), fill=(150, 156, 170))
        ini = "".join(w[0] for w in contact.split() if w[0].isalnum())[:2].upper()
        f = font("Bold", 36)
        d.text((W // 2 - _measure.textlength(ini, font=f) / 2, ST - 9), ini, font=f, fill=(255, 255, 255))
        cf = font("SemiBold", 30)
        d.text((W // 2 - _measure.textlength(contact, font=cf) / 2, ST + 62), contact, font=cf, fill=them_t)
        # visible bubbles, bottom-anchored scroll
        vis = [i for i, (ts, te) in enumerate(times) if tt >= ts]
        items = []
        for i in vis:
            ts, te = times[i]
            b = bubbles[i]
            if tt < te:  # typing dots
                items.append(("typing", i, 110))
            else:
                items.append(("msg", i, b["h"]))
        total = sum(h + 22 for _, _, h in items)
        area_top, area_bot = ST + head_h, SB - 20
        y = max(area_top, area_bot - total) if total > area_bot - area_top else area_top
        if total > area_bot - area_top:
            y = area_bot - total
        for kind, i, h in items:
            b = bubbles[i]
            ts, te = times[i]
            if kind == "typing":
                x0 = SL
                d.rounded_rectangle((x0, y, x0 + 160, y + 90), radius=45, fill=them_c)
                for k in range(3):
                    a = 0.5 + 0.5 * math.sin(tt * 9 - k * 0.9)
                    c = mix(them_c, (140, 140, 150), a)
                    d.ellipse((x0 + 34 + k * 36, y + 33, x0 + 58 + k * 36, y + 57), fill=c)
            else:
                p = ease_back((tt - te) / 0.25)
                x0 = (SR_ - b["w"]) if b["me"] else SL
                off = int((1 - p) * 40)
                col = me_c if b["me"] else them_c
                d.rounded_rectangle((x0, y + off, x0 + b["w"], y + off + b["h"]), radius=40, fill=col)
                text_block(d, b["lines"], bf, x0 + 30, y + off + 20, (255, 255, 255) if b["me"] else them_t, 10)
            y += h + 22
    scenes = [Scene(times_end, draw, sfx)]
    if spec.get("punchline"):
        scenes += build_kinetic({"lines": [spec["punchline"]], "theme": "navy"}, bpm)
        scenes[-1].sfx = [(0, "boom")]
    return scenes

# ----------------------------------------------------------------- COUNTDOWN
def build_countdown(spec, bpm):
    theme = spec.get("theme", "dark")
    T = THEMES[theme]
    items = spec["items"]
    n = len(items)
    scenes = []
    # title card
    tf, tl = fit(spec["title"], "Black", SR_ - SL, 5, 124, 64)
    def title_draw(t, img, d):
        img.paste(background(theme, t))
        y = (ST + SB) // 2 - len(tl) * (tf.size + 16) // 2
        d.rectangle((SL, y - 60, SL + 140 * ease_out(t / 0.4 + 0.5), y - 44), fill=T["accent"])
        text_block(d, tl, tf, SL, y, T["fg"], 16, hl=T["accent"])
        if t > 0.6:
            d.text((SL, SB - 90), "wait for #1", font=font("SemiBold", 40), fill=T["accent"])
        brand_badge(img, d, theme in ("navy", "dark"))
    scenes.append(Scene(max(2.4, beats(4, bpm)), title_draw, []))
    for pos, it in enumerate(reversed(items)):
        num = n - pos
        title, body = it["title"], it.get("body", "")
        tf2, tl2 = fit(title, "Bold", SR_ - SL, 3, 92, 56)
        bf = font("Medium", 46)
        bl = wrap(body, bf, SR_ - SL) if body else []
        nb = 6 if len(body) < 70 else 8
        def draw(t, img, d, num=num, tl2=tl2, tf2=tf2, bl=bl, pos=pos):
            img.paste(background(theme, t + pos * 2, pos))
            # progress bar
            for k in range(n):
                x = SL + k * ((SR_ - SL) // n)
                c = T["accent"] if k <= pos else mix(T["bg"], T["fg"], 0.2)
                d.rounded_rectangle((x, ST - 60, x + (SR_ - SL) // n - 14, ST - 48), radius=6, fill=c)
            s = ease_back(t / 0.3)
            nf = font("Black", max(20, int(330 * s)))
            d.text((SL - 10, ST + 200 + (1 - s) * 120), f"#{num}" if s > 0.5 else str(num), font=nf, fill=T["accent"])
            y = ST + 640
            xo = int((1 - ease_out((t - 0.2) / 0.35)) * -700)
            if t > 0.2:
                y = text_block(d, tl2, tf2, SL + xo, y, T["fg"], 12)
            if t > 0.6 and bl:
                text_block(d, bl, bf, SL, y + 30, T["sub"], 12, alpha=clamp((t - 0.6) / 0.4), bg=T["bg"])
            brand_badge(img, d, theme in ("navy", "dark"))
        scenes.append(Scene(beats(nb, bpm), draw, [(0.0, "whoosh" if num > 1 else "boom")]))
    return scenes

# ----------------------------------------------------------------- NOTES
def build_notes(spec, bpm):
    title, items = spec["title"], spec["items"]
    footer = spec.get("footer", "save this for later")
    paper = (255, 252, 240)
    line_c = (232, 226, 205)
    tf = font("Bold", 80)
    tl = wrap(title, tf, SR_ - SL)
    itf = font("Medium", 54)
    wrapped = [wrap(s, itf, SR_ - SL - 90) for s in items]
    cps = 26.0  # typing speed (chars/s)
    starts, t = [], 0.9
    for s in items:
        starts.append(t)
        t += len(s) / cps + 0.55
    dur = t + 1.6
    sfx = [(s + len(it) / cps + 0.1, "tick") for s, it in zip(starts, items)]
    def draw(tt, img, d):
        img.paste(Image.new("RGB", (W, H), paper))
        d.text((SL - 10, ST - 90), "‹ Notes", font=font("SemiBold", 38), fill=(214, 160, 0))
        y = text_block(d, tl, tf, SL, ST, INK, 10)
        d.text((SL, y + 4), "Today", font=font("Regular", 32), fill=MUTED)
        y += 80
        cur = None
        for i, (s, ls) in enumerate(zip(starts, wrapped)):
            if tt < s: break
            n = int((tt - s) * cps)
            full = items[i]
            shown = full[:n]
            done = n >= len(full)
            # checkbox
            d.rounded_rectangle((SL, y + 8, SL + 54, y + 62), radius=25, outline=(200, 170, 60), width=4,
                                fill=(255, 196, 30) if done and tt > s + len(full) / cps + 0.1 else None)
            if done and tt > s + len(full) / cps + 0.1:
                d.line((SL + 14, y + 35, SL + 24, y + 46, SL + 41, y + 22), fill=(255, 255, 255), width=6)
            sl = wrap(shown, itf, SR_ - SL - 90) if shown else [""]
            yy = text_block(d, sl, itf, SL + 80, y + 4, INK, 10)
            if not done:
                cur = (SL + 80 + _measure.textlength(sl[-1], font=itf) + 4, yy - itf.size - 10)
            y = y + max(len(ls), len(sl)) * (itf.size + 10) + 40
        if cur and int(tt * 2.5) % 2 == 0:
            d.rectangle((cur[0], cur[1] + 4, cur[0] + 5, cur[1] + itf.size + 6), fill=(214, 160, 0))
        if tt > starts[-1] + len(items[-1]) / cps + 0.4:
            a = clamp((tt - starts[-1] - len(items[-1]) / cps - 0.4) / 0.4)
            ff = font("Bold", 48)
            d.text((SL, SB - 70), footer, font=ff, fill=mix(paper, (214, 120, 0), a))
        brand_badge(img, d, False)
    return [Scene(dur, draw, sfx)]

# ----------------------------------------------------------------- QUIZ
def build_quiz(spec, bpm):
    theme = spec.get("theme", "navy")
    T = THEMES[theme]
    scenes = []
    tf, tl = fit(spec.get("title", "Quick quiz"), "Black", SR_ - SL, 4, 118, 64)
    def tdraw(t, img, d):
        img.paste(background(theme, t))
        y = (ST + SB) // 2 - 200
        d.text((SL, y - 90), "QUIZ TIME", font=font("Bold", 44), fill=T["accent"])
        text_block(d, tl, tf, SL, y, T["fg"], 16, hl=T["accent"])
        d.text((SL, SB - 90), "comment your score", font=font("SemiBold", 40), fill=T["sub"])
        brand_badge(img, d, theme in ("navy", "dark"))
    scenes.append(Scene(beats(4, bpm) if bpm < 100 else beats(6, bpm), tdraw, [(0, "pop")]))
    for qi, q in enumerate(spec["questions"]):
        qf, ql = fit(q["q"], "Bold", SR_ - SL, 4, 72, 48)
        of = font("SemiBold", 44)
        think = 3.0
        reveal_at = 0.9 + think
        why = q.get("why", "")
        wf = font("Medium", 40)
        wl = wrap(why, wf, SR_ - SL)
        dur = reveal_at + 1.4 + len(why) / 28
        def draw(t, img, d, ql=ql, qf=qf, q=q, qi=qi, wl=wl, think=think, reveal_at=reveal_at):
            img.paste(background(theme, t + qi, qi))
            d.text((SL, ST - 70), f"Q{qi + 1}/{len(spec['questions'])}", font=font("Bold", 40), fill=T["accent"])
            y = text_block(d, ql, qf, SL, ST, T["fg"], 12) + 40
            for oi, opt in enumerate(q["options"]):
                ts = 0.3 + oi * 0.15
                if t < ts: continue
                p = ease_back((t - ts) / 0.25)
                ol = wrap(opt, of, SR_ - SL - 140)
                h = len(ol) * (of.size + 8) + 50
                fill, txt = T["card"], INK
                if t >= reveal_at:
                    if oi == q["answer"]: fill, txt = GREEN, (255, 255, 255)
                    else: fill = mix(T["card"], T["bg"], 0.55)
                x0 = SL + (1 - p) * 300
                d.rounded_rectangle((x0, y, SR_, y + h), radius=26, fill=fill)
                d.text((x0 + 30, y + 22), "ABCD"[oi], font=font("Black", 46), fill=T["accent"] if t < reveal_at or oi != q["answer"] else (255, 255, 255))
                text_block(d, ol, of, x0 + 100, y + 24, txt, 8)
                y += h + 22
            if 0.9 <= t < reveal_at:  # timer bar
                frac = 1 - (t - 0.9) / think
                d.rounded_rectangle((SL, y + 20, SL + (SR_ - SL) * frac, y + 44), radius=12, fill=T["accent"])
                d.text((SR_ - 60, y + 60), str(int(math.ceil(frac * 3))), font=font("Black", 70), fill=T["fg"])
            if t >= reveal_at + 0.3 and wl:
                text_block(d, wl, wf, SL, y + 30, T["sub"], 10, alpha=clamp((t - reveal_at - 0.3) / 0.4), bg=T["bg"])
            brand_badge(img, d, theme in ("navy", "dark"))
        sfx = [(0.9 + k, "tick") for k in range(3)] + [(reveal_at, "correct")]
        scenes.append(Scene(dur, draw, sfx))
    return scenes

# ----------------------------------------------------------------- ALERTS (lock-screen notifications)
def build_alerts(spec, bpm):
    setup = spec["setup"]
    alerts = spec["alerts"]
    payoff = spec.get("payoff")
    sf, sl = fit(setup, "Bold", SR_ - SL, 4, 70, 46)
    gap = 1.5
    dur = 1.6 + len(alerts) * gap + 1.4
    nt, nb = font("Bold", 38), font("Regular", 36)
    def draw(t, img, d):
        img.paste(Image.new("RGB", (W, H), (0, 0, 0)))
        bg = background("dark", t * 0.5, 4).filter(ImageFilter.GaussianBlur(30))
        img.paste(bg)
        d = ImageDraw.Draw(img)
        clock = spec.get("clock", "9:41")
        cf = font("Light", 200)
        d.text((W / 2 - _measure.textlength(clock, font=cf) / 2, ST - 30), clock, font=cf, fill=(240, 242, 248))
        dl = spec.get("date", "Monday")
        df = font("Medium", 44)
        d.text((W / 2 - _measure.textlength(dl, font=df) / 2, ST - 80), dl, font=df, fill=(200, 205, 220))
        y = ST + 260
        y = text_block(d, sl, sf, SL, y, PAPER, 10, hl=AMBER, alpha=clamp(t / 0.4), bg=DARK) + 40
        for i, a in enumerate(alerts):
            ts = 1.6 + i * gap
            if t < ts: continue
            p = ease_back((t - ts) / 0.35)
            bl = wrap(a["body"], nb, SR_ - SL - 70)
            h = 150 + len(bl) * (nb.size + 8)
            yy = y - (1 - p) * 220
            card = Image.new("RGBA", (SR_ - SL, int(h)), (0, 0, 0, 0))
            cd = ImageDraw.Draw(card)
            cd.rounded_rectangle((0, 0, SR_ - SL - 1, h - 1), radius=34, fill=(245, 246, 250, int(235 * clamp(p))))
            img.paste(card, (SL, int(yy)), card)
            if BRAND["icon"]:
                ic = Image.open(os.path.join(HERE, "icon_blue.png")).convert("RGBA").resize((44, 44), Image.LANCZOS)
                img.paste(ic, (SL + 26, int(yy) + 24), ic)
            d.text((SL + 84, yy + 28), BRAND["name"].upper(), font=font("SemiBold", 28), fill=MUTED)
            w_ = a.get("when", "now")
            d.text((SR_ - 30 - _measure.textlength(w_, font=font("Regular", 28)), yy + 28), w_, font=font("Regular", 28), fill=MUTED)
            d.text((SL + 30, yy + 76), a["title"], font=nt, fill=INK)
            text_block(d, bl, nb, SL + 30, yy + 128, (60, 64, 76), 8)
            y += h + 20
        if t > 1.6 + len(alerts) * gap + 0.2:
            d.text((SL, SB - 60), "this is the whole point", font=font("SemiBold", 38), fill=AMBER)
        brand_badge(img, d, True)
    sfx = [(1.6 + i * gap, "ding") for i in range(len(alerts))]
    scenes = [Scene(dur, draw, sfx)]
    if payoff:
        k = build_kinetic({"lines": [payoff], "theme": "navy"}, bpm)
        k[0].sfx = [(0, "whoosh")]
        scenes += k
    return scenes

BUILDERS = {"kinetic": build_kinetic, "texts": build_texts, "countdown": build_countdown,
            "notes": build_notes, "quiz": build_quiz, "alerts": build_alerts}
DEFAULT_MOOD = {"kinetic": "confident", "texts": "tense", "countdown": "upbeat",
                "notes": "chill", "quiz": "playful", "alerts": "dramatic"}

def hook_overlay(img, hook, t, hold=2.4):
    """TikTok-style caption box shown over the first seconds, so the first frame always has a hook."""
    if not hook or t > hold + 0.4:
        return
    a = 1.0 if t < hold else 1 - (t - hold) / 0.4
    f, ls = fit(hook, "Bold", W - 2 * SL - 120, 3, 64, 44)
    lh = f.size + 10
    bh = len(ls) * lh + 50
    bw = max(_measure.textlength(l.replace("*", ""), font=f) for l in ls) + 70
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    x0, y0 = (W - bw) / 2, H * 0.42 - bh / 2
    ld.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=22, fill=(15, 17, 24, int(235 * a)))
    y = y0 + 22
    for l in ls:
        lw = _measure.textlength(l.replace("*", ""), font=f)
        ld.text(((W - lw) / 2, y), l.replace("*", ""), font=f, fill=(255, 255, 255, int(255 * a)))
        y += lh
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"))

def main(spec_path, out_dir):
    spec = json.load(open(spec_path))
    b = BRANDS.get(spec.get("brand", ""))
    global NAVY, AMBER
    if b:
        BRAND.update(name=b["name"], icon=b["icon"], site=b["site"])
        NAVY, AMBER = b["NAVY"], b["AMBER"]
        set_themes()
    fmt = spec["format"]
    mood = spec.get("mood") or DEFAULT_MOOD[fmt]
    seed = int(spec.get("seed", random.randint(0, 999)))
    bpm = music.mood_bpm(mood, seed)
    scenes = BUILDERS[fmt](spec, bpm) + [cta_scene(spec, bpm, spec.get("theme", "navy"))]
    total = sum(s.dur for s in scenes)
    if total > 58:
        print(f"WARNING: video is {total:.1f}s; aim for 12-35s")
    os.makedirs(out_dir, exist_ok=True)
    # audio
    events, t0 = [], 0.0
    for s in scenes:
        events += [(t0 + a, n) for a, n in s.sfx]
        t0 += s.dur
    wav = os.path.join(out_dir, "_audio.wav")
    music_on = spec.get("music", "library") == "synth"
    music.write_wav(wav, music.render(mood, total, seed, events, music_on))
    # video frames piped to ffmpeg
    out = os.path.join(out_dir, "video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    frame_i, cover_saved = 0, False
    snaps = []
    t_glob = 0.0
    for si, s in enumerate(scenes):
        nf = int(round(s.dur * FPS))
        for k in range(nf):
            img = Image.new("RGB", (W, H))
            d = ImageDraw.Draw(img)
            t = k / FPS
            s.draw(t, img, ImageDraw.Draw(img))
            if si == 0 and fmt in ("texts", "notes", "alerts"):
                hook_overlay(img, spec.get("hook"), t)
            if not cover_saved:
                img.save(os.path.join(out_dir, "cover.png")); cover_saved = True
            if k == int(nf * 0.85):
                snaps.append(img.resize((W // 3, H // 3)))
            ff.stdin.write(img.tobytes())
            frame_i += 1
    ff.stdin.close(); ff.wait()
    os.remove(wav)
    # contact sheet of each scene (for visual QA)
    if snaps:
        cols = min(4, len(snaps)); rows = math.ceil(len(snaps) / cols)
        sheet = Image.new("RGB", (cols * (W // 3), rows * (H // 3)), (0, 0, 0))
        for i, sn in enumerate(snaps):
            sheet.paste(sn, ((i % cols) * (W // 3), (i // cols) * (H // 3)))
        sheet.save(os.path.join(out_dir, "_sheet.png"))
    meta = {"format": fmt, "mood": mood, "music": "synth" if music_on else "library", "seed": seed, "bpm": bpm, "seconds": round(total, 1), "scenes": len(scenes)}
    json.dump(meta, open(os.path.join(out_dir, "meta.json"), "w"))
    print(json.dumps(meta))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
