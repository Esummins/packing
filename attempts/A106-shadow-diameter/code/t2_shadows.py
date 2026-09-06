"""A106 T2 — the shadows: a full 11-square local side-minimisation seeded from every open
A57 node at levels 2-4.

Per node, up to 4 seeds:
  s0  box centre        : the conditioned square at the box's centre pose, the other five free
                          squares greedily chosen from the node LP's fractional packing support
  s1  LP witness        : the heaviest placement of the LP packing whose pose lies IN the box,
                          the other five as above
  s2, s3 randomised     : the same greedy fill with randomised, weight-biased tie-breaks

Each seed runs A04's penalty continuation -> SLSQP polish on the class variety (shadow11.py),
then the landing is de-duplicated by pose distance 1e-4 (with k5_11's diagonal reflection
sigma, under which its pin set is invariant) and given an exact interval endpoint certificate.

ONE process, BLAS pinned, resumable through results/t2_shadows.jsonl.
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import argparse, json, math, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import shadow11 as S

RES = os.path.join(BASE, "results")
NODES = os.path.join(RES, "nodes")
OUT = os.path.join(RES, "t2_shadows.jsonl")


# ------------------------------------------------------------------ seeding
def sat_sep(c1, t1, c2, t2):
    """min over the 4 SAT axes of (penetration); <= 0 means separated."""
    d = np.asarray(c1) - np.asarray(c2)
    best = 1e9
    for (o, e) in ((t1, t2), (t2, t1)):
        for k in range(2):
            n = np.array([math.cos(o), math.sin(o)]) if k == 0 else np.array([-math.sin(o), math.cos(o)])
            r = 0.5 * (abs(math.cos(e) * n[0] + math.sin(e) * n[1])
                       + abs(-math.sin(e) * n[0] + math.cos(e) * n[1]))
            best = min(best, 0.5 + r - abs(float(d @ n)))
    return best


def greedy_fill(cands, fixed, need, tol_ladder=(0.0, 0.02, 0.06, 0.15, 0.4), rng=None):
    """cands: [(w, cx, cy, th)] sorted by preference.  fixed: [(c, th)] already placed.
    Return `need` placements each within tolerance of separation from all placed ones."""
    placed = list(fixed)
    out = []
    for tol in tol_ladder:
        for (w, cx, cy, th) in cands:
            if len(out) >= need:
                break
            c = np.array([cx, cy])
            if all(sat_sep(c, th, pc, pt) <= tol for (pc, pt) in placed):
                placed.append((c, th)); out.append((c, th))
        if len(out) >= need:
            break
    while len(out) < need:                     # last resort: random interior poses
        r = rng if rng is not None else np.random.default_rng(0)
        c = r.uniform(0.8, 3.0, size=2); th = r.uniform(0, math.pi / 2)
        placed.append((c, th)); out.append((c, th))
    return out[:need]


TRUMP = None


def trump_conf():
    """Trump's 11-square optimum (A87 t3lib), as (c(11,2), theta(11), shat)."""
    global TRUMP
    if TRUMP is None:
        sys.path.insert(0, os.path.abspath(os.path.join(BASE, "..", "A87-drain-flow", "code")))
        import t3lib as T
        z, _ = T.load_trump()
        z = np.asarray(z, float)
        conf = z[:33].reshape(11, 3)
        TRUMP = (conf[:, :2].copy(), conf[:, 2].copy(), float(z[33]))
    return TRUMP


def trump_transport(R, s):
    """Move Trump's five squares nearest the class slots ONTO the slots (axis-aligned) and
    leave his other six where they are: a class-admissible start with Trump's free geometry."""
    tc, tt, ts = trump_conf()
    tc = tc * (s / ts)
    pins = S.pins_at(R.aff, s)
    used, c, th = set(), np.zeros((11, 2)), np.zeros(11)
    for p in range(R.k):
        d = [(float(np.hypot(*(tc[i] - pins[p]))), i) for i in range(11) if i not in used]
        i = min(d)[1]
        used.add(i)
        c[p] = pins[p]; th[p] = 0.0
    rest = [i for i in range(11) if i not in used]
    for j, i in enumerate(rest):
        c[R.k + j] = tc[i]; th[R.k + j] = tt[i]
    return c, th


def build_seeds(row, node, R, nseeds=4, census=None):
    b = row["box"]
    th_mid = math.radians(0.5 * (b["th0"] + b["th1"]))
    cx_mid, cy_mid = 0.5 * (b["x0"] + b["x1"]), 0.5 * (b["y0"] + b["y1"])
    s_start = node.get("s", S.S0)
    pack = node.get("packing") or []
    cands = sorted([(p.get("y", 0.0), p["cx"], p["cy"], p["theta"]) for p in pack],
                   key=lambda t: -t[0])
    # LP witness inside the box (pose in B, theta compared mod 90 deg)
    inbox = []
    for (w, cx, cy, th) in cands:
        td = math.degrees(th) % 90.0
        if b["x0"] - 1e-9 <= cx <= b["x1"] + 1e-9 and b["y0"] - 1e-9 <= cy <= b["y1"] + 1e-9 \
                and b["th0"] - 1e-9 <= td <= b["th1"] + 1e-9:
            inbox.append((w, cx, cy, th))
    seeds = []
    # --- census seeds: the class's own low-lying shadows (t2a_census.py), relabelled so the
    # free square nearest the box becomes the conditioned one, then projected into B.
    for ci, sh in enumerate(census or []):
        cc = np.array(sh["conf"], float)
        c2 = cc[:, :2].copy()
        t2 = np.radians(cc[:, 2])
        d = sorted((float(np.hypot(c2[R.k + j][0] - cx_mid, c2[R.k + j][1] - cy_mid)), j)
                   for j in range(R.nfree))
        for rank in (0, 1):
            j = d[rank][1]
            c3, t3 = c2.copy(), t2.copy()
            c3[[R.k, R.k + j]] = c3[[R.k + j, R.k]]
            t3[[R.k, R.k + j]] = t3[[R.k + j, R.k]]
            seeds.append((f"cen{ci}r{rank}", R.z(c3, t3, float(sh["s"]))))

    # --- Trump-transport seeds.  The CONDITIONED square is always free index 0 (square k),
    # so the j-th nearest transported square is swapped into that slot before the pose box is
    # imposed; j = 0, 1, 2 give three different structural guesses at "which square is in B".
    tc, tth = trump_transport(R, s_start)
    d = sorted((float(np.hypot(tc[R.k + j][0] - cx_mid, tc[R.k + j][1] - cy_mid)), j)
               for j in range(R.nfree))
    ntr = max(0, min(3, (nseeds - len(seeds)) // 2))
    for rank in range(ntr):
        j = d[rank][1]
        c2, t2 = tc.copy(), tth.copy()
        c2[[R.k, R.k + j]] = c2[[R.k + j, R.k]]
        t2[[R.k, R.k + j]] = t2[[R.k + j, R.k]]
        seeds.append((f"trump{rank}", R.z(c2, t2, s_start)))
        c3, t3 = c2.copy(), t2.copy()
        c3[R.k] = [cx_mid, cy_mid]; t3[R.k] = th_mid
        seeds.append((f"trumpbox{rank}", R.z(c3, t3, s_start)))

    specs = [("box_centre", (cx_mid, cy_mid, th_mid))]
    if inbox:
        w, cx, cy, th = inbox[0]
        specs.append(("lp_witness", (cx, cy, th)))
    k = 2
    while len(specs) < max(0, nseeds - len(seeds)):
        specs.append((f"rand{k}", (cx_mid, cy_mid, th_mid)))
        k += 1
    aff = R.aff
    for si, (tag, (cx, cy, th)) in enumerate(specs[:max(0, nseeds - len(seeds))]):
        rng = np.random.default_rng(1000 + si)
        pins = S.pins_at(aff, s_start)
        fixed = [(pins[i], 0.0) for i in range(R.k)] + [(np.array([cx, cy]), th)]
        cc = cands
        if tag.startswith("rand"):
            jitter = rng.uniform(0.6, 1.4, size=len(cands))
            cc = sorted([(c[0] * j, c[1], c[2], c[3]) for c, j in zip(cands, jitter)],
                        key=lambda t: -t[0])
        rest = greedy_fill(cc, fixed, R.nfree - 1, rng=rng)
        c = np.zeros((11, 2)); tt = np.zeros(11)
        for i in range(R.k):
            c[i] = pins[i]
        c[R.k] = [cx, cy]; tt[R.k] = th
        for j, (pc, pt) in enumerate(rest):
            c[R.k + 1 + j] = pc; tt[R.k + 1 + j] = pt
        seeds.append((tag, R.z(c, tt, s_start)))
    return seeds


# ------------------------------------------------------------------ box-vs-pin emptiness
def pin_clash(R, box, n=5, m=3):
    """Is the node's pose box B geometrically incompatible with a class pin?

    A57's pinguard tests the rational CORES; this tests the true unit squares.  Grid the box
    (n^3 poses) against each pin's delta-slack core (m^2 offsets) and take the smallest SAT
    overlap.  min_overlap > 0 for some pin means NO admissible placement exists in B at ANY
    side, so the node is EMPTY on geometry alone -- no LP, no certificate needed."""
    xs = np.linspace(box["x0"], box["x1"], n)
    ys = np.linspace(box["y0"], box["y1"], n)
    ts = np.radians(np.linspace(box["th0"], box["th1"], n))
    us = np.linspace(-R.pin_hw, R.pin_hw, m) if R.pin_hw > 0 else np.array([0.0])
    worst = []
    for p in range(R.k):
        best = 1e9
        for ux in us:
            for uy in us:
                # the pin rides its slot line; only beta = 0 coordinates are s-independent, so
                # the R-anchored pins are evaluated at s0 (their own certified side).
                pc = S.pins_at(R.aff, S.S0)[p] + np.array([ux, uy])
                for x in xs:
                    for y in ys:
                        for t in ts:
                            v = sat_sep(np.array([x, y]), t, pc, 0.0)
                            if v < best:
                                best = v
        worst.append(float(best))
    return worst


# ------------------------------------------------------------------ landing signature
def sigma_image(c, th):
    """k5_11's diagonal reflection: (x,y)->(y,x), theta -> 90 - theta (mod 90)."""
    c2 = c[:, ::-1].copy()
    t2 = (math.pi / 2 - th) % (math.pi / 2)
    return c2, t2


def signature(R, z, sigma=False):
    x = R.x(z)
    c, th, s = S.unpack(x)
    fc, ft = c[R.k:].copy(), np.mod(th[R.k:], math.pi / 2)
    if sigma:
        fc, ft = sigma_image(fc, ft)
    order = np.lexsort((np.round(fc[:, 1], 6), np.round(fc[:, 0], 6)))
    return np.concatenate([fc[order].ravel(), ft[order], [s]])


def sig_dist(a, b):
    return float(np.abs(a - b).max())


# ------------------------------------------------------------------ driver
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall", type=float, default=5400.0)
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--hops", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--table", default="t1_boxes.json")
    ap.add_argument("--census", default="t2a_census.json")
    ap.add_argument("--ncensus", type=int, default=5)
    ap.add_argument("--endpoint", type=int, default=0, help="1 = exact endpoint cert per node")
    ap.add_argument("--priority", type=int, default=1,
                    help="1 = deepest / rarest levels first, then a stratified L2 sample")
    ap.add_argument("--l2cap", type=int, default=0, help="cap on k5_11 level-2 rows (0 = all)")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--pin_hw", type=float, default=-1.0,
                    help="pin slack half-width per axis; <0 = A57's live delta=1e-2 core "
                         "(0.01/sqrt2), 0 = exact slots")
    a = ap.parse_args()

    t1 = json.load(open(os.path.join(RES, a.table)))
    rows = t1["rows"]
    census = {}
    cp = os.path.join(RES, a.census)
    if os.path.exists(cp):
        cj = json.load(open(cp))
        for cls, d in cj.items():
            census[cls] = d["shadows"][:a.ncensus]
        print("census seeds: " + ", ".join(f"{c}:{len(v)}" for c, v in census.items()), flush=True)
    if a.priority:
        def key(r):
            return (-r["level"], 0 if r["cls"] == "k5_16" else 1, r["id"])
        rows = sorted(rows, key=key)
        if a.l2cap:
            keep, seen = [], 0
            for r in rows:
                if r["cls"] == "k5_11" and r["level"] == 2:
                    seen += 1
                    if seen % max(1, len(rows) // max(1, a.l2cap)) and seen > a.l2cap:
                        continue
                    if seen > a.l2cap:
                        continue
                keep.append(r)
            rows = keep
    if a.limit:
        rows = rows[:a.limit]
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out):
            try:
                done.add(json.loads(line)["id"])
            except Exception:
                pass
    slots = json.load(open(os.path.join(RES, "snapshot", "name_to_slots.json")))
    hw = S.PIN_HW if a.pin_hw < 0 else a.pin_hw
    Rc = {cls: S.Reduction(S.pin_affine(slots[cls]), pin_hw=hw) for cls in ("k5_11", "k5_16")}
    print(f"pin_hw = {hw!r}  (nz = {Rc['k5_11'].nz})", flush=True)

    t_start = time.time()
    fh = open(a.out, "a")
    for n, row in enumerate(rows):
        if row["id"] in done:
            continue
        if time.time() - t_start > a.wall:
            print("wall cap reached", flush=True)
            break
        R = Rc[row["cls"]]
        npath = os.path.join(NODES, row["id"] + ".json")
        if not os.path.exists(npath):
            continue
        t0 = time.time()
        b = row["box"]
        bnds = S.box_bounds(R, b)
        clash0 = pin_clash(R, b)
        if max(clash0) > 1e-9:
            # EMPTY on geometry: no pose in B can be separated from this pin at any side, so
            # there is nothing to minimise.  Recorded and skipped.
            rec = dict(id=row["id"], cls=row["cls"], level=row["level"], status=row["status"],
                       box=b, dmax=row["dmax"], deuc=row["deuc"], tau=row.get("tau"),
                       eta=row.get("eta"), a=row.get("a"), seconds=round(time.time() - t0, 2),
                       shadow=None, pin_clash=clash0, pin_clash_worst=max(clash0),
                       pin_empty=True, infeasible=None, landings=[])
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            print(f"[{n+1}/{len(rows)}] {row['id']:42s} L{row['level']} EMPTY-BY-PIN "
                  f"(clash={max(clash0):.5f}, pin {clash0.index(max(clash0))})", flush=True)
            continue
        node = json.load(open(npath))
        seeds = build_seeds(row, node, R, a.seeds, census=census.get(row["cls"], []))
        lands = []
        zmap = {}

        def record(tag, z0, bounds):
            try:
                z, ov, cv = S.minimise(R, z0, bounds=bounds)
                if max(ov, cv) > 1e-7:
                    # the descent jammed: buy feasibility first at a roomy fixed side, then
                    # descend from the repaired configuration
                    zr, m = S.push_margin(R, z0, 4.60, bounds=bounds)
                    if m > 1e-9:
                        z2, ov2, cv2 = S.minimise(R, zr, bounds=bounds)
                        if max(ov2, cv2) < max(ov, cv):
                            z, ov, cv = z2, ov2, cv2
            except Exception as e:
                lands.append(dict(seed=tag, error=repr(e)[:200]))
                return None
            x = R.x(z)
            c, th, s = S.unpack(x)
            lands.append(dict(
                seed=tag, s=float(s), ov=ov, cv=cv,
                feasible=bool(max(ov, cv) < 1e-7),
                conf=[[float(c[i, 0]), float(c[i, 1]), float(math.degrees(th[i]) % 90.0)]
                      for i in range(11)],
                sig=[float(v) for v in signature(R, z)],
                sig_sigma=[float(v) for v in signature(R, z, sigma=True)],
            ))
            zmap[len(lands) - 1] = z
            return z

        # (1) the BOX-CONSTRAINED minimum: square #5 (the conditioned one) is held in B
        for (tag, z0) in seeds:
            record(tag, S.clip_to(bnds, z0), bnds)
        for h in range(a.hops):
            ok = [(l["s"], i) for i, l in enumerate(lands) if l.get("feasible") and i in zmap]
            if not ok:
                break
            zb = zmap[min(ok)[1]]
            rng = np.random.default_rng(7000 + h)
            zp = zb.copy()
            zp[3:3 * R.nfree] += rng.normal(0, 0.06, 3 * R.nfree - 3)
            zp[0:3] += rng.normal(0, 0.01, 3)
            if R.nu:
                zp[3 * R.nfree:R.nz - 1] += rng.normal(0, 0.004, R.nu)
            zp[-1] = zb[-1] + 0.02
            record(f"hop{h}", S.clip_to(bnds, zp), bnds)

        clash = clash0
        ok = [(l["s"], i) for i, l in enumerate(lands) if l.get("feasible") and i in zmap]
        shadow = None
        infeasible = None
        if not ok:
            cand = [(max(l["ov"], l["cv"]), i) for i, l in enumerate(lands) if "ov" in l]
            if cand:
                resid, ib = min(cand)
                x = R.x(zmap[ib])
                o = S.sat_min_overlap(x); v = S.container_viol(x)
                infeasible = dict(
                    resid=float(resid), s=lands[ib]["s"], seed=lands[ib]["seed"],
                    bad_pairs=[[int(S.I_IDX[q]), int(S.J_IDX[q]), float(o[q])]
                               for q in range(len(o)) if R.pair_keep[q] and o[q] > 1e-6],
                    bad_cont=[[int(i2), float(v[i2])]
                              for i2 in range(len(v)) if R.cont_keep[i2] and v[i2] > 1e-6])
        if ok:
            sbox, ibest = min(ok)
            zb = zmap[ibest]
            # where in the box does the constrained minimum sit?
            act = dict(
                x=min(zb[0] - b["x0"], b["x1"] - zb[0]),
                y=min(zb[1] - b["y0"], b["y1"] - zb[1]),
                th=min(math.degrees(zb[2]) - b["th0"], b["th1"] - math.degrees(zb[2])),
            )
            interior = bool(act["x"] > 1e-6 and act["y"] > 1e-6 and act["th"] > 1e-5)
            # (2) release the box: which UNCONSTRAINED local minimum does it flow to?
            zf, ovf, cvf = S.minimise(R, zb.copy(), bounds=R.base_bounds)
            xf = R.x(zf)
            cf, thf, sf = S.unpack(xf)
            still = []
            for i in range(11):
                td = math.degrees(thf[i]) % 90.0
                if (b["x0"] - 1e-9 <= cf[i, 0] <= b["x1"] + 1e-9
                        and b["y0"] - 1e-9 <= cf[i, 1] <= b["y1"] + 1e-9
                        and b["th0"] - 1e-9 <= td <= b["th1"] + 1e-9):
                    still.append(i)
            eps, crep = (S.certify_endpoint(R, zb, bounds=bnds) if a.endpoint else (None, {}))
            shadow = dict(
                s_box=float(sbox), slack_box=float(sbox - S.S0), seed=lands[ibest]["seed"],
                boundary_slack=act, interior=interior,
                conf=lands[ibest]["conf"], sig=lands[ibest]["sig"],
                sig_sigma=lands[ibest]["sig_sigma"],
                free_s=float(sf), free_feasible=bool(max(ovf, cvf) < 1e-7),
                free_conf=[[float(cf[i, 0]), float(cf[i, 1]), float(math.degrees(thf[i]) % 90.0)]
                           for i in range(11)],
                free_sig=[float(v) for v in signature(R, zf)],
                free_sig_sigma=[float(v) for v in signature(R, zf, sigma=True)],
                free_in_box=still,
                endpoint_eps=eps, endpoint=crep,
            )
        rec = dict(id=row["id"], cls=row["cls"], level=row["level"], status=row["status"],
                   box=row["box"], dmax=row["dmax"], deuc=row["deuc"],
                   tau=row["tau"], eta=row["eta"], a=row["a"],
                   n_packing=len(node.get("packing") or []),
                   seconds=round(time.time() - t0, 2), shadow=shadow,
                   pin_clash=clash, pin_clash_worst=(max(clash) if clash else None),
                   pin_empty=bool(clash and max(clash) > 1e-9), infeasible=infeasible,
                   landings=[{k: v for k, v in l.items() if k != "conf"} for l in lands])
        fh.write(json.dumps(rec) + "\n"); fh.flush()
        print(f"[{n+1}/{len(rows)}] {row['id']:42s} L{row['level']} "
              f"s_box={shadow['s_box']:.7f} slack={shadow['slack_box']:.6f} "
              f"int={shadow['interior']} free={shadow['free_s']:.7f} "
              f"({rec['seconds']}s)" if shadow else
              f"[{n+1}/{len(rows)}] {row['id']:42s} L{row['level']} NO LANDING "
              f"(pin_clash_worst={rec['pin_clash_worst']:.5f} resid="
              f"{(infeasible or {}).get('resid', float('nan')):.4f})", flush=True)
    fh.close()


if __name__ == "__main__":
    main()
