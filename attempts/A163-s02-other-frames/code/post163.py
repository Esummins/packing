"""A163 -- the post-processing pass, all in ONE process (the box ceiling is on processes).

Runs, in order: the trump5 consumer test, the k5_11 control (which must reproduce A160's 114/50),
the witness re-verification, the verdict table, and the two `N_boxes163_*.json` files.

    python post163.py [--skip-control]

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def run(mod, argv):
    import importlib
    m = importlib.import_module(mod)
    old = sys.argv
    sys.argv = [mod] + argv
    try:
        print("\n===== %s %s =====" % (mod, " ".join(argv)), flush=True)
        m.main()
    finally:
        sys.argv = old


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-control", action="store_true")
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    steps = []
    res = os.path.join(os.path.dirname(HERE), "results")
    if a.only in (None, "consumer"):
        for cls, extra, out in (("trump5", [], "consumer163_trump5.json"),
                                ("k5_16", [], "consumer163_k5_16.json"),
                                ("k5_11", ["--control"], "consumer163_k5_11_control.json")):
            if cls == "k5_11" and a.skip_control:
                continue
            if os.path.exists(os.path.join(res, out)):
                print("skip consumer %s -- %s already written" % (cls, out))
                continue
            steps.append(("consumer163", ["--cls", cls] + extra))
    if a.only in (None, "witness"):
        steps.append(("witness163", []))
    if a.only in (None, "table"):
        steps.append(("table163", []))
    if a.only in (None, "nboxes"):
        steps.append(("nboxes163", []))
    for mod, argv in steps:
        run(mod, argv)


if __name__ == "__main__":
    main()
