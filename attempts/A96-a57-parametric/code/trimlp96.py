"""A96 offline: re-solve ALIVE nodes with the TRIMMED tilt bin, and measure the TC row filter.

Own copies only -- reads A57's code and warm start, writes only under A96.  The node hypothesis
is exactly tree57's `Hyp(pins + [box], [])`; the only change is that `box` carries the SURVIVING
tilt sub-interval instead of the full bin, which is a sub-box, so the certificate shape is the
ordinary one (see the report).

Also records, per node, the TC row screen: an LP row (a placement at centre p, tilt phi) whose
centre is within c of EVERY position in the box and whose tilt differs from EVERY tilt in the
(trimmed) bin by more than D(c) cannot be disjoint from any pose, so it is inadmissible and the
row may be dropped.  D(c) inverts Lemma TC, (1 + cos D + sin D)/2 <= c, which is EXACT: it is
min over directions alpha of (h1(alpha) + h2(alpha)) for two unit squares at tilt difference D,
attained at alpha = 0.
"""
import json, math, os, sys, time, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A57 = os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees"))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, os.path.join(A57, "code"))
from caselp import Box, Hyp, solve_node
from warm57 import merged_warm

S_RAT = 969271.0 / 250000.0
DELTA = 1e-2


def dmax_of_c(c):
    lo, hi = 0.0, 45.0
    for _ in range(60):
        m = (lo + hi) / 2.0
        D = math.radians(m)
        if (1 + math.cos(D) + math.sin(D)) / 2.0 <= c:
            lo = m
        else:
            hi = m
    return lo


def tc_screen(rows, b):
    """Rows TC alone proves inadmissible against box b (cheap closed-form pre-screen)."""
    out = []
    for (cx, cy, th) in rows:
        cmax = max(math.hypot(cx - x, cy - y) for x in (b.x0, b.x1) for y in (b.y0, b.y1))
        if cmax >= 1.20711:
            continue
        D = dmax_of_c(cmax)
        # tilt difference to EVERY tilt in the bin, mod 90
        worst = 91.0
        for t in (b.th0, b.th1):
            d = abs(th - t) % 90.0
            worst = min(worst, min(d, 90.0 - d))
        if worst > D:
            out.append((cx, cy, th))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--time-limit", type=float, default=240.0)
    a = ap.parse_args()
    cand = json.load(open(os.path.join(BASE, "results", "trim_lp_candidates.json")))
    cand = [c for c in cand if c.get("budget")][:a.n]
    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    hh = DELTA / math.sqrt(2.0)
    res_path = os.path.join(BASE, "results", "trimlp96.jsonl")
    done = set()
    if os.path.exists(res_path):
        for ln in open(res_path):
            try:
                done.add(json.loads(ln)["id"])
            except Exception:
                pass
    warm_cache = {}
    print(f"{len(cand)} candidates, {len(done)} done", flush=True)
    for c in cand:
        if c["id"] in done:
            continue
        nm = c["cls"]
        sl = [tuple(p) for p in slots_all[nm]]
        pins = [Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in sl]
        tb = c["trimmed_box"]
        b = Box(tb["x0"], tb["x1"], tb["y0"], tb["y1"], tb["th0"], tb["th1"])
        if nm not in warm_cache:
            warm_cache[nm] = merged_warm(nm, max_rows=30000)[0]
        W = warm_cache[nm]
        rec = dict(c, warm_rows=len(W["rows"]))
        rec["tc_rows_removed"] = len(tc_screen(W["rows"], b))
        t0 = time.time()
        try:
            r = solve_node(S_RAT, Hyp(pins + [b], []), c["budget"], sym_kind="C1",
                           warm=dict(atoms=list(W["atoms"]), rows=W["rows"]),
                           time_limit=a.time_limit, max_iter=900, out=None,
                           log=lambda *x: None, prune=0, prune_cols=3,
                           col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                           max_rows_add=2000, fine_slack=99.0, alternate=True)
            rec.update(tau_trimmed=r.get("tau"), converged=r.get("converged"),
                       eta_trimmed=(r.get("tau") - c["budget"]) if r.get("tau") is not None else None,
                       wall_s=round(time.time() - t0, 1))
        except Exception as e:
            rec.update(error=repr(e)[:200], wall_s=round(time.time() - t0, 1))
        with open(res_path, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"{c['id']:34s} surv={c['surviving']:.3f} tau_trim={rec.get('tau_trimmed')} "
              f"eta_trim={rec.get('eta_trimmed')} tc_rows={rec['tc_rows_removed']}/{rec['warm_rows']} "
              f"{rec['wall_s']}s", flush=True)
    print("trimlp96 done", flush=True)


if __name__ == "__main__":
    main()
