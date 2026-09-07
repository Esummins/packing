"""A120 T2 -- the controls, BEFORE any run.

C1  A112's two END-TO-END KILLS (`k5_11_interior_Y0036_D07_D01`, `k5_11_interior_Y0276_D05`; both
    are T5'' root kills, TRIM-EMPTY, no LP and no certificate) replayed through THIS runner's own
    code path -- `regiontree.logic_kill` reached through a120lib's imports, with A112's output
    directories redirected into A120.  The whole `logic` record must come back byte-identical to
    the one A112 stored, for every one of its four orderings.

C2  A112's 35 PASSing NO certificates replayed through the FROZEN verifier by the very call the
    runner makes -- `certify.run_verifier(cert, jobs=1, depth=56, max_w=64)` ->
    `verify_case.py` (sha 521cb01f...).  The stored certificates are replayed, never re-emitted:
    `certify.py --loop_cols` re-solves the node LP before emitting, so the EMISSION is wall-clock
    dependent while the VERIFIER is deterministic (A57 code/FREEZE_TAGS.txt).  Every field of the
    report except the certificate's own path and `time_s` must be identical.

C3  The COVERING ASSERTION on 3 target nodes: >= 10^4 SURVIVING configurations drawn with the four
    L squares in the MAPPED boxes and the pins in their slack cores, each tested at 30 sides
    spanning [3.82, s0].  A hit -- a packing of L u P at side <= s0 -- would refute the frame map
    or Theorem LOCAL.  Reported as drawn -> tested -> hits.

Writes results/t2_controls.json and logs/control.log.  READ-ONLY on A112 (certificates are copied
into this attempt before the verifier is pointed at them).
"""
from __future__ import annotations

import argparse, glob, hashlib, json, os, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a120lib as A                                     # noqa: E402
import regiontree as RT                                 # noqa: E402
import certify as CERTIFY                               # noqa: E402  (A112's, byte-identical)
from caselp import Hyp                                  # noqa: E402

KILLS = ["k5_11_interior_Y0036_D07_D01", "k5_11_interior_Y0276_D05"]
ORDERINGS = ["hybrid", "loadpath", "stranded", "wastage"]
A112C = os.path.join(A.ROOT, "attempts", "A112-dual-branching", "certs")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


# ------------------------------------------------------------------ C1
def replay_kills(log):
    out = []
    for nid in KILLS:
        for ordering in ORDERINGS:
            p = os.path.join(A.A112R, "rt_m2", nid, ordering, "R.json")
            if not os.path.exists(p):
                out.append(dict(node=nid, ordering=ordering, error="stored record missing"))
                continue
            stored = A.jload(p)
            hyp = Hyp.from_json(stored["hyp"])
            # A112 ran this with sample=True, seed = abs(hash("R")) % 1e6, nsample = 400; a
            # TRIM-EMPTY verdict returns before any pair is sampled, so the record is seed-free.
            got = RT.logic_kill(hyp, stored["s"], sample=True,
                                seed=abs(hash("R")) % 10 ** 6, nsample=400)
            same = canon(got) == canon(stored.get("logic"))
            out.append(dict(node=nid, ordering=ordering, stored_status=stored.get("status"),
                            stored_rule=(stored.get("logic") or {}).get("rule"),
                            replay_rule=got.get("rule"), replay_dead=got.get("dead"),
                            byte_identical=bool(same),
                            stored_sha=hashlib.sha256(canon(stored.get("logic")).encode()).hexdigest()[:16],
                            replay_sha=hashlib.sha256(canon(got).encode()).hexdigest()[:16]))
            log("  C1 %-30s %-9s stored=%s replay=%s identical=%s"
                % (nid, ordering, (stored.get("logic") or {}).get("rule"), got.get("rule"), same))
    return out


# ------------------------------------------------------------------ C2
def a112_no_certs():
    rows = []
    for p in sorted(glob.glob(os.path.join(A.A112R, "rt*", "*", "*", "*.json"))):
        try:
            r = A.jload(p)
        except Exception:
            continue
        if r.get("kind") == "NO" and (r.get("cert") or {}).get("result") == "PASS":
            rows.append(dict(rec=os.path.relpath(p, A.ROOT), tag=r["cert"]["tag"],
                             region=r.get("region"), ordering=r.get("ordering"),
                             key=r.get("key"), stored_seconds=r["cert"].get("seconds")))
    return rows


def replay_certs(log, jobs=1, depth=56, max_w=64, limit=0):
    rows = a112_no_certs()
    if limit:
        rows = rows[:limit]
    vc = os.path.join(A.A112C, "verify_case.py")
    out = dict(verify_case_sha256=sha(vc), n=len(rows), certs=[], all_pass=True,
               all_identical=True, seconds=0.0)
    for r in rows:
        src = os.path.join(A112C, r["tag"] + ".json")
        rep_src = os.path.join(A112C, r["tag"] + ".report.json")
        dst = os.path.join(A.CERTS, "replay__" + r["tag"] + ".json")
        if not os.path.exists(dst):
            shutil.copyfile(src, dst)                       # read-only on A112
        A.L.gate(log, "replay " + r["tag"])
        t0 = time.time()
        rc, txt = CERTIFY.run_verifier(dst, jobs, depth, max_w=max_w)
        dt = time.time() - t0
        out["seconds"] += dt
        got = None
        gp = os.path.splitext(dst)[0] + ".report.json"
        if os.path.exists(gp):
            got = A.jload(gp)
        stored = A.jload(rep_src) if os.path.exists(rep_src) else None
        drop = ("cert", "time_s")
        ident = None
        diffs = []
        if got is not None and stored is not None:
            g = {k: v for k, v in got.items() if k not in drop}
            s_ = {k: v for k, v in stored.items() if k not in drop}
            ident = canon(g) == canon(s_)
            if not ident:
                diffs = sorted(k for k in set(g) | set(s_) if canon(g.get(k)) != canon(s_.get(k)))
        res = (got or {}).get("result")
        row = dict(tag=r["tag"], region=r["region"], ordering=r["ordering"], key=r["key"],
                   cert_sha256=sha(src), rc=rc, result=res, stored_result="PASS",
                   report_identical=ident, differing_fields=diffs,
                   seconds=round(dt, 1), stored_seconds=r["stored_seconds"],
                   boxes=(got or {}).get("stats", {}).get("boxes"))
        out["certs"].append(row)
        out["all_pass"] &= (res == "PASS" and rc == 0)
        out["all_identical"] &= bool(ident)
        log("  C2 %-58s %s identical=%s (%.1f s, %s boxes)"
            % (r["tag"][:58], res, ident, dt, row["boxes"]))
    out["seconds"] = round(out["seconds"], 1)
    return out


# ------------------------------------------------------------------ C3
def covering(log, nodes, n_survivors=10000, seed=101):
    _, entry = A.n_entry()
    ex = A.extract_index()
    out = []
    for k, nid in enumerate(nodes):
        op = ex[nid].get("struct_op") or "e"
        mapped = [A.map_box(b, op) for b in entry["boxes"]]
        mpins = [A.map_pin(p, op) for p in entry["pins"]]
        lp, _ = A.node_src(nid)
        node = A.jload(lp)
        snd = A.soundness(nid, op, mapped, mpins, node["hyp"], entry, nsample=250)
        t0 = time.time()
        c = A.covering_check(mapped, mpins, n_survivors=n_survivors, seed=seed + k)
        c["seconds"] = round(time.time() - t0, 1)
        c["node"] = nid
        c["struct_op"] = op
        c["soundness_ok"] = snd["ok"]
        c["boxes"] = [dict(name=m["name"], x=[m["x0"], m["x1"]], y=[m["y0"], m["y1"]],
                           theta=[m["th0"], m["th1"]]) for m in mapped]
        out.append(c)
        log("  C3 %-30s %-5s drawn %d -> tested %d -> hits %d  (%.0f s)"
            % (nid, op, c["drawn"], c["tested"], c["hits"], c["seconds"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="all", help="c1|c2|c3|all")
    ap.add_argument("--survivors", type=int, default=10000)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--nodes", default="k5_11_interior_Y0230,k5_11_interior_Y0637,"
                                       "k5_11_interior_Y0036_D07_D00")
    a = ap.parse_args()
    log = A.mklog("control.log")
    p = os.path.join(A.RES, "t2_controls.json")
    out = A.jload(p) if os.path.exists(p) else dict(generated=None)
    t0 = time.time()
    if a.part in ("c1", "all"):
        log("C1: A112's two end-to-end kills through the runner's own logic path")
        out["C1_end_to_end_kills"] = replay_kills(log)
    if a.part in ("c2", "all"):
        log("C2: A112's 35 PASSing NO certificates through the frozen verify_case.py")
        out["C2_no_certificates"] = replay_certs(log, limit=a.limit)
    if a.part in ("c3", "all"):
        log("C3: the covering assertion on 3 target nodes")
        out["C3_covering"] = covering(log, [x for x in a.nodes.split(",") if x],
                                      n_survivors=a.survivors)
    out["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    out["seconds"] = round(time.time() - t0, 1)
    c1 = out.get("C1_end_to_end_kills") or []
    c2 = out.get("C2_no_certificates") or {}
    c3 = out.get("C3_covering") or []
    out["verdict"] = dict(
        C1_all_identical=bool(c1) and all(r.get("byte_identical") for r in c1),
        C2_all_pass=bool(c2.get("all_pass")), C2_all_identical=bool(c2.get("all_identical")),
        C3_all_zero_hits=bool(c3) and all(r["hits"] == 0 and r["tested"] >= 10000 for r in c3))
    A.jdump(p, out)
    log("T2 verdict: " + json.dumps(out["verdict"]))


if __name__ == "__main__":
    main()
