"""A242 -- the k0 cascade from the CROWD ROOT H_B: depth-first, resumable, per-cell commits.

COMPLETENESS.  The cascade is a depth-first enumeration of a binary tree whose root is H_B(band)
and whose edge relation is `root242.split_role` (bisect one role's widest axis).  The two children
of a cell cover it (the two halves share their common face, which is kept in BOTH children -- closed
boxes), so at any moment
        { the cells DEAD so far }  union  { the cells on the stack }  covers H_B(band),
and the band is closed exactly when the stack empties with every cell DEAD.  The only cells dropped
without a verdict are those `root242.pair_order_ok` rejects, which are relabellings of a sibling
(the two meeters of a corner are an unordered pair).

RESUME.  Every decided cell is appended to `results/crowd242.jsonl` (one JSON object per line,
flushed and fsynced) and the live stack to `results/stack242.json` (atomic replace).  A restart
reloads the stack, so a killed worker resumes at the cell it was on; a cell already present in the
jsonl is never re-run (the `seen` set).  `--commit-every` runs `git commit -- <explicit paths>`.

BUDGET.  `--wall` seconds per cell inside L1 (the brief's 2 h cap is the ceiling, not the target);
`--cells` cells per run; `--max-depth` cuts the branch and records it ALIVE at the cut (sound: an
undecided cell is an obligation, never a kill).
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import root242 as R                                                # noqa: E402
import leaves242 as L                                              # noqa: E402

RESULTS = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")


def _paths(band):
    return (os.path.join(RESULTS, "crowd242_%s.jsonl" % band),
            os.path.join(RESULTS, "stack242_%s.json" % band))


def _append(path, rec):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def _save_stack(path, stack):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(stack, fh)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _load(band):
    jl, st = _paths(band)
    seen, rows = set(), []
    if os.path.exists(jl):
        with open(jl, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    r = json.loads(ln)
                except Exception:                                   # noqa: BLE001
                    continue
                seen.add(r["label"])
                rows.append(r)
    stack = None
    if os.path.exists(st):
        try:
            stack = json.load(open(st, encoding="utf-8"))
        except Exception:                                           # noqa: BLE001
            stack = None
    return seen, rows, stack


def be_polite(mask=0xFFFF):
    """BelowNormal + affinity 0xFFFF on THIS process (A241's `be_polite`, same call)."""
    try:
        import ctypes
        h = ctypes.windll.kernel32.GetCurrentProcess()
        ctypes.windll.kernel32.SetPriorityClass(h, 0x00004000)      # BELOW_NORMAL_PRIORITY_CLASS
        ctypes.windll.kernel32.SetProcessAffinityMask(h, mask)
    except Exception as e:                                          # noqa: BLE001
        print("be_polite: %r" % (e,), flush=True)


def _commit(band, n):
    """No-op: the shell wrapper `run242.sh` owns the commits (explicit pathspecs, retried while
    another worker holds the index)."""
    return None


def run(args):
    band = args.band
    jl, st = _paths(band)
    seen, rows, stack = _load(band)
    if stack is None:
        stack = [dict(cell=R.root_cell(band), pockets=None)]
    be_polite()
    print("A242 cascade band=%s  resumed: %d decided, %d on the stack, kernels=%s"
          % (band, len(seen), len(stack), L.install()), flush=True)
    t_run = time.time()
    done = 0
    since_commit = 0
    while stack and done < args.cells:
        top = stack.pop()
        cell, pockets = top["cell"], top.get("pockets")
        if cell["label"] in seen:
            continue
        t0 = time.time()
        r = L.leaf_of(cell, parent_pockets=pockets,
                      budget=dict(total_deadline=args.wall), name=cell["label"][-30:])
        role, wide = R.widest_role(cell)
        rec = dict(label=cell["label"], band=band, depth=cell["depth"], parent=cell["parent"],
                   verdict=r.get("verdict"), leaf=r.get("leaf"), clip=r.get("clip"),
                   step=r.get("step"), seconds=r.get("seconds"), cn_bound=r.get("cn_bound"),
                   n_pockets=len(r.get("pockets") or []), n_alive=len(r.get("alive") or []),
                   alive=[[round(c, 5) for c in p] for p in (r.get("alive") or [])][:8],
                   l2_gate=r.get("l2_gate"), widest_role=role, widest=round(wide, 4),
                   roles={k: [round(c, 5) for c in v] for k, v in cell["roles"].items()},
                   reason=(r.get("reason") or "")[:300], t=round(time.time() - t0, 2))
        _append(jl, rec)
        seen.add(cell["label"])
        done += 1
        since_commit += 1
        if rec["verdict"] not in ("DEAD", "VACUOUS"):
            if cell["depth"] >= args.max_depth:
                rec["cut"] = True
                _append(jl, dict(label=cell["label"] + "#CUT", band=band, depth=cell["depth"],
                                 verdict="ALIVE-CUT", leaf=None,
                                 reason="depth cap %d: the cell is an open obligation" % args.max_depth))
            else:
                kids = R.split_role(cell, role)
                for k in reversed(kids):
                    stack.append(dict(cell=k, pockets=(r.get("alive") or None)))
        _save_stack(st, stack)
        print("%5d  d%-3d %-9s %-16s %6.1fs  pk=%d alive=%d  %s"
              % (done, cell["depth"], rec["verdict"], rec["clip"] or rec["step"] or "",
                 rec["t"], rec["n_pockets"], rec["n_alive"], cell["label"][-58:]), flush=True)
        if since_commit >= args.commit_every:
            _commit(band, len(seen))
            since_commit = 0
    _commit(band, len(seen))
    print("A242 cascade band=%s STOP: %d cells this run, %d total, %d on the stack, %.1f s"
          % (band, done, len(seen), len(stack), time.time() - t_run), flush=True)
    print("STACK %d" % len(stack), flush=True)
    return 0 if stack else 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--band", default="W")
    ap.add_argument("--cells", type=int, default=200)
    ap.add_argument("--wall", type=float, default=300.0)
    ap.add_argument("--max-depth", type=int, default=64)
    ap.add_argument("--commit-every", type=int, default=25)
    return run(ap.parse_args())


if __name__ == "__main__":
    sys.exit(main() or 0)
