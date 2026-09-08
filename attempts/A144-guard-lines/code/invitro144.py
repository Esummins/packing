"""A144 T2 -- the IN-VITRO node LP with the guard-line columns added.

Two arms per node, identical settings, identical warm start, identical (EXACT, A135-certified)
cores -- the ONLY difference is the guard columns:

    arm "base"   A135 exact cores, no guard line.  The control: A132/A131's lesson is that a
                 re-solve alone moves tau, so the stored record is not a control.
    arm "guard"  the same, plus the <= K guard-line columns of `guardline.line_family`, ranked by
                 their OFFLINE violation on the node's stored dual support (results/offline144.jsonl).

A kill in the "guard" arm is NOT a certificate: the frozen verifier cannot see a guard column, so
such a node is recorded as "LP-dead under guard lines, certificate pending v3" (notes/spec.md).
Y0147 is additionally pushed through the frozen certify path so the FAILURE MODE is on the record.

NOT a shard launch: nothing is written into any campaign.  A57's PAUSE sentinel is reported but not
obeyed (A124's sanctioned scoped-sentinel pattern); this driver watches its OWN sentinel
attempts/A144-guard-lines/PAUSE, and is resumable (skips ids already in the output).

    set PYTHONDONTWRITEBYTECODE=1 && python code/invitro144.py --shard 0/2 --cap 240
"""
import argparse
import ctypes
import json
import math
import os
import subprocess
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A53 = os.path.join(ATT, "A53-simple-strata")
A57 = os.path.join(ATT, "A57-shadow-trees")
A132 = os.path.join(ATT, "A132-polygon-core")
A135 = os.path.join(ATT, "A135-polycore-verifier")
for _p in (os.path.join(A57, "code"), os.path.join(A132, "code"), os.path.join(A135, "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import guardline as G                                                   # noqa: E402
import guardlp                                                          # noqa: E402
import offline144 as OFF                                                # noqa: E402
import exactcore                                                        # noqa: E402
import polycore                                                         # noqa: E402
from caselp import Box, Hyp, solve_node                                 # noqa: E402
from warm57 import merged_warm                                          # noqa: E402
from pausegate import paused, reason                                    # noqa: E402

S_RAT = float(G.S_RAT)
S_RAT_SIDE = "969271/250000"
DELTA = 1e-2
OWN_PAUSE = os.path.join(BASE, "PAUSE")
RES = os.path.join(BASE, "results")
NODES = os.path.join(RES, "nodes")
CERTS = os.path.join(BASE, "certs")


class ExactHyp(Hyp):
    """A57's Hyp with A135's certified EXACT core half-side on every box (pins AND the conditioned
    box).  Only `cores` changes; `ok_many` and everything else are the base class's, so both arms
    of this experiment differ ONLY in the guard columns."""

    def __init__(self, boxes=(), nofams=()):
        super().__init__(boxes, nofams)
        ex, stock = [], []
        for b, c0 in zip(self.boxes, self.cores):
            try:
                ex.append(exactcore.exact_core(b))
            except Exception:
                ex.append(c0)
            stock.append(c0)
        ok, wp, gap = exactcore.cores_pairwise_disjoint(ex)
        self.exact_ok = bool(ok)
        self.exact_gap = float(gap) if gap is not None else None
        if ok:
            self.cores = ex
        self.a_stock = [float(c.a) for c in stock]
        self.a_exact = [float(c.a) for c in self.cores]


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
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def select(n_deep=13, n_rank=6, first="k5_11_interior_Y0147"):
    """Y0147 first, then the deepest offline violations, then the highest-ranked (A142 subtree
    cost) violators not already picked."""
    rows = [json.loads(l) for l in open(os.path.join(RES, "offline144.jsonl"), encoding="utf-8")
            if l.strip()]
    rows = [r for r in rows if r.get("max_viol") is not None]
    viol = [r for r in rows if r["max_viol"] > 1e-9]
    deep = sorted(viol, key=lambda r: -r["max_viol"])
    rank = sorted(viol, key=lambda r: r["rank"])
    out, seen = [], set()
    for r in [x for x in rows if x["id"] == first] + deep[:n_deep] + rank[:n_rank * 3]:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        out.append(r)
        if len(out) >= 1 + n_deep + n_rank:
            break
    return out


def certify(node_path, cert_out, cert_time, jobs=1):
    cmd = [sys.executable, os.path.join(A57, "code", "certify.py"), node_path,
           "--s_rat", S_RAT_SIDE, "--rounds", "2", "--jobs", str(jobs), "--depth", "56",
           "--time_limit", str(cert_time), "--out", cert_out, "--scale", "0",
           "--scale_cap", "1.03000", "--max_w", "64", "--loop_cols"]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, round(time.time() - t0, 1), (p.stdout + p.stderr)[-2000:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--cap", type=float, default=240.0)
    ap.add_argument("--max-guard", type=int, default=8)
    ap.add_argument("--cpu-hours", type=float, default=2.0)
    ap.add_argument("--warm-rows", type=int, default=30000)
    ap.add_argument("--certify-id", default="k5_11_interior_Y0147")
    ap.add_argument("--cert-time", type=float, default=240.0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--only", default=None,
                    help="comma-separated node ids: run only these (stage 2 at a longer cap)")
    ap.add_argument("--arms", default="base,guard")
    a = ap.parse_args()
    si, sn = (int(x) for x in a.shard.split("/"))
    out = a.out or os.path.join(RES, f"invitro144_s{si}.jsonl")
    os.makedirs(NODES, exist_ok=True)
    os.makedirs(CERTS, exist_ok=True)
    bn = below_normal()
    print(f"[{time.strftime('%H:%M:%S')}] A144 invitro shard {a.shard} pid {os.getpid()} "
          f"belownormal={bn}; A57 PAUSE={paused()} ({reason()!r:.60}) -- reported, not obeyed; "
          f"own sentinel {OWN_PAUSE}", flush=True)

    jobs = select()
    if a.only:
        want = [x.strip() for x in a.only.split(",") if x.strip()]
        jobs = [r for r in jobs if r["id"] in want]
    mine = [r for i, r in enumerate(jobs) if i % sn == si]
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["id"])
            except Exception:
                pass
    mine = [r for r in mine if r["id"] not in done]
    print(f"[{time.strftime('%H:%M:%S')}] {len(mine)} nodes on this shard "
          f"(of {len(jobs)} selected); {len(done)} already done", flush=True)

    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json"),
                               encoding="utf-8"))
    hh = DELTA / math.sqrt(2.0)
    warm, spent = {}, 0.0
    for r in mine:
        if os.path.exists(OWN_PAUSE):
            print("A144 pause sentinel set; stopping cleanly", flush=True)
            break
        if spent >= a.cpu_hours * 3600.0:
            print(f"shard CPU cap reached ({spent/3600.0:.2f} h)", flush=True)
            break
        nid = r["id"]
        got = OFF.load_node(nid)
        if got is None:
            append(out, dict(id=nid, error="no stored record"))
            continue
        d, path = got
        pins, hbox = G.node_boxes(d)
        nm = "k5_11" if nid.startswith("k5_11") else "k5_16"
        bud = d.get("budget") or 5
        try:
            pcv = polycore.build(hbox, max_v=16).verts
        except Exception:
            pcv = None
        fam = G.line_family(pins, hbox, pc_verts=pcv, max_lines=40)
        grows = [G.guard_row(pins, hbox, L, pc_verts=pcv) for L in fam]
        scored = []
        for L, gr in zip(fam, grows):
            _c, lhs = G.support_chords(d, L, a=0.5)
            scored.append((lhs - gr["rhs_float"], L, gr))
        scored.sort(key=lambda x: -x[0])
        chosen = scored[:a.max_guard]
        lines = guardlp.attach_costs([x[1] for x in chosen], [x[2] for x in chosen])
        if nm not in warm:
            warm[nm] = merged_warm(nm, max_rows=a.warm_rows)[0]
        W = warm[nm]
        H = ExactHyp(pins + [hbox], [])
        rec = dict(id=nid, cls=nm, level=r["level"], budget=bud, rank=r["rank"],
                   subtree_cpuh=r["subtree_cpuh"], record=path, cap=a.cap,
                   offline_max_viol=r["max_viol"], n_lines=len(fam),
                   exact_cores=dict(ok=H.exact_ok, min_gap=H.exact_gap,
                                    a_stock=H.a_stock, a_exact=H.a_exact),
                   guard=[dict(line=L.to_json(), rhs=float(L.cost), offline_viol=v)
                          for (v, L, _g) in chosen],
                   control=dict(tau=d.get("tau"), converged=d.get("converged"),
                                minmass=d.get("minmass"), support=len(d.get("packing") or [])),
                   arms={})
        t_node = time.time()
        for arm in [x.strip() for x in a.arms.split(",") if x.strip()]:
            ts = time.time()
            kw = dict(sym_kind="C1", warm=dict(atoms=list(W["atoms"]), rows=W["rows"]),
                      time_limit=a.cap, max_iter=900, out=None, log=lambda *x: None,
                      prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                      max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True,
                      fine=False)
            try:
                if arm == "stock":
                    # A57's DEPLOYED cores: the attribution control that separates "A135 exact
                    # cores" from "a fresh re-solve at A132's settings".
                    s = solve_node(S_RAT, Hyp(pins + [hbox], []), bud, **kw)
                    zrep = []
                elif arm == "guard":
                    with guardlp.installed(lines):
                        s = solve_node(S_RAT, H, bud, **kw)
                        zrep = [dict(line=L.to_json(), cost=float(L.cost),
                                     z=float(zz)) for L, zz in
                                zip(lines, guardlp._ACTIVE["z"])] \
                            if guardlp._ACTIVE["z"] is not None else []
                else:
                    s = solve_node(S_RAT, H, bud, **kw)
                    zrep = []
                tau = s.get("tau")
                st = dict(tau=tau, eta=(tau - bud) if tau is not None else None,
                          converged=s.get("converged"), minmass=s.get("minmass"),
                          maxcov=s.get("maxcov"), n_rows=s.get("n_rows"),
                          n_orbits=s.get("n_orbits"), support=len(s.get("packing") or []),
                          kills=bool(tau is not None and tau < bud - 1e-6),
                          z=zrep, seconds=round(time.time() - ts, 1))
                if arm == "guard" and nid == a.certify_id and st["eta"] is not None \
                        and st["eta"] <= -1e-3:
                    np_ = os.path.join(NODES, nid + "_guard.json")
                    s["parent"] = nm
                    s["child_id"] = nid
                    json.dump(s, open(np_, "w"))
                    cp = os.path.join(CERTS, nid + "_guard.json")
                    rc, cs, tail = certify(np_, cp, a.cert_time)
                    st.update(frozen_cert=("PASS" if rc == 0 else f"FAIL(rc={rc})"),
                              cert_seconds=cs, cert_tail=tail[-900:],
                              verdict="LP-dead under guard lines, certificate pending v3")
            except Exception as e:
                st = dict(error=repr(e)[:400], seconds=round(time.time() - ts, 1))
            rec["arms"][arm] = st
            print(f"[{time.strftime('%H:%M:%S')}] {nid:32s} {arm:5s} "
                  f"tau={st.get('tau')} conv={st.get('converged')} "
                  f"kills={st.get('kills')} {st.get('seconds')}s", flush=True)
        rec["wall_s"] = round(time.time() - t_node, 1)
        spent += rec["wall_s"]
        b, g = rec["arms"].get("base", {}), rec["arms"].get("guard", {})
        rec["delta_tau"] = ((g.get("tau") - b.get("tau"))
                            if (g.get("tau") is not None and b.get("tau") is not None) else None)
        append(out, rec)
        print(f"[{time.strftime('%H:%M:%S')}] {nid:32s} DONE  tau {b.get('tau')} -> "
              f"{g.get('tau')}  d={rec['delta_tau']}  [{spent/3600.0:.2f} CPU-h]", flush=True)
    print("invitro144 shard done", flush=True)


if __name__ == "__main__":
    main()
