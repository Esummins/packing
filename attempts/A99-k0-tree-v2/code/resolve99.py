"""A99 R1: do A85's FAILed fixed-side certificates close by re-verification alone (no new LP)?

resolve96's method transposed from the s-window to the fixed-side (t, cx, cy) root.

IMPORTANT structural difference from A96, established here and not assumed.  verify_param splits
the widest axis of a 4-D cell, so on the FULL window the s-axis is starved and restricting the
window really does change the search: that is why resolve96's sub-window re-run PASSes where the
global run FAILs.  verify_case's `--depth` budget is instead UNIFORM over the root split: the
sub-tree explored below a box does not depend on what else is in the run.  Hence for a fixed side

    "every depth-56 witness box closes when granted `extra` more bisections"
        <=>  "the global run at depth 56 + extra PASSes"

and the two modes below measure the same predicate; `subbox` only prices the SHORTCUT (redo just
the uncovered boxes) against `ladder` (redo everything).

  --mode ladder  the FROZEN verify_case.py CLI on the certificate at increasing depth (A85's own
                 flags otherwise: split 3, max-witnesses 64, jobs 1), first PASS wins.
  --mode subbox  the depth-56 witness boxes of the A85 run, each re-verified through the SAME
                 frozen Verifier restricted to that box with `extra` extra bisections.

A witness whose sampled admissible placement has exact mass < 1 ("hole") is a genuine defect of
the certificate: it can never close at any depth, and is counted separately.

Nothing is edited: code/verify_case.py is byte-identical to A53's (code/frozen.sha256).
"""
import argparse, json, os, subprocess, sys, time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
VC = os.path.join(HERE, "verify_case.py")
RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs", "resolve99")
A85C = os.path.join(ROOT, "attempts", "A85-k0-route", "certs", "k0_00")

sys.path.insert(0, HERE)
import verify_case as VCM     # frozen module, imported read-only


def env1():
    return dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")


def cli_run(cert, depth, split, jobs, maxw, cap, tag):
    os.makedirs(CERTS, exist_ok=True)
    rp = os.path.join(CERTS, f"{tag}.d{depth}.report.json")
    wf = os.path.join(CERTS, f"{tag}.d{depth}.witnesses.json")
    cmd = [sys.executable, VC, cert, "--depth", str(depth), "--split", str(split),
           "--jobs", str(jobs), "--max-witnesses", str(maxw),
           "--report", rp, "--witness-file", wf, "--quiet"]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, env=env1(), timeout=cap)
        rc, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        rc, out = None, "TIMEOUT"
    w = round(time.time() - t0, 1)
    stats = {}
    if os.path.exists(rp):
        try:
            R = json.load(open(rp))
            stats = dict(boxes=R["stats"]["boxes"], covered=R["stats"]["covered"],
                         exempt=R["stats"]["exempt"], witnesses=R["stats"]["witnesses"],
                         max_depth=R["stats"]["max_depth"], atoms=R.get("atoms"),
                         total=R.get("total_float"))
        except Exception:
            pass
    kinds = {}
    if os.path.exists(wf):
        try:
            W = json.load(open(wf)).get("witnesses", [])
            for x in W:
                kinds[x.get("kind")] = kinds.get(x.get("kind"), 0) + 1
        except Exception:
            pass
    fail_line = ""
    for l in (out or "").splitlines():
        if l.startswith(("FAIL", "PASS", "MALFORMED")):
            fail_line = l[:220]
    return dict(depth=depth, rc=rc, wall_s=w, stats=stats, kinds=kinds, line=fail_line)


# --------------------------------------------------------------------------- sub-box mode
def box_ints(w, V):
    b = w["box"]
    def T(q):
        n = F(q) * V.T_ROOT
        assert n.denominator == 1, "t not representable"
        return int(n)
    def X(q):
        n = F(q) * V.D
        assert n.denominator == 1, "cx/cy not representable"
        return int(n)
    return (int(w["depth"]), T(b["t"][0]), T(b["t"][1]),
            X(b["cx"][0]), X(b["cx"][1]), X(b["cy"][0]), X(b["cy"][1]), (), 0)


def subbox(cert, W, deep):
    d, s, n, atoms, weights, total = VCM.load_certificate(cert, None)
    V = VCM.Verifier(s, atoms, weights, margin=VCM.ZERO, depth=deep, tscale=F(2), use_float=True,
                     max_witnesses=1, verbose=False, cores=d["_cores"], nofams=d["_nofams"])
    out = []
    for i, w in enumerate(W):
        rec = dict(i=i, kind=w.get("kind"), depth0=w.get("depth"), exact_mass=w.get("exact_mass"))
        if w.get("kind") == "hole":
            rec.update(result="HOLE", wall_s=0.0, boxes=0)
            out.append(rec)
            continue
        try:
            bx = box_ints(w, V)
        except AssertionError as e:
            rec.update(result="UNREPRESENTABLE", err=str(e), wall_s=0.0, boxes=0)
            out.append(rec)
            continue
        V.reset_stats()
        t0 = time.time()
        ok = V.run([bx])
        rec.update(result="CLOSED" if ok else "STILL_OPEN", wall_s=round(time.time() - t0, 3),
                   boxes=V.n_boxes, max_depth=V.max_depth_seen)
        if not ok and V.witnesses:
            rec["witness_kind"] = V.witnesses[0].get("kind")
        out.append(rec)
    return out


def failed_certs():
    names = []
    for f in sorted(os.listdir(A85C)):
        if not f.endswith(".json") or any(f.endswith(x) for x in (
                ".report.json", ".witnesses.json", ".certify.json",
                ".resolve.json", ".resolve1.json", ".resolve2.json")):
            continue
        rp = os.path.join(A85C, f.replace(".json", ".report.json"))
        if not os.path.exists(rp):
            continue
        try:
            if json.load(open(rp)).get("result") == "FAIL":
                names.append(f)
        except Exception:
            pass
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("ladder", "subbox"), default="ladder")
    ap.add_argument("--certs", default=None)
    ap.add_argument("--depths", default="56,64,72,88")
    ap.add_argument("--extra", type=int, default=16)
    ap.add_argument("--split", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--maxw", type=int, default=64)
    ap.add_argument("--cap", type=float, default=1200.0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    names = [x.strip() for x in a.certs.split(",")] if a.certs else failed_certs()
    outp = os.path.join(RES, a.out or f"r1_{a.mode}.jsonl")
    done = set()
    if os.path.exists(outp):
        for ln in open(outp):
            try:
                done.add(json.loads(ln)["cert"])
            except Exception:
                pass
    print(f"mode={a.mode}  {len(names)} certificate(s)", flush=True)
    for f in names:
        if f in done:
            print(f"skip {f}", flush=True)
            continue
        cert = os.path.join(A85C, f)
        tag = f[:-5]
        t0 = time.time()
        if a.mode == "ladder":
            steps, verdict, dmin = [], "FAIL", None
            for d in [int(x) for x in a.depths.split(",")]:
                r = cli_run(cert, d, a.split, a.jobs, a.maxw, a.cap, tag)
                steps.append(r)
                print(f"  {f} depth={d} rc={r['rc']} {r['wall_s']}s {r['kinds']} {r['line'][:110]}",
                      flush=True)
                if r["rc"] == 0:
                    verdict, dmin = "PASS", d
                    break
                if r["rc"] is None:
                    verdict = "TIMEOUT"
                    break
            rec = dict(cert=f, mode="ladder", verdict=verdict, depth_closed=dmin, steps=steps,
                       wall_s=round(time.time() - t0, 1))
        else:
            wf = os.path.join(A85C, f.replace(".json", ".witnesses.json"))
            W = json.load(open(wf))["witnesses"] if os.path.exists(wf) else []
            recs = subbox(cert, W, 56 + a.extra)
            cnt = {k: sum(1 for r in recs if r["result"] == k)
                   for k in ("HOLE", "CLOSED", "STILL_OPEN", "UNREPRESENTABLE")}
            rec = dict(cert=f, mode="subbox", extra=a.extra, n_boxes=len(W), counts=cnt,
                       a85_witness_list_truncated=(len(W) >= 64),
                       kinds={k: sum(1 for x in W if x.get("kind") == k)
                              for k in ("hole", "tight", "undecided")},
                       subbox_wall_s=round(sum(r["wall_s"] for r in recs), 2),
                       wall_s=round(time.time() - t0, 1), per_box=recs)
            print(f"  {f} boxes={len(W)} {cnt} {rec['subbox_wall_s']}s", flush=True)
        with open(outp, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
    print("resolve99 done", flush=True)


if __name__ == "__main__":
    main()
