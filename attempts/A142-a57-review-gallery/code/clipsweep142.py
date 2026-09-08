"""A142 -- the pin-clip re-run with the EXACT pin cores, over the surviving population.

A131 deployed the clip with the STOCK pin core half-side A_PIN = 1/2 - delta = 0.49.  A135
certified that the pin's guaranteed core is the larger square of half-side 1/2 - delta/sqrt2 =
0.4929289..., and that the frozen verifiers take the half-side VERBATIM.  Enlarging a_pin is
sound for the clip for the same reason it is sound for the verifier: the conditioned square is
interior-disjoint from the pin square, and the pin square CONTAINS K'(P) at every pose of the pin
box (certified vertex-wise), so it is interior-disjoint from K'(P) too.  So the clip run at
a_pin = a_exact is a strictly stronger geometric test than the deployed one, at the same cost.

A60 has never been clipped at all: its pins are EXACT placements (box x0 = x1), so their
guaranteed core is the whole unit square, a_pin = 1/2.

This script measures, geometry only, no LP:
  * A57: the 465 surviving work-owing nodes, clip at a_pin = 0.49 (A131's deployed value, the
    control) and at a_pin = a_exact, 8 tilt sub-bins, and reports the nodes that go EMPTY only
    under the exact core -- those are NEW T5''' kills the deployed clip cannot see;
  * A60: all 283 nodes with an LP support, clip at a_pin = 1/2.

    set PYTHONDONTWRITEBYTECODE=1 && python code/clipsweep142.py
"""
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import gallery142 as G                                        # noqa: E402
import pinclip                                                # noqa: E402
from caselp import Box                                        # noqa: E402

A_STOCK = pinclip.A_PIN                       # 49/100, the deployed value
A_EXACT = Fr(1, 2) - Fr(1, 100) / Fr(2).__rtruediv__(1) if False else None


def exact_pin_a(boxes):
    """the certified exact half-side of the pins of this hypothesis (they are congruent)."""
    import exactcore
    a, a0, ok = exactcore.exact_a(Box.from_json(boxes[0]))
    return (a if a is not None else a0), a0, ok


def run(camp, ids, out):
    rows = []
    t0 = time.time()
    for n, nid in enumerate(ids):
        try:
            d, _ = G.load_node(camp, nid)
        except Exception as ex:
            rows.append(dict(id=nid, camp=camp, error=str(ex)[:80]))
            continue
        boxes = d["hyp"]["boxes"]
        sl = G.slots_for(camp, nid)
        B = Box.from_json(boxes[-1])
        a_ex, a_st, ok = exact_pin_a(boxes)
        r = dict(id=nid, camp=camp, level=1 + nid.count("_D"),
                 a_stock=float(a_st), a_exact=float(a_ex), a_exact_certified=bool(ok))
        for tag, ap in (("stock", Fr(a_st).limit_denominator(10 ** 12) if camp == "A60"
                         else A_STOCK),
                        ("exact", Fr(a_ex).limit_denominator(10 ** 12))):
            try:
                c = pinclip.clip_node(B, sl, nsub=8, a_pin=ap)
                r[f"kept_{tag}"] = float(c["kept_vol"])
                r[f"empty_{tag}"] = bool(c["empty"])
                r[f"nempty_{tag}"] = int(c["n_empty"])
                r[f"refused_{tag}"] = bool(c.get("refused"))
            except Exception as ex:
                r[f"kept_{tag}"] = None
                r[f"empty_{tag}"] = None
                r[f"err_{tag}"] = str(ex)[:80]
        rows.append(r)
        if (n + 1) % 50 == 0:
            print(f"  {camp} {n + 1}/{len(ids)}  {time.time() - t0:.0f} s", flush=True)
    json.dump(rows, open(out, "w", encoding="utf-8"), indent=1)
    return rows


def main():
    pop = json.load(open(os.path.join(BASE, "results", "population142.json"), encoding="utf-8"))
    a57 = [r["id"] for r in pop["rank_a57"]]
    a60 = [r["id"] for r in pop["rank_a60"]]
    r57 = run("A57", a57, os.path.join(BASE, "results", "clipsweep142_A57.json"))
    r60 = run("A60", a60, os.path.join(BASE, "results", "clipsweep142_A60.json"))

    def summarise(rows, camp):
        ok = [r for r in rows if r.get("kept_exact") is not None]
        es = sum(1 for r in ok if r.get("empty_stock"))
        ee = sum(1 for r in ok if r.get("empty_exact"))
        new = [r["id"] for r in ok if r.get("empty_exact") and not r.get("empty_stock")]
        touched = sum(1 for r in ok if (r.get("kept_exact") or 1.0) < 0.999)
        tighter = sum(1 for r in ok
                      if (r.get("kept_exact") or 1.0) < (r.get("kept_stock") or 1.0) - 1e-12)
        return dict(camp=camp, n=len(rows), measured=len(ok), empty_stock=es, empty_exact=ee,
                    new_empty_under_exact=new, n_new=len(new), touched_exact=touched,
                    tighter_than_stock=tighter,
                    mean_kept_stock=round(sum(r.get("kept_stock") or 0 for r in ok)
                                          / max(1, len(ok)), 5),
                    mean_kept_exact=round(sum(r.get("kept_exact") or 0 for r in ok)
                                          / max(1, len(ok)), 5))
    s = dict(a57=summarise(r57, "A57"), a60=summarise(r60, "A60"),
             note="A57 'stock' = A131's deployed a_pin = 0.49; A57 'exact' = A135's certified "
                  "1/2 - delta/sqrt2. A60's pins are EXACT placements, so 'stock' and 'exact' "
                  "are both essentially 1/2 and the clip has never been run on A60 before.")
    p = os.path.join(BASE, "results", "clipsweep142.json")
    json.dump(s, open(p, "w", encoding="utf-8"), indent=1)
    print(json.dumps(s, indent=1))
    print("wrote", p)


if __name__ == "__main__":
    main()
