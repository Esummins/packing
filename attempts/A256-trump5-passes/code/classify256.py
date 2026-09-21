"""A256 -- the (a) / (b) TRIAGE of the 149 A212 trump5 nodes (BRIEF task 2): does the node's ROOT hypothesis, with its
boxes read at the pad's slab, admit a D4 image of a CONTRACTED Trump configuration z-hat - t v (ray256)?

  (a) NO ray image  -- ordinary residue: every kill rule of the chain may be applied, and a DEAD is a real kill.
  (b) a ray image MIGHT fit -- near t = 0 the kill rules cannot work (the node holds a packing at m = s-hat), so the
      only leaf that can close such a node is the tube theorem used as a kill (Lemma TUBE-KILL, notes/trump5_closure.md).

Soundness note: the triage is NOT a soundness gate.  Every rule of the chain is sound on every node; the gate only
says where a kill ATTEMPT is wasted (notes/trump5_tree.md s.1).  So the margins are taken OUTWARD (ray256.MARGIN,
the pin drift widened by the pad's dilation): a doubtful node is put in (b), never in (a).

The boxes are the RECORD's (pins + H), not a cascade's pieces: every piece of every descendant lies inside them
(the cascade only shrinks), so an (a) verdict at the root holds for the node's whole subtree.

    python classify256.py [--pad g1] [--out results/triage256.json]
"""
import argparse
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree", "code")
for _p in (A211, HERE):
    if _p in sys.path:
        sys.path.remove(_p)
sys.path.insert(0, A211)
sys.path.insert(0, HERE)
import load256                                                 # noqa: E402
load256.install()
import poly204 as P                                            # noqa: E402
import geo178 as G                                             # noqa: E402
import ray256 as RAY                                           # noqa: E402

FP = P.FP
S0 = RAY.S0
A212ROWS = os.path.join(ROOT, "attempts", "A212-trump5-tree", "results", "trump5tree212.jsonl")


def a212_verdicts():
    """nid -> the LAST A212 pad-0 row's verdict (149 nodes: 84 ALIVE, 65 DEAD)."""
    out = {}
    for ln in open(A212ROWS, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:                                      # noqa: BLE001
            continue
        if r.get("nid"):
            out[r["nid"]] = dict(verdict=r.get("verdict"), pad=r.get("pad"), seconds=r.get("seconds"),
                                 leaf=str(r.get("leaf") or "")[:120], cls=r.get("cls"), dpin=None)
    return out


def drift(pad):
    """the per-coordinate pin DRIFT the pad's slab allows: max over the class's |alpha| of (lam - 1)|alpha|.

    A trump5 pin rides k(s) = alpha + beta s with |alpha| in {1/2, 3/2} (squares 0, 1, 3 near the walls, 2 and 5 on
    the far walls).  A packing P at side m in the slab has its pin EXACTLY at slots(m); its dilate to s0 sits
    (lam - 1)|alpha| off slots(s0).  Contracting the tube ray by the same lam is what ray256 does; this number is
    what the node's pin BOX would have to allow for the dilated family to satisfy the node at all."""
    lam = RAY.PADS[pad]
    return {"1/2": (lam - 1) * Fr(1, 2), "3/2": (lam - 1) * Fr(3, 2)}


def boxes_of(nid, pad):
    rec, cls, row = FP.load_page(nid)
    b = G.base_roles(rec)
    d = drift(pad)["3/2"]                                      # the widest pin drift of the class
    pins = [(k, (Fr(str(b[k][0])) - d, Fr(str(b[k][1])) + d, Fr(str(b[k][2])) - d, Fr(str(b[k][3])) + d))
            for k in sorted(b) if k.startswith("P")]
    hb = [(k, tuple(b[k][:6])) for k in sorted(b) if k.startswith("H")]
    dpin = max(float(p.get("dpin") or 0.0) for p in rec["pins"])
    return pins, hb, cls, dpin, row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", default="g1")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "triage256.json"))
    a = ap.parse_args()
    V = a212_verdicts()
    rows, err = [], []
    for nid in sorted(V):
        try:
            pins, hb, cls, dpin, row = boxes_of(nid, a.pad)
            r = RAY.holds_ray_image(pins, hb, pad=a.pad)
        except Exception as e:                                 # noqa: BLE001
            err.append(dict(nid=nid, error=repr(e)[:160]))
            continue
        rows.append(dict(nid=nid, cls=cls, a212=V[nid]["verdict"], dpin=dpin, klass=("b" if r["holds"] else "a"),
                         g=r["g"], assignment=r["assignment"], why=r["why"], n_H=len(hb)))
    n = lambda f: sum(1 for r in rows if f(r))                 # noqa: E731
    out = dict(pad=a.pad, lam=float(RAY.PADS[a.pad]), margin=str(RAY.MARGIN),
               drift={k: float(v) for k, v in drift(a.pad).items()},
               n=len(rows), errors=err,
               counts=dict(a=n(lambda r: r["klass"] == "a"), b=n(lambda r: r["klass"] == "b"),
                           a_alive=n(lambda r: r["klass"] == "a" and r["a212"] == "ALIVE"),
                           b_alive=n(lambda r: r["klass"] == "b" and r["a212"] == "ALIVE"),
                           a_dead=n(lambda r: r["klass"] == "a" and r["a212"] == "DEAD"),
                           b_dead=n(lambda r: r["klass"] == "b" and r["a212"] == "DEAD"),
                           dpin_zero=n(lambda r: r["dpin"] <= 0.0), dpin_slack=n(lambda r: r["dpin"] > 0.0)),
               rows=rows)
    o = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(o), exist_ok=True)
    with open(o, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    print("pad %s (lam %.6f, pin drift %.4g / %.4g): %d nodes -> (a) %d [%d alive, %d dead], (b) %d [%d alive, %d dead]" % (
        a.pad, out["lam"], out["drift"]["1/2"], out["drift"]["3/2"], out["n"],
        out["counts"]["a"], out["counts"]["a_alive"], out["counts"]["a_dead"],
        out["counts"]["b"], out["counts"]["b_alive"], out["counts"]["b_dead"]))
    print("   pin slack of the records: delta_pin = 0 on %d, > 0 on %d (%s)" % (
        out["counts"]["dpin_zero"], out["counts"]["dpin_slack"],
        ", ".join("%s=%g" % (r["nid"], r["dpin"]) for r in rows if r["dpin"] > 0)))
    if err:
        print("   %d record(s) could not be read: %s" % (len(err), err[:3]))
    print("   -> %s" % os.path.relpath(o, ROOT).replace("\\", "/"))


if __name__ == "__main__":
    main()
