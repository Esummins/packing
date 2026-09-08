"""
A85 `tree85.py` -- A60's residual zone-tree driver, parametrised by a PROTECTED CLASS.

Derived from `tree60.py` (A60, copied verbatim into this attempt's code/).  Node semantics are
inherited unchanged -- A54 S0 (the sole kill arbiter is an exact rational certificate accepted by
verify_case.py), A57 T2 (theta windows uniform in t), T4 (columns-only warm starts), T5
(pinguard before any box is solved or read), T11 (refinement keeps the budget), and the CANARY
(a node realised by a Trump image of the class is NEVER certified).

What is parametrised (pilot_design.md 1.3):
  * the pin set is the class's k_S slots, SLACK at delta_pin = 2e-2 from the start;
  * the budget arithmetic is N = 11 - k_S:  YES child = N - |cond| - 1, NO child = N - |cond|;
  * the witness families are the G_S = 2 Trump images of the class (alive84), so `hugs` names an
    (image, square) pair and `unkillable` means SOME image is alive;
  * the canary is `images_realizing`, not `trump_realizes`.

Two corrections applied on top of pilot_design.md 1.3 (theory lead, this run):
  (a) the pinguard 'parent' tolerance for slack pins is delta_pin + 1e-9 (NOT w = delta/sqrt2):
      the dilated pin centre drifts by up to (lambda - 1) A <= delta and the YES witness must be
      provably distinct from the pin square wherever it can sit;
  (b) containment / gap against an UPRIGHT target square uses the mod-90 identification
      (theta-distance min(|th|, 90 - |th|), and t-distance through t -> (1-t)/(1+t) at the glue).
      A60 never needed this -- all its targets are tilted.

Nothing outside attempts/A85-k0-route is ever written.  A85 edit: the class module is
class85 (k0_00: no pins, N = 11, 8 images); the budget arithmetic N - |cond| - 1 is therefore
11 - |cond| - 1, and PINS = [] so pinguard.classify always returns "ok".
"""
import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # A57 T18: pin BLAS to 1 thread BEFORE numpy loads   # noqa: F401
import pilot59 as P
from pilot59 import rq, tbox_deg                                    # noqa: F401
from caselp import Box, NoFam, Hyp
from pinguard import classify, cores_meet
from substrat import zones
import class85 as K84
import alive84
import vac59

RBASIN = 3.0 / 2000.0           # A63 theta_t_transfer X.3 -- the Lean-concrete basin radius (t-world)
TSC = 0.566                     # dt/dtheta at theta_T
H = 3.7e-3                      # A36 basin radius (theta-radian diagnostic)
HW_TARGET = H / 4.55            # 8.13e-4 -- the G-A59-9 annulus closure
R_C_TUBE = 1.6e-3               # A83 certified landing profile: centre radius
R_T_TUBE = 2.1e-3               # A83 certified landing profile: theta radius (radians)
MIN_FREE_COMMIT_MB = 6144.0     # never launch an LP into a commit dip

RES = os.path.join(BASE, "results")
PROG = os.path.join(BASE, "progress")
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
for d in (RES, PROG, LOGS, CERTS, os.path.join(RES, "nodes")):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------ class context (set by setup)
CLS = None
C = None
PINS = []
PIN_FULL = []       # Lemma PD: (Core(Sigma_p), Core(Sigma_p + d_max)) per pin
SLOTS = []
NFREE = 0
PARENT_TOL = 1e-9
FREE = {}           # flat: "g<k>_sq<i>" -> (cx, cy, theta_rad)   [the image placement]
IMG = {}            # image key -> [names]
IMAGES = []


def setup(cls, delta=K84.DELTA_PIN, t_prime=None):
    global CLS, C, PINS, PIN_FULL, SLOTS, NFREE, PARENT_TOL, FREE, IMG, IMAGES
    CLS = cls
    C = K84.load_class(cls, delta, t_prime)
    PINS = C["_PINS"]
    PIN_FULL = C["_PIN_FULL"]
    SLOTS = C["SLOTS"]
    NFREE = C["N"]
    PARENT_TOL = delta + 1e-9                    # correction (a)
    FREE, IMG, IMAGES = {}, {}, []
    for im in C["images"]:
        IMAGES.append(im)
        IMG[im["key"]] = sorted(im["free"], key=lambda n: int(n.split("sq")[-1]))
        for nm, p in im["free"].items():
            FREE[nm] = tuple(p)
    if not os.path.exists(K84.witnesses_path(cls)):
        K84.write_class(cls, delta)
    alive84.load_witnesses(cls)                  # asserts the exact verification passed
    P.SUBDIR = cls
    P.SLOTS = SLOTS
    P.trump_realizes = lambda hyp, slots=None: bool(images_realizing(hyp))
    for d in (os.path.join(RES, "nodes", cls), os.path.join(CERTS, cls)):
        os.makedirs(d, exist_ok=True)
    return C


def img_of(name):
    return name.split("_")[0]


# ------------------------------------------------------------------ commit-headroom gate
def free_commit_mb():
    """available COMMIT in MB (Win32_OperatingSystem.FreeVirtualMemory equivalent:
    MEMORYSTATUSEX.ullAvailPageFile)."""
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPageFile / (1024.0 * 1024.0)
    except Exception:
        return 1e9


WAITS = []


class CommitStarved(Exception):
    """the commit-headroom gate never opened within the cap.  The node is NOT attempted and NOT
    marked done -- it is deferred, exactly like an allocation failure (A60 `defer`)."""


def wait_for_commit(tag, min_mb=MIN_FREE_COMMIT_MB, nap=60.0, cap=10800.0):
    """block while free commit is below the floor; every wait is logged AND banked.  NEVER
    proceeds into a dip: if the gate has not opened by `cap`, the node is deferred."""
    t0 = time.time()
    n = 0
    f = free_commit_mb()
    while f < min_mb:
        if time.time() - t0 > cap:
            ev = dict(tag=tag, waits=n, seconds=round(time.time() - t0, 1),
                      free_mb=round(f, 1), outcome="DEFERRED(commit gate never opened)",
                      ts=time.strftime("%Y-%m-%d %H:%M:%S"))
            WAITS.append(ev)
            with open(os.path.join(RES, "a85_waits.jsonl"), "a") as fh:
                fh.write(json.dumps(ev) + "\n")
            raise CommitStarved("free commit %.0f MB < %.0f MB for %.0f s" % (f, min_mb, cap))
        n += 1
        logline("  COMMIT-WAIT %s: free commit %.0f MB < %.0f MB; sleeping %ds (wait #%d)"
                % (tag, f, min_mb, int(nap), n))
        time.sleep(nap)
        f = free_commit_mb()
    if n:
        ev = dict(tag=tag, waits=n, seconds=round(time.time() - t0, 1),
                  free_mb_after=round(f, 1), outcome="gate opened",
                  ts=time.strftime("%Y-%m-%d %H:%M:%S"))
        WAITS.append(ev)
        with open(os.path.join(RES, "a85_waits.jsonl"), "a") as fh:
            fh.write(json.dumps(ev) + "\n")
    return n


# ------------------------------------------------------------------ geometry helpers
def core_box(name, hw, ht):
    """core box around image placement `name`: centre half-width hw, t half-width ht."""
    cx, cy, th = FREE[name]
    t = math.tan(th / 2.0)
    th0, th1 = tbox_deg(t - ht, t + ht)
    return Box(rq(cx - hw), rq(cx + hw), rq(cy - hw), rq(cy + hw), th0, th1)


def basin_box(name, hw=H):
    return core_box(name, hw, TSC * hw)


def img_deg(name):
    cx, cy, th = FREE[name]
    return cx, cy, math.degrees(th) % 90.0


def box_radius(b):
    return max(0.5 * (b.x1 - b.x0), 0.5 * (b.y1 - b.y0), 0.5 * math.radians(b.th1 - b.th0))


def box_volume(b):
    return (b.x1 - b.x0) * (b.y1 - b.y0) * math.radians(b.th1 - b.th0)


# --- correction (b): the mod-90 identification -----------------------------------------------
def _d90(a, b):
    d = abs(a - b) % 90.0
    return min(d, 90.0 - d)


def _theta_span_deg(th0, th1, thd):
    """max over th in [th0, th1] of the mod-90 distance to thd.  |.| is piecewise linear with
    interior maxima only at thd +- 45 (mod 90), so the max is over endpoints and those two."""
    cands = [th0, th1]
    for c in (thd + 45.0, thd - 45.0, thd + 135.0, thd - 135.0):
        c = c % 90.0
        if th0 <= c <= th1:
            cands.append(c)
    return max(_d90(c, thd) for c in cands)


def _t_of_deg(d):
    return math.tan(math.radians(d) / 2.0)


def _t_dist(t, tT):
    """t-world distance with the theta ~ theta + 90 glue at the ends of [0, 1].  The reflection
    t -> (1-t)/(1+t) is the t of the mod-90 complement, so it is the right representative when
    BOTH the box and the target sit near opposite ends (an UPRIGHT target, correction (b))."""
    d = abs(t - tT)
    if (t < 0.05 or t > 0.95) and (tT < 0.05 or tT > 0.95):
        d = min(d, abs((1 - t) / (1 + t) - tT))
    return d


def contain_t(b, name):
    """THE DISCHARGE TEST (A63 D.S6): max sup-norm distance from the image placement to a point
    of b in (cx, cy, t) coordinates.  b is a (D)-leaf core for `name` iff this is <= RBASIN."""
    cx, cy, th = FREE[name]
    tT = math.tan(th / 2.0)
    return max(abs(b.x0 - cx), abs(b.x1 - cx), abs(b.y0 - cy), abs(b.y1 - cy),
               _t_dist(_t_of_deg(b.th0), tT), _t_dist(_t_of_deg(b.th1), tT))


def contain_c(b, name):
    """centres only (the tube's r_c coordinate)."""
    cx, cy, th = FREE[name]
    return max(abs(b.x0 - cx), abs(b.x1 - cx), abs(b.y0 - cy), abs(b.y1 - cy))


def contain_theta(b, name):
    """theta-radians only (the tube's r_theta coordinate), mod 90."""
    cx, cy, thd = img_deg(name)
    return math.radians(_theta_span_deg(b.th0, b.th1, thd))


def sup_containment(b, name):
    """A36 h-metric diagnostic: sup-norm in (cx, cy, theta_radians)."""
    return max(contain_c(b, name), contain_theta(b, name))


def sup_gap(b, name):
    """sup-norm distance from the box CENTRE to the image placement (the ladder diagnostic)."""
    cx, cy, thd = img_deg(name)
    return max(abs(0.5 * (b.x0 + b.x1) - cx), abs(0.5 * (b.y0 + b.y1) - cy),
               math.radians(_d90(0.5 * (b.th0 + b.th1), thd)))


def ghost_distance(b):
    """A57 ordering: sup distance from the box centre to the NEAREST image square."""
    return min(sup_gap(b, n) for n in FREE)


def boxes_share_witness(b, c):
    if b.x1 < c.x0 or c.x1 < b.x0 or b.y1 < c.y0 or c.y1 < b.y0:
        return False
    if not (b.th1 < c.th0 or c.th1 < b.th0):
        return True
    return (b.th0 <= 1e-9 and c.th1 >= 90 - 1e-9) or (c.th0 <= 1e-9 and b.th1 >= 90 - 1e-9)


# ------------------------------------------------------------------ canary
def images_realizing(hyp, tol=1e-5):
    """the images of the class whose scaled placements satisfy the node hypotheses.  Such a node
    must NEVER be certified (A60 semantics; a PASS there is exit 9)."""
    out = []
    for im in IMAGES:
        Pl = [(x, y, math.degrees(th) % 90.0) for (x, y, th) in im["placements"]]
        ok = True
        for b in hyp.boxes:
            hit = any(b.x0 - tol <= x <= b.x1 + tol and b.y0 - tol <= y <= b.y1 + tol and
                      b.th0 - 1e-4 <= thd <= b.th1 + 1e-4 for (x, y, thd) in Pl)
            if not hit:
                ok = False
                break
        if ok:
            for f in hyp.nofams:
                if any(f.contains(x, y, thd) for (x, y, thd) in Pl):
                    ok = False
                    break
        if ok:
            out.append(im["key"])
    return out


# ------------------------------------------------------------------ pinguard, extended
def canary_pd():
    """Lemma PD canary (theory lead): an image square that TOUCHES a pin must keep its own
    residue box -- its core must not meet Sigma_p at lambda = 1.  Checked on a tiny box centred
    at every image placement of every image."""
    out = []
    for nm, (cx, cy, th) in sorted(FREE.items()):
        t = math.tan(th / 2.0)
        hw, ht = 1e-4, 1e-4
        th0, th1 = tbox_deg(max(0.0, t - ht), min(1.0, t + ht))
        b = Box(rq(cx - hw), rq(cx + hw), rq(cy - hw), rq(cy + hw), th0, th1)
        st, info = classify(b, PINS, SLOTS, PARENT_TOL, PIN_FULL)
        out.append(dict(name=nm, state=st, info=info, core_a=float(b.core().a)))
    bad = [r for r in out if r["state"] == "contradictory"]
    return out, bad


def classify_at(b, cond_boxes):
    st, info = classify(b, PINS, SLOTS, PARENT_TOL, PIN_FULL)
    if st != "ok":
        return st, info
    cb = b.core()
    for i, Cb in enumerate(cond_boxes):
        cc = Cb.core()
        if cc is None:
            continue
        if cores_meet(cb, cc):
            if boxes_share_witness(b, Cb):
                return "shared", dict(cond=i)
            return "contradictory", dict(cond=i)
    return "ok", None


# ------------------------------------------------------------------ the alive gate
def gate(b, cond_boxes, nofams, budget, cond_names=()):
    """full arbiter chain up to (but not including) the LP."""
    if b is not None:
        st, info = classify_at(b, cond_boxes)
    else:
        st, info = "ok", None
    out = dict(state=st, info=info, k=None, fam=None, hugs=None, unkillable=None, shares=None,
               per_image=None, hug=None)
    if st == "shared":
        out["shares"] = list(cond_names)[info["cond"]] if cond_names else info["cond"]
        return out
    if st != "ok":
        return out
    boxes = list(PINS) + list(cond_boxes) + ([b] if b is not None else [])
    hyp = Hyp(boxes, list(nofams))
    av = alive84.alive_verdict(hyp, budget, CLS)
    per = {}
    hugs = []
    for g, pi in av["per_image"].items():
        dr = [d for d in pi["dropped"] if d not in cond_names]
        h = dr[0] if len(dr) == 1 else None
        per[g] = dict(k=pi["k"], dropped=pi["dropped"], hug=h)
        if h is not None:
            hugs.append(h)
    # the primary hug: the drop of the image with the largest k (deterministic tie-break by key)
    best = sorted(per, key=lambda g: (-per[g]["k"], g))[0]
    hug = per[best]["hug"] or (hugs[0] if hugs else None)
    out.update(k=av["k"], fam=av["witness_family"], unkillable=bool(av["unkillable"]),
               dropped=av["per_image"][best]["dropped"], per_image=per, hugs=hugs, hug=hug,
               best_image=best)
    out["state"] = "unkillable" if out["unkillable"] else "attemptable"
    return out


# ------------------------------------------------------------------ records / resumability
class Sink:
    def __init__(self, jsonl, log):
        self.path = os.path.join(RES, jsonl)
        self.done = {}
        if os.path.exists(self.path):
            for line in open(self.path):
                try:
                    r = json.loads(line)
                    self.done[r["tag"]] = r
                except Exception:
                    pass
        P.JSONL = self.path
        P.LOGP = os.path.join(LOGS, log)
        P.done_tags = lambda: set(self.done)
        vac59.done_tags = P.done_tags

    def has(self, tag):
        return tag in self.done

    def put(self, rec):
        self.done[rec["tag"]] = rec
        with open(self.path, "a") as f:
            f.write(json.dumps(rec) + "\n")


def logline(*x):
    P.logline(*x)


# ------------------------------------------------------------------ the kill unit
def kill(sink, tag, b, cond_boxes, nofams, budget, extra, lp_time=300.0, cert_time=240.0,
         depth=56, jobs=2, pins=None):
    if sink.has(tag):
        return sink.done[tag]
    pin_boxes = list(PINS if pins is None else pins)
    base = pin_boxes + list(cond_boxes)
    hyp = Hyp(base + [b] if b is not None else base, list(nofams))
    n_cores = len(hyp.boxes)
    if 11 - n_cores != budget:
        raise AssertionError("node %s: budget %d != 11 - #cores %d -- the certificate would be "
                             "MALFORMED; check pins/cond_boxes" % (tag, budget, n_cores))
    real = images_realizing(hyp)
    if real:
        rec = dict(tag=tag, verdict="refused (CANARY: realised by %s, never certified)"
                   % ",".join(real), canary_images=real, budget=budget,
                   ts=time.strftime("%Y-%m-%d %H:%M:%S"), **extra)
        sink.put(rec)
        return rec
    if budget == 1:
        wait_for_commit(tag)
        rec = vac59.run_vacuity(tag, hyp, 1, rec_extra=extra, depth=max(depth, 60), jobs=jobs)
        if rec is not None:
            sink.done[tag] = rec
        return rec
    st = extra.get("pinguard", "ok")
    wait_for_commit(tag)
    rec = P.run_child(tag, hyp, budget, extra.get("depth_j", 0), extra.get("a"), extra.get("at"),
                      extra.get("kind", "YES"), st, extra.get("info"),
                      b.to_json() if b is not None else None,
                      lp_time=lp_time, cert_time=cert_time, depth=depth, jobs=jobs)
    if rec is not None:
        rec.update({k: v for k, v in extra.items() if k not in rec})
        sink.done[tag] = rec
        if str(rec.get("verdict", "")).startswith("FAIL"):
            fix = run_eps_geo(tag, cert_time=cert_time, depth=depth, jobs=jobs)
            if fix:
                rec = dict(rec)
                rec.update(fix)
        if rec.get("verdict") == "PASS" and images_realizing(hyp):
            logline("ENGINE BUG: PASS on an image-realizable child " + tag)
            sys.exit(9)
        sink.put(rec)
    return rec


def run_eps_geo(tag, margins=(0.002, 0.004), cert_time=240.0, depth=56, jobs=2):
    """A57 T14: re-solve with A56's row-shrink margin.  Sound -- shrinking rows makes the LP
    harder, the arbiter is unchanged, so a wrong margin can only produce another FAIL."""
    import subprocess
    node_path = os.path.join(RES, "nodes", CLS, tag + ".json")
    if not os.path.exists(node_path):
        return {}
    certdir = os.path.join(CERTS, CLS)
    steps = []
    for m in margins:
        cert_out = os.path.join(certdir, "%s_epsgeo%g.json" % (tag, m))
        cmd = [sys.executable, os.path.join(HERE, "certify.py"), node_path,
               "--s_rat", K84.S_RAT, "--eps_geo", "%g" % m, "--rounds", "2", "--jobs", str(jobs),
               "--depth", str(depth), "--time_limit", str(cert_time),
               "--resolve_time", str(cert_time), "--out", cert_out, "--scale", "0",
               "--scale_cap", "1.40000", "--max_w", "32", "--loop_cols"]
        wait_for_commit(tag + "_epsgeo")
        t0 = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True)
        with open(os.path.join(LOGS, "epsgeo_%s.log" % tag), "a") as f:
            f.write(p.stdout[-4000:] + "\n---\n")
        steps.append(dict(eps_geo=m, rc=p.returncode, seconds=round(time.time() - t0, 1)))
        if p.returncode == 0:
            open(cert_out + ".PASS", "w").write("ok")
            return dict(verdict="PASS", cert_path=cert_out, eps_geo_used=m, eps_geo=steps)
    return dict(verdict="FAIL(eps_geo retries exhausted) -> deepen", eps_geo=steps)


def defer(phase, j, tag, exc, extra=None):
    rec = dict(tag=tag, phase=phase, verdict="DEFERRED(%s)" % type(exc).__name__,
               error=str(exc)[:300], ts=time.strftime("%Y-%m-%d %H:%M:%S"))
    if extra:
        rec.update(extra)
    with open(os.path.join(RES, "a85_%s_deferred_j%d.jsonl" % (CLS, j)), "a") as f:
        f.write(json.dumps(rec) + "\n")
    logline("  DEFERRED %s: %s (node NOT marked done; a later pass retries it)" % (tag, exc))
    return rec


# ------------------------------------------------------------------ warm start
def class_warm(max_atoms=0):
    """columns-only warm pool (A57 T4).  Sources: A55's k4/k3 sweep nodes for THIS class, A53's
    simple-strata nodes, and this attempt's own nodes.  A57/A59/A60/A61/A82 are NOT read."""
    import glob
    ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
    ATT = os.path.join(ROOT, "attempts")
    srcs = []
    for root in (os.path.join(ATT, "A55-k4-sweep"), os.path.join(ATT, "A53-simple-strata")):
        srcs += [os.path.join(root, "results", "nodes", "%s.json" % CLS)]
        srcs += sorted(glob.glob(os.path.join(root, "results", "nodes", "%s_state*.json" % CLS)))
        srcs += sorted(glob.glob(os.path.join(root, "results", "nodes", "%s.prev*.json" % CLS)))
    srcs += sorted(glob.glob(os.path.join(RES, "nodes", CLS, "*.json")))
    atoms, seen, used = [], set(), []
    for p in srcs:
        if not os.path.exists(p):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        used.append(os.path.basename(p))
        for key in ("orbits", "atoms_all"):
            for a in d.get(key, []):
                k = (round(a[0], 7), round(a[1], 7))
                if k not in seen:
                    seen.add(k)
                    atoms.append((a[0], a[1]))
    if max_atoms and len(atoms) > max_atoms:
        atoms = atoms[:max_atoms]
    return atoms, used


def init_warm(max_atoms=0):
    atoms, used = class_warm(max_atoms)
    P.PILOT_WARM = dict(atoms=list(atoms), rows=[])
    P.PILOT_SEEN = {(round(a[0], 7), round(a[1], 7)) for a in atoms}
    logline("warm pool: %d atoms (columns only) from %s" % (len(atoms), used[:6]))


# ------------------------------------------------------------------ PHASE: zone cover / census
def build_cover(w=0.15, nth=8, a_min=0.34, cw=0.6, zone="interior"):
    from tree57 import cover
    rect = zones(K84.S0F, cw)[zone]
    boxes, bad, grid = cover(rect, K84.S0F, w, nth, a_min)
    return rect, boxes, bad, grid


def census(cond_names, w=0.15, nth=8, a_min=0.34, out=None, cond_boxes=None, zone="interior"):
    """classify the whole cover at conditioning depth j.  Exact; no LP."""
    cond = list(cond_boxes) if cond_boxes is not None else [basin_box(n) for n in cond_names]
    budget = NFREE - len(cond) - 1
    rect, boxes, bad, grid = build_cover(w, nth, a_min, zone=zone)
    rows = []
    counts = dict(cover=len(boxes), uncoverable=len(bad), contradictory=0, parent=0, shared=0,
                  nocore=0, attemptable=0, unkillable=0)
    pd_rules = {"slack-core": 0, "PD": 0}
    Pl = {n: img_deg(n) for n in FREE}
    inbox = {n: [] for n in FREE}
    for i, b in enumerate(boxes):
        g = gate(b, cond, [], budget, cond_names)
        counts[g["state"]] = counts.get(g["state"], 0) + 1
        if g["state"] == "contradictory" and isinstance(g["info"], dict):
            pd_rules[g["info"].get("rule", "?")] = pd_rules.get(g["info"].get("rule", "?"), 0) + 1
        hit = [n for n, (x, y, th) in Pl.items()
               if b.x0 - 1e-5 <= x <= b.x1 + 1e-5 and b.y0 - 1e-5 <= y <= b.y1 + 1e-5
               and b.th0 - 1e-4 <= th <= b.th1 + 1e-4]
        for n in hit:
            inbox[n].append((i, g["state"]))
        rows.append(dict(i=i, box=b.to_json(), state=g["state"], k=g["k"], fam=g["fam"],
                         hugs=g["hugs"], hug=g["hug"], shares=g["shares"],
                         per_image={gg: g["per_image"][gg]["k"] for gg in (g["per_image"] or {})},
                         ghost=ghost_distance(b), images_in_box=hit))
    # canary at level 0: every box containing an image placement must be unkillable or shared
    inzone = {n: (rect[0] <= Pl[n][0] <= rect[1] and rect[2] <= Pl[n][1] <= rect[3])
              for n in FREE}
    canary_bad = [dict(name=n, boxes=inbox[n]) for n in FREE
                  if inzone[n] and (not inbox[n] or
                                    any(s not in ("unkillable", "shared") for (_, s) in inbox[n]))]
    pdc, pdbad = canary_pd()
    res = dict(cls=CLS, cond=list(cond_names), j=len(cond_names), zone=zone,
               child_budget=budget, rect=list(rect), grid=list(grid), counts=counts,
               contradictory_by_rule=pd_rules, lemma_PD=C["lemma_PD"],
               canary_PD=pdc, canary_PD_violations=pdbad,
               delta_pin=C["delta_pin"], rho=C["rho"], A=C["A"], pin_core_a=C["pin_core_a"],
               boxes_with_an_image_placement=sum(1 for r in rows if r["images_in_box"]),
               images_in_zone={n: bool(inzone[n]) for n in FREE},
               image_boxes={n: inbox[n] for n in FREE},
               canary_violations=canary_bad, rows=rows)
    if out:
        json.dump(res, open(os.path.join(RES, out), "w"), indent=1)
    return res


def _sample_rows(rows, sample):
    """A57 stratified ordering: nearest / median / farthest third by ghost distance."""
    if not sample or sample >= len(rows):
        return list(rows)
    srt = sorted(rows, key=lambda r: (r["ghost"], r["i"]))
    n = sample // 3
    m = len(srt)
    lo = srt[:n]
    mid = srt[m // 2 - n // 2: m // 2 - n // 2 + n]
    hi = srt[-n:]
    out, seen = [], set()
    for r in lo + mid + hi:
        if r["i"] not in seen:
            seen.add(r["i"])
            out.append(r)
    for r in srt:
        if len(out) >= sample:
            break
        if r["i"] not in seen:
            seen.add(r["i"])
            out.append(r)
    return sorted(out, key=lambda r: r["i"])


def phase_cover(cond_names, shard="0/1", w=0.15, nth=8, a_min=0.34, lp_time=600.0,
                cert_time=300.0, wall=1e9, max_children=10 ** 9, sample=0, zone="interior"):
    j = len(cond_names)
    pref = "c%d" % j
    si, sn = map(int, shard.split("/"))
    sink = Sink("a85_%s_cover_j%d.jsonl" % (CLS, j), "%s_cover_j%d_s%d.log" % (CLS, j, si))
    init_warm()
    cen_path = os.path.join(RES, "a85_%s_census_j%d.json" % (CLS, j))
    cen = (json.load(open(cen_path)) if os.path.exists(cen_path)
           else census(cond_names, w, nth, a_min, out="a85_%s_census_j%d.json" % (CLS, j),
                       zone=zone))
    cond = [basin_box(n) for n in cond_names]
    budget = cen["child_budget"]
    todo = _sample_rows([r for r in cen["rows"] if r["state"] == "attemptable"], sample)
    logline("A84 %s cover j=%d budget=%d counts=%s sample=%d/%d shard=%s"
            % (CLS, j, budget, json.dumps(cen["counts"]), len(todo),
               sum(1 for r in cen["rows"] if r["state"] == "attemptable"), shard))
    mine = [r for i, r in enumerate(todo) if i % sn == si][:max_children]
    prog = os.path.join(PROG, "%s_cover_j%d_s%d.json" % (CLS, j, si))
    st = dict(phase="cover", cls=CLS, j=j, cond=list(cond_names), shard=shard, budget=budget,
              total=len(mine), sample=len(todo), counts=cen["counts"], done=0, passed=0,
              failed=0, alive=0, canary=0, started=time.strftime("%Y-%m-%d %H:%M:%S"))
    t0 = time.time()

    def flush():
        st["elapsed_s"] = round(time.time() - t0, 1)
        st["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        st["waits"] = len(WAITS)
        json.dump(st, open(prog, "w"), indent=1)

    flush()
    for r in mine:
        tag = "%s_Y%04d" % (pref, r["i"])
        if sink.has(tag):
            st["done"] += 1
            st["skipped"] = st.get("skipped", 0) + 1
            flush()
            continue
        if time.time() - t0 > wall:
            logline("wall reached; stopping cleanly")
            break
        b = Box.from_json(r["box"])
        try:
            rec = kill(sink, tag, b, cond, [], budget,
                       dict(kind="YES-cover", depth_j=j, pinguard="ok", a=float(b.core().a),
                            hugs=r["hugs"], hug=r["hug"], k=r["k"], ghost=r["ghost"],
                            per_image=r["per_image"], cond=list(cond_names), level=0),
                       lp_time=lp_time, cert_time=cert_time)
        except (MemoryError, CommitStarved) as e:
            defer("cover", j, tag, e, dict(box=r["box"], budget=budget))
            st["deferred"] = st.get("deferred", 0) + 1
            flush()
            time.sleep(30.0)
            continue
        v = (rec or {}).get("verdict", "")
        st["done"] += 1
        st["passed"] += 1 if v == "PASS" else 0
        st["failed"] += 1 if v.startswith("FAIL") else 0
        st["alive"] += 1 if v.startswith("refused (tau") else 0
        st["canary"] += 1 if "CANARY" in v else 0
        flush()
    st["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    flush()
    logline("cover shard done " + json.dumps({k: st[k] for k in
            ("cls", "j", "shard", "total", "done", "passed", "failed", "alive", "canary",
             "elapsed_s")}))
    return st


# ------------------------------------------------------------------ PHASE: residue ladder
def ladder_scan(cond_names, levels, w=0.15, nth=8, a_min=0.34, out=None, seed=None,
                stop_when_basin=True, refine_chain=False, cond_boxes=None, zone="interior"):
    """the EXACT residue ladder: bisect only the unkillable boxes, re-run pinguard + the alive
    gate on every sub-box, keep the still-unkillable ones.  No LP."""
    cond = list(cond_boxes) if cond_boxes is not None else [basin_box(n) for n in cond_names]
    j = len(cond)
    budget = NFREE - j - 1
    cen_path = os.path.join(RES, "a85_%s_census_j%d.json" % (CLS, j))
    if seed is not None:
        residue = [Box.from_json(d) for d in seed]
        chain = []
        cen = None
    else:
        cen = (json.load(open(cen_path)) if (os.path.exists(cen_path) and cond_boxes is None)
               else census(cond_names, w, nth, a_min,
                           out=("a85_%s_census_j%d.json" % (CLS, j)) if cond_boxes is None
                           else None, cond_boxes=cond_boxes, zone=zone))
        residue = [Box.from_json(r["box"]) for r in cen["rows"] if r["state"] == "unkillable"]
        chain = [(Box.from_json(r["box"]), r["shares"]) for r in cen["rows"]
                 if r["state"] == "shared"]
    hug = {}
    for b in residue:
        g = gate(b, cond, [], budget, cond_names)
        hug[b.key()] = g["hug"]
    Pl = {n: img_deg(n) for n in FREE}
    rect = zones(K84.S0F, 0.6)[zone]
    inzone = [n for n in FREE if rect[0] <= Pl[n][0] <= rect[1] and rect[2] <= Pl[n][1] <= rect[3]]
    out_levels, chains, bug = [], [], []
    for level in range(levels + 1):
        rad = max([box_radius(b) for b in residue], default=0.0)
        vol = sum(box_volume(b) for b in residue)
        gaps, inside, tube, cont, cont_t, cont_c, cont_th = [], 0, 0, [], [], [], []
        for b in residue:
            hb = hug.get(b.key())
            if hb:
                gaps.append(sup_gap(b, hb))
                cont.append(sup_containment(b, hb))
                cont_t.append(contain_t(b, hb))
                cont_c.append(contain_c(b, hb))
                cont_th.append(contain_theta(b, hb))
                inside += 1 if cont_t[-1] <= RBASIN else 0
                tube += 1 if (cont_c[-1] <= R_C_TUBE and cont_th[-1] <= R_T_TUBE) else 0
        ch_open = [(b, nm) for (b, nm) in chain if contain_t(b, nm) > RBASIN]
        # ---- canary: every in-zone image placement must sit in a residue/chain box ----------
        pool = [(b, "residue") for b in residue] + [(b, "chain") for (b, _) in chain]
        lvl_chain = {}
        for n in inzone:
            (x, y, thd) = Pl[n]
            hits = [k for k, (b, kind) in enumerate(pool)
                    if b.x0 - 1e-5 <= x <= b.x1 + 1e-5 and b.y0 - 1e-5 <= y <= b.y1 + 1e-5
                    and b.th0 - 1e-4 <= thd <= b.th1 + 1e-4]
            lvl_chain[n] = [dict(kind=pool[k][1], box=pool[k][0].to_json(),
                                 radius=box_radius(pool[k][0]),
                                 contain_t=contain_t(pool[k][0], n)) for k in hits]
            if not hits:
                bug.append(dict(level=level, name=n,
                                why="no residue/chain box contains this image placement"))
        chains.append(dict(level=level, placements=lvl_chain))
        rowl = dict(level=level, boxes=len(residue), volume=vol, max_box_radius=rad,
                    max_gap_to_image=(max(gaps) if gaps else None),
                    max_containment_theta=(max(cont_th) if cont_th else None),
                    max_containment_c=(max(cont_c) if cont_c else None),
                    max_containment_t=(max(cont_t) if cont_t else None),
                    max_containment_sup=(max(cont) if cont else None),
                    contraction_ratio=((max(gaps) / rad) if (gaps and rad > 0) else None),
                    rbasin=RBASIN, r_c_tube=R_C_TUBE, r_theta_tube=R_T_TUBE,
                    inside_A36_basin=inside, inside_tube_profile=tube,
                    all_inside=(inside == len(residue) and len(residue) > 0),
                    all_in_tube=(tube == len(residue) and len(residue) > 0),
                    chain_boxes=len(chain), chain_open=len(ch_open),
                    chain_discharged=len(chain) - len(ch_open),
                    canary_ok=not any(e["level"] == level for e in bug))
        out_levels.append(rowl)
        if (stop_when_basin and rowl["all_inside"] and rad <= HW_TARGET
                and (not ch_open or not refine_chain)):
            break
        if level == levels:
            break
        nxt, queue = [], []
        for b in residue:
            hb = hug.get(b.key())
            for sb in b.split():
                g = gate(sb, cond, [], budget, cond_names)
                if g["state"] == "unkillable":
                    nxt.append(sb)
                    hug[sb.key()] = g["hug"] or hb
                elif g["state"] == "attemptable":
                    queue.append(dict(box=sb.to_json(), k=g["k"], hugs=g["hugs"], hug=g["hug"],
                                      level=level, ghost=ghost_distance(sb)))
                elif g["state"] == "shared":
                    chain.append((sb, g["shares"]))
        nchain = []
        for (b, nm) in (ch_open if refine_chain else []):
            for sb in b.split():
                g = gate(sb, cond, [], budget, cond_names)
                if g["state"] == "shared":
                    nchain.append((sb, g["shares"]))
                elif g["state"] == "unkillable":
                    nxt.append(sb)
                    hug[sb.key()] = g["hug"] or nm
                elif g["state"] == "attemptable":
                    queue.append(dict(box=sb.to_json(), k=g["k"], hugs=g["hugs"], hug=g["hug"],
                                      level=level, ghost=ghost_distance(sb)))
        chain = ([(b, nm) for (b, nm) in chain if contain_t(b, nm) <= RBASIN] + nchain
                 if refine_chain else chain)
        out_levels[-1]["kill_queue"] = len(queue)
        out_levels[-1]["queue"] = queue
        residue = nxt
    pdc, pdbad = canary_pd()
    res = dict(cls=CLS, cond=list(cond_names), j=j, budget=budget, levels=out_levels,
               cond_boxes=[b.to_json() for b in cond], lemma_PD=C["lemma_PD"],
               delta_pin=C["delta_pin"], rho=C["rho"], A=C["A"],
               canary_PD=pdc, canary_PD_violations=pdbad,
               images_in_zone=inzone, canary_chain=chains, canary_bugs=bug,
               final_residue=[b.to_json() for b in residue],
               final_chain=[[b.to_json(), nm] for (b, nm) in chain])
    if out:
        json.dump(res, open(os.path.join(RES, out), "w"), indent=1)
    return res, None


def phase_ladder(cond_names, levels=26, shard="0/1", lp_time=600.0, cert_time=300.0,
                 wall=1e9, kill_queue=True, max_kills=10 ** 9, sample=0):
    j = len(cond_names)
    si, sn = map(int, shard.split("/"))
    sink = Sink("a85_%s_ladder_j%d.jsonl" % (CLS, j), "%s_ladder_j%d_s%d.log" % (CLS, j, si))
    if kill_queue:
        init_warm()
    scan_path = os.path.join(RES, "a85_%s_ladder_j%d_scan.json" % (CLS, j))
    if os.path.exists(scan_path):
        scan = json.load(open(scan_path))
    else:
        scan, _ = ladder_scan(cond_names, levels,
                              out="a85_%s_ladder_j%d_scan.json" % (CLS, j))
    cond = ([Box.from_json(d) for d in scan["cond_boxes"]] if scan.get("cond_boxes")
            else [basin_box(n) for n in cond_names])
    budget = scan["budget"]
    queue = [(L["level"], i, q) for L in scan["levels"] for i, q in enumerate(L.get("queue", []))]
    if sample:
        bands = [(6, 10), (12, 16), (18, 10 ** 6)]
        per = max(1, sample // len(bands))
        pick, seen = [], set()
        for (lo, hi) in bands:
            cand = [x for x in queue if lo <= x[0] <= hi]
            cand.sort(key=lambda x: (x[0], x[1]))
            step = max(1, len(cand) // per) if cand else 1
            for x in cand[::step][:per]:
                if (x[0], x[1]) not in seen:
                    seen.add((x[0], x[1]))
                    pick.append(x)
        for x in queue:
            if len(pick) >= sample:
                break
            if (x[0], x[1]) not in seen:
                seen.add((x[0], x[1]))
                pick.append(x)
        queue = sorted(pick, key=lambda x: (x[0], x[1]))[:sample]
    mine = [x for i, x in enumerate(queue) if i % sn == si][:max_kills]
    prog = os.path.join(PROG, "%s_ladder_j%d_s%d.json" % (CLS, j, si))
    st = dict(phase="ladder", cls=CLS, j=j, cond=list(cond_names), shard=shard, budget=budget,
              levels=[{k: L[k] for k in L if k != "queue"} for L in scan["levels"]],
              total=len(mine), queue_all=len(queue), done=0, passed=0, failed=0, alive=0,
              started=time.strftime("%Y-%m-%d %H:%M:%S"))
    t0 = time.time()

    def flush():
        st["elapsed_s"] = round(time.time() - t0, 1)
        st["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        st["waits"] = len(WAITS)
        json.dump(st, open(prog, "w"), indent=1)

    flush()
    logline("A84 %s ladder j=%d levels=%d queue=%d shard=%s"
            % (CLS, j, len(scan["levels"]), len(queue), shard))
    if not kill_queue:
        return st
    for (level, i, q) in mine:
        tag = "l%d_L%02d_%04d" % (j, level, i)
        if sink.has(tag):
            st["done"] += 1
            st["skipped"] = st.get("skipped", 0) + 1
            flush()
            continue
        if time.time() - t0 > wall:
            logline("wall reached; stopping cleanly")
            break
        b = Box.from_json(q["box"])
        try:
            rec = kill(sink, tag, b, cond, [], budget,
                       dict(kind="YES-ladder", depth_j=j, level=level, pinguard="ok",
                            a=float(b.core().a), hugs=q["hugs"], hug=q.get("hug"), k=q["k"],
                            ghost=q.get("ghost"), radius=box_radius(b),
                            # r_kill is measured against the NEAREST image square: an attemptable
                            # box drops >= 2 witnesses in every image, so it has no unique `hug`.
                            sup_gap=(q.get("ghost") if q.get("ghost") is not None
                                     else (sup_gap(b, q["hug"]) if q.get("hug") else None)),
                            hug_gap=(sup_gap(b, q["hug"]) if q.get("hug") else None),
                            cond=list(cond_names)),
                       lp_time=lp_time, cert_time=cert_time)
        except (MemoryError, CommitStarved) as e:
            defer("ladder", j, tag, e, dict(box=q["box"], budget=budget, level=level))
            st["deferred"] = st.get("deferred", 0) + 1
            flush()
            time.sleep(30.0)
            continue
        v = (rec or {}).get("verdict", "")
        st["done"] += 1
        st["passed"] += 1 if v == "PASS" else 0
        st["failed"] += 1 if v.startswith("FAIL") else 0
        st["alive"] += 1 if v.startswith("refused") else 0
        flush()
    st["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    flush()
    return st


# ------------------------------------------------------------------ PHASE: deepen (A57 T11)
def resisters(jsonl):
    p = os.path.join(RES, jsonl)
    if not os.path.exists(p):
        return []
    last = {}
    for line in open(p):
        try:
            r = json.loads(line)
        except Exception:
            continue
        last[r.get("tag")] = r
    return [r for r in last.values()
            if (r.get("verdict", "").startswith("refused (tau")
                or r.get("verdict", "").startswith("FAIL")) and r.get("box")]


def phase_deepen(cond_names, source, rnd=1, shard="0/1", lp_time=600.0, cert_time=300.0,
                 wall=1e9, max_children=10 ** 9, cond_boxes=None):
    j = len(cond_names)
    si, sn = map(int, shard.split("/"))
    cond = (list(cond_boxes) if cond_boxes is not None else [basin_box(n) for n in cond_names])
    budget = NFREE - len(cond) - 1
    src = resisters(source)
    sink = Sink("a85_%s_deepen_j%d_r%d.jsonl" % (CLS, j, rnd),
                "%s_deepen_j%d_r%d_s%d.log" % (CLS, j, rnd, si))
    init_warm()
    subs = []
    for r in src:
        b = Box.from_json(r["box"])
        for si_, sb in enumerate(b.split()):
            subs.append((r["tag"], si_, sb))
    mine = [x for i, x in enumerate(subs) if i % sn == si][:max_children]
    prog = os.path.join(PROG, "%s_deepen_j%d_r%d_s%d.json" % (CLS, j, rnd, si))
    st = dict(phase="deepen", cls=CLS, j=j, round=rnd, source=source, cond=list(cond_names),
              budget=budget, shard=shard, parents=len(src), total=len(mine), done=0, free=0,
              residue=0, passed=0, failed=0, alive=0,
              started=time.strftime("%Y-%m-%d %H:%M:%S"))
    t0 = time.time()

    def flush():
        st["elapsed_s"] = round(time.time() - t0, 1)
        st["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        st["waits"] = len(WAITS)
        json.dump(st, open(prog, "w"), indent=1)

    flush()
    logline("A84 %s deepen j=%d round=%d parents=%d sub-boxes=%d shard=%s"
            % (CLS, j, rnd, len(src), len(mine), shard))
    for (ptag, si_, sb) in mine:
        tag = "%s_D%d" % (ptag, si_)
        if sink.has(tag):
            st["done"] += 1
            st["skipped"] = st.get("skipped", 0) + 1
            flush()
            continue
        if time.time() - t0 > wall:
            logline("wall reached; stopping cleanly")
            break
        g = gate(sb, cond, [], budget, cond_names)
        if g["state"] in ("contradictory", "parent", "nocore", "shared"):
            sink.put(dict(tag=tag, parent=ptag,
                          verdict=("KILL-BY-LOGIC" if g["state"] == "contradictory"
                                   else "carried (%s)" % g["state"]),
                          state=g["state"], budget=budget, box=sb.to_json(), depth_j=j,
                          round=rnd, ts=time.strftime("%Y-%m-%d %H:%M:%S")))
            st["free" if g["state"] == "contradictory" else "residue"] += 1
            st["done"] += 1
            flush()
            continue
        if g["state"] == "unkillable":
            sink.put(dict(tag=tag, parent=ptag,
                          verdict="ALIVE-CERTIFIED (A57-3, k=%d>=budget %d)" % (g["k"], budget),
                          state=g["state"], k=g["k"], hugs=g["hugs"], hug=g["hug"],
                          budget=budget, box=sb.to_json(), depth_j=j, round=rnd,
                          ts=time.strftime("%Y-%m-%d %H:%M:%S")))
            st["residue"] += 1
            st["done"] += 1
            flush()
            continue
        try:
            rec = kill(sink, tag, sb, cond, [], budget,
                       dict(kind="YES-deepen", depth_j=j, round=rnd, parent=ptag,
                            pinguard="ok", a=float(sb.core().a), hugs=g["hugs"], hug=g["hug"],
                            k=g["k"], cond=list(cond_names)),
                       lp_time=lp_time, cert_time=cert_time)
        except (MemoryError, CommitStarved) as e:
            defer("deepen", j, tag, e, dict(box=sb.to_json(), budget=budget, parent=ptag))
            st["deferred"] = st.get("deferred", 0) + 1
            flush()
            time.sleep(30.0)
            continue
        v = (rec or {}).get("verdict", "")
        st["done"] += 1
        st["passed"] += 1 if v == "PASS" else 0
        st["failed"] += 1 if v.startswith("FAIL") else 0
        st["alive"] += 1 if v.startswith("refused") else 0
        flush()
    st["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    flush()
    logline("deepen done " + json.dumps({k: st[k] for k in
            ("cls", "j", "round", "shard", "total", "done", "free", "residue", "passed",
             "failed", "alive", "elapsed_s")}))
    return st


# ------------------------------------------------------------------ R4: the P1-analogue
def phase_p1(cw=0.6, zone="interior", lp_time=900.0, cert_time=480.0):
    """NO child: pins + NoFam(zone x [0, 90]) at budget N.  A PASS is Lemma A84-P1(<cls>):
    every packing containing the class's slack pins has a square centred in the zone."""
    rect = zones(K84.S0F, cw)[zone]
    nf = NoFam(rect[0], rect[1], rect[2], rect[3], [(0.0, 90.0)])
    budget = NFREE
    sink = Sink("a85_%s_p1.jsonl" % CLS, "%s_p1.log" % CLS)
    init_warm()
    g = gate(None, [], [nf], budget)
    hyp = Hyp(list(PINS), [nf])
    real = images_realizing(hyp)
    logline("A84 %s P1 zone=%s rect=%s budget=%d gate: k=%d state=%s per_image=%s canary=%s"
            % (CLS, zone, [round(v, 6) for v in rect], budget, g["k"], g["state"],
               json.dumps({gg: g["per_image"][gg]["k"] for gg in g["per_image"]}), real))
    out = dict(cls=CLS, zone=zone, rect=list(rect), budget=budget, gate_k=g["k"],
               gate_state=g["state"], per_image={gg: g["per_image"][gg]["k"]
                                                 for gg in g["per_image"]},
               canary_images=real, delta_pin=C["delta_pin"], rho=C["rho"], A=C["A"])
    if g["state"] == "unkillable":
        out["verdict"] = ("refused (ALIVE-CERTIFIED: k=%d >= budget %d -- the P1 NO child is "
                          "LP-unkillable, so no P1-analogue holds for this zone)"
                          % (g["k"], budget))
        json.dump(out, open(os.path.join(RES, "a85_%s_p1.json" % CLS), "w"), indent=1)
        print(json.dumps(out, indent=1))
        return out
    tag = "p1_%s" % zone
    try:
        rec = kill(sink, tag, None, [], [nf], budget,
                   dict(kind="NO-P1", depth_j=0, pinguard="ok", zone=zone, k=g["k"]),
                   lp_time=lp_time, cert_time=cert_time)
    except (MemoryError, CommitStarved) as e:
        rec = defer("p1", 0, tag, e, dict(budget=budget, zone=zone))
    out["record"] = rec
    out["verdict"] = (rec or {}).get("verdict")
    out["tau"] = (rec or {}).get("tau")
    out["eta"] = None if out["tau"] is None else out["tau"] - budget
    out["lp_s"] = (rec or {}).get("lp_s")
    out["cert_s"] = (rec or {}).get("cert_s")
    out["lemma"] = ("A84-P1(%s): every packing whose squares realise the %d slack pins of %s has "
                    "a square with centre in [%.6f, %.6f]^2" % (CLS, C["k_s"], CLS, rect[0],
                                                                rect[1])
                    if out["verdict"] == "PASS" else "NOT ESTABLISHED")
    json.dump(out, open(os.path.join(RES, "a85_%s_p1.json" % CLS), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "record"}, indent=1))
    return out


# ------------------------------------------------------------------ scoreboard / summary
def scoreboard(out=None):
    import collections
    out = out or "a85_%s_scoreboard.json" % CLS
    board = {}
    pref = "a85_%s_" % CLS
    for p in sorted(os.listdir(RES)):
        if not (p.startswith(pref) and p.endswith(".jsonl")) or "deferred" in p or "waits" in p:
            continue
        c = collections.Counter()
        lp = ct = 0.0
        last = {}
        for line in open(os.path.join(RES, p)):
            try:
                r = json.loads(line)
            except Exception:
                continue
            last[r.get("tag")] = r
        lps, etas = [], []
        for r in last.values():
            v = r.get("verdict", "?")
            key = ("PASS" if v == "PASS" else
                   "KILL-BY-LOGIC" if v.startswith("KILL-BY-LOGIC") else
                   "ALIVE-CERTIFIED" if v.startswith("ALIVE") else
                   "CANARY" if "CANARY" in v else
                   "LP-alive" if v.startswith("refused (tau") else
                   "cert-FAIL" if v.startswith("FAIL") else "other")
            c[key] += 1
            lp += r.get("lp_s") or 0.0
            ct += r.get("cert_s") or 0.0
            if r.get("lp_s"):
                lps.append(r["lp_s"])
            if r.get("eta") is not None:
                etas.append(r["eta"])
        den = c["PASS"] + c["LP-alive"] + c["cert-FAIL"]
        board[p] = dict(records=len(last), verdicts=dict(c), lp_s=round(lp, 1),
                        cert_s=round(ct, 1),
                        kill_rate=(round(c["PASS"] / float(den), 4) if den else None),
                        lp_s_list=sorted(lps), etas=sorted(etas))
    prog = {}
    for p in sorted(os.listdir(PROG)):
        if p.startswith(CLS) and p.endswith(".json"):
            try:
                prog[p] = json.load(open(os.path.join(PROG, p)))
            except Exception:
                pass
    res = dict(cls=CLS, generated=time.strftime("%Y-%m-%d %H:%M:%S"), phases=board,
               progress=prog)
    json.dump(res, open(os.path.join(RES, out), "w"), indent=1)
    return res


# ------------------------------------------------------------------ cli
def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["census", "cover", "ladderscan", "ladder", "deepen",
                                    "p1", "board"])
    ap.add_argument("--cls", required=True)
    ap.add_argument("--cond", default="")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--levels", type=int, default=28)
    ap.add_argument("--lp_time", type=float, default=600.0)
    ap.add_argument("--cert_time", type=float, default=300.0)
    ap.add_argument("--wall", type=float, default=1e9)
    ap.add_argument("--max_children", type=int, default=10 ** 9)
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--w", type=float, default=0.15)
    ap.add_argument("--nth", type=int, default=8)
    ap.add_argument("--a_min", type=float, default=0.34)
    ap.add_argument("--no_kill", action="store_true")
    ap.add_argument("--zone", default="interior")
    ap.add_argument("--source", default=None)
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--delta", type=float, default=K84.DELTA_PIN)
    ap.add_argument("--t_prime", type=float, default=None)
    a = ap.parse_args()
    setup(a.cls, a.delta, a.t_prime)
    cond = [c for c in a.cond.split(",") if c]
    for c in cond:
        assert c in FREE, "unknown image square " + c
    if a.cmd == "census":
        nm = ("a85_%s_census_j%d.json" % (a.cls, len(cond)) if a.zone == "interior"
              else "a85_%s_census_%s_j%d.json" % (a.cls, a.zone, len(cond)))
        r = census(cond, a.w, a.nth, a.a_min, out=nm, zone=a.zone)
        print(json.dumps(dict(cls=a.cls, j=r["j"], zone=a.zone, cond=r["cond"],
                              budget=r["child_budget"], counts=r["counts"],
                              contradictory_by_rule=r["contradictory_by_rule"],
                              lemma_PD=r["lemma_PD"],
                              image_boxes=r["boxes_with_an_image_placement"],
                              images_in_zone=r["images_in_zone"],
                              canary_PD_violations=r["canary_PD_violations"],
                              canary_violations=r["canary_violations"]), indent=1))
        if r["canary_PD_violations"]:
            print("ENGINE BUG: Lemma PD kills an image square's own box")
            sys.exit(9)
        if r["canary_violations"]:
            print("ENGINE BUG: image placement in a non-residue box")
            sys.exit(9)
    elif a.cmd == "cover":
        print(json.dumps(phase_cover(cond, a.shard, a.w, a.nth, a.a_min, a.lp_time,
                                     a.cert_time, a.wall, a.max_children, a.sample,
                                     a.zone), indent=1)[:2500])
    elif a.cmd == "ladderscan":
        r, _ = ladder_scan(cond, a.levels, a.w, a.nth, a.a_min,
                           out="a85_%s_ladder_j%d_scan.json" % (a.cls, len(cond)), zone=a.zone)
        print(json.dumps([{k: L[k] for k in L if k != "queue"} for L in r["levels"]], indent=1))
        print("images in zone: %s" % r["images_in_zone"])
        if r["canary_bugs"]:
            print("ENGINE BUG (canary): %s" % json.dumps(r["canary_bugs"][:5]))
            sys.exit(9)
    elif a.cmd == "ladder":
        st = phase_ladder(cond, a.levels, a.shard, a.lp_time, a.cert_time, a.wall,
                          kill_queue=not a.no_kill, max_kills=a.max_children, sample=a.sample)
        print(json.dumps({k: st[k] for k in st if k != "levels"}, indent=1))
    elif a.cmd == "deepen":
        src = a.source or ("a85_%s_cover_j%d.jsonl" % (a.cls, len(cond)))
        st = phase_deepen(cond, src, a.round, a.shard, a.lp_time, a.cert_time, a.wall,
                          a.max_children)
        print(json.dumps(st, indent=1))
    elif a.cmd == "p1":
        phase_p1(lp_time=a.lp_time, cert_time=a.cert_time, zone=a.zone)
    elif a.cmd == "board":
        b = scoreboard()
        print(json.dumps(b["phases"], indent=1))


if __name__ == "__main__":
    cli()
