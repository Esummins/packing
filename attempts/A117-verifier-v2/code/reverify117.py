"""A117 T1 -- parametric re-verification of A111's and A112's NO-side certificates.

For each converted certificate (code/to_param117.py) run verify_param_v2 ONCE over the whole
census window [191/50, s0] at the fixed-side run's own depth and jobs = 1, and compare the
verdict and the wall with the FOUR fixed-side runs it replaces on A57's four-side slack-core grid.

Read-only on A111/A112: only their certificates are opened, for reading.  Output goes to
attempts/A117-verifier-v2/results/no_reverify.jsonl (resumable: a certificate already in the sink
is skipped).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
V2_PATH = os.path.join(ROOT, "attempts", "A96-a57-parametric", "code", "verify_param_v2.py")

_spec = importlib.util.spec_from_file_location("a117_v2r", V2_PATH)
V2 = importlib.util.module_from_spec(_spec)
sys.modules["a117_v2r"] = V2
_spec.loader.exec_module(V2)
F = V2.F

N_SIDES = 4                     # A57's four-side slack-core grid: what one window pass replaces


class _Deadline(Exception):
    pass


class CappedPVerifier(V2.PVerifier):
    """v2's verifier with a wall cap.  The cap is checked once per box, in `covered`, so it never
    interferes with a decision: a capped run reports CAP, never PASS and never FAIL."""

    deadline = None

    def covered(self, *a, **k):
        if self.deadline is not None and time.time() > self.deadline:
            raise _Deadline()
        return super().covered(*a, **k)


def run(cert, slo, shi, depth, split, tscale, sscale, max_w, cap, cap_seconds=0):
    t0 = time.time()
    p, n, budget, aff, weights, cores, total, nofams = V2.load_param(cert)
    v = CappedPVerifier(aff, weights, cores, F(slo), F(shi), margin=V2.ZERO, depth=depth,
                        tscale=F(tscale), sscale=F(sscale), use_float=True, max_witnesses=max_w,
                        verbose=False, nofams=nofams)
    v.deadline = (t0 + cap_seconds) if cap_seconds else None
    capped = False
    try:
        v.run(v.root_boxes(split), per_box_cap=cap)
    except _Deadline:
        capped = True
    st = v.stats()
    st["witnesses"] = len(v.witnesses)
    ws = [w for w in v.witnesses if "s_range_float" in w]
    res = "CAP" if capped else ("PASS" if not v.witnesses else "FAIL")
    return dict(result=res, seconds=round(time.time() - t0, 3),
                atoms=len(aff), cores=len(cores), nofams=len(nofams), budget=budget,
                total=str(total), stats=st,
                witness_s_range=([min(w["s_range_float"][0] for w in ws),
                                  max(w["s_range_float"][1] for w in ws)] if ws else None))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--survey", default=os.path.join(RES, "no_survey.json"))
    ap.add_argument("--paramdir", default=os.path.normpath(
        os.path.join(HERE, "..", "certs", "param")))
    ap.add_argument("--out", default=os.path.join(RES, "no_reverify.jsonl"))
    ap.add_argument("--slo", default="191/50")
    ap.add_argument("--shi", default="969271/250000")
    ap.add_argument("--depth", type=int, default=0, help="0 = the fixed-side run's own depth")
    ap.add_argument("--split", type=int, default=3)
    ap.add_argument("--tscale", default="2")
    ap.add_argument("--sscale", default="8")
    ap.add_argument("--max-witnesses", type=int, default=200)
    ap.add_argument("--max-witnesses-per-box", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default=None, help="re-verify just this certificate name")
    ap.add_argument("--cap-seconds", type=float, default=300.0,
                    help="per-certificate wall cap; a capped run reports CAP, never a verdict")
    ap.add_argument("--budget-seconds", type=float, default=0.0, help="0 = no global budget")
    a = ap.parse_args()

    survey = {r["name"]: r for r in json.load(open(a.survey)) if r["nofams"]}
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out):
            ln = ln.strip()
            if ln:
                done.add(json.loads(ln)["name"])
    todo = [nm for nm in sorted(survey)
            if nm not in done
            and os.path.exists(os.path.join(a.paramdir, nm + ".param.json"))]
    # the certificates that carry an actual KILL first: a fixed-side FAIL proves nothing either way
    todo.sort(key=lambda nm: (survey[nm]["result"] != "PASS", survey[nm]["fixed_seconds"] or 0.0))
    if a.only:
        todo = [nm for nm in todo if nm == a.only]
    if a.limit:
        todo = todo[:a.limit]
    print("re-verifying %d NO-side certificates over [%s, %s] (%d already done)"
          % (len(todo), a.slo, a.shi, len(done)), flush=True)
    t_start = time.time()
    with open(a.out, "a") as sink:
        for i, nm in enumerate(todo):
            if a.budget_seconds and time.time() - t_start > a.budget_seconds:
                print("global budget %ss exhausted after %d certificates"
                      % (a.budget_seconds, i), flush=True)
                break
            s = survey[nm]
            cert = os.path.join(a.paramdir, nm + ".param.json")
            depth = a.depth or s["depth"]
            try:
                r = run(cert, a.slo, a.shi, depth, a.split, a.tscale, a.sscale,
                        a.max_witnesses, a.max_witnesses_per_box, a.cap_seconds)
                err = None
            except Exception as e:
                r, err = {}, repr(e)[:300]
            row = dict(name=nm, camp=s["camp"], src=s["cert"],
                       param=os.path.relpath(cert, ROOT).replace("\\", "/"),
                       slo=a.slo, shi=a.shi, depth=depth, split=a.split,
                       fixed_result=s["result"], fixed_seconds=s["fixed_seconds"],
                       fixed_boxes=s["boxes"],
                       four_side_seconds=(s["fixed_seconds"] or 0) * N_SIDES,
                       cap_seconds=a.cap_seconds, error=err, **r)
            sink.write(json.dumps(row) + "\n")
            sink.flush()
            print("[%d/%d] %-58s fixed %s %6.1fs  ->  window %s %8.1fs  %s"
                  % (i + 1, len(todo), nm[:58], s["result"], s["fixed_seconds"] or 0,
                     r.get("result", "ERR"), r.get("seconds", 0), err or ""), flush=True)


if __name__ == "__main__":
    main()
