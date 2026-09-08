"""A136 -- the F-COVER wrapper: NO zones rounded INWARD, ZONE subset BOX checked on the WRITTEN
rationals, at emission.

WHY (A126 finding F-COVER, specified in attempts/A133-tan-half-emission/notes/fcover.md).
A120's cover

    node  =  YES  u  NO_1 u ... u NO_|L|                                        (a tautology)
    YES   =  node & (for every i, some square's pose is in BOX_i)
    NO_i  =  node & (no square's pose is in BOX_i)

is discharged in Lean by `LocalCompose.node_dead_of_yes_no`, whose NO hypothesis is
`~ NoneIn (Ls.get i) z` -- about the BOX.  What a `case-measure-certificate-v1` proves is about
the ZONE it writes into `hypotheses.nofams`.  The bridge is

    NoneIn BOX z  ->  NoneIn ZONE z          i.e.   ZONE subset BOX  (as pose sets),

which is exactly the shape of `LocalCompose.noneIn_of_clamped` applied with `B' := BOX`,
`B := ZONE` (its `ht0 : B'.t0 <= B.t0`, `ht1 : B.t1 <= B'.t1` are `BOX.t0 <= ZONE.t0` and
`ZONE.t1 <= BOX.t1`, and its two centre clauses hold as soon as `ZONE` is inside `BOX` -- the
`max .. (1/2)` / `min .. (s - 1/2)` slack is A120's clamp, free by `centre_in_slab`).

A112's `caselp.make_certificate` writes the zone rounded OUTWARD (`t_lo`/`t_hi` = floor/ceil
-/+ one unit of 2^-24, `q` = nearest at 1e-9), so ZONE is up to 1.19e-7 in `t` and 5e-10 in the
centre OUTSIDE the box, and the containment -- hence the tautology -- fails on the written
rationals.  A120's own A6 guard compared the zone to the box BEFORE the rounding, which is why it
passed while the emitted certificates did not satisfy the containment.

WHAT THIS MODULE DOES.  `narrow()` post-processes the certificate dict `make_certificate` returns,
BEFORE it is written:

  * every NO-zone bound is re-derived from the EXACT zone (the node record's `hyp.nofams`, which
    A120 builds at full precision) and rounded INWARD to the same denominators -- lower bounds up,
    upper bounds down, each t-interval narrowed at both ends;
  * the BOX the YES side names is written into the certificate too (new key
    `hypotheses.nofam_boxes`), rounded INWARD as well.

    INWARD IS THE SOUND DIRECTION FOR THE BOX, and it is the one place this module departs from
    the letter of the A136 brief ("the YES box bounds outward").  The YES leaf is killed by
    "for every i, some square's pose is in BOX_i implies A116's hypothesis for N".  Shrinking
    BOX_i STRENGTHENS that hypothesis (a pose in the smaller box is a pose in A119's box), so the
    YES kill survives; WIDENING BOX_i would put poses outside A119's certified box into the YES
    hypothesis and would move the 1e-7 defect from the NO side to the YES side, where nothing
    would catch it.  Widening would also endanger A120's A2/A3 pose-disjointness.  The residual
    Lean obligation of the inward box is the antitonicity of `LocalDead` in the box list
    (a smaller box list is a stronger YES hypothesis); it is recorded in notes/fcover136.md.

  * the zone is then intersected with the written box, so `ZONE subset BOX` holds BY
    CONSTRUCTION; intersecting only shrinks the zone, which only WEAKENS the NO hypothesis;
  * the decidable check `zone_sub_box` is run on the WRITTEN rationals and RAISES on failure
    (`FCoverError`).  It is the same finite rational predicate the Lean side will `decide`.

A t-interval that would become empty under the narrowing is DROPPED, not emitted reversed
(dropping weakens the NO hypothesis further).  It cannot happen at A120's resolutions: the
narrowest measured t-interval is 8.75e-2, six orders of magnitude above the 2^-24 grid.

READ-ONLY on A112/A116/A119/A120/A126/A133: nothing there is edited or copied; A112's own
rounding helpers are IMPORTED so the denominators are identical by construction.
"""
from __future__ import annotations

import json, math, os, subprocess, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))

A112C = os.path.join(ROOT, "attempts", "A112-dual-branching", "code")
A120C = os.path.join(ROOT, "attempts", "A120-no-side-runner", "code")
A57C = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
for _p in (A112C, A57C):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1  # noqa: E402,F401   MUST precede numpy

# A112's OWN rounding helpers and grids -- imported, never re-typed, so the outward direction and
# the denominators are identical by construction.
from caselp import TDEN, XDEN, t_of_deg, q as q_near, q_up, t_lo as t_out_lo, t_hi as t_out_hi  # noqa: E402

RES = os.path.join(BASE, "results")
NODES = os.path.join(RES, "nodes")
CERTS = os.path.join(BASE, "certs")
LOGS = os.path.join(BASE, "logs")
PROG = os.path.join(BASE, "progress")
for _d in (RES, NODES, CERTS, LOGS, PROG):
    os.makedirs(_d, exist_ok=True)

VERIFY_CASE = os.path.join(A112C, "verify_case.py")
VERIFY_CASE_SHA = "521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af"
FCOVER_TAG = ("F-COVER fixed: NO zone rounded INWARD and intersected with the written box; "
              "ZONE subset BOX verified on the written rationals (A136 a136lib.narrow)")


class FCoverError(AssertionError):
    """The written zone is not inside the written box.  Never swallowed."""


# ---------------------------------------------------------------- inward rounding helpers
def q_dn(x):
    """float -> rational <= x at 1/XDEN (the mirror of caselp.q_up, which is ceil + 1)."""
    return Fr(math.floor(x * XDEN) - 1, XDEN)


def t_in_lo(th):
    """rational t >= tan(th/2): the INWARD mirror of caselp.t_lo."""
    return Fr(math.ceil(t_of_deg(th) * TDEN) + 1, TDEN) if th > 0 else Fr(0)


def t_in_hi(th):
    """rational t <= tan(th/2): the INWARD mirror of caselp.t_hi."""
    return Fr(math.floor(t_of_deg(th) * TDEN) - 1, TDEN) if th < 90 else Fr(1)


def rat_box(x0, x1, y0, y1, thetas, clamps=()):
    """A float box (thetas in DEGREES, a list of closed intervals already reduced mod 90) written
    as rationals rounded INWARD on every bound -- the written object is a SUBSET of the float one.
    Empty t-intervals are dropped.

    `clamps` is a list of (float value, exact Fraction) pairs for bounds that were produced by
    A120's CLAMP to the admissible strip rather than by the box itself.  Those bounds are EXACTLY
    rational (`1/2` and `s - 1/2`, and `s` is exactly `969271/250000`), so rounding them inward
    would shave a sliver off the zone AT THE WALL for no reason -- and that sliver is not
    exempt, not coverable at the verifier's depth, and is precisely what made every `BR(0,1)`
    (`NO3`) certificate FAIL in the first T1 pass.  Writing the clamp exactly is sound: the
    Lean bridge (`LocalCompose.noneIn_of_clamped`) asks for `min(ZONE.c1, s - 1/2) <= BOX.c1`
    and `BOX.c0 <= max(ZONE.c0, 1/2)`, both of which hold with the clamp written exactly.
    """
    cl = {}
    for v, ex in clamps:
        cl[repr(v)] = ex

    def lo(v):
        return cl.get(repr(v), q_up(v))

    def hi(v):
        return cl.get(repr(v), q_dn(v))

    tiv = []
    for a, b in thetas:
        a0, b0 = t_in_lo(a), t_in_hi(b)
        if a0 <= b0:
            tiv.append((a0, b0))
    return dict(x0=lo(x0), x1=hi(x1), y0=lo(y0), y1=hi(y1), t_intervals=tiv)


def intersect_into(zone, box):
    """Clamp `zone` into `box` (both in the rat_box form).  Only shrinks the zone."""
    z = dict(x0=max(zone["x0"], box["x0"]), x1=min(zone["x1"], box["x1"]),
             y0=max(zone["y0"], box["y0"]), y1=min(zone["y1"], box["y1"]), t_intervals=[])
    for (a, b) in zone["t_intervals"]:
        for (c, d) in box["t_intervals"]:
            lo, hi = max(a, c), min(b, d)
            if lo <= hi:
                z["t_intervals"].append((lo, hi))
    return z


def zone_sub_box(zone, box):
    """THE DECIDABLE CHECK, on the WRITTEN rationals -- the same predicate the Lean side
    discharges with one `decide` (`LocalCompose.noneIn_of_clamped`'s hypotheses).  Returns a list
    of failures; empty means the containment holds."""
    bad = []
    if zone["x0"] > zone["x1"] or zone["y0"] > zone["y1"]:
        bad.append(("zone-empty", 0.0))
    if not zone["t_intervals"]:
        bad.append(("zone-no-t-intervals", 0.0))
    for k, cmpk in (("x0", "ge"), ("y0", "ge")):
        if zone[k] < box[k]:
            bad.append((k, float(box[k] - zone[k])))
    for k in ("x1", "y1"):
        if zone[k] > box[k]:
            bad.append((k, float(zone[k] - box[k])))
    for (a, b) in zone["t_intervals"]:
        if not any(c <= a and b <= d for (c, d) in box["t_intervals"]):
            bad.append(("t-interval [%s, %s]" % (a, b), float("nan")))
    return bad


def jbox(b):
    return dict(x0=str(b["x0"]), x1=str(b["x1"]), y0=str(b["y0"]), y1=str(b["y1"]),
                t_intervals=[[str(a), str(c)] for a, c in b["t_intervals"]])


# ---------------------------------------------------------------- matching zones to boxes
def _clamped(v, lo, hi):
    return max(lo, min(v, hi))


def zone_of_box(m, s):
    """A120's `nofam_of`, verbatim: the box's own centre rectangle clamped to the admissible strip
    [1/2, s - 1/2], and the same tilt set reduced mod 90 (already in m['thetas'])."""
    return dict(x0=_clamped(m["x0"], 0.5, s - 0.5), x1=_clamped(m["x1"], 0.5, s - 0.5),
                y0=_clamped(m["y0"], 0.5, s - 0.5), y1=_clamped(m["y1"], 0.5, s - 0.5),
                thetas=[list(t) for t in m["thetas"]])


def match_box(nf, boxes, s, tol=1e-12):
    """The mapped box whose clamped zone IS this exact NO-family (A120's A6 identity).  Returns
    (box, exact_zone) or (None, None)."""
    nt = sorted([tuple(t) for t in nf["thetas"]])
    for m in boxes:
        z = zone_of_box(m, s)
        if sorted([tuple(t) for t in z["thetas"]]) != nt:
            continue
        if all(abs(z[k] - nf[k]) <= tol for k in ("x0", "x1", "y0", "y1")):
            return m, z
    return None, None


# ---------------------------------------------------------------- the wrapper
def narrow(cert, nofams_exact, boxes, s, tag=""):
    """Post-process the dict `caselp.make_certificate` returned, BEFORE it is written.

    `nofams_exact` -- the node's OWN `hyp['nofams']` (A120 builds these at full precision);
    `boxes`        -- the mapped A119 boxes of the node (`rec['boxes_used']`), the boxes the YES
                      side names;
    `s`            -- the node's side.

    Returns (new_cert, report).  Raises FCoverError if the containment fails on the written
    rationals, or if a zone cannot be matched to a box.
    """
    old = cert["hypotheses"]["nofams"]
    if len(old) != len(nofams_exact):
        raise FCoverError("%s: certificate has %d nofams, the node hypothesis has %d"
                          % (tag, len(old), len(nofams_exact)))
    new, rep = [], []
    boxes_out = []
    for k, (o, nf) in enumerate(zip(old, nofams_exact)):
        m, zex = match_box(nf, boxes, s)
        if m is None:
            raise FCoverError("%s: NO-family %d matches no mapped box (A6 identity broken)"
                              % (tag, k))
        box = rat_box(m["x0"], m["x1"], m["y0"], m["y1"], m["thetas"])
        # the two clamp values are EXACTLY rational: 1/2 and s - 1/2 with s = the certificate's
        # own `s` (969271/250000 here).  A bound the clamp produced is written exactly.
        sq = Fr(cert["s"])
        clamps = ((0.5, Fr(1, 2)), (s - 0.5, sq - Fr(1, 2)))
        zone = rat_box(zex["x0"], zex["x1"], zex["y0"], zex["y1"], zex["thetas"], clamps=clamps)
        zone = intersect_into(zone, box)
        bad = zone_sub_box(zone, box)
        if bad:
            raise FCoverError("%s: ZONE not inside BOX after inward rounding: %s" % (tag, bad))
        # what changed against the certificate as A112 wrote it
        d = {}
        for key in ("x0", "x1", "y0", "y1"):
            d[key] = float(zone[key] - Fr(o[key]))
        told = [(Fr(a), Fr(b)) for a, b in o["t_intervals"]]
        tnew = list(zone["t_intervals"])
        dt = []
        for (a, b), (c, e) in zip(sorted(told), sorted(tnew)):
            dt.append([float(c - a), float(e - b)])
        # ... and how far the WRITTEN zone is from the EXACT one (the inward rounding's own cost)
        de = {key: float(zone[key]) - zex[key] for key in ("x0", "x1", "y0", "y1")}
        det = []
        for (c, e), (a0, b0) in zip(sorted(tnew), sorted([tuple(t) for t in zex["thetas"]])):
            det.append([float(c) - t_of_deg(a0), float(e) - t_of_deg(b0)])
        rep.append(dict(index=k, box=m["name"],
                        delta_centre=d, delta_t=dt,
                        delta_vs_exact_centre=de, delta_vs_exact_t=det,
                        max_abs_delta_vs_exact=max([abs(v) for v in de.values()]
                                                   + [abs(v) for p in det for v in p]),
                        max_abs_delta=max([abs(v) for v in d.values()]
                                          + [abs(v) for p in dt for v in p]),
                        zone=jbox(zone), box_written=jbox(box),
                        zone_sub_box=True,
                        n_t_intervals=[len(told), len(tnew)]))
        new.append(jbox(zone))
        boxes_out.append(dict(name=m["name"], **jbox(box)))
    out = json.loads(json.dumps(cert))          # never mutate the caller's dict
    out["hypotheses"]["nofams"] = new
    out["hypotheses"]["nofam_boxes"] = boxes_out
    out["fcover"] = dict(fix=FCOVER_TAG, zone_sub_box=True, attempt="A136",
                         boxes_rounded="inward (subset of the mapped A119 box)",
                         zones_rounded="inward, then intersected with the written box",
                         per_family=rep)
    out["provenance"] = dict(out.get("provenance") or {})
    out["provenance"]["a136_fcover"] = FCOVER_TAG
    return out, rep


def narrow_file(cert_path, nofams_exact, boxes, s, out_path, tag=""):
    with open(cert_path, encoding="utf-8") as f:
        cert = json.load(f)
    out, rep = narrow(cert, nofams_exact, boxes, s, tag=tag)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=0)
    os.replace(tmp, out_path)
    return out, rep


# ---------------------------------------------------------------- the frozen verifier
def verify_frozen(cert_path, jobs=1, depth=56, max_w=64, wall=2600.0):
    """A112's `certify.run_verifier`, argument for argument, plus a hard wall (A120's rule: a
    verification cap can only ABORT, never decide).  The verifier is the frozen
    `verify_case.py` (sha 521cb01f...), byte-identical -- checked here, loudly."""
    import hashlib
    with open(VERIFY_CASE, "rb") as f:
        got = hashlib.sha256(f.read()).hexdigest()
    if got != VERIFY_CASE_SHA:
        raise RuntimeError("verify_case.py is NOT the frozen verifier: %s" % got)
    cmd = [sys.executable, VERIFY_CASE, cert_path, "--jobs", str(jobs), "--depth", str(depth),
           "--max-witnesses", str(max_w), "--report", "--quiet"]
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env[v] = "1"
    flags = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         env=env, creationflags=flags)
    capped = False
    try:
        txt = p.communicate(timeout=wall)[0] or ""
        rc = p.returncode
    except subprocess.TimeoutExpired:
        capped = True
        subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
        try:
            txt = p.communicate(timeout=60)[0] or ""
        except Exception:
            txt = ""
        rc = 124
    tail = [ln for ln in txt.splitlines()
            if ln.startswith(("PASS", "FAIL", "boxes", "  worst", "MALFORMED"))]
    return dict(result=("PASS" if rc == 0 else ("CAP" if capped else "FAIL")), rc=rc,
                capped=capped, seconds=round(time.time() - t0, 1), verifier=tail[-6:])


# ---------------------------------------------------------------- misc
def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def jdump(p, o):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(o, f, indent=1)
    os.replace(tmp, p)


def mklog(name):
    path = os.path.join(LOGS, name)

    def log(*a):
        msg = " ".join(str(x) for x in a)
        line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line, flush=True)
    return log
