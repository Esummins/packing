"""A170 -- EMPIRICAL audit of the `make_certificate` stock-core reversion.

For every certificate on disk (READ-ONLY), read the cores the certificate carries together with the
BOX each core carries, and recompute

  * the STOCK half-side   `caselp.Box.core().a`      (what `Hyp.from_json` rebuilds), and
  * the EXACT half-side   `exactcore.exact_a(box)`   (what A135 certifies and what an ExactHyp LP's
    row filter actually used).

Three outcomes per certificate:

  cores=exact   every carried `a` equals the exact `a`      -> emission lane carried the exact cores
  cores=stock   every carried `a` equals the stock `a`      -> `Hyp.from_json` reversion (or a
                                                               genuinely stock-core LP)
  cores=mixed   anything else

`bug` is True when the certificate is stock-cored AND the exact core is strictly larger AND the
certificate's provenance says it came from an exact-core lane -- that is the reversion, verbatim.

Nothing is written outside `attempts/A170-certfix/`.

    python code/scan170.py --out results/scan170.json
"""
import argparse
import collections
import glob
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (os.path.join(ATT, "A57-shadow-trees", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from caselp import Box                                        # noqa: E402  READ-ONLY (A57)
import exactcore as EC                                        # noqa: E402  READ-ONLY (A135)

SKIP = (".report.json", ".witnesses.json", ".certify.json", ".resolve2.json")


def box_of(c):
    b = c.get("box")
    if not b:
        return None
    return Box(**{k: b[k] for k in ("x0", "x1", "y0", "y1", "th0", "th1")})


def verdict_of(path):
    """the recorded frozen-verifier verdict beside a certificate, if any."""
    base = path[:-5]
    for suf in (".certify.json", ".report.json"):
        p = base + suf
        if os.path.exists(p):
            try:
                d = json.load(open(p, encoding="utf-8"))
            except Exception:                                  # noqa: BLE001
                continue
            v = d.get("result")
            if v:
                return str(v), os.path.basename(p)
    return None, None


def scan_one(path, cache):
    d = json.load(open(path, encoding="utf-8"))
    if d.get("format") != "case-measure-certificate-v1":
        return None
    prov = d.get("provenance", {}) or {}
    method = prov.get("method", "")
    exact_lane = bool(prov.get("cores_exact") or prov.get("core_scope")
                      or "exact-core" in method.lower())
    cores = (d.get("hypotheses", {}) or {}).get("cores") or []
    rows, kind = [], "none"
    n_stock = n_exact = n_other = 0
    err = None
    for c in cores:
        b = box_of(c)
        if b is None:
            err = "core carries no box"
            break
        key = (b.x0, b.x1, b.y0, b.y1, b.th0, b.th1)
        if key not in cache:
            try:
                ea, sa, ok = EC.exact_a(b)
            except Exception as ex:                            # noqa: BLE001
                cache[key] = (None, None, False, repr(ex)[:100])
            else:
                cache[key] = (ea, sa, ok, None)
        ea, sa, ok, e2 = cache[key]
        if ea is None:
            err = e2 or "exact_a failed"
            break
        car = Fr(c["a"])
        if car == ea and ea != sa:
            n_exact += 1
        elif car == sa:
            n_stock += 1
            if ea != sa:
                pass
        elif car == ea == sa:
            n_exact += 1
            n_stock += 1
        else:
            n_other += 1
        rows.append(dict(carried=str(car), exact=str(ea), stock=str(sa), vertex_ok=bool(ok),
                         ratio_ex_car=(float(ea) / float(car) if car else None)))
    if err:
        return dict(cert=os.path.relpath(path, ROOT).replace("\\", "/"), error=err)
    if n_other:
        kind = "mixed"
    elif n_exact and not [r for r in rows if Fr(r["carried"]) != Fr(r["exact"])]:
        kind = "exact"
    elif rows and all(Fr(r["carried"]) == Fr(r["stock"]) for r in rows):
        kind = "stock"
    elif rows:
        kind = "mixed"
    gap = max([r["ratio_ex_car"] for r in rows] or [1.0])
    v, vsrc = verdict_of(path)
    return dict(cert=os.path.relpath(path, ROOT).replace("\\", "/"),
                lane=os.path.relpath(path, ATT).replace("\\", "/").split("/")[0],
                ncores=len(cores), kind=kind, exact_lane=exact_lane, method=method[:70],
                max_ratio_exact_over_carried=gap, verdict=v, verdict_src=vsrc,
                budget=d.get("budget"), total=d.get("total"),
                bug=bool(kind == "stock" and gap > 1.0 + 1e-12 and exact_lane),
                repairable=bool(kind != "exact" and gap > 1.0 + 1e-12),
                cores=rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default=os.path.join(ATT, "*", "certs", "*.json"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "scan170.json"))
    ap.add_argument("--lanes", default="", help="comma-separated attempt dir names to restrict to")
    a = ap.parse_args()
    files = [f for f in sorted(glob.glob(a.glob)) if not f.endswith(SKIP)]
    if a.lanes:
        keep = set(a.lanes.split(","))
        files = [f for f in files if os.path.relpath(f, ATT).replace("\\", "/").split("/")[0] in keep]
    cache, out, skipped = {}, [], 0
    for i, f in enumerate(files):
        try:
            r = scan_one(f, cache)
        except Exception as ex:                                # noqa: BLE001
            r = dict(cert=os.path.relpath(f, ROOT).replace("\\", "/"), error=repr(ex)[:120])
        if r is None:
            skipped += 1
            continue
        out.append(r)
        if (i + 1) % 200 == 0:
            print("  %d/%d" % (i + 1, len(files)), flush=True)
    tab = collections.defaultdict(collections.Counter)
    for r in out:
        if "error" in r:
            tab[r["cert"].split("/")[1]]["error"] += 1
            continue
        tab[r["lane"]][r["kind"] + ("+BUG" if r["bug"] else "")] += 1
    print("%-34s %s" % ("lane", "kinds"))
    for L in sorted(tab):
        print("%-34s %s" % (L, dict(tab[L])))
    json.dump(dict(nfiles=len(files), nskipped=skipped, rows=out), open(a.out, "w"), indent=0)
    print("wrote %s  (%d certificates, %d non-certificate json skipped)"
          % (a.out, len(out), skipped), flush=True)


if __name__ == "__main__":
    main()
