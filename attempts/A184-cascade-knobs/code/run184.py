"""A184 -- the job runner for E1 / E2 on the sample (results/sample184.json).

Experiments (every node built by common184.make_child = A183's own child construction, seeded by
construction from the parent's recorded fixed point):

  c   coarse-only D -> S -> B at nsub 4 / refine 2 (S2 from the coarse-only S1, S3 from that S2)
  f   A183's D -> S -> B at 4/2 then 8/3 on every survivor (S2 from A183's S1, S3 from that S2)
  b   D -> B -> S at 4/2: the (H, D, B) intermediate from the coarse-only S1, then S added

Keys: "c|S2|<s2node>", "c|S3|<s2node>|<bidx>", "f|...", "b|HDB|<chain>|<bidx>",
"b|S3|<s2node>|<bidx>" -- so "c|S3|X|k" and "b|S3|X|k" are the SAME hypothesis {H, D, S_X, B_k}
reached in two orders.  Records: results/nodes184_s<k>of<n>.jsonl (resumable; a node whose parent
is held by the other shard waits), one line per node with roles, kept, vol, timings, rows.

    python run184.py --shard 0/2 [--exps c,f,b] [--levels 1,2]
"""
import argparse
import os
import sys
import time

import common184 as C
from common184 import R, RS, Box

SAMPLE = os.path.join(C.RES, "sample184.json")
S1_OUT = os.path.join(C.RES, "nodes184_S1.jsonl")
PAUSE = os.path.join(C.RES, "PAUSE184")


def side_path(k, n):
    return os.path.join(C.RES, "nodes184_s%dof%d.jsonl" % (k, n))


def load_all(n):
    recs = C.load_jsonl(S1_OUT)
    for k in range(n):
        recs.update(C.load_jsonl(side_path(k, n)))
    return recs


def jobs_of(S, exps):
    """(level, key, exp, step, parent_key, chain, s_node, b_idx)"""
    out = []
    for chain, ent in S["chains"].items():
        if not ent.get("B") or not ent.get("S"):
            continue
        for s in ent["S"]:
            sn = s["node"]
            for e in ("c", "f"):
                if e in exps:
                    setting = "42" if e == "c" else "83"
                    out.append((1, "%s|S2|%s" % (e, sn), e, "S2", "S1|%s|%s" % (setting, chain), chain, sn, None))
                    for b in ent["B"]:
                        out.append((2, "%s|S3|%s|%d" % (e, sn, b["idx"]), e, "S3", "%s|S2|%s" % (e, sn), chain, sn, b["idx"]))
        if "b" in exps:
            for b in ent["B"]:
                out.append((1, "b|HDB|%s|%d" % (chain, b["idx"]), "b", "HDB", "S1|42|%s" % chain, chain, None, b["idx"]))
                for s in ent["S"]:
                    out.append((2, "b|S3|%s|%d" % (s["node"], b["idx"]), "b", "S3", "b|HDB|%s|%d" % (chain, b["idx"]),
                                chain, s["node"], b["idx"]))
    return out


def new_role(S, chain, s_node, b_idx, want):
    ent = S["chains"][chain]
    if want == "S":
        s = [x for x in ent["S"] if x["node"] == s_node][0]
        return R.Role("S", [Box(*p) for p in s["pieces"]], src=s["src"]), "TR"
    b = [x for x in ent["B"] if x["idx"] == b_idx][0]
    return R.Role.from_box("B", Box(*b["box"]), nsub=4, src=b["box"]), "BR"


def run_job(S, job, recs):
    level, key, exp, step, pkey, chain, s_node, b_idx = job
    par = recs[pkey]
    rec = dict(key=key, exp=exp, step=step, parent=pkey, chain=chain, s_node=s_node, b_idx=b_idx,
               order=("D,S,B" if exp in ("c", "f") else "D,B,S"))
    if not par["verdict"].startswith("ALIVE"):
        rec.update(verdict="DEAD(C, ancestor %s: %s)" % (pkey, par["verdict"][:60]), leaf="ancestor", t_total=0.0,
                   setting=par.get("setting"))
        return rec
    setting = "83" if exp == "f" else "42"
    want = "S" if step == "S2" or (exp == "b" and step == "S3") else "B"
    nr, corner = new_role(S, chain, s_node, b_idx, want)
    proles = C.roles_from_json(par["roles"])
    first = [r for r in proles if r.name == C.FIRST_OF.get(nr.name)] or [None]
    t0 = time.time()
    dead, det = C.pre_tests(nr.bbox(), corner, first[0])
    rec["pre"] = det
    rec["t_pre"] = round(time.time() - t0, 2)
    if dead:
        rec.update(verdict=dead, leaf="R3" if "R3" in dead else "R1", t_total=rec["t_pre"], setting=C.SET42 if setting == "42" else C.SET83)
        return rec
    if nr.empty():
        rec.update(verdict="DEAD(C, no admissible pose of %s in the container)" % nr.name, leaf="container", t_total=rec["t_pre"])
        return rec
    roles = C.roles_copy(proles) + [nr]
    rec["seeded_kept"] = C.kept_of(roles)
    rr, r2 = C.make_child(roles, setting)
    rec.update({k: v for k, v in r2.items() if k != "cert"})
    if rr is not None:
        rec["roles"] = C.roles_json(rr)
        walls = ("top", "right", "bottom") if step != "S2" else ("top", "right")
        rec["rows"], rec["row_kill"] = C.rows_of(rr, walls)
        if rec["row_kill"]:
            rec["verdict"], rec["leaf"] = "DEAD(C, chord row A144 LINE-1 on the grown K')", "row"
    rec["t_total"] = round(time.time() - t0, 2)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--exps", default="c,f,b")
    ap.add_argument("--levels", default="1,2")
    ap.add_argument("--max_jobs", type=int, default=0)
    a = ap.parse_args()
    C.set_process()
    sk, sn = RS.shard_of(a.shard)
    S = C.jload(SAMPLE)
    levels = {int(x) for x in a.levels.split(",")}
    jobs = [j for j in jobs_of(S, set(a.exps.split(","))) if j[0] in levels]
    recs = load_all(sn)
    caps = C.wallcapped()
    out = side_path(sk, sn)
    todo = [j for i, j in enumerate(jobs) if i % sn == sk and j[1] not in recs]
    if a.max_jobs:
        todo = todo[:a.max_jobs]
    print("run184 shard %d/%d: %d jobs (%d of %d to do; %d recorded) -> %s" % (
        sk, sn, len(jobs), len(todo), len([j for i, j in enumerate(jobs) if i % sn == sk]), len(recs), out), flush=True)
    t00 = time.time()
    pending, waited, cnt = todo, 0, {}
    while pending:
        nxt, progress = [], False
        for job in pending:
            if os.path.exists(PAUSE):
                print("PAUSE sentinel; stop", flush=True)
                return 2
            key, pkey = job[1], job[4]
            if key in caps:
                rec = dict(key=key, exp=job[2], step=job[3], parent=pkey, chain=job[5], s_node=job[6], b_idx=job[7],
                           verdict="SKIPPED(cap: wall-capped at 1500 s)", leaf="cap", t_total=1500.0)
            elif pkey not in recs:
                nxt.append(job)
                continue
            else:
                with C.NodeWall(key):
                    rec = run_job(S, job, recs)
            recs[key] = rec
            C.append_jsonl(out, rec)
            progress = True
            k = rec["verdict"].split("(")[0] + ("/" + str(rec.get("leaf")) if rec.get("leaf") else "")
            cnt[k] = cnt.get(k, 0) + 1
            print("  %-34s %-40s kept %s  t %.0fs (clip42 %s clip83 %s)" % (
                key, rec["verdict"][:40], {k2: round(v, 3) for k2, v in (rec.get("kept") or {}).items()},
                rec.get("t_total", 0), rec.get("t_clip42"), rec.get("t_clip83")), flush=True)
        if not nxt:
            break
        if not progress:
            waited += 1
            if waited > 240:
                print("giving up on %d jobs waiting for parents" % len(nxt), flush=True)
                break
            time.sleep(60)
        else:
            waited = 0
        for q, r in load_all(sn).items():
            recs.setdefault(q, r)
        pending = nxt
    print("run184 shard %d/%d done: %s, %.0fs" % (sk, sn, cnt, time.time() - t00), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
