"""A158 -- assemble every measurement into results/summary158.json and print the report tables."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
R = os.path.join(BASE, "results")


# A141's own verdict on the six PI cells, read from
# attempts/A141-polycore-lane/results/t2_a5760_s{0,1}.jsonl (verdict, lane_lb, M, M_exact).
# NEAR-MISS-OR-WORSE is the EARLY-EXIT branch (lane_lb + M_lb >= 2 at the 8,000-pose screen, so
# the covers were skipped and M_exact is false) -- not the certified NEAR-MISS.
A141_VERDICT = {
    ("c0_Y0076", "TL(0,0)"): ("UNDECIDED", 0, 1, True),
    ("c0_Y0787", "BR(0,1)"): ("NEAR-MISS-OR-WORSE", 1, 1, False),
    ("c0_Y0959", "TR(0,1)"): ("UNDECIDED", 1, 1, True),
    ("k5_11_interior_Y0130", "TR(0,0)"): ("NEAR-MISS-OR-WORSE", 1, 1, False),
    ("k5_11_interior_Y0147", "TR(0,0)"): ("NEAR-MISS-OR-WORSE", 1, 1, False),
    ("k5_11_interior_Y1110", "TR(0,0)"): ("UNDECIDED", 1, 1, True),
}


def jl(name):
    p = os.path.join(R, name)
    if not os.path.exists(p):
        return []
    out = []
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except Exception:                                      # noqa: BLE001
                pass
    return out


def jf(name):
    p = os.path.join(R, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def main():
    pop = jf("pop158.json")
    recs = jf("recs158.json")
    alive_by = {}
    for v in recs.values():
        k = v["src"] + "/" + v["cls"]
        alive_by[k] = alive_by.get(k, 0) + 1
    pop["alive_by_src_cls"] = alive_by
    top = jl("top158.jsonl")
    xo = jl("xover158_tt.jsonl") + jl("xover158.jsonl") + jl("xover158_gap.jsonl")
    no = jl("no158.jsonl")
    pr = jl("pair158.jsonl")

    # ---- YES side, best over tilt, per (nid, slot)
    yes = {}
    for d in xo:
        if d.get("error"):
            continue
        k = (d["nid"], d["slot"])
        cur = yes.setdefault(k, dict(nid=d["nid"], slot=d["slot"], cls=d.get("cls"),
                                     src=d.get("src"), level=d.get("level"),
                                     n_free=d.get("n_free"), n_meeting=d.get("n_meeting"),
                                     by_tt={}))
        for row in d.get("rows", []):
            cur["by_tt"][str(row["tt"])] = row["r_yes"]
        cur["n_free"] = max(cur.get("n_free") or 0, d.get("n_free") or 0)
    for v in yes.values():
        v["r_yes_at_tt0"] = v["by_tt"].get("0.0", v["by_tt"].get("0"))
        v["max_tt_alive"] = max([float(t) for t, r in v["by_tt"].items() if r is not None and
                                 r >= 0.0], default=None)
        v["yes_closable_at_PI_box"] = bool(v["by_tt"].get("10.0", -1.0) is not None
                                           and (v["by_tt"].get("10.0", -1.0) or -1.0) >= 0.10)

    # ---- the fast YES screen at the PI box (covers cells the bisection did not reach)
    ys = jl("yesscreen158.jsonl") + jl("yesscreen_pop158.jsonl")
    screen = {}
    for d in ys:
        if d.get("error"):
            continue
        screen[(d["nid"], d["slot"])] = d
        k = (d["nid"], d["slot"])
        cur = yes.setdefault(k, dict(nid=d["nid"], slot=d["slot"], cls=d.get("cls"),
                                     src=d.get("src"), level=d.get("level"), by_tt={}))
        cur["screen_refuted_at_PI_box"] = bool(d.get("yes_refuted"))
        cur["screen_pieces"] = d.get("pieces")

    # ---- the CERTIFYING YES cover, where it was bought (overrides the screen)
    for d in jl("yescert158.jsonl"):
        k = (d["nid"], d["slot"])
        cur = yes.setdefault(k, dict(nid=d["nid"], slot=d["slot"], by_tt={}))
        cur.setdefault("cover", []).append(
            dict(piece=d["piece"], lane_ub=d["lane_ub"], M=d["M"],
                 total_meeters=d["total_meeters"], kill=d["kill"], cert=d.get("cert")))
    for v in yes.values():
        cov = v.get("cover")
        if cov:
            # the YES child is dead only if EVERY tilt piece of S closes (S is their union)
            v["yes_certified_dead"] = all(c["kill"] for c in cov) and len(cov) >= 2
            v["cover_lane_ub"] = max((c["lane_ub"] if c["lane_ub"] is not None else 9)
                                     for c in cov)
            v["cover_M"] = max((c["M"] if c["M"] is not None else 9) for c in cov)

    # ---- NO side, per (nid, slot): kill at the PI box, and the thresholds
    no_by = {}
    for d in no:
        if d.get("error") or d.get("tau") is None:
            continue
        k = (d["nid"], d["slot"])
        e = no_by.setdefault(k, dict(nid=d["nid"], slot=d["slot"], cls=d.get("cls"),
                                     src=d.get("src"), level=d.get("level"),
                                     tau0=d.get("tau0"), budget=d.get("budget"), runs=[]))
        e["runs"].append(dict(r=d["r"], tt=d["tt"], tau=d["tau"], eta=d["eta"],
                              kill=d["kill"], secs=d["secs"], cert=d.get("cert"),
                              converged=d.get("converged"),
                              control=bool(d.get("control") or d["r"] < 0)))
    for e in no_by.values():
        ctl = [x for x in e["runs"] if x["control"]]
        e["tau_control"] = ctl[0]["tau"] if ctl else None
        e["control_kills"] = bool(ctl and ctl[0]["kill"])
        e["runs"] = [x for x in e["runs"] if not x["control"]]
        pi = [x for x in e["runs"] if abs(x["r"] - 0.10) < 1e-12 and abs(x["tt"] - 10.0) < 1e-12]
        # a kill counts for the SPLIT only if the same exact-core re-solve WITHOUT the NoFam does
        # not already kill (and only if a control was run at all)
        e["kill_at_PI_box"] = bool(pi and pi[0]["kill"] and not e["control_kills"])
        e["kill_needs_control"] = bool(pi and pi[0]["kill"] and not ctl)
        e["tau_at_PI_box"] = pi[0]["tau"] if pi else None
        e["eta_at_PI_box"] = pi[0]["eta"] if pi else None
        e["cert"] = next((x["cert"] for x in e["runs"] if x.get("cert")), None)
        kr = [x["r"] for x in e["runs"] if x["kill"] and abs(x["tt"] - 10.0) < 1e-12]
        nr = [x["r"] for x in e["runs"] if not x["kill"] and abs(x["tt"] - 10.0) < 1e-12]
        e["r_no_kill_min"] = min(kr) if kr else None
        e["r_no_nokill_max"] = max(nr) if nr else None
        kt = [x["tt"] for x in e["runs"] if x["kill"] and abs(x["r"] - 0.10) < 1e-12]
        nt = [x["tt"] for x in e["runs"] if not x["kill"] and abs(x["r"] - 0.10) < 1e-12]
        e["tt_no_kill_min"] = min(kt) if kt else None
        e["tt_no_nokill_max"] = max(nt) if nt else None

    cells = sorted(set(list(yes) + list(no_by)))
    table = []
    for k in cells:
        y, n = yes.get(k, {}), no_by.get(k, {})
        j = next((t for t in top if (t["nid"], t["slot"]) == k), {})
        # the YES child is DEAD at the PI box only if the bisection says the closable radius
        # reaches 0.10 at tt = 10 AND the fast screen did not realise a counterexample
        # the YES child is DEAD only when the CERTIFYING cover says so (LANE = 0 AND M = 0 on
        # both tilt pieces).  Where no cover was bought, the screen decides whether one was even
        # worth buying: a refuted screen is a sound "not dead", an unrefuted screen is UNDECIDED.
        if y.get("yes_certified_dead") is not None:
            yd = bool(y["yes_certified_dead"])
            ystate = "dead" if yd else "cover: LANE<=%s M=%s" % (y.get("cover_lane_ub"),
                                                                 y.get("cover_M"))
        elif y.get("screen_refuted_at_PI_box") or (
                y.get("by_tt", {}).get("10.0", -1.0) or -1.0) < 0.10:
            yd, ystate = False, "REFUTED"
        else:
            yd, ystate = False, "UNDECIDED (cover not bought)"
        nd = bool(n.get("kill_at_PI_box"))
        table.append(dict(nid=k[0], slot=k[1], cls=y.get("cls") or n.get("cls") or j.get("cls"),
                          src=y.get("src") or n.get("src") or j.get("src"),
                          level=y.get("level") or n.get("level") or j.get("level"),
                          w=j.get("w"), ext=j.get("ext"), pinned=j.get("pinned", False),
                          tau0=n.get("tau0") or j.get("tau"), budget=n.get("budget"),
                          yes_dead=yd, yes_state=ystate, no_dead=nd,
                          yes_cover=y.get("cover"),
                          outcome=("BOTH" if (yd and nd) else "NO-only" if nd
                                   else "YES-only" if yd else "NEITHER"),
                          r_yes_at_tt0=y.get("r_yes_at_tt0"),
                          max_tt_with_yes=y.get("max_tt_alive"),
                          n_free=y.get("n_free"),
                          tau_no=n.get("tau_at_PI_box"), eta_no=n.get("eta_at_PI_box"),
                          tau_control=n.get("tau_control"),
                          control_kills=n.get("control_kills"),
                          kill_needs_control=n.get("kill_needs_control"),
                          cert=n.get("cert"),
                          r_no_kill_min=n.get("r_no_kill_min"),
                          r_no_nokill_max=n.get("r_no_nokill_max"),
                          tt_no_kill_min=n.get("tt_no_kill_min"),
                          tt_no_nokill_max=n.get("tt_no_nokill_max"),
                          a141=A141_VERDICT.get(k),
                          screen_refuted=y.get("screen_refuted_at_PI_box")))

    pairs = [d for d in pr if d.get("pair")]
    out = dict(population=pop, top=top, cells=table,
               outcome_counts={k: sum(1 for t in table if t["outcome"] == k)
                               for k in ("BOTH", "NO-only", "YES-only", "NEITHER")},
               realised_pairs=len(pairs),
               pair_examples=pairs[:12],
               n_cells=len(table))
    json.dump(out, open(os.path.join(R, "summary158.json"), "w", encoding="utf-8"), indent=1)

    hid = 0
    print("%-32s %-9s %-6s %-4s %-5s %-24s %-13s %-9s %s"
          % ("nid", "slot", "cls", "lvl", "w", "YES", "NO", "outcome", "r_yes(tt=0)"))
    for t in table:
        if t.get("tau_no") is None and t.get("yes_state") == "REFUTED":
            hid += 1
            continue                                 # the uniform mass, counted below
        print("%-32s %-9s %-6s %-4s %-5s %-24s %-13s %-9s %s"
              % (t["nid"], t["slot"], t["cls"], t["level"],
                 ("%.2f" % t["w"]) if t["w"] is not None else "-",
                 t.get("yes_state"),
                 ("dead %.6g" % t["tau_no"]) if t["no_dead"] else
                 ("alive %.6g" % t["tau_no"] if t["tau_no"] is not None else "-"),
                 t["outcome"], t["r_yes_at_tt0"]))
    print("(%d further cells omitted: YES REFUTED by a realised pose, NO child not run)" % hid)
    nref = sum(1 for d in ys if d.get("yes_refuted"))
    out["yes_screen"] = dict(cells=len(ys), refuted_at_PI_box=nref,
                             cover_worth_buying=sum(1 for d in ys
                                                    if d.get("cover_worth_buying")))
    print()
    print("outcomes:", out["outcome_counts"], " realised (S-pose, free second meeter) pairs:",
          len(pairs))
    print("fast YES screen at S(0.10, 10 deg): %d cells, %d refuted, %d would need a cover"
          % (len(ys), nref, out["yes_screen"]["cover_worth_buying"]))
    print("wrote", os.path.join(R, "summary158.json"))


if __name__ == "__main__":
    main()
