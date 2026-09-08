"""A125 -- the consumer: which alive nodes fall inside a certified neighbourhood N of S33 / S38.

For every N certified by run125.py (DEAD, 0 sample hits, Trump outside) the test of A116 sec 7(b),
widened so that a node of a SMALLER class can be tested against a bigger-class N:

    the node's LP-support representative (A107 `extract.json` `cfg`, eleven poses at s0) is
    carried into the class frame and matched, INJECTIVELY, against ALL the bodies of N --
    the |L| free boxes (centre within r in the inf-norm of the anchor, tilt within rho mod 90 deg,
    respecting the cut) AND the |P| pin cores (centre within the delta-core halfwidth of the slot
    cell at s0, tilt 0 mod 90 deg).  A node that matches has its whole hypothesis inside N, so its
    YES leaf is dead by Theorem LOCAL.

Testing the pins is what makes a trump5 (A60) node admissible against a k6_07 N: trump5's five
pins are a SUBSET of k6_07's six, so the sixth cell BL(0,2) has to be found in the support, it is
not free by the node's class.

Two frames are reported per node:
  struct_op : A107's own canonicalising D4 element (A116/A119's consumer test);
  anyD4     : the best of the eight D4 images (sound as a kill: a packing at the node whose image
              satisfies N is killed with its image).

Read-only on A107, A116, A119, A122 and every campaign; writes results/consumer.json.
"""
from __future__ import annotations
import argparse, glob, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a125lib as G
import a116lib as A

A107R = os.path.join(A.ROOT, "attempts", "A107-shadow-gallery", "results")
D4 = ("e", "r90", "r180", "r270", "mx", "my", "diag", "anti")


def node_class(rec):
    if rec["src"] == "A57":
        return rec["nid"].split("_interior")[0]
    if rec["src"] == "A60":
        return "trump5"
    return rec["nid"].split(".")[0] if "." in rec["nid"] else rec["nid"].split("_")[0]


def tilt_dev(a_rad, b_rad):
    d = abs(math.degrees(a_rad) - math.degrees(b_rad)) % 90.0
    return min(d, 90.0 - d)


def _match(feas, nleft, nright):
    """Kuhn's augmenting paths: an injection of the left vertices into distinct right ones."""
    to = [-1] * nright
    who = [-1] * nleft

    def try_(i, seen):
        for j in feas[i]:
            if seen[j]:
                continue
            seen[j] = True
            if to[j] < 0 or try_(to[j], seen):
                to[j] = i
                who[i] = j
                return True
        return False

    for i in range(nleft):
        if not try_(i, [False] * nright):
            return None
    return who


def inside(bodies, sup, cut, r, rho, s0=None):
    """Injection of EVERY body of N (free boxes and pin cores) into distinct support squares."""
    s0 = G.S0 if s0 is None else s0
    feas, dv, tv = [], {}, {}
    for i, b in enumerate(bodies):
        row = []
        if b.kind == "free":
            ax, ay, at = b.anchor
            rad, trad = r, rho
        else:
            ax, ay = b.ax[0] + b.ax[1] * s0, b.ay[0] + b.ay[1] * s0
            at, rad, trad = 0.0, b.hh, 1e-6
        for j, (x, y, t) in enumerate(sup):
            d = max(abs(x - ax), abs(y - ay))
            td = tilt_dev(t, at)
            dv[(i, j)], tv[(i, j)] = d, td
            if d > rad or td > trad:
                continue
            if cut is not None and b.kind == "free" and abs(at) > 1e-9:
                if (math.degrees(t) % 90.0) < cut:
                    continue
            row.append(j)
        feas.append(row)
    who = _match(feas, len(bodies), len(sup))
    if who is None:
        return False, None, None
    free_i = [i for i, b in enumerate(bodies) if b.kind == "free"]
    dmax = max(dv[(i, who[i])] for i in free_i)
    tmax = max(tv[(i, who[i])] for i in free_i)
    return True, dmax, tmax


def pin_eligible(bodies, sup, s0=None):
    """can the |P| PIN cores alone be filled by distinct squares of the support (centre inside the
    delta-core, tilt 0 mod 90)?  This is the gate a trump5 (5-pin) node has to pass to be testable
    against a k6_07 / k6_21 (6-pin) N at all: the sixth cell must be occupied in the support."""
    s0 = G.S0 if s0 is None else s0
    pins = [b for b in bodies if b.kind == "pin"]
    feas = []
    for b in pins:
        ax, ay = b.ax[0] + b.ax[1] * s0, b.ay[0] + b.ay[1] * s0
        feas.append([j for j, (x, y, t) in enumerate(sup)
                     if max(abs(x - ax), abs(y - ay)) <= b.hh and tilt_dev(t, 0.0) <= 1e-6])
    return _match(feas, len(pins), len(sup)) is not None


def blocker(bodies, sup, s0=None):
    """the body of N whose nearest support square is furthest OUTSIDE its own tolerance, measured
    as (centre excess / halfwidth) for a pin and (centre dev, tilt dev) for a free box."""
    s0 = G.S0 if s0 is None else s0
    worst = None
    for b in bodies:
        if b.kind == "pin":
            ax, ay = b.ax[0] + b.ax[1] * s0, b.ay[0] + b.ay[1] * s0
            cand = [(max(abs(x - ax), abs(y - ay)), tilt_dev(t, 0.0)) for (x, y, t) in sup]
            d, td = min(cand, key=lambda z: (z[0] / b.hh, z[1]))
            score = max(d / b.hh, td / 1e-6)
        else:
            ax, ay, at = b.anchor
            cand = [(max(abs(x - ax), abs(y - ay)), tilt_dev(t, at)) for (x, y, t) in sup]
            d, td = min(cand, key=lambda z: z[0])
            score = d
        if worst is None or score > worst[0]:
            worst = (score, b.name, b.kind, round(d, 5), round(td, 4))
    return dict(body=worst[1], kind=worst[2], d_centre=worst[3], d_tilt_deg=worst[4])


def min_radius(bodies, cfg, f, cut, rho, ops=D4, rmax=1.6, tol=2e-3):
    """the smallest centre radius r at which SOME D4 image of the support matches every body of N
    (free boxes at tilt half-width rho, pin cores at their own halfwidth) -- A116 sec 7's distance
    census, done as a bisection on r.  None if no r <= rmax works."""
    sups = [[tuple(f[op](x, y, t)) for (x, y, t) in cfg] for op in ops]

    def ok(r):
        return any(inside(bodies, s, cut, r, rho)[0] for s in sups)

    if not ok(rmax):
        return None
    lo, hi = 0.0, rmax
    while hi - lo > tol:
        m = 0.5 * (lo + hi)
        if ok(m):
            hi = m
        else:
            lo = m
    return hi


def certified_from(pattern, samp_extra):
    out, seen = [], set()
    for p in sorted(glob.glob(pattern)):
        if "_smoke" in p:
            continue
        for line in open(p, encoding="utf-8"):
            d = json.loads(line)
            cid = "%s_%s_r%.2f_rho%g" % (d["tag"], d["cls"], d["r"], d["rho"])
            hits = (samp_extra.get(cid) or d.get("sampling") or {}).get("hits", 1)
            if d["tree"]["dead"] and hits == 0 and not d["trump"]["inside"] and cid not in seen:
                seen.add(cid)
                out.append(dict(id=cid, tag=d["tag"], cls=d["cls"], r=d["r"], rho=d["rho"],
                                cut=d["cut"], L=d["L"], P=d["P"],
                                certified_min=d["tree"]["certified_min"],
                                seconds=d["seconds_tree"]))
    return sorted(out, key=lambda q: (-q["r"], -q["rho"]))


def load_nodes():
    """EVERY alive node of A107's input (Part I and the k0 Part II), with its LP-support
    representative -- the shadow-explained ones and the unexplained ones alike, so that the
    denominator is A107's own (A60/trump5: 325 = 283 explained + 42 unexplained)."""
    rows = []
    for snf, exf, part in (("shadow_nodes.json", "extract.json", "I"),
                           ("shadow_nodes_k0.json", "extract_k0.json", "II")):
        sn = json.load(open(os.path.join(A107R, snf), encoding="utf-8"))
        ex = json.load(open(os.path.join(A107R, exf), encoding="utf-8"))["nodes"]
        shadow_of = {}
        for tag, recs in sn.items():
            for rec in recs:
                shadow_of[(rec["src"], rec["nid"])] = tag
        for n in ex:
            if not n.get("cfg"):
                continue
            key = (n["src"], n["nid"])
            rows.append(dict(part=part, shadow=shadow_of.get(key, "unexplained"),
                             src=n["src"], nid=n["nid"], level=n.get("level"),
                             cls=node_class(n), struct_op=n.get("struct_op") or "e",
                             struct_op_raw=n.get("struct_op"), cfg=n["cfg"]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", default="S33,S38")
    a = ap.parse_args()
    nodes = load_nodes()
    f = dict(A.L11.d4_ops(G.S0))
    sp = os.path.join(G.RES, "sampling.json")
    samp_extra = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
    certified = []
    for tag in a.tags.split(","):
        certified += certified_from(os.path.join(G.RES, "grid_%s*.jsonl" % tag), samp_extra)
    out = dict(s0=G.S0, n_nodes=len(nodes),
               n_by_src={s: sum(1 for q in nodes if q["src"] == s) for s in ("A57", "A60", "A61")},
               certified=certified, per_N=[])
    for c in certified:
        bodies, nv, s_sh, P = G.build_bodies125(c["tag"], c["r"], c["rho"], anchor_side=G.S0,
                                                pin_slack=G.PIN_SLACK, tilt_floor_deg=c["cut"])
        rows = []
        for q in nodes:
            best = None
            for op in D4:
                sup = [tuple(f[op](x, y, t)) for (x, y, t) in q["cfg"]]
                ins, dmax, tmax = inside(bodies, sup, c["cut"], c["r"], c["rho"])
                if ins and (best is None or dmax < best[1]):
                    best = (op, dmax, tmax)
            sup = [tuple(f[q["struct_op"]](x, y, t)) for (x, y, t) in q["cfg"]]
            ins0, d0, t0 = inside(bodies, sup, c["cut"], c["r"], c["rho"])
            elig = any(pin_eligible(bodies, [tuple(f[op](x, y, t)) for (x, y, t) in q["cfg"]])
                       for op in D4)
            q["_pin_eligible"] = elig
            q["_blocker"] = blocker(bodies, [tuple(f[best[0] if best else q["struct_op"]](x, y, t))
                                             for (x, y, t) in q["cfg"]])
            if ins0 or best:
                rows.append(dict(part=q["part"], shadow=q["shadow"], src=q["src"], nid=q["nid"],
                                 level=q["level"], cls=q["cls"], struct_op=q["struct_op_raw"],
                                 inside_structop=bool(ins0),
                                 dmax=None if d0 is None else round(d0, 4),
                                 tmax=None if t0 is None else round(t0, 3),
                                 inside_anyD4=bool(best), anyD4_op=(best[0] if best else None),
                                 anyD4_dmax=(round(best[1], 4) if best else None),
                                 anyD4_tmax=(round(best[2], 3) if best else None)))
        n_elig = sum(1 for q in nodes if q.get("_pin_eligible"))
        n_elig_a60 = sum(1 for q in nodes if q.get("_pin_eligible") and q["src"] == "A60")
        blk = {}
        for q in nodes:
            b = (q.get("_blocker") or {}).get("body")
            blk[b] = blk.get(b, 0) + 1
        n_so = sum(1 for q in rows if q["inside_structop"])
        n_d4 = sum(1 for q in rows if q["inside_anyD4"])
        a60 = [q for q in rows if q["src"] == "A60" and q["inside_anyD4"]]
        a57 = [q for q in rows if q["src"] == "A57" and q["inside_anyD4"]]
        a61 = [q for q in rows if q["src"] == "A61" and q["inside_anyD4"]]
        gal = [q for q in rows if q["shadow"] in ("S33", "S34", "S35", "S38", "K19")]
        e = dict(N=c, boxes=[b.name for b in bodies if b.kind == "free"],
                 pins=[b.name for b in bodies if b.kind == "pin"],
                 inside_structop=n_so, inside_anyD4=n_d4,
                 pin_eligible=n_elig, pin_eligible_A60=n_elig_a60,
                 blocker_histogram=dict(sorted(blk.items(), key=lambda z: -z[1])),
                 a60_trump5_inside=len(a60), a57_inside=len(a57), a61_inside=len(a61),
                 by_shadow={t: sum(1 for q in rows if q["inside_anyD4"] and q["shadow"] == t)
                            for t in sorted({q["shadow"] for q in rows if q["inside_anyD4"]})},
                 gallery_rows=gal, nodes=rows[:400])
        out["per_N"].append(e)
        print("%s/%s r=%.2f rho=%4.1f: inside  struct_op %3d | anyD4 %3d   "
              "(A60/trump5 %3d, A57 %3d, A61 %3d)  pin-eligible %d (A60 %d)  shadows %s"
              % (c["tag"], c["cls"], c["r"], c["rho"], n_so, n_d4, len(a60), len(a57), len(a61),
                 n_elig, n_elig_a60, e["by_shadow"]), flush=True)
        print("    blockers (the body of N whose nearest support square is furthest outside its "
              "own tolerance): %s" % list(e["blocker_histogram"].items())[:6])
        for q in gal:
            print("    gallery %-4s %-5s %-16s struct_op=%s  inside_structop=%s inside_anyD4=%s "
                  "(op %s, dmax %s, tmax %s)"
                  % (q["shadow"], q["src"], q["nid"], q["struct_op"], q["inside_structop"],
                     q["inside_anyD4"], q["anyD4_op"], q["anyD4_dmax"], q["anyD4_tmax"]))
    # -- the distance census: what radius would be needed (A116 sec 7)
    RHOS = (5.0, 10.0, 20.0, 40.0)
    LADDER = (0.05, 0.1, 0.2, 0.3, 0.5, 1.0)
    out["census"] = []
    for tag in sorted({c["tag"] for c in certified}):
        biggest = max([c for c in certified if c["tag"] == tag], key=lambda q: (q["r"], q["rho"]))
        bodies, nv, s_sh, P = G.build_bodies125(tag, biggest["r"], max(RHOS), anchor_side=G.S0,
                                                pin_slack=G.PIN_SLACK)
        per = {}
        for rho in RHOS:
            bd, _, _, _ = G.build_bodies125(tag, biggest["r"], rho, anchor_side=G.S0,
                                            pin_slack=G.PIN_SLACK, tilt_floor_deg=biggest["cut"])
            rr = []
            for q in nodes:
                r = min_radius(bd, q["cfg"], f, biggest["cut"], rho)
                if r is not None:
                    rr.append(dict(src=q["src"], nid=q["nid"], shadow=q["shadow"], r=round(r, 4)))
            per[rho] = dict(
                counts={"r<=%g" % t: sum(1 for z in rr if z["r"] <= t) for t in LADDER},
                counts_A60={"r<=%g" % t: sum(1 for z in rr if z["r"] <= t and z["src"] == "A60")
                            for t in LADDER},
                nearest=sorted(rr, key=lambda z: z["r"])[:12])
        out["census"].append(dict(tag=tag, cls=G.SHADOWS[tag]["cls"], per_rho=per,
                                  n_nodes=len(nodes)))
        print("\ndistance census, %s (%s): minimal centre radius r for a full match, by tilt "
              "half-width" % (tag, G.SHADOWS[tag]["cls"]))
        for rho in RHOS:
            print("   rho=%4.1f deg: %s   (A60/trump5 only: %s)"
                  % (rho, per[rho]["counts"], per[rho]["counts_A60"]))
            print("      nearest: %s" % [(z["shadow"], z["src"], z["nid"], z["r"])
                                         for z in per[rho]["nearest"][:5]])
    with open(os.path.join(G.RES, "consumer.json"), "w", encoding="utf-8") as fo:
        json.dump(out, fo, indent=1)
    print("\nwrote results/consumer.json  (%d alive nodes scanned: %s)"
          % (len(nodes), out["n_by_src"]))


if __name__ == "__main__":
    main()
