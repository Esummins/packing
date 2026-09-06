"""A109 Trump canaries.

(a) EXACT: the second-largest free-square depth d2 of the exact Trump (A03 trump11_exact.json,
    60 digits) at every completable slot of trump5, in A109's own slot frames, compared with
    docs/proofs/slot_crowds.md sec 7.  Validates the frames used by T1/T2.
(b) LP: the trump5 CLASS ROOT with A57's slack pin boxes (h = rho/sqrt2, rho = 1e-2) at s0 --
    a hypothesis the exact Trump SATISFIES -- carries the crowd rows of each configuration.
    Lemma SLOT-CROWD is TRUE of Trump at every usable slot (d2 = 0.280 / 0.264 / 0.305 at
    BL(1,1), TR(0,1), TR(1,0)), so this node must NOT be killed at any delta <= 0.264.
"""
import json, math, os, sys, time
from decimal import Decimal, getcontext
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401
import a109lib as L
import lpbox94
import slotfam94 as SF
from corner85 import f_min_max
from caselp94 import Hyp, Box, solve_node

# docs/proofs/slot_crowds.md sec 7 (the lead's exact depths)
REF = {"BL(0,2)": (0.967442, 0.016049), "BL(1,1)": (0.542145, 0.280083),
       "BR(0,1)": (0.524494, 0.252050), "TR(0,1)": (0.542145, 0.264033),
       "TR(1,0)": (0.451358, 0.305293), "TL(0,0)": (0.168321, 0.155475)}


def _sig(t):
    return (1 - t) / (1 + t)


def load_trump():
    getcontext().prec = 80
    d = json.load(open(os.path.join(L.ROOT, "attempts", "A03-upper-reconstruct",
                                    "trump11_exact.json")))
    sT = Fr(Decimal(d["s"]))
    t = Fr(Decimal(d["t_tan_half_theta"]))
    out = []
    for i, q in enumerate(d["squares"]):
        cx, cy, th = Fr(Decimal(q["cx"])), Fr(Decimal(q["cy"])), Fr(Decimal(q["theta"]))
        up = abs(th) < Fr(1, 10 ** 50)
        out.append(dict(i=i, cx=cx, cy=cy, t=(Fr(0) if up else t), upright=up))
    return sT, out


def exact_canary(log=print):
    sT, sq = load_trump()
    pins = [SF.pin_at(p, sT) for p in SF.CLASSES["trump5"]["pins"]]
    pin_i = set()
    for q in sq:
        if q["upright"] and any(abs(q["cx"] - p[0]) < Fr(1, 10 ** 30)
                                and abs(q["cy"] - p[1]) < Fr(1, 10 ** 30) for p in pins):
            pin_i.add(q["i"])
    assert len(pin_i) == 5, sorted(pin_i)
    cells = [("BL", 0, 2), ("BL", 1, 1), ("BR", 0, 1), ("TR", 0, 1), ("TR", 1, 0), ("TL", 0, 0)]
    rows, worst = [], 0.0
    for (c, i, j) in cells:
        ds = []
        for q in sq:
            if q["i"] in pin_i:
                continue
            u = (q["cx"] if c in ("BL", "TL") else sT - q["cx"]) - i
            v = (q["cy"] if c in ("BL", "BR") else sT - q["cy"]) - j
            tt = q["t"] if c in ("BL", "TR") else _sig(q["t"])
            d = 1 - f_min_max(u, v, tt)
            if d > Fr(1, 10 ** 30):
                ds.append((float(d), q["i"]))
        ds.sort(reverse=True)
        name = "%s(%d,%d)" % (c, i, j)
        d1 = ds[0][0] if ds else 0.0
        d2 = ds[1][0] if len(ds) > 1 else 0.0
        r = REF.get(name)
        dev = max(abs(d1 - r[0]), abs(d2 - r[1])) if r else None
        if dev is not None:
            worst = max(worst, dev)
        rows.append(dict(cell=name, n_meeters=len(ds), d1=d1, d2=d2, ref=r, dev=dev,
                         meeters=[q for (_, q) in ds]))
        log("  %-9s meeters=%d d1=%.6f d2=%.6f ref=%s dev=%s"
            % (name, len(ds), d1, d2, r, None if dev is None else "%.1e" % dev))
    ok = worst < 1e-6
    log("  exact Trump slot canary: worst deviation %.2e -> %s" % (worst, "PASS" if ok else "FAIL"))
    return ok, worst, rows


def root_node(cls="trump5", rho=1e-2):
    h = rho / math.sqrt(2.0) * (1 + 1e-12)
    boxes = []
    for p in SF.CLASSES[cls]["pins"]:
        x, y = SF.pin_at(p, SF.S0)
        boxes.append(Box(float(x) - h, float(x) + h, float(y) - h, float(y) + h, 0.0, 0.0))
    return Hyp(boxes, []), h


def lp_canary(cfgs=("sound", "d0.05", "d0.1", "d0.3"), e=Fr(1, 2), lp_time=600.0, log=print):
    cls = "trump5"
    hyp, h = root_node(cls)
    budget0 = 11 - len(hyp.boxes)
    out = []
    for cfg in cfgs:
        fam = L.get_fam(cls, cfg, log=lambda *a: None)
        B = 2 * fam["m_u"]            # class root: no branched core, the full incidence budget
        bonus = int(math.floor(float(e) * B))
        budget = budget0 + bonus
        p = os.path.join(L.NODES, "trump5_root__%s__e%s.json" % (cfg, str(e).replace("/", "o")))
        if os.path.exists(p):
            r = json.load(open(p))
        else:
            SF.install_rhs(fam, e, lpbox94)
            t0 = time.time()
            try:
                r = solve_node(float(SF.S0), hyp, budget, sym_kind="C1",
                               warm=None, time_limit=lp_time, max_iter=900, out=None,
                               log=lambda *x: None, prune=0, prune_cols=3,
                               col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                               max_rows_add=2000, fine_slack=99.0, alternate=True)
            finally:
                SF.install_rhs(None, None, lpbox94)
            r["a109_lp_s"] = round(time.time() - t0, 1)
            r["a109"] = dict(nid="trump5_root", cfg=cfg, e=str(e), B=B, bonus=bonus,
                             budget=budget, rmax_branched=[], cls=cls, m_u=fam["m_u"],
                             a_w=[str(x) for x in fam["a_w"]])
            json.dump(r, open(p, "w"))
        dead = bool(r["converged"] and r["tau"] < budget - 1e-6)
        rec = dict(cfg=cfg, e=str(e), m_u=fam["m_u"], B=B, bonus=bonus, budget0=budget0,
                   budget=budget, tau=r["tau"], eta=r["tau"] - budget,
                   converged=bool(r["converged"]), minmass=r["minmass"], dead=dead,
                   dead_unconv=bool(r["tau"] < budget - 1e-6), lp_s=r.get("a109_lp_s"),
                   must_not_die=(cfg != "d0.3"))
        out.append(rec)
        log("  trump5 root %-6s m_u=%d budget %d->%d tau=%.4f eta=%+.4f conv=%s DEAD=%s "
            "(must_not_die=%s) %ss"
            % (cfg, fam["m_u"], budget0, budget, r["tau"], rec["eta"], r["converged"], dead,
               rec["must_not_die"], rec["lp_s"]))
    return out


if __name__ == "__main__":
    logp = os.path.join(L.LOGS, "canary109.log")

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfgs", default="sound,d0.05,d0.1,d0.3")
    ap.add_argument("--lp_time", type=float, default=600.0)
    ap.add_argument("--exact_only", action="store_true")
    A = ap.parse_args()
    log("=== A109 Trump canary ===")
    ok, worst, rows = exact_canary(log)
    res = dict(exact=dict(ok=bool(ok), worst_dev=worst, rows=rows))
    if not A.exact_only:
        res["lp"] = lp_canary(tuple(A.cfgs.split(",")), lp_time=A.lp_time, log=log)
        bad = [r for r in res["lp"] if r["must_not_die"] and (r["dead"] or r["dead_unconv"])]
        res["verdict"] = "REFUTED" if bad else "PASS"
        log("  LP canary verdict: %s%s" % (res["verdict"],
                                           "" if not bad else " -- killed at " + str([b["cfg"] for b in bad])))
    json.dump(res, open(os.path.join(L.RES, "canary109.json"), "w"), indent=1, default=str)
