"""A139 (R4) -- inspect a `local-cert-t-v2` certificate: shapes, denominators, counts.

READ-ONLY on every campaign directory.  Writes nothing.
"""
from __future__ import annotations

import gzip, json, os, sys
from fractions import Fraction as Q

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
CERT = os.path.join(ROOT, "attempts", "A134-certcover-close", "certs")


def den2(x):
    """(odd part, power of two) of the denominator."""
    d = Q(x).denominator
    k = 0
    while d % 2 == 0:
        d //= 2
        k += 1
    return d, k


def main():
    cid = sys.argv[1]
    with gzip.open(os.path.join(CERT, cid + ".t2cert.json.gz"), "rt", encoding="utf-8") as f:
        c = json.load(f)
    print("top keys:", sorted(c.keys()))
    m = c["meta"]
    print("meta keys:", sorted(m.keys()))
    print("format", m["format"], "nv", m["nv"], "s_lo", m["s_lo"], "s_hi", m["s_hi"])
    for b in m["bodies"]:
        print("  body", {k: v for k, v in b.items()})
    print("leaves:", len(c["leaves"]))
    L0 = c["leaves"][0]
    print("leaf keys:", sorted(L0.keys()))
    print("leaf0 box[:3]:", L0["box"][:3])
    print("leaf0 rows[0]:", json.dumps(L0["rows"][0])[:400])
    print("root keys:", sorted(c["root"].keys()))
    # node kind census + max depth + node field samples
    kinds = {}
    seen = {}
    maxdepth = [0]
    dens = {}

    def note(x, tag):
        od, k = den2(x)
        d = dens.setdefault(tag, [0, 0, set()])
        d[0] = max(d[0], k)
        d[1] = max(d[1], len(str(Q(x).numerator)))
        d[2].add(od)

    def walk(n, d):
        maxdepth[0] = max(maxdepth[0], d)
        kinds[n["k"]] = kinds.get(n["k"], 0) + 1
        if n["k"] not in seen:
            seen[n["k"]] = {k: (v if k != "ch" else "<%d children>" % len(v)) for k, v in n.items()}
        if n["k"] == "bisect":
            note(n["mid"], "mid")
        for ch in n.get("ch", []):
            walk(ch, d + 1)

    walk(c["root"], 0)
    print("node census:", kinds, "max depth", maxdepth[0])
    for k, v in seen.items():
        print("  sample", k, json.dumps(v)[:400])
    # leaf box denominators
    nb = 0
    for L in c["leaves"]:
        for lo, hi in L["box"]:
            note(lo, "box"); note(hi, "box")
        for r in L["rows"]:
            nb += 1
            note(r["k"], "rowk")
            for v, a in r["co"].items():
                note(a, "rowco")
            if "y" in r:
                note(r["y"], "rowy")
    print("rows:", nb)
    for tag, (k, nd, od) in sorted(dens.items()):
        print("  %-6s max 2-exp %3d  max |num| digits %3d  odd parts %s"
              % (tag, k, nd, sorted(od)[:6]))
    r0 = c["leaves"][0]["rows"][0]
    print("row keys:", sorted(r0.keys()))
    env, pc = c["env"], c["pcert"]
    print("env sizes:", {k: len(v) for k, v in env.items()})
    print("pcert sizes:", {k: len(v) for k, v in pc.items()})
    kh = sorted(env["h"])[0]
    print("env h sample:", kh, env["h"][kh])
    print("pcert h sample:", json.dumps(pc["h"][kh])[:300])
    ks = sorted(env["S"])[0]
    print("env S sample:", ks, env["S"][ks])
    print("pcert S sample keys:", sorted(pc["S"][ks].keys()), "tm", pc["S"][ks]["tm"])
    for mode in ("xy", "x", "y"):
        for kw in sorted(env["w"]):
            if pc["w"][kw]["mode"] == mode:
                print("env w sample (%s):" % mode, kw, env["w"][kw])
                print("  pcert w keys:", sorted(pc["w"][kw].keys()))
                print("  pcert w:", json.dumps(pc["w"][kw])[:400])
                break
    # tm == cell midpoint?
    bad = 0
    for k, v in pc["S"].items():
        a, b = (Q(t) for t in k.split("|"))
        if Q(v["tm"]) != (a + b) / 2:
            bad += 1
    print("S entries whose tm != cell midpoint:", bad)


if __name__ == "__main__":
    main()
