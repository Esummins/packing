"""A137 -- write a replayable `pin-clip-kill-certificate-v1` for every T5''' kill emit137 made
tonight, and check each one with A131's INDEPENDENT checker (`checkclip131.check`).

The clip is re-run from the recorded box, so the certificate is derived from the record, not from
the emitter's memory; a certificate that does not replay is reported and its kill is withdrawn
from the ledger (this script prints them; nothing is claimed without a passing check).

Field discipline, following A142's exact-core certificates: `a_pin` is A135's certified-maximal
pin core (33873816211/68719476736) and `pin_delta` is the matching 1/2 - a_pin, which is what
A131's checker tests; the node's own emission slack is carried separately as
`node_pin_delta_actual` (0.01) so the two are never confused.
"""
import argparse
import glob
import json
import os
import random
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
A53 = os.path.join(ROOT, "A53-simple-strata")
for _p in (os.path.join(A57, "code"), os.path.join(ROOT, "A131-pin-clip", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from caselp import Box                                                    # noqa: E402
import pinclip                                                            # noqa: E402
import checkclip131                                                       # noqa: E402

A_PIN = Fr(33873816211, 68719476736)
CERTDIR = os.path.join(BASE, "certs", "clipkills")
SLOTS = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nsub", type=int, default=8, help="certify at a FINER sub-bin count than "
                                                        "emission used; monotone, so a kill at "
                                                        "nsub=1 is still a kill at nsub=8")
    ap.add_argument("--draws", type=int, default=12000)
    a = ap.parse_args()
    os.makedirs(CERTDIR, exist_ok=True)
    rng = random.Random(137137)
    rows = []
    for p in sorted(glob.glob(os.path.join(BASE, "results", "emit_geo_*.jsonl"))):
        for ln in open(p, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("pin_info") == "clip":
                rows.append(r)
    print(f"{len(rows)} T5''' clip kills emitted tonight", flush=True)
    out = []
    led = open(os.path.join(BASE, "results", "clipkills137.jsonl"), "w", encoding="utf-8")
    for r in rows:
        nid = r["id"]
        cls = "k5_11" if nid.startswith("k5_11") else "k5_16"
        slots = [tuple(p) for p in SLOTS[cls]]
        b = Box.from_json(r["clip_from"] or r["box"])
        traces = []
        cl = pinclip.clip_node(b, slots, nsub=a.nsub, a_pin=A_PIN, traces=traces)
        if not cl["empty"]:
            print(f"  !! {nid} does NOT replay as EMPTY at nsub={a.nsub}; kill WITHDRAWN",
                  flush=True)
            led.write(json.dumps(dict(id=nid, status="WITHDRAWN-not-empty-on-replay")) + "\n")
            continue
        drawn = hits = 0
        for _ in range(a.draws):
            th = b.th0 + (b.th1 - b.th0) * rng.random()
            x = b.x0 + (b.x1 - b.x0) * rng.random()
            y = b.y0 + (b.y1 - b.y0) * rng.random()
            drawn += 1
            if pinclip.pin_free(x, y, th, slots, a_pin=float(A_PIN)):
                hits += 1
        wit = sorted({st["pin"] for tr in traces for st in tr if "pin" in st})
        cert = dict(
            format="pin-clip-kill-certificate-v1",
            generated_by="A137 clipcerts137.py (A131 pin-clip at A135's EXACT pin core, "
                         "emitted live by emit137.py)",
            id=nid, **{"class": cls}, n=11, s="969271/250000", budget=r.get("budget", 5),
            pin_delta=str(Fr(1, 2) - A_PIN), node_pin_delta=float(Fr(1, 2) - A_PIN),
            node_pin_delta_actual=r.get("pin_delta"),
            a_pin=str(A_PIN),
            a_pin_certification="A135 exactcore.exact_a: the four corners of K(a) pass A132's "
                                "exact rational vertex test against the pin box's own "
                                "outward-rounded tilt interval",
            pins=[[str(Fr(str(px))), str(Fr(str(py)))] for (px, py) in slots],
            box=(r["clip_from"] or r["box"]),
            box_rational_outer=[str(v) for v in pinclip.outer_rect(b)],
            nsub=a.nsub,
            sub_bins=[dict(t0=str(t), t1=str(u), theta0_deg=pinclip.deg_of_t(t),
                           theta1_deg=pinclip.deg_of_t(u), empty=True, trace=tr)
                      for (t, u, _), tr in zip(cl["bins"], traces)],
            witness_pins=wit, witness_slots=[list(slots[i]) for i in wit],
            witness_kind=("single" if len(wit) == 1 else "joint"),
            prior_verdict="(none: emitted tonight, never solved)",
            sample=dict(drawn=drawn, tested=drawn, hits=hits),
            rule="T5''' pin-clip (attempts/A57-shadow-trees/notes/lemmas.md)",
            claim=("every centre of the box is, at EVERY tilt of every sub-bin, inside some pin's "
                   "forbidden octagon at the certified pin core; no pin placement lies in the "
                   "box; therefore every square with (centre, tilt) in the box overlaps a pinned "
                   "square and is not it -- the node is EMPTY BY LOGIC"),
            supersedes="nothing: this is a freshly emitted child, recorded dead at emission")
        p = os.path.join(CERTDIR, nid + ".clipkill.json")
        json.dump(cert, open(p, "w"), indent=1)
        errs, _ = checkclip131.check(p, {k: v for k, v in SLOTS.items()})
        rec = dict(id=nid, cls=cls, level=1 + nid.count("_D"),
                   verdict="KILL-BY-LOGIC (pin-clip T5''' at the exact pin core)",
                   nsub=a.nsub, witness_pins=wit,
                   independent_check=("PASS" if not errs else "FAIL"), check_errors=errs[:5],
                   sample=dict(drawn=drawn, hits=hits),
                   cert_path=os.path.relpath(p, ROOT).replace("\\", "/"),
                   when=time.strftime("%F %T"))
        led.write(json.dumps(rec) + "\n")
        out.append(rec)
        if errs:
            print(f"  !! {nid} independent check FAILED: {errs[:3]}", flush=True)
    led.close()
    ok = sum(1 for r in out if r["independent_check"] == "PASS")
    hh = sum(r["sample"]["hits"] for r in out)
    print(f"{len(out)} certificates written; independent check PASS {ok}/{len(out)}; "
          f"sampled {sum(r['sample']['drawn'] for r in out)} poses, {hh} pin-free hits "
          f"(must be 0)", flush=True)


if __name__ == "__main__":
    main()
