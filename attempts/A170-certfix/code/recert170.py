"""A170 -- re-certify FAILing records with A135's EXACT cores carried through.

Two modes, both writing only under `attempts/A170-certfix/`:

  --mode patch   take an EXISTING certificate on disk, enlarge its cores to `exactcore.exact_a`,
                 write the patched copy under A170/certs and run the FROZEN verify_case.py.
                 (A166's `certaudit166.py` path, copied -- A166's files are not edited.)

  --mode k0      take A115's STORED LP record (`results/nodes/<nid>.t{4,5}.lp.json`, which keeps
                 `atoms_all`, `rows_all` and `hyp`), re-emit the certificate from the STORED measure
                 with `certwrap170.make_certificate_exact` (NO re-solve), and verify.  The scale rule
                 is A115's own (`t4.certify_plain`):
                     scale = max(1.005, min(1.4, (budget - 0.005)/tau - 0.002)).

Every campaign and prior attempt is READ-ONLY.

    python code/recert170.py --mode k0    --out results/recert170_k0.jsonl   --jobs 1
    python code/recert170.py --mode patch --certs <dir-or-list> --out results/recert170_<tag>.jsonl
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
sys.path.insert(0, HERE)
for _p in (os.path.join(ATT, "A140-k0-residue-gallery", "code"),):
    if _p not in sys.path:
        sys.path.append(_p)

import certwrap170 as W                                        # noqa: E402

CERTS = os.path.join(BASE, "certs")
RES = os.path.join(BASE, "results")
S0_RAT = "969271/250000"
SENTINELS = [os.path.join(ROOT, "PAUSE"), os.path.join(ROOT, "STOP"),
             os.path.join(BASE, "PAUSE"), os.path.join(BASE, "STOP")]


def sentinel():
    for p in SENTINELS:
        if os.path.exists(p):
            return p
    return None


def done_ids(out):
    seen = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try:
                    seen.add(json.loads(ln)["id"])
                except Exception:                              # noqa: BLE001
                    pass
    return seen


def emit(out, rec):
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


# --------------------------------------------------------------------------- mode: k0
def k0_targets(shard, nshards):
    import cells140 as C140                                    # READ-ONLY (A140)
    pool = C140.open_pool()
    out = []
    for i, row in enumerate(pool):
        nid, verdict, lp = row[0], row[1], row[2]
        d = row[3] if len(row) > 3 else {}
        if not str(verdict).startswith("kill-candidate"):
            continue
        if not lp or not os.path.exists(lp):
            continue
        if i % nshards != shard:
            continue
        out.append((nid, verdict, lp, d))
    return out


def run_k0(a):
    tgt = k0_targets(a.shard, a.nshards)
    seen = done_ids(a.out)
    print("k0 targets %d (shard %d/%d), %d already done" % (len(tgt), a.shard, a.nshards, len(seen)),
          flush=True)
    t_start = time.time()
    for nid, verdict, lp, rec in tgt:
        if nid in seen:
            continue
        s = sentinel()
        if s:
            print("SENTINEL %s -- stopping" % s, flush=True)
            return
        if time.time() - t_start > a.wall:
            print("wall %.0f s reached -- stopping" % a.wall, flush=True)
            return
        t0 = time.time()
        try:
            res = json.load(open(lp, encoding="utf-8"))
        except Exception as ex:                                # noqa: BLE001
            emit(a.out, dict(id=nid, lane="k0", result="ERROR", err=repr(ex)[:150]))
            continue
        budget, tau = res["budget"], res["tau"]
        scale = (max(1.005, min(1.4, (budget - 0.005) / tau - 0.002)) if tau > 1e-12 else 1.005)
        try:
            cert = W.make_certificate_exact(res, S0_RAT, scale=scale)
        except Exception as ex:                                # noqa: BLE001
            emit(a.out, dict(id=nid, lane="k0", result="ERROR", err=repr(ex)[:150]))
            continue
        rep = cert["provenance"]["a170_core_report"]
        tot = float(Fr(cert["total"]))
        base = dict(id=nid, lane="k0", was=verdict, budget=budget, tau=tau, scale=scale,
                    total=tot, lp=os.path.relpath(lp, ROOT).replace("\\", "/"),
                    cores=rep, n_applied=sum(1 for r in rep if r.get("applied")),
                    max_ratio=max([r.get("ratio", 1.0) or 1.0 for r in rep] or [1.0]),
                    prev=(rec.get("cert") or {}).get("result") if isinstance(rec.get("cert"), dict)
                    else None)
        if tot >= budget:
            emit(a.out, dict(result="FAIL(total>=budget)", verify_s=0.0, **base))
            print("%-28s FAIL(total>=budget) %.6f >= %d" % (nid, tot, budget), flush=True)
            continue
        p = os.path.join(CERTS, "k0_%s__exact.json" % nid)
        json.dump(cert, open(p, "w"), indent=0)
        rc, txt = W.run_frozen_verifier(p, jobs=a.jobs, depth=a.depth, timeout=a.timeout)
        tail = W.verifier_tail(txt)
        result = "PASS" if rc == 0 else ("TIMEOUT" if rc is None else "FAIL")
        emit(a.out, dict(result=result, rc=rc, verify_s=round(time.time() - t0, 1),
                         cert=os.path.relpath(p, ROOT).replace("\\", "/"),
                         verifier=tail[:3], verifier_sha=W.FROZEN_SHA, **base))
        print("%-28s %-7s tot %.5f/%d  scale %.4f  cores x%d (max %.4f)  %.0fs | %s"
              % (nid, result, tot, budget, scale, base["n_applied"], base["max_ratio"],
                 time.time() - t0, (tail[-1][:90] if tail else "")), flush=True)


# --------------------------------------------------------------------------- mode: patch
def patch_targets(spec, only_fail=True):
    import glob
    files = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if os.path.isdir(part):
            files += sorted(glob.glob(os.path.join(part, "*.json")))
        else:
            files += sorted(glob.glob(part))
    out = []
    for f in files:
        if f.endswith((".report.json", ".witnesses.json", ".certify.json", ".resolve2.json")):
            continue
        base = f[:-5]
        verdict = None
        for suf in (".certify.json", ".report.json"):
            if os.path.exists(base + suf):
                try:
                    verdict = json.load(open(base + suf, encoding="utf-8")).get("result")
                except Exception:                              # noqa: BLE001
                    pass
                if verdict:
                    break
        if only_fail and verdict != "FAIL":
            continue
        out.append((f, verdict))
    return out


def run_patch(a):
    tgt = patch_targets(a.certs, only_fail=not a.all)
    seen = done_ids(a.out)
    print("patch targets %d, %d already done" % (len(tgt), len(seen)), flush=True)
    t_start = time.time()
    for f, verdict in tgt:
        rel = os.path.relpath(f, ROOT).replace("\\", "/")
        tag = os.path.splitext(os.path.basename(f))[0]
        lane = os.path.relpath(f, ATT).replace("\\", "/").split("/")[0]
        key = lane + "/" + tag
        if key in seen:
            continue
        s = sentinel()
        if s:
            print("SENTINEL %s -- stopping" % s, flush=True)
            return
        if time.time() - t_start > a.wall:
            print("wall %.0f s reached -- stopping" % a.wall, flush=True)
            return
        t0 = time.time()
        try:
            cert = json.load(open(f, encoding="utf-8"))
        except Exception as ex:                                # noqa: BLE001
            emit(a.out, dict(id=key, lane=lane, result="ERROR", err=repr(ex)[:150], src=rel))
            continue
        if cert.get("format") != "case-measure-certificate-v1":
            continue
        rep = W.carry_exact_cores(cert)
        n_app = sum(1 for r in rep if r.get("applied"))
        base = dict(id=key, lane=lane, src=rel, was=verdict, budget=cert.get("budget"),
                    total=cert.get("total"), cores=rep, n_applied=n_app,
                    max_ratio=max([r.get("ratio", 1.0) or 1.0 for r in rep] or [1.0]))
        if n_app == 0:
            emit(a.out, dict(result="NO-CHANGE", verify_s=0.0, **base))
            print("%-52s NO-CHANGE (cores already exact)" % key, flush=True)
            continue
        p = os.path.join(CERTS, "%s__%s__exact.json" % (lane.split("-")[0], tag))
        json.dump(cert, open(p, "w"), indent=0)
        rc, txt = W.run_frozen_verifier(p, jobs=a.jobs, depth=a.depth, timeout=a.timeout)
        tail = W.verifier_tail(txt)
        result = "PASS" if rc == 0 else ("TIMEOUT" if rc is None else "FAIL")
        emit(a.out, dict(result=result, rc=rc, verify_s=round(time.time() - t0, 1),
                         cert=os.path.relpath(p, ROOT).replace("\\", "/"),
                         verifier=tail[:3], verifier_sha=W.FROZEN_SHA, **base))
        print("%-52s %s -> %-5s  cores x%d (max %.4f)  %.0fs | %s"
              % (key, verdict, result, n_app, base["max_ratio"], time.time() - t0,
                 (tail[-1][:80] if tail else "")), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("k0", "patch"), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--certs", default="", help="patch mode: dirs/globs, comma separated")
    ap.add_argument("--all", action="store_true", help="patch mode: not just FAILs")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--wall", type=float, default=7200.0)
    a = ap.parse_args()
    os.makedirs(CERTS, exist_ok=True)
    a.out = a.out if os.path.isabs(a.out) else os.path.join(BASE, a.out)
    W.assert_frozen()
    (run_k0 if a.mode == "k0" else run_patch)(a)


if __name__ == "__main__":
    main()
