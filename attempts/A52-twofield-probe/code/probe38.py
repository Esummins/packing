#!/usr/bin/env python3
"""A38 depth probe: 8-way refinement of a chosen parent list, with CERTIFICATION IN THE LOOP.

Per child:
  1. W1/W2 node-kill test (node38.w1_node_scan, ~ms, no LP)          -> status 'w1kill'
  2. else the A27 case-LP through node38.solve_a38_node (W1 row filter OFF per design Amendment 1,
     the node-kill test above is the strictly-stronger form)
  3. an LP kill (dead(T1)) is IMMEDIATELY put through the exact certificate loop (certify.py, the
     same verify-with-witness-feedback used for the root and the l1 sample) under a hard wall cap:
        PASS  -> 'dead(certified)'
        else  -> 'dead(LP-uncertified)'
     (the 2/8 float-hole failures in the l1 sample are why an uncertified kill does not count)

    python probe38.py --parents 61,65,74,95,100 --strata alive,... --outdir ../results/l2_nodes \
                      --out ../results/l2_a38.json --time_limit 180 --cert_cap 120 --workers 6
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import traceback

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results")
S_RAT = "969271/250000"
S0F = 3.877084


def refine8(b):
    """2x2x2 split of a box dict {x0,x1,y0,y1,th0,th1}."""
    xm = 0.5 * (b["x0"] + b["x1"]); ym = 0.5 * (b["y0"] + b["y1"]); tm = 0.5 * (b["th0"] + b["th1"])
    out = []
    for ix, (x0, x1) in enumerate(((b["x0"], xm), (xm, b["x1"]))):
        for iy, (y0, y1) in enumerate(((b["y0"], ym), (ym, b["y1"]))):
            for it, (t0, t1) in enumerate(((b["th0"], tm), (tm, b["th1"]))):
                out.append((dict(x0=x0, x1=x1, y0=y0, y1=y1, th0=t0, th1=t1), (ix, iy, it)))
    return out


def run_certify(node_json, out_cert, budget, cap, jobs=2, depth=48, rounds=2, eps_geo=0.003):
    tl = max(20.0, cap / 3.0)
    cmd = [sys.executable, os.path.join(HERE, "certify.py"), node_json, "--s_rat", S_RAT,
           "--scale", "0", "--rounds", str(rounds), "--jobs", str(jobs), "--depth", str(depth),
           "--time_limit", str(tl), "--eps_geo", str(eps_geo), "--out", out_cert,
           "--max_cols", "300", "--resolve_time", str(tl)]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=cap)
        rc, txt, to = p.returncode, p.stdout + p.stderr, False
    except subprocess.TimeoutExpired as e:
        rc, to = 124, True
        txt = ((e.stdout or b"").decode("utf8", "replace") if isinstance(e.stdout, bytes)
               else (e.stdout or "")) + "\n[TIMEOUT at %.0f s]" % cap
    try:
        with open(out_cert.replace(".json", ".certify.log"), "w") as f:
            f.write(txt)
    except Exception:
        pass
    return dict(rc=rc, timeout=to, result=("PASS" if rc == 0 else "FAIL"),
                seconds=time.time() - t0,
                tail=[l for l in txt.splitlines()
                      if l.startswith(("PASS", "FAIL", "CERTIFIED", "NOT certified", "[round",
                                       "certificate total"))][-6:])


def _work(args):
    (cid, parent, stratum, bjson, split, budget, tl, eps_geo, cert_cap, deadline,
     outdir, logdir) = args
    t0 = time.time()
    rec = dict(cid=cid, parent=parent, stratum=stratum, split=list(split), box=bjson,
               budget=budget)
    rp = os.path.join(outdir, "%s.rec.json" % cid)
    try:
        if time.time() >= deadline:
            rec.update(status="notrun", seconds_lp=0.0, seconds_cert=0.0)
            json.dump(rec, open(rp, "w"), indent=1); return rec
        import node38
        from caselp import Box
        B = Box.from_json(bjson)
        mk = node38.mask()
        verdict, det = node38.w1_node_scan([B], mk)
        rec["c_core"] = det["core_mlow"][0]
        rec["thr_cert"] = det["thr_cert"]; rec["thr_node"] = det.get("thr_node")
        rec["w1_verdict"] = verdict
        if verdict is not None:
            rec.update(status="w1kill", w1kind=verdict, kill_thr=det.get("kill_thr"),
                       seconds_lp=time.time() - t0, seconds_cert=0.0)
            json.dump(rec, open(rp, "w"), indent=1); return rec

        out = os.path.join(outdir, "%s.json" % cid)
        lg = os.path.join(logdir, "%s.log" % cid)

        def log(*a):
            with open(lg, "a") as f:
                f.write(" ".join(str(x) for x in a) + "\n")

        log("### A38 probe %s parent=%s stratum=%s %r budget=%d tl=%g c_core=%.9f"
            % (cid, parent, stratum, B, budget, tl, rec["c_core"]))
        tl_eff = min(tl, max(10.0, deadline - time.time()))
        r = node38.solve_a38_node(S0F, [B], budget, w1=False, w2=False, time_limit=tl_eff,
                                  out=out, log=log, eps_geo=eps_geo, sym_kind="C1",
                                  theta_box="0-90",
                                  checkpoint=out.replace(".json", "_state.json"))
        t_lp = time.time() - t0
        st = r["status"]; maxcov = r.get("maxcov")
        if st == "dead(T1)":
            status = "dead(LP-uncertified)"
        elif st == "alive" and maxcov is not None and maxcov <= 1 + 1e-3:
            status = "alive(LP)"
        else:
            status = "undecided"
        rec.update(status=status, lp_status=st, tau=r["tau"], slack=r["slack"],
                   converged=r["converged"], minmass=r["minmass"], maxcov=maxcov,
                   rows=r["n_rows"], orbits=r["n_orbits"], iters=r.get("iters"),
                   last_added_rows=r.get("last_added_rows"), seconds_lp=t_lp, seconds_cert=0.0)
        json.dump(rec, open(rp, "w"), indent=1)

        # -------------------------------------------------- certification in the loop
        if st == "dead(T1)" and cert_cap > 0:
            cert = os.path.join(outdir, "%s.cert.json" % cid)
            cr = run_certify(out, cert, budget, cert_cap)
            rec["cert"] = cr
            rec["seconds_cert"] = cr["seconds"]
            rec["status"] = "dead(certified)" if cr["result"] == "PASS" else "dead(LP-uncertified)"
            log("CERT " + json.dumps(cr))
        rec["seconds"] = time.time() - t0
        json.dump(rec, open(rp, "w"), indent=1)
        return rec
    except Exception:
        rec.update(status="error", error=traceback.format_exc()[-1500:],
                   seconds_lp=time.time() - t0, seconds_cert=0.0)
        try:
            json.dump(rec, open(rp, "w"), indent=1)
        except Exception:
            pass
        return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parentfile", required=True,
                    help='json list of {"id","stratum","box":{x0..th1},"budget"}')
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--logdir", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--time_limit", type=float, default=180.0)
    ap.add_argument("--cert_cap", type=float, default=120.0)
    ap.add_argument("--eps_geo", type=float, default=1e-4)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--wall", type=float, default=3600.0, help="hard wall seconds for this phase")
    ap.add_argument("--tag", default="l2")
    ap.add_argument("--resume", type=int, default=1)
    a = ap.parse_args()
    outdir = os.path.abspath(a.outdir); os.makedirs(outdir, exist_ok=True)
    logdir = os.path.abspath(a.logdir or os.path.join(outdir, "logs")); os.makedirs(logdir, exist_ok=True)
    parents = json.load(open(a.parentfile))
    t_start = time.time(); deadline = t_start + a.wall

    # jobs, INTERLEAVED by parent (round-robin over the 8 splits) so that a wall cut-off
    # truncates every stratum equally instead of starving the last parents in the list.
    per_parent = []
    done = []
    for p in parents:
        L = []
        for (cb, split) in refine8(p["box"]):
            cid = "%s_p%s_%d%d%d" % (a.tag, p["id"], *split)
            rp = os.path.join(outdir, "%s.rec.json" % cid)
            if a.resume and os.path.exists(rp):
                try:
                    d = json.load(open(rp))
                    if d.get("status") not in (None, "notrun", "error"):
                        done.append(d); continue
                except Exception:
                    pass
            L.append((cid, p["id"], p["stratum"], cb, split, p.get("budget", 10),
                      a.time_limit, a.eps_geo, a.cert_cap, deadline, outdir, logdir))
        per_parent.append(L)
    jobs = []
    for r in range(8):
        for L in per_parent:
            if r < len(L):
                jobs.append(L[r])
    print("A38 probe %s: %d parents -> %d children (%d resumed, %d to run), workers=%d tl=%g "
          "cert_cap=%g wall=%gs" % (a.tag, len(parents), len(jobs) + len(done), len(done),
                                    len(jobs), a.workers, a.time_limit, a.cert_cap, a.wall),
          flush=True)

    recs = list(done)
    with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(_work, j) for j in jobs]
        for fu in cf.as_completed(futs):
            r = fu.result(); recs.append(r)
            print("  %-22s p=%-4s %-10s %-22s tau=%s cc=%.4f lp=%.0fs cert=%.0fs  [%d/%d %.0fs]"
                  % (r["cid"], r["parent"], r["stratum"], r["status"],
                     ("%.4f" % r["tau"]) if r.get("tau") is not None else "-",
                     r.get("c_core", float("nan")), r.get("seconds_lp", 0.0),
                     r.get("seconds_cert", 0.0), len(recs), len(jobs) + len(done),
                     time.time() - t_start), flush=True)
    recs.sort(key=lambda r: r["cid"])
    doc = dict(format="A38-depth-probe-v1", tag=a.tag, when=time.strftime("%Y-%m-%dT%H:%M:%S"),
               s=S_RAT, time_limit=a.time_limit, cert_cap=a.cert_cap, eps_geo=a.eps_geo,
               workers=a.workers, w1_row_filter="OFF (design Amendment 1)",
               parents=parents, n_children=len(recs), records=recs,
               seconds=time.time() - t_start)
    json.dump(doc, open(a.out, "w"), indent=1)
    print("->", a.out, "in %.0f s" % (time.time() - t_start), flush=True)


if __name__ == "__main__":
    main()
