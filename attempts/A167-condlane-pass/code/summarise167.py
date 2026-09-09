"""A167 T6 -- which lever did the work in each kill, and the PI's cell in detail.

    python summarise167.py
"""
import argparse
import collections
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--certs", default=os.path.join(BASE, "certs"))
    ap.add_argument("--rows", nargs="*", default=[os.path.join(BASE, "results", f) for f in
                                                  ("pass_s0.jsonl", "pass_s1.jsonl",
                                                   "y0169.jsonl")])
    ap.add_argument("--nogo", default=os.path.join(BASE, "results", "nogo.jsonl"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "levers.json"))
    a = ap.parse_args()

    pieces_tot = collections.Counter()
    per_cert = []
    for f in sorted(glob.glob(os.path.join(a.certs, "cond_*.json"))):
        c = json.load(open(f, encoding="utf-8"))
        kinds = collections.Counter()
        for p in c["pieces"]:
            if p.get("chord_contradiction"):
                k = "chord-contradiction (rhs < 0 on the piece)"
            elif p["m"] == 0:
                k = "m=0: beta=%d + LANE_out=%d" % (p.get("beta", -1), (p.get("out_cover") or
                                                                       {}).get("value", -1))
            elif p.get("beta") == 0:
                k = "m=1, per-piece beta=0 (no band cover needed)"
            else:
                k = "m=1, beta=%d, band cover closed LANE_band=%s" % (
                    p.get("beta"), (p.get("band_cover") or {}).get("value"))
            kinds[k] += 1
            pieces_tot[k] += 1
        per_cert.append(dict(cert=os.path.basename(f), nid=c["nid"], slot=c["slot"],
                             cls=c["cls"], level=c["level"], n_pieces=len(c["pieces"]),
                             kinds=dict(kinds),
                             offs=sorted({p["line"]["off"] for p in c["pieces"] if p.get("line")}),
                             sample=(c.get("sample_lines") or [None])[0]))
    print("== piece accounting over all A167 kill certificates ==")
    for k, v in pieces_tot.most_common():
        print("   %-58s %4d" % (k, v))
    print()
    print("== per certificate ==")
    for r in per_cert:
        print("%-34s %-9s L%-2s pieces=%-3d %s" % (r["nid"], r["slot"], r["level"],
                                                   r["n_pieces"], r["kinds"]))
    rows = {}
    for f in a.rows:
        if not os.path.exists(f):
            continue
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            if (r["nid"], r["slot"]) not in rows or r.get("verdict") == "KILL":
                rows[(r["nid"], r["slot"])] = r
    print()
    print("== c0_Y0169 (the PI's node) ==")
    for k, r in sorted(rows.items()):
        if k[0] == "c0_Y0169":
            print("%s %s -> %s  pieces %s (done %s, open %s, nogo %s)  %s s"
                  % (k[0], k[1], r["verdict"], r.get("n_pieces"), r.get("n_done"),
                     r.get("n_open"), r.get("n_nogo"), r.get("elapsed")))
            ng = r.get("nogo") or {}
            if ng:
                print("   first no-go piece %r (m=%s): all %s swept offsets screened, "
                      "min free meeters over offsets = %s"
                      % (ng.get("path"), ng.get("m"), ng.get("n_dead_offsets"),
                         ng.get("dead_min_free")))
                for d in (ng.get("dead_sample") or [])[:3]:
                    print("      %s" % json.dumps(d))
    nog = {}
    if os.path.exists(a.nogo):
        for ln in open(a.nogo, encoding="utf-8"):
            q = json.loads(ln)
            nog[(q["nid"], q["slot"])] = q
    ok = [q for q in nog.values() if q.get("ok")]
    print()
    print("== exact two-crowd witnesses: %d of %d attempted ==" % (len(ok), len(nog)))
    byc = collections.Counter((q["cls"], q["slot"]) for q in ok)
    for k, v in byc.most_common():
        print("   %-8s %-9s %3d" % (k[0], k[1], v))
    if ok:
        q = ok[0]
        print("   example %s %s: H = %s, F = %s (gap %.4f, den %d)"
              % (q["nid"], q["slot"], q["H"], q["F"], q["gap"], q["den"]))
    json.dump(dict(piece_kinds=dict(pieces_tot), per_cert=per_cert,
                   nogo_exact=len(ok), nogo_attempted=len(nog),
                   nogo_by_class_slot={"%s|%s" % k: v for k, v in byc.items()}),
              open(a.out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
