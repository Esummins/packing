"""A168 resume (2026-09-09, after the 02:20 reboot) -- the pieces the restart needed:

  SIDEBAND leaves from A169 (docs/proofs/sideband.md), consumed per its section 6:
    R3  lonely_box(box, corner): a SOUND box test for "every meeter pose in the box is LONELY"
        (Theorem B, clauses (W), (S), (NE) all fail, and for c > 1 clause (P) fails).  A lonely pose
        admits no second meeter of the widened corner box, so a K0-BLOCKED family has no square
        there: the box is DEAD for ANY role (the first meeter, the second meeter, a coexistence
        candidate).  Clause tests: the three one-parameter inequalities on the centre rectangle
        with g(n) >= 1/2 (sound), decided on a 2001-point grid with a Lipschitz margin [S]; (P) by
        A131's exact clip against the pressed square shrunk by 1e-6 (every pose's interior meets
        int [0,1]^2 <=> the pressed square is NOT a second meeter) [T per sub-bin].
    R1  cells_dead(first, second, corner): Lemma A2 -- the two meeters of one corner have centres
        in DIFFERENT cells of the 2x2 grid at c = 1 + w_rat (both rects inside one cell => DEAD),
        and Lemma A1 -- l_inf centre distance >= 1/sqrt2 (max over the two rects < 1/sqrt2 => DEAD).
        Both replace the [C]-pending SIDEBAND row of notes/cascade.md sec 0.
  Corner-local frames (BL-local coordinates; a reflection maps tilt th -> 90 - th).
  Shard / merge bookkeeping for the multi-process S3 and coexistence runs, the per-node 1,500 s
  wall that kills the process TREE (taskkill /T /F), and the memory gate before any LP.
"""
import ctypes
import json
import math
import os
import subprocess
import sys
import threading
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import roles168 as R                                             # noqa: E402
import numpy as np                                               # noqa: E402
from caselp import Box                                           # noqa: E402

C_RAT = 1 + K.W0_RAT                      # the widened box side, rational (>= the float pad)
C_F = float(C_RAT)
INV_SQ2 = 1.0 / math.sqrt(2.0)
GRID = np.linspace(0.0, 0.5 * math.pi, 2001)
COSG, SING = np.cos(GRID), np.sin(GRID)
HSTEP = GRID[1] - GRID[0]


# ===================================================================== corner-local frames
def to_local(box, corner):
    """the box in BL-local coordinates of `corner` (container coords -> distance from the two
    walls of that corner); a single reflection maps tilt th -> 90 - th, a double one keeps it."""
    s = K.S0
    x0, x1, y0, y1, t0, t1 = box.x0, box.x1, box.y0, box.y1, box.th0, box.th1
    rx = corner in ("BR", "TR")
    ry = corner in ("TL", "TR")
    if rx:
        x0, x1 = s - x1, s - x0
    if ry:
        y0, y1 = s - y1, s - y0
    if rx != ry:
        t0, t1 = 90.0 - t1, 90.0 - t0
    return Box(x0, x1, y0, y1, t0, t1)


def local_rect(pieces, corner):
    bs = [to_local(b, corner) for b in pieces]
    return (min(b.x0 for b in bs), max(b.x1 for b in bs), min(b.y0 for b in bs), max(b.y1 for b in bs))


# ===================================================================== R3: lonely boxes
def _clause_fails_everywhere(f, L):
    """f on GRID (numpy), Lipschitz constant L: f >= 0 on the whole interval (sound margin)."""
    return bool(np.all(f >= 0.5 * L * HSTEP + 1e-9))


def _gmin(angle_grid, th0, th1, nth=64):
    """lower bound of g(n) = (|cos(alpha - th)| + |sin(alpha - th)|)/2 over th in [th0, th1] (deg),
    per grid angle alpha (rad): a th-grid minimum minus the Lipschitz margin (|dg/dth| <= 1/sqrt2),
    never below 1/2."""
    ths = np.radians(np.linspace(th0, th1, nth)) if th1 > th0 else np.radians(np.array([th0]))
    ph = angle_grid[:, None] - ths[None, :]
    g = 0.5 * (np.abs(np.cos(ph)) + np.abs(np.sin(ph))).min(axis=1)
    hth = (ths[1] - ths[0]) if len(ths) > 1 else 0.0
    return np.maximum(0.5, g - 0.5 * INV_SQ2 * hth)


def lonely_box(box, corner, c=C_F, nsub=4):
    """SOUND: every pose in `box` (a `corner` meeter box in container coordinates) is lonely at the
    widened box of side c (Theorem B with clause (P)).  Returns (True, detail) or (False, detail).
    Each clause is h(n) >= rhs(n) for every n of its family, with h(n) >= n.z_min + g_min(n)."""
    lb = to_local(box, corner)
    x0, x1, y0, y1 = lb.x0, lb.x1, lb.y0, lb.y1
    det = {}
    gW = _gmin(GRID + 0.5 * math.pi, lb.th0, lb.th1)          # n_W(z) = (-sin z, cos z)
    gS = _gmin(-GRID, lb.th0, lb.th1)                         # n_S(z) = (cos z, -sin z)
    gN = _gmin(GRID, lb.th0, lb.th1)                          # n_NE(a) = (cos a, sin a)
    # (W) fails everywhere:  -x sin z + y cos z + g >= c cos z - sin^2 z  for all z, all (x,y) in B
    fW = -x1 * SING + y0 * COSG + gW - c * COSG + SING ** 2
    LW = x1 + y0 + c + 1.0 + INV_SQ2
    det["W"] = _clause_fails_everywhere(fW, LW)
    fS = -y1 * SING + x0 * COSG + gS - c * COSG + SING ** 2
    LS = y1 + x0 + c + 1.0 + INV_SQ2
    det["S"] = _clause_fails_everywhere(fS, LS)
    fN = x0 * COSG + y0 * SING + gN - c * (COSG + SING)
    LN = x0 + y0 + 2 * c + INV_SQ2
    det["NE"] = _clause_fails_everywhere(fN, LN)
    if not (det["W"] and det["S"] and det["NE"]):
        det["P"] = None
        return False, det
    # (P) fails: the pressed square [0,1]^2 is not a second meeter <=> every pose of B has interior
    # meeting int [0,1]^2: A131's exact clip against the axis core (1/2, 1/2, 1/2 - 1e-6) per sub-bin
    core = (Fr(1, 2), Fr(1, 2), Fr(1, 2) - Fr(1, 10 ** 6))
    th0, th1 = lb.th0, lb.th1
    edges = [th0 + (th1 - th0) * k / nsub for k in range(nsub + 1)] if th1 > th0 else [th0, th1]
    for k in range(len(edges) - 1):
        pb = Box(lb.x0, lb.x1, lb.y0, lb.y1, edges[k], edges[k + 1])
        if R.clip_piece(pb, [core]) is not None:
            det["P"] = False
            return False, det
    det["P"] = True
    return True, det


def lonely_role(role, corner):
    """every piece of the role is a lonely box."""
    dets = []
    for b in role.pieces:
        ok, d = lonely_box(b, corner)
        dets.append(d)
        if not ok:
            return False, dets
    return True, dets


# ===================================================================== R1: cells and l_inf
def cells_dead(first_pieces, second_pieces, corner, c=C_F):
    """Lemma A2 / A1 on the two meeters' centre rectangles (container coords -> local).  Returns
    (reason or None, detail)."""
    a = local_rect(first_pieces, corner)
    b = local_rect(second_pieces, corner)
    eps = 1e-9

    def cls(r):
        xs = "lo" if r[1] < c - eps else ("hi" if r[0] >= c + eps else "straddle")
        ys = "lo" if r[3] < c - eps else ("hi" if r[2] >= c + eps else "straddle")
        return xs, ys
    ca, cb = cls(a), cls(b)
    det = dict(first=[round(v, 6) for v in a], second=[round(v, 6) for v in b], cell_first=ca,
               cell_second=cb, c=c)
    if "straddle" not in ca and ca == cb:
        return "R1 cells: both meeters' centres in cell %s/%s of the grid at c = 1 + w (Lemma A2)" % ca, det
    dx = max(abs(a[1] - b[0]), abs(b[1] - a[0]))
    dy = max(abs(a[3] - b[2]), abs(b[3] - a[2]))
    det["linf_max"] = max(dx, dy)
    if max(dx, dy) < INV_SQ2 - eps:
        return "R1 l_inf: every centre pair at l_inf distance < 1/sqrt2 (Lemma A1)", det
    return None, det


FIRST_OF = {"S2": "D", "S4": "B", "S6": "T1", "S8": "L1"}


# ===================================================================== shard / merge / wall / memory
def shard_of(spec_text):
    if not spec_text or spec_text in ("", "0/1"):
        return 0, 1
    k, n = spec_text.split("/")
    return int(k), int(n)


def shard_path(cell, step, k, n):
    return os.path.join(K.RES, "shards", "tree_%s__%s_s%dof%d.json" % (cell, step, k, n))


def save_shard(T, touched, cell, step, k, n):
    """persist only the nodes this shard touched (parents + their children)."""
    nodes = {}
    for p in touched:
        nodes[p] = T["nodes"][p]
        for cp in T["nodes"][p].get("children", []):
            nodes[cp] = T["nodes"][cp]
    K.jdump(dict(cell=cell, step=step, shard=[k, n], parents=sorted(touched), nodes=nodes,
                 saved=time.strftime("%Y-%m-%d %H:%M:%S")), shard_path(cell, step, k, n))


def merge_shards(T, cell, step):
    """fold every shard file of (cell, step) into T; returns the number of nodes merged."""
    d = os.path.join(K.RES, "shards")
    n_nodes = 0
    if not os.path.isdir(d):
        return 0
    for fn in sorted(os.listdir(d)):
        if not fn.startswith("tree_%s__%s_s" % (cell, step)):
            continue
        S = K.jload(os.path.join(d, fn))
        for p, node in S["nodes"].items():
            T["nodes"][p] = node
            n_nodes += 1
    return n_nodes


WALLCAP_S = 1500.0


def wallcap_path(cell):
    return os.path.join(K.RES, "wallcap_%s.json" % cell)


def wallcapped(cell):
    p = wallcap_path(cell)
    return set(K.jload(p)) if os.path.exists(p) else set()


class NodeWall:
    """the per-node wall: at WALLCAP_S the node is recorded as wall-capped (kept in its prior
    state: CAP is never a verdict) and the whole process TREE is killed (taskkill /T /F)."""

    def __init__(self, cell, path, seconds=WALLCAP_S):
        self.cell, self.path, self.seconds = cell, path, seconds
        self.t = threading.Timer(seconds, self.fire)
        self.t.daemon = True

    def __enter__(self):
        self.t.start()
        return self

    def __exit__(self, *a):
        self.t.cancel()

    def fire(self):
        try:
            caps = wallcapped(self.cell)
            caps.add(self.path)
            K.jdump(sorted(caps), wallcap_path(self.cell))
            print("WALL-CAP %s after %.0fs: killing the process tree" % (self.path, self.seconds), flush=True)
        finally:
            subprocess.run(["taskkill", "/PID", str(os.getpid()), "/T", "/F"],
                           capture_output=True)


class _MEMSTAT(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def memstat():
    m = _MEMSTAT()
    m.dwLength = ctypes.sizeof(_MEMSTAT)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return dict(free_phys_mb=m.ullAvailPhys / 2 ** 20, commit_headroom_mb=m.ullAvailPageFile / 2 ** 20)


def n_lab_python():
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "@(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                              "Where-Object { $_.CommandLine -like '*code\\packing\\attempts*' }).Count"],
                             capture_output=True, text=True, timeout=60).stdout.strip()
        return int(out or 0)
    except Exception:                                            # noqa: BLE001
        return -1


def memory_gate(free_mb=3072, headroom_mb=6144, max_wait=1800, tag=""):
    """block until > 3 GB free physical and > 6144 MB commit headroom (the LP gate)."""
    t0 = time.time()
    while True:
        m = memstat()
        if m["free_phys_mb"] > free_mb and m["commit_headroom_mb"] > headroom_mb:
            return m
        if time.time() - t0 > max_wait:
            print("memory gate %s: waited %.0fs, still %s -- skipping" % (tag, time.time() - t0, m), flush=True)
            return None
        time.sleep(20)


def box_json(b):
    return dict(x0=b.x0, x1=b.x1, y0=b.y0, y1=b.y1, th0=b.th0, th1=b.th1)


if __name__ == "__main__":
    # smoke: a pressed TR square (touching both walls) is lonely at the unit box only for th >= 12.8deg
    s = K.S0
    for th in (0.0, 5.0, 20.0, 45.0):
        b = Box(s - 0.72, s - 0.70, s - 0.72, s - 0.70, th, th + 1.0)
        print(th, lonely_box(b, "TR"))
    print(memstat(), n_lab_python())
