"""
A60 campaign driver -- the trump5 residual zone-tree with the P0 engine fold-ins (G-A59-11).

Node semantics inherited VERBATIM (nothing here weakens an arbiter):
  * A54 S0  -- tau bounds tau* in neither direction; the SOLE kill arbiter is an exact rational
    certificate accepted by verify_case.py.
  * A57 T2  -- theta windows uniform in t = tan(theta/2).
  * A57 T4  -- columns-only warm starts.
  * A57 T5  -- pinguard.classify before any box is solved or read (extended here to conditioned
    cores: classify_at).
  * A57 T11 -- refinement of a box keeps the budget (the residue ladder).
  * Canary  -- substrat.trump_realizes on every child; a Trump-realizable child is NEVER
    certified.  Trump's configuration must land in a (D) leaf.

The two P0 fold-ins:
  (i)  ALIVE GATE (Lemma A57-3, exact, ~1 ms): k(N) = # of Trump's six strictly-separated scaled
       free squares surviving the node's cores and NO-families.  tau*(N) >= k(N), so k >= budget
       makes the node PROVABLY uncertifiable -- record ALIVE-CERTIFIED and never launch the LP.
       This is an efficiency gate on the KILL side only: it never turns a non-kill into a kill.
  (ii) ZERO-ATOM VACUITY ARBITER (vac59) for every budget-1 node: no LP, no EPS_CORE/EPS_ZONE
       shell (whose 2e-3 floor is the same scale as the A36 basin radius h = 3.7e-3).

Phases (P3/P4/P5 of the A59 program):
  cover   -- interior zone cover at conditioning depth j; census + kills of the attemptable boxes.
  ladder  -- residue ladder: bisect ONLY the alive-gated (unkillable) boxes, re-run pinguard +
             alive-gate on each sub-box, kill the newly attemptable ones, until every residue box
             is inside the A36 basin slice of the Trump placement it hugs.

Nothing outside attempts/A60-trump5-campaign is ever written.
"""
import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # A57 T18: pin BLAS to 1 thread BEFORE numpy loads
import pilot59 as P
from pilot59 import (S0F, S_RAT, PINS, SLOTS, FREE, TH_T, core_box, rq, tbox_deg,
                     boxes_pairwise_disjoint, init_warm)
from caselp import Box, NoFam, Hyp
from pinguard import classify, cores_meet
from substrat import zones, trump_realizes
from alive59 import alive_verdict
import vac59

H = 3.7e-3                      # A36 basin radius, sup-norm in (cx, cy, theta_rad)
TSC = 0.566                     # dt/dtheta at theta_T: t half-width of a theta-radian ball
HW_TARGET = H / 4.55            # 8.13e-4 -- the G-A59-9 annulus closure (P5)
ORDER = ["sq7", "sq8", "sq9", "sq4", "sq6", "sq10"]     # P4 conditioning order

RES = os.path.join(BASE, "results")
PROG = os.path.join(BASE, "progress")
LOGS = os.path.join(BASE, "logs")
for d in (RES, PROG, LOGS, os.path.join(BASE, "certs"), os.path.join(RES, "nodes")):
    os.makedirs(d, exist_ok=True)


# ------------------------------------------------------------------ geometry helpers
def basin_box(name, hw=H):
    """the conditioning core box: sup-norm ball of radius hw around Trump's placement `name`."""
    return core_box(name, hw, TSC * hw)


def trump_deg(name):
    cx, cy, th = FREE[name]
    return cx, cy, math.degrees(th) % 90.0


def box_radius(b):
    """sup-norm half-width of a box in (cx, cy, theta_radians)."""
    return max(0.5 * (b.x1 - b.x0), 0.5 * (b.y1 - b.y0),
               0.5 * math.radians(b.th1 - b.th0))


def sup_containment(b, name):
    """max sup-norm distance from Trump's placement `name` to a point of b, in
    (cx, cy, theta_rad).  b lies inside the A36 basin slice of `name` iff this is <= h."""
    cx, cy, thd = trump_deg(name)
    return max(abs(b.x0 - cx), abs(b.x1 - cx), abs(b.y0 - cy), abs(b.y1 - cy),
               abs(math.radians(b.th0 - thd)), abs(math.radians(b.th1 - thd)))


def sup_gap(b, name):
    """sup-norm distance from the box CENTRE to Trump's placement (the ladder diagnostic)."""
    cx, cy, thd = trump_deg(name)
    return max(abs(0.5 * (b.x0 + b.x1) - cx), abs(0.5 * (b.y0 + b.y1) - cy),
               abs(math.radians(0.5 * (b.th0 + b.th1) - thd)))


def box_volume(b):
    return (b.x1 - b.x0) * (b.y1 - b.y0) * math.radians(b.th1 - b.th0)


def boxes_share_witness(b, c):
    """can ONE square realise both boxes?  (c, theta) overlap, theta 0/90 identified."""
    if b.x1 < c.x0 or c.x1 < b.x0 or b.y1 < c.y0 or c.y1 < b.y0:
        return False
    if not (b.th1 < c.th0 or c.th1 < b.th0):
        return True
    return (b.th0 <= 1e-9 and c.th1 >= 90 - 1e-9) or (c.th0 <= 1e-9 and b.th1 >= 90 - 1e-9)


# ------------------------------------------------------------------ pinguard, extended (A57 T5)
def classify_at(b, cond_boxes):
    """classify a YES box against the pins AND the already-conditioned cores.

    Against the pins: pinguard.classify verbatim.
    Against a conditioned core box C: if core(b) meets core(C) then a square realising b and a
    square realising C overlap, so they are the SAME square.  Two sub-cases, both decided from
    the boxes alone:
      * b and C are (c, theta)-DISJOINT -> one square cannot lie in both -> the hypotheses are
        CONTRADICTORY: a free logic kill (no LP, no certificate).
      * b and C can share a witness -> the child would be counted at a budget one lower than the
        squares it actually accounts for -> UNSOUND-AT-REDUCED-BUDGET ('shared'), never certified.
    """
    st, info = classify(b, PINS, SLOTS)
    if st != "ok":
        return st, info
    cb = b.core()
    for i, C in enumerate(cond_boxes):
        cc = C.core()
        if cc is None:
            continue
        if cores_meet(cb, cc):
            if boxes_share_witness(b, C):
                return "shared", dict(cond=i)
            return "contradictory", dict(cond=i)
    return "ok", None


# NOTE (G-A60-1, soundness delta vs A59's pilot census).  A59's level-1 branching census called
# pinguard.classify with the conditioned cores appended to the PIN list, so a cover box whose
# core meets a conditioned core was booked as 'contradictory' -- a free kill -- WITHOUT checking
# whether one square could realise both boxes.  For 1-3 boxes per conditioning level (exactly the
# cover boxes that contain the conditioned Trump square) that is wrong: those are the CHAIN boxes
# and they carry Trump.  classify_at separates them as 'shared': never certified, carried at the
# PARENT budget, refined by the ladder until the box lies inside the A36 basin of the square it
# may share, at which point it is a (D)-chain node (a refinement of that conditioning core).
# The counts still reproduce A59 exactly once 'shared' is added back to 'contradictory' (T2).


# ------------------------------------------------------------------ the alive gate (P0 i)
def gate(b, cond_boxes, nofams, budget, cond_names=()):
    """full arbiter chain up to (but not including) the LP.
    -> dict(state, k, fam, dropped, hugs, unkillable)"""
    st, info = classify_at(b, cond_boxes)
    out = dict(state=st, info=info, k=None, fam=None, hugs=None, unkillable=None, shares=None)
    if st == "shared":
        out["shares"] = list(cond_names)[info["cond"]] if cond_names else info["cond"]
        return out
    if st != "ok":
        return out
    hyp = Hyp(PINS + list(cond_boxes) + [b], list(nofams))
    av = alive_verdict(hyp, budget)
    out.update(k=av["k"], fam=av["witness_family"], unkillable=bool(av["unkillable"]),
               dropped=[d[0] for d in av["dropped"]])
    # the Trump square this box "hugs": the witness it removes that is not already conditioned
    drop = [d for d in out["dropped"] if d not in cond_names]
    out["hugs"] = drop[0] if len(drop) == 1 else (drop or None)
    out["state"] = "unkillable" if out["unkillable"] else "attemptable"
    return out


# ------------------------------------------------------------------ records / resumability
class Sink:
    """one append-only jsonl + a done-set, with pilot59's run_child plumbed into it."""

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
        vac59.done_tags = P.done_tags        # vac59 imported the function by value

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
         depth=56, jobs=2):
    """attempt an exact kill on an attemptable node.  budget 1 -> zero-atom vacuity (no LP);
    budget >= 2 -> LP + certify.  Returns the record (or the cached one)."""
    if sink.has(tag):
        return sink.done[tag]
    hyp = Hyp(PINS + list(cond_boxes) + [b] if b is not None else PINS + list(cond_boxes),
              list(nofams))
    if trump_realizes(hyp, SLOTS):
        rec = dict(tag=tag, verdict="refused (CANARY: Trump-realizable, never certified)",
                   budget=budget, ts=time.strftime("%Y-%m-%d %H:%M:%S"), **extra)
        sink.put(rec)
        return rec
    if budget == 1:
        rec = vac59.run_vacuity(tag, hyp, 1, rec_extra=extra, depth=max(depth, 60), jobs=jobs)
        if rec is not None:
            sink.done[tag] = rec           # vac59 already appended to P.JSONL == sink.path
        return rec
    st = extra.get("pinguard", "ok")
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
        # run_child appended its own record BEFORE `extra` was merged, so append the enriched
        # one too (level / k / hugs / cond / any eps_geo repair).  board keeps the LAST per tag.
        sink.put(rec)
    return rec


def run_eps_geo(tag, margins=(0.002, 0.004), cert_time=240.0, depth=56, jobs=2):
    """A57 T14, folded in (A59's copy of tree57.py predates it).  A certificate with tau
    comfortably under budget can still FAIL with ZERO holes and a few witness boxes the verifier
    cannot DECIDE -- atoms sitting on placement boundaries, which more depth does not fix.
    Re-solve the node LP with A56's row-shrink margin EPS_GEO = m, then certify.  Sound: shrinking
    rows makes the LP HARDER (tau can only rise) and the arbiter is unchanged, so a wrong margin
    can only produce another FAIL."""
    import subprocess
    node_path = os.path.join(RES, "nodes", tag + ".json")
    if not os.path.exists(node_path):
        return {}
    certdir = os.path.join(BASE, "certs")
    steps = []
    for m in margins:
        cert_out = os.path.join(certdir, "%s_epsgeo%g.json" % (tag, m))
        cmd = [sys.executable, os.path.join(HERE, "certify.py"), node_path, "--s_rat", S_RAT,
               "--eps_geo", "%g" % m, "--rounds", "2", "--jobs", str(jobs), "--depth", str(depth),
               "--time_limit", str(cert_time), "--resolve_time", str(cert_time),
               "--out", cert_out, "--scale", "0", "--scale_cap", "1.40000",
               "--max_w", "32", "--loop_cols"]
        t0 = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True)
        with open(os.path.join(LOGS, "epsgeo_%s.log" % tag), "a") as f:
            f.write(p.stdout[-4000:] + "\n---\n")
        steps.append(dict(eps_geo=m, rc=p.returncode, seconds=round(time.time() - t0, 1)))
        if p.returncode == 0:
            open(cert_out + ".PASS", "w").write("ok")
            return dict(verdict="PASS", cert_path=cert_out, eps_geo_used=m, eps_geo=steps)
    return dict(verdict="FAIL(eps_geo retries exhausted) -> deepen", eps_geo=steps)


# ------------------------------------------------------------------ PHASE: zone cover
def build_cover(w=0.15, nth=8, a_min=0.34, cw=0.6, zone="interior"):
    from tree57 import cover
    rect = zones(S0F, cw)[zone]
    boxes, bad, grid = cover(rect, S0F, w, nth, a_min)
    return rect, boxes, bad, grid


def census(cond_names, w=0.15, nth=8, a_min=0.34, out=None, cond_boxes=None, zone="interior"):
    """classify the whole interior cover at conditioning depth j = len(cond_names).  Exact
    arithmetic only -- no LP is launched.  This IS the alive gate applied wholesale."""
    cond = list(cond_boxes) if cond_boxes is not None else [basin_box(n) for n in cond_names]
    budget = 6 - len(cond) - 1                          # YES child budget
    rect, boxes, bad, grid = build_cover(w, nth, a_min, zone=zone)
    rows, counts = [], dict(cover=len(boxes), uncoverable=len(bad), contradictory=0, parent=0,
                            shared=0, nocore=0, attemptable=0, unkillable=0)
    trump_boxes = 0
    Pl = {n: trump_deg(n) for n in FREE}
    for i, b in enumerate(boxes):
        g = gate(b, cond, [], budget, cond_names)
        counts[g["state"]] = counts.get(g["state"], 0) + 1
        hit = [n for n, (x, y, th) in Pl.items()
               if b.x0 - 1e-5 <= x <= b.x1 + 1e-5 and b.y0 - 1e-5 <= y <= b.y1 + 1e-5
               and b.th0 - 1e-4 <= th <= b.th1 + 1e-4]
        trump_boxes += 1 if hit else 0
        rows.append(dict(i=i, box=b.to_json(), state=g["state"], k=g["k"], fam=g["fam"],
                         hugs=g["hugs"], shares=g["shares"], trump_in_box=hit))
    res = dict(cond=list(cond_names), j=len(cond_names), zone=zone, child_budget=budget, rect=list(rect),
               grid=list(grid), counts=counts, boxes_with_a_trump_placement=trump_boxes,
               rows=rows)
    if out:
        json.dump(res, open(os.path.join(RES, out), "w"), indent=1)
    return res


def phase_cover(cond_names, shard="0/1", w=0.15, nth=8, a_min=0.34, lp_time=300.0,
                cert_time=240.0, wall=1e9, max_children=10 ** 9, tag_prefix=None):
    """P3/P4: kill every attemptable box of the interior cover at conditioning depth j."""
    j = len(cond_names)
    pref = tag_prefix or ("c%d" % j)
    si, sn = map(int, shard.split("/"))
    sink = Sink("a60_cover_j%d.jsonl" % j, "cover_j%d_s%d.log" % (j, si))
    init_warm()
    cen_path = os.path.join(RES, "a60_census_j%d.json" % j)
    cen = (json.load(open(cen_path)) if os.path.exists(cen_path)
           else census(cond_names, w, nth, a_min, out="a60_census_j%d.json" % j))
    cond = [basin_box(n) for n in cond_names]
    budget = cen["child_budget"]
    logline("A60 cover j=%d cond=%s budget=%d counts=%s shard=%s"
            % (j, cond_names, budget, json.dumps(cen["counts"]), shard))
    todo = [r for r in cen["rows"] if r["state"] == "attemptable"]
    mine = [r for i, r in enumerate(todo) if i % sn == si][:max_children]
    prog = os.path.join(PROG, "cover_j%d_s%d.json" % (j, si))
    st = dict(phase="cover", j=j, cond=list(cond_names), shard=shard, budget=budget,
              total=len(mine), attemptable_all=len(todo), counts=cen["counts"],
              done=0, passed=0, failed=0, alive=0, canary=0,
              started=time.strftime("%Y-%m-%d %H:%M:%S"))
    t0 = time.time()

    def flush():
        st["elapsed_s"] = round(time.time() - t0, 1)
        st["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
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
        rec = kill(sink, tag, b, cond, [], budget,
                   dict(kind="YES-cover", depth_j=j, pinguard="ok", a=float(b.core().a),
                        hugs=r["hugs"], k=r["k"], cond=list(cond_names), level=0),
                   lp_time=lp_time, cert_time=cert_time)
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
            ("j", "shard", "total", "done", "passed", "failed", "alive", "canary", "elapsed_s")}))
    return st


# ------------------------------------------------------------------ PHASE: residue ladder
def ladder_scan(cond_names, levels, w=0.15, nth=8, a_min=0.34, out=None, seed=None,
                stop_when_basin=True, refine_chain=False, cond_boxes=None, zone="interior"):
    """the EXACT part of the residue ladder: bisect only the unkillable boxes, re-run pinguard +
    the alive gate on every sub-box, keep the still-unkillable ones.  No LP.  Emits, per level,
    the residue statistics AND the list of newly attemptable sub-boxes (the kill queue)."""
    cond = list(cond_boxes) if cond_boxes is not None else [basin_box(n) for n in cond_names]
    j = len(cond)
    budget = 6 - j - 1
    if seed is not None:
        residue = [Box.from_json(d) for d in seed]
        chain = []
    else:
        cen_path = os.path.join(RES, "a60_census_j%d.json" % j)
        cen = (json.load(open(cen_path)) if (os.path.exists(cen_path) and cond_boxes is None)
               else census(cond_names, w, nth, a_min,
                           out=("a60_census_j%d.json" % j) if cond_boxes is None else None,
                           cond_boxes=cond_boxes, zone=zone))
        residue = [Box.from_json(r["box"]) for r in cen["rows"] if r["state"] == "unkillable"]
        chain = [(Box.from_json(r["box"]), r["shares"]) for r in cen["rows"]
                 if r["state"] == "shared"]
    hug = {}
    for b in residue:
        g = gate(b, cond, [], budget, cond_names)
        h_ = g["hugs"]
        hug[b.key()] = h_ if isinstance(h_, str) else (h_[0] if h_ else None)
    lv, out_levels = [], []
    for level in range(levels + 1):
        rad = max([box_radius(b) for b in residue], default=0.0)
        vol = sum(box_volume(b) for b in residue)
        gaps, inside, cont = [], 0, []
        for b in residue:
            hb = hug.get(b.key())
            if hb:
                gaps.append(sup_gap(b, hb))
                cont.append(sup_containment(b, hb))
                inside += 1 if sup_containment(b, hb) <= H else 0
        # (D)-chain bookkeeping: a 'shared' box is discharged into the conditioning core it
        # shares as soon as it lies inside that square's A36 basin slice.
        ch_open = [(b, nm) for (b, nm) in chain if sup_containment(b, nm) > H]
        rowl = dict(level=level, boxes=len(residue), volume=vol,
                    max_box_radius=rad, max_gap_to_trump=(max(gaps) if gaps else None),
                    max_containment=(max(cont) if cont else None),
                    inside_A36_basin=inside, all_inside=(inside == len(residue)),
                    chain_boxes=len(chain), chain_open=len(ch_open),
                    chain_discharged=len(chain) - len(ch_open))
        out_levels.append(rowl)
        lv.append((level, list(residue)))
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
                    h_ = g["hugs"]
                    h_ = h_ if isinstance(h_, str) else (h_[0] if h_ else None)
                    hug[sb.key()] = h_ or hb
                elif g["state"] == "attemptable":
                    queue.append(dict(box=sb.to_json(), k=g["k"], hugs=g["hugs"], level=level))
                elif g["state"] == "shared":
                    chain.append((sb, g["shares"]))
                # contradictory / parent: free, nothing to do
        nchain = []
        for (b, nm) in (ch_open if refine_chain else []):
            for sb in b.split():
                g = gate(sb, cond, [], budget, cond_names)
                if g["state"] == "shared":
                    nchain.append((sb, g["shares"]))
                elif g["state"] == "unkillable":
                    nxt.append(sb)
                    h_ = g["hugs"]
                    hug[sb.key()] = (h_ if isinstance(h_, str) else (h_[0] if h_ else None)) or nm
                elif g["state"] == "attemptable":
                    queue.append(dict(box=sb.to_json(), k=g["k"], hugs=g["hugs"], level=level))
        chain = ([(b, nm) for (b, nm) in chain if sup_containment(b, nm) <= H] + nchain
                 if refine_chain else chain)
        out_levels[-1]["kill_queue"] = len(queue)
        out_levels[-1]["queue"] = queue
        residue = nxt
    res = dict(cond=list(cond_names), j=j, budget=budget, levels=out_levels,
               cond_boxes=[b.to_json() for b in cond],
               final_residue=[b.to_json() for b in residue],
               final_chain=[[b.to_json(), nm] for (b, nm) in chain])
    if out:
        json.dump(res, open(os.path.join(RES, out), "w"), indent=1)
    return res, lv


def phase_ladder(cond_names, levels=26, shard="0/1", lp_time=300.0, cert_time=240.0,
                 wall=1e9, kill_queue=True, max_kills=10 ** 9):
    """P3/P5: run the residue ladder and kill every newly-attemptable sub-box it produces."""
    j = len(cond_names)
    si, sn = map(int, shard.split("/"))
    sink = Sink("a60_ladder_j%d.jsonl" % j, "ladder_j%d_s%d.log" % (j, si))
    if kill_queue:
        init_warm()
    scan_path = os.path.join(RES, "a60_ladder_j%d_scan.json" % j)
    if os.path.exists(scan_path):
        scan = json.load(open(scan_path))
    else:
        scan, _ = ladder_scan(cond_names, levels, out="a60_ladder_j%d_scan.json" % j)
    cond = ([Box.from_json(d) for d in scan["cond_boxes"]] if scan.get("cond_boxes")
            else [basin_box(n) for n in cond_names])
    budget = scan["budget"]
    prog = os.path.join(PROG, "ladder_j%d_s%d.json" % (j, si))
    queue = [(L["level"], i, q) for L in scan["levels"] for i, q in enumerate(L.get("queue", []))]
    mine = [x for i, x in enumerate(queue) if i % sn == si][:max_kills]
    st = dict(phase="ladder", j=j, cond=list(cond_names), shard=shard, budget=budget,
              levels=[{k: L[k] for k in L if k != "queue"} for L in scan["levels"]],
              total=len(mine), queue_all=len(queue), done=0, passed=0, failed=0, alive=0,
              started=time.strftime("%Y-%m-%d %H:%M:%S"))
    t0 = time.time()

    def flush():
        st["elapsed_s"] = round(time.time() - t0, 1)
        st["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        json.dump(st, open(prog, "w"), indent=1)

    flush()
    logline("A60 ladder j=%d levels=%d queue=%d shard=%s"
            % (j, len(scan["levels"]), len(queue), shard))
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
        rec = kill(sink, tag, b, cond, [], budget,
                   dict(kind="YES-ladder", depth_j=j, level=level, pinguard="ok",
                        a=float(b.core().a), hugs=q["hugs"], k=q["k"], cond=list(cond_names)),
                   lp_time=lp_time, cert_time=cert_time)
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
#
# G-A60-3.  The alive gate's 'attemptable' verdict only says the A57-3 obstruction is ABSENT
# (k is a lower bound on tau*, never an upper one -- A54 S0).  A box the gate calls attemptable
# can still come back `refused (tau >= budget)` or FAIL from the certifier, and such a box is
# NOT resolved: it must be bisected and re-processed at the SAME budget (A57 T11 -- a refinement
# of the same disjunction spends no budget).  Sub-boxes have a strictly larger rational core
# (a = (1/2 - hd)/(1 + dt) rises toward 1/2 as the box shrinks), which is what makes the retry
# worth anything.  This phase is what closes the gap between 'attemptable' and 'killed'.
def resisters(jsonl):
    """records that did not resolve: LP-alive at the node's resolution, or a failed certificate."""
    p = os.path.join(RES, jsonl)
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p):
        try:
            r = json.loads(line)
        except Exception:
            continue
        v = r.get("verdict", "")
        if (v.startswith("refused (tau") or v.startswith("FAIL")) and r.get("box"):
            out.append(r)
    return out


def phase_deepen(cond_names, source, rnd=1, shard="0/1", lp_time=300.0, cert_time=240.0,
                 wall=1e9, max_children=10 ** 9, cond_boxes=None):
    j = len(cond_names)
    si, sn = map(int, shard.split("/"))
    cond = (list(cond_boxes) if cond_boxes is not None
            else [basin_box(n) for n in cond_names])
    budget = 6 - len(cond) - 1
    src = resisters(source)
    sink = Sink("a60_deepen_j%d_r%d.jsonl" % (j, rnd), "deepen_j%d_r%d_s%d.log" % (j, rnd, si))
    init_warm()
    subs = []
    for r in src:
        b = Box.from_json(r["box"])
        for si_, sb in enumerate(b.split()):
            subs.append((r["tag"], si_, sb))
    mine = [x for i, x in enumerate(subs) if i % sn == si][:max_children]
    prog = os.path.join(PROG, "deepen_j%d_r%d_s%d.json" % (j, rnd, si))
    st = dict(phase="deepen", j=j, round=rnd, source=source, cond=list(cond_names), budget=budget,
              shard=shard, parents=len(src), total=len(mine), done=0, free=0, residue=0,
              passed=0, failed=0, alive=0, started=time.strftime("%Y-%m-%d %H:%M:%S"))
    t0 = time.time()

    def flush():
        st["elapsed_s"] = round(time.time() - t0, 1)
        st["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        json.dump(st, open(prog, "w"), indent=1)

    flush()
    logline("A60 deepen j=%d round=%d parents=%d sub-boxes=%d shard=%s"
            % (j, rnd, len(src), len(mine), shard))
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
            sink.put(dict(tag=tag, parent=ptag, verdict="KILL-BY-LOGIC" if g["state"] == "contradictory"
                          else "carried (%s)" % g["state"], state=g["state"], budget=budget,
                          box=sb.to_json(), depth_j=j, round=rnd,
                          ts=time.strftime("%Y-%m-%d %H:%M:%S")))
            st["free" if g["state"] == "contradictory" else "residue"] += 1
            st["done"] += 1
            flush()
            continue
        if g["state"] == "unkillable":
            sink.put(dict(tag=tag, parent=ptag, verdict="ALIVE-CERTIFIED (A57-3, k=%d>=budget %d)"
                          % (g["k"], budget), state=g["state"], k=g["k"], hugs=g["hugs"],
                          budget=budget, box=sb.to_json(), depth_j=j, round=rnd,
                          ts=time.strftime("%Y-%m-%d %H:%M:%S")))
            st["residue"] += 1
            st["done"] += 1
            flush()
            continue
        rec = kill(sink, tag, sb, cond, [], budget,
                   dict(kind="YES-deepen", depth_j=j, round=rnd, parent=ptag, pinguard="ok",
                        a=float(sb.core().a), hugs=g["hugs"], k=g["k"], cond=list(cond_names)),
                   lp_time=lp_time, cert_time=cert_time)
        v = (rec or {}).get("verdict", "")
        st["done"] += 1
        st["passed"] += 1 if v == "PASS" else 0
        st["failed"] += 1 if v.startswith("FAIL") else 0
        st["alive"] += 1 if v.startswith("refused") else 0
        flush()
    st["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    flush()
    logline("deepen done " + json.dumps({k: st[k] for k in
            ("j", "round", "shard", "total", "done", "free", "residue", "passed", "failed",
             "alive", "elapsed_s")}))
    return st


# ------------------------------------------------------------------ scoreboard
def scoreboard(out="a60_scoreboard.json"):
    """one consolidated per-phase scoreboard over every jsonl this campaign has written."""
    import collections
    board = {}
    for p in sorted(os.listdir(RES)):
        if not (p.startswith("a60_") and p.endswith(".jsonl")):
            continue
        c = collections.Counter()
        lp = ct = 0.0
        last = {}
        for line in open(os.path.join(RES, p)):
            try:
                r = json.loads(line)
            except Exception:
                continue
            last[r.get("tag")] = r          # A57 convention: last record per tag wins
        n = len(last)
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
        board[p] = dict(records=n, verdicts=dict(c), lp_s=round(lp, 1), cert_s=round(ct, 1),
                        kill_rate=(round(c["PASS"] / float(c["PASS"] + c["LP-alive"] +
                                                           c["cert-FAIL"]), 4)
                                   if (c["PASS"] + c["LP-alive"] + c["cert-FAIL"]) else None))
    prog = {}
    for p in sorted(os.listdir(PROG)):
        if p.endswith(".json"):
            try:
                prog[p] = json.load(open(os.path.join(PROG, p)))
            except Exception:
                pass
    res = dict(generated=time.strftime("%Y-%m-%d %H:%M:%S"), phases=board, progress=prog)
    json.dump(res, open(os.path.join(RES, out), "w"), indent=1)
    return res


# ------------------------------------------------------------------ cli
def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["census", "cover", "ladderscan", "ladder", "deepen",
                                    "board"])
    ap.add_argument("--cond", default="", help="comma list of conditioned Trump squares, in order")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--levels", type=int, default=26)
    ap.add_argument("--lp_time", type=float, default=300.0)
    ap.add_argument("--cert_time", type=float, default=240.0)
    ap.add_argument("--wall", type=float, default=1e9)
    ap.add_argument("--max_children", type=int, default=10 ** 9)
    ap.add_argument("--w", type=float, default=0.15)
    ap.add_argument("--nth", type=int, default=8)
    ap.add_argument("--a_min", type=float, default=0.34)
    ap.add_argument("--no_kill", action="store_true")
    ap.add_argument("--zone", default="interior")
    ap.add_argument("--source", default=None)
    ap.add_argument("--round", type=int, default=1)
    a = ap.parse_args()
    cond = [c for c in a.cond.split(",") if c]
    for c in cond:
        assert c in FREE, "unknown square " + c
    if a.cmd == "census":
        r = census(cond, a.w, a.nth, a.a_min, out="a60_census_j%d.json" % len(cond))
        print(json.dumps(dict(j=r["j"], cond=r["cond"], budget=r["child_budget"],
                              counts=r["counts"],
                              trump_boxes=r["boxes_with_a_trump_placement"]), indent=1))
    elif a.cmd == "cover":
        print(json.dumps(phase_cover(cond, a.shard, a.w, a.nth, a.a_min, a.lp_time,
                                     a.cert_time, a.wall, a.max_children), indent=1)[:2000])
    elif a.cmd == "ladderscan":
        r, _ = ladder_scan(cond, a.levels, a.w, a.nth, a.a_min,
                           out="a60_ladder_j%d_scan.json" % len(cond))
        print(json.dumps([{k: L[k] for k in L if k != "queue"} for L in r["levels"]], indent=1))
    elif a.cmd == "ladder":
        st = phase_ladder(cond, a.levels, a.shard, a.lp_time, a.cert_time, a.wall,
                          kill_queue=not a.no_kill, max_kills=a.max_children)
        print(json.dumps({k: st[k] for k in st if k != "levels"}, indent=1))
    elif a.cmd == "deepen":
        src = a.source or ("a60_cover_j%d.jsonl" % len(cond))
        st = phase_deepen(cond, src, a.round, a.shard, a.lp_time, a.cert_time, a.wall,
                          a.max_children)
        print(json.dumps(st, indent=1))
    elif a.cmd == "board":
        b = scoreboard()
        print(json.dumps(b["phases"], indent=1))


if __name__ == "__main__":
    cli()
