"""A89-O3 campaign: the shallow-corner root kills, in priority order, ONE LP at a time.

Monotonicity used to order the runs: SHALLOW(delta) is implied by SHALLOW(delta') for every
delta' <= delta, and the exempt pose set R_c(1-delta) SHRINKS as delta grows, so tau is
nondecreasing in delta.  A certified kill at delta therefore discharges every delta' <= delta:
run the LARGEST delta first and only fall back to a smaller one if it fails.
"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401
import o3run as R

PLAN = [
    # (name, pattern, delta, window, lp_time, cert_time, do_cert)
    # A89-O3 re-prioritisation (11:53): R1 (4-shallow, delta 0.3) PASSED -> discharges every
    # delta <= 0.3.  R2 (3-shallow, delta 0.3) FAILED at tau 10.046 (witness rounds 10.209).
    # tau is nondecreasing as corners are DROPPED from the pattern, so 2-shallow at delta 0.3 is
    # strictly harder than the 3-shallow run that just failed -- skip it.  tau is nondecreasing
    # in delta (the exempt box (0,(1-delta)/lambda_max)^2 shrinks as delta grows), so the useful
    # fallback is the SAME pattern at a SMALLER delta.
    ("R2_3shallow_d0.1",      ("BL", "BR", "TR"),        0.1,  True,  900, 300, True),
    ("R2_3shallow_d0.05",     ("BL", "BR", "TR"),        0.05, True,  900, 300, True),
    ("R3adj_2shallow_d0.05",  ("BL", "BR"),              0.05, True,  900, 300, True),
    ("R3diag_2shallow_d0.05", ("BL", "TR"),              0.05, True,  900, 300, True),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=200.0)
    ap.add_argument("--only", default=None)
    ap.add_argument("--nsteps", type=int, default=8)
    A = ap.parse_args()
    t_end = time.time() + 60 * A.minutes
    done = {}
    R.logline("=== O3 campaign start, wall budget %.0f min, %d runs planned"
              % (A.minutes, len(PLAN)))
    for (name, pat, delta, win, lpt, ct, cert) in PLAN:
        if A.only and A.only not in name:
            continue
        left = (t_end - time.time()) / 60.0
        if left <= 3:
            R.logline("=== budget exhausted (%.1f min left); stopping before %s" % (left, name))
            break
        # a certified kill at a larger delta discharges every smaller one: skip the fallback
        fam = name.split("_d")[0]
        if any(k.startswith(fam + "_d") and v == "PASS" for k, v in done.items()) and \
                name.endswith(("d0.1", "d0.05")):
            R.logline("=== skip %s (already PASS at a larger delta)" % name)
            continue
        R.logline("=== %s  (%.0f min left)" % (name, left))
        try:
            rec = R.run(pat, delta, window=win, nsteps=A.nsteps, lp_time=lpt, cert_time=ct,
                        jobs=1, do_cert=cert, deadline=t_end, tag=name)
            done[name] = rec.get("verdict")
        except Exception as e:
            R.logline("=== %s DEFERRED %s: %s" % (name, type(e).__name__, str(e)[:200]))
            done[name] = "DEFERRED(%s)" % type(e).__name__
    R.logline("=== O3 campaign done: " + json.dumps(done))


if __name__ == "__main__":
    main()
