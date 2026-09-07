"""A117 T2 -- does a replayed TC fire transfer to the WHOLE WINDOW, or only to its own side?

Lemma TC is side-blind: it sees two bins.  A bin need not be.  For each A112 TC fire this script
decides, from the node record's own hypothesis, whether BOTH boxes of the fire are s-INDEPENDENT:

* a branch/conditioned bin is the node's own support box, emitted at one side and not a function
  of s -- s-independent by construction;
* a CLASS PIN box is centred on a core `(kx, ky)`; it is s-independent exactly when A96's
  `core_affine` gives beta = 0 on BOTH coordinates (a bottom/left slot anchor such as 1/2 or 3/2),
  and it MOVES with the side when beta = 1 (a top/right anchor such as s - 1/2) or when the
  coordinate is a cover-family coordinate `c0 + q(s - 2c0)`.

A fire whose two boxes are both s-independent kills the pair at EVERY side of the window.
Writes results/tc_sidecheck.json.  Read-only on A112.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction as F

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A96-a57-parametric", "code"))
import to_param96 as T96                                          # noqa: E402


def beta_of(coord):
    try:
        return T96.core_affine(coord)[1]
    except Exception:
        return None                       # not a slot and not in Q_dy: no parametric anchoring


def main():
    tc = json.load(open(os.path.join(RES, "tc_replay.json")))
    rows = []
    for r in tc["rows"]:
        if r["src"] != "A112":
            continue
        rec = json.load(open(os.path.join(ROOT, r["record"])))
        cores = (rec.get("hyp") or {}).get("cores") or []
        info = []
        for nm, bx in zip(r["pair"], [None, None]):
            if not str(nm).lower().startswith("pin"):
                info.append(dict(name=nm, kind="bin", s_independent=True,
                                 why="node's own support box, not a function of s"))
                continue
            k = int(str(nm)[3:])
            c = cores[k] if k < len(cores) else None
            if c is None:
                info.append(dict(name=nm, kind="pin", s_independent=None, why="pin not in record"))
                continue
            bx_, by_ = beta_of(c["kx"]), beta_of(c["ky"])
            info.append(dict(name=nm, kind="pin", kx=str(c["kx"]), ky=str(c["ky"]),
                             beta_x=(str(bx_) if bx_ is not None else None),
                             beta_y=(str(by_) if by_ is not None else None),
                             s_independent=(bx_ == F(0) and by_ == F(0)),
                             why=("both core coordinates are slot anchors with beta = 0"
                                  if bx_ == F(0) and by_ == F(0)
                                  else "a core coordinate moves with s (beta != 0) or has no "
                                       "parametric anchoring")))
        wv = all(b.get("s_independent") is True for b in info)
        rows.append(dict(record=r["record"], region=r["region"], ordering=r["ordering"],
                         node=r["node"], pair=r["pair"], kind=r["kind"],
                         boxes=info, window_valid=wv))
    n_wv = sum(1 for r in rows if r["window_valid"])
    doc = dict(n=len(rows), window_valid=n_wv, side_local=len(rows) - n_wv,
               note=("A111's fires are NOT included: both boxes there are derived from a shadow "
                     "at its own side s* and mapped into the node's frame, so their transfer to "
                     "the window is A111's frame-slack question (|s* - s0| = 0.0097 for S02, "
                     "0.0085 for S07), not settled by this script."),
               rows=rows)
    json.dump(doc, open(os.path.join(RES, "tc_sidecheck.json"), "w"), indent=1)
    print("A112 TC fires: %d, window-valid (both boxes s-independent) %d, side-local %d"
          % (len(rows), n_wv, len(rows) - n_wv))
    for r in rows:
        print("  %-34s %-9s %-14s %s  %s" % (r["region"], r["ordering"], "/".join(r["pair"]),
                                             "WINDOW" if r["window_valid"] else "s0-only",
                                             r["boxes"][1].get("why", "")[:60]))


if __name__ == "__main__":
    main()
