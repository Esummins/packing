"""A131 T3 -- the LP effect of the pin-clip, in vitro.

Ten nodes: Y0036's four alive depth-2 children (D02/D03/D06/D07) plus six more ALIVE boxes with
a kept fraction < 0.5 at mixed levels.  Each is re-solved ONCE on its PIN-CLIPPED centre box over
its own tilt bin (nsub = 1, i.e. the exact intersection of the forbidden octagons over the whole
bin -- the tilt range is NOT narrowed, so the clip is the only variable).  The control is the
node's STORED record; per lemmas.md ("EMISSION IS NONDETERMINISTIC"), a re-emission is not a
reproduction, so nothing here re-emits the control and any kill is claimed only by REPLAYING a
certificate through the frozen verifier (certify.py -> verify_case.py).

Two-stage protocol, as A124/A96:
  stage 1  solve at a 240 s LP cap.  eta = tau - budget <= -1e-3  ->  certify at once.
  stage 2  otherwise (knife edge / unconverged) re-solve at 900 s, then certify if eta <= -1e-3.

This is NOT a shard launch.  It uses A124's scoped-sentinel mechanism (PAUSED.md v2 section 7a):
attempts/A57-shadow-trees/PAUSE is left in place and untouched -- it keeps every tree57 shard and
both deepen producers stopped -- and this driver watches its OWN sentinel,
attempts/A131-pin-clip/PAUSE, which is passed to pausegate.paused(base=...) explicitly.

    python code/lp131.py --shard 0/2 --cpu-hours 3

Writes only under attempts/A131-pin-clip: results/lp131.jsonl, results/nodes/, certs/, logs/.
"""
import argparse, ctypes, json, math, os, subprocess, sys, threading, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ATT, "A57-shadow-trees")
A96 = os.path.join(ATT, "A96-a57-parametric")
A53 = os.path.join(ATT, "A53-simple-strata")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(A96, "code"))
sys.path.insert(0, os.path.join(A57, "code"))

import pinclip
import recheck96                                    # read-only: S_RAT, DELTA, the queue helpers
from caselp import Box, Hyp, solve_node
from warm57 import merged_warm
from pausegate import paused, reason

RES = os.path.join(BASE, "results", "lp131.jsonl")
NODES = os.path.join(BASE, "results", "nodes")
CERTS = os.path.join(BASE, "certs")
SENTINEL = os.path.join(BASE, "PAUSE")             # OUR sentinel; A57's PAUSE is left alone
EXIT_WALL = 3
S_RAT_SIDE = "969271/250000"

# the ten in-vitro nodes: (id, tree key holding the stored record)
TARGETS = [
    ("k5_11_interior_Y0036_D02", "k5_11_interior_G1_D2"),
    ("k5_11_interior_Y0036_D03", "k5_11_interior_G1_D2"),
    ("k5_11_interior_Y0036_D06", "k5_11_interior_G1_D2"),
    ("k5_11_interior_Y0036_D07", "k5_11_interior_G1_D2"),
    ("k5_16_interior_Y0674", "k5_16_interior_G1"),
    ("k5_11_interior_Y0996", "k5_11_interior_G1"),
    ("k5_11_interior_Y1128", "k5_11_interior_G1"),
    ("k5_11_interior_Y0414_D06", "k5_11_interior_G1_D2"),
    ("k5_11_interior_Y0636_D04", "k5_11_interior_G1_D2"),
    ("k5_11_interior_Y0186_D00_D00", "k5_11_interior_G1_D2_D2"),
]


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


def append(path, rec):
    with open(path, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def stored_rows():
    """{id: row} over every A57 tree jsonl (the control records)."""
    import glob
    out = {}
    for f in sorted(glob.glob(os.path.join(A57, "results", "tree_k5_1*_interior_*.jsonl"))):
        for ln in open(f):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("box") and r["id"] not in out:
                out[r["id"]] = r
    return out


def done_ids():
    d = set()
    if os.path.exists(RES):
        for ln in open(RES):
            try:
                d.add(json.loads(ln)["id"])
            except Exception:
                pass
    return d


def certify(node_path, cert_out, cert_time, jobs):
    cmd = [sys.executable, os.path.join(A57, "code", "certify.py"), node_path,
           "--s_rat", S_RAT_SIDE, "--rounds", "2", "--jobs", str(jobs), "--depth", "56",
           "--time_limit", str(cert_time), "--out", cert_out, "--scale", "0",
           "--scale_cap", "1.03000", "--max_w", "64", "--loop_cols"]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, round(time.time() - t0, 1), (p.stdout + p.stderr)[-2500:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/2")
    ap.add_argument("--cap", type=float, default=240.0)
    ap.add_argument("--cap2", type=float, default=900.0)
    ap.add_argument("--cert-time", type=float, default=240.0)
    ap.add_argument("--node-wall", type=float, default=2400.0)
    ap.add_argument("--cpu-hours", type=float, default=3.0)
    ap.add_argument("--nsub", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args()
    si, sn = (int(x) for x in a.shard.split("/"))
    os.makedirs(NODES, exist_ok=True)
    os.makedirs(CERTS, exist_ok=True)

    bn = below_normal()
    print(f"[{time.strftime('%H:%M:%S')}] A131 lp131 shard {a.shard} pid {os.getpid()} "
          f"belownormal={bn}  A57 PAUSE present={os.path.exists(os.path.join(A57,'PAUSE'))} "
          f"(left untouched; this driver watches {SENTINEL})", flush=True)

    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    hh = recheck96.DELTA / math.sqrt(2.0)
    rows = stored_rows()
    done = done_ids()
    mine = [(nid, key) for i, (nid, key) in enumerate(TARGETS)
            if i % sn == si and nid not in done]
    print(f"[{time.strftime('%H:%M:%S')}] {len(mine)} nodes on this shard", flush=True)

    warm = {}
    spent = 0.0
    for nid, key in mine:
        if paused(base=BASE):
            print(f"A131 sentinel set ({reason(base=BASE)}); stopping cleanly", flush=True)
            break
        if spent >= a.cpu_hours * 3600.0:
            print(f"shard CPU cap reached ({spent/3600.0:.2f} h)", flush=True)
            break
        if nid in done_ids():
            continue
        r = rows.get(nid)
        if r is None:
            append(RES, dict(id=nid, error="no stored record"))
            continue
        nm = "k5_11" if nid.startswith("k5_11") else "k5_16"
        sl = [tuple(p) for p in slots_all[nm]]
        pins = [Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in sl]
        b0 = Box.from_json(r["box"])
        cl = pinclip.clip_node(b0, slots_all[nm], nsub=a.nsub)
        if cl["refused"] or cl["union_rect"] is None:
            append(RES, dict(id=nid, verdict="CLIP-EMPTY" if not cl["refused"] else "CLIP-REFUSED",
                             reason=cl["reason"], kept=cl["kept_vol"], wall_s=0.0))
            print(f"{nid:34s} {'CLIP-EMPTY' if not cl['refused'] else 'CLIP-REFUSED'}", flush=True)
            continue
        ux0, ux1, uy0, uy1 = cl["union_rect"]
        bc = Box(float(ux0), float(ux1), float(uy0), float(uy1), b0.th0, b0.th1)

        # stored control
        ctrl = dict(tau=r.get("tau"), eta=r.get("eta"), converged=r.get("converged"),
                    minmass=r.get("minmass"), cert=r.get("cert"), lp_seconds=r.get("lp_seconds"))
        sp = os.path.join(A57, "results", "tree", key, nid + ".json")
        if os.path.exists(sp):
            try:
                sres = json.load(open(sp))
                ctrl.update(minmass=sres.get("minmass"), maxcov=sres.get("maxcov"),
                            converged=sres.get("converged"), n_rows=sres.get("n_rows"),
                            support=len(sres.get("packing") or []))
            except Exception:
                pass

        if nm not in warm:
            warm[nm] = merged_warm(nm, max_rows=30000)[0]
        W = warm[nm]
        bud = r.get("budget") or 5
        rec = dict(id=nid, cls=nm, level=1 + nid.count("_D"), budget=bud, nsub=a.nsub,
                   box_before=b0.to_json(), box_after=bc.to_json(),
                   kept_vol=round(cl["kept_vol"], 6), kept_union=round(cl["kept_union"], 6),
                   control=ctrl, shard=a.shard)

        t0 = time.time()
        stop = threading.Event()

        def guard(node=nid):
            if stop.wait(a.node_wall):
                return
            try:
                append(RES, dict(id=node, verdict="WALL-CAP", node_wall=a.node_wall,
                                 wall_s=round(time.time() - t0, 1),
                                 comment="hard wall hit; NOT a verdict"))
                sys.stderr.write(f"WALL-CAP {node}; exiting {EXIT_WALL}\n")
                sys.stderr.flush()
            finally:
                os._exit(EXIT_WALL)

        threading.Thread(target=guard, daemon=True).start()

        stages = []
        node_path = os.path.join(NODES, nid + "_clip.json")
        cert_path = os.path.join(CERTS, nid + "_clip.json")
        killed = False
        for stage, cap in ((1, a.cap), (2, a.cap2)):
            print(f"[{time.strftime('%H:%M:%S')}] {nid} stage {stage} cap {cap:.0f}s "
                  f"kept={cl['kept_vol']:.4f}", flush=True)
            ts = time.time()
            try:
                s = solve_node(recheck96.S_RAT, Hyp(pins + [bc], []), bud, sym_kind="C1",
                               warm=dict(atoms=list(W["atoms"]), rows=W["rows"]),
                               time_limit=cap, max_iter=900, out=None, log=lambda *x: None,
                               prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                               max_cols_add=400, max_rows_add=2000, fine_slack=99.0,
                               alternate=True)
            except Exception as e:
                stages.append(dict(stage=stage, cap=cap, error=repr(e)[:200],
                                   seconds=round(time.time() - ts, 1)))
                break
            tau = s.get("tau")
            eta = (tau - bud) if tau is not None else None
            st = dict(stage=stage, cap=cap, tau=tau, eta=eta, converged=s.get("converged"),
                      minmass=s.get("minmass"), maxcov=s.get("maxcov"),
                      support=len(s.get("packing") or []), n_rows=s.get("n_rows"),
                      seconds=round(time.time() - ts, 1))
            if eta is not None and eta <= -1e-3:
                s["parent"] = nm
                s["child_id"] = nid
                json.dump(s, open(node_path, "w"))
                rc, cs, tail = certify(node_path, cert_path, a.cert_time, a.jobs)
                st.update(cert=("PASS" if rc == 0 else f"FAIL(rc={rc})"), cert_seconds=cs)
                if rc == 0:
                    open(cert_path + ".PASS", "w").write("ok")
                    killed = True
                st["cert_tail"] = tail[-600:]
            stages.append(st)
            if killed or (eta is not None and eta <= -1e-3):
                break
            if stage == 1:
                print(f"[{time.strftime('%H:%M:%S')}] {nid} knife edge "
                      f"(eta={eta}); going to stage 2", flush=True)
        rec["stages"] = stages
        rec["killed"] = killed
        rec["wall_s"] = round(time.time() - t0, 1)
        stop.set()
        spent += rec["wall_s"]
        append(RES, rec)
        last = stages[-1] if stages else {}
        print(f"[{time.strftime('%H:%M:%S')}] {nid:30s} kept={cl['kept_vol']:.4f} "
              f"eta {ctrl.get('eta')} -> {last.get('eta')} conv={last.get('converged')} "
              f"cert={last.get('cert')} {rec['wall_s']}s [{spent/3600.0:.2f} CPU-h]", flush=True)
    print("lp131 shard done", flush=True)


if __name__ == "__main__":
    main()
