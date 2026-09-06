"""Three-arm test at a 900 s cap, separating the levers.  OFFLINE, own copies, no deployment.

    arm A  plain          full tilt bin,     all warm rows
    arm B  trimmed        T5'' surviving bin, all warm rows
    arm C  trimmed+rows   T5'' surviving bin, all-poses row filter applied

Arm C is the one that needs a verifier clause change (see notes/verifier_v2_rowfilter.md); A and
B need none.  Running all three on the SAME nodes at the SAME cap is the only way to attribute a
kill to the right lever.

THE ALL-POSES ROW FILTER.  A warm row is a candidate placement: a unit square at (p, phi).  If it
overlaps EVERY pose (c, theta) in the conditioned box B, no packing can contain both it and the
conditioned square, so it cannot appear in a packing satisfying the node hypothesis and the LP
need not cover it.  Two unit squares are disjoint iff one of four axes separates them
(alpha in {phi, phi+90, theta, theta+90}), so "overlaps every pose" is certified by showing, for
each axis family, that the separation gap stays NEGATIVE over the whole box:

    max over (c, theta) in B of |(c - p) . n_alpha|  <  min over theta of (h_r(alpha) + h_Q(alpha))
    h(alpha) for a unit square at tilt psi = (|cos(psi - alpha)| + |sin(psi - alpha)|)/2

For the two fixed axes (alpha = phi, phi+90) the left side is a max over the box corners; for the
two moving axes (alpha = theta, theta+90) it is the same max-projection bound trim57 uses.  Only
the DROP side is certified, so a row that is not provably dominated is kept: the filter can only
shrink the LP, never weaken what it must cover... but see the spec -- that IS a clause change,
because the verifier must then check the matching weaker statement.

TC (Lemma TC, exact) is used as an O(1) pre-screen: if the centre distance already permits the
tilt difference, the row cannot be dominated and the exact test is skipped.
"""
import argparse, glob, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A57 = os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees"))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, os.path.join(A57, "code"))
from caselp import Box, Hyp, solve_node
from warm57 import merged_warm
import trim57
from pausegate import paused, reason

S_RAT = 969271.0 / 250000.0
DELTA = 1e-2
MARGIN = 1e-9


def _h(psi_deg, alpha_deg):
    r = math.radians(psi_deg - alpha_deg)
    return (abs(math.cos(r)) + abs(math.sin(r))) / 2.0


def _h_min(psi_lo, psi_hi, alpha_deg):
    """min over psi in [psi_lo, psi_hi] of h(psi, alpha); extrema at multiples of 90 from alpha."""
    best = min(_h(psi_lo, alpha_deg), _h(psi_hi, alpha_deg))
    k = math.ceil((psi_lo - alpha_deg) / 90.0)
    while alpha_deg + k * 90.0 <= psi_hi + 1e-12:
        best = min(best, _h(alpha_deg + k * 90.0, alpha_deg))
        k += 1
    return best


def dominates(b, px, py, phi):
    """True if the unit square at (px,py,phi) overlaps EVERY pose in box b (so the row is dead)."""
    corners = [(x - px, y - py) for x in (b.x0, b.x1) for y in (b.y0, b.y1)]
    # fixed axes: alpha = phi, phi+90
    for alpha in (phi, phi + 90.0):
        n = (math.cos(math.radians(alpha)), math.sin(math.radians(alpha)))
        lhs = max(abs(dx * n[0] + dy * n[1]) for dx, dy in corners)
        rhs = 0.5 + _h_min(b.th0, b.th1, alpha) - MARGIN
        if lhs >= rhs:
            return False
    # moving axes: alpha = theta, theta+90
    for off in (0.0, 90.0):
        lhs = max(trim57._max_proj(dx, dy, b.th0, b.th1, off) for dx, dy in corners)
        # h_Q on its own axis is 1/2; h_r depends on phi - theta, minimised over the bin
        rhs = 0.5 + min(_h(phi, b.th0 + off), _h(phi, b.th1 + off),
                        _h_min(b.th0 + off, b.th1 + off, phi)) - MARGIN
        if lhs >= rhs:
            return False
    return True


def dmax_of_c(c):
    lo, hi = 0.0, 45.0
    for _ in range(50):
        m = (lo + hi) / 2.0
        D = math.radians(m)
        if (1 + math.cos(D) + math.sin(D)) / 2.0 <= c:
            lo = m
        else:
            hi = m
    return lo


def filter_rows(rows, b):
    """-> (kept rows, dropped count, tc_prescreened count)."""
    kept, dropped, screened = [], 0, 0
    for (cx, cy, th) in rows:
        cmax = max(math.hypot(cx - x, cy - y) for x in (b.x0, b.x1) for y in (b.y0, b.y1))
        if cmax >= 1.20711:                     # TC pre-screen: cannot be dominated
            screened += 1
            kept.append((cx, cy, th))
            continue
        if dominates(b, cx, cy, th):
            dropped += 1
        else:
            kept.append((cx, cy, th))
    return kept, dropped, screened


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["A", "B", "C"], required=True)
    ap.add_argument("--cap", type=float, default=900.0)
    ap.add_argument("--n", type=int, default=32)
    a = ap.parse_args()
    cand = json.load(open(os.path.join(BASE, "results", "trim_lp_candidates.json")))
    cand = [c for c in cand if c.get("budget")][:a.n]
    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    hh = DELTA / math.sqrt(2.0)
    res = os.path.join(BASE, "results", f"arms96_{a.arm}.jsonl")
    done = set()
    if os.path.exists(res):
        for ln in open(res):
            try:
                done.add(json.loads(ln)["id"])
            except Exception:
                pass
    warm = {}
    print(f"arm {a.arm}: {len(cand)} nodes, cap {a.cap:.0f} s, {len(done)} done", flush=True)
    for c in cand:
        if c["id"] in done:
            continue
        if paused():
            print(f"pause sentinel ({reason()}); stopping with finished nodes recorded", flush=True)
            break
        nm = c["cls"]
        sl = [tuple(p) for p in slots_all[nm]]
        pins = [Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in sl]
        ob = c["box"]
        b = (Box(ob["x0"], ob["x1"], ob["y0"], ob["y1"], ob["th0"], ob["th1"]) if a.arm == "A"
             else Box(**{k: c["trimmed_box"][k] for k in ("x0", "x1", "y0", "y1", "th0", "th1")}))
        if nm not in warm:
            warm[nm] = merged_warm(nm, max_rows=30000)[0]
        W = warm[nm]
        rows = W["rows"]
        rec = dict(id=c["id"], cls=nm, arm=a.arm, cap=a.cap, level=c["level"],
                   surviving=c["surviving"], budget=c["budget"], warm_rows=len(rows))
        if a.arm == "C":
            t0 = time.time()
            rows, dropped, screened = filter_rows(rows, b)
            rec.update(rows_dropped=dropped, rows_kept=len(rows), tc_screened=screened,
                       filter_s=round(time.time() - t0, 1))
        t0 = time.time()
        try:
            s = solve_node(S_RAT, Hyp(pins + [b], []), c["budget"], sym_kind="C1",
                           warm=dict(atoms=list(W["atoms"]), rows=rows),
                           time_limit=a.cap, max_iter=900, out=None, log=lambda *x: None,
                           prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                           max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)
            tau = s.get("tau")
            rec.update(tau=tau, converged=s.get("converged"),
                       eta=(tau - c["budget"]) if tau is not None else None)
        except Exception as e:
            rec.update(error=repr(e)[:200])
        rec["wall_s"] = round(time.time() - t0, 1)
        with open(res, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"[{a.arm}] {c['id']:32s} eta={rec.get('eta')} conv={rec.get('converged')} "
              f"rows={rec.get('rows_kept', rec['warm_rows'])} {rec['wall_s']}s", flush=True)
    print(f"arm {a.arm} done", flush=True)


if __name__ == "__main__":
    main()
