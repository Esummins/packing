"""A136 T1 -- the positive control: A120's 22 PASSing NO certificates, re-written through the
F-COVER wrapper and RE-CERTIFIED under the frozen verifier.

    python recert136.py [--shard i/n] [--wall 2600]

For every certificate A120 emitted that the frozen `verify_case.py` accepted:

  1. the NO zone is re-derived from the node's OWN exact hypothesis (`hyp.nofams` of the LP node
     json, which A120 built at full precision) and written INWARD; the mapped A119 box the YES
     side names is written INWARD too and put into the certificate; the zone is intersected with
     it (`a136lib.narrow`);
  2. `ZONE subset BOX` is checked on the WRITTEN rationals -- the decidable predicate, failing
     loudly (`FCoverError`);
  3. the per-bound CHANGE against A120's own written certificate is measured (expected
     <= 1.2e-7 in t and <= 1.5e-9 in the centre bounds);
  4. the rewritten certificate is REPLAYED through the frozen `verify_case.py`
     (sha 521cb01f..., byte-identical, checked).  This is a replay, NOT a re-emission: the atoms,
     the weights and the cores are A120's, untouched, and only the NO zone (which the verifier
     reads as an EXEMPTION) has moved.  The zone got SMALLER, so strictly fewer boxes are exempt
     and the same measure has strictly more to cover: a PASS here is a stronger statement than
     A120's, and a FAIL is a genuine result, not a rounding artefact.

Read-only on A120: the rewritten certificates are new files under this attempt's certs/.
"""
from __future__ import annotations

import argparse, glob, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a136lib as A                                                # noqa: E402

A120B = os.path.join(A.ROOT, "attempts", "A120-no-side-runner")
A120N = os.path.join(A120B, "results", "nodes")
A120CERTS = os.path.join(A120B, "certs")


def passing_certificates():
    """Every certificate file A120 wrote whose `.json.done` records result PASS, with the node
    record and the LP node json it was emitted from."""
    out = []
    for p in sorted(glob.glob(os.path.join(A120CERTS, "*.json.done"))):
        d = A.jload(p)
        if d.get("result") != "PASS":
            continue
        tag = d["tag"]
        cert = os.path.join(A120CERTS, tag + ".json")
        if not os.path.exists(cert):
            continue
        # tag = <nid>_a120__a116N__NO<i>[_r<rounds>]
        key = tag.split("__")[-1]
        base = key.split("_r")[0]
        nid = tag.split("_a120__")[0]
        node_json = os.path.join(A120N, "%s_a120__a116N__%s.json" % (nid, base))
        cls = nid.split("_interior")[0]
        rec = os.path.join(A120N, "rec__%s__%s.json" % (cls, nid))
        if not (os.path.exists(node_json) and os.path.exists(rec)):
            continue
        out.append(dict(tag=tag, cert=cert, node_json=node_json, rec=rec, nid=nid, key=key,
                        base=base, a120_seconds=d.get("seconds"), a120_rounds=d.get("rounds")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--wall", type=float, default=2600.0)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--rewrite_only", action="store_true")
    a = ap.parse_args()
    i, n = (int(x) for x in a.shard.split("/"))
    log = A.mklog("recert136_%d.log" % i)

    allc = passing_certificates()
    mine = [c for k, c in enumerate(allc) if k % n == i]
    log("A136 T1: %d PASSing A120 certificates total, %d in shard %d/%d" % (len(allc), len(mine), i, n))
    outp = os.path.join(A.RES, "t1_recert_%d.jsonl" % i)
    done = set()
    if os.path.exists(outp):
        with open(outp, encoding="utf-8") as f:
            for ln in f:
                try:
                    done.add(json.loads(ln)["tag"])
                except Exception:
                    pass
    t0 = time.time()
    for c in mine:
        if c["tag"] in done:
            log("  [cache] %s" % c["tag"])
            continue
        node = A.jload(c["node_json"])
        rec = A.jload(c["rec"])
        s = node["s"]
        row = dict(tag=c["tag"], node=c["nid"], child=c["key"], s=s,
                   a120=dict(seconds=c["a120_seconds"], rounds=c["a120_rounds"], result="PASS"))
        newp = os.path.join(A.CERTS, c["tag"] + ".fcover.json")
        try:
            cert, rep = A.narrow_file(c["cert"], node["hyp"]["nofams"], rec["boxes_used"], s,
                                      newp, tag=c["tag"])
        except A.FCoverError as e:
            row.update(zone_sub_box=False, error=str(e), result="FCOVER-FAIL")
            with open(outp, "a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
            log("  %-52s FCOVER-FAIL %s" % (c["tag"], e))
            continue
        row["zone_sub_box"] = True
        row["fcover"] = rep
        row["max_abs_delta"] = max(r["max_abs_delta"] for r in rep)
        row["cert_file"] = os.path.relpath(newp, A.ROOT)
        log("  %-52s ZONE subset BOX ok, max bound change %.3e"
            % (c["tag"], row["max_abs_delta"]))
        if a.rewrite_only:
            with open(outp, "a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
            continue
        v = A.verify_frozen(newp, jobs=1, depth=a.depth, max_w=64, wall=a.wall)
        row["verify"] = v
        row["result"] = v["result"]
        with open(outp, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        log("  %-52s re-certified %s (%.0f s; A120 %.0f s)"
            % (c["tag"], v["result"], v["seconds"], c["a120_seconds"] or 0.0))
    log("T1 shard %d done in %.0f s" % (i, time.time() - t0))


if __name__ == "__main__":
    sys.exit(main())
