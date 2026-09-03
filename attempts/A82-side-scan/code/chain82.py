"""A82: run scan82 over several classes in ONE process (one LP slot per chain)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1                                                        # noqa: E402,F401
import argparse                                                     # noqa: E402
import time                                                         # noqa: E402
import scan82                                                       # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--classes", nargs="+", required=True)
    ap.add_argument("--lp_time", type=float, default=600.0)
    ap.add_argument("--max_iter", type=int, default=200)
    ap.add_argument("--headroom", type=float, default=6.0)
    ap.add_argument("--headroom_wait", type=float, default=7200)
    ap.add_argument("--tag", default="")
    ap.add_argument("--sides", default="", help="comma-separated rational sides "
                                                "(default: the full A82 ladder)")
    a = ap.parse_args()
    sides = [s for s in a.sides.split(",") if s]
    for cls in a.classes:
        t0 = time.time()
        print("### chain: %s starting %s" % (time.strftime("%H:%M:%S"), cls), flush=True)
        argv = ["--cls", cls, "--lp_time", str(a.lp_time), "--max_iter", str(a.max_iter),
                "--headroom", str(a.headroom), "--headroom_wait", str(a.headroom_wait)]
        if a.tag:
            argv += ["--tag", a.tag]
        if sides:
            argv += ["--sides"] + sides
        old = sys.argv
        sys.argv = ["scan82.py"] + argv
        try:
            rc = scan82.main()
        except Exception as e:                                       # keep the chain alive
            rc = "EXC %r" % (e,)
        finally:
            sys.argv = old
        print("### chain: %s finished %s rc=%s (%.0fs)"
              % (time.strftime("%H:%M:%S"), cls, rc, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
