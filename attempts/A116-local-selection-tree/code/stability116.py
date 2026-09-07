"""A116 -- the PI's route: stability radii of the minimum's contacts.

For S07 (trump5 frame) and S02 (k5_11 frame), for every pair of bodies of L u P:
  * contact pairs (SAT gap ~ 0 at the exact minimum): the minimum's selection(s) (a flush pair
    has two: either square's edge normal), the riding vertex's tangential coordinate tau on the
    owner's edge, the slack 1/2 - |tau| to the nearer end (mechanism (a): the vertex reaching the
    end of its edge), the relative-tilt margin to a multiple of 90 deg (mechanism (b): a different
    vertex/edge coming into play), the first-order estimate of the forced radius, and the
    RIGOROUS forced radius: the largest per-square delta (tilt half-width rho = kappa*delta) such
    that interval bisection over the pair's 6-D pose box proves that every disjoint configuration
    satisfies the minimum's selection (the row of the chain is then valid on the whole box).
  * non-contact pairs: the far radius = the largest delta at which one selection's gap stays
    >= 0 on the whole box (the pair can never come into contact: no row, no branch).
Then N_PI = the per-square box at the minimum of the chain contacts' forced radii, and the single
leaf (the minimum's selections, flush pairs as disjunctions) is evaluated by the tree over N_PI.

Writes results/stability_<tag>.json and notes/stability_table.md.
"""
from __future__ import annotations
import json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a116lib as A

KAPPAS = (100.0, 0.0)          # rho_deg = kappa * delta  (0.1 <-> 10 deg), and position-only


def pair_analysis(tag, cls, kappa, s_lo=A.S_LO, s_hi=A.S_HI_DEFAULT, pin_slack=A.PIN_SLACK, log=print):
    bodies, nv, s_sh, P = A.build_bodies(tag, cls, 0.0, 0.0, anchor_side=A.S0, pin_slack=pin_slack)
    # contact geometry is read at the EXACT minimum (anchor s*), radii around the s0 anchor
    _, Pexact, slots, free = A.anchored(tag, s_sh)
    ss = A.shadow_selections(bodies, Pexact)
    rows = []
    nb = len(bodies)
    for i in range(nb):
        for j in range(i + 1, nb):
            bi, bj = bodies[i], bodies[j]
            if bi.kind == "pin" and bj.kind == "pin":
                # two axis-aligned slack cores: the selection is the slot geometry (forced at any delta)
                pass
            rec = dict(pair="%s|%s" % (bi.name, bj.name), kinds=(bi.kind, bj.kind))
            t0 = time.time()
            if (i, j) in ss:
                sels = ss[(i, j)]
                geo = A.contact_geometry(bi, bj, Pexact, sels[0])
                rec.update(contact=True, selections=[list(s) for s in sels], geometry=geo)
                # first-order estimate: tangential drift of the riding vertex <= 2 delta (|t_x|+|t_y|) + rho (1/sqrt2)(1 + 1)
                (o, k, eps) = sels[0]
                bw = bi if o == 0 else bj
                a = A.axis(Pexact[bw.name][2], k); tvec = (-a[1], a[0])
                drift_per_delta = 2.0 * (abs(tvec[0]) + abs(tvec[1])) + 2.0 * math.radians(kappa) / math.sqrt(2.0)
                if bi.kind == "pin" or bj.kind == "pin":
                    drift_per_delta = (abs(tvec[0]) + abs(tvec[1])) + math.radians(kappa) / math.sqrt(2.0)
                rec["estimate"] = (geo["slack"] / drift_per_delta) if drift_per_delta > 0 else float("inf")

                def test(d):
                    box = A.pair_box(bi, bj, d, math.radians(kappa * d), s_lo, s_hi)
                    ok, n = A.forced_test(box, [tuple(s) for s in sels])
                    return ok
                if bi.kind == "pin" and bj.kind == "pin":
                    rec["forced_radius"] = float("inf")
                else:
                    rec["forced_radius"] = A.radius_search(test, dmax=0.4, tol=2e-3)
            else:
                rec.update(contact=False)
                pi_, pj_ = Pexact[bi.name], Pexact[bj.name]
                rec["gap_at_minimum"] = A.sat_gap(pi_[:2], pi_[2], pj_[:2], pj_[2])

                def test(d):
                    return A.far_test(A.pair_box(bi, bj, d, math.radians(kappa * d), s_lo, s_hi))
                rec["far_radius"] = A.radius_search(test, dmax=0.4, tol=2e-3)
            rec["seconds"] = round(time.time() - t0, 2)
            rows.append(rec)
            log("  %-22s %s %s" % (rec["pair"], "contact" if rec["contact"] else "far",
                                   ("forced r=%.3f (est %.3f, slack %.3f, dtheta %.1f)" % (rec["forced_radius"], rec["estimate"], rec["geometry"]["slack"], rec["geometry"]["dtheta_margin_deg"]))
                                   if rec["contact"] else ("far r=%.3f (gap %.4f)" % (rec["far_radius"], rec["gap_at_minimum"]))))
    return rows, bodies, ss


def chain_pairs(tag):
    """the load-bearing chain contacts (A110 sec 2): the rows the kill needs."""
    if tag == "S07":
        return {"f0|BL(0,1)", "f0|f2", "f2|TR(0,0)", "f0|f4", "f4|BR(0,0)"}
    return {"f1|BL(0,1)", "f1|f2", "f2|f3", "f3|BR(0,1)", "BR(0,1)|BR(0,0)", "f1|TL(0,0)", "f1|f3"}


def main():
    out = {}
    logp = os.path.join(A.LOGS, "stability.log")

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    for tag, cls in (("S07", "trump5"), ("S02", "k5_11")):
        out[tag] = {}
        for kappa in KAPPAS:
            log("=== %s / %s  kappa = %g (rho_deg = kappa * delta)" % (tag, cls, kappa))
            rows, bodies, ss = pair_analysis(tag, cls, kappa, log=log)
            cp = chain_pairs(tag)
            chain_r = min((r["forced_radius"] for r in rows if r["contact"] and r["pair"] in cp), default=None)
            all_contact_r = min((r["forced_radius"] for r in rows if r["contact"]), default=None)
            far_r = min((r["far_radius"] for r in rows if not r["contact"]), default=None)
            lim = min((r for r in rows if r["contact"] and r["pair"] in cp), key=lambda r: r["forced_radius"])
            log("  chain-contact min forced radius %.3f (limiter %s); all contacts %.3f; far pairs %.3f"
                % (chain_r, lim["pair"], all_contact_r, far_r))
            out[tag][str(kappa)] = dict(rows=rows, chain_min_forced_radius=chain_r, limiter=lim["pair"],
                                        all_contacts_min_forced_radius=all_contact_r, far_min_radius=far_r,
                                        chain_pairs=sorted(cp))
    with open(os.path.join(A.RES, "stability.json"), "w") as f:
        json.dump(out, f, indent=1)
    # markdown table
    lines = ["# Stability radii of the minimum's contacts (A116, PI route)", "",
             "delta = per-square centre box half-width; rho = kappa * delta (kappa = 100 deg/unit: 0.1 <-> 10 deg) or rho = 0.",
             "forced radius = largest delta at which interval bisection proves the minimum's selection on every disjoint",
             "configuration of the pair's box (rigorous); estimate = tangential slack / drift rate (first order).",
             "Pins: A57 slack cores (half-width 0.00707), side in [3.82, s0 + 0.02].", ""]
    for tag in out:
        for kappa in out[tag]:
            d = out[tag][kappa]
            lines.append("## %s, kappa = %s  -- chain min forced radius %.3f (limiter %s), all contacts %.3f, far pairs %.3f" %
                         (tag, kappa, d["chain_min_forced_radius"], d["limiter"], d["all_contacts_min_forced_radius"], d["far_min_radius"]))
            lines.append("")
            lines.append("| pair | chain | type | owner/axis/sign | tau | slack to end | dtheta margin | estimate | forced radius | far radius |")
            lines.append("|---|---|---|---|---|---|---|---|---|---|")
            for r in d["rows"]:
                if r["contact"]:
                    g = r["geometry"]
                    typ = "flush" if g["flush"] else "vertex-on-edge"
                    lines.append("| %s | %s | %s | %s/e%d/%+d | %.3f | %.3f | %.1f | %.3f | **%.3f** | - |" % (
                        r["pair"], "yes" if r["pair"] in d["chain_pairs"] else "", typ, g["owner"], g["k"] + 1, g["eps"],
                        g["tau"], g["slack"], g["dtheta_margin_deg"], r["estimate"], r["forced_radius"]))
                else:
                    lines.append("| %s |  | non-contact (gap %.3f) |  |  |  |  |  | - | %.3f |" % (r["pair"], r["gap_at_minimum"], r["far_radius"]))
            lines.append("")
    with open(os.path.join(A.BASE, "notes", "stability_table.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log("stability done")


if __name__ == "__main__":
    main()
