"""A119 T1 -- generate the exact certificate of a certified neighbourhood N.

For each N the tree is re-run with `record=True` and a kill threshold s0 + 1e-8 (so the exported
multipliers keep a margin over the checker's own rounding), and the whole proof object is
written out:

  meta   : the bodies (boxes, slack cores, variable indices), the window, the cut, s0;
  root   : the proof tree -- `bisect` / `qsplit` / `branch` internal nodes, `imp` / `imp_sel`
           leaves (a cell with no interior-disjoint configuration), `dead` leaves carrying the
           selections the multipliers use, which of them are FORCED (not supplied by a branch),
           and the RATIONAL Farkas vector (every multiplier a multiple of 2^-40, re-verified
           against the relaxed rows before it is written).

The file is checked by `check_local.py`, which shares no code with the generator.

Usage: python exact119.py [id ...]      (default: all five certified N)
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a119lib as L
import a116lib as A

TARGETS = {
    # a small N kept as the pipeline regression (A116 t2: DEAD 3.885781 in 7 s)
    "S02_k5_11_r0.02_rho2": dict(tag="S02", cls="k5_11", r=0.02, rho=2.0, cut=None),
    # a q-range-splitting N, kept so the checker's qsplit path is exercised (A116 t2: 144 splits)
    "S07_trump5_r0.05_rho10": dict(tag="S07", cls="trump5", r=0.05, rho=10.0, cut=41.565),
    "S02_k5_11_r0.20_rho10": dict(tag="S02", cls="k5_11", r=0.2, rho=10.0, cut=None),
    "S02_k5_11_r0.05_rho20": dict(tag="S02", cls="k5_11", r=0.05, rho=20.0, cut=None),
    "S02_k5_11_r0.10_rho10": dict(tag="S02", cls="k5_11", r=0.1, rho=10.0, cut=None),
    "S07_trump5_r0.10_rho40": dict(tag="S07", cls="trump5", r=0.1, rho=40.0, cut=41.565),
    "S07_trump5_r0.20_rho10": dict(tag="S07", cls="trump5", r=0.2, rho=10.0, cut=41.565),
}


def body_json(b):
    if b.kind == "free":
        return dict(name=b.name, kind="free", vi=b.vi, ti=b.ti, x0=b.x0, x1=b.x1, y0=b.y0, y1=b.y1,
                    t0=b.t0, t1=b.t1, anchor=[b.anchor[0], b.anchor[1], b.anchor[2]])
    return dict(name=b.name, kind="pin", vi=b.vi, ax=list(b.ax), ay=list(b.ay), hh=b.hh)


def count(node, acc):
    k = node.get("k")
    acc[k] = acc.get(k, 0) + 1
    if k == "dead":
        acc["mult"] = acc.get("mult", 0) + len(node["y"])
    for c in node.get("ch", ()):
        count(c, acc)
    return acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--time_cap", type=float, default=3600.0)
    a = ap.parse_args()
    ids = a.ids or [k for k in TARGETS if k not in ("S02_k5_11_r0.02_rho2", "S07_trump5_r0.05_rho10")]
    logp = os.path.join(L.LOGS, "exact119.log")

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    man = {}
    mp = os.path.join(L.CERTS, "manifest.json")
    if os.path.exists(mp):
        man = json.load(open(mp, encoding="utf-8"))
    for cid in ids:
        t = TARGETS[cid]
        t0 = time.time()
        bodies, nv, s_sh, P = A.build_bodies(t["tag"], t["cls"], t["r"], t["rho"],
                                             anchor_side=A.S0, pin_slack=A.PIN_SLACK,
                                             tilt_floor_deg=t["cut"])
        _, Pe, _, _ = A.anchored(t["tag"], s_sh)
        ss = A.shadow_selections(bodies, Pe)
        T = L.RecTree(bodies, nv, contact_pairs=list(ss), min_cell_deg=0.05, node_cap=8000000,
                      time_cap=a.time_cap, record=True, inherit=False, margin=1e-8, round_bits=40)
        v = T.run()
        if not v["dead"]:
            log("%s NOT DEAD at margin 1e-8 (capped=%s, live=%d, unresolved=%d) -- no certificate"
                % (cid, v["capped"], v["stats"]["live_low"], v["stats"]["unresolved"]))
            continue
        cert = dict(meta=dict(
            id=cid, tag=t["tag"], cls=t["cls"], r=t["r"], rho_deg=t["rho"], cut_deg=t["cut"],
            pin_slack=A.PIN_SLACK, anchor_side=A.S0, s_lo=A.S_LO, s_hi=A.S_HI_DEFAULT,
            s0=[969271, 250000], kill_margin=1e-8, multiplier_denominator="2^40",
            nv=nv, bodies=[body_json(b) for b in bodies],
            L=[b.name for b in bodies if b.kind == "free"],
            P=[b.name for b in bodies if b.kind == "pin"],
            generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
            generator="attempts/A119-local-cert-lean/code/exact119.py",
            theorem="Theorem LOCAL (docs/proofs/local_certificate.md sec 3): every cell/leaf of "
                    "the recorded cover has relaxed LP value > s0, hence Dead_{L u P}(N, s0)"),
            stats=v["stats"], certified_min=v["certified_min"], seconds_tree=round(time.time() - t0, 1),
            root=T.proof)
        acc = count(T.proof, {})
        cert["meta"]["node_counts"] = acc
        path = os.path.join(L.CERTS, "%s.cert.json.gz" % cid)
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump(cert, f, separators=(",", ":"))
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        man[cid] = dict(file=os.path.basename(path), sha256=h, bytes=os.path.getsize(path),
                        node_counts=acc, certified_min=v["certified_min"],
                        seconds_tree=cert["seconds_tree"], generated=cert["meta"]["generated"])
        with open(mp, "w", encoding="utf-8") as f:
            json.dump(man, f, indent=1, sort_keys=True)
        log("%-24s DEAD  cells(bisect) %-6d branch %-4d imp %-5d dead-leaves %-6d multipliers %-7d "
            "certmin %.7f  %.0fs  %.1f MB  %s" %
            (cid, acc.get("bisect", 0), acc.get("branch", 0),
             acc.get("imp", 0) + acc.get("imp_sel", 0), acc.get("dead", 0), acc.get("mult", 0),
             v["certified_min"], cert["seconds_tree"], os.path.getsize(path) / 1e6, h[:16]))


if __name__ == "__main__":
    main()
