"""A96 step 3c: turn a partial window certificate into a full one by RE-VERIFYING the same
certificate on its own uncovered sub-windows.

FINDING (endpoint96.py, results/endpoint96.jsonl).  The "recurring slivers"

    A [191/50, 977934271/256000000]            B [979732417/256000000, 7654271/2000000]

are NOT node hardness and NOT a boundary degeneracy of the geometry: they are an s-RESOLUTION
artifact of running one global pass.  verify_param splits the widest axis of a 4-D cell, so on
the full window W = [191/50, s0] the (t, cx, cy) depth budget is exhausted before the s-axis is
cut finely enough at those two places.  Restricting the window to the sliver makes every s-cell
there ~1000x finer from the first split, and the SAME certificate then passes:

    k5_11_interior_Y0192  sliver A   PASS in 2.4 s      (full-window run: FAIL, 99.90% covered)
    k5_11_interior_Y0271  sliver B   PASS in 0.5 s      (full-window run: FAIL, 99.90% covered)
    k5_11_interior_Y0067  slivers A+B PASS in 1.0-1.5 s (full-window run: FAIL, 99.80% covered)

So the repair costs SECONDS and needs no new LP, no new certificate, and nothing new to audit:
it is the frozen verifier re-run on a narrower window, and the results compose as A86 T4's
WindowRows disjunction (a finite union of closed sub-windows whose union is W).

This script does that generally: for every FAIL node it reads the EXACT s-intervals of the
witness cells out of the witness file (not the float coverage summary), merges them, and
re-verifies the certificate on each one, bisecting a sub-window that still fails, down to
--max-bisect.  A node all of whose gaps close is upgraded to FULL WINDOW.

Writes results/resolve96.jsonl (one record per node, with the exact row list for Lean).
"""
import argparse, json, os, subprocess, sys, time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
VP = os.path.join(HERE, "verify_param.py")
OUT = os.path.join(BASE, "results")
A95 = os.path.abspath(os.path.join(BASE, "..", "A95-a57-shortcuts", "results"))
SLO, SHI = F(191, 50), F(969271, 250000)


def exact_gaps(witfile):
    """The union of the witness cells' EXACT s-intervals, merged.  These are the only parts of
    the window the run did not discharge."""
    W = json.load(open(witfile))["witnesses"]
    iv = sorted((F(w["box"]["s"][0]), F(w["box"]["s"][1])) for w in W if "box" in w)
    merged = []
    for a, b in iv:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return merged


def run(cert, lo, hi, depth, out_tag, env, cap):
    rp = os.path.join(BASE, "certs", "resolve", out_tag + ".report.json")
    wf = os.path.join(BASE, "certs", "resolve", out_tag + ".witnesses.json")
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    cmd = [sys.executable, VP, cert, "--slo", str(lo), "--shi", str(hi), "--depth", str(depth),
           "--jobs", "1", "--strict-margin", "0", "--report", rp, "--witness-file", wf,
           "--max-witnesses", "400", "--max-witnesses-per-box", "1", "--quiet"]
    t0 = time.time()
    try:
        rc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=cap).returncode
    except subprocess.TimeoutExpired:
        rc = None
    return (("TIMEOUT" if rc is None else
             {0: "PASS", 1: "FAIL", 2: "MALFORMED"}.get(rc, f"rc={rc}")),
            round(time.time() - t0, 1), wf)


def resolve(cert, gaps, depth, maxbis, env, cap, tag):
    """Returns (rows, residual, wall).  rows = closed sub-windows certified here."""
    rows, residual, wall, n = [], [], 0.0, 0
    stack = [(lo, hi, 0) for lo, hi in gaps]
    while stack:
        lo, hi, d = stack.pop(0)
        n += 1
        v, w, _ = run(cert, lo, hi, depth, f"{tag}.g{n}", env, cap)
        wall += w
        if v == "PASS":
            rows.append([str(lo), str(hi), float(lo), float(hi), w])
        elif d < maxbis:
            m = (lo + hi) / 2
            stack.append((lo, m, d + 1))
            stack.append((m, hi, d + 1))
        else:
            residual.append([str(lo), str(hi), float(lo), float(hi), v])
    return rows, residual, round(wall, 1)


def sources():
    """(node, cls, cert path, witness file, full-window wall) for every completed FAIL."""
    out = []
    for src, pdir, cls_default in (
            (os.path.join(A95, "t1_param.jsonl"), os.path.join(A95, "param"), "k5_11_G1"),
            (os.path.join(OUT, "param96.jsonl"), None, None),
            # the level-2 batch writes its param certs into the same certs/param/<cls> tree, so
            # only the results file differs; level-2 partials resolve by the identical mechanism
            (os.path.join(OUT, "param96_level2.jsonl"), None, None)):
        if not os.path.exists(src):
            continue
        for ln in open(src):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("verdict") != "FAIL" or not r.get("search_complete"):
                continue
            cls = r.get("cls", cls_default)
            d = pdir or os.path.join(BASE, "certs", "param", cls)
            pj = os.path.join(d, r["id"] + ".param.json")
            wf = os.path.join(d, r["id"] + ".witnesses.json")
            if os.path.exists(pj) and os.path.exists(wf):
                out.append(dict(id=r["id"], cls=cls, cert=pj, wit=wf,
                                full_window_wall_s=r.get("param_wall_s"),
                                fixed_wall_s=r.get("fixed_wall_s"),
                                covered_frac_before=r.get("coverage", {}).get("certified_frac")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--cap", type=float, default=180.0)
    ap.add_argument("--max-bisect", type=int, default=3)
    a = ap.parse_args()
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    res = os.path.join(OUT, "resolve96.jsonl")
    done = set()
    if os.path.exists(res):
        for ln in open(res):
            try:
                done.add(json.loads(ln)["id"])
            except Exception:
                pass
    S = [s for s in sources() if s["id"] not in done]
    # Fewest gaps first.  A node whose only misses are the two recurring slivers closes in
    # seconds; a node with a long witness list (k5_11_interior_Y0540 has six) can absorb the
    # whole budget in bisection, and it must not block the cheap ones.
    for s in S:
        s["_gaps"] = exact_gaps(s["wit"])
    S.sort(key=lambda s: (len(s["_gaps"]), s["id"]))
    print(f"{len(S)} FAIL node(s) to resolve; gap counts "
          f"{[len(s['_gaps']) for s in S]}", flush=True)
    for s in S:
        gaps = s.pop("_gaps")
        rows, residual, wall = resolve(s["cert"], gaps, a.depth, a.max_bisect, env, a.cap, s["id"])
        gw = sum(float(b) - float(a_) for a_, b in gaps)
        cw = sum(r[3] - r[2] for r in rows)
        rec = dict(s, gaps=[[str(x), str(y)] for x, y in gaps], gap_width=gw,
                   rows=rows, residual=residual, resolve_wall_s=wall,
                   closed=not residual,
                   covered_frac_after=round(min(1.0, (s["covered_frac_before"] or 0)
                                                + cw / float(SHI - SLO)), 9))
        with open(res, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"{s['cls']:9s} {s['id']:26s} gaps={len(gaps)} width={gw:.3e} "
              f"-> rows={len(rows)} residual={len(residual)} {wall:7.1f}s "
              f"{'CLOSED' if not residual else 'PARTIAL'}", flush=True)
    print("resolve96 done", flush=True)


if __name__ == "__main__":
    main()
