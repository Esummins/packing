"""A241 -- results/rows241.md: the extension table for the 16 protected classes + the 8 A55-killed k4
classes, each extension's window status, what can be rowed today and what waits on which frontier nodes.

    python rows241.py [--out results/rows241.md]

Sources, all read-only: the A56 scoreboard (the full-window rows), A241's results/param241.jsonl
(the window statements this attempt produced), A55 results/cap.json (the exact s0 kills and their
witnesses), and the k5 frontier's own closure ledgers for the three still-open k5 classes.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A241 = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(A241, "..", ".."))
ATT = os.path.join(ROOT, "attempts")
sys.path.insert(0, HERE)
import rowcascade241 as RC                                                      # noqa: E402

SB = RC.SCOREBOARD
CAP = os.path.join(ATT, "A55-k4-sweep", "results", "cap.json")
FULL = RC.FULL
TIER = ["trump5", "k4_03", "k4_05", "k4_06", "k4_08", "k4_11", "corners4",
        "k3_01", "k3_02", "k3_03", "k3_04", "k3_05", "k2_00", "k2_01", "k2_02", "k1_00",
        "k4_00", "k4_01", "k4_02", "k4_04", "k4_07", "k4_09", "k4_10", "k4_12", "k3_00"]
A55_KILLED = ("k4_00", "k4_01", "k4_02", "k4_04", "k4_07", "k4_09", "k4_10", "k4_12")
OPEN_K5 = ("trump5", "k5_11", "k5_16")
PROTECTED = ("k4_03", "k4_05", "k4_06", "k4_08", "k4_11", "k4_13", "corners4",
             "k3_01", "k3_02", "k3_03", "k3_04", "k3_05", "k2_00", "k2_01", "k2_02", "k1_00", "k0_00")


def frontier():
    """{k5 class: alive frontier nodes still covering it} from A211's closure ledger, best effort."""
    out = {}
    for rel in (("A211-coarse-tree", "results", "frontier211.json"),
                ("A211-coarse-tree", "results", "ledger211.json"),
                ("A209-k5-killer", "results", "ledger209.json"),
                ("A57-shadow-trees", "results", "ledger57.json")):
        f = os.path.join(ATT, *rel)
        if not os.path.exists(f):
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:                                                       # noqa: BLE001
            continue
        rows = d.get("rows") if isinstance(d, dict) else d
        if isinstance(rows, dict):
            for k, v in rows.items():
                if isinstance(v, dict) and v.get("alive") is not None:
                    out.setdefault(k, []).append((os.path.join(*rel), v.get("alive")))
    return out


def status(name, sbrows):
    """the window status of an extension class, with its citation."""
    if name is None:
        return "never a class", "the pin set + this slot is not a census class"
    r = sbrows.get(name)
    if r and str(r.get("status", "")).startswith(FULL):
        src = (r.get("a241") or {}).get("route")
        cite = r.get("status")
        if src:
            cite += " [A241 %s]" % src
        return "FULL-WINDOW", cite
    if name in OPEN_K5:
        return "OPEN", "the k5 frontier: %s is not closed on the window" % name
    if name in A55_KILLED:
        return "s0 only", "A55 exact kill, no window statement yet (A241 campaign)"
    if name in PROTECTED:
        return "OPEN", "K1-protected: %s is a sub-skeleton of an open k5 class" % name
    return "no row", "no full-window scoreboard row"


def table():
    import load_cl241 as L
    CL = L.classes()
    sbrows = json.load(open(SB, encoding="utf-8"))["rows"]
    fr = frontier()
    out = []
    for c in TIER:
        try:
            cells = CL.forced_cells(c)
        except Exception as e:                                                  # noqa: BLE001
            out.append(dict(cls=c, error=repr(e)))
            continue
        exts = []
        for r in cells:
            st, cite = status(r["extension"], sbrows)
            exts.append(dict(cell=r["cell"], ext=r["extension"], status=st, cite=cite,
                             waits=fr.get(r["extension"] or "")))
        own = sbrows.get(c)
        out.append(dict(cls=c, n=len(cells), usable=sum(1 for e in exts if e["status"] == "FULL-WINDOW"),
                        rowed=bool(own and str(own.get("status", "")).startswith(FULL)),
                        own_status=(own or {}).get("status"), exts=exts))
    return out


def md(rows):
    L = ["# A241 -- the ROW cascade: one-slot extensions and their window status", "",
         "`FULL-WINDOW` = the extension class carries a scoreboard row `%s`, so Lemma SLOT-CROWD" % FULL,
         "applies at that cell and Theorem FC gives the class a forced cell.  `s0 only` = A55 killed the class",
         "exactly, but at s0 -- and `closed_disjoint_bridge.md` B.2 makes that worth NOTHING on the window",
         "(corpus margin rho ~ 1.0e-9, A = 5/2, so (H') reads s''/m - 1 < 4.0e-10: no side of [3.82, s-hat]",
         "is reached).  Turning those into window rows is A241's campaign (`code/param241.py`).", "",
         "| class | own row | forced cells | USABLE | extension -> status |", "|---|---|---|---|---|"]
    for r in rows:
        if r.get("error"):
            L.append("| `%s` | - | - | - | (%s) |" % (r["cls"], r["error"][:60]))
            continue
        L.append("| `%s` | %s | %d | **%d** | %s |" % (
            r["cls"], ("**ROWED** " + (r["own_status"] or "")[:48]) if r["rowed"] else "--",
            r["n"], r["usable"],
            ", ".join("%s→%s [%s]" % (e["cell"], e["ext"], e["status"]) for e in r["exts"]) or "—"))
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(A241, "results", "rows241.md"))
    a = ap.parse_args(argv)
    rows = table()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(md(rows))
    json.dump(rows, open(os.path.join(A241, "results", "rows241.json"), "w", encoding="utf-8"), indent=1)
    for r in rows:
        print("%-9s usable %s / %s  %s" % (r["cls"], r.get("usable"), r.get("n"),
                                           "ROWED" if r.get("rowed") else ""))
    print("-> %s" % os.path.relpath(a.out, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
