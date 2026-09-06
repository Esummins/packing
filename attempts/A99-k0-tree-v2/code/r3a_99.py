"""A99 R3(a): certification wall at --jobs 1 vs --jobs 4 on 10 A85 certificates, with the
verdict and the exact witness census required to be IDENTICAL.

verify_case's --jobs splits the 4^k root boxes across worker processes; the per-box search is
deterministic and independent, so the only legitimate differences are wall time and the ORDER of
the witness list (imap_unordered).  This checks: same return code, same box/covered/exempt counts,
same multiset of witness boxes.  The measured speed-up is what the tree's certification phase
would actually get from 4 slots on one node.

This is the ONE test in A99 that runs 4 worker processes; it runs alone (no other A99 leg
in flight) and is otherwise BLAS-pinned like everything else.
"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
VC = os.path.join(HERE, "verify_case.py")
RES = os.path.join(BASE, "results")
OUTC = os.path.join(BASE, "certs", "r3a")
A85C = os.path.join(ROOT, "attempts", "A85-k0-route", "certs", "k0_00")


def env1():
    return dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")


def run(cert, jobs, depth, split, maxw, cap, tag):
    os.makedirs(OUTC, exist_ok=True)
    rp = os.path.join(OUTC, f"{tag}.j{jobs}.report.json")
    wf = os.path.join(OUTC, f"{tag}.j{jobs}.witnesses.json")
    cmd = [sys.executable, VC, cert, "--depth", str(depth), "--split", str(split),
           "--jobs", str(jobs), "--max-witnesses", str(maxw),
           "--max-witnesses-per-box", "8",
           "--report", rp, "--witness-file", wf, "--quiet"]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, env=env1(), timeout=cap)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        rc = None
    w = round(time.time() - t0, 2)
    st, boxes = {}, None
    if os.path.exists(rp):
        R = json.load(open(rp))
        s = R["stats"]
        st = dict(boxes=s["boxes"], covered=s["covered"], exempt=s["exempt"],
                  vacuous=s["vacuous"], split=s["split"], witnesses=s["witnesses"],
                  max_depth=s["max_depth"])
    if os.path.exists(wf):
        W = json.load(open(wf)).get("witnesses", [])
        boxes = sorted(json.dumps(x["box"], sort_keys=True) for x in W)
    return dict(jobs=jobs, rc=rc, wall_s=w, stats=st, n_witness=len(boxes or []),
                witness_key=hash(tuple(boxes)) if boxes is not None else None,
                witness_boxes=boxes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--split", type=int, default=3)
    ap.add_argument("--maxw", type=int, default=64)
    ap.add_argument("--cap", type=float, default=1200.0)
    ap.add_argument("--jobs", default="1,4")
    ap.add_argument("--out", default="r3a_jobs.jsonl")
    a = ap.parse_args()
    names = []
    for f in sorted(os.listdir(A85C)):
        if not f.endswith(".json") or f.endswith((".report.json", ".witnesses.json",
                                                  ".certify.json", ".resolve.json",
                                                  ".resolve1.json", ".resolve2.json")):
            continue
        if os.path.exists(os.path.join(A85C, f.replace(".json", ".report.json"))):
            names.append(f)
    names = names[:a.n]
    outp = os.path.join(RES, a.out)
    done = set()
    if os.path.exists(outp):
        for ln in open(outp):
            try:
                done.add(json.loads(ln)["cert"])
            except Exception:
                pass
    print(f"{len(names)} certificate(s): {names}", flush=True)
    for f in names:
        if f in done:
            continue
        cert = os.path.join(A85C, f)
        tag = f[:-5]
        runs = [run(cert, int(j), a.depth, a.split, a.maxw, a.cap, tag)
                for j in a.jobs.split(",")]
        base = runs[0]
        rec = dict(cert=f, depth=a.depth, split=a.split, runs=runs,
                   same_rc=len({r["rc"] for r in runs}) == 1,
                   same_stats=all(r["stats"] == base["stats"] for r in runs),
                   same_witnesses=all(r["witness_boxes"] == base["witness_boxes"]
                                      for r in runs),
                   speedup=(round(base["wall_s"] / runs[-1]["wall_s"], 3)
                            if runs[-1]["wall_s"] else None))
        for r in rec["runs"]:
            r.pop("witness_boxes", None)
        with open(outp, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"  {f:44s} " + "  ".join(f"j{r['jobs']}={r['wall_s']:7.2f}s rc={r['rc']}"
                                        for r in runs)
              + f"  x{rec['speedup']} same_rc={rec['same_rc']} "
                f"same_stats={rec['same_stats']} same_wit={rec['same_witnesses']}", flush=True)
    print("r3a done", flush=True)


if __name__ == "__main__":
    main()
