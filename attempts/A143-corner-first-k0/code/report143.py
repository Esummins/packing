"""A143 -- the report tables (T2 first, T1 second, T3 third), written to notes/tables.md."""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
R = os.path.join(BASE, "results")


def jl(p):
    if not os.path.exists(p):
        return []
    out = []
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            out.append(json.loads(ln))
    return out


def lp_table(rows, title):
    L = [f"### {title}", "",
         "| node | kind | cell(s) | tau | eta | conv | minmass | maxcov | kill | certified | "
         "K' extra cols | wall s |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        kp = r.get("kprime") or {}
        L.append("| {n} | {k} | {c} | {t} | {e} | {cv} | {mm} | {mc} | {kl} | {ce} | {kp} | {w} |"
                 .format(n=r["node"], k=r.get("kind", ""), c=r.get("cell", ""),
                         t=("%.5f" % r["tau"]) if r.get("tau") is not None else "—",
                         e=("%+.4f" % r["eta"]) if r.get("eta") is not None else "—",
                         cv=r.get("converged"), mm=("%.4f" % r["minmass"])
                         if r.get("minmass") is not None else "—",
                         mc=("%.4f" % r["maxcov"]) if r.get("maxcov") is not None else "—",
                         kl=r.get("kills_converged"), ce=r.get("certified", "—"),
                         kp=f"{kp.get('n_kprime_only', '—')} of {kp.get('n_rows', '—')}",
                         w=r.get("wall_s")))
    etas = [r["eta"] for r in rows if r.get("eta") is not None]
    if etas:
        L += ["", f"n = {len(rows)}, eta in [{min(etas):+.4f}, {max(etas):+.4f}], "
                  f"median {sorted(etas)[len(etas)//2]:+.4f}; converged kills "
                  f"{sum(1 for r in rows if r.get('kills_converged'))}; certified "
                  f"{sum(1 for r in rows if r.get('certified') == 'PASS')}."]
    return L


def main():
    out = ["# A143 tables", ""]
    single = jl(os.path.join(R, "lp143_single_s0.jsonl"))
    pair = jl(os.path.join(R, "lp143_pair_s0.jsonl"))
    for r in single + pair:
        nl = json.load(open(os.path.join(R, "nodes_single.json"), encoding="utf-8")) \
            if r in single else json.load(open(os.path.join(R, "nodes_pair.json"),
                                               encoding="utf-8"))
        for n in nl:
            if n["node"] == r["node"]:
                r["kind"] = n.get("kind")
    out += lp_table(single, "T2 — single-intruder root, budget 10, cap 240 s, exact cores") + [""]
    out += lp_table(pair, "T2b — doubly-met pair root, budget 9, cap 240 s, exact cores") + [""]

    g = {r["cell"]: r for r in jl(os.path.join(R, "geom143.dedup.jsonl"))}
    cnt = collections.Counter(r["verdict"] for r in g.values())
    lanes = collections.Counter()
    for r in g.values():
        for cn, v in (r.get("lanes") or {}).items():
            lanes[(cn, v["verdict"])] += 1
    out += ["### T1 — geometry on the single-intruder cover (216 cells)", "",
            "| verdict | cells |", "|---|---|"]
    for k, v in cnt.most_common():
        out.append(f"| {k} | {v} |")
    out += ["", "| corner | LANE>=2 | LANE<=1 | LANE<=0 | UNDECIDED |", "|---|---|---|---|---|"]
    for cn in ("BL(0,0)", "BR(0,0)", "TR(0,0)", "TL(0,0)"):
        out.append(f"| {cn} | {lanes[(cn,'LANE>=2')]} | {lanes[(cn,'LANE<=1')]} | "
                   f"{lanes[(cn,'LANE<=0')]} | {lanes[(cn,'UNDECIDED')]} |")

    ps = json.load(open(os.path.join(R, "pairs143_geom.stats.json"), encoding="utf-8"))
    pl = jl(os.path.join(R, "pairs143_lane_s0.jsonl"))
    plc = collections.Counter()
    for r in pl:
        for cn, v in r["lanes"].items():
            plc[(cn, v["verdict"])] += 1
    out += ["", "### T1b — geometry on the pair cover", "",
            f"unordered pairs {ps['total']}, D4_BL-canonical {ps['canonical']}; "
            f"P2 {ps['P2']}, P1 {ps['P1']}, P1s {ps['P1s']}, alive {ps['alive']} "
            f"({100.0*(ps['canonical']-ps['alive'])/ps['canonical']:.1f} % killed by geometry)",
            "", f"lane test on {len(pl)} of {ps['alive']} survivors: "
                f"{sum(1 for r in pl if r['verdict'] != 'ALIVE-GEOM')} kills", "",
            "| corner | LANE>=2 | LANE<=1 | LANE<=0 | UNDECIDED |", "|---|---|---|---|---|"]
    for cn in ("BL(0,0)", "BR(0,0)", "TR(0,0)", "TL(0,0)"):
        out.append(f"| {cn} | {plc[(cn,'LANE>=2')]} | {plc[(cn,'LANE<=1')]} | "
                   f"{plc[(cn,'LANE<=0')]} | {plc[(cn,'UNDECIDED')]} |")

    it = json.load(open(os.path.join(R, "intersect143.json"), encoding="utf-8"))
    out += ["", "### T2 — intersection with the twelve converged-alive interior cells", "",
            "| interior cell | support | BL meeters (unwidened) | corner-first cells | "
            "support pairs alive / dead | Rule III fires |", "|---|---|---|---|---|---|"]
    for k, v in it.items():
        al = sum(1 for p in v["pairs"] if p["verdict"] == "ALIVE-CORE")
        cells = sorted({tuple(m["cell_canon"]) for m in v["meeters"] if m["cell_canon"]})
        out.append(f"| {k} | {v['n_support']} | {v['n_bl_meeters']} "
                   f"({v['n_bl_meeters_unwidened']}) | {len(cells)} | {al} / "
                   f"{len(v['pairs'])-al} | {'YES' if al == 0 else 'no'} |")

    cov = json.load(open(os.path.join(R, "cover143.json"), encoding="utf-8"))
    out += ["", "### T1 — sampled cover confirmation", "",
            f"single: {cov['single']['drawn']} drawn, {cov['single']['hits']} admissible "
            f"BL-meeting poses, {cov['single']['misses']} misses, "
            f"{cov['single']['distinct_cells_hit']} distinct cells hit",
            f"pair: {cov['pair']['drawn']} drawn, {cov['pair']['realised_2crowds']} realised "
            f"interior-disjoint BL 2-crowds, {cov['pair']['violations']} violations, "
            f"{cov['pair']['distinct_pair_cells_hit']} distinct pair cells hit"]

    de = json.load(open(os.path.join(R, "descend143.json"), encoding="utf-8"))
    out += ["", "### the Trump lineage, descended (geometry only)", "",
            f"image {de['image']}, BL meeters {de['poses']}, cells {de['cells']}", "",
            "| depth | P1 | P2 | BL | BR | TR | TL | any kill |", "|---|---|---|---|---|---|---|---|"]
    for L in de["levels"]:
        ln = L["lanes"]
        out.append("| {d} | {p1} | {p2} | {bl} | {br} | {tr} | {tl} | {k} |".format(
            d=L["depth"], p1=L["P1_fires"], p2=L["P2_fires"],
            bl=f"{ln['BL(0,0)']['verdict']} M={ln['BL(0,0)']['M']}",
            br=f"{ln['BR(0,0)']['verdict']} M={ln['BR(0,0)']['M']}",
            tr=f"{ln['TR(0,0)']['verdict']} M={ln['TR(0,0)']['M']}",
            tl=f"{ln['TL(0,0)']['verdict']} M={ln['TL(0,0)']['M']}", k=L["any_kill"]))

    p = os.path.join(BASE, "notes", "tables.md")
    open(p, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out))
    print("\nwrote", p)


if __name__ == "__main__":
    main()
