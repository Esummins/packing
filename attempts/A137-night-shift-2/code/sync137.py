"""A137 -- the SINGLE writer that appends tonight's finished rows into A57's canonical files.

Two sources, both in the tree's own record format already:
  results/emit_geo_<key>_s<i>.jsonl   geometry verdicts from emit137 (logic kills, parent boxes,
                                      canaries) -- these are complete records;
  results/emit_lp_<key>_s<i>.jsonl    the LP + frozen-verifier verdict for the children that
                                      survived the screens (written by run137/node137), merged
                                      onto the geometry record the emitter kept for them.

Appends to `attempts/A57-shadow-trees/results/tree_<key>_s<i>.jsonl`, skipping any id already
present there (idempotent, so it can be re-run at any time).  Nothing is ever rewritten: the
prior-verdict discipline of `superseded_by_*.jsonl` is for nodes that already had a verdict; these
are new ids that never had one.
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
    # id -> LP record, from every worker file
    lp = {}
    for p in glob.glob(os.path.join(BASE, "results", "emit_lp_*.jsonl")):
        for r in jl(p):
            lp[r["id"]] = r
    for gp in sorted(glob.glob(os.path.join(BASE, "results", "emit_geo_*.jsonl"))):
        tag = os.path.basename(gp)[len("emit_geo_"):-len(".jsonl")]
        if tag.endswith("_D2"):
            dest = os.path.join(A57, "results", f"tree_{tag}.jsonl")
        else:
            key, si = tag.rsplit("_s", 1)
            dest = os.path.join(A57, "results", f"tree_{key}_s{si}.jsonl")
        have = {r["id"] for r in jl(dest)}
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
        # the LP verdicts, merged onto the geometry record the queue carried
        for qp in glob.glob(os.path.join(BASE, "results", f"emitq_{tag}.json")):
            for j in json.load(open(qp)):
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
                    continue          # never a verdict: the node stays unclaimed
                elif res in ("ERROR", "NO-RESULT"):
                    continue
                else:
                    base["cert"] = f"FAIL({res})"
                base.update(tau=r.get("tau"), converged=r.get("converged"),
                            eta=(r["tau"] - base["budget"]) if r.get("tau") is not None else None,
                            minmass=r.get("minmass"), lp_seconds=r.get("lp_wall_s"),
                            core_scope=r.get("scope"), cores_exact=r.get("a_report"),
                            pin_gate=r.get("pin_gate"),
                            verifier="FROZEN verify_case.py (521cb01f)",
                            emitted_by="A137")
                rows.append(base)
                have.add(j["id"])
                stats["lp"] += 1
        if rows and not a.dry_run:
            with open(dest, "a", encoding="utf-8") as f:
                for r in rows:
                    r["synced"] = time.strftime("%F %T")
                    f.write(json.dumps(r) + "\n")
        stats[os.path.basename(dest)] += len(rows)
    print(json.dumps(dict(stats), indent=1))


if __name__ == "__main__":
    main()
