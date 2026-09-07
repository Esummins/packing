"""A126 T1 -- extract every DEAD leaf of an A119 certificate as exact rational Farkas data.

    python extract126.py <cert.json.gz> [--den 9]

A119's `check_local.py` is IMPORTED (read-only): its `Checker` walks and VALIDATES the tree, and
a subclass records, for every `dead` leaf the parent accepted (feasible bound leaves AND
infeasibility rays -- the parent captures only the former), the leaf's

  * variable box (per-leaf: the s range, the body boxes / slack cores, and the TILT CELL),
  * relaxed rows named by the Farkas multipliers, rebuilt by A119's own `LeafRows`,
  * multipliers.

Everything is then put on ONE denominator `D = 10^den`:

  * each row coefficient is rounded to the nearest multiple of `1/D` and the row's constant is
    LOWERED by the total rounding slack over the box, so the emitted rational row is IMPLIED by
    the true relaxed row (A119 `gen_local_lean.py`'s discipline, there with `den = 15`);
  * each box bound is rounded OUTWARD, so the emitted box CONTAINS the true one;
  * each multiplier is rounded to the nearest multiple of `1/D`, clamped at `0`.

None of these three roundings can make a false leaf pass, but any of them can make a true leaf
fail, so the Farkas bound is RE-EVALUATED from the emitted integers in exact rational arithmetic
and required to exceed `s0 = 969271/250000` (an infeasibility ray: `> 0`).  Nothing is written
unless every leaf passes.  Output: `results/<id>.leaves.json`, consumed by `gen_lean126.py`.
"""
from __future__ import annotations

import argparse, json, math, os, sys, time
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
A119 = os.path.abspath(os.path.join(HERE, "..", "..", "A119-local-cert-lean", "code"))
sys.path.insert(0, A119)
import check_local as C          # noqa: E402
from exactiv import SCALE        # noqa: E402

RES = os.path.abspath(os.path.join(HERE, "..", "results"))
S0 = Q(969271, 250000)


def rebuild(ch, node, cells, qrec):
    """the rows the multipliers name, rebuilt exactly as `C.Checker.dead` rebuilds them.
    Only called for leaves the parent has ALREADY validated."""
    box = ch.cellbox(cells)
    sel = {kp: tuple(v) for kp, v in node.get("sel", {}).items()}
    LR = C.LeafRows(ch.meta, ch.bodies, cells, sel, qrec, box)
    want, rows = {}, {}
    for ks, val in node["y"].items():
        parts = ks.split("|")
        if parts[0] == "w":
            key = ("w", parts[1], parts[2], parts[3], int(parts[4]))
        elif parts[0] == "s":
            key = ("s", parts[1], parts[2], int(parts[3]), int(parts[4]), int(parts[5]), parts[6])
        else:
            key = ("q", parts[1], parts[2], int(parts[3]), int(parts[4]), parts[5])
        want[key] = Q(val)
    for key in want:
        if key[0] == "w":
            rows[key] = LR.wall(key[1], key[2], key[3], key[4])
        else:
            rows.update(LR.sel_rows(key[1], key[2], key[3], key[4]))
    return box, sel, {k: rows[k] for k in want}, want


class CapChecker(C.Checker):
    """A119's checker with EVERY accepted dead leaf recorded (the parent records only the
    feasible ones).  The parent's verdict is authoritative: nothing is recorded that it
    rejected, and the recording never influences the walk."""

    def dead(self, node, cells, fixed, qrec):
        ok = C.Checker.dead(self, node, cells, fixed, qrec)
        if ok and bool(node.get("infeas")):
            box, sel, rows, want = rebuild(self, node, cells, qrec)
            self.capture.append(dict(cells=dict(cells), sel=dict(sel), qrec=dict(qrec),
                                     rows=rows, y=want, box=box, bound=None, node=node))
        return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("--den", type=int, default=9, help="everything on the denominator 10^DEN")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    D = 10 ** a.den

    t0 = time.time()
    cert = C.load(a.cert)
    ch = CapChecker(cert)
    ch.capture_max = 10 ** 9
    ok = ch.walk(cert["root"], ch.root_cells(), {}, {}, {})
    meta = cert["meta"]
    nv = meta["nv"]
    print("checker ok=%s  counts=%s  captured=%d  %.1f s"
          % (ok, ch.n, len(ch.capture), time.time() - t0))
    if not ok:
        sys.exit("certificate did not pass the A119 checker")
    if len(ch.capture) != ch.n["dead"]:
        sys.exit("captured %d of %d dead leaves" % (len(ch.capture), ch.n["dead"]))

    leaves, nz_total, worst = [], 0, None
    for cap in ch.capture:
        box = cap["box"]
        blo = [math.floor(Q(box[v].lo, SCALE) * D) for v in range(nv)]     # outward
        bhi = [math.ceil(Q(box[v].hi, SCALE) * D) for v in range(nv)]
        rows = []
        for key, yv in sorted(cap["y"].items(), key=lambda kv: str(kv[0])):
            f = cap["rows"][key]
            co, slack = {}, Q(0)
            for v, aiv in f.co.items():
                am = Q(aiv.lo + aiv.hi, 2 * SCALE)
                r = round(am * D)                                          # integer numerator
                rq = Q(r, D)
                wid = max(abs(Q(aiv.lo, SCALE) - rq), abs(Q(aiv.hi, SCALE) - rq))
                slack += wid * max(abs(Q(blo[v], D)), abs(Q(bhi[v], D)))
                if r != 0:
                    co[v] = r
            k = math.floor((Q(f.k.lo, SCALE) - slack) * D)
            y = max(0, round(Q(yv) * D))
            rows.append((co, k, y))
            nz_total += len(co)
        infeas = bool(cap["node"].get("infeas"))
        # re-evaluate the Farkas bound from the EMITTED integers, exactly
        acc, kacc = ({} if infeas else {0: Q(1)}), Q(0)
        for (co, k, y) in rows:
            yq = Q(y, D)
            for v, c in co.items():
                acc[v] = acc.get(v, Q(0)) + yq * Q(c, D)
            kacc += yq * Q(k, D)
        lb = kacc
        for v, c in acc.items():
            lb += min(c * Q(blo[v], D), c * Q(bhi[v], D))
        thr = Q(0) if infeas else S0
        if not lb > thr:
            sys.exit("leaf bound %s <= %s after rounding to 10^-%d" % (float(lb), float(thr), a.den))
        marg = lb - thr
        if worst is None or marg < worst[0]:
            worst = (marg, float(lb), infeas)
        leaves.append(dict(infeas=infeas, blo=blo, bhi=bhi,
                           rows=[dict(co=sorted(r[0].items()), k=r[1], y=r[2]) for r in rows],
                           cells={k: [float(v[0]), float(v[1])] for k, v in cap["cells"].items()},
                           sel={k: list(v) for k, v in cap["sel"].items()}))
    out = a.out or os.path.join(RES, "%s.leaves.json" % meta["id"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(dict(id=meta["id"], nv=nv, den=a.den,
                       s0=[S0.numerator, S0.denominator],
                       bodies=meta["bodies"], L=meta["L"], P=meta["P"],
                       s_lo=meta["s_lo"], s_hi=meta["s_hi"],
                       counts=dict(ch.n), leaves=leaves), f)
    print("leaves %d (%d infeasibility rays)  rows %d  nonzero coefficients %d"
          % (len(leaves), sum(1 for l in leaves if l["infeas"]),
             sum(len(l["rows"]) for l in leaves), nz_total))
    print("worst margin %.3e (bound %.9f, infeas=%s)" % (float(worst[0]), worst[1], worst[2]))
    print("wrote %s (%.1f MB, %.1f s)" % (out, os.path.getsize(out) / 1e6, time.time() - t0))


if __name__ == "__main__":
    main()
