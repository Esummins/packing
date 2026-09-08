"""A141 T6 -- the incremental attribution of the usable-slot kills against the CLIP kills.

A131 (`results/backlog_kills.jsonl`, 132 nodes) and A142 (`results/exactclip_kills_a57.jsonl`,
17 A57 nodes; `exactclip_kills_a60.jsonl`, 34 A60 nodes) already retire nodes by emptying the
hypothesis box at the exact pin core.  A141's slot kills are a DIFFERENT leaf (the slot is met by
one square, so SLOT-CROWD is contradicted) and this script measures how much of it is new.

    python t6_overlap.py
"""
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))

A131 = os.path.join(ROOT, "attempts", "A131-pin-clip", "results")
A142 = os.path.join(ROOT, "attempts", "A142-a57-review-gallery", "results")


def ids(path, key="id"):
    out = set()
    if not os.path.exists(path):
        return out
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            out.add(json.loads(ln)[key])
    return out


def main():
    a131 = ids(os.path.join(A131, "backlog_kills.jsonl"))
    a131_clip = ids(os.path.join(A131, "backlog_clip_only.jsonl"))
    a142_57 = ids(os.path.join(A142, "exactclip_kills_a57.jsonl"))
    a142_60 = ids(os.path.join(A142, "exactclip_kills_a60.jsonl"))
    clip = a131 | a142_57 | a142_60

    rows = []
    for f in sorted(glob.glob(os.path.join(BASE, "results", "t2_a5760_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            rows.append(json.loads(ln))
    swept = {}
    for r in rows:
        swept.setdefault(r["nid"], r)
    kills = {}
    for r in rows:
        if r.get("kill"):
            kills.setdefault(r["nid"], r)

    by_src = collections.Counter(r["src"] for r in kills.values())
    by_cls = collections.Counter(r["cls"] for r in kills.values())
    a57 = {n for n, r in kills.items() if r["cls"] in ("k5_11", "k5_16")}
    a60 = {n for n, r in kills.items() if r["cls"] == "trump5"}

    out = dict(
        swept_records=len(rows), swept_nodes=len(swept),
        kill_nodes=len(kills), kill_pairs=sum(len(r["kill_cells"]) for r in kills.values()),
        by_src=dict(by_src), by_cls=dict(by_cls),
        slots=dict(collections.Counter(c for r in kills.values() for c in r["kill_cells"])),
        levels=dict(collections.Counter(r["level"] for r in kills.values())),
        clip_lists=dict(a131=len(a131), a131_clip_only=len(a131_clip),
                        a142_a57=len(a142_57), a142_a60=len(a142_60), union=len(clip)),
        a57=dict(kills=len(a57), overlap_with_clip=len(a57 & clip),
                 new=len(a57 - clip), overlap_ids=sorted(a57 & clip)),
        a60=dict(kills=len(a60), overlap_with_clip=len(a60 & clip),
                 new=len(a60 - clip), overlap_ids=sorted(a60 & clip)),
        clip_nodes_not_swept=len(clip - set(swept)),
    )
    p = os.path.join(BASE, "results", "t6_overlap.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("a57", "a60")}, indent=1))
    for k in ("a57", "a60"):
        print(k, {kk: vv for kk, vv in out[k].items() if kk != "overlap_ids"},
              "overlap ids:", out[k]["overlap_ids"][:10])
    print("wrote", p)


if __name__ == "__main__":
    sys.exit(main())
