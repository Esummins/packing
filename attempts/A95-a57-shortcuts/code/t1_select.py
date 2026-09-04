"""A95 T1 step 1: pick the 20 k5_11 G1 level-1 nodes to re-emit parametrically.

10 easy PASS  = cert PASS, no eps_geo repair, largest headroom (most negative eta)
 5 marginal   = cert PASS with the tightest headroom (eta nearest 0); in practice the
                eps_geo-repaired leaves land here, which is exactly the T25 origin split
 5 failed     = cert FAIL(eps_geo retries exhausted); the base certify.py cert file exists

Read-only over A57.  Writes results/t1_selection.json.
"""
import json, glob, os

A57 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "A57-shadow-trees"))
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
CERTDIR = os.path.join(A57, "certs", "tree", "k5_11_interior_G1")


def epsgeo_seconds(r):
    return sum(s.get("seconds", 0.0) for s in (r.get("eps_geo") or []))


def load():
    """Rows, deduplicated by id keeping the FIRST record.  A57's s1 shard was re-run over its
    tail, so 15 ids appear twice; the second copy has lp_seconds = 0 (the node json was reloaded
    from disk) and would understate the fixed-side wall."""
    R, seen = [], set()
    for f in sorted(glob.glob(os.path.join(A57, "results", "tree_k5_11_interior_G1_s*.jsonl"))):
        for ln in open(f):
            ln = ln.strip()
            if not ln:
                continue
            r = json.loads(ln)
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            r["_shard"] = os.path.basename(f)
            R.append(r)
    return R


def cert_for(r):
    """The case-measure certificate whose LP data we convert.  For a PASS that needed an
    eps_geo repair the PASSing cert is the *_epsgeoM.json one (cert_path); for a FAIL we take
    the base certify.py output (it exists even though verification failed)."""
    cp = r.get("cert_path")
    if cp and os.path.exists(cp):
        return cp
    base = os.path.join(CERTDIR, r["id"] + ".json")
    return base if os.path.exists(base) else None


def info(p):
    from fractions import Fraction as F
    d = json.load(open(p))
    tot = sum(F(w) for w in d.get("weights", []))
    return dict(total_ge_budget=bool(tot >= F(d["budget"])),
                atoms=len(d.get("atoms", [])), budget=d.get("budget"),
                total=d.get("total"), nofams=len(d["hypotheses"].get("nofams") or []),
                cores=len(d["hypotheses"]["cores"]),
                lp_tau=d.get("provenance", {}).get("lp_tau"),
                eps_geo=d.get("provenance", {}).get("eps_geo"))


def main():
    R = load()
    cand = []
    for r in R:
        c = r.get("cert") or ""
        if c.startswith("KILL-BY-LOGIC") or c.startswith("ALIVE"):
            continue
        p = cert_for(r)
        if p is None:
            continue
        try:
            ci = info(p)
        except Exception as e:
            continue
        if ci["nofams"]:
            continue                       # verify_param v1 rejects nofams (NO children)
        if ci["total_ge_budget"]:
            # certify.py's x1.0934 weight scaling can push sum(w) over the budget on a tight
            # node; such a document proves nothing and both verifiers reject it up front (rc 2).
            # Excluding them keeps the cost measurement about 4-D search, not about malformed
            # input -- there are 4 such rows among the 17 k5_11 G1 cert_fail nodes.
            continue
        cand.append(dict(id=r["id"], cert=c, cert_file=p,
                         eta=r.get("eta"), tau=r.get("tau"),
                         scale_ceiling=r.get("scale_ceiling"),
                         eps_geo_used=r.get("eps_geo_used"),
                         lp_seconds=r.get("lp_seconds") or 0.0,
                         cert_seconds=r.get("cert_seconds") or 0.0,
                         epsgeo_seconds=epsgeo_seconds(r),
                         fixed_wall_s=round((r.get("lp_seconds") or 0.0)
                                            + (r.get("cert_seconds") or 0.0)
                                            + epsgeo_seconds(r), 1),
                         **ci))
    passes = [c for c in cand if c["cert"] == "PASS"]
    fails = [c for c in cand if c["cert"].startswith("FAIL")]
    # "easy" = certified straight through, comfortable headroom (eta <= -1).  Sampled EVENLY
    # across the fixed-side wall distribution rather than off its cheap tail, so the cost ratio
    # is representative of the class instead of flattering the parametric route.
    direct = sorted([c for c in passes if c["eps_geo_used"] is None and c["eta"] <= -1.0],
                    key=lambda c: (c["fixed_wall_s"], c["id"]))
    idx = sorted({round(i * (len(direct) - 1) / 9) for i in range(10)})
    easy = [direct[i] for i in idx]
    rest = [c for c in passes if c["id"] not in {e["id"] for e in easy}]
    marginal = sorted(rest, key=lambda c: -c["eta"])[:5]
    # spread the 5 FAILs over the atom range rather than taking the head
    fails = sorted(fails, key=lambda c: c["atoms"])
    if len(fails) > 5:
        idx = [round(i * (len(fails) - 1) / 4) for i in range(5)]
        fails = [fails[i] for i in sorted(set(idx))]
    sel = ([dict(group="easy_pass", **c) for c in easy]
           + [dict(group="marginal_pass", **c) for c in marginal]
           + [dict(group="cert_fail", **c) for c in fails])
    json.dump(dict(n_candidates=len(cand), n_pass=len(passes), selection=sel),
              open(os.path.join(OUT, "t1_selection.json"), "w"), indent=1)
    for s in sel:
        print(f"{s['group']:14s} {s['id']:22s} atoms={s['atoms']:4d} eta={s['eta']:+.4f} "
              f"epsgeo={s['eps_geo_used']} fixed_wall={s['fixed_wall_s']:8.1f}s")
    print(f"candidates={len(cand)} pass={len(passes)} selected={len(sel)}")


if __name__ == "__main__":
    main()
