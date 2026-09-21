"""A257 -- the SYNTHETIC Trump-containing trump5 page at slack pins (the seam pilot's instrument).

A212 notes/trump5_tree.md s.6 built it once (`scratchpad/synth_trump.py`, not kept): f1_L10_0003 -- the only trump5
record whose root gate is true -- with its SECOND H box (A60's ladder box H1, which holds NO image square) REPLACED
by a box of half-width 0.02 / 2 deg about Trump's square 9.  The page then contains the image g = id at every node
of the spine and the aligned split can walk down to the tube.  A257 rebuilds it and adds the one thing the window
needs: the five class pins carry SLACK cores, half-side a = 1/2 - delta_pin (A57's G1 convention, delta_pin = 1e-2),
so that Lemma SEAM's (K) condition T_K(delta_pin) >= T' can hold at a window pad at all
(A256 notes/trump5_closure.md s.4: A60's records carry delta_pin = 3.08e-8, i.e. T_K < 0).

**What this page is and is not.**  It is a MEASUREMENT INSTRUMENT, not a certificate about trump5: its H1 box is not
A60's, so nothing proved on it is inherited by any real node.  Widening the pin cores is a WEAKENING of the
hypothesis (the role box P_k grows from a point to +-delta_pin), so every rule that kills on this page would also
kill on the tight-pin page -- the measurement is if anything pessimistic, which is the right direction for a pilot
whose question is "do the near-Trump siblings die?".

    python synth257.py [--dpin 0.01] [--half 0.02] [--deg 2.0]   -> results/nodes/<nid>.json, prints the nid
"""
import argparse
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A256 = os.path.join(ROOT, "attempts", "A256-trump5-passes", "code")
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree", "code")
SRC = os.path.join(ROOT, "attempts", "A60-trump5-campaign", "results", "nodes", "f1_L10_0003.json")
NODES = os.path.abspath(os.path.join(HERE, "..", "results", "nodes"))
IMAGE_SQUARE = 9                      # the square H1 is rebuilt around (A212 s.6)


def _img():
    for p in (A211, A256):
        if p not in sys.path:
            sys.path.insert(0, p)
    import trump256 as TR                                      # noqa: E402  READ-ONLY (A256): the embedded image
    return TR


def nid_of(dpin, half, deg):
    return "synth257_d%s_h%s_t%s" % (("%g" % dpin).replace(".", ""), ("%g" % half).replace(".", ""),
                                     ("%g" % deg).replace(".", ""))


def build(dpin=0.01, half=0.02, deg=2.0):
    """-> (nid, path): f1_L10_0003 with H1 rebuilt around image square 9 and the five pin cores slackened."""
    TR = _img()
    q = next(x for x in TR.base() if x["i"] == IMAGE_SQUARE)
    cx, cy = float(q["cx"]), float(q["cy"])
    th = TR.MB.deg_of_t(q["t"])
    d = json.load(open(SRC, encoding="utf-8"))
    hyp = d["hyp"]
    boxes, cores = hyp["boxes"], hyp["cores"]
    if len(boxes) != 7 or len(cores) != 7:
        raise SystemExit("A257: f1_L10_0003 no longer has 5 pins + H0 + H1 (%d boxes)" % len(boxes))
    boxes[6] = dict(x0=cx - half, x1=cx + half, y0=cy - half, y1=cy + half, th0=th - deg, th1=th + deg)
    cores[6] = dict(cores[6], kx=str(Fr(round(cx * 10 ** 12), 10 ** 12)), ky=str(Fr(round(cy * 10 ** 12), 10 ** 12)),
                    box=dict(boxes[6]), float=dict(kx=cx, ky=cy, theta_deg=th, a=float(Fr(str(cores[6]["a"])))),
                    synthetic="A257: the H1 core rebuilt about the embedded Trump square %d (A212 s.6)" % IMAGE_SQUARE)
    a = Fr(1, 2) - Fr(str(dpin))                              # the SLACK pin core (geo178.load_record: dpin = 1/2 - a)
    for k in range(5):
        cores[k] = dict(cores[k], a=str(a), float=dict(cores[k].get("float") or {}, a=float(a)),
                        slack="A257: delta_pin = %s (contraction_tube.md s.4.4 item 1; A57's G1 convention)" % dpin)
    d["hyp"] = dict(hyp, boxes=boxes, cores=cores)
    d["a257"] = dict(source=os.path.relpath(SRC, ROOT).replace("\\", "/"), dpin=dpin, half=half, deg=deg,
                     image_square=IMAGE_SQUARE, image_centre=[cx, cy], image_tilt_deg=th,
                     what="SYNTHETIC measurement page (A257 code/synth257.py): NOT a certificate about trump5 -- "
                          "H1 is replaced by a box about the Trump image's square, and the pin cores are slackened "
                          "to 1/2 - delta_pin, which WEAKENS the hypothesis (a superset of the real node's packings).")
    nid = nid_of(dpin, half, deg)
    os.makedirs(NODES, exist_ok=True)
    path = os.path.join(NODES, "%s.json" % nid)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    return nid, path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpin", type=float, default=0.01)
    ap.add_argument("--half", type=float, default=0.02)
    ap.add_argument("--deg", type=float, default=2.0)
    a = ap.parse_args()
    nid, path = build(a.dpin, a.half, a.deg)
    print(nid)
    print(os.path.relpath(path, ROOT).replace("\\", "/"))
