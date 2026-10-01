"""Merge the lyric sheet with WhisperX word times -> analysis/timeline.json.

Each lyric word is matched to a transcript word (difflib over normalised tokens);
unmatched words are interpolated between matched neighbours, so every lyric line
gets start/end times even where Whisper misheard the singing.
"""
import difflib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())

def parse_sheet(path):
    sections, cur = [], None
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^\[([^\]]+)\]\s*(.*)$", line)
        if m and not m.group(2):
            if m.group(1).lower() == "end":
                continue
            name = m.group(1)
            cur = {"tag": name, "kind": re.split(r"[:\s]", name)[0].lower(), "lines": []}
            sections.append(cur)
            continue
        speaker = None
        if m:
            speaker, line = m.group(1), m.group(2)
        cur["lines"].append({"text": line, "speaker": speaker or cur["tag"].split(":", 1)[-1].split(",")[0].strip()})
    return sections

def align(L, T):
    """Monotonic DP alignment (Needleman-Wunsch) of lyric tokens L to transcript tokens T."""
    import numpy as np
    n, m = len(L), len(T)
    sim = lambda a, b: 2.0 if a == b else (1.0 if difflib.SequenceMatcher(None, a, b).ratio() >= 0.75 else -1.0)
    GAP = -0.4
    D = np.zeros((n + 1, m + 1)); P = np.zeros((n + 1, m + 1), np.int8)
    D[1:, 0] = GAP * np.arange(1, n + 1); D[0, 1:] = GAP * np.arange(1, m + 1)
    P[1:, 0] = 1; P[0, 1:] = 2
    for i in range(1, n + 1):
        a = L[i - 1]
        for j in range(1, m + 1):
            d = D[i - 1, j - 1] + sim(a, T[j - 1][0])
            u = D[i - 1, j] + GAP
            l = D[i, j - 1] + GAP
            if d >= u and d >= l:
                D[i, j], P[i, j] = d, 0
            elif u >= l:
                D[i, j], P[i, j] = u, 1
            else:
                D[i, j], P[i, j] = l, 2
    times = [None] * n
    i, j = n, m
    while i > 0 and j > 0:
        p = P[i, j]
        if p == 0:
            if sim(L[i - 1], T[j - 1][0]) > 0:
                times[i - 1] = (T[j - 1][1], T[j - 1][2])
            i, j = i - 1, j - 1
        elif p == 1:
            i -= 1
        else:
            j -= 1
    return times

def main(words_path=ROOT / "analysis/words.json", out=ROOT / "analysis/timeline.json"):
    sections = parse_sheet(ROOT / "analysis/lyrics_sung.txt")
    segs = json.loads(Path(words_path).read_text())
    tw = [(norm(w["w"]), w["s"], w["e"]) for s in segs for w in s["words"] if w.get("s") is not None and norm(w["w"])]
    lw = []  # (section idx, line idx, word)
    for si, sec in enumerate(sections):
        for li, ln in enumerate(sec["lines"]):
            for w in ln["text"].split():
                if norm(w):
                    lw.append((si, li, w))
    times = align([norm(w) for *_x, w in lw], tw)
    matched = sum(t is not None for t in times)
    known = [i for i, t in enumerate(times) if t]
    for i in range(len(times)):  # interpolate gaps
        if times[i]:
            continue
        prev = max((k for k in known if k < i), default=None)
        nxt = min((k for k in known if k > i), default=None)
        t0 = times[prev][1] if prev is not None else 0.0
        t1 = times[nxt][0] if nxt is not None else t0 + 2.0
        span = (nxt if nxt is not None else len(times)) - (prev if prev is not None else -1)
        pos = i - (prev if prev is not None else -1)
        s = t0 + (t1 - t0) * (pos - 0.5) / span
        times[i] = (s, s + (t1 - t0) / span * 0.8)
    for (si, li, w), (s, e) in zip(lw, times):
        sections[si]["lines"][li].setdefault("words", []).append({"w": w, "s": round(s, 3), "e": round(e, 3)})
    for sec in sections:
        for ln in sec["lines"]:
            ws = ln.get("words", [])
            ln["start"], ln["end"] = (ws[0]["s"], ws[-1]["e"]) if ws else (None, None)
        st = [l["start"] for l in sec["lines"] if l["start"] is not None]
        sec["start"] = min(st) if st else None
    for a, b in zip(sections, sections[1:]):
        a["end"] = b["start"]
    sections[-1]["end"] = json.loads((ROOT / "analysis/beats.json").read_text())["duration"]
    Path(out).write_text(json.dumps(sections, indent=1))
    print(f"matched {matched}/{len(lw)} lyric words ({100 * matched / len(lw):.0f}%)")
    for i, s in enumerate(sections):
        print(f"{i:2d} {s['start']:7.2f}-{s['end']:7.2f}  {s['tag']}")

if __name__ == "__main__":
    main(*sys.argv[1:])
