"""A96 step 1: enumerate EVERY A57 node that the parametric pass can take, in run order.

Sources (read-only over A57):
  results/tree_{name}_interior_{TAG}_s*.jsonl   level-1 leaves, one file per shard
  results/tree_{name}_interior_{TAG}_D2.jsonl   level-2 children (deepen.py)

Classification, and why each class is or is not a parametric candidate:

  KILL-BY-LOGIC   NOT a candidate.  These boxes are killed because the child's core provably
                  meets a pin core -- a pure geometry fact that is NOT invariant in s
                  (cover_invariance.md CI-4: the cover box and the pins both move with s, so the
                  contradiction can flip).  They are recomputed per side by grid.py --ccheck.
                  Counted separately in the scoreboard; never fed to verify_param.
  ALIVE-at-LP     NOT a candidate: the LP never produced a certificate, so there is nothing to
                  re-emit.  These are the nodes that must descend to level 2.
  PASS / FAIL     candidate iff a case-measure-certificate-v1 file exists for it and
                    - it has no nofams (verify_param v1 rejects them), and
                    - sum(weights) < budget (certify.py's weight scaling can push a tight node
                      over its budget; such a document proves nothing and both verifiers reject
                      it with rc 2 -- excluded as MALFORMED-AT-SOURCE, not silently dropped).

Run order (brief item 2, with one documented change):
    1 epsgeo   PASS that needed an eps_geo repair -- highest yield: A95 measured 0.024 of four
               fixed sides on these, because the fixed-side route pays the repair four times.
    2 easy     PASS straight through.
    3 level2   the D2 children -- promoted ABOVE cert_fail (the brief's order puts them last)
               because the level-2 re-projection is a deliverable and cert_fail nodes are the
               slowest with the least yield (A95: 2 of 6 hit the 1500 s cap).
    4 fail     cert FAIL: the parametric run still discharges everything except a few witness
               cells, so it converts a dead fixed-side node into a near-complete window kill.

Writes results/selection96.json.
"""
import json, glob, os, sys
from fractions import Fraction as F

A57 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "A57-shadow-trees"))
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
NAMES = ("k5_11", "k5_16")
# Level-1: G1 ONLY.  G1 is the deployed cover (side s0, pin_delta = 1e-2 slack cores).  L1 is the
# earlier delta = 0 emission whose logic kills are quarantined under the old tag; its level-1
# leaves certify the same stratum but under a different pin hypothesis, so a window kill of an L1
# leaf does not discharge a G1 box.  Spending the pass on them buys no window coverage.
# Level-2: every *_D2.jsonl regardless of tag.  No G1_D2 exists yet (deepen at G1 starts when the
# scaler's G1 shard queue empties), so L1_D2 is the only level-2 corpus available to measure the
# per-child cost and descent rate with -- it is reported as a level-2 PROBE, not as coverage.
TAGS = ("G1", "L1")
L1_LEVELS = (2,)             # from tag L1 take D2 children only
GROUP_ORDER = ("epsgeo", "easy", "level2", "fail")


def epsgeo_seconds(r):
    return sum(s.get("seconds", 0.0) for s in (r.get("eps_geo") or []))


def cert_for(r, certdir):
    cp = r.get("cert_path")
    if cp and os.path.exists(cp):
        return cp
    base = os.path.join(certdir, r["id"] + ".json")
    return base if os.path.exists(base) else None


def certinfo(p):
    d = json.load(open(p))
    tot = sum(F(w) for w in d.get("weights", []))
    return dict(total_ge_budget=bool(tot >= F(d["budget"])),
                atoms=len(d.get("atoms", [])), budget=d.get("budget"),
                nofams=len(d["hypotheses"].get("nofams") or []),
                cores=len(d["hypotheses"]["cores"]),
                eps_geo=d.get("provenance", {}).get("eps_geo"))


def rows():
    """(row, class_key, level) for every A57 tree row, first record wins on duplicate id."""
    seen, out = set(), []
    for nm in NAMES:
        for tag in TAGS:
            key = f"{nm}_interior_{tag}"
            files = sorted(glob.glob(os.path.join(A57, "results", f"tree_{key}_s*.jsonl")))
            files += sorted(glob.glob(os.path.join(A57, "results", f"tree_{key}_D2.jsonl")))
            for f in files:
                lvl = 2 if f.endswith("_D2.jsonl") else 1
                if tag == "L1" and lvl not in L1_LEVELS:
                    continue
                certdir = os.path.join(A57, "certs", "tree", key + ("_D2" if lvl == 2 else ""))
                for ln in open(f):
                    ln = ln.strip()
                    if not ln:
                        continue
                    r = json.loads(ln)
                    k = (nm, tag, lvl, r["id"])
                    if k in seen:
                        continue
                    seen.add(k)
                    out.append((r, nm, tag, lvl, certdir, os.path.basename(f)))
    return out


def main():
    cand, stats = [], {}
    for r, nm, tag, lvl, certdir, src in rows():
        cls = nm + "_" + tag
        st = stats.setdefault(cls, dict(total=0, logic_kill=0, alive=0, no_cert=0, nofams=0,
                                        malformed=0, candidate=0, level2=0))
        st["total"] += 1
        if lvl == 2:
            st["level2"] += 1
        c = r.get("cert") or ""
        if c.startswith("KILL-BY-LOGIC"):
            st["logic_kill"] += 1
            continue
        if c.startswith("ALIVE"):
            st["alive"] += 1
            continue
        p = cert_for(r, certdir)
        if p is None:
            st["no_cert"] += 1
            continue
        try:
            ci = certinfo(p)
        except Exception:
            st["no_cert"] += 1
            continue
        if ci["nofams"]:
            st["nofams"] += 1
            continue
        if ci["total_ge_budget"]:
            st["malformed"] += 1
            continue
        st["candidate"] += 1
        if lvl == 2:
            g = "level2"
        elif c.startswith("FAIL"):
            g = "fail"
        elif r.get("eps_geo_used") is not None:
            g = "epsgeo"
        else:
            g = "easy"
        cand.append(dict(id=r["id"], name=nm, tag=tag, level=lvl, cls=cls, group=g, cert=c,
                         cert_file=p, src=src, parent=r.get("parent"),
                         eta=r.get("eta"), eps_geo_used=r.get("eps_geo_used"),
                         lp_seconds=r.get("lp_seconds") or 0.0,
                         cert_seconds=r.get("cert_seconds") or 0.0,
                         epsgeo_seconds=epsgeo_seconds(r),
                         fixed_wall_s=round((r.get("lp_seconds") or 0.0)
                                            + (r.get("cert_seconds") or 0.0)
                                            + epsgeo_seconds(r), 1),
                         **ci))
    # within a group: cheapest fixed-side wall first is WRONG (it front-loads the easy tail and
    # makes the mean look good); sort by atom count, which is the honest proxy for 4-D cost.
    cand.sort(key=lambda c: (GROUP_ORDER.index(c["group"]), c["atoms"], c["cls"], c["id"]))
    json.dump(dict(n=len(cand), stats=stats, order=GROUP_ORDER, selection=cand),
              open(os.path.join(OUT, "selection96.json"), "w"), indent=1)
    for cls in sorted(stats):
        print(cls, json.dumps(stats[cls]))
    from collections import Counter
    print("groups:", dict(Counter(c["group"] for c in cand)), "total candidates:", len(cand))


if __name__ == "__main__":
    main()
