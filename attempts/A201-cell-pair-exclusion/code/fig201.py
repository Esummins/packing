"""A201 -- the page after the fast steps WITH the cell-pair table, drawn from certs/pe201_<nid>[_pad0].json (one panel per
pad) into docs/residue_map/pairexcl201_<nid>.svg.  Drawing rules = A200's live200 (READ-ONLY import: pins blue stock
boxes, H black clipped box with its hypothesis square at an ADMISSIBLE sampled pose (dashed if none found),
instantiated meeters purple, cells GREY STIPPLE where some slot's meeter still has surviving centres -- never green,
the count witness cells yellow) plus, in red, every pair the table EXCLUDED among A200's witness cover and the rule
that did it, and a note on each panel saying what it IS.  Nothing is recomputed.
    python fig201.py [nid ...]      (default: every certificate)
"""
import glob
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A200-k516-quick", "code"))
import live200 as L                                            # noqa: E402  READ-ONLY (A200)

CERTS = os.path.join(HERE, "..", "certs")
OUTD = os.path.join(ROOT, "docs", "residue_map")
S0 = L.S0
text = L.text
RULECOL = {"A1": "#6a1b9a", "CN": "#c62828", "EXACT": "#e65100"}


def hull_centre(rec_hull):
    return 0.5 * (rec_hull[0] + rec_hull[1]), 0.5 * (rec_hull[2] + rec_hull[3])


def overlay(cert, body, ox, oy, S):
    """red segments for the excluded pairs of A200's witness cover (round 1), labelled by rule."""
    X = lambda x: ox + x * S
    Y = lambda y: oy + (S0 - y) * S
    rounds = cert.get("rounds") or []
    wc = (rounds[0].get("witness_check") if rounds else None) or {}
    pe = cert.get("pair_excl") or {}
    excl_by = {}
    for r in pe.get("rounds", []):
        for e in r.get("excl", []):
            if "a" not in e:                                   # a COVER refutation has no pair
                continue
            excl_by[(str(e["a"]), str(e["b"]))] = e
            excl_by[(str(e["b"]), str(e["a"]))] = e
    n = 0
    for p in wc.get("pairs", []):
        if p.get("compatible"):
            continue
        e = excl_by.get((str(p["a"]), str(p["b"])))
        if not e:
            continue
        (xa, ya), (xb, yb) = hull_centre(e["hull_a"]), hull_centre(e["hull_b"])
        col = RULECOL.get(e["rule"], "#c62828")
        for h in (e["hull_a"], e["hull_b"]):
            body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" stroke-width="1.6"/>' % (
                X(h[0]), Y(h[3]), max(1, (h[1] - h[0]) * S), max(1, (h[3] - h[2]) * S), col))
        body.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.2"/>' % (X(xa), Y(ya), X(xb), Y(yb), col))
        lab = "%s %s" % (e["rule"], ("max dist %.3f" % e["maxdist"]) if e["rule"] == "CN" else (("l-inf %.3f" % e["linf_max"]) if e["rule"] == "A1"
                                                                                                 else ("cell pair %s" % e.get("cells") if e.get("level") == "cell" else "option pair: one side empties")))
        body.append(text(X(0.5 * (xa + xb)), Y(0.5 * (ya + yb)) - 4, lab, 7.5, col, True, "middle"))
        n += 1
    return n


def side(cert, body, x, y):
    v = cert.get("verdict")
    col = "#c62828" if v == "DEAD" else "#2e7d32"
    lines = [("%s at pad %s: %s%s" % (cert["nid"], cert.get("pad"), v, ("  [killed at step: %s]" % cert["step_killed"]) if cert.get("step_killed") else ""), 11, col, True)]
    if cert.get("leaf"):
        s = str(cert["leaf"])
        while s:
            lines.append((s[:110], 8, col, False)); s = s[110:]
    lines.append(("WHAT THIS IS: the page's node after A200's fast steps (normalise / options / union caps / assignment count) with the count's pairwise test", 8, "#333", False))
    lines.append(("replaced by the CELL-PAIR TABLE -- (a) Lemma A1, (b) Lemma CN (max Euclidean centre distance of two hulls < 1 => excluded), (c) the seeded pair clip", 8, "#333", False))
    lines.append(("on the two rows' own pieces against each other's K' (a side with no pose left => excluded; cell pair first, then option pair); the count re-runs until", 8, "#333", False))
    lines.append(("it is infeasible or its cover is VERIFIED pair by pair.  'cell-pair mutual exclusion' is the PI's reading of 2026-09-10.  Undecided cells: grey stipple, never green.", 8, "#333", False))
    cs = [st for st in (cert.get("steps") or []) if st["step"] == "count"]
    if cs:
        lines.append(("count covers refuted: %s pairwise + %s by the joint clip; last cover verified pair by pair: %s; joint clip alive: %s" % (
            sum(int(st.get("refutations", 0)) for st in cs), sum(int(st.get("joint_refutations", 0) or 0) for st in cs),
            cs[-1].get("cover_verified"), cs[-1].get("cover_joint_ok")), 8, "#000", True))
    steps = cert.get("steps") or []
    lines.append(("STEPS (s): " + " > ".join("%s%s %.1f" % (st["step"], ("[" + str(st.get("label", "")) + "]") if st.get("label") else "", st.get("seconds", 0)) for st in steps), 7.5, "#333", False))
    lines.append(("whole run %.0f s, %d exact tests, %d round(s); lam %s; window pending %s" % (float(cert.get("seconds") or 0), len(cert.get("tests") or []), len(cert.get("rounds") or []), cert.get("lam"), cert.get("window_pending")), 7.5, "#555", False))
    for k, rd in enumerate(cert.get("rounds") or []):
        pe = rd.get("pair_excl") or {}
        cn, cc = rd.get("count_nochord") or {}, rd.get("count_chord") or {}
        lines.append(("round %d: count no-chords %s (%s nodes, %d exclusions used) / chords %s (%s nodes, %d used); caps %s%s" % (
            rd["round"], cn.get("feasible"), cn.get("nodes"), len(cn.get("excl_used") or []), cc.get("feasible"), cc.get("nodes"), len(cc.get("excl_used") or []),
            rd.get("caps"), ("; DEAD: " + rd["dead"][:70]) if rd.get("dead") else ""), 8, "#000", True))
        if pe:
            lines.append(("   table: %d lookups; exclusions A1 %s / CN %s / EXACT %s (exact nodes tested %s, %.1f s of the %.0f s budget, %s pairs left undecided by budget)" % (
                pe.get("lookups", 0), pe.get("by_rule", {}).get("A1"), pe.get("by_rule", {}).get("CN"), pe.get("by_rule", {}).get("EXACT"),
                pe.get("exact_tested"), float(pe.get("exact_seconds") or 0), float(pe.get("budget") or 0), pe.get("undecided_budget")), 7.5, "#333", False))
        wc = rd.get("witness_check")
        if wc:
            lines.append(("   A200's witness cover (%d rows found of %d): %s" % (wc["n_found"], wc["n_keys"], "DEAD" if wc["dead"] else "every pair compatible"), 8, "#c62828" if wc["dead"] else "#2e7d32", True))
            for p in wc["pairs"]:
                if not p["compatible"]:
                    lines.append(("      %s | %s : %s" % (p["a"], p["b"], p["why"]), 7, RULECOL.get(p["rule"], "#c62828"), False))
    excl = [e for r in (cert.get("pair_excl") or {}).get("rounds", []) for e in r.get("excl", [])]
    if excl:
        lines.append(("all exclusions found (%d), by rule:" % len(excl), 8, "#000", True))
        for rule in ("COVER", "EXACT", "CN", "A1"):
            es = [e for e in excl if e["rule"] == rule]
            for e in es[:8]:
                if rule == "COVER":
                    lines.append(("   COVER (joint clip of a pairwise-verified cover): dead row %s; sub-cover %s; %s" % (
                        e.get("dead"), e.get("subcover") or "whole cover", (e.get("why") or "")[:60]), 6.5, "#880e4f", False))
                else:
                    lines.append(("   %s  %s | %s  %s" % (rule, e["a"], e["b"], (e.get("why") or "")[:70]), 6.5, RULECOL[rule], False))
            if len(es) > 8:
                lines.append(("   ... %d more %s exclusions in the certificate" % (len(es) - 8, rule), 6.5, RULECOL.get(rule, "#880e4f"), False))
    if cert.get("decisive_rules"):
        lines.append(("DECISIVE RULES of the kill: %s" % cert["decisive_rules"], 9, "#c62828", True))
    yy = y
    for t, sz, c, b in lines:
        t = str(t)
        while True:
            body.append(text(x, yy, t[:150], sz, c, b))
            yy += sz + 4
            t = t[150:]
            if not t:
                break
    return yy


def page_svg(nid, certs):
    S, TW = 118, 700
    PW = int(S0 * S) + 20
    W = len(certs) * (PW + TW) + 40
    body = [text(20, 22, "%s -- A201 cell-pair mutual exclusion (PI, 2026-09-10) in A200's quick chain: the page AFTER THE FAST STEPS, one panel per pad" % nid, 13, "#000", True),
            text(20, 38, "grey stipple = cells where some forced slot's meeter still has surviving centres (undecided); white = none; dashed colour = slot unit + its union box; blue = pins; "
                 "black = H's clipped box with its hypothesis square at an admissible sampled pose (dashed if none); purple = instantiated meeters; yellow = the count's witness cells;", 8, "#444"),
            text(20, 50, "RED = A200's witness pairs the table excludes (rule + number).  Drawn from the certificates, nothing recomputed; rendered %s" % time.strftime("%Y-%m-%d %H:%M:%S"), 8, "#444")]
    y0, ybot = 70, 70
    for k, c in enumerate(certs):
        ox = 20 + k * (PW + TW)
        body.append(text(ox, y0 - 6, "PANEL %d: %s (pad %s; written %s)" % (k + 1, c["_file"], c.get("pad"), time.strftime("%H:%M:%S", time.localtime(c["_mtime"]))), 9, "#000", True))
        yb = L.panel(c, body, ox, y0, S)
        overlay(c, body, ox, y0, S)
        yt = side(c, body, ox + PW + 10, y0 + 12)
        ybot = max(ybot, yb, yt)
    return "\n".join(['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, sans-serif" style="background:#fff">' % (W, ybot + 20), L.defs()] + body + ["</svg>"])


def render_page(nid):
    certs = []
    for f in sorted(glob.glob(os.path.join(CERTS, "pe201_%s*.json" % nid))):
        if os.path.basename(f) not in ("pe201_%s.json" % nid, "pe201_%s_pad0.json" % nid):
            continue
        c = json.load(open(f, encoding="utf-8"))
        c["_file"], c["_mtime"] = os.path.basename(f), os.path.getmtime(f)
        certs.append(c)
    if not certs:
        return None
    certs.sort(key=lambda c: {"g1": 0, "window": 0, "zero": 1}.get(c.get("pad"), 2))
    os.makedirs(OUTD, exist_ok=True)
    p = os.path.join(OUTD, "pairexcl201_%s.svg" % nid)
    doc = page_svg(nid, certs)                                 # built BEFORE the file is opened: a failure leaves the old page
    open(p, "w", encoding="utf-8").write(doc)
    import xml.dom.minidom
    xml.dom.minidom.parse(p)
    return p


if __name__ == "__main__":
    nids = sys.argv[1:] or sorted(set(os.path.basename(f)[6:-5].replace("_pad0", "") for f in glob.glob(os.path.join(CERTS, "pe201_*.json"))))
    for nid in nids:
        print(nid, render_page(nid), flush=True)
