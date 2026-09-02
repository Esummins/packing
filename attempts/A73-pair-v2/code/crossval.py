#!/usr/bin/env python
# -*- coding: ascii -*-
"""crossval.py -- C3 cross-validation: reference verify_pair2.py vs the compiled
verify_pair2_rs on the v1 toy corpus + corruption gates + A73 anchors.
Verdicts and (W2, threshold) must agree; node counts may differ (free heuristics).
Writes results/crossval.json."""
import copy
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A73 = os.path.abspath(os.path.join(HERE, ".."))
A66C = os.path.abspath(os.path.join(A73, "..", "A66-corners4-pair", "certs"))
RS = os.path.join(HERE, "verify_pair2_rs", "target", "release", "verify_pair2.exe")
PY = sys.executable


def run_one(tool, cert, extra):
    if tool == "py":
        cmd = [PY, os.path.join(HERE, "verify_pair2.py"), cert] + extra
    else:
        cmd = [RS, cert] + extra
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
    verdict = None
    for line in (r.stdout or "").splitlines():
        if "VERDICT" in line:
            verdict = line.strip()
    return {"exit": r.returncode, "verdict_line": verdict}


def main():
    rs = RS if os.path.exists(RS) else RS.replace(".exe", "")
    if not os.path.exists(rs):
        print("compiled binary not found at %s" % RS)
        return 2
    cases = [
        ("toy_s199", os.path.join(A66C, "pair_toy_s199.json"), ["--depth", "40"], 0),
        ("control_s201", os.path.join(A66C, "pair_control_s201.json"),
         ["--depth", "12"], 1),
        ("smoke_paths", os.path.join(A66C, "pair_smoke_paths.json"),
         ["--depth", "26"], 1),
        ("anchor05", os.path.join(A73, "certs", "anchor_grid05_s3.json"),
         ["--depth", "40"], 0),
        ("anchor06", os.path.join(A73, "certs", "anchor_grid06_s3.json"),
         ["--depth", "40"], 0),
    ]
    # corruption gates from the smoke cert
    base = json.load(open(os.path.join(A66C, "pair_smoke_paths.json")))
    gates = []
    g = copy.deepcopy(base); g["provenance"] = {"x": 1.5}
    gates.append(("gate_float", g, 2))
    g = copy.deepcopy(base); g["total"] = "1/1"
    gates.append(("gate_total", g, 2))
    g = copy.deepcopy(base); g["atoms"][0]["w"] = "100/1"; g.pop("total", None)
    gates.append(("gate_p1", g, 2))
    gdir = os.path.join(A73, "results", "xval_gates")
    os.makedirs(gdir, exist_ok=True)
    for name, doc, exp in gates:
        p = os.path.join(gdir, name + ".json")
        if name == "gate_float":
            # must write the raw float literal (json.dump would too)
            json.dump(doc, open(p, "w"))
        else:
            json.dump(doc, open(p, "w"))
        cases.append((name, p, ["--depth", "6"], exp))

    out = {"binary": rs, "cases": {}}
    agree_all = True
    for name, cert, extra, expected in cases:
        rp = run_one("py", cert, extra)
        rr = run_one("rs", cert, extra)
        agree = (rp["exit"] == rr["exit"] == expected)
        agree_all &= agree
        out["cases"][name] = {"expected_exit": expected, "py": rp, "rs": rr,
                              "agree": agree}
        print("%-14s expected=%d py=%d rs=%d %s"
              % (name, expected, rp["exit"], rr["exit"],
                 "OK" if agree else "MISMATCH"))
    out["all_agree"] = agree_all
    json.dump(out, open(os.path.join(A73, "results", "crossval.json"), "w"),
              indent=1)
    print("ALL %s" % ("AGREE" if agree_all else "MISMATCH"))
    return 0 if agree_all else 1


if __name__ == "__main__":
    sys.exit(main())
