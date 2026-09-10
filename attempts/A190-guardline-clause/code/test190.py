"""A190 unit tests of the guard-line clause on SYNTHETIC certificates (seconds; no LP).

 T1  line-only cover: no atoms, 4 horizontal densities z = 3 at spacing 0.85 (< 1: every admissible closed unit
     square crosses one of them with chord >= 1/3 -- at 45 deg a line at distance V has chord 2(sqrt2/2 - V), and
     V <= 0.425 gives >= 0.564), no cores, n = 100 so the total 12 s < 100: expect PASS, every box line-covered.
 T2  one line only: squares far from it have mass 0: expect FAIL with HOLE witnesses whose exact mass is 0.
 T3  (G1) declared rhs above the re-derived rhs*: exit 2.
 T4  a core whose pbox does not contain it: exit 2.
 T5  two cores sharing a unit square (both with positive chord on the line): exit 2 (not provably distinct).
 T6  the rhs* arithmetic on an A57-style hypothesis (two pins + a boxed square on the PI's line of Y0147): the
     verifier's rhs* equals A144's guard_row rhs exactly, and a certificate declaring that rhs loads.
 T7  --scale-weights scales z with the weights (the total printed follows).
    python test190.py
"""
import contextlib
import io
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
TMP = os.path.join(BASE, "results", "tmp")
os.makedirs(TMP, exist_ok=True)
sys.path.insert(0, HERE)
import verify_case_v5 as v5                                      # noqa: E402
S = "969271/250000"


def run(cert, name, extra=()):
    p = os.path.join(TMP, "test190_%s.json" % name)
    json.dump(cert, open(p, "w"))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = v5.main([p, "--jobs", "1", "--depth", "40", "--max-witnesses", "8", "--quiet", "--report",
                      p[:-5] + ".report.json", "--witness-file", p[:-5] + ".w.json"] + list(extra))
    return rc, buf.getvalue(), p


def base(lines, cores=(), atoms=(), weights=(), n=11):
    return dict(format="test", n=n, s=S, budget=n - len(cores), atoms=[[str(a), str(b)] for a, b in atoms],
                weights=[str(w) for w in weights], hypotheses=dict(cores=list(cores), nofams=[], guardlines=lines))


def gl(orient, off, z, rhs):
    return dict(orient=orient, off=str(off), z=str(z), rhs=str(rhs))


def main():
    s = Fr(S)
    ok = True
    # T1
    lines = [gl("h", Fr(1, 2) + Fr(17, 20) * k, 3, s) for k in range(4)]
    rc, out, p = run(base(lines, n=100), "t1")
    st = json.load(open(p[:-5] + ".report.json"))["stats"]["free"]
    print("T1 line-only cover: rc", rc, "boxes", st["boxes"], "line-only covers", st["line_only_covers"],
          "atom checks", st["exact_atom_checks"], "->", "OK" if rc == 0 and st["exact_atom_checks"] == 0 else "FAIL")
    ok &= rc == 0
    # T2
    rc, out, p = run(base([gl("h", Fr(3, 2), 2, s)], n=100), "t2")
    w = json.load(open(p[:-5] + ".w.json"))["witnesses"]
    holes = [x for x in w if x.get("kind") == "hole"]
    zero = all(Fr(x["exact_mass"]) == 0 for x in holes)
    print("T2 one line: rc", rc, "witnesses", len(w), "holes", len(holes), "all mass 0:", zero,
          "->", "OK" if rc == 1 and holes and zero else "FAIL")
    ok &= rc == 1 and bool(holes) and zero
    # T3
    rc, out, p = run(base([gl("h", Fr(3, 2), 1, s + 1)]), "t3")
    print("T3 rhs > rhs*: rc", rc, "->", "OK" if rc == 2 and "re-derived" in out else "FAIL", "|", out.strip().splitlines()[0][:100])
    ok &= rc == 2
    # T4: a pin core at (1/2, 1/2), t = 0, a = 0.49, with a pbox that does not contain it
    core = dict(kx="1/2", ky="1/2", tm="0", a="49/100", pbox=dict(x0="2", x1="2", y0="2", y1="2", t0="0", t1="0"))
    rc, out, p = run(base([gl("h", Fr(3, 2), 1, s)], cores=[core]), "t4")
    print("T4 bad pbox: rc", rc, "->", "OK" if rc == 2 and "pbox" in out else "FAIL", "|", out.strip().splitlines()[0][:100])
    ok &= rc == 2
    # T5: two small cores inside one unit square, both crossed by y = 1/2
    c1 = dict(kx="3/10", ky="1/2", tm="0", a="1/10")
    c2 = dict(kx="7/10", ky="1/2", tm="0", a="1/10")
    rc, out, p = run(base([gl("h", Fr(1, 2), 1, s)], cores=[c1, c2]), "t5")
    print("T5 non-distinct cores: rc", rc, "->", "OK" if rc == 2 and "distinct" in out else "FAIL", "|", out.strip().splitlines()[0][:100])
    ok &= rc == 2
    # T6: Y0147's line y = s0 - 0.99 with pin P2 (0.5, 3.3770839) and H's box; rhs = s - 1 - 1 (A144 measurement.md)
    sys.path.insert(0, os.path.join(BASE, "..", "A144-guard-lines", "code"))
    import guardline as G
    from caselp import Box, t_lo, t_hi
    hb = Box(2.357813, 2.49757, 2.637327, 2.777084, 82.3718503314193, 90.0)
    hh = 0.01 / math.sqrt(2.0)
    pins = [Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in ((0.5, 0.5), (0.5, 3.3770839))]
    ln = G.Line("h", Fr(round((float(s) - 0.99) * 10 ** 9), 10 ** 9))
    r144 = G.guard_row(pins, hb, ln)
    cores = []
    for b in pins + [hb]:
        k = b.core()
        cores.append(dict(kx=str(k.kx), ky=str(k.ky), tm=str(k.tm), a=str(k.a),
                          pbox=dict(x0=str(Fr(b.x0)), x1=str(Fr(b.x1)), y0=str(Fr(b.y0)), y1=str(Fr(b.y1)),
                                    t0=str(max(Fr(0), t_lo(b.th0))), t1=str(min(Fr(1), t_hi(b.th1))))))
    d, *_ = v5.load_certificate_v5(run(base([gl("h", ln.off, 0, r144["rhs"])], cores=cores), "t6")[2])
    L = d["_lines"][0]
    print("T6 Y0147 rhs*:", float(L.rhs_star), "A144 rhs:", float(r144["rhs"]), "terms", [(j, float(c)) for j, c in L.terms],
          "->", "OK" if L.rhs_star == r144["rhs"] else "FAIL")
    ok &= L.rhs_star == r144["rhs"]
    # T7
    rc, out, p = run(base([gl("h", Fr(3, 2), 1, s)], n=100), "t7", extra=["--scale-weights", "2"])
    print("T7 scale: ", [l for l in out.splitlines() if l.startswith("s = ")][0][-80:], "->",
          "OK" if "line part 7.754168" in out else "FAIL")
    ok &= "line part 7.754168" in out
    print("ALL OK" if ok else "SOME TEST FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
