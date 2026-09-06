"""Re-check the ALIVE population at a 900 s LP cap.  Resumable; NOT launched.

A109 found 28 of 46 ALIVE nodes were merely UNCONVERGED at the 240 s cap, i.e. the cap decided
the verdict rather than the mathematics.  This re-solves every ALIVE node at 900 s and records
whether it converges and whether tau drops below budget (a kill the campaign currently does not
have).

Resumable on (cls, id) -- never the bare id, per A100's collision bug -- and it honours the pause
sentinel BETWEEN nodes, so pausing preserves the in-flight node's result instead of discarding it.

    python code/recheck96.py --cap 900 [--limit N] [--trimmed]

--trimmed re-solves on the T5''-trimmed bin as well, which is the combination worth pricing: a
longer cap on a smaller hypothesis.
"""
import argparse, glob, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A57 = os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees"))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, os.path.join(A57, "code"))
from caselp import Box, Hyp, solve_node
from warm57 import merged_warm
import trim57
from pausegate import paused, reason

S_RAT = 969271.0 / 250000.0
DELTA = 1e-2


def alive_rows():
    out, seen = [], set()
    for pat in ("tree_k5_1*_interior_G1_s*.jsonl", "tree_k5_1*_interior_G1_D2*.jsonl"):
        for f in sorted(glob.glob(os.path.join(A57, "results", pat))):
            if "_D2_s0.jsonl" in f or "_D2_D2_s0.jsonl" in f:
                continue
            for ln in open(f):
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                if r["id"] in seen or not r.get("box"):
                    continue
                if not str(r.get("cert") or "").startswith("ALIVE"):
                    continue
                seen.add(r["id"])
                r["_cls"] = ("k5_11" if r["id"].startswith("k5_11") else "k5_16") + "_G1"
                r["_name"] = r["_cls"].split("_G1")[0]
                out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=900.0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--trimmed", action="store_true")
    a = ap.parse_args()
    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    hh = DELTA / math.sqrt(2.0)
    res = os.path.join(BASE, "results", "recheck96.jsonl")
    done = set()
    if os.path.exists(res):
        for ln in open(res):
            try:
                r = json.loads(ln)
                done.add((r.get("cls"), r["id"]))
            except Exception:
                pass
    R = [r for r in alive_rows() if (r["_cls"], r["id"]) not in done]
    if a.limit:
        R = R[:a.limit]
    print(f"{len(R)} ALIVE nodes to re-check at {a.cap:.0f} s"
          f"{' on the trimmed bin' if a.trimmed else ''}", flush=True)
    warm = {}
    for r in R:
        if paused():
            print(f"pause sentinel set ({reason()}); stopping cleanly with "
                  f"every finished node recorded", flush=True)
            break
        nm = r["_name"]
        sl = [tuple(p) for p in slots_all[nm]]
        pins = [Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in sl]
        b = Box.from_json(r["box"])
        note = None
        if a.trimmed:
            subs, excl = trim57.trim_box(b, sl)
            if not subs:
                with open(res, "a") as fh:
                    fh.write(json.dumps(dict(id=r["id"], cls=r["_cls"], verdict="TRIM-KILL",
                                             excluded=len(excl), wall_s=0.0)) + "\n")
                print(f"{r['id']:34s} TRIM-KILL (empty surviving bin)", flush=True)
                continue
            b = max(subs, key=lambda s: s.th1 - s.th0)
            note = f"trimmed bin [{b.th0:.4f},{b.th1:.4f}]"
        if nm not in warm:
            warm[nm] = merged_warm(nm, max_rows=30000)[0]
        W = warm[nm]
        bud = r.get("budget") or 5
        t0 = time.time()
        rec = dict(id=r["id"], cls=r["_cls"], budget=bud, cap=a.cap, trimmed=bool(a.trimmed),
                   note=note, tau_before=r.get("tau"), eta_before=r.get("eta"))
        try:
            s = solve_node(S_RAT, Hyp(pins + [b], []), bud, sym_kind="C1",
                           warm=dict(atoms=list(W["atoms"]), rows=W["rows"]),
                           time_limit=a.cap, max_iter=900, out=None, log=lambda *x: None,
                           prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                           max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)
            tau = s.get("tau")
            rec.update(tau_after=tau, converged=s.get("converged"),
                       eta_after=(tau - bud) if tau is not None else None,
                       kills=(tau is not None and tau < bud))
        except Exception as e:
            rec.update(error=repr(e)[:200])
        rec["wall_s"] = round(time.time() - t0, 1)
        with open(res, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"{r['id']:34s} tau {rec.get('tau_before')} -> {rec.get('tau_after')} "
              f"conv={rec.get('converged')} kills={rec.get('kills')} {rec['wall_s']}s", flush=True)
    print("recheck96 done", flush=True)


if __name__ == "__main__":
    main()
