"""A113 T2 -- the LP dual supports of the k0_00 ALIVE / FAIL cells: drawn, and classified by
A107's method (slot snapping + structure match against the 53-shadow gallery).

Conventions from docs/residue_map/gen_a57_lp.py, adapted to k0_00's hypothesis: no pins, one
conditioned core (or 2/4/6 cores for the S2-S5 corner nodes), so the whole shadow is
  cores  +  the LP dual-support placements (packing entries with dual weight y > 0).

READ-ONLY on A38/A85/A99/A107; writes only under attempts/A113-k0-manifold-distance/.
"""
import os, sys, json, glob, math, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import manifold as M                                                        # noqa: E402
sys.path.insert(0, os.path.join(M.ROOT, "attempts", "A107-shadow-gallery", "code"))
import shadowlib as L                                                       # noqa: E402

S = M.S0
RES = M.RES
SVG = os.path.join(M.BASE, "results", "svg")
os.makedirs(SVG, exist_ok=True)

SIMPLE = 1e-2          # eta of a pose below this = a SIMPLE placement (on the manifold)
NEAR = (0.05, 0.10, 0.20)
SHADOWS = json.load(open(os.path.join(M.ROOT,
                    "attempts/A107-shadow-gallery/results/shadows.json"), encoding="utf-8"))


def core_pose(c):
    b = c.get("box") or {}
    fl = c.get("float", {})
    cx = 0.5 * (b["x0"] + b["x1"]) if "x0" in b else float(fl.get("kx", 0))
    cy = 0.5 * (b["y0"] + b["y1"]) if "y0" in b else float(fl.get("ky", 0))
    th = 0.5 * (b.get("th0", 0.0) + b.get("th1", 0.0)) if "th0" in b \
        else float(fl.get("theta_deg", 0.0))
    return (cx, cy, th)


def load(p):
    d = json.load(open(p, encoding="utf-8"))
    cores = [core_pose(c) for c in (d.get("hyp") or {}).get("cores", [])]
    pk = [(float(q["cx"]), float(q["cy"]), math.degrees(float(q["theta"])) % 90.0,
           float(q.get("y", 0.0))) for q in d.get("packing", [])]
    return d, cores, pk


def slotset(poses):
    """A107 snap: (sorted slot names, n free)."""
    sl, nf = [], 0
    for (x, y, th) in poses:
        nm = L.snap(x, y, math.radians(th), S)
        if nm:
            sl.append(nm)
        else:
            nf += 1
    return tuple(sorted(set(sl))), nf


def d4_slotsets(poses):
    out = set()
    for nm, f in L.d4_ops(S):
        q = [f(x, y, math.radians(th)) for (x, y, th) in poses]
        q = [(a, b, math.degrees(c)) for (a, b, c) in q]
        out.add(slotset(q))
    return out


def _trump_slots():
    """the slot set of a Trump image's five simple squares (the trump5 skeleton)."""
    W = json.load(open(os.path.join(M.ROOT, "attempts/A85-k0-route/results/witnesses_k0_00.json"),
                       encoding="utf-8"))["images"]["g0"]["squares"]
    ps = [(q["cx_f"], q["cy_f"], q["theta_deg"]) for q in W]
    return slotset(ps)[0]


TRUMP = _trump_slots()


def shadow_match(poses):
    """structural match of the support's slot set against the A107 gallery, over the D4 orbit.
    exact  = some image's slot set equals the shadow's;
    subset = some image's slot set is contained in the shadow's (the LP support is a partial
             skeleton of that shadow);
    best   = max Jaccard over shadows and over D4."""
    mine = [sl for (sl, nf) in d4_slotsets(poses) if sl]
    exact, subset, best = [], [], (0.0, None, None)
    for sh in SHADOWS:
        ss = set(sh["slots"])
        for sl in mine:
            s = set(sl)
            j = len(s & ss) / float(len(s | ss)) if (s | ss) else 0.0
            if j > best[0]:
                best = (j, sh["id"], round(sh["s"], 6))
            if s == ss and sh["id"] not in exact:
                exact.append(sh["id"])
            elif s and s <= ss and sh["id"] not in subset:
                subset.append(sh["id"])
    # Trump itself
    tj = 0.0
    for sl in mine:
        s = set(sl)
        tj = max(tj, len(s & set(TRUMP)) / float(len(s | set(TRUMP))))
    return dict(exact=exact, subset=subset[:6], n_subset=len(subset),
                best_jaccard=round(best[0], 3), best_shadow=best[1], best_s=best[2],
                trump_jaccard=round(tj, 3))


def classify(cores, pk, ythr=0.5):
    sup = [q for q in pk if q[3] > ythr]
    frac = [q for q in pk if q[3] > 0.02]
    poses = [(x, y, t) for (x, y, t, _) in sup]
    allp = cores + poses
    etas = [M.eta_point(x, y, t)[0] for (x, y, t) in allp]
    slots, nfree = slotset(allp)
    return dict(n_placements=len(pk), n_integral_support=len(sup), n_frac_support=len(frac),
                sum_y=sum(q[3] for q in pk),
                integral=all(q[3] < 1e-6 or q[3] > 1 - 1e-6 for q in pk),
                n_simple=sum(1 for e in etas if e < SIMPLE),
                n_near={str(t): sum(1 for e in etas if e <= t) for t in NEAR},
                eta_min=min(etas) if etas else None,
                etas=sorted(round(e, 4) for e in etas),
                a107_slots=list(slots), a107_nfree=nfree,
                shadow_hits=shadow_match(allp))


# ---------------------------------------------------------------------------- drawing
PX = 110


def svg_panel(ox, oy, title, sub, cores, pk, ythr=0.02):
    o = ['<text x="%.1f" y="%.1f" font-size="12" font-weight="bold" fill="#111">%s</text>'
         % (ox, oy - S * PX - 24, title),
         '<text x="%.1f" y="%.1f" font-size="9.5" fill="#555">%s</text>'
         % (ox, oy - S * PX - 10, sub),
         '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" stroke="#000" '
         'stroke-width="2"/>' % (ox, oy - S * PX, S * PX, S * PX)]
    # the k >= 1 manifold: the 36 corner-lattice cells
    for nm, (x, y) in M.LAT_ITEMS:
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#cfe3f7" '
                 'stroke-width="1"/>' % (ox + (x - 0.5) * PX, oy - (y + 0.5) * PX, PX, PX))
        o.append('<circle cx="%.1f" cy="%.1f" r="1.6" fill="#7fb3e0"/>'
                 % (ox + x * PX, oy - y * PX))

    def poly(x, y, th, fill, op, stroke, sw=1.0):
        c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
        pts = " ".join("%.2f,%.2f" % (ox + (x + 0.5 * (dx * c - dy * s_)) * PX,
                                      oy - (y + 0.5 * (dx * s_ + dy * c)) * PX)
                       for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)))
        return ('<polygon points="%s" fill="%s" fill-opacity="%.3f" stroke="%s" '
                'stroke-width="%.1f"/>' % (pts, fill, op, stroke, sw))
    ymax = max([q[3] for q in pk] or [1.0])
    for (x, y, t, w) in pk:
        if w <= ythr:
            continue
        e = M.eta_point(x, y, t)[0]
        col = "#c0392b" if e < SIMPLE else ("#e08214" if e <= 0.2 else "#4a4a4a")
        o.append(poly(x, y, t, col, 0.18 + 0.5 * (w / ymax), col, 1.0))
    for (x, y, t) in cores:
        o.append(poly(x, y, t, "#000000", 0.0, "#000000", 2.4))
    return o


def main():
    targets = []
    # --- A38 level 1: the ALIVE(LP) cells, the FAILED-CERT cells, and every tau >= budget cell
    l1 = json.load(open(os.path.join(M.ROOT, "attempts/A38-root-power/results/l1_a38.json"),
                        encoding="utf-8"))
    bud = l1["budget"]
    for r in l1["matrix"]:
        p = os.path.join(M.ROOT, "attempts/A38-root-power/results/l1_nodes",
                         "node_%03d.json" % r["idx"])
        if not os.path.exists(r"%s" % p):
            continue
        kl = r.get("kill_label")
        v = ("ALIVE" if r["status"] == "alive(LP)" else
             "FAIL" if kl == "kill(FAILED-CERT)" else
             "PASS" if kl == "kill(certified)" else
             "KILL(LP)" if r["status"] == "dead(T1)" else "UNDECIDED")
        eta, dp, dt, nm = M.eta_box(r["box"])
        targets.append(dict(src="A38-l1", cid="l1_%03d" % r["idx"], path=p, verdict=v,
                            tau=r["tau"], budget=bud, unkillable=r["tau"] >= bud - 1e-9,
                            eta=eta, d_pos=dp, d_tilt=dt, slot=nm,
                            lp_s=r.get("seconds")))
    # --- A85 nodes (certification-in-the-loop verdicts)
    samp = {}
    for l in open(os.path.join(M.ROOT, "attempts/A85-k0-route/results/a85_lp_samples.jsonl"),
                  encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            samp[r["tag"]] = r
    for p in sorted(glob.glob(os.path.join(
            M.ROOT, "attempts/A85-k0-route/results/nodes/k0_00/*.json"))):
        tag = os.path.basename(p)[:-5]
        r = samp.get(tag, {})
        v = r.get("verdict", "not-run")
        vv = ("PASS" if v.startswith("PASS") else "FAIL" if v.startswith("FAIL")
              else "REFUSED" if v.startswith("refused") else v.upper())
        d = json.load(open(p, encoding="utf-8"))
        es = [M.eta_box(c["box"]) for c in d["hyp"]["cores"]]
        eta, dp, dt, nm = min(es)
        targets.append(dict(src="A85", cid=tag, path=p, verdict=vv, tau=r.get("tau"),
                            budget=r.get("budget"), unkillable=False,
                            eta=eta, d_pos=dp, d_tilt=dt, slot=nm, lp_s=r.get("lp_s")))

    recs = []
    for t in targets:
        d, cores, pk = load(t["path"])
        c = classify(cores, pk)
        c.update({k: t[k] for k in
                  ("src", "cid", "verdict", "tau", "budget", "unkillable",
                   "eta", "d_pos", "d_tilt", "slot", "lp_s")})
        c["n_cores"] = len(cores)
        c["path"] = os.path.relpath(t["path"], M.ROOT).replace("\\", "/")
        recs.append(c)
    with open(os.path.join(RES, "t2_supports.jsonl"), "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")

    # ------------------------------------------------------------------ report
    o = []
    w = o.append
    w("# A113 T2 -- LP dual supports of the k0_00 ALIVE / FAIL cells\n")
    w("Shadow = hypothesis cores + LP dual support (`packing`, dual weight y > 0.5 integral).\n")
    w("A SIMPLE placement = eta(pose) < %.2g, i.e. axis-aligned on a corner-lattice cell "
      "centre.\n" % SIMPLE)
    sets = [("A38-l1 ALIVE(LP)", [r for r in recs if r["src"] == "A38-l1"
                                  and r["verdict"] == "ALIVE"]),
            ("A38-l1 FAIL (certification failed)", [r for r in recs if r["src"] == "A38-l1"
                                                    and r["verdict"] == "FAIL"]),
            ("A85 FAIL (eps_geo retries exhausted)", [r for r in recs if r["src"] == "A85"
                                                      and r["verdict"] == "FAIL"]),
            ("A38-l1 tau >= budget (un-killable at the measured LP state)",
             [r for r in recs if r["src"] == "A38-l1" and r["unkillable"]]),
            ("A38-l1 PASS (certified kill), for contrast",
             [r for r in recs if r["src"] == "A38-l1" and r["verdict"] == "PASS"]),
            ("A85 PASS, for contrast", [r for r in recs if r["src"] == "A85"
                                        and r["verdict"] == "PASS"])]
    for name, sel in sets:
        w("\n## %s (n = %d)\n" % (name, len(sel)))
        if not sel:
            continue
        w("| cell | eta(cell) | tau | support | int? | simple | <=0.20 | A107 slot set "
          "| best shadow (Jaccard @ s*) | subset-of | Trump J |")
        w("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in sorted(sel, key=lambda r: r["cid"]):
            h = r["shadow_hits"]
            w("| %s | %.4f | %s | %d/%d | %s | **%d** | %d | %s | %s | %s | %.2f |" % (
                r["cid"], r["eta"], "%.4f" % r["tau"] if r["tau"] else "-",
                r["n_integral_support"], r["n_placements"],
                "y" if r["integral"] else "n", r["n_simple"], r["n_near"]["0.2"],
                " ".join(r["a107_slots"]) or "(none)",
                ("%s %.2f @ %.4f" % (h["best_shadow"], h["best_jaccard"], h["best_s"]))
                if h["best_shadow"] else "-",
                ("%d (%s)" % (h["n_subset"], ",".join(h["subset"][:3]))) if h["n_subset"] else "-",
                h["trump_jaccard"]))
        tot = sum(r["n_simple"] for r in sel)
        w("")
        w("counts: %d cells, %d simple placements in total, %d cells with >= 1 simple placement, "
          "%d cells whose support snaps to any named slot, %d whose slot set is a SUBSET of some "
          "A107 shadow's, %d exact." % (
              len(sel), tot, sum(1 for r in sel if r["n_simple"] > 0),
              sum(1 for r in sel if r["a107_slots"]),
              sum(1 for r in sel if r["shadow_hits"]["n_subset"]),
              sum(1 for r in sel if r["shadow_hits"]["exact"])))

    # aggregate over the whole corpus
    w("\n## aggregate over every k0_00 node with LP data on disk (%d)\n" % len(recs))
    w("| verdict | n | mean simple/support | >=1 simple | >=2 simple | slot snap | subset of a "
      "shadow | median best Jaccard | median s* of best shadow |")
    w("|---|---|---|---|---|---|---|---|---|")
    import statistics as _st
    g = collections.defaultdict(list)
    for r in recs:
        g[r["verdict"]].append(r)
    for v in sorted(g):
        s = g[v]
        js = [r["shadow_hits"]["best_jaccard"] for r in s]
        ss = [r["shadow_hits"]["best_s"] for r in s if r["shadow_hits"]["best_s"]]
        w("| %s | %d | %.2f | %d | %d | %d | %d | %.2f | %s |" % (
            v, len(s), sum(r["n_simple"] for r in s) / len(s),
            sum(1 for r in s if r["n_simple"] > 0), sum(1 for r in s if r["n_simple"] > 1),
            sum(1 for r in s if r["a107_slots"]),
            sum(1 for r in s if r["shadow_hits"]["n_subset"]),
            _st.median(js), "%.4f" % _st.median(ss) if ss else "-"))
    txt = "\n".join(o) + "\n"
    open(os.path.join(M.BASE, "results", "t2_supports.md"), "w", encoding="utf-8").write(txt)

    # ------------------------------------------------------------------ drawings
    draw = ([r for r in recs if r["src"] == "A38-l1" and r["verdict"] == "ALIVE"]
            + [r for r in recs if r["src"] == "A38-l1" and r["verdict"] == "FAIL"]
            + [r for r in recs if r["src"] == "A85" and r["verdict"] == "FAIL"])
    cols = 4
    wpx = int(S * PX + 40)
    hpx = int(S * PX + 60)
    body = []
    for i, r in enumerate(draw):
        d, cores, pk = load(os.path.join(M.ROOT, r["path"]))
        ox = 20 + (i % cols) * wpx
        oy = 55 + (i // cols) * hpx + S * PX
        body += svg_panel(ox, oy, "%s  %s  eta=%.3f" % (r["cid"], r["verdict"], r["eta"]),
                          "tau %.4f / budget %s; support %d/%d; simple %d; %s"
                          % (r["tau"] or 0, r["budget"], r["n_integral_support"],
                             r["n_placements"], r["n_simple"],
                             " ".join(r["a107_slots"]) or "no slot snap"),
                          cores, pk)
    # A107 discipline: report containment and the worst pairwise SAT gap of every drawn square
    chk = []
    for r in draw:
        d, cores, pk = load(os.path.join(M.ROOT, r["path"]))
        ps = [(x, y, t) for (x, y, t, wt) in pk if wt > 0.02] + cores
        nc = sum(1 for (x, y, t) in ps if L.contained(x, y, math.radians(t), S, tol=1e-9))
        g = min([L.sat_gap(ps[i][:2], math.radians(ps[i][2]), ps[j][:2], math.radians(ps[j][2]))
                 for i in range(len(ps)) for j in range(i + 1, len(ps))] or [0.0])
        chk.append((r["cid"], len(ps), nc, g))
    with open(os.path.join(M.BASE, "results", "t2_supports.md"), "a", encoding="utf-8") as f:
        f.write("\n## drawn-panel checks (A107 discipline; the raw LP panel allows overlaps)\n\n")
        f.write("| panel | drawn squares | contained in [0,s]^2 | worst pairwise SAT gap |\n")
        f.write("|---|---|---|---|\n")
        for cid, n, nc, g in chk:
            f.write("| %s | %d | %d | %+.4f |\n" % (cid, n, nc, g))
    W = 20 + cols * wpx
    H = 60 + ((len(draw) + cols - 1) // cols) * hpx
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
           'viewBox="0 0 %d %d"><rect width="%d" height="%d" fill="#fafafa"/>'
           '<text x="20" y="26" font-size="15" font-weight="bold">A113 T2 - LP dual supports of '
           'the k0_00 ALIVE and FAIL cells (blue = the 36 corner-lattice cells = the k&gt;=1 '
           'manifold; black outline = conditioned core; red = simple placement, orange = within '
           '0.2, grey = far)</text>%s</svg>'
           % (W, H, W, H, W, H, "".join(body)))
    open(os.path.join(SVG, "k0_alive_fail_supports.svg"), "w", encoding="utf-8").write(svg)
    print(txt)
    print("svg -> results/svg/k0_alive_fail_supports.svg (%d panels)" % len(draw))


if __name__ == "__main__":
    main()
