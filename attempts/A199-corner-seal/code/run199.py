"""A199 driver.  python run199.py --pages k5_16_interior_Y0491 [--lam 1.0] [--side s] [--out results/seal199.jsonl]
   --sweep 1.0,1.001,...   the pad threshold at s0 (one page)
   --slabs LAMSLAB         cover [3.82, s0] by slabs of ratio LAMSLAB, each run at its top side with its own pad
   --all                   every ALIVE a57v4 page of docs/shadows/STATUS.md
Rows are appended to the jsonl (resumable: pages already present at the same (side, lam) are skipped unless --force)."""
import argparse
import json
import math
import os
import re
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seal199 as S            # noqa: E402
import seal199b as SB          # noqa: E402

ROOT = S.ROOT
STATUS = os.path.join(ROOT, "docs", "shadows", "STATUS.md")


def alive_a57v4():
    out = []
    for line in open(STATUS, encoding="utf-8"):
        m = re.match(r"\| \[ \] \[`([A-Za-z0-9_]+)\.svg`\].*\*\*ALIVE\*\*", line)
        if m and not m.group(1).startswith("l"):
            out.append(m.group(1))
    return out


def done_keys(path):
    ks = set()
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                ks.add((d["page"], round(d["s"], 9), round(d["lam"], 9)))
    return ks


def one(page, s, lam, args, log):
    t = time.time()
    r = SB.run_page(page, s=s, lam=lam, log=log, nsub=args.nsub, refine=args.refine, depth=args.depth,
                    fine=(args.fine_nsub, args.fine_refine), grid=tuple(args.grid))
    r["when"] = time.strftime("%Y-%m-%d %H:%M:%S")
    r["settings"] = dict(nsub=args.nsub, refine=args.refine, depth=args.depth, fine=[args.fine_nsub, args.fine_refine], grid=args.grid)
    r["wall"] = round(time.time() - t, 1)
    log("  => %s %s at s=%.6f lam=%.6f (pad0 %.5f) in %.0fs: %s" % (page, r["verdict"], float(s), float(lam), r["pad0"], r["wall"], r.get("leaf")))
    return r


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--lam", default="1")
    ap.add_argument("--side", default=None)
    ap.add_argument("--sweep", default=None)
    ap.add_argument("--slabs", default=None, type=float)
    ap.add_argument("--lo", default=3.82, type=float)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "seal199.jsonl"))
    ap.add_argument("--nsub", type=int, default=4)
    ap.add_argument("--refine", type=int, default=2)
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--fine-nsub", type=int, default=8)
    ap.add_argument("--fine-refine", type=int, default=4)
    ap.add_argument("--grid", type=int, nargs=3, default=[2, 2, 2])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--wall", type=float, default=None, help="total wall (s) for the run")
    args = ap.parse_args(argv)
    pages = [p for p in args.pages.split(",") if p]
    if args.all:
        pages += [p for p in alive_a57v4() if p not in pages]
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    done = done_keys(out)
    T0 = time.time()

    def log(msg):
        print("[%6.0fs] %s" % (time.time() - T0, msg), flush=True)

    jobs = []                                          # (page, s, lam)
    if args.sweep:
        for v in args.sweep.split(","):
            jobs += [(p, S.S0, Fr(v)) for p in pages]
    elif args.slabs:
        ls = Fr(str(args.slabs))
        tops = []
        s = S.S0
        while float(s) > args.lo * (1 + 1e-12):
            tops.append(s)
            s = s / ls
        log("slabs: %d of ratio %.6f down to %.6f (pad0 %.5f each)" % (len(tops), float(ls), float(tops[-1] / ls), float(S.pad(0, ls))))
        for s in tops:
            jobs += [(p, s, ls) for p in pages]
    else:
        s = S.S0 if args.side is None else Fr(args.side)
        jobs = [(p, s, Fr(args.lam)) for p in pages]
    for (p, s, lam) in jobs:
        if args.wall and time.time() - T0 > args.wall:
            log("wall reached; stopping")
            break
        if not args.force and (p, round(float(s), 9), round(float(lam), 9)) in done:
            log("skip %s (done)" % p)
            continue
        try:
            r = one(p, s, lam, args, log)
        except Exception as e:                      # record the failure, keep going
            r = dict(page=p, s=float(s), lam=float(lam), verdict="ERROR", error=repr(e)[:300], when=time.strftime("%Y-%m-%d %H:%M:%S"))
            log("  !! %s ERROR %r" % (p, e))
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(r) + "\n")
    log("done")


if __name__ == "__main__":
    main()
