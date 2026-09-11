"""A204 report: the kill table (page, pad, round, the clip that killed it, seconds), the survivors' state (kept per role,
forced slots, instantiated roles, alive cells at the fixed point), per-round timings -- from results/polyclip204.jsonl
and the certificates.      python report204.py  ->  results/report204.md (printed too)"""
import glob
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(ATT, "results", "polyclip204.jsonl")
CERTS = os.path.join(ATT, "certs")


def rows():
    last = {}
    for ln in open(RES, encoding="utf-8"):
        try:
            d = json.loads(ln)
        except Exception:
            continue
        if d.get("pad") in ("g1", "zero"):
            last[(d["nid"], d["pad"])] = d
    return last


def main():
    R = rows()
    L = ["# A204 polyclip204 -- report (from results/polyclip204.jsonl + certs)", ""]
    kills = [d for d in R.values() if d.get("verdict") == "DEAD"]
    L.append("## Kill table (%d)" % len(kills))
    L.append("| page | pad | round | clip | seconds | leaf |")
    L.append("|---|---|---|---|---|---|")
    for d in sorted(kills, key=lambda d: (d["nid"], d["pad"])):
        L.append("| %s | %s | %s | %s | %s | %s |" % (d["nid"], d["pad"], d.get("killed_round"), d.get("clip"), d.get("seconds"), str(d.get("leaf") or "")[:140].replace("|", "/")))
    L += ["", "## Every (page, pad): verdict, rounds, seconds per round, kept, forced H, roles, alive cells at the last round", ""]
    L.append("| page | pad | verdict | rounds | s/round | total s | fixed pt | kept H | roles (slots) | forced H | alive cells | H units in |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    tot, nround, fix_s = [], [], []
    for (nid, pad), d in sorted(R.items()):
        cert = os.path.join(CERTS, "polyclip204_%s.json" % nid)
        alive = ""
        try:
            c = json.load(open(cert, encoding="utf-8"))
            snaps = (c["pads"].get(pad) or {}).get("snapshots") or []
            if snaps:
                fz = snaps[-1].get("forcing") or {}
                alive = " ".join("%s:%d" % (p.replace("(", "").replace(")", "").replace(",", ""), len(v)) for p, v in (fz.get("single") or {}).items())
            rts = (c["pads"].get(pad) or {}).get("round_times") or []
            fix_s += [r.get("fix") for r in rts if r.get("fix")]
        except Exception:
            pass
        kept = d.get("kept") or {}
        roles = d.get("role_slots") or {}
        st = d.get("start") or {}
        L.append("| %s | %s | **%s** | %s | %s | %s | %s | %s | %s | %s | %s | %s/%s |" % (
            nid.replace("_interior", ""), pad, d.get("verdict"), d.get("n_rounds"), d.get("round_seconds"), d.get("seconds"),
            "yes" if d.get("fixed_point") else ("WALL" if d.get("wall") else "-"), kept.get("H"),
            ", ".join("%s:%s(%s)" % (k, kept.get(k), "+".join(v)) for k, v in roles.items()) or "-", d.get("forced_H") or "-",
            alive, st.get("n_units_alive"), st.get("n_units")))
        tot.append(float(d.get("seconds") or 0))
        nround.append(int(d.get("n_rounds") or 0))
    L += ["", "## Timings", ""]
    if tot:
        L.append("- %d (page, pad) runs: total seconds median %.0f, max %.0f, sum %.0f (%.2f CPU-h); rounds median %s, max %s; fixed-point seconds per round median %.0f, max %.0f" % (
            len(tot), statistics.median(tot), max(tot), sum(tot), sum(tot) / 3600, statistics.median(nround), max(nround),
            statistics.median(fix_s) if fix_s else 0, max(fix_s) if fix_s else 0))
    pages = {nid for nid, _ in R}
    dead_pages = {d["nid"] for d in kills}
    L.append("- pages: %d touched, %d DEAD at some pad (%d at g1), %d ALIVE" % (len(pages), len(dead_pages), len({d["nid"] for d in kills if d["pad"] == "g1"}), len(pages - dead_pages)))
    inst = [(nid, pad, d.get("role_slots")) for (nid, pad), d in R.items() if d.get("role_slots")]
    L.append("- instantiated roles on %d runs: %s" % (len(inst), "; ".join("%s/%s %s" % (n.replace("_interior", ""), p, r) for n, p, r in sorted(inst))))
    out = "\n".join(L)
    open(os.path.join(ATT, "results", "report204.md"), "w", encoding="utf-8").write(out + "\n")
    print(out)


if __name__ == "__main__":
    main()
