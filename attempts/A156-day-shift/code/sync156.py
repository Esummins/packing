"""A156 -- the day's SINGLE writer into A57's canonical `tree_*.jsonl` files.

Same contract as A137's `sync137.py` (which it is a re-based copy of, and which remains the night's
writer): append-only, idempotent, and it never rewrites a row that already exists.  A `WALL-CAP`
is skipped -- CAP is never a verdict, so the node keeps its prior state -- and so are ERROR and
NO-RESULT rows.

What differs: the LP verdicts come from **A156's** `results/lp156_*.jsonl` as well as A137's
`emit_lp_*.jsonl`, the geometry rows from both attempts' `emit_geo_*.jsonl`, and each row is
stamped with the attempt that decided it (`emitted_by`).

    python code\\sync156.py --dry_run 1     # what it would append
    python code\\sync156.py                 # append
"""
import argparse
import collections
import glob
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
A137 = os.path.join(ROOT, "A137-night-shift-2")


def jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except Exception:
                    pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry_run", type=int, default=0)
    a = ap.parse_args()
    stats = collections.Counter()

    lp, who = {}, {}
    for p in sorted(glob.glob(os.path.join(A137, "results", "emit_lp_*.jsonl"))):
        for r in jl(p):
            lp[r["id"]] = r
            who[r["id"]] = "A137"
    for p in sorted(glob.glob(os.path.join(BASE, "results", "lp156_*.jsonl"))):
        for r in jl(p):
            lp[r["id"]] = r
            who[r["id"]] = "A156"

    geo_files = sorted(glob.glob(os.path.join(A137, "results", "emit_geo_*.jsonl"))) + \
        sorted(glob.glob(os.path.join(BASE, "results", "emit_geo_*.jsonl")))
    for gp in geo_files:
        tag = os.path.basename(gp)[len("emit_geo_"):-len(".jsonl")]
        # A156's deepen lane writes under an ALIAS tag (…G1a156_D2) whenever the canonical tag is
        # A137's own night file, because this attempt never appends to another chore's rows.  The
        # alias maps back to the canonical tree file here: "a156" is dropped from the key.
        canon = tag.replace("a156", "")
        if canon.endswith("_D2"):
            dest = os.path.join(A57, "results", f"tree_{canon}.jsonl")
        else:
            key, si = canon.rsplit("_s", 1)
            dest = os.path.join(A57, "results", f"tree_{key}_s{si}.jsonl")
        have = {r["id"] for r in jl(dest) if "id" in r}
        rows = []
        for r in jl(gp):
            if r["id"] in have:
                stats["already"] += 1
                continue
            if r.get("cert") is None:
                continue
            rows.append(r)
            have.add(r["id"])
            stats["geo"] += 1
        for qdir in (A137, BASE):
            for qp in glob.glob(os.path.join(qdir, "results", f"emitq_{tag}.json")):
                try:
                    Q = json.load(open(qp))
                except Exception:
                    continue
                for j in Q:
                    r = lp.get(j["id"])
                    if r is None or j["id"] in have:
                        continue
                    base = dict(j["geo"])
                    res = r.get("result")
                    if res == "PASS":
                        base["cert"] = "PASS"
                        base["cert_path"] = r.get("cert")
                    elif res == "NO-KILL":
                        base["cert"] = ("ALIVE-at-LP (tau >= budget: certification refused) "
                                        "-> queued for depth 2")
                    elif res == "WALL-CAP":
                        continue            # never a verdict: the node stays unclaimed
                    elif res in ("ERROR", "NO-RESULT"):
                        continue
                    else:
                        base["cert"] = f"FAIL({res})"
                    base.update(tau=r.get("tau"), converged=r.get("converged"),
                                eta=(r["tau"] - base["budget"]) if r.get("tau") is not None
                                else None,
                                minmass=r.get("minmass"), lp_seconds=r.get("lp_wall_s"),
                                core_scope=r.get("scope"), cores_exact=r.get("a_report"),
                                pin_gate=r.get("pin_gate"),
                                verifier="FROZEN verify_case.py (521cb01f)",
                                emitted_by=who.get(j["id"], "A156"))
                    rows.append(base)
                    have.add(j["id"])
                    stats["lp_" + who.get(j["id"], "A156")] += 1
        if rows and not a.dry_run:
            with open(dest, "a", encoding="utf-8") as f:
                for r in rows:
                    r["synced"] = time.strftime("%F %T")
                    f.write(json.dumps(r) + "\n")
        if rows:
            stats[os.path.basename(dest)] += len(rows)
    print(json.dumps(dict(stats), indent=1))


if __name__ == "__main__":
    main()
