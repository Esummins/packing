"""A201 report: the table over A200's fast-phase certificates (ALIVE ones, both pads) -- what the cell-pair table did on
each: A200's witness cover dead? (by which rule), page dead?, exclusions by rule, refutations, exact seconds, the
per-step seconds.  Reads attempts/A200-k516-quick/certs/q200_*.json and attempts/A201-cell-pair-exclusion/certs/pe201_*.json.
    python report201.py [--md notes/table.md]
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A200C = os.path.join(ROOT, "attempts", "A200-k516-quick", "certs")
A201C = os.path.join(HERE, "..", "certs")


def load(f):
    try:
        return json.load(open(f, encoding="utf-8"))
    except Exception:
        return None


def fast_seconds(cert):
    return sum(float(s.get("seconds", 0)) for s in (cert.get("steps") or []) if s["step"] not in ("seal", "pair-test", "noroom"))


def steps_str(cert):
    out = []
    for s in cert.get("steps") or []:
        if s["step"] in ("seal", "pair-test", "noroom"):
            continue
        lab = s.get("label") or ""
        extra = ""
        if s["step"] == "count":
            extra = " r%s%s" % (s.get("refutations", 0), "" if s.get("feasible") else " DEAD")
        out.append("%s%s %.0f%s" % (s["step"], ("[" + lab + "]") if lab else "", s.get("seconds", 0), extra))
    return " > ".join(out)


def row(nid, pad):
    suf = "_pad0" if pad == "zero" else ""
    a = load(os.path.join(A200C, "q200_%s%s.json" % (nid, suf)))
    if a is None and pad == "g1":
        a = load(os.path.join(A200C, "q200_%s_deep.json" % nid))
    b = load(os.path.join(A201C, "pe201_%s%s.json" % (nid, suf)))
    r = dict(nid=nid.replace("k5_16_interior_", ""), pad=pad, a200=(a or {}).get("verdict"), a200_fast=round(fast_seconds(a), 0) if a else None)
    if b is None:
        r.update(a201="(not run)")
        return r
    rounds = b.get("rounds") or []
    pe = b.get("pair_excl") or {}
    by = {"A1": 0, "CN": 0, "EXACT": 0}
    nref = nrefd = 0
    exact_s = 0.0
    undec = 0
    for t in pe.get("rounds", []):
        for k, v in (t.get("by_rule") or {}).items():
            by[k] = by.get(k, 0) + v
        nref += t.get("n_refutations", 0)
        nrefd += t.get("n_refuted", 0)
        exact_s += float(t.get("exact_seconds") or 0)
        undec += t.get("undecided_budget", 0)
    wc = rounds[0].get("witness_check") if rounds else None
    wdead = None
    if wc:
        rules = sorted(set(p["rule"] for p in wc["pairs"] if not p["compatible"]))
        wdead = ("DEAD by " + "+".join(rules)) if wc["dead"] else "alive"
    last = rounds[-1] if rounds else {}
    cs = [s for s in b.get("steps") or [] if s["step"] == "count"]
    verified = cs[-1].get("cover_verified") if cs else None
    r.update(a201=b.get("verdict"), step_killed=b.get("step_killed"), witness_cover=wdead, excl_A1=by["A1"], excl_CN=by["CN"], excl_EXACT=by["EXACT"],
             refutations="%d (%d refuted)" % (nref, nrefd), undecided=undec, exact_s=round(exact_s, 0), seconds=b.get("seconds"),
             cover_verified=verified, decisive=b.get("decisive_rules"), steps=steps_str(b), leaf=(b.get("leaf") or "")[:120])
    return r


def main():
    nids = sorted(set(os.path.basename(f)[5:-5].replace("_pad0", "").replace("_deep", "") for f in glob.glob(os.path.join(A200C, "q200_*.json"))))
    rows = []
    for nid in nids:
        for pad in ("g1", "zero"):
            a = load(os.path.join(A200C, "q200_%s%s.json" % (nid, "_pad0" if pad == "zero" else "")))
            if a is None and pad == "g1":
                a = load(os.path.join(A200C, "q200_%s_deep.json" % nid))
            if a is None or a.get("verdict") != "ALIVE":
                continue
            rows.append(row(nid, pad))
    cols = ["nid", "pad", "a200", "a200_fast", "a201", "witness_cover", "excl_A1", "excl_CN", "excl_EXACT", "refutations", "undecided", "cover_verified", "exact_s", "seconds", "decisive"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    lines.append("")
    for r in rows:
        if r.get("steps"):
            lines.append("- %s / %s: %s%s" % (r["nid"], r["pad"], r["steps"], ("  -- " + r["leaf"]) if r.get("leaf") else ""))
    txt = "\n".join(lines)
    print(txt)
    if "--md" in sys.argv:
        p = sys.argv[sys.argv.index("--md") + 1]
        open(p, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    main()
