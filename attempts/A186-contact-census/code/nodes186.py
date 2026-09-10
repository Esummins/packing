"""A186 -- the boxed assignments of c0_Y1033 as BODIES (A116 pattern) carrying their multibox PIECES.

Reads A182's journal (attempts/A180-forced-first-assignment/results/journal/c0_Y1033.jsonl, READ-ONLY):
every complete assignment that is alive ('branch' record, six cells assigned, dead None) with its
`capture` = the pieces [x0, x1, y0, y1, th0_deg, th1_deg] of every role at the multibox fixed point.

Bodies: the five pins on their slot lines (A57 frame, pin slack 1e-6: the record's pin boxes are
4e-8 wide and their tilt bins 3.4e-6 deg, a corner moves by <= tilt * sqrt2/2 -- [S]); every boxed
free role (H, F1..F5) a PieceBody whose centre box DEPENDS ON THE TILT CELL: the hull of the pieces
whose tilt sub-bin meets the cell (a superset of the poses of the cell -- sound).

    python nodes186.py            # writes results/assignments186.json (the 23 alive assignments)
"""
from __future__ import annotations
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
RES = os.path.join(BASE, "results")
os.makedirs(RES, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "attempts", "A116-local-selection-tree", "code"))
import a116lib as A                                           # noqa: E402  READ-ONLY (blas1 first)

IV = A.IV
S0 = A.S0
JOURNAL = os.path.join(ROOT, "attempts", "A180-forced-first-assignment", "results", "journal", "c0_Y1033.jsonl")
PIN_SLOT = {"P0": "BL(0,0)", "P1": "BL(1,0)", "P2": "BL(0,1)", "P3": "BR(0,0)", "P4": "TR(0,0)"}
PIN_SLACK = 1e-6


def load_records(path=JOURNAL):
    """label -> the LAST 'branch' record of every complete alive assignment (six cells assigned)."""
    recs = {}
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        lab = r.get("label", "")
        if r.get("kind") == "branch" and "?" not in lab and lab.count("=") == 6 and r.get("dead") is None \
                and r.get("capture"):
            recs[lab] = r
    return recs


def short_label(lab):
    """'BL11=F1+F2 BR01=H+F1 TR01=H+F1 TL00=F2+F3 BL02=F2+F4 TR10=F2+F5'."""
    out = []
    for part in lab.split("/")[1:]:
        cell, rhs = part.split(":", 1)[1].split("=")
        out.append(cell.replace("(", "").replace(",", "").replace(")", "") + "=" + rhs.split("@")[0])
    return " ".join(out)


class PieceBody(A.Body):
    """A free body whose centre box is the hull of the pieces meeting the current tilt cell."""
    __slots__ = ("pieces",)

    def __init__(self, name, pieces, vi, ti):
        pcs = [(p[0], p[1], p[2], p[3], math.radians(p[4]), math.radians(p[5])) for p in pieces]
        x0 = min(p[0] for p in pcs); x1 = max(p[1] for p in pcs)
        y0 = min(p[2] for p in pcs); y1 = max(p[3] for p in pcs)
        t0 = min(p[4] for p in pcs); t1 = max(p[5] for p in pcs)
        super().__init__(name, "free", x0=x0, x1=x1, y0=y0, y1=y1, t0=t0, t1=t1, vi=vi, ti=ti,
                         anchor=(0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (t0 + t1)))
        self.pieces = pcs

    def pieces_in(self, cell):
        a, b = cell
        return [p for p in self.pieces if max(p[4], a) <= min(p[5], b) + 1e-15]

    def box_for(self, cell):
        """(x0, x1, y0, y1) hull of the pieces meeting the tilt cell, or None (no pose there)."""
        P = self.pieces_in(cell)
        if not P:
            return None
        return (min(p[0] for p in P), max(p[1] for p in P), min(p[2] for p in P), max(p[3] for p in P))

    def xrange(self, s_lo, s_hi, cells=None):
        if cells and self.name in cells:
            bx = self.box_for(cells[self.name])
            if bx is not None:
                return IV(bx[0], bx[1]), IV(bx[2], bx[3])
        return IV(self.x0, self.x1), IV(self.y0, self.y1)

    def pose_iv(self, s_lo, s_hi, cells=None):
        xr, yr = self.xrange(s_lo, s_hi, cells)
        return (xr, yr, self.tilt(cells))

    def specialise(self, cells):
        """A plain Body for the LP of one tilt cell (Rows reads x0..y1 and t0, t1 directly)."""
        if not cells or self.name not in cells:
            return self
        cell = cells[self.name]
        bx = self.box_for(cell)
        if bx is None:
            return None
        return A.Body(self.name, "free", x0=bx[0], x1=bx[1], y0=bx[2], y1=bx[3], t0=cell[0], t1=cell[1],
                      vi=self.vi, ti=self.ti, anchor=self.anchor)


def build_bodies(rec, pin_slack=PIN_SLACK):
    """[bodies], nv for one assignment record: pins first (slot lines), then the boxed free roles."""
    cap = rec["capture"]
    bodies, nv = [], 1
    for p in ("P0", "P1", "P2", "P3", "P4"):
        ax, ay = A.slot_affine(PIN_SLOT[p])
        bodies.append(A.Body(p, "pin", ax=ax, ay=ay, hh=pin_slack, vi=nv,
                             anchor=(A.slot_xy(PIN_SLOT[p], S0)[0], A.slot_xy(PIN_SLOT[p], S0)[1], 0.0)))
        nv += 2
    free = [r for r in rec["roles"] if r not in PIN_SLOT]
    for r in free:
        bodies.append(PieceBody(r, cap[r]["pieces"], nv, None))
        nv += 2
    for b in bodies:
        if b.kind == "free":
            b.ti = nv; nv += 1
    return bodies, nv


def check_pins(rec):
    """[S] the record's pin hulls sit on the slot lines at s0 within 1e-7."""
    worst = 0.0
    for p, slot in PIN_SLOT.items():
        h = rec["hull"][p]
        x, y = A.slot_xy(slot, S0)
        worst = max(worst, abs(h[0] - x), abs(h[1] - x), abs(h[2] - y), abs(h[3] - y), math.radians(h[5]) * 0.71)
    return worst


def main():
    recs = load_records()
    out = []
    for lab, r in sorted(recs.items(), key=lambda kv: (-len(kv[1]["roles"]), kv[0])):
        bodies, nv = build_bodies(r)
        out.append(dict(label=lab, short=short_label(lab), n_roles=len(r["roles"]), budget=11 - len(r["roles"]),
                        corners=r.get("corners"), assign=r.get("assign"), pin_worst=check_pins(r),
                        hull=r["hull"], n_pieces={b.name: len(b.pieces) for b in bodies if b.kind == "free"},
                        kept=r.get("kept"), invariant=r.get("invariant"), journal_i=r.get("i")))
    json.dump(out, open(os.path.join(RES, "assignments186.json"), "w"), indent=1)
    for a in out:
        print(a["budget"], a["short"], a["n_pieces"], "pin_worst %.1e" % a["pin_worst"], "inv", a["invariant"])
    print(len(out), "alive complete assignments;", sum(1 for a in out if a["budget"] == 0), "at budget 0")


if __name__ == "__main__":
    main()
