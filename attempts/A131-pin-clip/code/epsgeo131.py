"""A131 follow-up -- the T14 eps_geo retry on the three T3 nodes that reached eta <= -0.5 but
whose certificate FAILed.

WHICH LADDER, AND WHY NOT THE OTHER ONE.  A57 has two ladders:
  * the ROW-SHRINK (eps_geo) ladder -- `certify.py --eps_geo <m>`, a plain CLI with `--out`, which
    is exactly what `tree57.run_eps_geo` shells out to on every FAIL.  Sound because shrinking
    rows only RAISES tau (the LP gets harder) while the arbiter `verify_case.py` is unchanged.
    Margins from `tree57.eps_geo_margins`: all three nodes have scale ceiling >= 1.05, so (0.002,
    0.004).  THIS is what runs here.
  * the EPS_CORE ladder -- `attempts/A57-shadow-trees/code/epsladder.py`.  SKIPPED: it hardcodes
    its certificate directory to A57's `certs/epsladder` and writes `results/epsladder_<id>.json`
    into A57's tree, with no flag to redirect either, so running it would write A57 state.  Its
    mechanism (set `caselp.EPS_CORE`, re-solve, certify) is a library call, but the program is not
    one, and A57's state stays untouched.

Writes only under attempts/A131-pin-clip.  <= 1 CPU-h, 2 BelowNormal BLAS-pinned processes.

    python code/epsgeo131.py --shard 0/2 --cpu-hours 0.5
"""
import argparse, ctypes, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A57 = os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees"))
RES = os.path.join(BASE, "results", "epsgeo131.jsonl")
CERTS = os.path.join(BASE, "certs", "epsgeo")
S_RAT_SIDE = "969271/250000"

# the three T3 nodes with eta <= -1e-3 whose certificate FAILed
TARGETS = ["k5_11_interior_Y0036_D03", "k5_11_interior_Y0996", "k5_11_interior_Y0636_D04"]
MARGINS = (0.002, 0.004)          # tree57.eps_geo_margins: ceiling >= 1.05 on all three


def below_normal():
    try:
        k32 = ctypes.windll.kernel32
        k32.GetCurrentProcess.restype = ctypes.c_void_p
        k32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        k32.GetPriorityClass.argtypes = [ctypes.c_void_p]
        h = k32.GetCurrentProcess()
        k32.SetPriorityClass(h, 0x00004000)
        return k32.GetPriorityClass(h) == 0x00004000
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/2")
    ap.add_argument("--time-limit", type=float, default=240.0)
    ap.add_argument("--cpu-hours", type=float, default=0.5)
    a = ap.parse_args()
    si, sn = (int(x) for x in a.shard.split("/"))
    os.makedirs(CERTS, exist_ok=True)
    bn = below_normal()
    print(f"[{time.strftime('%H:%M:%S')}] epsgeo131 shard {a.shard} pid {os.getpid()} "
          f"belownormal={bn}", flush=True)
    done = set()
    if os.path.exists(RES):
        for ln in open(RES):
            try:
                done.add(json.loads(ln)["id"])
            except Exception:
                pass
    spent = 0.0
    for i, nid in enumerate(TARGETS):
        if i % sn != si or nid in done:
            continue
        if spent >= a.cpu_hours * 3600.0:
            print("shard CPU cap reached", flush=True)
            break
        node = os.path.join(BASE, "results", "nodes", nid + "_clip.json")
        res0 = json.load(open(node))
        ceil = res0["budget"] / res0["tau"] if res0["tau"] > 0 else 0.0
        rec = dict(id=nid, node=os.path.relpath(node, BASE).replace("\\", "/"),
                   tau=res0["tau"], budget=res0["budget"], scale_ceiling=ceil,
                   margins=list(MARGINS), steps=[], cert="FAIL(eps_geo retries exhausted)")
        t0 = time.time()
        for m in MARGINS:
            out = os.path.join(CERTS, f"{nid}_clip_epsgeo{m:g}.json")
            cmd = [sys.executable, os.path.join(A57, "code", "certify.py"), node,
                   "--s_rat", S_RAT_SIDE, "--eps_geo", f"{m:g}", "--rounds", "1", "--jobs", "1",
                   "--depth", "56", "--time_limit", str(a.time_limit),
                   "--resolve_time", str(a.time_limit), "--out", out, "--scale", "0",
                   "--scale_cap", "1.03000", "--max_w", "32", "--loop_cols"]
            t1 = time.time()
            p = subprocess.run(cmd, capture_output=True, text=True)
            tail = [l.strip() for l in (p.stdout + p.stderr).splitlines()
                    if l.strip().startswith(("worst", "[round", "PASS", "FAIL", "NOT"))][-4:]
            step = dict(eps_geo=m, rc=p.returncode, seconds=round(time.time() - t1, 1), tail=tail)
            rec["steps"].append(step)
            print(f"[{time.strftime('%H:%M:%S')}] {nid} eps_geo={m:g} rc={p.returncode} "
                  f"{step['seconds']}s :: {tail[-1] if tail else ''}", flush=True)
            if p.returncode == 0:
                open(out + ".PASS", "w").write("ok")
                rec.update(cert="PASS", cert_path=os.path.relpath(out, BASE).replace("\\", "/"),
                           eps_geo_used=m)
                break
        rec["wall_s"] = round(time.time() - t0, 1)
        spent += rec["wall_s"]
        with open(RES, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
    print("epsgeo131 shard done", flush=True)


if __name__ == "__main__":
    main()
