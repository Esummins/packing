"""A207 -- the markdown tables for notes/basin.md: the per-slot basin table (results/basin207.jsonl) and the kill table
(results/basinclip207.jsonl).        python scratch/tables207.py [basins|kills]"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")


def rows(f):
    return [json.loads(l) for l in open(os.path.join(RES, f), encoding="utf-8") if l.strip()]


def basins():
    print("| class | slot | extension | core | r_c | r_t (deg) | verdict | LP tau (s) | certify (s) | verify_param (s) | window | C2 | margin | total s | certificate |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows("basin207.jsonl"):
        v = r["verdict"]
        c2 = "" if not r.get("c2") else "%d/%d" % (sum(1 for c in r["c2"] if c["result"] == "PASS"), len(r["c2"]))
        print("| %s | %s | %s | %s | %s | %s | %s | %.3f (%s) | %s (%s) | %s (%s) | %s | %s | %s | %s | %s |" % (
            r.get("cls") or "-", r.get("slot") or "-", r["ext"], r["idx"], r["r_c"], r["r_t_deg"], "**BASIN**" if v == "BASIN" else v,
            r.get("tau") or 0, r.get("lp_seconds"), r.get("certify") or "-", r.get("certify_seconds") or "-", r.get("param") or "-", r.get("param_seconds") or "-",
            " ".join(r["window"]) if r.get("window") else "-", c2 or "-", ("%.4f" % r["margin"]) if r.get("margin") is not None else "-",
            r.get("seconds") or "-", os.path.basename(r["certificate"]) if r.get("certificate") else "-"))


def kills():
    print("| page | run | mode | leaf | verdict | nodes | dead / alive leaves | kills (label: clip r) | basins | s |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows("basinclip207.jsonl"):
        ks = "; ".join("%s: %s r%s" % (k["label"], k["clip"], k["round"]) for k in (r.get("killing") or []))
        bs = ", ".join("%s %s/%s" % (b["cell"], b["r_c"], b.get("r_t_deg")) for b in (r.get("basins") or []))
        print("| %s | %s | %s | %s | %s | %s | %s / %s | %s | %s | %s |" % (
            r["nid"].replace("_interior_", " "), r["run"], r["mode"], r.get("leaf_label") or "-", ("**%s**" % r["verdict"]) if r["verdict"] == "DEAD" else r["verdict"],
            r.get("n_nodes"), r.get("dead_leaves"), r.get("alive_leaves"), ks[:400], bs, r.get("seconds")))


if __name__ == "__main__":
    (basins if (sys.argv[1:] or ["basins"])[0] == "basins" else kills)()
