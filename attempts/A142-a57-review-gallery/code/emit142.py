"""A142 follow-up -- replayable kill certificates for the nodes the EXACT-pin-core clip empties.

A131's clip is deployed at the STOCK pin core `a_pin = 1/2 - delta = 0.49`.  A135's `exactcore`
certifies the pin's guaranteed core to be the larger square of half-side

    a_pin = 33873816211/68719476736 = 0.49292890196375083          (the 1/2^40 grid, reduced)

and the frozen verifiers take the core half-side VERBATIM, so enlarging it is sound for the clip
for the verifier's own reason: the conditioned square is interior-disjoint from the pin square,
and the pin square CONTAINS K'(P) at every pose of the pin box (certified vertex by vertex).
A60's pins are EXACT placements (box x0 = x1), so their guaranteed core is the whole unit square
and `a_pin` is 1/2 to the grid.

This emits, for each node the exact-core clip empties, a `pin-clip-kill-certificate-v1` in
A131's own format -- so A131's INDEPENDENT checker `checkclip131.check` reads it unchanged -- with

  * `a_pin`      = the exact half-side actually used in the clip, as a rational string;
  * `pin_delta`  = 1/2 - a_pin (the checker's identity `a_pin = 1/2 - pin_delta`), and
    `node_pin_delta` its float, so the checker's second clause passes on the EXACT inset rather
    than on the deployed one; the deployed delta is kept alongside as `node_delta_deployed`;
  * `exactcore_certification` = A135's `exact_a` result for every pin box (a_exact, a_stock, the
    vertex test verdict, the grid), which is what licenses the larger a_pin;
  * the full per-sub-bin replay trace, unchanged, so the checker replays every slab step.

Writes ONLY under attempts/A142-a57-review-gallery/certs/{a57,a60}/ and results/.  A57, A96 and
A60 state is untouched; the owners fold these in at resume.

    set PYTHONDONTWRITEBYTECODE=1 && python code/emit142.py [--nsub 8] [--draws 12000]
"""
import argparse
import collections
import json
import os
import random
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A53 = os.path.join(ATT, "A53-simple-strata")
A57 = os.path.join(ATT, "A57-shadow-trees")
A131 = os.path.join(ATT, "A131-pin-clip")
A135 = os.path.join(ATT, "A135-polycore-verifier")
for p in (os.path.join(A57, "code"), os.path.join(A131, "code"),
          os.path.join(ATT, "A132-polygon-core", "code"), os.path.join(A135, "code"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import pinclip                                                # noqa: E402
import checkclip131                                           # noqa: E402
import exactcore                                              # noqa: E402
import trim57                                                 # noqa: E402  (read-only)
from caselp import Box, t_lo, t_hi                             # noqa: E402
import gallery142 as G                                        # noqa: E402

SLOTS = json.load(open(os.path.join(A53, "results", "name_to_slots.json"), encoding="utf-8"))
S_RAT = pinclip.S_RAT


def class_of(camp, nid):
    if camp == "A60":
        return "trump5"
    return "k5_11" if nid.startswith("k5_11") else "k5_16"


def witness_kind(traces):
    """'single' when one pin alone empties every sub-bin; 'joint-k' otherwise."""
    per = [sorted({st["pin"] for st in tr if "pin" in st}) for tr in traces]
    k = max((len(p) for p in per), default=0)
    return "single" if k <= 1 else f"joint-{k}"


def t5pp_alone(box, slots):
    try:
        alive, _dead = trim57.split_bin(box, [tuple(p) for p in slots])
        return not alive
    except Exception:
        return None


def emit(camp, nodes, certdir, ledger, nsub, draws, rng, pop):
    os.makedirs(certdir, exist_ok=True)
    rank = {r["id"]: r for r in (pop["rank_a57"] + pop["rank_a60"])}
    out = []
    with open(ledger, "w", encoding="utf-8") as led:
        for nid in nodes:
            d, recpath = G.load_node(camp, nid)
            boxes = d["hyp"]["boxes"]
            cls = class_of(camp, nid)
            slots = SLOTS[cls]
            b = Box.from_json(boxes[-1])

            # ---- A135: certify the exact core of every PIN box (tilt width 0)
            certs, a_ex = [], None
            for i, bb in enumerate(boxes[:-1]):
                if bb["th1"] > bb["th0"] + 1e-12:
                    continue                       # a tilt window: a conditioned square, not a pin
                Bi = Box.from_json(bb)
                a, a0, ok = exactcore.exact_a(Bi)
                ki = Bi.core()
                certs.append(dict(pin=i, a_exact=str(a), a_exact_float=float(a),
                                  a_stock=str(Fr(a0).limit_denominator(10 ** 18)),
                                  a_stock_float=float(a0), deployed_core_certified=bool(ok),
                                  vertex_test=bool(exactcore.a_ok(Bi, ki.kx, ki.ky, ki.cm, ki.sm,
                                                                  a, t_lo(Bi.th0), t_hi(Bi.th1))),
                                  grid="1/2**40 (exactcore.ADEN)"))
                a_ex = a if a_ex is None else min(a_ex, a)
            assert a_ex is not None, nid

            # ---- the clip AT THAT a_pin, with the replay traces
            traces = []
            cl = pinclip.clip_node(b, slots, nsub=nsub, a_pin=a_ex, traces=traces)
            if not cl["empty"] or cl["n_empty"] != nsub:
                print(f"  !! {nid}: NOT empty at a_pin = {a_ex} (nsub {nsub}); SKIPPED",
                      flush=True)
                continue

            # ---- sampled confirmation: the whole box x tilt bin is discarded
            drawn = tested = hits = 0
            for _ in range(draws):
                th = b.th0 + (b.th1 - b.th0) * rng.random()
                x = b.x0 + (b.x1 - b.x0) * rng.random()
                y = b.y0 + (b.y1 - b.y0) * rng.random()
                drawn += 1
                tested += 1
                if pinclip.pin_free(x, y, th, slots, a_pin=float(a_ex)):
                    hits += 1
            wit = sorted({st["pin"] for tr in traces for st in tr if "pin" in st})
            wk = witness_kind(traces)
            r = rank.get(nid, {})
            delta = Fr(1, 2) - a_ex
            cert = dict(
                format="pin-clip-kill-certificate-v1",
                generated_by="A142 emit142.py (A131 pin-clip at A135's EXACT pin core)",
                id=nid, **{"class": cls},
                n=11, s=str(S_RAT), budget=int(d.get("budget") or 5),
                pin_delta=str(delta), node_pin_delta=float(delta),
                node_delta_deployed=(0.0 if camp == "A60" else 0.01),
                a_pin=str(a_ex), a_pin_float=float(a_ex),
                a_pin_deployed=str(pinclip.A_PIN),
                exactcore_certification=dict(
                    source="A135-polycore-verifier/code/exactcore.py exact_a / a_ok",
                    claim="K(pin centre, tilt 0, a_exact) is contained in the pinned unit square "
                          "at EVERY pose of the pin's box, certified corner by corner in exact "
                          "rationals (polycore.vertex_ok); the frozen verifiers take the core "
                          "half-side verbatim, so the larger a_pin needs no verifier change",
                    pins=certs, all_certified=all(c["vertex_test"] for c in certs)),
                pins=[[str(Fr(str(px))), str(Fr(str(py)))] for (px, py) in slots],
                box=boxes[-1],
                box_rational_outer=[str(v) for v in pinclip.outer_rect(b)],
                nsub=nsub,
                sub_bins=[dict(t0=str(t), t1=str(u),
                               theta0_deg=pinclip.deg_of_t(t), theta1_deg=pinclip.deg_of_t(u),
                               empty=True, trace=tr)
                          for (t, u, _), tr in zip(cl["bins"], traces)],
                witness_pins=wit, witness_slots=[list(slots[i]) for i in wit],
                witness_kind=wk,
                prior_verdict=(r.get("verdict") or "ALIVE"),
                prior_tau=(r.get("tau") if camp == "A60" else None) or float(d.get("tau") or 0.0),
                prior_eta=float(d.get("tau") or 0.0) - int(d.get("budget") or 5),
                record=recpath,
                t5pp_alone_empties=t5pp_alone(b, slots),
                empty_at_deployed_a_pin=False,
                sample=dict(drawn=drawn, tested=tested, hits=hits),
                rule="T5''' pin-clip (attempts/A57-shadow-trees/notes/lemmas.md) run at the "
                     "A135-certified EXACT pin core instead of the deployed 1/2 - delta",
                claim=("every centre of the box is, at EVERY tilt of every sub-bin, inside some "
                       "pin's forbidden octagon built on the pin's CERTIFIED EXACT core; no pin "
                       "placement lies in the box; therefore every square with (centre, tilt) in "
                       "the box overlaps a pinned square and is not it, so the node's hypotheses "
                       "are contradictory and the node is EMPTY BY LOGIC -- no LP, no measure "
                       "certificate"),
                supersedes="nothing: A57 / A96 / A60 state is untouched; the owner folds this in "
                           "at resume")
            p = os.path.join(certdir, nid + ".clipkill.json")
            json.dump(cert, open(p, "w", encoding="utf-8"), indent=1)
            errs, _ = checkclip131.check(p, SLOTS)
            rec = dict(id=nid, camp=camp, cls=cls, level=int(r.get("level") or
                                                             1 + nid.count("_D")),
                       prior_verdict=cert["prior_verdict"], prior_tau=cert["prior_tau"],
                       prior_eta=cert["prior_eta"],
                       new_verdict="KILL-BY-LOGIC (pin-clip T5''' at the exact pin core)",
                       a_pin=str(a_ex), a_pin_deployed=str(pinclip.A_PIN),
                       empty_at_deployed_a_pin=False,
                       nsub=nsub, box=boxes[-1],
                       tilt_sub_bins=[[pinclip.deg_of_t(t), pinclip.deg_of_t(u)]
                                      for (t, u, _) in cl["bins"]],
                       witness_pins=wit, witness_slots=[list(slots[i]) for i in wit],
                       witness_kind=wk, t5pp_alone_empties=cert["t5pp_alone_empties"],
                       exactcore_all_certified=cert["exactcore_certification"]["all_certified"],
                       exact_decision="rational (t = tan(theta/2)); no epsilon",
                       sample=dict(drawn=drawn, tested=tested, hits=hits),
                       independent_check=("PASS" if not errs else "FAIL"),
                       check_errors=errs[:5],
                       cert_path=os.path.relpath(p, BASE).replace("\\", "/"))
            led.write(json.dumps(rec) + "\n")
            out.append(rec)
            print(f"  {nid:30s} {rec['independent_check']}  wit {wit} ({wk})  "
                  f"sample hits {hits}/{tested}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nsub", type=int, default=8)
    ap.add_argument("--draws", type=int, default=12000)
    a = ap.parse_args()
    t0 = time.time()
    pop = json.load(open(os.path.join(BASE, "results", "population142.json"), encoding="utf-8"))
    cs = json.load(open(os.path.join(BASE, "results", "clipsweep142.json"), encoding="utf-8"))
    a57 = cs["a57"]["new_empty_under_exact"]
    r60 = json.load(open(os.path.join(BASE, "results", "clipsweep142_A60.json"),
                         encoding="utf-8"))
    a60 = [r["id"] for r in r60 if r.get("empty_exact")]
    print(f"A57 {len(a57)} nodes, A60 {len(a60)} nodes", flush=True)
    rng = random.Random(142142)
    o57 = emit("A57", a57, os.path.join(BASE, "certs", "a57"),
               os.path.join(BASE, "results", "exactclip_kills_a57.jsonl"), a.nsub, a.draws,
               rng, pop)
    o60 = emit("A60", a60, os.path.join(BASE, "certs", "a60"),
               os.path.join(BASE, "results", "exactclip_kills_a60.jsonl"), a.nsub, a.draws,
               rng, pop)

    def summ(o, camp):
        return dict(camp=camp, nodes=len(o),
                    independent_check=dict(
                        passed=sum(1 for r in o if r["independent_check"] == "PASS"),
                        failed=sum(1 for r in o if r["independent_check"] != "PASS")),
                    sample_totals=dict(drawn=sum(r["sample"]["drawn"] for r in o),
                                       tested=sum(r["sample"]["tested"] for r in o),
                                       hits=sum(r["sample"]["hits"] for r in o)),
                    by_level=dict(collections.Counter(r["level"] for r in o)),
                    by_class=dict(collections.Counter(r["cls"] for r in o)),
                    by_witness_kind=dict(collections.Counter(r["witness_kind"] for r in o)),
                    t5pp_alone_suffices=sum(1 for r in o if r["t5pp_alone_empties"]),
                    exactcore_all_certified=all(r["exactcore_all_certified"] for r in o))
    S = dict(a57=summ(o57, "A57"), a60=summ(o60, "A60"),
             a_pin_exact="33873816211/68719476736 = 0.49292890196375083 (A57 pins, delta = 1e-2); "
                         "A60's pins are exact placements, a_pin = 1/2 to the 1/2**40 grid",
             a_pin_deployed=str(pinclip.A_PIN),
             checker="A131 checkclip131.check, unchanged, on every certificate",
             seconds=round(time.time() - t0, 1),
             note="A57 / A96 / A60 state UNTOUCHED; one line appended to A57's PAUSED.md resume "
                  "block and to A60's notes/ledger.md so the owners fold them in")
    p = os.path.join(BASE, "results", "exactclip_kills.json")
    json.dump(S, open(p, "w", encoding="utf-8"), indent=1)
    print(json.dumps(S, indent=1))
    print("wrote", p)


if __name__ == "__main__":
    main()
