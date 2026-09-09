"""A183 (3) -- the LP CONSUMES THE SURVIVING PIECES of a role, not its union box.

The frozen verifier (A143 verify_case.py, sha 521cb01f...) reads ONE rational square per
hypothesised packed square: hypotheses.cores = [{kx, ky, tm, a}], exempting every unit square Q
that meets some core, with the bridge "some square Q0 of the packing CONTAINS the core".  It does
not read the box a core carries, and it cannot take a LIST of boxes per square: an exemption
"Q meets some K_i of a list" is UNSOUND for the bridge (a packed square other than Q0 may meet a
K_i it does not contain and would be wrongly exempt), while a per-piece disjunction has no clause
at all.  What v1 CAN consume from the pieces is any rational square K with K ⊆ K'(role) = the
certified intersection of the per-piece cores (A172): every pose in the surviving pieces contains
its piece's core, hence K'(role), hence K [T].  lp168's `ExactHyp(boxes)` used the core of the
UNION BOX of the pieces -- the poses the clip excluded are re-admitted and the core shrinks
(cascade168 stage_nodes: "LP box = bounding box of the role's pieces").  Here the core per role
is the union box's A135 exact core (its centre and tilt kept) GROWN inside K'(role): the half-side
is bisected upward while the four corners stay `polycore.vertex_ok` against EVERY surviving piece
(K(union box) ⊆ K'(role); each K(piece) is convex, so four certified corners put the whole square
inside) -- a Core(kx, ky, tm, a', box=union bbox) with a' >= a that the LP's row filter uses and
certwrap170 carries verbatim (it never shrinks a live core).  (`Role.axis`, the centred AXIS square
inside K', was tried first and is SMALLER on root/D0/S1: 0.301 / 0.293 / 0.360 against the union
box's tilted 0.380 / 0.304 / 0.374 -- an axis square about the centroid is a poor inscription of a
tilted polygon; it is reported as `a_axis`.)  The polygon K' itself would need a v4 clause: hypotheses.
poly_cores = [{vertices: [[x, y], ...]}] with the exemption "Q meets the closed convex polygon"
decided by exact SAT over Q's two axes and the polygon's edge normals, bridge unchanged.

    python lp183.py --cell l1_104 --node root/D0/S1 [--cap 240] [--cert_time 150]
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import roles168 as R                                             # noqa: E402
import resume168 as RS                                           # noqa: E402
import lp168 as L                                                # noqa: E402
import polycore as PC                                            # noqa: E402
import renorm181 as R8                                           # noqa: E402
from caselp import Box, Core, Hyp, solve_node                    # noqa: E402


def grow_core(core, pieces, iters=40):
    """the union-box exact core (kx, ky, tm, a) ENLARGED about its own centre and tilt while its four
    corners stay `vertex_ok` against EVERY surviving piece: K(union box) ⊆ K'(role), each K(piece)
    is convex, so four certified corners put the whole square inside K'(role) [T].  Returns the
    grown Core (a >= the input's; the input's own a is re-certified first)."""
    kx, ky, tm, cm, sm = Fr(core.kx), Fr(core.ky), Fr(core.tm), Fr(core.cm), Fr(core.sm)

    def ok(a):
        for i in (-1, 1):
            for j in (-1, 1):
                vx, vy = kx + i * a * cm - j * a * sm, ky + i * a * sm + j * a * cm
                if not all(PC.vertex_ok(vx, vy, b) for b in pieces):
                    return False
        return True
    a0 = Fr(core.a)
    if not ok(a0):
        return core, False
    lo, hi = a0, Fr(1, 2)
    if ok(hi):
        return Core(kx, ky, tm, hi, core.box), True
    for _ in range(iters):
        mid = (lo + hi) / 2
        if ok(mid):
            lo = mid
        else:
            hi = mid
    a = Fr(int(lo * 2 ** 40), 2 ** 40)
    while a > a0 and not ok(a):
        a -= Fr(1, 2 ** 40)
    return Core(kx, ky, tm, max(a, a0), core.box), True


class PiecesHyp(Hyp):
    """the hypothesis whose cores are the union-box exact cores GROWN inside K'(role) of the pieces."""

    def __init__(self, roles):
        boxes = [r.bbox() for r in roles]
        super().__init__(boxes, [])
        self.a_stock = [float(c.a) for c in self.cores]
        ex = L.ExactHyp(boxes, [])
        self.a_union_exact = [float(c.a) for c in ex.cores]
        self.a_axis = [float(r.axis[2]) for r in roles]
        cores, self.grown_ok = [], []
        for r, c in zip(roles, ex.cores):
            g, okk = grow_core(c, r.pieces)
            cores.append(g)
            self.grown_ok.append(bool(okk))
        self.cores = cores
        self.a_pieces = [float(c.a) for c in cores]
        self.names = [r.name for r in roles]


def node_roles(cell, path):
    recs = R8.load_side(cell)
    r = recs.get(path)
    if r is None or not r.get("roles"):
        raise SystemExit("no ALIVE renorm181/183 record with roles for %s" % path)
    return r, R.roles_from_json(r["roles"])


def solve_pieces(tag, roles, budget, cap, warm, cert_time=150):
    rec = dict(node=tag, budget=budget, cap=cap, boxes=[b.to_json() for b in (r.bbox() for r in roles)],
               hypothesis="A183 pieces: the union-box exact core grown inside K'(role) (four corners vertex_ok on every piece)")
    t0 = time.time()
    H = PiecesHyp(roles)
    rec.update(roles=H.names, a_stock=H.a_stock, a_union_exact=H.a_union_exact, a_axis=H.a_axis, a_pieces=H.a_pieces,
               grown_ok=H.grown_ok,
               k_area={r.name: float(R.poly_area(r.core)) for r in roles})
    gate = []
    for i in range(len(H.cores)):
        for j in range(i + 1, len(H.cores)):
            ok, g = L.cores_disjoint_exact(H.cores[i], H.cores[j])
            gate.append(dict(i=i, j=j, disjoint=bool(ok), gap=float(g)))
    rec["cores_disjoint"] = all(g["disjoint"] for g in gate)
    rec["core_gate"] = gate
    if not rec["cores_disjoint"]:
        rec.update(verdict="UNDECIDED(core gate: exact cores not certifiably disjoint)", wall_s=round(time.time() - t0, 1))
        return rec
    try:
        s = solve_node(K.S0, H, budget, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900,
                       out=None, log=lambda *x: None, prune=0, prune_cols=3, col_stop_iter=10 ** 6,
                       col_stop_cov=1.002, max_cols_add=400, max_rows_add=2000, fine_slack=99.0,
                       alternate=True, fine=False)
    except Exception as e:                                       # noqa: BLE001
        rec.update(error=repr(e)[:300], wall_s=round(time.time() - t0, 1))
        return rec
    tau = s.get("tau")
    rec.update(tau=tau, eta=(tau - budget) if tau is not None else None, converged=bool(s.get("converged")),
               minmass=s.get("minmass"), maxcov=s.get("maxcov"), n_rows=s.get("n_rows"),
               kills=bool(tau is not None and tau < budget - 1e-6),
               kills_converged=bool(s.get("converged") and tau is not None and tau < budget - 1e-6))
    rec["window_transfer"] = ("by dilation (Lemma B.0 + K0-WIDEN: the boxes are stated on F = D_lambda P at s0; "
                              "obligation K0-O1 for the K0-FREE branch)")
    if rec["kills_converged"]:
        v, log = L.certify(s, H, budget, tag, rounds=1, time_limit=cert_time)
        rec["certified"], rec["cert_log"] = v, log
    rec["verdict"] = ("DEAD(LP)" if rec.get("certified") == "PASS"
                      else ("DEAD(LP, certificate pending)" if rec["kills_converged"]
                            else ("LP-dead unconverged (kill candidate)" if rec["kills"] else "ALIVE(LP)")))
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--node", required=True)
    ap.add_argument("--cap", type=float, default=240)
    ap.add_argument("--cert_time", type=float, default=150)
    a = ap.parse_args()
    r, roles = node_roles(a.cell, a.node)
    if not r["verdict"].startswith("ALIVE"):
        raise SystemExit("%s is %s" % (a.node, r["verdict"]))
    m = RS.memory_gate(tag="lp183 " + a.node)
    if m is None:
        raise SystemExit("memory gate not met")
    warm = L.load_warm(a.cell)
    tag = "lp183_%s_%s" % (a.cell, a.node.replace("/", "_"))
    rec = solve_pieces(tag, roles, 11 - len(roles), a.cap, warm, cert_time=a.cert_time)
    rec.update(cell=a.cell, setting=r.get("setting"), kept=r.get("kept"), when=time.strftime("%Y-%m-%d %H:%M"))
    out = os.path.join(K.RES, "lp183_%s.jsonl" % a.cell)
    with open(out, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
    print("%s b=%d cores a: stock %s | union-box exact %s | PIECES %s | tau=%s conv=%s %s %.0fs" % (
        a.node, rec["budget"], [round(x, 4) for x in rec["a_stock"]], [round(x, 4) for x in rec["a_union_exact"]],
        [round(x, 4) for x in rec["a_pieces"]], rec.get("tau"), rec.get("converged"), rec.get("verdict"), rec["wall_s"]), flush=True)


if __name__ == "__main__":
    main()
