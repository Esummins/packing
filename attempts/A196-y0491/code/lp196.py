"""A196 step 4 -- the two LPs at the node's fixed point, with the chord rows and the NO-family zone.

 (a) the EXACT-CORE LP (A57 caselp.solve_node on A144's ExactHyp: every role whose hull carries an A135 exact core is
     an UNATTACHED core -- pins, H, a meeter when its hull is small enough; budget 11 - #cores), the zone Z as
     `nofams` (v1's clause), A144's guard-line columns whose rhs = s - SUM_j minchord(hull_j, l) is EXACTLY what
     verify_case_v5 re-derives (G1; a declared rhs must equal rhs*).  A converged kill is certified by the FROZEN
     verify_case.py (sha 521cb01f...) when NO line carried density (the certificate is then a v1 certificate with
     cores + nofams verbatim), else by verify_case_v5 [C under v5 ONLY].
 (b) the WINDOWS + guard-line LP (A185 WindowsHyp: every role windowed on its pieces, its grown core attached where
     it has one; budget b4 = 11 - m + r_c), the same zone, rhs = s (every core attached), certified by v5 only.
The support of an alive LP is characterised: full-weight placements, their pairwise SAT gaps, fractional mass.
"""
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
os.makedirs(CERTS, exist_ok=True)
for _p in (os.path.join(ATT, "A191-combined-cascade", "code"), os.path.join(ATT, "A190-guardline-clause", "code"),
           os.path.join(ATT, "A185-boxed-windows-clause", "code"), os.path.join(ATT, "A170-certfix", "code"),
           os.path.join(ATT, "A168-cascade-fable", "code"), os.path.join(ATT, "A144-guard-lines", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import prio196                                                   # noqa: E402
import cert191 as C                                              # noqa: E402  READ-ONLY (A191)
import lines191 as LN                                            # noqa: E402  READ-ONLY (A191)
import emit190 as E                                              # noqa: E402  READ-ONLY (A190)
import winlp185 as W                                             # noqa: E402  READ-ONLY (A185)
import certwrap170 as CW                                         # noqa: E402  READ-ONLY (A170)
import guardline as GL                                           # noqa: E402  READ-ONLY (A144)
from caselp import Box, NoFam, warm_from_result, q, t_lo, t_hi   # noqa: E402  READ-ONLY (A57)
from warm57 import merged_warm                                   # noqa: E402  READ-ONLY (A57)
import rows196 as RW                                             # noqa: E402

S_RAT = GL.S_RAT
S0 = float(S_RAT)
N = 11
FROZEN = CW.FROZEN


class _R:
    """a minimal role for lines191.family: name, bbox(), core (K' verts or None)."""
    def __init__(self, name, hull, kprime):
        self.name, self._b, self.core = name, Box(*hull), ([(Fr(v[0]), Fr(v[1])) for v in kprime] if kprime else None)

    def bbox(self):
        return self._b


def nofams_of(rects):
    return [NoFam(x0, x1, y0, y1, [(0.0, 90.0)]) for (x0, x1, y0, y1) in rects]


def nofams_json(nfs):
    return [dict(x0=str(q(f.x0)), x1=str(q(f.x1)), y0=str(q(f.y0)), y1=str(q(f.y1)),
                 t_intervals=[[str(t_lo(a)), str(t_hi(b))] for a, b in f.thetas]) for f in nfs]


def line_family(node, extra_lines):
    roles = [_R(k, node["hull"][k], node["kprime"].get(k)) for k in node["hull"]]
    fam = LN.family(roles)
    seen = set((L.orient, L.off) for L in fam)
    for L in extra_lines:
        if (L.orient, L.off) not in seen:
            fam.append(GL.Line(L.orient, L.off, L.tag)); seen.add((L.orient, L.off))
    return fam


def warm_of(record, cls, max_rows=30000):
    d = json.load(open(os.path.join(ROOT, record), encoding="utf-8"))
    w0 = warm_from_result(d)
    try:
        wm = merged_warm(cls, max_rows=max_rows)[0]
    except Exception:                                            # noqa: BLE001
        wm = dict(atoms=[], rows=[])
    return dict(atoms=list(w0["atoms"]) + list(wm["atoms"]), rows=(list(w0["rows"]) + list(wm["rows"]))[:max_rows + 20000]), d


def support_kind(packing):
    """full-weight placements and their pairwise SAT gaps (gen_a57_lp's test): a real near-packing or a phantom."""
    def sq(cx, cy, th):
        c, s_ = math.cos(th), math.sin(th)
        return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]

    def sat(p, qq):
        axes = []
        for poly in (p, qq):
            for i in range(4):
                a, b = poly[i], poly[(i + 1) % 4]
                ex, ey = b[0] - a[0], b[1] - a[1]
                n = math.hypot(ex, ey)
                axes.append((-ey / n, ex / n))
        best = -9
        for ax in axes:
            pp = [x * ax[0] + y * ax[1] for x, y in p]
            q2 = [x * ax[0] + y * ax[1] for x, y in qq]
            best = max(best, min(q2) - max(pp), min(pp) - max(q2))
        return best
    pk = packing or []
    ys = [float(p.get("y", 0)) for p in pk]
    full = [p for p in pk if float(p.get("y", 0)) > 0.999]
    polys = [sq(float(p["cx"]), float(p["cy"]), float(p["theta"])) for p in full]
    gaps = [sat(polys[i], polys[j]) for i in range(len(polys)) for j in range(i + 1, len(polys))]
    worst = min(gaps) if gaps else None
    kind = ("empty" if not pk else ("integral: %d unit-weight placements, worst pairwise gap %+.4f (%s)" % (
        len(full), worst if worst is not None else 0.0, "a real packing of the support at s0" if (worst is None or worst >= -1e-6)
        else "overlapping: a near-packing, side >= s0 + %.4f" % (-worst)) if len(full) == len(pk)
        else "fractional: %d placements, %d at weight 1, mass %.3f (a phantom)" % (len(pk), len(full), sum(ys))))
    return dict(kind=kind, n=len(pk), n_full=len(full), mass=sum(ys), worst_gap=worst,
                rows=[[float(p["cx"]), float(p["cy"]), float(p["theta"]), float(p.get("y", 0))] for p in pk][:200])


def frozen_certify(res, hyp, tag, deadline, log, rounds=2):
    """A170's exact-core certificate through the FROZEN verifier, with A190's witness feedback."""
    out = os.path.join(CERTS, tag + "_frozen.json")
    lg, extra, budget = [], [], N - hyp.m()
    for rd in range(rounds + 1):
        tau = res["tau"]
        scale = max(1.005, min(1.30, (budget - 0.005) / tau - 0.002)) if tau > 1e-12 else 1.005
        cert = CW.make_certificate_exact(res, S_RAT, scale=scale, hyp=hyp)
        json.dump(cert, open(out, "w"), indent=0)
        tot = float(Fr(cert["total"]))
        if tot >= budget:
            lg.append(dict(round=rd, tau=tau, total=tot, result="MARGIN"))
            return "MARGIN", lg, out
        prio196.wait_box(own=1, max_wait=600, log=log)
        rc, txt = CW.run_frozen_verifier(out, jobs=1, depth=56, max_w=64, timeout=max(60, min(420, deadline - time.time())))
        lg.append(dict(round=rd, tau=tau, total=tot, rc=rc, verifier=CW.verifier_tail(txt)[:6]))
        if rc == 0:
            json.dump(dict(cert=out, rounds=lg, result="PASS", verifier=FROZEN, verifier_sha=CW.frozen_sha(), label="[C] frozen verify_case.py"),
                      open(out.replace(".json", ".certify.json"), "w"), indent=1)
            return "PASS", lg, out
        if rc == 2 or rd == rounds or rc is None or time.time() > deadline - 120:
            break
        wf = out.replace(".json", ".witnesses.json")
        if not os.path.exists(wf):
            break
        for w in json.load(open(wf)).get("witnesses", []):
            p = w.get("placement")
            if not p:
                continue
            th = math.radians(p["theta_deg"])
            extra.append((p["cx_float"], p["cy_float"], th))
            for d in (0.002, 0.005):
                for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d), (d, d), (-d, -d), (d, -d), (-d, d)):
                    extra.append((p["cx_float"] + dx, p["cy_float"] + dy, th))
        res, _ = C.solve_guarded(hyp, budget, [], warm_from_result(res), min(240, max(30, deadline - time.time() - 150)), extra_rows=extra)
        if not (res["tau"] < budget - 1e-6):
            lg.append(dict(round=rd + 1, tau=res["tau"], result="re-solve lost the kill"))
            break
    json.dump(dict(cert=out, rounds=lg, result="FAIL", verifier=FROZEN), open(out.replace(".json", ".certify.json"), "w"), indent=1)
    return "FAIL", lg, out
