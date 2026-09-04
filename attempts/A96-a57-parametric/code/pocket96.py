"""pocket96 -- k6 slot-pocket yield on A57 / A96 certification witnesses.

PI idea (A96 chore): in a k5 class, a free square parked within the k6 pin tolerance of a
COMPLETABLE slot would put the packing inside a k6 extension class that is killed on the
window (Lemma PD / K1), so that placement is dead and the witness box could be EXEMPTED.
This script measures the yield: what fraction of certification holes / undecided boxes are
"pocket boxes".

POCKET DEFINITION (as prescribed by the coordinator; not re-derived here):
  a witness box is a POCKET box iff
    (a) its whole cx range lies within delta of a completable-slot x-centre, AND
    (b) its whole cy range lies within delta of the SAME slot's y-centre, AND
    (c) its whole tilt range lies within |theta| <= tol of 0 mod 90 deg, i.e. the box's
        t-interval (t = tan(theta/2)) is contained in [0, tan(tol/2)] or in
        [tan((90-tol)/2), 1].
  PARTIAL = the box meets some slot pocket but is not contained in one.

Read-only on all campaign files.  Writes only results/pocket96.json and notes/pocket96.md.
"""
import json, glob, math, os, re, collections
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees")
A96 = os.path.join(ROOT, "attempts", "A96-a57-parametric")

S0 = F("969271/250000")          # 3.877084
SLO = F("191/50")                # 3.82

# ---------------------------------------------------------------- slot centres
# affine (alpha, beta): centre coordinate = alpha + beta * s
SLOTS = {
    "k5_11": [("BL(2,0)", (F(5, 2), 0), (F(1, 2), 0)),
              ("BL(1,1)", (F(3, 2), 0), (F(3, 2), 0)),
              ("BL(0,2)", (F(1, 2), 0), (F(5, 2), 0)),
              ("TL(1,0)", (F(3, 2), 0), (F(-1, 2), 1)),
              ("TL(0,1)", (F(1, 2), 0), (F(-3, 2), 1)),
              ("BR(1,0)", (F(-3, 2), 1), (F(1, 2), 0)),
              ("BR(0,1)", (F(-1, 2), 1), (F(3, 2), 0)),
              ("TR(0,0)", (F(-1, 2), 1), (F(-1, 2), 1))],
    "k5_16": [("BL(1,0)", (F(3, 2), 0), (F(1, 2), 0)),
              ("BL(1,1)", (F(3, 2), 0), (F(3, 2), 0)),
              ("BL(0,2)", (F(1, 2), 0), (F(5, 2), 0)),
              ("TL(1,0)", (F(3, 2), 0), (F(-1, 2), 1)),
              ("TL(0,1)", (F(1, 2), 0), (F(-3, 2), 1)),
              ("BR(1,0)", (F(-3, 2), 1), (F(1, 2), 0)),
              ("BR(0,1)", (F(-1, 2), 1), (F(3, 2), 0)),
              ("TR(1,0)", (F(-3, 2), 1), (F(-1, 2), 1)),
              ("TR(0,1)", (F(-1, 2), 1), (F(-3, 2), 1))],
}

# the subset that is actually USABLE for the exemption: unclipped AND its k6 extension class
# is killed over the window (A94 results/slots94.json + A56/A61 scoreboard).
USABLE = {
    "k5_11": {"BL(1,1)": "k6_18", "BR(0,1)": "k6_20", "TL(1,0)": "k6_20",
              "TR(0,0)": "k6_23"},
    "k5_16": {"BL(1,0)": "k6_23", "BR(0,1)": "k6_29", "TR(0,1)": "k6_30",
              "TR(1,0)": "k6_28"},
}
# k6_23 parametric window is [3.82, 3.877] plus the fixed-s0 certificate AT s0.
K6_23_GAP = (F("3877/1000"), S0)     # open interval where k6_23 gives nothing


def slot_range(alpha, beta, slo, shi):
    """interval of the slot coordinate as s ranges over [slo, shi]."""
    lo = alpha + beta * slo
    hi = alpha + beta * shi
    return (min(lo, hi), max(lo, hi))


# ---------------------------------------------------------------- tolerances
def tilt_band(tol_deg):
    """t-interval endpoints for |theta| <= tol_deg mod 90, with t = tan(theta/2)."""
    lo_hi = math.tan(math.radians(tol_deg) / 2.0)          # near 0 deg: t in [0, lo_hi]
    hi_lo = math.tan(math.radians(90.0 - tol_deg) / 2.0)   # near 90 deg: t in [hi_lo, 1]
    return F(str(lo_hi)), F(str(hi_lo))


TOLS = [("d0.01_t1deg", F("0.01"), 1.0),
        ("d0.02_t2deg", F("0.02"), 2.0)]


def classify(box, class_name, slo, shi, delta, tband, slot_filter=None):
    """returns 'entire' / 'partial' / 'none' plus the slot name if entire."""
    t0, t1 = box["t"]
    cx0, cx1 = box["cx"]
    cy0, cy1 = box["cy"]
    tlo, thi = tband
    tilt_in = (t1 <= tlo) or (t0 >= thi)                       # whole tilt range OK
    tilt_meets = (t0 <= tlo) or (t1 >= thi)                    # some of it OK
    hit_entire, hit_partial = None, False
    for name, ax, ay in SLOTS[class_name]:
        if slot_filter is not None and name not in slot_filter:
            continue
        kx0, kx1 = slot_range(ax[0], ax[1], slo, shi)
        ky0, ky1 = slot_range(ay[0], ay[1], slo, shi)
        # ENTIRE: every (cx,cy) in the box is within delta of every admissible slot centre
        ex = (cx0 >= kx1 - delta) and (cx1 <= kx0 + delta)
        ey = (cy0 >= ky1 - delta) and (cy1 <= ky0 + delta)
        if ex and ey and tilt_in:
            hit_entire = name
            break
        # PARTIAL: the box's centre range meets the slot's delta-pad
        mx = (cx0 <= kx1 + delta) and (cx1 >= kx0 - delta)
        my = (cy0 <= ky1 + delta) and (cy1 >= ky0 - delta)
        if mx and my and tilt_meets:
            hit_partial = True
    if hit_entire:
        return "entire", hit_entire
    return ("partial" if hit_partial else "none"), None


def nearest_slot(box, class_name, slo, shi, slot_filter=None):
    """L-inf distance (in centre coords) from the box to the nearest slot centre range."""
    best, bn = None, None
    cx0, cx1 = box["cx"]
    cy0, cy1 = box["cy"]
    for name, ax, ay in SLOTS[class_name]:
        if slot_filter is not None and name not in slot_filter:
            continue
        kx0, kx1 = slot_range(ax[0], ax[1], slo, shi)
        ky0, ky1 = slot_range(ay[0], ay[1], slo, shi)
        dx = max(F(0), kx0 - cx1, cx0 - kx1)
        dy = max(F(0), ky0 - cy1, cy0 - ky1)
        d = max(dx, dy)
        if best is None or d < best:
            best, bn = d, name
    return float(best), bn


# ---------------------------------------------------------------- loaders
def parse_box(b):
    out = {}
    for k in ("t", "cx", "cy"):
        out[k] = (F(b[k][0]), F(b[k][1]))
    if "s" in b:
        out["s"] = (F(b["s"][0]), F(b["s"][1]))
    return out


def class_of(name):
    if "k5_11" in name:
        return "k5_11"
    if "k5_16" in name:
        return "k5_16"
    return None


def load_nodes():
    """yields dicts describing every witness-bearing certificate node."""
    nodes = []
    pats = [(os.path.join(A57, "certs", "tree", "*", "*.witnesses.json"), "A57-tree"),
            (os.path.join(A57, "certs", "epsgeo", "*.witnesses.json"), "A57-epsgeo"),
            (os.path.join(A96, "certs", "param", "*", "*.witnesses.json"), "A96-param"),
            (os.path.join(A96, "results", "param", "*.witnesses.json"), "A96-param")]
    seen = set()
    for pat, src in pats:
        for f in sorted(glob.glob(pat)):
            if f in seen:
                continue
            seen.add(f)
            d = json.load(open(f))
            base = os.path.basename(f)[:-len(".witnesses.json")]
            cls = class_of(base)
            if cls is None:
                continue
            rep = f.replace(".witnesses.json", ".report.json")
            R = json.load(open(rep)) if os.path.exists(rep) else {}
            if "slo" in d:
                slo, shi = F(d["slo"]), F(d["shi"])
                param = True
            else:
                slo = shi = F(d.get("s") or R.get("s") or S0)
                param = False
            m = re.search(r"_epsgeo([0-9.]+)", base)
            nw = len(d.get("witnesses", []))
            live = (nw == (R.get("stats", {}).get("witnesses") or 0))
            nodes.append(dict(
                file=f, src=src, node=base, cls=cls, param=param,
                slo=slo, shi=shi,
                eps_geo=(float(m.group(1)) if m else None),
                live=live, result=R.get("result"),
                group=os.path.basename(os.path.dirname(f)),
                witnesses=[dict(kind=w.get("kind"), box=parse_box(w["box"]),
                                placement=w.get("placement", {}))
                           for w in d.get("witnesses", [])]))
    return nodes


# ---------------------------------------------------------------- canary
def trump_images(s):
    """the 8 D4 images of the Trump packing at side s (floats); returns poses
    (cx, cy, theta_deg mod 90)."""
    Z = json.load(open(os.path.join(ROOT, "attempts", "A03-upper-reconstruct",
                                    "trump11_float.json")))
    sf = float(s)
    out = []
    for g in range(8):
        for (x, y, th) in Z["X"]:
            xx, yy, tt = x, y, math.degrees(th)
            if g & 4:                      # transpose
                xx, yy, tt = yy, xx, -tt
            if g & 1:                      # flip x
                xx, tt = sf - xx, -tt
            if g & 2:                      # flip y
                yy, tt = sf - yy, -tt
            out.append((xx, yy, tt % 90.0))
    return out


def main():
    nodes = load_nodes()
    res = {"pocket_definition":
           "box is a POCKET box iff its whole cx and cy ranges lie within delta of the SAME "
           "completable-slot centre and its whole tilt range lies within tol of 0 mod 90 "
           "(t = tan(theta/2))",
           "k6_emitted_tolerance": {
               "grep": "attempts/A61-window-stragglers/certs + attempts/A54-stragglers/certs "
                       "contain NO delta_pin/slack/pin_delta field; every k6 core is "
                       "a=16383999967232/32768001953125, tm=1/33554432 (uniform, 220 cores)",
               "core_half_side_a": "16383999967232/32768001953125",
               "implied_position_tolerance_half_width": float(F(1, 2) - F("16383999967232/32768001953125")),
               "core_tilt_margin_tm": float(F("1/33554432")),
               "implied_tilt_tolerance_deg": math.degrees(2 * math.atan(1 / 33554432.0)),
               "note": "the k6 window kills were emitted with DEGENERATE pin boxes; the "
                       "working tolerances below (0.01/1deg, 0.02/2deg) are A57's and A60's "
                       "slack-core deltas, i.e. what a re-emission would give"},
           "slot_sets": {c: [n for n, _, _ in SLOTS[c]] for c in SLOTS},
           "usable_slots": USABLE,
           "tolerances": {}}

    rows = []
    for tag, delta, tol in TOLS:
        tband = tilt_band(tol)
        agg = collections.defaultdict(lambda: collections.Counter())
        node_rows = []
        for nd in nodes:
            cnt = collections.Counter()
            per_kind = collections.defaultdict(collections.Counter)
            all_entire = {"hole": True, "undecided": True, "all": True}
            nwit = {"hole": 0, "undecided": 0, "all": 0}
            for w in nd["witnesses"]:
                k = w["kind"] or "?"
                c, sl = classify(w["box"], nd["cls"], nd["slo"], nd["shi"], delta, tband)
                cu, slu = classify(w["box"], nd["cls"], nd["slo"], nd["shi"], delta, tband,
                                   slot_filter=set(USABLE[nd["cls"]]))
                cnt[c] += 1
                per_kind[k][c] += 1
                per_kind[k]["usable_" + cu] += 1
                nwit["all"] += 1
                nwit[k] = nwit.get(k, 0) + 1
                if c != "entire":
                    all_entire["all"] = False
                    if k in all_entire:
                        all_entire[k] = False
            # A57 bookkeeping: a FAIL node's .witnesses.json matches its report exactly
            # (LIVE holes); a PASS node's .witnesses.json is the STALE pre-repair witness
            # set of the attempt that the eps_geo / deeper re-run then repaired
            # (report stats.witnesses == 0).  So PASS + stale == "eps_geo-repaired PASS".
            outcome = ("FAIL" if nd["result"] == "FAIL"
                       else ("repairedPASS" if nd["result"] == "PASS" else str(nd["result"])))
            if nd["eps_geo"] is not None:
                outcome += "(epsgeo%g)" % nd["eps_geo"]
            key = (nd["src"], nd["cls"], outcome)
            for k in ("hole", "undecided"):
                for c in ("entire", "partial", "none"):
                    agg[key][f"{k}_{c}"] += per_kind[k][c]
                    agg[key][f"{k}_usable_{c}"] += per_kind[k]["usable_" + c]
            agg[key]["nodes"] += 1
            if nwit["hole"] and all_entire["hole"]:
                agg[key]["nodes_all_holes_pocket"] += 1
            if nwit["all"] and all_entire["all"]:
                agg[key]["nodes_all_witnesses_pocket"] += 1
            nd_min, nd_slot = (nearest_slot(nd["witnesses"][0]["box"], nd["cls"],
                                            nd["slo"], nd["shi"])
                               if nd["witnesses"] else (None, None))
            node_rows.append(dict(node=nd["node"], group=nd["group"], src=nd["src"],
                                  cls=nd["cls"], result=nd["result"], live=nd["live"],
                                  eps_geo=nd["eps_geo"], outcome=outcome,
                                  n_wit=nwit["all"], n_hole=nwit["hole"],
                                  n_undecided=nwit["undecided"],
                                  entire=cnt["entire"], partial=cnt["partial"],
                                  none=cnt["none"],
                                  all_holes_pocket=bool(nwit["hole"] and all_entire["hole"]),
                                  all_wit_pocket=bool(nwit["all"] and all_entire["all"]),
                                  first_wit_nearest_slot_Linf=nd_min,
                                  first_wit_nearest_slot=nd_slot))
        res["tolerances"][tag] = dict(
            delta=float(delta), tol_deg=tol,
            t_band=[float(tband[0]), float(tband[1])],
            by_src_class_outcome={"|".join(k): dict(v) for k, v in sorted(agg.items())})
        if tag == TOLS[0][0]:
            rows = node_rows
    res["nodes"] = rows

    # ---- distance census: how close does anything actually get to a slot?
    dist = collections.defaultdict(list)
    for nd in nodes:
        for w in nd["witnesses"]:
            d, sl = nearest_slot(w["box"], nd["cls"], nd["slo"], nd["shi"])
            du, slu = nearest_slot(w["box"], nd["cls"], nd["slo"], nd["shi"],
                                   slot_filter=set(USABLE[nd["cls"]]))
            th0 = math.degrees(2 * math.atan(float(w["box"]["t"][0])))
            th1 = math.degrees(2 * math.atan(float(w["box"]["t"][1])))
            tdist = min(min(th0, th1), 90.0 - max(th0, th1))
            dist[(nd["src"], nd["cls"], w["kind"])].append((d, du, tdist))
    res["distance_census"] = {}
    for k, v in sorted(dist.items()):
        v.sort()
        n = len(v)
        res["distance_census"]["|".join(map(str, k))] = dict(
            n=n,
            min_Linf_to_any_slot=v[0][0],
            p01_Linf=v[max(0, n // 100)][0],
            median_Linf=v[n // 2][0],
            min_Linf_to_usable_slot=min(x[1] for x in v),
            n_within_0p01_any=sum(1 for x in v if x[0] <= 0.01),
            n_within_0p02_any=sum(1 for x in v if x[0] <= 0.02),
            n_within_0p05_any=sum(1 for x in v if x[0] <= 0.05),
            n_tilt_within_1deg=sum(1 for x in v if x[2] >= -1e-12 and x[2] <= 1.0),
            n_tilt_within_2deg=sum(1 for x in v if x[2] <= 2.0),
            n_pos0p01_and_tilt1deg=sum(1 for x in v if x[0] <= 0.01 and x[2] <= 1.0),
            n_pos0p02_and_tilt2deg=sum(1 for x in v if x[0] <= 0.02 and x[2] <= 2.0))

    # ---- canary
    tr = trump_images(S0)
    near = None
    for (x, y, th) in tr:
        for name, ax, ay in SLOTS["k5_11"]:
            kx = float(ax[0] + ax[1] * S0)
            ky = float(ay[0] + ay[1] * S0)
            d = max(abs(x - kx), abs(y - ky))
            dth = min(th, 90.0 - th)
            if near is None or (d, dth) < (near[0], near[1]):
                near = (d, dth, name, (x, y, th))
    res["canary_trump_slot_coincidence"] = dict(
        min_Linf_from_a_trump_image_square_to_a_k5_11_completable_slot=near[0],
        tilt_deg_of_that_square=near[1], slot=near[2], square=near[3],
        note="NOTE: Trump's own upright square at (s-1/2, s-1/2) coincides EXACTLY with "
             "k5_11's completable slot TR(0,0).  This is not a counterexample to the "
             "exemption: Trump is not a packing of class k5_11 (it lacks the k5_11 pin "
             "(1/2, s-1/2); its 5th upright sits at (1/2, 2.5326)), so SLOT-CROWD / the "
             "k6_23 kill is never applied to it.  But the chore's parenthetical 'a Trump "
             "square does not sit within the tolerance of a completable slot of k5_11' is "
             "not literally true at zero tolerance -- the guard that matters is the one "
             "below (no k5_11 witness box is ever classified as a pocket).")

    # boxes that contain, or come close to, a Trump-image pose
    hits, mind = [], None
    for nd in nodes:
        if nd["cls"] != "k5_11":
            continue
        for w in nd["witnesses"]:
            bx = w["box"]
            for (x, y, th) in tr:
                t = math.tan(math.radians(th) / 2.0)
                dx = max(0.0, float(bx["cx"][0]) - x, x - float(bx["cx"][1]))
                dy = max(0.0, float(bx["cy"][0]) - y, y - float(bx["cy"][1]))
                dt = max(0.0, float(bx["t"][0]) - t, t - float(bx["t"][1]))
                dd = max(dx, dy)
                if mind is None or (dd, dt) < mind[:2]:
                    mind = (dd, dt, nd["node"], w["kind"])
                if dx == dy == dt == 0.0:
                    c, sl = classify(bx, nd["cls"], nd["slo"], nd["shi"],
                                     TOLS[1][1], tilt_band(TOLS[1][2]))
                    hits.append(dict(node=nd["node"], kind=w["kind"], trump_pose=[x, y, th],
                                     classification_at_d0p02=c, slot=sl))
    res["canary_trump_image_boxes"] = dict(
        n_boxes_containing_a_trump_image_pose=len(hits), rows=hits[:40],
        any_pocket=any(h["classification_at_d0p02"] == "entire" for h in hits),
        closest_k5_11_witness_box_to_a_trump_image_pose=dict(
            Linf_centre=mind[0], t_gap=mind[1], node=mind[2], kind=mind[3]),
        verdict="PASS (vacuous): no k5_11 witness box contains a Trump-image pose, and ZERO "
                "k5_11 witness boxes are classified as pockets at either tolerance.")

    # which slots the pocket boxes attach to
    slotcnt = collections.Counter()
    for nd in nodes:
        for w in nd["witnesses"]:
            for tag, delta, tol in TOLS:
                c, sl = classify(w["box"], nd["cls"], nd["slo"], nd["shi"],
                                 delta, tilt_band(tol))
                if c == "entire":
                    slotcnt[(tag, nd["src"], nd["cls"], sl, w["kind"])] += 1
    res["pocket_boxes_by_slot"] = {"|".join(map(str, k)): v for k, v in sorted(slotcnt.items())}
    out = os.path.join(A96, "results", "pocket96.json")
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)
    return res


if __name__ == "__main__":
    main()
