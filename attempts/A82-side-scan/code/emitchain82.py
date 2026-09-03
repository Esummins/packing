"""A82: run emit82 for several classes at one side, sequentially (one LP slot)."""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1                                                        # noqa: E402,F401
import argparse                                                     # noqa: E402
import emit82                                                       # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--classes", nargs="+", required=True)
    ap.add_argument("--side", required=True)
    ap.add_argument("--eps_geo", type=float, default=0.0015)
    ap.add_argument("--rounds", type=int, default=5)
    ap.add_argument("--scale_cap", type=float, default=1.05)
    a = ap.parse_args()
    for cls in a.classes:
        t0 = time.time()
        print("### emitchain %s starting %s" % (time.strftime("%H:%M:%S"), cls), flush=True)
        argv = ["--cls", cls, "--side", a.side, "--depth", "60", "--cert_depth", "56",
                "--rounds", str(a.rounds), "--time_limit", "420",
                "--scale_cap", str(a.scale_cap), "--eps_geo", str(a.eps_geo)]
        old, sys.argv = sys.argv, ["emit82.py"] + argv
        try:
            rc = emit82.main()
        except Exception as e:
            rc = "EXC %r" % (e,)
        finally:
            sys.argv = old
        print("### emitchain %s finished %s rc=%s (%.0fs)"
              % (time.strftime("%H:%M:%S"), cls, rc, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
