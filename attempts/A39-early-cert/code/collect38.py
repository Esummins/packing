#!/usr/bin/env python3
"""Rebuild a probe38 result document from the per-node .rec.json checkpoints (used when the
phase is cut at the wall), then aggregate."""
import argparse, glob, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aggregate38 as agg  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--parentfile", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", default="l2")
    ap.add_argument("--time_limit", type=float, default=180.0)
    ap.add_argument("--cert_cap", type=float, default=120.0)
    a = ap.parse_args()
    parents = json.load(open(a.parentfile))
    recs = []
    for f in sorted(glob.glob(os.path.join(a.outdir, "*.rec.json"))):
        try:
            recs.append(json.load(open(f)))
        except Exception as e:
            print("skip", f, e)
    have = {r["cid"] for r in recs}
    # fill in the children that never started as explicit notrun
    import probe38
    for p in parents:
        for (cb, split) in probe38.refine8(p["box"]):
            cid = "%s_p%s_%d%d%d" % (a.tag, p["id"], *split)
            if cid not in have:
                recs.append(dict(cid=cid, parent=p["id"], stratum=p["stratum"], split=list(split),
                                 box=cb, budget=p.get("budget", 10), status="notrun",
                                 seconds_lp=0.0, seconds_cert=0.0))
    recs.sort(key=lambda r: r["cid"])
    doc = dict(format="A38-depth-probe-v1", tag=a.tag, when=time.strftime("%Y-%m-%dT%H:%M:%S"),
               s="969271/250000", time_limit=a.time_limit, cert_cap=a.cert_cap,
               w1_row_filter="OFF (design Amendment 1)", parents=parents,
               n_children=len(recs), records=recs, note="rebuilt from checkpoints (wall cut)")
    doc["aggregate"] = agg.summarize(doc)
    json.dump(doc, open(a.out, "w"), indent=1)
    print(json.dumps(doc["aggregate"], indent=1))
    print("->", a.out, "n=%d" % len(recs))


if __name__ == "__main__":
    main()
