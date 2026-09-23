"""A269 task 1 -- RE-EMIT A60's 149 trump5 records with SLACK pin cores (notes/trump5_row.md s.1).

Source: the 149 nodes of A256's triage (results/triage256.json: A212's 84 ALIVE + 65 DEAD at pad 0), each an A60 record
attempts/A60-trump5-campaign/results/nodes/<nid>.json (hyp.boxes / hyp.cores, geo178.load_record's format; the 13
gallery pages are A60 records too).  A60's files are READ ONLY; the re-emitted records go to records/<nid><suffix>.json.

The rewrite touches ONE hypothesis field: the five pin cores' half-side a := 1/2 - delta_pin (geo178.load_record reads a pin's
slack as dpin = 1/2 - a; its role box is then kx +- dpin, ky +- dpin, tilt 0).  Boxes, the H boxes and every other
hypothesis field are copied (json round trip); A60's LP payload (rows_all / atoms_all / hist_tail, ~220 kB, no part of the
hypothesis) is dropped and the source is cited by sha256.  Each record then states exactly:

  HYP(nid, delta, lam):  P is a packing of eleven unit squares at a side m in (s0/lam, s0] whose five class pins are
  trump5's corner squares (upright, centres at slots(m) = alpha + beta m), and whose dilate F = Delta_{s0/m} P has
  (i) pin k an upright unit square centred within delta of slot_k(s0) (box kx +- delta, ky +- delta), and
  (ii) its H square(s) with centre and tilt in the record's H box(es).
  (i) is IMPLIED by the class for every m in the slab (Corollary B': drift (lam - 1)|alpha| <= (lam - 1)3/2 < delta,
  pads269.py); so HYP is "trump5 at m in the slab with H in the box", and a DEAD at pad lam is a window statement.

    python reemit269.py            -> records/*_r269a.json (pad tube, 9/500), *_r269b.json (pad window, 9/400), records/index.json
"""
import hashlib
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
sys.path.insert(0, HERE)
import pads269 as PD                                           # noqa: E402

SRC = os.path.join(ROOT, "attempts", "A60-trump5-campaign", "results", "nodes")
TRIAGE = os.path.join(ROOT, "attempts", "A256-trump5-passes", "results", "triage256.json")
OUT = os.path.join(ATT, "records")
DROP = ("rows_all", "atoms_all", "hist_tail")


def population():
    d = json.load(open(TRIAGE, encoding="utf-8"))
    return [(r["nid"], r["a212"], r.get("dpin")) for r in d["rows"]]


def is_pin(b):
    return abs(float(b["th1"]) - float(b["th0"])) < 1e-9 and abs(float(b["x1"]) - float(b["x0"])) < 0.05


def reemit(nid, pad):
    f = os.path.join(SRC, "%s.json" % nid)
    raw = open(f, "rb").read()
    d = json.loads(raw.decode("utf-8"))
    dropped = [k for k in DROP if d.pop(k, None) is not None]      # A60's LP data (~220 kB): not hypothesis, cited by sha256
    hyp = d["hyp"]
    delta = PD.DPIN[pad]
    a = Fr(1, 2) - delta
    pins = [k for k, b in enumerate(hyp["boxes"]) if is_pin(b)]
    if len(pins) != 5:
        raise SystemExit("A269: %s has %d pin boxes, not trump5's five" % (nid, len(pins)))
    old = sorted({str(hyp["cores"][k]["a"]) for k in pins})
    for k in pins:
        c = hyp["cores"][k]
        hyp["cores"][k] = dict(c, a=str(a), float=dict(c.get("float") or {}, a=float(a)))
    new = "%s%s" % (nid, PD.SUFFIX[pad])
    d["a269"] = dict(source=os.path.relpath(f, ROOT).replace("\\", "/"), source_sha256=hashlib.sha256(raw).hexdigest(),
                     nid_source=nid, pad=pad, lam=str(PD.LAM[pad]), slab=["%s" % PD.S_BOT[pad], str(PD.S0)],
                     delta_pin=str(delta), dropped_lp_fields=dropped, pin_indices=pins, pin_a_before=old, pin_a_after=str(a),
                     hypothesis=("HYP(%s, delta_pin = %s, lam = %s): a packing P of 11 unit squares at a side m in (%s, s0] "
                                 "with trump5's five class pins (upright corner squares at slots(m)) whose dilate "
                                 "F = Delta_{s0/m} P has every pin within delta_pin of slot(s0) -- implied by the class, "
                                 "Corollary B', drift (lam - 1)*3/2 = %.7f < %s -- and its H square(s) in the H box(es) of "
                                 "A60's record %s (copied unchanged)." % (new, delta, PD.LAM[pad], float(PD.S_BOT[pad]),
                                                                         float((PD.LAM[pad] - 1) * PD.A_T5), delta, nid)),
                     what="A269 re-emission (code/reemit269.py): ONLY the five pin cores' a changed (1/2 - delta_pin); "
                          "A60's tree kills above this record were proved at delta_pin = 3.08e-8 and do NOT inherit.")
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "%s.json" % new)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, indent=1)
    return new, p, old, len(hyp["boxes"]) - 5


def main():
    rows, idx = population(), []
    for nid, a212, dp in rows:
        for pad in ("tube", "window"):
            new, p, old, nh = reemit(nid, pad)
            idx.append(dict(nid=new, source=nid, pad=pad, delta_pin=str(PD.DPIN[pad]), a212_pad0=a212, dpin_before=dp,
                            pin_a_before=old, n_H=nh, record=os.path.relpath(p, ROOT).replace("\\", "/")))
    json.dump(dict(n_source=len(rows), n_records=len(idx), pads={p: dict(lam=str(PD.LAM[p]), delta_pin=str(PD.DPIN[p]))
                                                              for p in ("tube", "window")}, rows=idx),
              open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"), indent=1)
    print("re-emitted %d records from %d A60 records (%d with 2 H boxes); pin a before: %s" % (
        len(idx), len(rows), sum(1 for r in idx if r["n_H"] > 1) // 2, sorted({x for r in idx for x in r["pin_a_before"]})))


if __name__ == "__main__":
    main()
