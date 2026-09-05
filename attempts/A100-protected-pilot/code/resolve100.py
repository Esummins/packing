"""A100 step 3: A96's RESOLVER, pointed at this attempt's parametric ledger.

Identical logic to attempts/A96-a57-parametric/code/resolve96.py (which see for the finding that
the recurring window slivers are an s-resolution artefact, not node hardness): for every COMPLETED
FAIL of the parametric pass, read the EXACT s-intervals of the witness cells, merge them, and
re-run the SAME frozen certificate on each gap, bisecting a gap that still fails down to
--max-bisect.  A node all of whose gaps close is upgraded to FULL WINDOW.

Only the source of the FAIL list differs (results/param100.jsonl, and certs/param/<cls>/).
"""
import argparse, json, os, subprocess, sys, time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
VP = os.path.join(HERE, "verify_param.py")
OUT = os.path.join(BASE, "results")
SLO, SHI = F(191, 50), F(969271, 250000)


def exact_gaps(witfile):
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
             {0: "PASS", 1: "FAIL", 2: "MALFORMED"}.get(rc, "rc=%s" % rc)),
            round(time.time() - t0, 1), wf)


def resolve(cert, gaps, depth, maxbis, env, cap, tag):
    rows, residual, wall, n = [], [], 0.0, 0
    stack = [(lo, hi, 0) for lo, hi in gaps]
    while stack:
        lo, hi, d = stack.pop(0)
        n += 1
        v, w, _ = run(cert, lo, hi, depth, "%s.g%d" % (tag, n), env, cap)
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


def sources(src):
    out = []
    if not os.path.exists(src):
        return out
    for ln in open(src):
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if r.get("verdict") != "FAIL" or not r.get("search_complete"):
            continue
        cls = r["cls"]
        d = os.path.join(BASE, "certs", "param", cls)
        pj = os.path.join(d, r["id"] + ".param.json")
        wf = os.path.join(d, r["id"] + ".witnesses.json")
        if os.path.exists(pj) and os.path.exists(wf):
            out.append(dict(id=r["id"], cls=cls, cert=pj, wit=wf,
                            full_window_wall_s=r.get("param_wall_s"),
                            fixed_wall_s=r.get("fixed_wall_s"),
                            covered_frac_before=(r.get("coverage") or {}).get("certified_frac")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--cap", type=float, default=180.0)
    ap.add_argument("--max-bisect", type=int, default=3)
    ap.add_argument("--src", default=os.path.join(OUT, "param100.jsonl"))
    ap.add_argument("--out", default=os.path.join(OUT, "resolve100.jsonl"))
    a = ap.parse_args()
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    # A100 fix: A96's resolve96.py keys `done` on the bare node id, so a node whose id also occurs
    # in ANOTHER class is silently skipped.  A100 runs two classes whose cover tags collide by
    # construction (both are c0_Y####), and k4_11's c0_Y1119 was dropped this way.  Key on
    # (cls, id).  Worth porting back to A96 before it runs a second class.
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out):
            try:
                r = json.loads(ln)
                done.add((r.get("cls"), r["id"]))
            except Exception:
                pass
    S = [s for s in sources(a.src) if (s["cls"], s["id"]) not in done]
    for s in S:
        s["_gaps"] = exact_gaps(s["wit"])
    S.sort(key=lambda s: (len(s["_gaps"]), s["id"]))
    print("%d FAIL node(s) to resolve; gap counts %s"
          % (len(S), [len(s["_gaps"]) for s in S]), flush=True)
    for s in S:
        gaps = s.pop("_gaps")
        rows, residual, wall = resolve(s["cert"], gaps, a.depth, a.max_bisect, env, a.cap, s["id"])
        gw = sum(float(b) - float(a_) for a_, b in gaps)
        cw = sum(r[3] - r[2] for r in rows)
        rec = dict(s, gaps=[[str(x), str(y)] for x, y in gaps], gap_width=gw,
                   rows=rows, residual=residual, resolve_wall_s=wall, closed=not residual,
                   covered_frac_after=round(min(1.0, (s["covered_frac_before"] or 0)
                                                + cw / float(SHI - SLO)), 9))
        with open(a.out, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print("%-8s %-22s gaps=%d width=%.3e -> rows=%d residual=%d %7.1fs %s"
              % (s["cls"], s["id"], len(gaps), gw, len(rows), len(residual), wall,
                 "CLOSED" if not residual else "PARTIAL"), flush=True)
    print("resolve100 done", flush=True)


if __name__ == "__main__":
    main()
