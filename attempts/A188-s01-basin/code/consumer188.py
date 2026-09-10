"""A188 T3 -- the consumer test of the S01 LINE basin on the alive gallery pages.  READ-ONLY.

For every ALIVE page (A187's list; the S01 and S03 pages are the ones reported) and every
axis-parallel line through a row / column of the page's OWN pins (read from its record):

  contained   the page's conditioned box H has minchord(H, l) >= 1 for some admissible c, i.e. H is
              a full member of the band -- the LocalCompose YES leaf "H + (3 - k) other squares in
              the band" is dead by the S01 certificate; `needs_NO` = 3 - k boxes the NO children
              still have to supply (A187's caveat: containment is necessary, not sufficient);
  direct      k + minchord(H, l) > s0: the page itself is dead by A144's guard line (none expected);
  support     A107's representative configuration has (4 - k) DISTINCT non-pin squares with chord
              >= 1 on the line (the A116/A151 consumer's "inside N"); and the fraction of the LP
              dual-support weight whose chord on the best line is >= 1;
  growth      if not contained: (band half-width H would need) / W_ANY at the best c.

    python consumer188.py   -> results/consumer188.jsonl, results/consumed188.jsonl, a summary
"""
from __future__ import annotations

import json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib188 as L                          # noqa: E402

CGRID = Fr(1, 200)


def scan(box, orient, c_lo, c_hi):
    """max over an admissible c-grid of minchord(box, line c); returns (best c, minchord)."""
    best = (None, Fr(-1))
    c = Fr(c_lo)
    mid = Fr(str(round(0.5 * ((box.y0 + box.y1) if orient == "h" else (box.x0 + box.x1)), 4)))
    cands = []
    while c <= Fr(c_hi):
        cands.append(c); c += CGRID
    if Fr(c_lo) <= mid <= Fr(c_hi):
        cands.append(mid)
    for c in cands:
        m = L.minchord(box, orient, c)
        if m > best[1]:
            best = (c, m)
    return best


def is_pin_pose(x, y, pins):
    return any(abs(x - 0.5 * (p.x0 + p.x1)) < 0.03 and abs(y - 0.5 * (p.y0 + p.y1)) < 0.03 for p in pins)


def one_page(pg, ex, gal, certs):
    nid = pg["nid"]
    rec = L.load_record((gal.get(nid) or {}).get("record") or "")
    if not rec:
        return dict(page=pg["page"], nid=nid, error="no record")
    pins, free = L.record_pins_and_box(rec)
    names = [L.pin_name_of(p) for p in pins]
    lines = L.pin_lines([n for n in names if n])
    cfg = [(float(q[0]), float(q[1]), float(q[2])) for q in ((ex.get(nid) or {}).get("cfg") or [])]
    sup = [(q["cx"], q["cy"], q.get("theta", 0.0), float(q.get("y", 0.0))) for q in (rec.get("packing") or [])]
    frame = L.frame_of(pg["cls"])
    rows = []
    for (orient, key), (pn, c_lo, c_hi) in sorted(lines.items()):
        k = len(pn)
        c_lo2, c_hi2 = Fr(c_lo) + Fr(1, 1000), Fr(c_hi) - Fr(1, 1000)
        for hi, H in enumerate(free):
            c, m = scan(H, orient, c_lo2, c_hi2)
            if c is None:
                continue
            thr = Fr(1) if k < 3 else (L.S_RAT - k)
            inside = bool(m >= 1)
            direct = bool(k + m > L.S_RAT)
            # support at this c: non-pin squares of the representative with chord >= 1 (H's own
            # square is one of them if it is inside); the LP support weight fraction
            nfull = sum(1 for (x, y, t) in cfg if not is_pin_pose(x, y, pins)
                        and L.chord_of_pose(x, y, t, orient, c) >= 1 - 1e-9)
            tot = sum(w for (_, _, _, w) in sup)
            frac = (sum(w for (x, y, t, w) in sup if L.chord_of_pose(x, y, t, orient, c) >= 1 - 1e-9) / tot) if tot > 0 else None
            # growth: the half-width the band would need to hold H entirely at this c
            lo, hi = (H.y0, H.y1) if orient == "h" else (H.x0, H.x1)
            need = max(abs(hi - float(c)), abs(lo - float(c)))
            variant = "any"
            cert_id = "S01_%s_%s%s_k%d_%s" % (frame, orient, key.replace("/", "_"), k, variant)
            rows.append(dict(orient=orient, key=key, pins=pn, k=k, H=hi, c=float(c), minchord=float(m),
                             inside=inside, direct=direct, needs_NO=(3 - k) if inside else None,
                             support_full=nfull, support_inside=bool(k + nfull >= 4),
                             support_frac=(round(frac, 3) if frac is not None else None),
                             growth=round(need / float(L.W_ANY), 3),
                             cert=cert_id if cert_id in certs else None))
    best = None
    for r in rows:
        keyf = (0 if r["direct"] else 1, 0 if r["inside"] else 1, r["needs_NO"] if r["inside"] else 9,
                -r["minchord"])
        if best is None or keyf < best[0]:
            best = (keyf, r)
    b = best[1] if best else None
    return dict(page=pg["page"], nid=nid, cls=pg["cls"], frame=frame, family=pg["family"],
                s_family=pg.get("s_family"), level=pg["level"], n_free_boxes=len(free),
                box=[free[0].x0, free[0].x1, free[0].y0, free[0].y1, free[0].th0, free[0].th1] if free else None,
                pins=names, n_cfg=len(cfg), n_support=len(sup),
                contained=bool(b and b["inside"]), direct=bool(b and b["direct"]),
                needs_NO=(b["needs_NO"] if b and b["inside"] else None),
                support_inside=bool(any(r["support_inside"] for r in rows)),
                support_frac_best=max([r["support_frac"] or 0.0 for r in rows] or [0.0]),
                growth=(min(r["growth"] for r in rows) if rows and not (b and b["inside"]) else (1.0 if b else None)),
                best=b, lines=rows)


def main():
    pages = L.load_pages()
    ex, gal = L.load_extract(), L.load_gallery()
    certs = {json.loads(l)["id"] for l in open(os.path.join(L.RES, "s01_basin.jsonl"), encoding="utf-8")}
    out = [one_page(pg, ex, gal, certs) for pg in pages]
    p = os.path.join(L.RES, "consumer188.jsonl")
    with open(p, "w", encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")
    consumed = []
    for r in out:
        if r.get("error"):
            continue
        if r["direct"]:
            v = "RETIRED"
        elif r["contained"]:
            v = "CONTAINED_YES_LEAF (NO side owing: %d box(es))" % r["needs_NO"]
        else:
            continue
        b = r["best"]
        consumed.append(dict(page=r["page"], nid=r["nid"], cls=r["cls"], family=r["family"], verdict=v,
                             cert=b["cert"], cert_path="attempts/A188-s01-basin/results/s01_basin.jsonl#%s" % b["cert"],
                             line="%s=%.3f" % (b["orient"], b["c"]), k=b["k"], needs_NO=r["needs_NO"],
                             support_inside=r["support_inside"], support_frac=r["support_frac_best"],
                             theorem="docs/proofs/local_certificate_s01.md Theorem S01-LINE"))
    p2 = os.path.join(L.RES, "consumed188.jsonl")
    with open(p2, "w", encoding="utf-8") as fh:
        for r in consumed:
            fh.write(json.dumps(r) + "\n")
    for fam in ("S01", "S03", "ALL"):
        rs = [r for r in out if not r.get("error") and (fam == "ALL" or r["family"] == fam)]
        print("%s: %d pages | contained %d (needs_NO 0/1/2: %d/%d/%d) | direct %d | support inside %d | support_frac>=0.5: %d" % (
            fam, len(rs), sum(r["contained"] for r in rs),
            sum(1 for r in rs if r["needs_NO"] == 0), sum(1 for r in rs if r["needs_NO"] == 1),
            sum(1 for r in rs if r["needs_NO"] == 2), sum(r["direct"] for r in rs),
            sum(r["support_inside"] for r in rs), sum(1 for r in rs if r["support_frac_best"] >= 0.5)))
    for r in out:
        if r.get("error") or r["family"] not in ("S01", "S03"):
            continue
        b = r["best"] or {}
        print("  %-24s %-9s %s box y[%.3f,%.3f] x[%.3f,%.3f] | best %s=%.3f k=%d minchord %.3f %s needsNO=%s sup_full=%s frac=%s growth=%s" % (
            r["nid"][:24], r["cls"], r["family"], r["box"][2], r["box"][3], r["box"][0], r["box"][1],
            b.get("orient"), b.get("c", 0), b.get("k", 0), b.get("minchord", 0),
            "IN" if r["contained"] else "out", r["needs_NO"], b.get("support_full"), b.get("support_frac"), r["growth"]))
    print("wrote", p, "and", p2, "(%d rows)" % len(consumed))


if __name__ == "__main__":
    main()
