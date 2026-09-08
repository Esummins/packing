"""A151 -- assemble the T2 table (the growth ladder) from the workers' jsonl.

    python report151.py results/grow_A.jsonl results/grow_B.jsonl [--out notes/t2_table.md]

READ-ONLY on every campaign.
"""
from __future__ import annotations
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("srcs", nargs="+")
    ap.add_argument("--out", default=os.path.join(BASE, "notes", "t2_table.md"))
    a = ap.parse_args()
    rows, finals = [], []
    for p in a.srcs:
        job = os.path.basename(p).replace("grow_", "").replace(".jsonl", "")
        for ln in open(p, encoding="utf-8"):
            if not ln.strip():
                continue
            r = json.loads(ln)
            r["_job"] = job
            (finals if r.get("knob") in ("FINAL",) else rows).append(r)
    out = ["# A151 T2 — the growth ladder (one knob at a time from the certified symmetric "
           "(0.2, 10 deg) base)", "",
           "`DEAD` = the selection tree closed every leaf AND the sampling check found 0 hits; "
           "`CAPPED` = the wall cap fired (a compute limit, NOT a geometric one — no claim is made "
           "from it); `LIVE-LOW` = a real partial packing of L u P at side <= s0 was found.", "",
           "| job | square | axis | value | verdict | certified min | leaves | witnesses | "
           "unresolved | drawn | tested | hits | wall |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("knob") == "VERIFY":
            sq, ax, val = "(all)", "VERIFY", "-"
        else:
            sq, ax = r["knob"].split("/")
            val = r.get("value")
        t = r["tree"]
        st = t["stats"]
        verdict = ("DEAD" if r["dead"] else
                   ("CAPPED" if t["capped"] else
                    ("LIVE-LOW (%d)" % r["n_witnesses"] if r["n_witnesses"] else "UNRESOLVED")))
        sp = r.get("sampling") or {}
        out.append("| %s | %s | %s | %s | **%s** | %s | %d | %d | %d | %s | %s | %s | %.0f s |"
                   % (r["_job"], sq, ax, val, verdict,
                      ("%.7f" % t["certified_min"]) if t.get("certified_min") else "-",
                      st["dead_lp"], r["n_witnesses"], r["n_unresolved"],
                      sp.get("n_samples", "-"), sp.get("free_pairs_disjoint", "-"),
                      sp.get("hits", "-"), r["seconds"]))
    for f in finals:
        out += ["", "**FINAL %s** (%.0f s): `%s`" % (f["_job"], f["seconds"], json.dumps(f["spec"])),
                "", "saturated: `%s`" % json.dumps(f.get("saturated", {}))]
    txt = "\n".join(out)
    open(a.out, "w", encoding="utf-8").write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
