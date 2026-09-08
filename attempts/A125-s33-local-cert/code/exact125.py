"""A125 -- the exact (rational Farkas) certificate of a certified neighbourhood N of S33 / S38.

Same object and same file format as A119 T1 (`exact119.py`), so that A119's INDEPENDENT checker
`check_local.py` -- which shares no code with any generator, reads only the file, and decides in
exact rational interval arithmetic -- verifies it unchanged:

  meta : the bodies (boxes, slack cores, variable indices), the window, the cut, s0;
  root : the proof tree -- `bisect` / `qsplit` / `branch` internal nodes, `imp` / `imp_sel`
         leaves, `dead` leaves with the selections the multipliers use, which of them are FORCED,
         and the RATIONAL Farkas vector (every multiplier a multiple of 2^-40, re-verified
         against the relaxed rows by weak duality before it is written).

Usage:  python exact125.py S33:0.2:20 [S38:0.1:10 ...]
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a125lib as G
import a116lib as A
import a119lib as L


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
    ap.add_argument("targets", nargs="+", help="tag:r:rho[:cut]")
    ap.add_argument("--time_cap", type=float, default=3600.0)
    ap.add_argument("--min_cell_deg", type=float, default=0.05)
    ap.add_argument("--no_inherit", action="store_true",
                    help="disable dual inheritance (A119's exact119 setting; ~5x slower). "
                         "Inheritance is sound for the exported object: a child is closed on the "
                         "inherited vector only when that vector certifies the bound on the "
                         "CHILD's own rows, and check_local.py re-derives it from the file.")
    a = ap.parse_args()
    logp = os.path.join(G.LOGS, "exact125.log")

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    mp = os.path.join(G.CERTS, "manifest.json")
    man = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {}
    for spec in a.targets:
        parts = spec.split(":")
        tag, r, rho = parts[0], float(parts[1]), float(parts[2])
        cut = float(parts[3]) if len(parts) > 3 and parts[3] not in ("", "None") else None
        cid = "%s_%s_r%.2f_rho%g" % (tag, G.SHADOWS[tag]["cls"], r, rho)
        t0 = time.time()
        bodies, nv, s_sh, P = G.build_bodies125(tag, r, rho, anchor_side=G.S0,
                                                pin_slack=G.PIN_SLACK, tilt_floor_deg=cut)
        _, Pe, _, _ = G.anchored125(tag, s_sh)
        ss = A.shadow_selections(bodies, Pe)
        T = L.RecTree(bodies, nv, s_lo=G.S_LO, s_hi=G.S_HI, contact_pairs=list(ss),
                      min_cell_deg=a.min_cell_deg, node_cap=8000000, time_cap=a.time_cap,
                      record=True, inherit=not a.no_inherit, margin=1e-8, round_bits=40)
        v = T.run()
        if not v["dead"]:
            log("%s NOT DEAD at margin 1e-8 (capped=%s live=%d unresolved=%d) -- no certificate"
                % (cid, v["capped"], v["stats"]["live_low"], v["stats"]["unresolved"]))
            continue
        cert = dict(meta=dict(
            id=cid, tag=tag, cls=G.SHADOWS[tag]["cls"], frame=G.SHADOWS[tag]["frame"],
            r=r, rho_deg=rho, cut_deg=cut, pin_slack=G.PIN_SLACK, anchor_side=G.S0,
            s_lo=G.S_LO, s_hi=G.S_HI, s0=[969271, 250000], kill_margin=1e-8,
            multiplier_denominator="2^40", nv=nv, bodies=[body_json(b) for b in bodies],
            L=[b.name for b in bodies if b.kind == "free"],
            P=[b.name for b in bodies if b.kind == "pin"],
            s_star=s_sh,
            generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
            generator="attempts/A125-s33-local-cert/code/exact125.py",
            minimum="A122 attempts/A122-s33-certify/results/exact.json (%s, 50-digit Lagrange solution)" % tag,
            theorem="Theorem LOCAL (docs/proofs/local_certificate.md sec 3): every cell/leaf of "
                    "the recorded cover has relaxed LP value > s0, hence Dead_{L u P}(N, s0)"),
            stats=v["stats"], certified_min=v["certified_min"],
            seconds_tree=round(time.time() - t0, 1), root=T.proof)
        acc = count(T.proof, {})
        cert["meta"]["node_counts"] = acc
        path = os.path.join(G.CERTS, "%s.cert.json.gz" % cid)
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump(cert, f, separators=(",", ":"))
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        man[cid] = dict(file=os.path.basename(path), sha256=h, bytes=os.path.getsize(path),
                        node_counts=acc, certified_min=v["certified_min"],
                        seconds_tree=cert["seconds_tree"], generated=cert["meta"]["generated"])
        with open(mp, "w", encoding="utf-8") as f:
            json.dump(man, f, indent=1, sort_keys=True)
        log("%-26s DEAD  cells(bisect) %-6d branch %-4d imp %-5d dead-leaves %-6d multipliers %-7d "
            "certmin %.7f  %.0fs  %.3f MB  %s"
            % (cid, acc.get("bisect", 0), acc.get("branch", 0),
               acc.get("imp", 0) + acc.get("imp_sel", 0), acc.get("dead", 0), acc.get("mult", 0),
               v["certified_min"], cert["seconds_tree"], os.path.getsize(path) / 1e6, h[:16]))


if __name__ == "__main__":
    main()
