# -*- coding: utf-8 -*-
import json, sys
from pathlib import Path
sys.path.insert(0, ".")
from scripts.plan_episode import load_all, used_ranges, overlaps
blocks = load_all()
used = used_ranges(None)
banned = {"exnFXUMMLLI", "q0GyNI3X8cg", "IXiLxkgHUMM", "naVkgtFmRvg", "Sq1YChd0RqQ"}
shorts = json.loads(Path("state/used_shorts.json").read_text(encoding="utf-8")).get("windows") or []
out = []
for b in blocks:
    if b["video_id"] in banned or overlaps(b, used): continue
    if any(s["video_id"]==b["video_id"] and b["start"]<s["end"] and s["start"]<b["end"] for s in shorts): continue
    d = b["end"]-b["start"]
    if d < 45 or d > 300: continue
    t = (b.get("title") or "").strip()
    if not t: continue
    out.append(f"{'R' if b.get('risk') else ' '} [{b['video_id']}] {b['start']:.0f}-{b['end']:.0f} ({d:.0f}s) sc={b.get('score',0):.2f} | {t}")
out.sort(key=lambda s: s[2:15])
Path("work/_unused_1017.txt").write_text("\n".join(out), encoding="utf-8")
print(len(out))
