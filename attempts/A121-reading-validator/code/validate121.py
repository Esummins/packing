"""A121 - validate the PI's shadow readings and turn them into node cuts.

READ-ONLY on every campaign and attempt except attempts/A121-reading-validator/**.
Pure geometry: no LP, no solver.  The lane test is A118's `lanelib` verdict, read from
A118's frozen records (`results/lane_s{0,1}.jsonl`) -- the same corner frames, the same
a_w = 1, the same rho = 0, the same M(C) = ncond_pot.

T1  validate each reading against the entry's MINIMISED packing (right-panel frame):
      r  <sq> <cell>   the cell is met, open interior, by exactly the named square
      ns <sq> <cell>   the square sits a hair off the cell (SNAP; `*` = hypothesis square)
      i                incomplete support (< 11 squares) -> A115 warm re-solve queue
      g  <text>        a genuine grain (load path / shared tilt)
T2  map each validated reading to a cut in each explained node's OWN frame (through the
    node's stored `struct_op`, inverted), classify it, and run A118's lane test there.
T3  price the node kills that follow from the readings alone.

Incremental: a row is re-processed when its PI_reading text changes (sha1 in
results/state.json), or when --since <commit> says the CSV cell differs from that commit.

  python code/validate121.py                # rows whose reading changed since the last run
  python code/validate121.py --all          # every filled row
  python code/validate121.py --since HEAD~1 # rows whose reading differs from that commit
"""
import argparse
import collections
import csv
import glob
import hashlib
import io
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "code")
sys.path.insert(0, A118)

import blas1  # noqa: F401,E402   (must precede numpy: one BLAS thread)
import numpy as np  # noqa: E402
import lanelib as L  # noqa: E402
import corpus as CP  # noqa: E402

RES = os.path.join(BASE, "results")
NOTES = os.path.join(BASE, "notes")

CSV_PATH = os.path.join(ROOT, "docs", "shadows", "review.csv")
A107 = os.path.join(ROOT, "attempts", "A107-shadow-gallery", "results")
A118R = os.path.join(ROOT, "attempts", "A118-lane-count", "results")
A115R = os.path.join(ROOT, "attempts", "A115-k0-corner-rows", "results")

SHAT = 3.877083590022814
S0 = CP.S0

# ---- tolerances -----------------------------------------------------------------------
MEET = -1e-7        # SAT gap below this = genuine open-interior meet
GRAZE = 1e-7        # |gap| <= this = tangency/graze (A107 books contacts at gap < 1e-7)
SNAP_D = 0.05       # A107's snap position tolerance (shadowlib.snap dtol)
SNAP_A = 3.0        # A107's snap tilt tolerance, degrees (shadowlib.snap atol)
EXACT_D = 1e-5      # "already exactly on the cell": position, and
EXACT_A = 1e-3      #   tilt in degrees (the minimiser's own convergence scale)
NODE_COST_S = 850.0             # A118 price model: the tree's per-node decision cost
A99_L1_CPUH = (43.2, 100.3)     # A115 t4_report: A99 k0 frontier, per level-1 cell

D4_INV = {"e": "e", "r90": "r270", "r180": "r180", "r270": "r90",
          "mx": "mx", "my": "my", "diag": "diag", "anti": "anti"}


# ------------------------------------------------------------------ small geometry helpers
def tmod90(t_rad):
    """tilt reduced to [0, 45] degrees (distance to the nearest axis)."""
    q = math.pi / 2.0
    a = math.degrees(t_rad - q * math.floor(t_rad / q))
    return min(a, 90.0 - a)


def cellname(tok):
    """'br00' / 'BR(0,0)' -> 'BR(0,0)'."""
    tok = tok.strip()
    if "(" in tok:
        return tok.upper()
    return "%s(%s,%s)" % (tok[:2].upper(), tok[2], tok[3])


# A107 shadowlib.d4_ops, verbatim (the 8 elements of D4 on [0,s]^2, acting on (x, y, theta))
def d4_ops(s):
    return {
        "e":    lambda x, y, t: (x, y, t),
        "r90":  lambda x, y, t: (s - y, x, t),
        "r180": lambda x, y, t: (s - x, s - y, t),
        "r270": lambda x, y, t: (y, s - x, t),
        "mx":   lambda x, y, t: (s - x, y, -t),
        "my":   lambda x, y, t: (x, s - y, -t),
        "diag": lambda x, y, t: (y, x, -t),
        "anti": lambda x, y, t: (s - y, s - x, -t),
    }


def slot_cells(s, imax=4):
    """A107 shadowlib.slot_cells: named axis-aligned unit cells stacked into the corners."""
    out = {}
    for i in range(imax):
        for j in range(imax):
            out["BL(%d,%d)" % (i, j)] = (0.5 + i, 0.5 + j)
            out["BR(%d,%d)" % (i, j)] = (s - 0.5 - i, 0.5 + j)
            out["TL(%d,%d)" % (i, j)] = (0.5 + i, s - 0.5 - j)
            out["TR(%d,%d)" % (i, j)] = (s - 0.5 - i, s - 0.5 - j)
    return out


def cell_map(name, op):
    """Image of a named cell under a D4 op (name -> name; independent of the side)."""
    c, i, j = L.parse_cell(name)
    s = S0
    cx, cy = L.cell_centre(c, i, j, s)
    x, y, _ = d4_ops(s)[op](cx, cy, 0.0)
    best, bd = None, 1e9
    for nm, (px, py) in slot_cells(s).items():
        d = math.hypot(x - px, y - py)
        if d < bd:
            best, bd = nm, d
    assert bd < 1e-6, "cell %s under %s did not land on a named cell (%.2e)" % (name, op, bd)
    return best


def gap_to_cell(x, y, t, fr):
    return float(L.gap_pose_vs_core(np.array([[x, y]]), np.array([t]), L.cell_square(fr))[0])


def is_corner(name):
    c, i, j = L.parse_cell(name)
    return i == 0 and j == 0


# ------------------------------------------------------------------ the corpus
def load_entries():
    """id -> dict(kind, s, slots, free, analysis, ...) for both galleries."""
    out = {}
    for fn, kind in (("shadows_k0.json", "k0"), ("shadows.json", "S")):
        p = os.path.join(A107, fn)
        if not os.path.exists(p):
            continue
        for e in json.load(open(p)):
            e["kind"] = kind
            out[e["id"]] = e
    return out


def load_nodes_of_entry():
    out = {}
    for fn in ("shadow_nodes_k0.json", "shadow_nodes.json"):
        p = os.path.join(A107, fn)
        if os.path.exists(p):
            out.update(json.load(open(p)))
    return out


def load_struct_ops():
    """(src, nid) -> node record with struct_op, and idx -> (src, nid) per gallery set.

    `structs[*]['members']` in shadows*.json are indices into the corresponding extract
    file's `nodes` list, so the index map is what identifies the PRIMARY structure's nodes
    (the structure whose minimum is the drawn right panel)."""
    out, idx = {}, {}
    for fn in ("extract_k0.json", "extract.json"):
        p = os.path.join(A107, fn)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        setname = "k0" if fn == "extract_k0.json" else "pinned"
        for k, n in enumerate(d["nodes"]):
            if "struct_op" in n:
                out[(n["src"], n["nid"])] = n
            idx[(setname, k)] = (n["src"], n["nid"])
    return out, idx


def load_lane():
    """(src, nid) -> A118 lane record."""
    out = {}
    for p in sorted(glob.glob(os.path.join(A118R, "lane_s*.jsonl"))):
        for ln in open(p):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            out[(r["src"], r["nid"])] = r
    return out


def load_a115():
    """nid -> A115 T4 warm re-solve record; plus the plan's not-reached list."""
    recs = {}
    for p in glob.glob(os.path.join(A115R, "t4", "*.json")):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        recs[d.get("nid") or os.path.basename(p)[:-5]] = d
    summ = {}
    p = os.path.join(A115R, "t4_summary.json")
    if os.path.exists(p):
        summ = json.load(open(p))
    return recs, summ


# ------------------------------------------------------------------ the shorthand
def parse_reading(txt):
    """-> [dict(type, sq, cell, star, text)]; `;`-separated items inherit the last type."""
    items, typ = [], None
    for part in txt.split(";"):
        w = part.strip().split()
        if not w:
            continue
        if w[0].lower() in ("r", "ns", "i", "g"):
            typ = w[0].lower()
            w = w[1:]
        if typ is None:
            items.append(dict(type="?", sq=None, cell=None, star=False, text=part.strip()))
            continue
        if typ == "i":
            items.append(dict(type="i", sq=None, cell=None, star=False, text=part.strip()))
            continue
        if typ == "g":
            items.append(dict(type="g", sq=None, cell=None, star=False, text=" ".join(w)))
            continue
        if len(w) < 2:
            items.append(dict(type=typ, sq=None, cell=None, star=False,
                              text=part.strip(), parse_error="expected '<sq> <cell>'"))
            continue
        sq = w[0]
        star = "*" in sq
        items.append(dict(type=typ, sq=sq.replace("*", ""), cell=cellname(w[1]),
                          star=star, text=part.strip()))
    return items


def expand_squares(text):
    """'f0/1/3/4/5/6' -> ['f0','f1','f3','f4','f5','f6']; also plain 'f0 f1'."""
    out = []
    for tok in text.replace(",", " ").split():
        if "/" in tok and tok[0] in "fF":
            head = tok.split("/")[0]
            pre = head[0]
            out.append(head)
            for k in tok.split("/")[1:]:
                if k.isdigit():
                    out.append(pre + k)
        elif tok[0] in "fF" and tok[1:].isdigit():
            out.append(tok)
    return out


# ------------------------------------------------------------------ the minimised packing
def packing_of(e):
    """[(name, cx, cy, theta)] of the entry's minimised packing, right-panel frame."""
    s = e["s"]
    P = []
    for nm in e["slots"]:
        c, i, j = L.parse_cell(nm)
        cx, cy = L.cell_centre(c, i, j, s)
        P.append((nm, cx, cy, 0.0))
    for k, q in enumerate(e["free"]):
        P.append(("f%d" % k, float(q[0]), float(q[1]), float(q[2])))
    return s, P


def entry_audit(e, P, s):
    """Entry-level facts the readings depend on: which `free` squares of the minimised packing
    actually sit ON a named cell (so the gallery's slot/free split under-counts the slots), and
    the corner-cell occupancy of the drawn packing."""
    cells = slot_cells(s)
    on = []
    for (nm, x, y, t) in P:
        if not nm.startswith("f"):
            continue
        tilt = tmod90(t)
        if tilt > EXACT_A:
            continue
        best, bd = None, 1e9
        for cn_, (px, py) in cells.items():
            d = max(abs(x - px), abs(y - py))
            if d < bd:
                best, bd = cn_, d
        if bd <= EXACT_D:
            on.append(dict(sq=nm, cell=best, linf=bd, tilt_deg=tilt))
    corners = {}
    for cn_ in ("BL(0,0)", "BR(0,0)", "TR(0,0)", "TL(0,0)"):
        _, met, gz = occupancy(P, s, cn_)
        corners[cn_] = dict(met=[m["sq"] for m in met],
                            depths=[round(m["depth"], 6) for m in met],
                            grazers=[g["sq"] for g in gz])
    return dict(type="audit", text="(entry audit)", entry=e["id"], s_star=s, k=e["nsquares"],
                gallery_slots=e["slots"], gallery_nfree=e["nfree"],
                free_squares_on_named_cells=on,
                true_slot_count=len(e["slots"]) + len(on),
                corner_occupancy=corners, flags=(
                    ["? the gallery calls this %d slot + %d free, but %d of the free squares sit"
                     " exactly on named cells (%s): the true split is %d slot + %d free"
                     % (len(e["slots"]), e["nfree"], len(on),
                        ", ".join("%s@%s" % (o["sq"], o["cell"]) for o in on),
                        len(e["slots"]) + len(on), e["nfree"] - len(on))] if on else []))


def occupancy(P, s, cell):
    """Who meets / grazes the OPEN cell, with SAT gaps and corner-frame depths."""
    c, i, j = L.parse_cell(cell)
    fr = L.frame(c, i, j, s)
    met, graze = [], []
    for (nm, x, y, t) in P:
        g = gap_to_cell(x, y, t, fr)
        if g < MEET:
            mu = float(L.mu_many([[x, y]], [t], fr)[0])
            # the corner-frame depth d = max(0, 1 - mu) is the SLOT depth only where Lemma CONT
            # holds (Q misses R_p); otherwise mu is small because Q sits in the arm, not deep in
            # the cell, and the honest local measure is the SAT penetration |gap|.
            cont = all(float(L.mu_many([[x, y]], [t], gfr)[0]) >= -1e-9
                       for gfr in L.cont_frames(fr, 0.0))
            met.append(dict(sq=nm, gap=g, depth=max(0.0, 1.0 - mu), mu=mu,
                            penetration=-g, cont=bool(cont)))
        elif abs(g) <= GRAZE:
            graze.append(dict(sq=nm, gap=g))
    return fr, met, graze


# ------------------------------------------------------------------ T1
def validate_item(e, P, s, it, cls):
    """One reading item against the minimised packing.  Returns the T1 record."""
    rec = dict(type=it["type"], sq=it["sq"], cell=it["cell"], star=it["star"],
               text=it["text"], flags=[])
    if it.get("parse_error"):
        rec["flags"].append("? parse: " + it["parse_error"])
        return rec

    if it["type"] == "i":
        k = e["nsquares"]
        rec.update(k=k, nslot=len(e["slots"]), nfree=e["nfree"], s=s)
        if k >= 11:
            rec["flags"].append("? support is COMPLETE: k = %d squares, not < 11" % k)
        return rec

    if it["type"] == "g":
        sqs = expand_squares(it["text"])
        tilts = {}
        for nm in sqs:
            q = dict((n, (x, y, t)) for n, x, y, t in P).get(nm)
            if q is None:
                rec["flags"].append("? %s is not a square of this entry" % nm)
                continue
            tilts[nm] = tmod90(q[2])
        # tilts_deg = distance to the NEAREST axis (0-45); tilts_mod90 = A107's convention (0-90)
        rec["tilts_deg"] = {k: round(v, 6) for k, v in tilts.items()}
        rec["tilts_mod90_deg"] = {}
        for nm in tilts:
            q = dict((n, (x, y, t)) for n, x, y, t in P)[nm][2]
            rec["tilts_mod90_deg"][nm] = round(
                math.degrees(q - (math.pi / 2) * math.floor(q / (math.pi / 2))), 6)
        if len(tilts) >= 2:
            spread = max(tilts.values()) - min(tilts.values())
            rec["tilt_spread_deg"] = spread
            rec["shared_tilt"] = bool(spread <= 0.5)
            if spread > 0.5:
                rec["flags"].append("? tilt spread %.4f deg over %s -- not a shared tilt"
                                    % (spread, "/".join(sorted(tilts))))
        an = e.get("analysis") or {}
        res = an.get("resultant") or {}
        force = collections.defaultdict(float)
        for k, v in res.items():
            for side in k.split("|"):
                force[side.strip()] += float(v)
        rec["fj_force"] = {nm: round(force.get(nm, 0.0), 8) for nm in tilts}
        rec["loaded"] = e.get("loaded", [])
        rec["contacts"] = [[c["a"], c["b"], c["kind"], c["gap"]] for c in an.get("contacts", [])]
        zero = [nm for nm in tilts if force.get(nm, 0.0) <= 1e-6]
        if zero:
            rec["flags"].append("? %s carry NO Fritz-John force (resultant 0) -- in the grain "
                                "but not on the load path" % ",".join(sorted(zero)))
        rat = {r["removed"]: r for r in (e.get("rattlers") or [])}
        rec["rattler_role"] = {nm: rat[nm]["role"] for nm in tilts if nm in rat}
        rec["rattler_drop"] = {nm: rat[nm]["drop"] for nm in tilts if nm in rat}
        rec["kkt_residual"] = an.get("kkt_residual")
        rec["rank"] = an.get("rank")
        rec["nrows"] = an.get("nrows")
        rec["flexes_fixed_s"] = an.get("flexes_fixed_s")
        if (an.get("kkt_residual") or 0.0) > 1e-6:
            rec["flags"].append("? this entry's Fritz-John decomposition does NOT close "
                                "(kkt_residual = %.4g, rank %s of %s rows): the multipliers "
                                "below are an nnls least-squares fit, not a certified load path"
                                % (an["kkt_residual"], an.get("rank"), an.get("nrows")))
        for nm in sorted(zero):
            if nm in rat and rat[nm]["role"] == "load-bearing":
                rec["flags"].append("  (but the rattler test calls %s LOAD-BEARING: removing it "
                                    "drops s by %.5f -- FJ and the rattler test disagree on %s)"
                                    % (nm, rat[nm]["drop"], nm))
        rec["a116_stability"] = ("not applicable (A116's stability radii cover S02/S07 only; "
                                 "this is %s)" % e["id"])
        return rec

    # r / ns -------------------------------------------------------------------------
    D = dict((n, (x, y, t)) for n, x, y, t in P)
    if it["sq"] not in D:
        rec["flags"].append("? %s is not a square of this entry (has %s)"
                            % (it["sq"], ", ".join(n for n, _, _, _ in P)))
        return rec
    x, y, t = D[it["sq"]]
    c, i, j = L.parse_cell(it["cell"])
    fr, met, graze = occupancy(P, s, it["cell"])
    cx, cy = L.cell_centre(c, i, j, s)
    linf = max(abs(x - cx), abs(y - cy))
    tilt = tmod90(t)
    mu = float(L.mu_many([[x, y]], [t], fr)[0])
    rec.update(s=s, cell_centre=[cx, cy], pose=[x, y, math.degrees(t)],
               linf=linf, tilt_mod90_deg=tilt, mu=mu, depth=max(0.0, 1.0 - mu),
               met=met, grazers=graze,
               corner=is_corner(it["cell"]),
               usable=it["cell"] in CP.CLASSES.get(cls, {}).get("usable", {}),
               extension=CP.CLASSES.get(cls, {}).get("usable", {}).get(it["cell"]))
    others = [m for m in met if m["sq"] != it["sq"]]
    rec["others"] = others
    rec["cell_singly_met"] = (len(met) == 1 and met[0]["sq"] == it["sq"])
    rec["cell_unmet_by_others"] = (len(others) == 0)

    if not any(m["sq"] == it["sq"] for m in met):
        g = gap_to_cell(x, y, t, fr)
        rec["flags"].append("? %s does NOT meet the open cell %s (SAT gap %+.3e)"
                            % (it["sq"], it["cell"], g))
    for m in others:
        d = (", corner-frame depth %.4f" % m["depth"]) if (rec["corner"] and m["cont"]) else \
            (", corner-frame depth %.4f NOT a slot depth here (Lemma CONT does not hold: "
             "%s sits in the arm R_p)" % (m["depth"], m["sq"]))
        rec["flags"].append("? %s is ALSO met by %s (SAT penetration %.4f%s) -- crowd, not room"
                            % (it["cell"], m["sq"], m["penetration"], d))
    if it["type"] == "ns":
        # Lemma SNAP-D needs the cell otherwise unmet; the shell bound prices the grazers.
        eps = linf + 0.5 - 1.0 / (2.0 * (abs(math.cos(t)) + abs(math.sin(t))))
        rec["snap_eps"] = eps
        rec["shell_bound"] = (1.0 + math.sqrt(2.0)) * eps
        rec["snap_applies"] = bool(rec["cell_unmet_by_others"])
        if linf > SNAP_D:
            rec["flags"].append("? %s is %.4f from the centre of %s (L-inf), not 'a hair' "
                                "(A107 snap tolerance %.2f)" % (it["sq"], linf, it["cell"], SNAP_D))
        if tilt > SNAP_A:
            rec["flags"].append("? %s tilt %.3f deg off axis (A107 snap tolerance %.1f deg)"
                                % (it["sq"], tilt, SNAP_A))
        rec["already_on_cell"] = bool(linf <= EXACT_D and tilt <= EXACT_A)
        if rec["already_on_cell"]:
            rec["snap_vacuous"] = True
            rec["flags"].append("? %s sits EXACTLY on %s (L-inf %.2e, tilt %.2e deg): already "
                                "snapped, not near-snapped -- the SNAP move is the identity and "
                                "the entry's slot/free split under-counts the slot squares"
                                % (it["sq"], it["cell"], linf, tilt))
        # Lemma SHELL (flood_lemma 1.3) prices the second meeter's depth only at a CORNER cell
        # or an unclipped completable slot of a PINNED class -- k0_00 has no pins, so the bound
        # is quoted only at the four corner cells.
        if rec["corner"]:
            for m in others:
                if m["cont"] and m["depth"] <= rec["shell_bound"]:
                    rec["flags"].append("  (SHELL: the second meeter %s has depth %.4f <= "
                                        "(1+sqrt2)eps = %.4f -- a grazer, per flood_lemma 1.3)"
                                        % (m["sq"], m["depth"], rec["shell_bound"]))
    return rec


# ------------------------------------------------------------------ T2
def cut_kind(cls, cell, typ, star, corner):
    if typ == "i":
        return "d", "warm re-solve (< 11 squares)"
    usable = CP.CLASSES.get(cls, {}).get("usable", {})
    if cls == "k0_00":
        if corner:
            if typ == "ns" and star:
                return "c", "SNAP of the node's own hypothesis square into a corner cell"
            return "a", "K0-FREE teleport of a FREE square into a corner cell (-> k1_00)"
        return "none", ("cell %s is not a usable cell of k0_00 (only the four corner cells "
                        "have a certified/OPEN extension); no teleport lemma applies" % cell)
    if cell in usable:
        if typ == "ns" and star:
            return "c", "SNAP of the node's own hypothesis square into a usable slot"
        return "b", "SLOT-CROWD teleport into usable slot %s (extension %s)" % (cell, usable[cell])
    return "none", "cell %s is not a usable slot of %s" % (cell, cls)


def lane_at(lrec, cell):
    if lrec is None:
        return None
    for c in lrec.get("cells", []):
        if c["cell"] == cell:
            return c
    return None


# ------------------------------------------------------------------ driver
def sha(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def read_csv_readings(text):
    rows = {}
    for row in csv.DictReader(io.StringIO(text)):
        sid = (row.get("shadow") or "").strip()
        if sid:
            rows[sid] = row
    return rows


def git_show(commit, path):
    try:
        return subprocess.check_output(["git", "show", "%s:%s" % (commit, path)],
                                       cwd=ROOT, stderr=subprocess.DEVNULL).decode("utf-8")
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=CSV_PATH)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--since", default="")
    ap.add_argument("--only", default="", help="comma-separated entry ids")
    a = ap.parse_args()

    os.makedirs(RES, exist_ok=True)
    os.makedirs(NOTES, exist_ok=True)
    text = open(a.csv, encoding="utf-8").read()
    rows = read_csv_readings(text)
    filled = {k: (v.get("PI_reading") or "").strip() for k, v in rows.items()}
    filled = {k: v for k, v in filled.items() if v}

    statep = os.path.join(RES, "state.json")
    state = json.load(open(statep)) if os.path.exists(statep) else {}
    prev = {}
    if a.since:
        old = git_show(a.since, os.path.relpath(a.csv, ROOT).replace("\\", "/"))
        if old is None:
            print("WARNING --since %s: cannot read the CSV at that commit; using state.json"
                  % a.since)
        else:
            prev = {k: (v.get("PI_reading") or "").strip()
                    for k, v in read_csv_readings(old).items()}

    todo = []
    for sid, txt in sorted(filled.items()):
        if a.only and sid not in a.only.split(","):
            continue
        if a.all:
            todo.append(sid)
        elif a.since and prev:
            if prev.get(sid, "") != txt:
                todo.append(sid)
        elif state.get(sid) != sha(txt):
            todo.append(sid)
    print("filled rows: %d;  to process: %d  %s" % (len(filled), len(todo), todo), flush=True)

    entries = load_entries()
    nodes_of = load_nodes_of_entry()
    sops, nidx = load_struct_ops()
    lane = load_lane()
    a115, a115sum = load_a115()
    not_reached = set(a115sum.get("not_reached", []))

    readings, cuts = [], []
    for sid in todo:
        e = entries.get(sid)
        if e is None:
            readings.append(dict(entry=sid, error="no A107 gallery entry"))
            continue
        cls = "k0_00" if e["kind"] == "k0" else None
        s, P = packing_of(e)
        items = parse_reading(filled[sid])
        ns = nodes_of.get(sid, [])
        setname = "k0" if e["kind"] == "k0" else "pinned"
        prim_members, prim_gk = None, None
        if e.get("structs"):
            prim = max(e["structs"], key=lambda d: d["nnodes"])
            prim_gk = prim["gk"]
            prim_members = set()
            for m in (prim.get("members") or []):
                k = nidx.get((setname, m))
                if k:
                    prim_members.add(k)

        aud = entry_audit(e, P, s)
        aud["reading"] = filled[sid]
        readings.append(aud)

        for it in items:
            v = validate_item(e, P, s, it, cls)
            v.update(entry=sid, s_star=s, nodes_explained=len(ns), reading=filled[sid])
            readings.append(v)
            if it["type"] == "g":
                continue

            kind, why = cut_kind(cls, it["cell"] or "", it["type"], it["star"],
                                 v.get("corner", False))
            for nd in ns:
                key = (nd["src"], nd["nid"])
                so = sops.get(key)
                op = so.get("struct_op") if so else None
                ncell = cell_map(it["cell"], D4_INV[op]) if (op and it["cell"]) else None
                lr = lane.get(key)
                lc = lane_at(lr, ncell) if ncell else None
                lane_ub = lc.get("lane_ub") if lc else None
                M = lc.get("ncond_pot") if lc else None
                node_kill = bool(lc and lane_ub is not None and M is not None
                                 and lane_ub + M <= 1)
                row = dict(entry=sid, reading_type=it["type"], reading=it["text"],
                           shadow_cell=it["cell"], shadow_square=it["sq"], star=it["star"],
                           src=nd["src"], nid=nd["nid"], shard=nd.get("shard"),
                           level=nd.get("level"), cls=cls, tau=nd.get("tau"),
                           budget=nd.get("budget"),
                           struct_op=op, node_cell=ncell,
                           in_primary_struct=(key in prim_members)
                           if prim_members is not None else None,
                           primary_gk=prim_gk,
                           cut_kind=kind, cut_why=why,
                           reading_ok=(not [f for f in v["flags"] if f.startswith("?")]),
                           lane_verdict=(lc or {}).get("verdict"),
                           lane_ub=lane_ub, M=M,
                           node_kill=node_kill,
                           lane_at_other_corners=None, a115=None)
                if lr and cls == "k0_00":
                    row["lane_at_other_corners"] = {
                        c["cell"]: dict(verdict=c["verdict"], M=c["ncond_pot"],
                                        kill=bool(c.get("lane_ub") is not None
                                                  and c["ncond_pot"] is not None
                                                  and c["lane_ub"] + c["ncond_pot"] <= 1))
                        for c in lr.get("cells", []) if c["cell"] != ncell}
                    row["node_killed_at_some_corner"] = bool(lr.get("kill"))
                if it["type"] == "i":
                    r = a115.get(nd["nid"])
                    if r is not None:
                        row["a115"] = dict(verdict=r.get("verdict"), eta=r.get("eta"),
                                           tau=r.get("tau"), budget=r.get("budget"),
                                           converged=r.get("converged"),
                                           minmass=r.get("minmass"))
                    elif nd["nid"] in not_reached:
                        row["a115"] = dict(verdict="NOT REACHED (A115 T4 queue)")
                    else:
                        row["a115"] = dict(verdict="not in A115's T4 queue (%s campaign)"
                                                   % nd["src"])
                cuts.append(row)
        state[sid] = sha(filled[sid])

    # ---- merge into the jsonl outputs (replace every row of a re-processed entry) --------
    def merge(path, new, keyf):
        old = []
        if os.path.exists(path):
            for ln in open(path, encoding="utf-8"):
                try:
                    old.append(json.loads(ln))
                except Exception:
                    pass
        touched = set(keyf(r) for r in new)
        keep = [r for r in old if keyf(r) not in touched]
        with open(path, "w", encoding="utf-8") as fh:
            for r in keep + new:
                fh.write(json.dumps(r) + "\n")
        return keep + new

    allread = merge(os.path.join(RES, "readings.jsonl"), readings, lambda r: r.get("entry"))
    allcuts = merge(os.path.join(RES, "cuts.jsonl"), cuts, lambda r: r.get("entry"))
    json.dump(state, open(statep, "w"), indent=1)

    summary = summarise(allread, allcuts, entries, nodes_of)
    json.dump(summary, open(os.path.join(RES, "summary.json"), "w"), indent=1)
    write_report(allread, allcuts, summary)
    print(json.dumps(summary["headline"], indent=1))
    print("wrote results/{readings,cuts}.jsonl, results/summary.json, notes/report.md")


def summarise(readings, cuts, entries, nodes_of):
    per_type = collections.defaultdict(lambda: dict(
        items=0, entries=set(), nodes=set(), cut_nodes=set(), kills=set(),
        no_cut=set(), m1_blocked=set(), undecided=set(), disagreements=0))
    for r in readings:
        t = r.get("type", "?")
        d = per_type[t]
        d["items"] += 1
        d["entries"].add(r.get("entry"))
        d["disagreements"] += len([f for f in r.get("flags", []) if f.startswith("?")])
    for c in cuts:
        d = per_type[c["reading_type"]]
        k = (c["src"], c["nid"])
        d["nodes"].add(k)
        if c["cut_kind"] == "none":
            d["no_cut"].add(k)
            continue
        d["cut_nodes"].add(k)
        if c["reading_type"] == "i":
            continue
        if c["node_kill"]:
            d["kills"].add(k)
        elif c["lane_ub"] is not None:
            d["m1_blocked"].add(k)
        else:
            d["undecided"].add(k)

    table = {}
    for t, d in per_type.items():
        table[t] = dict(items=d["items"], entries=sorted(x for x in d["entries"] if x),
                        nodes_explained=len(d["nodes"]), nodes_with_a_cut=len(d["cut_nodes"]),
                        nodes_no_cut=len(d["no_cut"]),
                        node_kills=len(d["kills"]),
                        lane_le1_blocked_by_M=len(d["m1_blocked"]),
                        lane_ge2_or_undecided=len(d["undecided"]),
                        disagreements=d["disagreements"])

    kills = set()
    for c in cuts:
        if c.get("node_kill"):
            kills.add((c["src"], c["nid"], c["level"], c["cls"]))
    # what the blanket A118 scan already had, at some other corner
    already = set()
    for c in cuts:
        if c.get("node_killed_at_some_corner") and not c.get("node_kill"):
            already.add((c["src"], c["nid"]))

    # attribution against A118's blanket scan: a reading-directed kill is NEW only if A118's
    # own 4-cell sweep of that node did not already book it.
    a118_kills = set()
    p = os.path.join(A118R, "report118.json")
    if os.path.exists(p):
        for k in json.load(open(p)).get("kills", []):
            a118_kills.add((k["key"].split("/")[0], k["key"].split("/")[-1]))
    new_kills = sorted("%s/%s" % (k[0], k[1]) for k in kills
                       if (k[0], k[1]) not in a118_kills)
    entry_nodes = set()
    for c in cuts:
        entry_nodes.add((c["src"], c["nid"]))
    a118_in_batch = sorted("%s/%s" % k for k in a118_kills if k in entry_nodes)

    by_cls_level = collections.Counter((k[3], "L%s" % k[2]) for k in kills)
    a99_l1 = len([k for k in kills if k[0] == "A99" and k[2] == 1])
    cpu_h = len(kills) * NODE_COST_S / 3600.0
    frontier = (a99_l1 * A99_L1_CPUH[0], a99_l1 * A99_L1_CPUH[1])

    disag = [dict(entry=r["entry"], type=r["type"], item=r.get("text"), flags=r["flags"])
             for r in readings if [f for f in r.get("flags", []) if f.startswith("?")]]
    return dict(headline=dict(
        rows=len(set(r["entry"] for r in readings if r.get("entry"))),
        reading_items=len(readings),
        node_cuts=len(cuts),
        node_kills_from_readings=len(kills),
        node_kills_by_class_level={"%s/%s" % k: v for k, v in by_cls_level.items()},
        cpu_h_at_850s=round(cpu_h, 3),
        a99_level1_kills=a99_l1,
        a99_frontier_cpu_h=[round(frontier[0], 1), round(frontier[1], 1)],
        nodes_killed_elsewhere_by_A118=len(already),
        new_node_kills=len(new_kills),
        new_cpu_h=round(len(new_kills) * NODE_COST_S / 3600.0, 3),
        a118_kills_among_these_nodes=len(a118_in_batch),
        disagreements=len(disag)),
        per_type=table, disagreements=disag,
        kills=sorted("%s/%s" % (k[0], k[1]) for k in kills),
        new_kills=new_kills, a118_kills_among_these_nodes=a118_in_batch,
        killed_elsewhere=sorted("%s/%s" % k for k in already))


def write_report(readings, cuts, summary):
    L_ = []
    h = summary["headline"]
    L_.append("# A121 - reading validator: per-batch table\n")
    L_.append("Generated by `code/validate121.py`; re-runs incrementally on changed rows.\n")
    L_.append("## T3 - what it is worth\n")
    L_.append("%d node kills from the readings alone (no LP) = %.2f CPU-h at 850 s/node, of "
              "which **%d are NEW** (%.2f CPU-h) -- the other %d are already booked by A118's "
              "blanket 4-corner sweep. %d of the kills are A99 k0 level-1 cells, worth "
              "%.1f-%.1f CPU-h off A99's frontier (conditional on k1_00). A118 kills %d of the "
              "nodes in this batch; the readings point at the killing cell for %d of them and "
              "at a non-killing corner for %d.\n"
              % (h["node_kills_from_readings"], h["cpu_h_at_850s"], h["new_node_kills"],
                 h["new_cpu_h"], h["node_kills_from_readings"] - h["new_node_kills"],
                 h["a99_level1_kills"], h["a99_frontier_cpu_h"][0], h["a99_frontier_cpu_h"][1],
                 h["a118_kills_among_these_nodes"], h["node_kills_from_readings"],
                 h["nodes_killed_elsewhere_by_A118"]))
    L_.append("\n## T2 - per reading type\n")
    L_.append("| type | items | entries | nodes explained | nodes with a cut | node kills | "
              "LANE<=1 blocked by M | LANE>=2 / undecided | no cut | disagreements |")
    L_.append("|---|---|---|---|---|---|---|---|---|---|")
    for t, d in sorted(summary["per_type"].items()):
        if t == "audit":
            continue
        L_.append("| `%s` | %d | %s | %d | %d | %d | %d | %d | %d | %d |"
                  % (t, d["items"], " ".join(d["entries"]), d["nodes_explained"],
                     d["nodes_with_a_cut"], d["node_kills"], d["lane_le1_blocked_by_M"],
                     d["lane_ge2_or_undecided"], d["nodes_no_cut"], d["disagreements"]))
    irows = [c for c in cuts if c["reading_type"] == "i"]
    if irows:
        L_.append("\n## T2(d) - the `i` rows against A115's warm re-solve queue\n")
        L_.append("| entry | k | node | src | level | A115 T4 verdict | eta | minmass |")
        L_.append("|---|---|---|---|---|---|---|---|")
        kof = {}
        for r in readings:
            if r.get("type") == "i":
                kof[r["entry"]] = r.get("k")
        for c in sorted(irows, key=lambda c: (c["entry"], c["nid"])):
            a = c.get("a115") or {}
            L_.append("| %s | %s | `%s` | %s | L%s | %s | %s | %s |"
                      % (c["entry"], kof.get(c["entry"]), c["nid"], c["src"], c["level"],
                         a.get("verdict", "-"),
                         ("%+.4g" % a["eta"]) if a.get("eta") is not None else "-",
                         ("%.3f" % a["minmass"]) if a.get("minmass") is not None else "-"))

    L_.append("\n## T1 - disagreements (`?` rows the PI wants re-drawn)\n")
    for d in summary["disagreements"]:
        L_.append("* **%s** `%s` (%s)" % (d["entry"], d["item"], d["type"]))
        for f in d["flags"]:
            L_.append("  * %s" % f)
    open(os.path.join(NOTES, "report.md"), "w", encoding="utf-8").write("\n".join(L_) + "\n")


if __name__ == "__main__":
    main()
