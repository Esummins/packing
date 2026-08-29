#!/usr/bin/env python3
"""A42-T2 -- render results/chain.json as the chain table + slack-decay fit."""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHAIN = os.path.abspath(os.path.join(HERE, "..", "results", "chain.json"))


def f(x, spec="%.5f"):
    return "-" if x is None else (spec % x)


def main():
    d = json.load(open(CHAIN))
    rows = d["rows"]
    print("A42-T2 occupancy chain @ s0 = %s   r_occ=%s dth=%s  ORDER=%s"
          % (d["s_rat"], d["r_occ"], d["dth"], d["order"]))
    print("%-11s %-4s %-4s %-4s %-17s %9s %9s %8s %8s %5s %6s %6s %5s"
          % ("tag", "k", "ball", "bud", "status", "tau", "slack", "t_dec", "wall_s",
             "cert", "rows", "orbits", "fed"))
    for r in rows:
        print("%-11s %-4s %-4s %-4d %-17s %9s %9s %8s %8s %5s %6s %6s %5s"
              % (r["tag"], r["k"], r.get("ball"), r["budget"], r.get("status"),
                 f(r.get("tau")), f(r.get("slack"), "%+.5f"), f(r.get("t_decide"), "%.0f"),
                 f(r.get("wall_s"), "%.0f"), r.get("n_cert_attempts"), r.get("n_rows"),
                 r.get("n_orbits"), r.get("rows_fed_back")))
    ch = [r for r in rows if r["kind"] == "chain" and r.get("slack") is not None]
    ch.sort(key=lambda r: r["k"])
    if len(ch) >= 2:
        print("\nslack curve (tau - budget):")
        for r in ch:
            print("  k=%-3d %+.5f   %s" % (r["k"], r["slack"], r["status"]))
        neg = [r for r in ch if r["slack"] < 0]
        if len(neg) >= 2:
            k0, s0v = neg[0]["k"], -neg[0]["slack"]
            print("\n  |slack| decay from k=%d (|slack|=%.5f):" % (k0, s0v))
            for r in neg[1:]:
                dk = r["k"] - k0
                ratio = (-r["slack"]) / s0v if s0v else float("nan")
                print("    k=%-3d |slack|=%.5f  ratio=%.4f  per-step=%.4f"
                      % (r["k"], -r["slack"], ratio,
                         ratio ** (1.0 / dk) if dk and ratio > 0 else float("nan")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
