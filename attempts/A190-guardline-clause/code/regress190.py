"""A190 regression (A185's regress185 pattern, one clause up).

(a) On v1 certificates (no `windows`, no `guardlines`) verify_case_v5 must give the IDENTICAL verdict and the
    IDENTICAL box-tree statistics as the frozen v1 verifier, in-process, same arguments (jobs 1, the report's
    depth / split / scale_weights, --max-witnesses 64): 25 PASS + 25 FAIL from A149's certs, 25 + 25 from A57's.
(b) On every A185 v4 certificate on disk (`attempts/A185-boxed-windows-clause/certs/*.json`, the windows clause)
    v5 must give the identical verdict and identical per-clause statistics as v4.
Writes results/regress190.json; read-only on the corpora (reports / witnesses go to results/tmp).

    python regress190.py [--per 25] [--max-time 60] [--v4-max-time 900]
"""
import argparse
import contextlib
import glob
import io
import json
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
RES = os.path.join(BASE, "results")
TMP = os.path.join(RES, "tmp")
os.makedirs(TMP, exist_ok=True)
sys.path.insert(0, HERE)
import prio190                                                  # noqa: E402,F401  BelowNormal, affinity 0xFFFF
import verify_case_v5 as v5                                      # noqa: E402  (asserts the frozen shas)
vc, v4 = v5.vc, v5.v4

CORPORA = [os.path.join(ATT, "A149-a57-reprice", "certs"), os.path.join(ATT, "A57-shadow-trees", "certs")]
V4_CERTS = os.path.join(ATT, "A185-boxed-windows-clause", "certs")


def pick(corpus, per, max_time):
    rows = {"PASS": [], "FAIL": []}
    for rp in glob.glob(os.path.join(corpus, "**", "*.report.json"), recursive=True):
        try:
            r = json.load(open(rp))
        except Exception:                                        # noqa: BLE001
            continue
        cert = rp[:-len(".report.json")] + ".json"
        if r.get("result") not in rows or not os.path.exists(cert) or r.get("time_s", 1e9) > max_time:
            continue
        if not (r.get("stats") or {}).get("boxes"):
            continue
        try:
            c = json.load(open(cert))
            if F(c["total"]) * F(str(r.get("scale_weights", "1"))) >= int(c.get("budget", c.get("n", 11))):
                continue
        except Exception:                                        # noqa: BLE001
            continue
        rows[r["result"]].append((r.get("time_s", 0), cert, r))
    out = []
    for k in ("PASS", "FAIL"):
        rows[k].sort(key=lambda t: t[0])
        out += [(cert, r) for (_, cert, r) in rows[k][:per]]
    return out


def run(fn, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(argv)
    return rc, buf.getvalue()


def clean(st):
    """v5's own counters (always 0 without guard lines) are dropped before comparing with v1 / v4."""
    if st is None:
        return None
    st = dict(st)
    for k in ("line_boxes", "line_only_covers"):
        st.pop(k, None)
    return st


def compare(cert, rep, base_name, base_fn, tag):
    depth, split, scale = int(rep.get("depth", 48)), int(rep.get("split", 3)), str(rep.get("scale_weights", "1"))
    args = [cert, "--jobs", "1", "--depth", str(depth), "--split", str(split), "--scale-weights", scale,
            "--max-witnesses", "64", "--quiet"]
    out = {}
    for name, fn in ((base_name, base_fn), ("v5", v5.main)):
        rp = os.path.join(TMP, "%s.%s.report.json" % (tag, name))
        wf = os.path.join(TMP, "%s.%s.witnesses.json" % (tag, name))
        t0 = time.time()
        rc, _ = run(fn, args + ["--report", rp, "--witness-file", wf])
        st = json.load(open(rp))["stats"] if os.path.exists(rp) else None
        if st is not None and base_name == "v1" and name == "v5":
            st = st.get("free", st)
            st.pop("exempt_poly", None)
        if st is not None and base_name == "v4":
            st = {k: clean(v) for k, v in st.items()}
        out[name] = dict(rc=rc, stats=clean(st) if base_name == "v1" else st, time=round(time.time() - t0, 2))
    same = (out[base_name]["rc"] == out["v5"]["rc"]) and (out[base_name]["stats"] == out["v5"]["stats"])
    return same, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per", type=int, default=25)
    ap.add_argument("--max-time", type=float, default=60.0)
    ap.add_argument("--v4-max-time", type=float, default=900.0)
    ap.add_argument("--skip-v1", action="store_true")
    a = ap.parse_args()
    items = []
    if not a.skip_v1:
        for c in CORPORA:
            items += [("v1", cert, rep) for cert, rep in pick(c, a.per, a.max_time)]
    for cert in sorted(glob.glob(os.path.join(V4_CERTS, "*.json"))):
        if cert.endswith((".report.json", ".certify.json", ".witnesses.json", ".resolve.json")):
            continue
        rp = cert[:-5] + ".report.json"
        if not os.path.exists(rp):
            continue
        rep = json.load(open(rp))
        if rep.get("time_s", 1e9) <= a.v4_max_time:
            items.append(("v4", cert, rep))
    print("regress190: %d certificates (%d v1, %d v4)" % (len(items), sum(1 for i in items if i[0] == "v1"),
                                                         sum(1 for i in items if i[0] == "v4")), flush=True)
    results, n_ok = [], 0
    t00 = time.time()
    for k, (base, cert, rep) in enumerate(items):
        tag = os.path.basename(cert)[:-5][:80]
        same, out = compare(cert, rep, base, vc.main if base == "v1" else v4.main, tag)
        row = dict(base=base, cert=os.path.relpath(cert, ATT).replace("\\", "/"), report_result=rep.get("result"),
                   base_rc=out[base]["rc"], v5_rc=out["v5"]["rc"], identical=same,
                   t_base=out[base]["time"], t_v5=out["v5"]["time"])
        n_ok += bool(same)
        results.append(row)
        print("%3d/%d [%s] %-60s rc %s/%s %s (%.1fs/%.1fs)" % (k + 1, len(items), base, tag[:60], row["base_rc"],
                                                              row["v5_rc"], "IDENTICAL" if same else "*** DIFFERENT ***",
                                                              row["t_base"], row["t_v5"]), flush=True)
        json.dump(dict(n=len(items), identical=n_ok, rows=results, elapsed_s=round(time.time() - t00, 1)),
                  open(os.path.join(RES, "regress190.json"), "w"), indent=1)
    print("regress190: %d / %d identical (verdict AND box-tree statistics), %.0f s" % (n_ok, len(items), time.time() - t00))


if __name__ == "__main__":
    main()
