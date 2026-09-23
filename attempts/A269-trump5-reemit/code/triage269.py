"""A269 -- the (a)/(b) triage of the RE-EMITTED records at their own pads (A256's classify256 / ray256, read-only).

(b) = the record's ROOT boxes (pins widened by the pad's drift, outward margin; H boxes) might hold a D4 image of the
contracted Trump configuration Delta_{s0/m}(z-hat - t v) for some m in the slab -- the only roots where Lemma
TUBE-KILL is needed at all.  An (a) verdict at the root holds for the whole subtree (the cascade only shrinks).

    python triage269.py     -> results/triage269.json (both pads)"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A256-trump5-passes", "code"))
import classify256 as C56                                      # noqa: E402  READ-ONLY (A256): installs load256
sys.path.append(HERE)
import pads269 as PD                                           # noqa: E402
import load269                                                 # noqa: E402

PD.install()
load269.install()


def main():
    idx = json.load(open(os.path.join(ATT, "records", "index.json"), encoding="utf-8"))["rows"]
    out = dict(pads={}, rows=[])
    for pad in ("tube", "window"):
        cnt = dict(a=0, b=0, err=0)
        for r in [x for x in idx if x["pad"] == pad]:
            try:
                pins, hb, cls, dpin, _row = C56.boxes_of(r["nid"], pad)
                h = C56.RAY.holds_ray_image(pins, hb, pad=pad)
                k = "b" if h["holds"] else "a"
                out["rows"].append(dict(nid=r["nid"], source=r["source"], pad=pad, cls=cls, dpin=dpin, klass=k, g=h["g"],
                                        assignment=h["assignment"], why=h["why"], a212_pad0=r["a212_pad0"]))
                cnt[k] += 1
            except Exception as e:                             # noqa: BLE001
                out["rows"].append(dict(nid=r["nid"], pad=pad, error=repr(e)[:200]))
                cnt["err"] += 1
        out["pads"][pad] = dict(cnt, lam=str(PD.LAM[pad]), drift_3_2=float((PD.LAM[pad] - 1) * PD.A_T5), delta_pin=str(PD.DPIN[pad]))
        print("pad %s: (a) %d, (b) %d, errors %d" % (pad, cnt["a"], cnt["b"], cnt["err"]))
    json.dump(out, open(os.path.join(ATT, "results", "triage269.json"), "w", encoding="utf-8"), indent=1, default=str)


if __name__ == "__main__":
    main()
