#!/usr/bin/env python3
"""Performance log + format picker for the TikTok agent. Lets each run learn from earlier posts.

Data lives in perf/log.json (one entry per post) and perf/insights.md (running notes).

  python3 perf.py report                       # stats by format / mood / topic type + NEXT FORMAT suggestion
  python3 perf.py add '<json entry>'           # log a new post (see FIELDS)
  python3 perf.py stats <postiz_id> views=1200 likes=40 comments=3 shares=2 saves=9 [followers=1]
                                               # record TikTok numbers for a post (repeatable; latest wins)

FIELDS for add: date (Pacific YYYY-MM-DD-HHMM), postiz_id, brand, format, mood, theme, topic,
  angle (pov|listicle|myth|checklist|hot_take|tip|quiz|industry|story|comparison|product),
  industry, hook, caption, hashtags (list), seconds, track (TikTok music id or "synth"/"auto")
"""
import json, os, sys, random, datetime
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "perf", "log.json")
FORMATS = ["kinetic", "texts", "countdown", "notes", "quiz", "alerts", "slideshow"]
# Owner preference (2026-10-01): likes the text-message story format most, quiz too. >1 = shown more often.
OWNER_BOOST = {"texts": 1.6, "quiz": 1.1}

MOOD_FOR = {  # default + allowed alternatives, so music always fits the vibe
    "kinetic":   ["confident", "dramatic", "tense"],
    "texts":     ["tense", "playful"],
    "countdown": ["upbeat", "confident"],
    "notes":     ["chill"],
    "quiz":      ["playful", "upbeat"],
    "alerts":    ["dramatic", "tense", "chill"],
    "slideshow": ["(TikTok auto music)"],
}

def load():
    if not os.path.exists(LOG):
        return []
    return json.load(open(LOG))

def save(rows):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    json.dump(rows, open(LOG, "w"), indent=1)

def score(st):
    """Engagement score: views matter most; interactions weighted by how strongly TikTok rewards them."""
    v = st.get("views", 0)
    inter = st.get("likes", 0) + 2 * st.get("comments", 0) + 3 * st.get("shares", 0) + 3 * st.get("saves", 0) + 5 * st.get("followers", 0)
    rate = inter / v if v else 0
    return v * (1 + 5 * rate), rate

def group(rows, key):
    g = defaultdict(list)
    for r in rows:
        if r.get("stats"):
            g[r.get(key, "?")].append(r)
    out = []
    for k, rs in g.items():
        vs = [r["stats"].get("views", 0) for r in rs]
        sc = [score(r["stats"])[0] for r in rs]
        er = [score(r["stats"])[1] for r in rs]
        out.append((k, len(rs), sum(vs) / len(vs), sum(er) / len(er), sum(sc) / len(sc)))
    return sorted(out, key=lambda x: -x[4])

def pick_next(rows, brand="certtrack"):
    rows = [r for r in rows if r.get("brand", "certtrack") == brand]
    recent = [r["format"] for r in rows[-5:]]
    last = recent[-1] if recent else None
    cands = [f for f in FORMATS if f != last and recent.count(f) < 2]
    if "slideshow" in cands and "slideshow" in recent[-4:]:
        cands.remove("slideshow")  # slideshows at most 1 in 5
    stats = {k: (n, sc) for k, n, _, _, sc in group(rows, "format")}
    unexplored = [f for f in cands if stats.get(f, (0, 0))[0] < 3]
    rnd = random.Random(datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H"))
    # owner's favourite: bring texts back roughly every 3rd post (never twice in a row)
    if "texts" in cands and "texts" not in recent[-2:] and rnd.random() < 0.6:
        return "texts", "owner's favourite format"
    if unexplored and (len(unexplored) == len(cands) or rnd.random() < 0.4):
        use = defaultdict(int)
        for r in rows:
            use[r["format"]] += 1
        unexplored.sort(key=lambda f: (use[f], rnd.random()))
        return unexplored[0], "exploring (not enough data on this format yet)"
    scored = [(f, stats[f][1] * OWNER_BOOST.get(f, 1.0)) for f in cands if f in stats and stats[f][0] >= 3]
    if not scored:
        return rnd.choice(cands), "random among allowed"
    tot = sum(s for _, s in scored) or 1
    x, acc = rnd.random() * tot, 0
    for f, s in scored:
        acc += s
        if x <= acc:
            return f, "exploiting (weighted by past performance)"
    return scored[0][0], "exploiting"

def report(brand="certtrack"):
    rows = [r for r in load() if r.get("brand", "certtrack") == brand]
    with_stats = [r for r in rows if r.get("stats")]
    print(f"{len(rows)} posts logged, {len(with_stats)} with TikTok stats.\n")
    for key in ("format", "mood", "angle", "industry"):
        g = group(rows, key)
        if g:
            print(f"By {key}:  (name, posts, avg views, avg engagement rate, score)")
            for k, n, v, er, sc in g:
                print(f"  {k:<12} n={n:<3} views={v:<8.0f} eng={er:.1%}  score={sc:.0f}")
            print()
    if with_stats:
        best = sorted(with_stats, key=lambda r: -score(r["stats"])[0])
        print("Top posts (reuse what worked: hook style, angle, format, music):")
        for r in best[:5]:
            s = r["stats"]
            print(f"  {r['date']} {r['format']}/{r.get('mood')} {r.get('angle')} views={s.get('views')} likes={s.get('likes')} "
                  f"comments={s.get('comments')} shares={s.get('shares')} saves={s.get('saves')} | hook: {r.get('hook')}")
        print("Weakest posts (avoid repeating these patterns):")
        for r in best[-3:][::-1]:
            s = r["stats"]
            print(f"  {r['date']} {r['format']}/{r.get('mood')} {r.get('angle')} views={s.get('views')} | hook: {r.get('hook')}")
        print()
    missing = [r for r in rows if not r.get("stats") and r.get("postiz_id")]
    if missing:
        print(f"{len(missing)} posts still need stats (oldest first): " + ", ".join(r["date"] for r in missing[:8]))
    print("Last 5 formats: " + ", ".join(r["format"] for r in rows[-5:]))
    print("Last 8 topics: " + " | ".join(r.get("topic", "?") for r in rows[-8:]))
    f, why = pick_next(load(), brand)
    print(f"\nNEXT FORMAT: {f}  ({why})  allowed moods: {', '.join(MOOD_FOR[f])}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report":
        report(sys.argv[2] if len(sys.argv) > 2 else "certtrack")
    elif cmd == "add":
        rows = load()
        e = json.loads(sys.argv[2])
        e.setdefault("brand", "certtrack")
        assert e.get("format") in FORMATS, f"format must be one of {FORMATS}"
        rows.append(e); save(rows); print("logged", e.get("date"), e["format"])
    elif cmd == "stats":
        rows = load(); pid = sys.argv[2]
        kv = {k: int(v) for k, v in (a.split("=") for a in sys.argv[3:])}
        hit = [r for r in rows if r.get("postiz_id") == pid or r.get("date") == pid]
        assert hit, f"no post {pid}"
        for r in hit:
            r["stats"] = {**r.get("stats", {}), **kv, "checked": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")}
        save(rows); print("updated", pid, kv)
