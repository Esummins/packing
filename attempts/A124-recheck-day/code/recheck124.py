"""A124 T1 -- sharded, wall-capped supervisor loop around A96's recheck96 node solve.

WHY A NEW DRIVER (A96's recheck96.py is read-only for this attempt):
  * recheck96.py has no --shard, so two copies would re-solve the SAME nodes: the done-set is
    read once at startup and both processes then walk the identical queue in the identical order.
  * it has no hard per-node wall.  `--cap` is the LP's internal time_limit; the night's run saw
    walls of 2263 s against a 900 s cap, and A57's k5_16_interior_Y0381 shows the post-time-limit
    path can spin forever.  A wall has to be enforced by killing the PROCESS, so it is a watchdog
    thread that calls os._exit, plus a supervisor that restarts the worker.
  * it honours A57's PAUSE sentinel, which must stay in place today (nothing else of A57 may
    start).  This driver watches its OWN sentinel: attempts/A124-recheck-day/PAUSE.

Everything mathematical is unchanged: the queue is recheck96.alive_rows(), the bin is
trim57.trim_box's widest survivor when --trimmed, and the solve is the identical solve_node call
with the identical parameters.  Completed records are appended to A96's results/recheck96.jsonl
in its own schema (the campaign ledger stays authoritative) and to this attempt's ledger with the
extra bookkeeping fields.  WALL-CAP rows go ONLY to the A124 ledger: a cap is not a verdict, so
the node must stay re-checkable by a later full pass.

    python code/recheck124.py --shard 0/2 --cap 900 --node-wall 1500 --cpu-hours 10
"""
import argparse, ctypes, json, math, os, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A96 = os.path.join(ATT, "A96-a57-parametric")
A57 = os.path.join(ATT, "A57-shadow-trees")
A53 = os.path.join(ATT, "A53-simple-strata")
sys.path.insert(0, os.path.join(A96, "code"))
sys.path.insert(0, os.path.join(A57, "code"))

import recheck96                                  # queue + constants, unmodified
from caselp import Box, Hyp, solve_node
from warm57 import merged_warm
import trim57

A96_RES = os.path.join(A96, "results", "recheck96.jsonl")
A124_RES = os.path.join(BASE, "results", "recheck124.jsonl")
CLAIMS = os.path.join(BASE, "results", "claims")
SENTINEL = os.path.join(BASE, "PAUSE")
EXIT_WALL = 3                                     # supervisor restarts on this code


# ------------------------------------------------------------------ box plumbing
class _MEMSTATUS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def free_phys_mb():
    m = _MEMSTATUS()
    m.dwLength = ctypes.sizeof(_MEMSTATUS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / (1024.0 * 1024.0)


def below_normal():
    """BELOW_NORMAL_PRIORITY_CLASS on self; set here so it survives supervisor restarts."""
    try:
        k32 = ctypes.windll.kernel32
        k32.GetCurrentProcess.restype = ctypes.c_void_p      # pseudo-handle -1 must not truncate
        k32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        k32.GetPriorityClass.argtypes = [ctypes.c_void_p]
        h = k32.GetCurrentProcess()
        k32.SetPriorityClass(h, 0x00004000)
        return k32.GetPriorityClass(h) == 0x00004000          # verified, not assumed
    except Exception:
        return False


def append(path, rec):
    with open(path, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def ledger():
    """(done keys from BOTH ledgers, cpu seconds already spent by this shard)."""
    done = set()
    for p in (A96_RES, A124_RES):
        if not os.path.exists(p):
            continue
        for ln in open(p):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("id"):
                done.add((r.get("cls"), r["id"]))
    return done


def claim(node, ttl):
    """Take a node, or return False if the other shard is already on it.

    Needed because a watchdog restart re-derives the shard split from the CURRENT remaining
    queue: indices shift, so without a claim the restarted worker can pick the node the sibling
    is mid-solve on (a node is not in either ledger until it finishes).  Duplicate work, not
    unsoundness -- but a duplicate is a wasted 900 s out of a 20 CPU-h budget."""
    os.makedirs(CLAIMS, exist_ok=True)
    p = os.path.join(CLAIMS, node.replace("/", "_") + ".claim")
    if os.path.exists(p):
        try:
            if time.time() - os.path.getmtime(p) < ttl:
                return False
        except OSError:
            return False
    with open(p, "w") as fh:
        fh.write(f"{os.getpid()} {time.time():.0f}\n")
    return True


def shard_cpu_s(shard):
    tot = 0.0
    if os.path.exists(A124_RES):
        for ln in open(A124_RES):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("shard") == shard:
                tot += float(r.get("wall_s") or 0.0)
    return tot


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/2")
    ap.add_argument("--cap", type=float, default=900.0)        # LP time_limit, as the night's run
    ap.add_argument("--node-wall", type=float, default=1500.0)  # hard process wall per node
    ap.add_argument("--cpu-hours", type=float, default=10.0)    # this shard's slice of the cap
    ap.add_argument("--deadline", default="")                   # HH:MM local, stop before it
    ap.add_argument("--min-free-mb", type=float, default=3072.0)
    ap.add_argument("--trimmed", action="store_true")
    a = ap.parse_args()
    si, sn = (int(x) for x in a.shard.split("/"))

    bn = below_normal()
    print(f"[{time.strftime('%H:%M:%S')}] shard {a.shard} pid {os.getpid()} "
          f"belownormal={bn} cap={a.cap:.0f} wall={a.node_wall:.0f}", flush=True)

    deadline = None
    if a.deadline:
        hh, mm = (int(x) for x in a.deadline.split(":"))
        lt = time.localtime()
        deadline = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, hh, mm, 0, 0, 0, -1))

    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    hh_pin = recheck96.DELTA / math.sqrt(2.0)
    done = ledger()
    Q = [r for r in recheck96.alive_rows() if (r["_cls"], r["id"]) not in done]
    mine = [r for i, r in enumerate(Q) if i % sn == si]
    spent = shard_cpu_s(a.shard)
    print(f"[{time.strftime('%H:%M:%S')}] {len(Q)} remaining, {len(mine)} on this shard; "
          f"{spent/3600.0:.2f} CPU-h already spent by it", flush=True)

    warm = {}
    for r in mine:
        if os.path.exists(SENTINEL):
            print("A124 sentinel set; stopping cleanly", flush=True)
            break
        if spent >= a.cpu_hours * 3600.0:
            print(f"shard CPU cap reached ({spent/3600.0:.2f} h)", flush=True)
            break
        if deadline and time.time() > deadline:
            print("deadline reached", flush=True)
            break
        fm = free_phys_mb()
        if fm < a.min_free_mb:
            print(f"free physical {fm:.0f} MB < {a.min_free_mb:.0f} MB gate; stopping", flush=True)
            break

        if not claim(r["id"], a.node_wall + 300.0):
            print(f"{r['id']:34s} claimed by the sibling shard; skipping", flush=True)
            continue

        nm = r["_name"]
        sl = [tuple(p) for p in slots_all[nm]]
        pins = [Box(x - hh_pin, x + hh_pin, y - hh_pin, y + hh_pin, 0.0, 0.0) for (x, y) in sl]
        b = Box.from_json(r["box"])
        note = None
        if a.trimmed:
            subs, excl = trim57.trim_box(b, sl)
            if not subs:
                rec = dict(id=r["id"], cls=r["_cls"], verdict="TRIM-KILL",
                           excluded=len(excl), wall_s=0.0)
                append(A96_RES, rec)
                append(A124_RES, dict(rec, shard=a.shard, level=1 + r["id"].count("_D")))
                print(f"{r['id']:34s} TRIM-KILL (empty surviving bin)", flush=True)
                continue
            b = max(subs, key=lambda s: s.th1 - s.th0)
            note = f"trimmed bin [{b.th0:.4f},{b.th1:.4f}]"
        if nm not in warm:
            warm[nm] = merged_warm(nm, max_rows=30000)[0]
        W = warm[nm]
        bud = r.get("budget") or 5

        # ---- hard wall.  The watchdog records the node as WALL-CAP in the A124 ledger only and
        # kills the process; the supervisor restarts us and the node is skipped as already seen.
        t0 = time.time()
        stop = threading.Event()

        def guard(node=r["id"], cls=r["_cls"], lvl=1 + r["id"].count("_D")):
            if stop.wait(a.node_wall):
                return
            try:
                append(A124_RES, dict(id=node, cls=cls, shard=a.shard, level=lvl,
                                      verdict="WALL-CAP", cap=a.cap, node_wall=a.node_wall,
                                      trimmed=bool(a.trimmed), note=note,
                                      wall_s=round(time.time() - t0, 1),
                                      comment="hard wall hit; NOT a verdict, node stays ALIVE"))
                sys.stderr.write(f"WALL-CAP {node} after {a.node_wall:.0f}s; exiting {EXIT_WALL}\n")
                sys.stderr.flush()
            finally:
                os._exit(EXIT_WALL)

        th = threading.Thread(target=guard, daemon=True)
        th.start()

        rec = dict(id=r["id"], cls=r["_cls"], budget=bud, cap=a.cap, trimmed=bool(a.trimmed),
                   note=note, tau_before=r.get("tau"), eta_before=r.get("eta"))
        try:
            s = solve_node(recheck96.S_RAT, Hyp(pins + [b], []), bud, sym_kind="C1",
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
        stop.set()
        spent += rec["wall_s"]
        append(A96_RES, rec)
        append(A124_RES, dict(rec, shard=a.shard, level=1 + r["id"].count("_D")))
        print(f"[{time.strftime('%H:%M:%S')}] {r['id']:34s} tau {rec.get('tau_before')} -> "
              f"{rec.get('tau_after')} conv={rec.get('converged')} kills={rec.get('kills')} "
              f"{rec['wall_s']}s [{spent/3600.0:.2f} CPU-h]", flush=True)
    print("recheck124 shard done", flush=True)


if __name__ == "__main__":
    main()
