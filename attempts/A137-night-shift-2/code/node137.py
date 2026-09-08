"""A137 -- ONE node of the exact-pin-core re-emission, in its own process.

Run as a child of `run137.py`, which owns the 1,500 s per-node process wall (A124: the Y0381 hang
is inside a single `h.run()` call and cannot be interrupted from inside the process, so the wall
has to be a process wall -- and CAP is never a verdict).

The LP + certificate + FROZEN verifier chain is A135's `emit135.certify`, imported unchanged:
exact certified-maximal rational cores (`exactcore`, A132's vertex test), the same core objects in
the LP row filter and in the emitted `case-measure-certificate-v1`, and `verify_case.py`
(sha 521cb01f) as the arbiter.  Nothing here edits tree57.py, lpbox.py or any verifier.
"""
import argparse
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A135 = os.path.join(ROOT, "A135-polycore-verifier", "code")
if A135 not in sys.path:
    sys.path.insert(0, A135)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True, help="path to a json file with the job record")
    ap.add_argument("--out", required=True, help="where to write the result record")
    ap.add_argument("--cap", type=float, default=420.0)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--warm_rows", type=int, default=9000)
    ap.add_argument("--fine", type=int, default=1)
    ap.add_argument("--scale_cap", type=float, default=1.03)
    ap.add_argument("--certdir", default=os.path.join(BASE, "certs"))
    a = ap.parse_args()

    import emit135                                            # noqa: E402  (after sys.path)
    j = json.load(open(a.job))
    os.makedirs(a.certdir, exist_ok=True)

    def log(*x):
        print(*x, flush=True)

    t0 = time.time()
    try:
        rec = emit135.certify(j["id"], j["box"], j["budget"], j.get("scope", "exall"), a.cap,
                              a.rounds, a.jobs, a.depth, a.warm_rows, bool(a.fine), a.scale_cap,
                              a.certdir, log)
    except Exception as e:
        rec = dict(id=j["id"], scope=j.get("scope", "exall"), result="ERROR",
                   error=repr(e)[:400], tb=traceback.format_exc()[-1500:])
    rec["wall_s"] = round(time.time() - t0, 1)
    rec["level"] = j.get("level")
    rec["cls"] = j.get("cls")
    rec["prior"] = j.get("prior")
    rec["eta_before"] = j.get("eta")
    rec["tau_before"] = j.get("tau")
    rec["lane"] = "exact-core re-emission"
    json.dump(rec, open(a.out, "w"))
    print("RESULT " + str(rec.get("result")), flush=True)


if __name__ == "__main__":
    main()
