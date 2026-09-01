"""
A55/k3_ext leg: rebuild the emptiness map with the k3_ext PASS ledger folded in.

Thin wrapper over attempts/A55-k4-sweep/code/cap.py (unmodified): the only change is that
`certified_names()` additionally globs k3_ext/certs/*.json.PASS, tagged src "A55/k3_ext".
Writes A55's results/cap.json (backed up first by the caller) and stamps a `note` field.
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
K3EXT = os.path.abspath(os.path.join(HERE, ".."))
A55 = os.path.abspath(os.path.join(K3EXT, ".."))
sys.path.insert(0, os.path.join(A55, "code"))
import cap

_orig = cap.certified_names


def certified_names():
    got = _orig()
    for p in sorted(glob.glob(os.path.join(K3EXT, "certs", "*.json.PASS"))):
        got.setdefault(os.path.basename(p).replace(".json.PASS", ""), "A55/k3_ext")
    return got


cap.certified_names = certified_names

OUT = os.path.join(A55, "results", "cap.json")
NOTE = ("A55/k3_ext (2026-09-01): k3_00 -- the full left-wall column "
        "{(1/2,1/2),(1/2,3/2),(1/2,5/2)}, budget 8 -- KILLED by an exact certificate "
        "(k3_ext/certs/k3_00.json, 3 degenerate cores + 579 atoms, total 399/50 = 7.98 < 8, "
        "scale 1.0412 of the ceiling 8/tau = 1.04381 at tau = 7.664262), verified inside the "
        "certification loop and RE-VERIFIED independently at --depth 60 --jobs 6: PASS, "
        "2817596 boxes, 0 witnesses, max depth used 44, 66.6 s "
        "(k3_ext/reverify_d60.report.json). Lever: A54/A55 merged warm start with row pruning "
        "OFF (2951 atoms / 64297 rows, union of A55's scout node, its four witness-feedback "
        "re-solves, its witness placements and the recovered checkpoint of an interrupted "
        "pass), column-only pruning, lifted scale ceiling; PASS came at certification round 0. "
        "This closes GAP-A55-6 and, with it, the last pin-LP target below k = 4: every "
        "remaining open Young class at every k is K1-protected (a sub-skeleton of k5_11, "
        "trump5 or k5_16), so no further certificate of this kind can exist.")

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "--out", OUT] + sys.argv[1:]
    cap.main()
    d = json.load(open(OUT))
    d["notes"] = d.get("notes", []) + [NOTE]
    json.dump(d, open(OUT, "w"), indent=1)
    print("note appended to", OUT)
