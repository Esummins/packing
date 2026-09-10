"""A188 T1 -- what S01 is, exactly.  READ-ONLY on A107.

Reads A107's S01 entry (attempts/A107-shadow-gallery/results/shadows.json: the side-4.000 family's
representative, trump5's five slots + six free squares), and answers, with exact chord bounds:

  * which axis-parallel line carries FOUR unit chords (the lock) and how much tangential room
    each of the four has inside its unit-chord band (the plateau's extent along the lock);
  * the exact side lower bound Lemma LINE-1 gives on the representative (>= 4);
  * the contact graph A107 recorded, the rattlers (squares with no contact at all), and the
    dimension count of the plateau (free motions at side exactly 4);
  * the t = tan(theta/2) values of every square (0 for the axis-aligned ones; the rattler f0's
    tilt is a FREE parameter, not a value).

    python s01exact188.py        -> notes/s01_identity.json + a printed summary
"""
from __future__ import annotations

import json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib188 as L                          # noqa: E402

SH = os.path.join(L.ATT, "A107-shadow-gallery", "results", "shadows.json")


def main():
    sh = [e for e in json.load(open(SH, encoding="utf-8")) if e["id"] == "S01"][0]
    s_star = sh["s"]
    slots = list(sh["slots"])
    free = [(x, y, t) for (x, y, t) in sh["free"]]
    names = ["f%d" % i for i in range(len(free))] + slots
    poses = {}
    for i, (x, y, t) in enumerate(free):
        poses["f%d" % i] = (x, y, t)
    for n in slots:
        x, y = L.slot_xy(n, Fr(4))
        poses[n] = (float(x), float(y), 0.0)
    # (1) the lock: every axis-parallel line at the grid of 1/200; count unit chords
    best = None
    lines = []
    for orient in ("h", "v"):
        for k in range(1, 800):
            c = k / 200.0
            full = [n for n, (x, y, t) in poses.items() if L.chord_of_pose(x, y, t, orient, c) >= 1 - 1e-9]
            tot = sum(L.chord_of_pose(x, y, t, orient, c) for (x, y, t) in poses.values())
            if len(full) >= 4:
                lines.append(dict(orient=orient, c=c, full=full, chord_sum=round(tot, 6)))
            if best is None or tot > best[0]:
                best = (tot, orient, c, full)
    # the horizontal lock family: the c-interval on which the SAME four squares are full
    fam = {}
    for ln in lines:
        key = (ln["orient"], tuple(ln["full"]))
        fam.setdefault(key, []).append(ln["c"])
    families = [dict(orient=o, squares=list(f), c_lo=min(cs), c_hi=max(cs), n=len(cs))
                for (o, f), cs in fam.items()]
    # (2) exact LINE-1 bound at the lock line (degenerate boxes = the poses themselves)
    lock = max(families, key=lambda d: d["c_hi"] - d["c_lo"]) if families else None
    exact = None
    if lock:
        c = Fr(round(0.5 * (lock["c_lo"] + lock["c_hi"]), 3))
        tot = Fr(0)
        terms = {}
        for n in lock["squares"]:
            x, y, t = poses[n]
            td = math.degrees(t) % 90.0
            # a hair-width box around the pose (A144's minchord_box is written for boxes with a
            # tilt bin; a zero-width bin at t = 0 hits its degenerate branch)
            b = L.Box(x - 1e-9, x + 1e-9, y - 1e-9, y + 1e-9, max(0.0, td - 1e-6), min(90.0, td + 1e-6))
            m = L.minchord(b, lock["orient"], c)
            terms[n] = str(m)
            tot += m
        exact = dict(c=str(c), terms=terms, chord_sum=str(tot), chord_sum_float=float(tot),
                     s_lower_bound_ge_4=bool(tot >= 4))
    # (3) contacts, rattlers, plateau count
    contacts = [(a["a"], a["b"], a["kind"]) for a in sh["analysis"]["contacts"]]
    walls = [(w["a"], w["b"]) for w in sh["analysis"]["walls"]]
    touched = {a for a, _, _ in contacts} | {b for _, b, _ in contacts} | {a for a, _ in walls}
    rattlers = [n for n in names if n not in touched]
    # free motions at side exactly 4: a square keeps s = 4 if it is not in the lock and can slide;
    # count coordinates not fixed by a contact (rough: 3 per rattler, 1 per one-contact square)
    deg = {n: 0 for n in names}
    for a, b, _ in contacts:
        deg[a] += 1; deg[b] += 1
    for a, _ in walls:
        deg[a] += 1
    tvals = {n: (str(Fr(0)) if abs(math.degrees(t) % 90.0) < 1e-3 else
                 "free (rattler)" if n in rattlers else "%.6f" % math.tan(0.5 * (t % (math.pi / 2))))
             for n, (x, y, t) in poses.items()}
    out = dict(source=os.path.relpath(SH, L.ROOT), s_star=s_star, slots=slots,
               free=[dict(name="f%d" % i, x=x, y=y, theta_deg=math.degrees(t)) for i, (x, y, t) in enumerate(free)],
               lock_families=families, lock=lock, exact_line_bound=exact, best_line=dict(
                   chord_sum=best[0], orient=best[1], c=best[2], full=best[3]),
               contacts=contacts, walls=walls, rattlers=rattlers, contact_degree=deg, t_values=tvals,
               gamma_min=(math.sqrt(2) - 1) / 2, W_ANY=str(L.W_ANY))
    p = os.path.join(L.NOTES, "s01_identity.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print("S01 s* =", s_star)
    print("lock families (>= 4 unit chords on one axis-parallel line):")
    for f in families:
        print("  %s  c in [%.3f, %.3f]  squares %s" % (f["orient"], f["c_lo"], f["c_hi"], f["squares"]))
    print("exact LINE-1 bound at the lock:", exact)
    print("rattlers:", rattlers, " contact degrees:", deg)
    print("wrote", p)


if __name__ == "__main__":
    main()
