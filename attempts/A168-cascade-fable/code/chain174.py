"""A174 -- run several cascade168 stages in sequence in ONE lab process (children inherit the
launcher's BelowNormal priority and affinity), stopping at the first failure or sentinel.

    python chain174.py --cell l1_153 --stages s5,s6,s7,s8 --parents canary
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_153")
    ap.add_argument("--stages", default="s5,s6,s7,s8")
    ap.add_argument("--parents", default="canary")
    ap.add_argument("--extra", default="")
    a = ap.parse_args()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for st in a.stages.split(","):
        if K.sentinel():
            print("sentinel; stop", flush=True)
            return
        t0 = time.time()
        cmd = [sys.executable, "-u", os.path.join(HERE, "cascade168.py"), st, "--cell", a.cell,
               "--parents", a.parents] + (a.extra.split() if a.extra else [])
        print("== %s: %s" % (st, " ".join(cmd[2:])), flush=True)
        p = subprocess.run(cmd, env=env, cwd=HERE)
        print("== %s rc %d, %.0fs" % (st, p.returncode, time.time() - t0), flush=True)
        if p.returncode != 0:
            return
    print("chain done", flush=True)


if __name__ == "__main__":
    main()
