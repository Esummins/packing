"""A270 -- the campaign's progress page (results/progress270.md) with the PER-SLAB line, and the CPU-h CAP.

Reads only A270's own files: records/index.json (the *_r270w4 records and their pop270 priority), certs/ (a record is
CLOSED when one of its certificates says DEAD at g4 -- queue270.closed), results/slab270.jsonl (run211's rows: the
seconds).  If the campaign's CPU-h exceed CAP (150) it writes logs/STOP and logs/STOP_LOOP: the workers finish their
current start node and exit, the loop exits at the top of its next pass (nothing is killed).

What each slab needs (notes/slabs270.md s.3-4) -- per class S in {k5_11, k5_16}:
  G1 (incl. s-hat)  A57's G1 tree leaves + A211's g1 page kills (as on disk) + EVERY priority-1 record DEAD at g4
                    (the 296 never-emitted cover boxes and the two s0-only pages Y1117, Y0436)
  G2                + every priority-2 record DEAD at g4 (the chain / ledger closures), with A57's PASS and T5 leaves
                    carried to G2 by Corollary B'' (the sharp slot form, notes s.3) -- the NO child likewise
  G3, G4            + every record DEAD at g4 + the 9/400 logic kills (pop270) + the NO child re-certified at pin
                    cores <= 1/2 - 0.01495 (an LP obligation, not run here)

    python progress270.py"""
import collections
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
CAP = 150.0


def main():
    sys.path.insert(0, HERE)
    import queue270 as Q
    idx = [r for r in json.load(open(Q.INDEX, encoding="utf-8"))["rows"] if r["nid"].endswith("_r270w4")]
    secs = collections.defaultdict(float)
    for ln in open(os.path.join(ATT, "results", "slab270.jsonl"), encoding="utf-8") if os.path.exists(os.path.join(ATT, "results", "slab270.jsonl")) else []:
        try:
            d = json.loads(ln)
        except Exception:                                          # noqa: BLE001
            continue
        if str(d.get("nid", "")).endswith("_r270w4"):
            secs[d["nid"]] += float(d.get("seconds") or 0)
    tab = collections.defaultdict(lambda: collections.Counter())
    for r in idx:
        files = Q.certs_of(r["nid"])
        st = "DEAD" if (files and Q.closed(files)) else ("run, open" if files else "not run")
        tab[(r["cls"], r.get("prio"))][st] += 1
    cpuh = sum(secs.values()) / 3600
    L = ["# A270 progress -- %s" % time.strftime("%Y-%m-%d %H:%M:%S"), "",
         "The pad-g4 campaign (notes/slabs270.md): A57's level-1 cover rebuilt at pin slack 9/400, every chain page re-emitted "
         "as <id>_r270w4 and run through A211's chain at pad g4 = the window (3.82, s0] with A268's levers (count268, leaf268, "
         "the STALLED invariant).  A DEAD here is a statement on the WHOLE window, s-hat included.", "",
         "| class | priority | records | DEAD at g4 | run, open | not run |", "|---|---|---|---|---|---|"]
    for (cls, p), c in sorted(tab.items()):
        L.append("| %s | %s | %d | %d | %d | %d |" % (cls, p, sum(c.values()), c["DEAD"], c["run, open"], c["not run"]))
    L += ["", "## Per slab", ""]
    for cls in ("k5_11", "k5_16"):
        open_p = {p: sum(v for k, v in tab[(cls, p)].items() if k != "DEAD") for p in (1, 2, 3, 4)}
        L.append("* **%s**: G1 (incl. s-hat) %s; G2 %s; G3 / G4 %s." % (
            cls,
            "DEAD" if open_p[1] == 0 else "OPEN -- %d priority-1 record(s) not yet DEAD at g4" % open_p[1],
            "DEAD (with B'')" if open_p[1] + open_p[2] == 0 else "OPEN -- %d priority-1/2 record(s) left" % (open_p[1] + open_p[2]),
            "OPEN -- %d record(s) left + the NO-child LP at 9/400 cores" % sum(open_p.values())))
    B = ["| class | G1 = (3.861637, s0], s-hat incl. | G2 = (3.847016, 3.861637] | G3 = (3.832450, 3.847016] | G4 = [3.82, 3.832450] |",
         "|---|---|---|---|---|"]
    for cls in ("k5_11", "k5_16"):
        open_p = {p: sum(v for k, v in tab[(cls, p)].items() if k != "DEAD") for p in (1, 2, 3, 4)}
        g1 = ("**DEAD**: A57 G1 leaves + A205-A211 g1 page kills + A270 g4 kills of the never-emitted boxes" if open_p[1] == 0 else
              "**OPEN**: %d cover box(es) with no G1 row / an s0-only kill, not yet DEAD at g4" % open_p[1])
        g2 = ("**DEAD** (A270 g4 tiers 1-2 + Corollary B'')" if open_p[1] + open_p[2] == 0 else
              "**OPEN**: %d record(s) of tiers 1-2 left (A270 g4)" % (open_p[1] + open_p[2]))
        g34 = "**OPEN**: %d record(s) left + the NO-child LP" % sum(open_p.values())
        B.append("| `%s` | %s | %s | %s | %s |" % (cls, g1, g2, g34, g34))
    B.append("| `trump5` | **OPEN**: A268's g1 verdicts ran on A60's 3e-8 records (s0-only); A269 re-emits | **OPEN** (A269 pad tube) | **OPEN** (A269) | **OPEN** (A269 pad window) |")
    B += ["", "No kill on disk before A270 reaches below 3.851408 for these classes (every k5 record carries pin slack <= 1e-2).  "
          "Live: `attempts/A270-k5-lower-slabs/results/progress270.md`; the argument: `notes/slabs270.md`."]
    with open(os.path.join(ATT, "results", "slabs270_board.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(B) + "\n")
    L += ["", "trump5: all four slabs OPEN here -- A269 (re-emitted records, pads tube / window) owns them.", "",
          "CPU-h spent by the campaign: **%.2f** (cap %.0f)" % (cpuh, CAP)]
    if cpuh > CAP:
        for f in ("STOP", "STOP_LOOP"):
            open(os.path.join(ATT, "logs", f), "w").write("A270 CAP: %.2f CPU-h > %.0f at %s\n" % (cpuh, CAP, time.strftime("%Y-%m-%d %H:%M:%S")))
        L.append("* **CAP reached: logs/STOP and logs/STOP_LOOP written -- the workers exit after their current start node**")
    with open(os.path.join(ATT, "results", "progress270.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    print("progress270: %d records, %.2f CPU-h" % (len(idx), cpuh))


if __name__ == "__main__":
    main()
