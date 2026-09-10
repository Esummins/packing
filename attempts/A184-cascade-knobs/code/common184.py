"""A184 -- shared plumbing for the three knob experiments (read-only imports of A168's code, the
A171 library, A164's leaf).  Nothing here writes outside attempts/A184-cascade-knobs.

  * `make_child(roles, new, setting)`: the cascade's own child normalise exactly as A183 builds a
    NEW node (roles168.make_node's path: polyclip175.make_node at nsub 4 / refine 2, then on a
    survivor renorm183.make_node_83 from that fixed point when setting == "83"), the parent seeding
    by construction (the inherited roles ARE the parent's fixed-point pieces), TIMED: the library
    clip (poly_normalise) separately from the rebuild / invariant / OVL tail, and the 8/3 pass
    separately from the 4/2 pass.
  * the per-node wall (own cap file), the BelowNormal / affinity 0xFFFF setting, the lab-python
    count under the box ceiling, jsonl records.
"""
import ctypes
import json
import os
import subprocess
import sys
import threading
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
A168 = os.path.join(ATT, "A168-cascade-fable")
for _p in (os.path.join(A168, "code"), os.path.join(ATT, "A164-wastage-area", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import cas168 as K                                               # noqa: E402  (A168, read-only)
import roles168 as R                                             # noqa: E402
import cascade168 as CS                                          # noqa: E402
import resume168 as RS                                           # noqa: E402
import polyclip175 as PX                                         # noqa: E402
import renorm181 as R8                                           # noqa: E402
import renorm183 as R83                                          # noqa: E402
import multibox as MB                                            # noqa: E402  (A171, read-only)
from caselp import Box                                           # noqa: E402

assert "uid" in getattr(MB.Obstacle, "__slots__", ()), "multibox.py predates 13f23204"
CELL = "l1_104"
B0 = float(K.S_RAT * K.S_RAT - 11)                               # the wastage budget s0^2 - 11
WALLCAP_S = 1500
SET42, SET83 = "nsub 4 / refine 2", R83.SET83
CORNER_OF = PX.CORNER_OF
FIRST_OF = {"S": "D", "Bp": "B"}                                 # second meeters and their first


# ------------------------------------------------------------------ process discipline
def set_process():
    """BelowNormal priority, affinity 0xFFFF (logical CPUs 0-15) for THIS process."""
    try:
        h = ctypes.windll.kernel32.GetCurrentProcess()
        ctypes.windll.kernel32.SetPriorityClass(h, 0x4000)
        ctypes.windll.kernel32.SetProcessAffinityMask(h, 0xFFFF)
    except Exception as e:                                        # noqa: BLE001
        print("set_process failed:", e, flush=True)


def lab_python_count():
    """every python.exe on the box except the Claude-extension venvs (relative command lines count)."""
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "@(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                              "Where-Object { -not ($_.CommandLine -like '*Claude Extensions*') }).Count"],
                             capture_output=True, text=True, timeout=90).stdout.strip()
        return int(out or 0)
    except Exception:                                            # noqa: BLE001
        return -1


def wait_slot(need=1, ceiling=12, max_wait=10800):
    t0 = time.time()
    while time.time() - t0 < max_wait:
        n = lab_python_count()
        if 0 <= n and n + need <= ceiling:
            return n
        print("box ceiling: %d lab pythons, need %d more; waiting" % (n, need), flush=True)
        time.sleep(60)
    return None


def wallcap_path():
    return os.path.join(RES, "wallcap184.json")


def wallcapped():
    p = wallcap_path()
    return set(json.load(open(p, encoding="utf-8"))) if os.path.exists(p) else set()


class NodeWall:
    """the per-node wall: the node is listed in results/wallcap184.json (CAP is never a verdict)
    and the whole process TREE is killed (taskkill /T /F); the launcher relaunches (resumable)."""

    def __init__(self, key, seconds=WALLCAP_S):
        self.key, self.seconds = key, seconds
        self.t = threading.Timer(seconds, self.fire)
        self.t.daemon = True

    def __enter__(self):
        self.t.start()
        return self

    def __exit__(self, *a):
        self.t.cancel()

    def fire(self):
        try:
            caps = wallcapped()
            caps.add(self.key)
            json.dump(sorted(caps), open(wallcap_path(), "w", encoding="utf-8"))
            print("WALL-CAP %s after %.0fs: killing the process tree" % (self.key, self.seconds), flush=True)
        finally:
            subprocess.run(["taskkill", "/PID", str(os.getpid()), "/T", "/F"], capture_output=True)


# ------------------------------------------------------------------ records
def load_jsonl(path, key="key"):
    recs = {}
    if os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            try:
                d = json.loads(ln)
            except Exception:                                    # noqa: BLE001
                continue
            recs[d[key]] = d
    return recs


def append_jsonl(path, rec):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")


def jload(p):
    return json.load(open(p, encoding="utf-8"))


def jdump(obj, p):
    json.dump(obj, open(p, "w", encoding="utf-8"), indent=1, default=str)


# ------------------------------------------------------------------ the timed child normalise
_CLIP_T = [0.0]
_orig_poly_normalise = PX.poly_normalise


def _timed_poly_normalise(*a, **kw):
    t0 = time.time()
    try:
        return _orig_poly_normalise(*a, **kw)
    finally:
        _CLIP_T[0] += time.time() - t0


PX.poly_normalise = _timed_poly_normalise                        # this process only


def roles_copy(roles):
    return [R.Role(r.name, list(r.pieces), src=r.src) for r in roles]


def vols(roles):
    return {r.name: float(sum(R.vol(b) for b in r.pieces)) for r in roles}


def kept_of(roles):
    return {r.name: r.kept_frac() for r in roles}


def pre_tests(new_box, corner, first):
    """the A169 leaves before any normalisation: R3 (lonely => dead for any role) and, for a second
    meeter, R1 against the first meeter's pieces (same cell / l_inf < 1/sqrt2 => dead)."""
    lon, ldet = RS.lonely_box(new_box, corner)
    if lon:
        return "DEAD(C, R3 lonely: every meeter pose in the box admits no second %s meeter)" % corner, dict(lonely=ldet)
    if first is not None:
        why, cdet = RS.cells_dead(first.pieces, [new_box], corner)
        if why:
            return "DEAD(C, R1 %s)" % why, dict(cells=cdet)
    return None, {}


def make_child(roles, setting, lonely=True):
    """`roles` = the parent's fixed-point roles + the new role (already a Role).  Returns
    (roles or None, record) with the timings t_clip42 / t_rest42 / t_clip83 / t_rest83 / t_total."""
    rec = dict(setting=SET42 if setting == "42" else SET83)
    t0 = time.time()
    _CLIP_T[0] = 0.0
    rr, rep = PX.make_node(roles, refine=2, lonely=lonely)
    t1 = time.time()
    rec.update(t_clip42=round(_CLIP_T[0], 2), t_rest42=round(t1 - t0 - _CLIP_T[0], 2), passes_42=rep.get("passes"),
               kept_42=rep.get("kept"), n_pieces_42=rep.get("n_pieces"))
    if rr is None:
        rec.update(verdict="DEAD(C, %s)" % rep["dead"], leaf=rep.get("leaf"), died_at="4/2", cert=rep.get("cert"))
        rec["t_total"] = round(time.time() - t0, 2)
        return None, rec
    rec.update(vol_42=vols(rr), k_area_42=rep.get("k_area"))
    if setting == "83":
        _CLIP_T[0] = 0.0
        t2 = time.time()
        rr, rep = R83.make_node_83(rr, lonely=lonely)
        t3 = time.time()
        rec.update(t_clip83=round(_CLIP_T[0], 2), t_rest83=round(t3 - t2 - _CLIP_T[0], 2), passes_83=rep.get("passes"))
        if rr is None:
            rec.update(verdict="DEAD(C, %s)" % rep["dead"], leaf=rep.get("leaf"), died_at="8/3", cert=rep.get("cert"))
            rec["t_total"] = round(time.time() - t0, 2)
            return None, rec
    rec.update(kept=rep.get("kept"), n_pieces=rep.get("n_pieces"), k_area=rep.get("k_area"), vol1=vols(rr),
               invariant_ok=bool((rep.get("invariant") or {}).get("ok")), verdict="ALIVE(geometry)", leaf=None)
    rec["t_total"] = round(time.time() - t0, 2)
    return rr, rec


def roles_json(roles):
    return R.roles_json(roles)


def roles_from_json(d):
    return [R.Role.from_json(v) for v in d.values()]


def rows_of(roles, walls):
    rows = {w: R.best_row(roles, CS.lines_of(w)) for w in walls}
    kill = bool(any(Fr(r["rhs"]) < 0 for r in rows.values()))
    return {w: dict(rhs_f=r["rhs_f"], beta=r["beta"], off_f=r["off_f"]) for w, r in rows.items()}, kill
