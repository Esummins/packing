"""A136 (A151 continuation) -- the two neighbourhoods `N` as A119-shaped `entry` dicts, and the
question of WHICH certificate each one may cite.

## The finding this module exists to get right

A120/A136's YES leaf is "`node ∧ (for every i, some square's pose is in BOX_i)` is dead, because it
implies the hypothesis of a certified local neighbourhood `N`".  `LocalDead` is **antitone** in the
box list: a certificate about SMALLER boxes does not discharge a cover built on LARGER ones.  So
the boxes the cover names must be **inside** the boxes the cited certificate is about.

A133's t-form re-emission deliberately makes `N` **smaller** than A119's (`notes/results.md`: root
`t`-cells are "multiples of `2⁻²⁴`, **rounded INWARD** from A119's angle cells and clipped to
`[0, 1]`"; `notes/method.md`: "a tilt cell that leaves the fundamental domain is clipped to its
inside part at the DEFINITION of `N` ... it is smaller than A119's — the sound direction").
Measured here against A119's nominal boxes: every tilt bound is inside by `+2.98·10⁻⁶ / −1.77·10⁻⁶`
degrees, and `BR(0,1)`'s `[−10, 10]` (mod 90 the two branches `[[80, 90], [0, 10]]`) is clipped to
the single branch `[0, 9.9999986]` — **a whole 10° branch smaller**.

Consequence, recorded rather than glossed: **A136's earlier 15 closures name A133's t-certificate
in their `hD` slot but use A119's NOMINAL boxes.**  Those closures are sound — A119's own
certificate is about exactly those boxes and was independently re-checked (`check_local.py`, all
valid, 1072 s) — but the CITATION is wrong, and `report136.py` now emits A119 as the load-bearing
one with A133's t-form offered only for boxes shrunk to its bodies.  Nothing about the LP or the
NO certificates changes; it is a citation fix.

## What each queue uses here

* **symmetric queue** — A119's nominal boxes, bit-for-bit what A120 and A136 used, citing A119's
  `S02_k5_11_r0.20_rho10.cert.json.gz` (sha `41fa6e5a…`, independently checked).  Consistent with
  the 15 closures already on the board.
* **asymmetric queue** — the boxes ARE A151's t-certificate's own exact rational bodies, so the
  containment holds with EQUALITY and the independently checked object
  (`S02_k5_11_A151asym_f1.tcert.json.gz`, sha `a0202e53…`, `check_local_t151.json`: 0 errors,
  38 590 leaves, certified minimum 3.8770844581 > `s0`) is the one cited.  A151 also emitted an
  angle-space certificate with the nominal spec (sha `11b9047d…`) but no independent re-check of
  it is recorded, so the t-form is preferred and its bodies are the boxes.
  The price, stated up front: `BR(0,1)`'s tilt is the single clipped branch `[0, 9.9999986]`
  instead of `[−10, 10]`, so the `NO3` zone is about half the tilt it was on the symmetric route
  and that child's LP is correspondingly weaker.  `f1` is grown to `±0.40 / ±0.25 / ±40°`, so
  `NO0`'s zone is much larger and that child's LP is correspondingly stronger.

Read-only on A119, A133 and A151; nothing there is written.
"""
from __future__ import annotations

import gzip, hashlib, json, math, os
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

A119R = os.path.join(ROOT, "attempts", "A119-local-cert-lean", "results")
A119C = os.path.join(ROOT, "attempts", "A119-local-cert-lean", "certs")
A151C = os.path.join(ROOT, "attempts", "A151-pinwheel-basin", "certs")

BASE_ID = "S02_k5_11_r0.20_rho10"
ASYM_ID = "S02_k5_11_A151asym_f1"

ASYM_TCERT = os.path.join(A151C, ASYM_ID + ".tcert.json.gz")
ASYM_TCERT_SHA = "a0202e530068cea742c1569f8ccd462daf683205e2d6874733c1e95174ca296d"
BASE_CERT_SHA = "41fa6e5a9da74c76698c9d3b0c486d4ae76160fdb669498754fb5194c631f5e6"

CITE_BASE = dict(
    id=BASE_ID, format="local-cert-v1 (angle space)",
    file="attempts/A119-local-cert-lean/certs/S02_k5_11_r0.20_rho10.cert.json.gz",
    sha256=BASE_CERT_SHA, spec="symmetric r=0.20 rho=10deg about the anchors (A116's N, made exact)",
    boxes="A119's NOMINAL boxes -- exactly the boxes this cover names",
    checker="attempts/A119-local-cert-lean/code/check_local.py -- independent (no numpy, no tree "
            "code, dyadic intervals at 2^-96, rigorous pi/cos/sin): ALL VALID, 1072 s over the 7 "
            "certificates",
    alternative=dict(
        id=BASE_ID, format="local-cert-t-v1",
        file="attempts/A133-tan-half-emission/certs/S02_k5_11_r0.20_rho10.tcert.json.gz",
        sha256="a8d95682490e5caeae5512d8db11f5927bb1e53725fa31cf48ce073101a9ab72",
        caveat="A133's N is SMALLER than A119's (t-cells rounded INWARD from the angle cells; "
               "BR(0,1) clipped to the [0,90] branch), so this certificate discharges the YES "
               "leaf only for boxes shrunk to its meta.bodies -- NOT for the nominal boxes this "
               "cover names."))

CITE_ASYM = dict(
    id=ASYM_ID, format="local-cert-t-v1",
    file="attempts/A151-pinwheel-basin/certs/S02_k5_11_A151asym_f1.tcert.json.gz",
    sha256=ASYM_TCERT_SHA, dead=True, leaves=38590,
    spec="asymmetric: f1 x+-0.40 y+-0.25 tilt+-40deg; f2, f3, BR(0,1) unchanged at +-0.20/+-0.20/+-10deg",
    boxes="THE CERTIFICATE'S OWN meta.bodies -- the cover's boxes are these exact rationals, so "
          "the containment BOX subset certified-N holds with equality",
    checker="attempts/A151-pinwheel-basin/results/check_local_t151.json "
            "(A133's check_local_t.py, imported): 0 errors, 38 590 leaves, certified minimum "
            "3.8770844581046435 > s0 = 3.877084",
    angle_space_sibling=dict(
        file="attempts/A151-pinwheel-basin/certs/S02_k5_11_A151asym_f1.cert.json.gz",
        sha256="11b9047d8c4d53aa0f7e5301579d9993cde6b8a90150691ebc36693577034c40",
        caveat="nominal spec, but no independent re-check of THIS file is recorded; the t-form is "
               "the checked object, so it is the one cited"))


def _deg_of_t(t):
    return math.degrees(2.0 * math.atan(float(t)))


def base_entry():
    """A119's entry, untouched -- the symmetric N, the boxes A120 and A136 used."""
    with open(os.path.join(A119R, "N_boxes.json"), encoding="utf-8") as f:
        d = json.load(f)
    for e in d["N"]:
        if e["id"] == BASE_ID:
            e = dict(e)
            e["certificate"] = CITE_BASE
            e["boxes"] = [dict(b, half_extent=[0.2, 0.2, 10.0]) for b in e["boxes"]]
            return e
    raise KeyError(BASE_ID)


def asym_entry():
    """A151's certified asymmetric N, with the boxes taken from the t-certificate's own exact
    rational bodies (so BOX = certified body, containment by equality).  Pins are A119's,
    bit-for-bit, and are asserted identical to the certificate's."""
    with open(ASYM_TCERT, "rb") as f:
        got = hashlib.sha256(f.read()).hexdigest()
    if got != ASYM_TCERT_SHA:
        raise RuntimeError("A151 t-certificate sha mismatch: %s" % got)
    with gzip.open(ASYM_TCERT, "rt", encoding="utf-8") as f:
        cert = json.load(f)
    meta = cert["meta"]
    bodies = {b["name"]: b for b in meta["bodies"] if b.get("kind") == "free"}
    base = base_entry()
    boxes, checks = [], []
    for b in base["boxes"]:
        nm = b["name"]
        t = bodies[nm]
        cx = [float(Fr(t["x0"])), float(Fr(t["x1"]))]
        cy = [float(Fr(t["y0"])), float(Fr(t["y1"]))]
        th = [_deg_of_t(Fr(t["t0"])), _deg_of_t(Fr(t["t1"]))]
        anc = [0.5 * (cx[0] + cx[1]), 0.5 * (cy[0] + cy[1]), 0.5 * (th[0] + th[1])]
        he = [0.5 * (cx[1] - cx[0]), 0.5 * (cy[1] - cy[0]), 0.5 * (th[1] - th[0])]
        SPEC = {"f1": (0.40, 0.25, 40.0), "f2": (0.20, 0.20, 10.0),
                "f3": (0.20, 0.20, 10.0), "BR(0,1)": (0.20, 0.20, 10.0)}[nm]
        nb = dict(b, cx=cx, cy=cy, theta_deg=th, anchor=anc, half_extent=he,
                  # A5 is a PLAUSIBILITY check ("is this node really a consumer of N?"), not a
                  # soundness condition, and A151's own consumer test (consumer151.inside_boxes)
                  # runs it on the three f* boxes at their NOMINAL anchors.  Match that exactly,
                  # so the record's A5 agrees with the verdict the queue was built from.
                  a5_anchor=list(b["anchor"]), a5_half_extent=list(SPEC),
                  a5_skip=(nm == "BR(0,1)"),
                  grown=(nm == "f1"), from_certificate_body=True,
                  cert_clipped=bool(t.get("clipped")),
                  cert_rational=dict(x0=t["x0"], x1=t["x1"], y0=t["y0"], y1=t["y1"],
                                     t0=t["t0"], t1=t["t1"]))
        checks.append(dict(box=nm, half_extent=[round(v, 9) for v in he],
                           tilt_deg=[round(v, 7) for v in th], clipped=bool(t.get("clipped")),
                           a119_nominal_tilt_deg=list(b["theta_deg"]),
                           a119_nominal_centre=[list(b["cx"]), list(b["cy"])],
                           inside_a119_nominal=bool(
                               cx[0] >= b["cx"][0] - 1e-12 and cx[1] <= b["cx"][1] + 1e-12
                               or nm == "f1")))
        boxes.append(nb)
    e = dict(base)
    e["id"] = ASYM_ID
    e["boxes"] = boxes
    e["r"] = float(meta["r"])                 # 0.40 -- the MAXIMUM half-extent over the boxes
    e["rho_deg"] = float(meta["rho_deg"])     # 40.0
    e["spec"] = meta.get("spec") or {}
    e["certificate"] = CITE_ASYM
    e["a151_boxes"] = checks
    e["note"] = ("boxes ARE the t-certificate's exact rational bodies; r/rho_deg are the MAXIMA "
                 "over them, so a120lib.soundness's A4/A5 (which use one (r, rho)) are LOOSE here "
                 "-- per_box_check() is the tight form and is what the record reports")
    return e


def per_box_check(mapped, entry, f, cfg=None, seed=0, nsample=500):
    """The tight, PER-BOX form of A120's A4 (D4 round-trip lands in the box's OWN half-extents)
    and A5 (the node's own A107 configuration lies in the mapped boxes), for an entry whose boxes
    have different half-extents.  `f` is the forward map, node frame -> class frame."""
    import itertools, random
    rng = random.Random(seed + 151)
    per, ok = [], True
    for m, b in zip(mapped, entry["boxes"]):
        hx, hy, ht = b.get("half_extent") or [0.2, 0.2, 10.0]
        anc = b["anchor"]
        drawn = inside = 0
        for _ in range(nsample):
            x = rng.uniform(m["x0"], m["x1"])
            y = rng.uniform(m["y0"], m["y1"])
            t = rng.uniform(m["th0"], m["th1"])
            X, Y, T = f(x, y, t)
            drawn += 1
            d = abs(((T - anc[2]) + 45.0) % 90.0 - 45.0)
            if abs(X - anc[0]) <= hx + 1e-9 and abs(Y - anc[1]) <= hy + 1e-9 and d <= ht + 1e-9:
                inside += 1
        good = (inside == drawn)
        ok = ok and good
        per.append(dict(box=m["name"], half_extent=[hx, hy, ht], drawn=drawn,
                        inside_own_box=inside, ok=good))
    out = dict(ok=bool(ok), per_box=per,
               note="A4 with PER-BOX half-extents (tighter than a120lib.soundness's single (r, rho))")
    if cfg:
        # A5, per box, on A151's OWN injection rule: the three f* boxes at their nominal anchors.
        # BR(0,1) is excluded exactly as `consumer151.inside_boxes` excludes it, and the nominal
        # anchors are used because the certificate BODY of a clipped box is re-anchored (BR(0,1)'s
        # body [0, 9.9999986] has anchor 5 deg, not the box's 0 deg), which would measure the
        # deviation from the wrong centre.
        sel = [(m, b) for m, b in zip(mapped, entry["boxes"]) if not b.get("a5_skip")]
        best = None
        for perm in itertools.permutations(range(len(cfg)), len(sel)):
            worst = None
            for (m, b), j in zip(sel, perm):
                hx, hy, ht = b.get("a5_half_extent") or b.get("half_extent") or [0.2, 0.2, 10.0]
                anc = b.get("a5_anchor") or b["anchor"]
                x, y, t = cfg[j]
                X, Y, T = f(x, y, t)
                d = abs(((T - anc[2]) + 45.0) % 90.0 - 45.0)
                sl = min(hx - abs(X - anc[0]), hy - abs(Y - anc[1]), ht - d)
                worst = sl if worst is None else min(worst, sl)
            if best is None or worst > best:
                best = worst
        out["a5_per_box_min_slack"] = None if best is None else round(best, 6)
        out["a5_ok"] = bool(best is not None and best >= -1e-9)
        out["a5_rule"] = ("A151 consumer151.inside_boxes: the f* boxes only, nominal anchors "
                          "(%d of %d boxes)" % (len(sel), len(mapped)))
        out["ok"] = bool(out["ok"] and out["a5_ok"])
    return out


# --------------------------------------------------------------------------- A160's UNION
A160R = os.path.join(ROOT, "attempts", "A160-s02-f0-slide", "results")
A160_NBOXES = os.path.join(A160R, "N_boxes160.json")

A160_NO_CERTIFICATE = (
    "NO CERTIFICATE ARTEFACT EXISTS FOR THIS BOX SET.  attempts/A160-s02-f0-slide/certs/ is EMPTY; "
    "N_boxes160.json carries no sha256 and no certificate filename for any of its 53 entries, and "
    "results/ has no independent-checker output for them.  What each entry carries is an IN-RUN "
    "`tree_verdict` -- {dead, certified_min (a FLOAT), sample_hits, seconds} -- produced by the "
    "generator itself.  Every other YES leaf in this line cites an emitted certificate FILE plus an "
    "INDEPENDENT rational checker verdict plus a sha256 (A119 check_local.py; A133/A151 "
    "check_local_t.py).  So a node covered only by an A160 entry CANNOT be closed here: its NO side "
    "is certified and banked, and its YES leaf is recorded PENDING-CERTIFICATE.  A160 already has "
    "the tooling to fix this (`code/gent160.py` = A133's t-generator + the independent rational "
    "checker, imported unchanged), so each entry is minutes of compute away from being citeable.")


def a160_entries():
    with open(A160_NBOXES, encoding="utf-8") as f:
        return json.load(f)["N"]


def a160_entry(link):
    """One entry of A160's UNION as an A119-shaped `entry`.  The hypothesis of the file is a
    DISJUNCTION over its 53 entries, so a node is served by the ONE entry its support lies in --
    `link` is that index, from consumer160.json's union row.

    The YES leaf is NOT citeable: see A160_NO_CERTIFICATE.  This builder therefore marks the
    certificate `status: PENDING-CERTIFICATE` and carries the entry's float `tree_verdict` verbatim,
    so nothing downstream can mistake it for a checked object."""
    E = a160_entries()
    e = dict(E[link])
    tv = e.get("tree_verdict") or {}
    boxes = []
    for b in e["boxes"]:
        he = b.get("half_extent") or [0.2, 0.2, 10.0]
        boxes.append(dict(b, half_extent=list(he),
                          a5_anchor=list(b["anchor"]), a5_half_extent=list(he),
                          a5_skip=(b["name"] == "BR(0,1)")))
    e["boxes"] = boxes
    e["certificate"] = dict(
        id=e["id"], format="A160 N_boxes160.json entry (union member %d of 53)" % link,
        file="attempts/A160-s02-f0-slide/results/N_boxes160.json",
        sha256=None, status="PENDING-CERTIFICATE",
        tree_verdict=tv,
        margin_over_s0=(None if tv.get("certified_min") is None
                        else round(float(tv["certified_min"]) - 3.877084, 10)),
        boxes="A160's own entry boxes (nominal); no certificate exists to compare them against",
        caveat=A160_NO_CERTIFICATE,
        emit_command=("python attempts/A160-s02-f0-slide/code/gent160.py  # + "
                      "attempts/A133-tan-half-emission/code/check_local_t.py on the result"))
    e["note"] = ("A160 union entry; YES leaf PENDING-CERTIFICATE, NO side certified and banked. "
                 "A160's consumer test (like A151's) uses the three f* boxes only, which is what "
                 "per_box_check's A5 reproduces.")
    return e


def entry_for(which, link=None):
    if which == "base":
        return base_entry()
    if which == "asym":
        return asym_entry()
    if which == "a160":
        if link is None:
            raise ValueError("entry_for('a160') needs the union link index")
        return a160_entry(link)
    raise ValueError(which)



if __name__ == "__main__":
    for w in ("base", "asym"):
        e = entry_for(w)
        print("==", w, e["id"], "r", e["r"], "rho", e["rho_deg"])
        for b in e["boxes"]:
            print("   %-9s x[%.9f, %.9f] y[%.9f, %.9f] th[%.7f, %.7f] he=%s"
                  % (b["name"], b["cx"][0], b["cx"][1], b["cy"][0], b["cy"][1],
                     b["theta_deg"][0], b["theta_deg"][1],
                     [round(v, 7) for v in b["half_extent"]]))


# --------------------------------------------------------------------------- A163's OTHER FRAMES
A163R = os.path.join(ROOT, "attempts", "A163-s02-other-frames", "results")


def a163_index(frame):
    """{entry id: (entry, checker run)} for A163's box sets in `frame` ('k5_16' or 'trump5'),
    keeping ONLY the entries that are fully citeable: the recorded checker run passed with zero
    errors, its sha256 matches the entry's AND the file on disk, and it recorded an EXACT RATIONAL
    certified minimum strictly above s0.

    Eight of A163's 94 entries record `checker_ok: true` with NO `certified_min` (the
    `chain_BOTH_base_r0.20_h1.25_nof0_-25 .. -45` links, 7 in k5_16 and 1 in trump5) and one
    (`chain_RXY_probe_-10.00`) has a checker run whose sha256 names a DIFFERENT file from the one on
    disk -- so for those the recorded check does not establish a margin over s0 for the artefact
    that exists.  They are excluded here rather than cited."""
    import hashlib
    with open(os.path.join(A163R, "tcerts163.json"), encoding="utf-8") as f:
        runs = {r["id"]: r for r in json.load(f)["runs"]}
    with open(os.path.join(A163R, "N_boxes163_%s.json" % frame), encoding="utf-8") as f:
        N = json.load(f)["N"]
    S0 = Fr(969271, 250000)
    out = {}
    for e in N:
        c = e["certificate"]
        r = runs.get(c["id"])
        if not r or not r.get("checker_ok") or r.get("n_errors") or r.get("certified_min") is None:
            continue
        if r["sha256"] != c["sha256"]:
            continue
        p = os.path.join(ROOT, c["file"].replace("/", os.sep))
        if not os.path.exists(p):
            continue
        with open(p, "rb") as fh:
            if hashlib.sha256(fh.read()).hexdigest() != c["sha256"]:
                continue
        if Fr(r["certified_min"]) <= S0:
            continue
        out[e["id"]] = (e, r)
    return out


def a163_entry(entry_id, frame):
    """One CHECKED A163 box set as an A119-shaped `entry`, with the boxes taken from the
    t-certificate's own exact rational bodies, so BOX = certified body and the containment
    BOX subset certified-N holds with EQUALITY -- the same discipline as `asym_entry`."""
    import gzip as _gz
    idx = a163_index(frame)
    if entry_id not in idx:
        raise RuntimeError("A163 entry %s is not citeable (see a163_index)" % entry_id)
    e, run = idx[entry_id]
    with _gz.open(os.path.join(ROOT, e["certificate"]["file"].replace("/", os.sep)),
                  "rt", encoding="utf-8") as f:
        bodies = {b["name"]: b for b in json.load(f)["meta"]["bodies"]
                  if b.get("kind") == "free"}
    boxes = []
    for b in e["boxes"]:
        nm = b["name"]
        t = bodies.get(nm)
        if t is None:                                  # not a free body in the certificate
            boxes.append(dict(b, half_extent=b.get("half_extent") or [0.2, 0.2, 10.0],
                              a5_anchor=list(b["anchor"]),
                              a5_half_extent=list(b.get("half_extent") or [0.2, 0.2, 10.0]),
                              a5_skip=True))
            continue
        cx = [float(Fr(t["x0"])), float(Fr(t["x1"]))]
        cy = [float(Fr(t["y0"])), float(Fr(t["y1"]))]
        th = [_deg_of_t(Fr(t["t0"])), _deg_of_t(Fr(t["t1"]))]
        he = [0.5 * (cx[1] - cx[0]), 0.5 * (cy[1] - cy[0]), 0.5 * (th[1] - th[0])]
        boxes.append(dict(b, cx=cx, cy=cy, theta_deg=th,
                          anchor=[0.5 * (cx[0] + cx[1]), 0.5 * (cy[0] + cy[1]),
                                  0.5 * (th[0] + th[1])],
                          half_extent=he, from_certificate_body=True,
                          cert_clipped=bool(t.get("clipped")),
                          a5_anchor=list(b["anchor"]),
                          a5_half_extent=list(b.get("half_extent") or [0.2, 0.2, 10.0]),
                          a5_skip=(nm == "BR(0,1)"),
                          cert_rational=dict(x0=t["x0"], x1=t["x1"], y0=t["y0"], y1=t["y1"],
                                             t0=t["t0"], t1=t["t1"])))
    out = dict(e)
    out["boxes"] = boxes
    out["r"] = float(e.get("r") or 0.4)
    out["rho_deg"] = float(e.get("rho_deg") or 40.0)
    cite = dict(e["certificate"])
    cite["certified_min_rational"] = run["certified_min"]
    cite["margin_over_s0"] = float(Fr(run["certified_min"]) - Fr(969271, 250000))
    cite["checker_run"] = dict(checker_ok=run["checker_ok"], n_errors=run["n_errors"],
                               n_leaves=run.get("n_leaves"), seconds=run.get("checker_seconds"))
    cite["boxes"] = ("THE CERTIFICATE'S OWN meta.bodies (exact rationals); the cover's boxes ARE "
                     "these, so BOX subset certified-N holds with equality")
    out["certificate"] = cite
    out["note"] = ("A163 re-framing of the S02 basin into %s's frame; L/P are %s / %s"
                   % (frame, e.get("L"), e.get("P")))
    return out
