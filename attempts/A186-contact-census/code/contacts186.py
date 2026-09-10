"""A186 step 1 -- CANDIDATE CONTACTS from the pieces.

For every pair of boxed roles: over every pair of pieces (A, B) the interval enclosure of the eight
signed separating-axis rows g_sigma (A116 gap_sel_iv on a111lib.IV, outward-rounded).  On (A, B):
  * gap_lo(A,B) := max_sigma inf g_sigma  -- a certified LOWER bound on the SAT gap of every pose pair
    of (A, B) (Lemma SAT: gap >= 0 iff disjoint; touching poses have gap 0);
  * gap_hi(A,B) := max_sigma sup g_sigma  -- an upper bound on the gap; < 0 means no disjoint pose pair
    in (A, B) at all (the multibox mutual clip should have removed such piece pairs).
The pair (i, j) is FAR (never in contact, [T] by Lemma SAT) iff min over piece pairs of gap_lo > 0;
otherwise it is a CANDIDATE EDGE, with the certified band [min gap_lo, min gap_hi].
Walls: per free role, the certified minimum of c.e - h(theta) (near walls) and s0 - c.e - h(theta)
(far walls) over the pieces; <= 0 (within 1e-9) means the role can touch that wall.
Exterior faces: the faces of the pieces not shared with an adjacent piece (the loadable box rows
of Theorem CC in docs/proofs/contact_census.md).

    python contacts186.py [--budget0]      # writes results/candidates186.json
"""
from __future__ import annotations
import argparse, itertools, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nodes186 as N                                          # noqa: E402
A, IV, S0 = N.A, N.IV, N.S0
SELS = A.SELS
FAR_EPS = 1e-9


def piece_iv(p):
    return (IV(p[0], p[1]), IV(p[2], p[3]), IV(p[4], p[5]))


def pair_band(Pi, Pj, pin_j=False):
    """(min gap_lo, min gap_hi, argmin piece pair) over the piece pairs of two roles."""
    glo, ghi, arg = math.inf, math.inf, None
    for a, pa in enumerate(Pi):
        Ba = piece_iv(pa)
        for b, pb in enumerate(Pj):
            Bb = piece_iv(pb)
            lo_best, hi_best = -math.inf, -math.inf
            for (o, k, e) in SELS:
                g = A.gap_sel_iv(Ba, Bb, o, k, e)
                lo_best = max(lo_best, g.lo); hi_best = max(hi_best, g.hi)
            if lo_best < glo:
                glo, arg = lo_best, (a, b)
            ghi = min(ghi, hi_best)
    return glo, ghi, arg


def wall_band(P):
    """certified minima of the four wall gaps over the pieces: (L, B, R, T)."""
    m = [math.inf] * 4
    for p in P:
        x, y, t = piece_iv(p)
        h = A.w_iv(t) * IV(0.5)
        for k, g in enumerate(((x - h), (y - h), (IV(S0) - x - h), (IV(S0) - y - h))):
            m[k] = min(m[k], g.lo)
    return m


def exterior_faces(P, tol=1e-9):
    """number of piece faces (6 per piece) not shared with a neighbouring piece."""
    n = 0
    for a, pa in enumerate(P):
        for f in range(6):
            ax = f // 2; hi = f % 2            # face on axis ax (0 x, 1 y, 2 t), low/high side
            coord = pa[2 * ax + hi]
            shared = False
            for b, pb in enumerate(P):
                if b == a:
                    continue
                if abs(pb[2 * ax + (1 - hi)] - coord) > tol:
                    continue
                ok = True
                for o in range(3):
                    if o == ax:
                        continue
                    if min(pa[2 * o + 1], pb[2 * o + 1]) - max(pa[2 * o], pb[2 * o]) <= tol:
                        ok = False; break
                if ok:
                    shared = True; break
            if not shared:
                n += 1
    return n


def analyse(rec):
    cap = rec["capture"]
    roles = rec["roles"]
    pieces = {r: [(p[0], p[1], p[2], p[3], math.radians(p[4]), math.radians(p[5])) for p in cap[r]["pieces"]]
              for r in roles}
    pairs, edges = {}, []
    for i, j in itertools.combinations(roles, 2):
        if i in N.PIN_SLOT and j in N.PIN_SLOT:
            continue
        glo, ghi, arg = pair_band(pieces[i], pieces[j])
        far = glo > FAR_EPS
        pairs["%s|%s" % (i, j)] = dict(gap_lo=glo, gap_hi=ghi, far=far, argmin=arg,
                                        n_piece_pairs=len(pieces[i]) * len(pieces[j]))
        if not far:
            edges.append((i, j))
    walls, faces = {}, {}
    for r in roles:
        if r in N.PIN_SLOT:
            continue
        m = wall_band(pieces[r])
        walls[r] = dict(L=m[0], B=m[1], R=m[2], T=m[3], touch=[w for w, v in zip("LBRT", m) if v <= FAR_EPS])
        faces[r] = exterior_faces(cap[r]["pieces"])
    return dict(label=rec["label"], short=N.short_label(rec["label"]), budget=11 - len(roles), roles=roles,
                pairs=pairs, edges=edges, n_edges=len(edges),
                n_free_edges=sum(1 for i, j in edges if i not in N.PIN_SLOT and j not in N.PIN_SLOT),
                walls=walls, faces=faces)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget0", action="store_true")
    args = ap.parse_args()
    recs = N.load_records()
    out = []
    for lab, r in sorted(recs.items(), key=lambda kv: (-len(kv[1]["roles"]), kv[0])):
        if args.budget0 and len(r["roles"]) < 11:
            continue
        t0 = time.time()
        a = analyse(r)
        a["seconds"] = round(time.time() - t0, 1)
        out.append(a)
        imp = [k for k, v in a["pairs"].items() if v["gap_hi"] < 0]
        print("%s  edges %d (free-free %d)  walls %s  faces %s  impossible-piece-pairs %s  %.1fs" %
              (a["short"], a["n_edges"], a["n_free_edges"],
               {k: "".join(v["touch"]) for k, v in a["walls"].items()}, a["faces"], imp, a["seconds"]))
        print("   edges:", " ".join("%s-%s(%.3f)" % (i, j, a["pairs"]["%s|%s" % (i, j)]["gap_lo"]) for i, j in a["edges"]))
    json.dump(out, open(os.path.join(N.RES, "candidates186%s.json" % ("_b0" if args.budget0 else "")), "w"), indent=1)


if __name__ == "__main__":
    main()
