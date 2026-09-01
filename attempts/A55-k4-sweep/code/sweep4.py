"""
A55 leg 1: the k = 4 sweep.  One shard = ONE heavy process; run at most 3.

Per node it calls ladder.py (A54's rung 1 + rung 2 with the banked levers: merged warm start,
row pruning OFF / COLUMN pruning only, lifted scale cap = budget/tau, cheap-cert every round).
Budget = 7.

Canary discipline (S4 + A55's new containment canary):
  * the four k = 4 classes that are SUB-SKELETONS of trump5 (k4_03, k4_06, k4_08, k4_11) are
    PROVABLY ALIVE -- a kill of any of them would kill trump5 by the L5 cap corollary.  They are
    measured (--no_cert) and never certified.
  * corners4 (k4_13) must reproduce the A14/A16 tau -> 7.000 baseline; certification is refused
    automatically once tau >= budget.
Checkpointed: a node whose results/<name>_<tag>.json exists is skipped.
"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))

TRUMP_SUBSETS = ("k4_03", "k4_06", "k4_08", "k4_11")     # provably alive; never certify
CORNERS4 = "k4_13"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--tag", default="s1")
    ap.add_argument("--time_limit", type=float, default=900)
    ap.add_argument("--max_iter", type=int, default=900)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--cert_time", type=float, default=420)
    ap.add_argument("--max_cols_add", type=int, default=350)
    ap.add_argument("--prune_cols", type=int, default=3)
    ap.add_argument("--col_stop_cov", type=float, default=1.03)
    ap.add_argument("--only", default=None, help="comma list of node names")
    a = ap.parse_args()
    si, sn = map(int, a.shard.split("/"))

    names = sorted(n for n in json.load(open(os.path.join(BASE, "results", "name_to_slots.json")))
                   if n.startswith("k4_"))
    if a.only:
        names = [n for n in names if n in a.only.split(",")]
    names = [n for i, n in enumerate(names) if i % sn == si]

    logf = open(os.path.join(BASE, "logs", f"sweep_shard{si}_{a.tag}.log"), "a", buffering=1)
    def log(*x):
        print(*x, file=logf, flush=True)
    log(f"=== A55 sweep shard {a.shard} tag={a.tag} {time.strftime('%Y-%m-%d %H:%M:%S')} nodes={names}")

    for nm in names:
        recp = os.path.join(BASE, "results", f"{nm}_{a.tag}.json")
        if os.path.exists(recp):
            log(f"[skip] {nm} (checkpoint {os.path.basename(recp)})")
            print(json.dumps(dict(name=nm, skipped=True)), flush=True)
            continue
        cmd = [sys.executable, os.path.join(HERE, "ladder.py"), "--name", nm, "--tag", a.tag,
               "--time_limit", str(a.time_limit), "--max_iter", str(a.max_iter),
               "--rounds", str(a.rounds), "--jobs", str(a.jobs), "--depth", "56",
               "--cert_time", str(a.cert_time), "--max_cols_add", str(a.max_cols_add),
               "--prune_cols", str(a.prune_cols), "--col_stop_cov", str(a.col_stop_cov),
               "--scale_cap", "1.40"]      # A54 S2: the real ceiling is budget/tau, not 1.03
        if nm in TRUMP_SUBSETS:
            cmd.append("--no_cert")        # S4: subset of trump5 => provably alive
        t0 = time.time()
        log(f"[{time.strftime('%H:%M:%S')}] {nm}: " + " ".join(cmd[-14:]))
        p = subprocess.run(cmd, capture_output=True, text=True)
        log(f"  rc={p.returncode} ({time.time()-t0:.0f}s) {p.stdout.strip()[-600:]}")
        if p.stderr.strip():
            log("  stderr: " + p.stderr.strip()[-1500:])
        print(f"{nm} done rc={p.returncode} {time.time()-t0:.0f}s", flush=True)
    log("shard done")
    print("shard done", flush=True)


if __name__ == "__main__":
    main()
