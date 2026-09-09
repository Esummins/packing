"""A181 (2) -- fold-in, overlay, comparison with A176 and the per-step report of renorm181's records.

    python renorm181b.py report  --cell l1_104      alive before (A168) / after (A181) per step, from the
                                                    side files + the tree (todo = every ALIVE node with roles)
    python renorm181b.py compare --cell l1_104 --chains root/D0/S0;root/D1/S0
                                                    A176 vs A181 per node on the chain + its recorded children
    python renorm181b.py apply   --cell l1_104      fold into the tree (A168 record kept under node['a168'],
                                                    A176's fold-in never happened); DEAD(ancestor) closure
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import cascade168 as CS                                          # noqa: E402
import renorm175 as RN                                           # noqa: E402
import renorm176 as R6                                           # noqa: E402
import renorm181 as R8                                           # noqa: E402

TAG = R8.TAG


def overlay_side(T, cell):
    """fold the A181 side files into an IN-MEMORY tree (figures while the runs are in flight);
    also stores the seeding record so a page can print the seeded kept fractions."""
    recs = R8.load_side(cell)
    n = 0
    for p, r in recs.items():
        node = T["nodes"].get(p)
        if node is None or r["verdict"].startswith("SKIPPED"):
            continue
        node["verdict"] = r["verdict"]
        node[TAG] = {k: r.get(k) for k in ("leaf", "kept", "kept_mb", "k_area", "passes", "n_pieces", "wall_s",
                                            "seeded_kept", "seeded_n_pieces", "vol1", "vol1_le_parent", "reused_from",
                                            "setting", "kept_42")}
        if r.get("roles"):
            node["roles"], node["kept"], node["invariant"] = r["roles"], r.get("kept"), r.get("invariant")
            node["clip_passes"], node["rows"], node["row_kill"] = r.get("passes"), r.get("rows"), r.get("row_kill")
        n += 1
    return n


def todo_all(T):
    out = {}
    for p, n in T["nodes"].items():
        st = n.get("step") or "root"
        if not n.get("roles") or not n["verdict"].startswith("ALIVE") or str(st).endswith("complement"):
            continue
        out[p] = st
    return out


def stage_report(a):
    T, _ = RN.load_tree_overlay(a.cell, 1)
    todo = todo_all(T)
    recs = R8.load_side(a.cell)
    rep = {}
    for p, st in todo.items():
        d = rep.setdefault(st, dict(alive_before=0, done=0, alive_after=0, dead=0, leaves={}, reused=0, wall_s=0.0))
        d["alive_before"] += 1
        r = recs.get(p)
        if r is None or r["verdict"].startswith("SKIPPED"):
            continue
        d["done"] += 1
        d["wall_s"] += float(r.get("wall_s") or 0)
        d["reused"] += int(bool(r.get("reused_from")))
        if r["verdict"].startswith("ALIVE"):
            d["alive_after"] += 1
        else:
            d["dead"] += 1
            lf = str(r.get("leaf"))
            d["leaves"][lf] = d["leaves"].get(lf, 0) + 1
    # descendants of a DEAD or not-yet-done parent: closure counts (not recorded, but implied)
    for p, st in todo.items():
        if p in recs:
            continue
        q = T["nodes"][p].get("parent")
        while q and q not in recs:
            q = T["nodes"][q].get("parent")
        if q and recs[q]["verdict"].startswith("DEAD"):
            rep[st]["dead_by_closure"] = rep[st].get("dead_by_closure", 0) + 1
    for st in rep:
        rep[st]["wall_s"] = round(rep[st]["wall_s"])
        rep[st]["not_done_under_alive"] = rep[st]["alive_before"] - rep[st]["done"] - rep[st].get("dead_by_closure", 0)
    mono = sum(1 for r in recs.values() if r.get("vol1_le_parent") is False)
    out = dict(cell=a.cell, when=time.strftime("%Y-%m-%d %H:%M"), steps=rep, n_records=len(recs), vol1_exceeds_parent=mono)
    K.jdump(out, os.path.join(K.RES, "%s_report_%s.json" % (TAG, a.cell)))
    for st in sorted(rep, key=lambda s: (s != "root", s)):
        print("%-5s %s" % (st, json.dumps(rep[st])))
    print("records %d; vol1 > parent on %d nodes (must be 0)" % (len(recs), mono))


def _line(r, nm=None):
    if r is None:
        return "-"
    v = r["verdict"].split("(")[0] + ("/" + str(r.get("leaf")) if r.get("leaf") else "")
    kp = r.get("kept") or {}
    vo = r.get("vol1") or {}
    return "%s kept %s vol1 %s%s" % (v, {k: round(x, 3) for k, x in kp.items()}, {k: round(x, 4) for k, x in vo.items()},
                                     " pieces %s" % r.get("n_pieces") if r.get("n_pieces") else "")


def stage_compare(a):
    T, _ = RN.load_tree_overlay(a.cell, 1)
    r81, r76 = R8.load_side(a.cell), R6.load_side(a.cell)
    out = {}
    for chain in [c for c in a.chains.split(";") if c]:
        paths = []
        q = chain
        while q:
            paths.append(q)
            q = T["nodes"][q].get("parent")
        paths.reverse()
        kids = [c for c in T["nodes"][chain].get("children", []) if c in r81 or c in r76]
        for p in paths + kids[:a.n_kids]:
            out[p] = dict(a176=_line(r76.get(p)), a181=_line(r81.get(p)),
                          seeded=(r81.get(p) or {}).get("seeded_kept"))
            print("%-24s\n   A176: %s\n   A181: %s\n   seeded: %s" % (p, out[p]["a176"], out[p]["a181"],
                  {k: round(v, 3) for k, v in (out[p]["seeded"] or {}).items() if v is not None}))
        # children monotonicity in both records
        for tag, rr in (("a176", r76), ("a181", r81)):
            par = rr.get(chain)
            if not par or not par.get("vol1"):
                continue
            bad = []
            for c in T["nodes"][chain].get("children", []):
                r = rr.get(c)
                if r and r.get("vol1"):
                    for k in par["vol1"]:
                        if k in r["vol1"] and r["vol1"][k] > par["vol1"][k] * (1 + 1e-9) + 1e-12:
                            bad.append((c, k, round(r["vol1"][k], 4), round(par["vol1"][k], 4)))
            print("   %s: %d recorded children of %s; %d exceed the parent's vol1 %s" % (tag, sum(1 for c in T["nodes"][chain].get("children", []) if c in rr), chain, len(bad), bad[:4]))
            out.setdefault("monotonicity", {})["%s:%s" % (tag, chain)] = dict(n_bad=len(bad), examples=bad[:6])
    K.jdump(out, os.path.join(K.RES, "%s_compare_%s.json" % (TAG, a.cell)))


def stage_apply(a):
    T = CS.load_tree(a.cell)
    recs = R8.load_side(a.cell)
    before, after = {}, {}
    n_app = 0
    for p, n in T["nodes"].items():
        st = n.get("step") or "root"
        if str(st).endswith("complement") or not n.get("roles"):
            continue
        before.setdefault(st, [0, 0])
        before[st][0 if n["verdict"].startswith("ALIVE") else 1] += 1
        r = recs.get(p)
        if r is not None and n["verdict"].startswith("ALIVE") and not r["verdict"].startswith("SKIPPED"):
            if "a168" not in n:
                n["a168"] = dict(verdict=n["verdict"], kept=n.get("kept"),
                                 roles={k: dict(pieces=v["pieces"], kept=v.get("kept")) for k, v in n["roles"].items()})
            n["verdict"] = r["verdict"]
            n[TAG] = {k: r.get(k) for k in ("leaf", "kept", "kept_mb", "k_area", "k_area_mb", "passes", "n_pieces", "lonely",
                                             "seeded_kept", "seeded_n_pieces", "wall_s", "refine", "vol0", "vol1",
                                             "vol1_le_parent", "reused_from", "lib", "setting", "kept_42")}
            if r.get("cert"):
                c = dict(r["cert"])
                if c.get("trace"):
                    c["trace"] = c["trace"][-60:]
                n[TAG]["cert"] = c
            if r.get("roles"):
                n["roles"], n["kept"], n["invariant"] = r["roles"], r.get("kept"), r.get("invariant")
                n["clip_passes"], n["rows"], n["row_kill"] = r.get("passes"), r.get("rows"), r.get("row_kill")
            elif r.get("witness"):
                n["witness"] = r["witness"]
            n_app += 1
        after.setdefault(st, [0, 0])
        after[st][0 if n["verdict"].startswith("ALIVE") else 1] += 1
    n_anc = 0
    for q in sorted(T["nodes"], key=len):
        n = T["nodes"][q]
        par = n.get("parent")
        if par and T["nodes"].get(par, {}).get("verdict", "").startswith("DEAD") and n["verdict"].startswith("ALIVE"):
            n["verdict"] = "DEAD(C, ancestor %s: %s)" % (par, T["nodes"][par]["verdict"][:60])
            st = n.get("step") or "root"
            after.setdefault(st, [0, 0])
            after[st][0] -= 1
            after[st][1] += 1
            n_anc += 1
    for spec in CS.STEPS:
        if any(n.get("step") == spec["step"] for n in T["nodes"].values()):
            CS.canary_locate(T, spec)
    T[TAG] = dict(n_applied=n_app, n_dead_by_ancestor=n_anc, before=before, after=after, when=time.strftime("%Y-%m-%d %H:%M"),
                  source="A181 renorm181 (parent-seeded top-down; multibox >= 13f23204, polygon + lonely clip)")
    CS.save_tree(T)
    K.jdump(T[TAG], os.path.join(K.RES, "%s_summary_%s.json" % (TAG, a.cell)))
    print("apply %s: %d nodes; alive/dead before %s after %s (+%d dead by ancestor)" % (a.cell, n_app, before, after, n_anc), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("report", "compare", "apply"))
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--chains", default="root/D0/S0;root/D1/S0")
    ap.add_argument("--n_kids", type=int, default=4)
    a = ap.parse_args()
    {"report": stage_report, "compare": stage_compare, "apply": stage_apply}[a.stage](a)


if __name__ == "__main__":
    main()
