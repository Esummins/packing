"""A185 regression: on v1 certificates (no `windows` field) verify_case_v4 must give the IDENTICAL verdict and
the IDENTICAL box-tree statistics as the frozen v1 verifier, run in-process with the same arguments (jobs 1,
the report's depth / split / scale_weights, --max-witnesses 64).  Sample: 25 PASS + 25 FAIL from
attempts/A149-a57-reprice/certs and 25 PASS + 25 FAIL from attempts/A57-shadow-trees/certs (smallest report
time first).  Writes results/regress185.json; read-only on the corpora (reports/witnesses go to results/tmp).

    python regress185.py [--per 25] [--max-time 60]
"""
import argparse
import contextlib
import glob
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
RES = os.path.join(BASE, "results")
TMP = os.path.join(RES, "tmp")
os.makedirs(TMP, exist_ok=True)
sys.path.insert(0, HERE)
import prio185                                                  # noqa: E402,F401  BelowNormal, affinity 0xFFFF
import verify_case_v4 as v4                                      # noqa: E402  (asserts the frozen shas)
vc = v4.vc

CORPORA = [os.path.join(ATT, "A149-a57-reprice", "certs"), os.path.join(ATT, "A57-shadow-trees", "certs")]


def pick(corpus, per, max_time):
    rows = {"PASS": [], "FAIL": []}
    for rp in glob.glob(os.path.join(corpus, "**", "*.report.json"), recursive=True):
        try:
            r = json.load(open(rp))
        except Exception:                                        # noqa: BLE001
            continue
        cert = rp[:-len(".report.json")] + ".json"
        if r.get("result") not in rows or not os.path.exists(cert):
            continue
        if r.get("time_s", 1e9) > max_time:
            continue
        if not (r.get("stats") or {}).get("boxes"):
            continue                                             # no tree was walked (rc 2): uninformative
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per", type=int, default=25)
    ap.add_argument("--max-time", type=float, default=60.0)
    a = ap.parse_args()
    items = []
    for c in CORPORA:
        items += pick(c, a.per, a.max_time)
    print("regress185: %d certificates" % len(items), flush=True)
    results, n_ok = [], 0
    t00 = time.time()
    for k, (cert, rep) in enumerate(items):
        depth = int(rep.get("depth", 48))
        split = int(rep.get("split", 3))
        scale = str(rep.get("scale_weights", "1"))
        tag = os.path.basename(cert)[:-5]
        row = dict(cert=os.path.relpath(cert, ATT).replace("\\", "/"), report_result=rep.get("result"),
                   depth=depth, split=split, scale=scale)
        args = [cert, "--jobs", "1", "--depth", str(depth), "--split", str(split), "--scale-weights", scale,
                "--max-witnesses", "64", "--quiet"]
        out = {}
        for name, fn in (("v1", vc.main), ("v4", v4.main)):
            rp = os.path.join(TMP, "%s.%s.report.json" % (tag, name))
            wf = os.path.join(TMP, "%s.%s.witnesses.json" % (tag, name))
            t0 = time.time()
            rc, txt = run(fn, args + ["--report", rp, "--witness-file", wf])
            st = json.load(open(rp))["stats"] if os.path.exists(rp) else None
            if name == "v4" and st is not None:
                st = st.get("free", st)
                st.pop("exempt_poly", None)          # v3's own extra counter (always 0 without polycores)
            out[name] = dict(rc=rc, stats=st, time=round(time.time() - t0, 2))
        same = (out["v1"]["rc"] == out["v4"]["rc"]) and (out["v1"]["stats"] == out["v4"]["stats"])
        row.update(v1_rc=out["v1"]["rc"], v4_rc=out["v4"]["rc"], stats_identical=(out["v1"]["stats"] == out["v4"]["stats"]),
                   identical=same, t_v1=out["v1"]["time"], t_v4=out["v4"]["time"],
                   boxes=(out["v1"]["stats"] or {}).get("boxes"))
        n_ok += bool(same)
        results.append(row)
        print("%3d/%d %-60s v1 rc %s v4 rc %s boxes %s %s  (%.1fs/%.1fs)" % (
            k + 1, len(items), tag[:60], row["v1_rc"], row["v4_rc"], row["boxes"],
            "IDENTICAL" if same else "*** DIFFERENT ***", row["t_v1"], row["t_v4"]), flush=True)
        json.dump(dict(n=len(items), identical=n_ok, rows=results, elapsed_s=round(time.time() - t00, 1)),
                  open(os.path.join(RES, "regress185.json"), "w"), indent=1)
    print("regress185: %d / %d identical (verdict AND box-tree statistics), %.0f s" % (n_ok, len(items), time.time() - t00))


if __name__ == "__main__":
    main()
