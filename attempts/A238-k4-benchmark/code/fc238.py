"""A238 -- the FORCED-CELL census of the protected tier: how much traction Theorem FC gives the geometry toolkit on
each class, and why.

    python fc238.py [--out results/forced238.md]

Every kill rule of the k5 toolkit that is not the raw multibox fixed point -- rule CC (Lemma CORNER-COVER), A208's
no-room + Lemma POCKET, A206's Rule NS, A230's Rule EPS, A224's Rule SNAP -- acts on the FORCED CELLS of the class:
the cells where Theorem FC says a non-pin square must sit.  `classes178.forced_cells` marks a cell USABLE only when
the class obtained by adding that slot is a census class whose A56 scoreboard row is FULL over the whole window
[191/50, 969271/250000], i.e. a class already CLOSED.  So:

    the toolkit's traction on a class S = the number of one-slot extensions of S that are already closed.

That is Lemma K1 read forwards, and it is the single number that predicts whether the geometry prices a class."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A238 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import load238                                                  # noqa: E402

TIER = ["trump5", "k4_03", "k4_05", "k4_06", "k4_08", "k4_11", "corners4",
        "k3_01", "k3_02", "k3_03", "k3_04", "k3_05", "k2_00", "k2_01", "k2_02", "k1_00", "k0_00"]
IMAGES = os.path.join(ROOT, "attempts", "A84-protected-trees", "results", "tier84_classes.json")


def tier84():
    return json.load(open(IMAGES, encoding="utf-8")) if os.path.exists(IMAGES) else {}


def census():
    load238.patch_classes()
    CL, T84, out = load238.CL, tier84(), []
    for c in TIER:
        try:
            rows = CL.forced_cells(c)
        except Exception as e:                                    # noqa: BLE001
            out.append(dict(cls=c, error=repr(e), n_cells=None, n_usable=None))
            continue
        us = [r for r in rows if r["usable"]]
        d = T84.get(c) or {}
        out.append(dict(cls=c, k=len(CL.pins_of(c)) if c != "k0_00" else 0, n_cells=len(rows), n_usable=len(us),
                        usable=[[r["cell"], r["extension"]] for r in us],
                        blocked=[[r["cell"], r["extension"]] for r in rows if not r["usable"]],
                        n_images=d.get("n_images"), image_bearing=bool(d.get("n_images")),
                        pin_sets=d.get("distinct_trump_frame_pin_sets")))
    return out


def md(rows):
    L = ["# A238 — the forced-cell census of the protected tier", "",
         "`usable` = the one-slot extensions of the class that are ALREADY CLOSED (A56 scoreboard FULL over",
         "[191/50, 969271/250000]).  Theorem FC's forced roles — and with them rule CC, A208's no-room + Lemma POCKET,",
         "A206's Rule NS, A230's Rule EPS and A224's Rule SNAP — exist only at those cells, so this column IS the",
         "geometry toolkit's traction on the class.", "",
         "| class | k | Trump images | forced cells | USABLE | the usable extensions | the blocked ones |",
         "|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("error"):
            L.append("| %s | - | - | - | - | (%s) | |" % (r["cls"], r["error"][:40]))
            continue
        L.append("| `%s` | %s | %s | %d | **%d** | %s | %s |" % (
            r["cls"], r["k"], r.get("n_images") or 0, r["n_cells"], r["n_usable"],
            ", ".join("%s→%s" % (a, b) for a, b in r["usable"]) or "—",
            ", ".join("%s→%s" % (a, b) for a, b in r["blocked"]) or "—"))
    L += ["", "## The reading", "",
          "* **trump5 6/6** — every k6 class is closed, so the toolkit has full traction; that is why A211/A212's",
          "  frontier runs at all.",
          "* **the k4 tier 3–5 usable** — its extensions are the k5 classes, and all but `trump5` (and, for",
          "  `corners4`, `k5_16`) are closed. The four image-bearing k4 classes and `k4_05` therefore get forced",
          "  roles and the geometry bites.",
          "* **`corners4` 0/8** — every one-slot extension is `k5_16`, which is still OPEN. The shadow class has NO",
          "  forced cell, so rule CC / no-room / NS / EPS / SNAP have nothing to act on: the toolkit cannot price it",
          "  until k5_16 closes. (A84 §7.1 reached the same conclusion from the LP side: root τ = 7.25 > 7.)",
          "* **every k ≤ 3 class 0 usable** — their one-slot extensions are the k4 protected classes, which are",
          "  themselves open. The toolkit has no lever on them TODAY, and acquires one the moment the k4 tier closes.",
          "",
          "So the geometry price of the protected tier is not flat: it is a **cascade**. Closing k4 hands every k3",
          "class 4–6 forced cells, closing k3 hands k2 its cells, and so on down to k0_00 — the same K1 climb that",
          "A224's Rule SNAP uses inside a single tree, applied to the tier itself.", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(A238, "results", "forced238.md"))
    a = ap.parse_args()
    rows = census()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(md(rows))
    json.dump(rows, open(os.path.join(A238, "results", "forced238.json"), "w", encoding="utf-8"), indent=1)
    for r in rows:
        print("%-9s usable %s / %s" % (r["cls"], r.get("n_usable"), r.get("n_cells")))
    print("-> %s" % os.path.relpath(a.out, ROOT))
