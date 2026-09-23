"""A269 -- the progress page results/progress.md (no chain import: reads the run rows, the latest queue, ran / stalled).

Per pad: records CLOSED (a run row with pad verdict DEAD: every start node present then died -- queue269.closed's
rule), records with open start nodes in the latest queue, STALLED start nodes, crashes, CPU-s spent."""
import collections
import glob
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(ATT, "results")


def jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            try:
                out.append(json.loads(ln))
            except Exception:                                      # noqa: BLE001
                pass
    return out


def lines(p):
    return [ln.split("#")[0].split() for ln in open(p, encoding="utf-8")] if os.path.exists(p) else []


def main():
    idx = json.load(open(os.path.join(ATT, "records", "index.json"), encoding="utf-8"))["rows"]
    rows = jl(os.path.join(RES, "terminal269.jsonl"))
    dead = {(r["nid"], r["pad"]) for r in rows if str(r.get("verdict") or "").startswith("DEAD")}
    secs = collections.Counter()
    for r in rows:
        secs[r.get("pad")] += float(r.get("seconds") or 0)
    qs = sorted(glob.glob(os.path.join(ATT, "queues", "queue269_pass*.txt")), key=lambda f: int(f.rsplit("pass", 1)[1][:-4]))
    q = [x for x in lines(qs[-1]) if x] if qs else []
    openq = collections.Counter((x[0], x[1].split(":")[0]) for x in q if len(x) >= 2)
    st = [x for x in lines(os.path.join(RES, "stalled269.txt")) if x]
    cr = [x for x in lines(os.path.join(RES, "crashed269.txt")) if x]
    ran = [x for x in lines(os.path.join(RES, "ran269.txt")) if x]
    out = ["# A269 progress -- trump5 re-emitted records, window pads (%s)" % time.strftime("%Y-%m-%d %H:%M"), "",
           "Pads: `window` = pad B, lam = 969271/955000, slab (3.82, s0], records `*_r269b` (delta_pin 9/400);",
           "`tube` = pad A, lam = 969271/958021, slab (3.832084, s0], records `*_r269a` (delta_pin 9/500).",
           "A DEAD at pad B is the full-window statement for its record and implies pad A (HYP_A is inside HYP_B).", "",
           "| pad | records | CLOSED (DEAD) | open start nodes (latest queue: %s) | records with open start nodes | runs | CPU-h |" % (
               os.path.basename(qs[-1]) if qs else "none"),
           "|---|---|---|---|---|---|---|"]
    for pad in ("window", "tube"):
        recs = [r["nid"] for r in idx if r["pad"] == pad]
        nd = sum(1 for n in recs if (n, pad) in dead)
        no = sum(v for (n, p), v in openq.items() if p == pad)
        nr = sum(1 for (n, p) in openq if p == pad)
        runs = sum(1 for r in rows if r.get("pad") == pad)
        out.append("| %s | %d | %d | %d | %d | %d | %.2f |" % (pad, len(recs), nd, no, nr, runs, secs[pad] / 3600))
    out += ["", "STALLED start nodes (never requeued; ALIVE, not a verdict): %d" % len(st)]
    out += ["* `%s %s`" % (x[0], x[1]) for x in st[:60]]
    out += ["", "Crashed runs (requeued, not a pass): %d; finished runs: %d" % (len(cr), len(ran))]
    open(os.path.join(RES, "progress.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print("\n".join(out[5:9 + 2]))


if __name__ == "__main__":
    main()
