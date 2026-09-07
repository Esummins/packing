"""A131 follow-up -- the RETROSPECTIVE BACKLOG SWEEP: pure geometry, no LP.

For each of the recorded-open A57 nodes that the pin-clip empties (`results/backlog131.jsonl`),
emit a `pin-clip-kill-certificate-v1` under `certs/backlog/` and a ledger row in
`results/backlog_kills.jsonl`, then verify every certificate with the INDEPENDENT checker
(`checkclip131.py`, which re-derives the dead test in the t-parametrisation and shares no
decision code with `pinclip.py`).

WRITES NOTHING INTO A57 OR A96.  Their jsonl / progress / cert trees are untouched; these rows
supersede nothing until the A57 owner folds them in at resume.

    python code/backlog_certs131.py [--nsub 8] [--draws 12000]
"""
import argparse, collections, json, math, os, random, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ATT, "A57-shadow-trees")
A53 = os.path.join(ATT, "A53-simple-strata")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(A57, "code"))

import pinclip
import checkclip131
from caselp import Box

SLOTS = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
CERTDIR = os.path.join(BASE, "certs", "backlog")
LEDGER = os.path.join(BASE, "results", "backlog_kills.jsonl")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nsub", type=int, default=8)
    ap.add_argument("--draws", type=int, default=12000)
    a = ap.parse_args()
    os.makedirs(CERTDIR, exist_ok=True)
    rng = random.Random(131131)
    rows = [json.loads(l) for l in open(os.path.join(BASE, "results", "backlog131.jsonl"))]
    print(f"{len(rows)} recorded-open nodes to certify", flush=True)

    t0 = time.time()
    out = []
    with open(LEDGER, "w") as led:
        for n, r in enumerate(rows):
            nid, cls = r["id"], r["cls"]
            slots = SLOTS[cls]
            b = Box.from_json(r["box"])
            traces = []
            cl = pinclip.clip_node(b, slots, nsub=a.nsub, traces=traces)
            if not cl["empty"] or cl["n_empty"] != a.nsub:
                print(f"  !! {nid} is NOT empty at nsub={a.nsub}; skipping", flush=True)
                continue
            # sampled confirmation: the WHOLE box x tilt bin is discarded, so drawn == tested
            drawn = tested = hits = 0
            for _ in range(a.draws):
                th = b.th0 + (b.th1 - b.th0) * rng.random()
                x = b.x0 + (b.x1 - b.x0) * rng.random()
                y = b.y0 + (b.y1 - b.y0) * rng.random()
                drawn += 1
                tested += 1
                if pinclip.pin_free(x, y, th, slots):
                    hits += 1
            wit = sorted({st["pin"] for tr in traces for st in tr if "pin" in st})
            cert = dict(
                format="pin-clip-kill-certificate-v1",
                generated_by="A131 backlog_certs131.py",
                id=nid, node_class=cls, **{"class": cls},
                n=11, s="969271/250000", budget=r.get("prior_tau") and 5 or 5,
                pin_delta=str(pinclip.DELTA), node_pin_delta=0.01,
                a_pin=str(pinclip.A_PIN),
                pins=[[str(Fr(str(px))), str(Fr(str(py)))] for (px, py) in slots],
                box=r["box"],
                box_rational_outer=[str(v) for v in pinclip.outer_rect(b)],
                nsub=a.nsub,
                sub_bins=[dict(t0=str(t), t1=str(u),
                               theta0_deg=pinclip.deg_of_t(t), theta1_deg=pinclip.deg_of_t(u),
                               empty=True, trace=tr)
                          for (t, u, _), tr in zip(cl["bins"], traces)],
                witness_pins=wit,
                witness_slots=[list(slots[i]) for i in wit],
                witness_kind=r["witness_kind"],
                prior_verdict=r["prior_verdict"], prior_tau=r.get("prior_tau"),
                prior_eta=r.get("prior_eta"),
                t5pp_alone_empties=r["t5pp_alone_empties"],
                sample=dict(drawn=drawn, tested=tested, hits=hits),
                rule="T5''' pin-clip (attempts/A57-shadow-trees/notes/lemmas.md)",
                claim=("every centre of the box is, at EVERY tilt of every sub-bin, inside some "
                       "pin's forbidden octagon; no pin placement lies in the box; therefore every "
                       "square with (centre, tilt) in the box overlaps a pinned square and is not "
                       "it, so the node's hypotheses are contradictory and the node is EMPTY BY "
                       "LOGIC -- no LP, no measure certificate"),
                supersedes="nothing: A57/A96 state is untouched; the A57 owner folds this in at resume")
            cert.pop("node_class")
            p = os.path.join(CERTDIR, nid + ".clipkill.json")
            json.dump(cert, open(p, "w"), indent=1)
            errs, _ = checkclip131.check(p, SLOTS)
            rec = dict(id=nid, cls=cls, level=r["level"], prior_verdict=r["prior_verdict"],
                       prior_tau=r.get("prior_tau"), prior_eta=r.get("prior_eta"),
                       new_verdict="KILL-BY-LOGIC (pin-clip T5''')",
                       nsub=a.nsub, box=r["box"],
                       tilt_sub_bins=[[pinclip.deg_of_t(t), pinclip.deg_of_t(u)]
                                      for (t, u, _) in cl["bins"]],
                       witness_pins=wit, witness_slots=[list(slots[i]) for i in wit],
                       witness_kind=r["witness_kind"],
                       t5pp_alone_empties=r["t5pp_alone_empties"],
                       needs_two_pin_joint=(r["witness_kind"] != "single"),
                       exact_decision="rational (t = tan(theta/2)); no epsilon",
                       sample=dict(drawn=drawn, tested=tested, hits=hits),
                       independent_check=("PASS" if not errs else "FAIL"),
                       check_errors=errs[:5],
                       cert_path=os.path.relpath(p, BASE).replace("\\", "/"))
            led.write(json.dumps(rec) + "\n")
            out.append(rec)
            if (n + 1) % 25 == 0:
                print(f"  {n+1}/{len(rows)}  {time.time()-t0:.0f}s", flush=True)

    ok = sum(1 for r in out if r["independent_check"] == "PASS")
    hits = sum(r["sample"]["hits"] for r in out)
    drawn = sum(r["sample"]["drawn"] for r in out)
    tested = sum(r["sample"]["tested"] for r in out)
    joint = [r["id"] for r in out if r["needs_two_pin_joint"]]
    summ = dict(
        nodes=len(out), nsub=a.nsub,
        independent_check=dict(passed=ok, failed=len(out) - ok),
        sample_totals=dict(drawn=drawn, tested=tested, hits=hits,
                           min_tested_per_node=min((r["sample"]["tested"] for r in out), default=0)),
        by_level=dict(collections.Counter(r["level"] for r in out)),
        by_class=dict(collections.Counter(r["cls"] for r in out)),
        by_prior_verdict=dict(collections.Counter(r["prior_verdict"] for r in out)),
        by_witness_kind=dict(collections.Counter(r["witness_kind"] for r in out)),
        single_pin=sum(1 for r in out if not r["needs_two_pin_joint"]),
        two_pin_joint=len(joint), two_pin_joint_ids=joint,
        t5pp_alone_suffices=sum(1 for r in out if r["t5pp_alone_empties"]),
        needs_the_clip=sum(1 for r in out if not r["t5pp_alone_empties"]),
        seconds=round(time.time() - t0, 1),
        note=("recorded-open A57 nodes killed by T5''' geometry alone; A57/A96 state UNTOUCHED, "
              "the A57 owner folds this in at resume (PAUSED.md v2 resume block)"))
    json.dump(summ, open(os.path.join(BASE, "results", "backlog_kills.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
