"""A144 -- the guard-line COLUMN, injected into A57's node LP without editing any A57 file.

A57's node LP (`lpbox.run`, driven by `caselp.solve_node`) is the covering LP: primal columns are
atom orbits, primal rows are placements.  A guard line l enters as ONE MORE PRIMAL COLUMN --
a measure of density z >= 0 spread along l -- with

    objective coefficient  rhs(l) = s - SUM_pins minchord - minchord(H)     (guardline.guard_row)
    coefficient in row Q   |l n Q|                                          (guardline (CH))

Soundness (A144 notes/spec.md Sec.1): for a packing consistent with the hypothesis,
budget <= SUM_i mu(Q_i) <= SUM_k m_k w_k + SUM_l z_l rhs(l) = objective, so tau < budget still
kills.  Adding columns can only lower tau.

THE WRAPPER.  `lpbox.run` builds `Model(...)` and `RowOracle(...)` by their module-global names, so
this module swaps in two subclasses and restores them afterwards (A131/A135's pattern: no frozen
or campaign file is touched).

  * `GuardModel` adds the G guard columns FIRST, so HiGHS column index = G + orbit index; the only
    overrides are `add_row` (offset the orbit indices, append the chord coefficients), `solve`
    (split the solution vector into z and w) and `prune_cols` (offset).  `add_orbit`, `prune_rows`,
    `packing_images` and the checkpoint are the frozen ones.
  * `GuardRowOracle` overrides ONLY `mass` and `mass_many`, so the separation oracle sees the true
    measure mu = atoms + SUM_l z_l H^1|_l.  This matters: with the stock oracle the LP would keep
    adding rows the line already covers and converge back to the atoms-only optimum.  The internal
    prefix-sum cell prefilter of `exact_theta` stays atoms-only, which is a conservative SUPERSET
    (the line mass is non-negative), so no violated placement is filtered out by it; the reported
    `minmass` is then the true one, computed by the overridden `mass_many` on the candidates.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import guardline as G                                                   # noqa: E402
import lpbox                                                            # noqa: E402 (read-only)
import highspy                                                          # noqa: E402

# LP-side half-side: the rows are the SHRUNK squares (lpbox.EPS_GEO), and using the shrunk chord in
# the column is conservative on both sides of the bridge -- it under-states what the line covers,
# and SUM_i |l n Q_i^shrunk| <= SUM_i |l n Q_i| <= rhs(l) still holds.
LP_HALF = 0.5 - lpbox.EPS_GEO

_ACTIVE = dict(lines=[], z=None, off=None, orient=None)


def _chord_coeffs(lines, cx, cy, th, a=LP_HALF):
    return np.array([G.chord_float(a, th, L.foff - (cy if L.orient == "h" else cx))
                     for L in lines])


def _line_mass_many(C, theta):
    """SUM_l z_l |l n Q(c, theta)| for centres C (m,2) at one theta."""
    lines, z = _ACTIVE["lines"], _ACTIVE["z"]
    C = np.asarray(C, float).reshape(-1, 2)
    if not lines or z is None or len(C) == 0 or not np.any(z > 1e-14):
        return np.zeros(len(C))
    out = np.zeros(len(C))
    TH = np.full(len(C), float(theta))
    for k, L in enumerate(lines):
        if z[k] <= 1e-14:
            continue
        V = L.foff - (C[:, 1] if L.orient == "h" else C[:, 0])
        out += z[k] * G.chord_many(LP_HALF, TH, V)
    return out


class GuardModel(lpbox.Model):
    LINES = []                       # set by the driver before solve_node

    def __init__(self, s, n, sym, tbox, verbose=False, hyp=None):
        super().__init__(s, n, sym, tbox, verbose=verbose, hyp=hyp)
        self.lines = list(GuardModel.LINES)
        self.G = len(self.lines)
        self.cost = np.array([float(L.cost) for L in self.lines]) if self.G else np.zeros(0)
        for c in self.cost:                       # no rows yet: empty columns
            self.h.addCol(float(c), 0.0, highspy.kHighsInf, 0,
                          np.zeros(0, np.int32), np.zeros(0, float))
        self.z = np.zeros(self.G)
        _ACTIVE.update(lines=self.lines, z=self.z)

    # ---- rows: orbit index k is HiGHS column G + k; the guard columns take the chord coefficient
    def add_row(self, cx, cy, th):
        al = self.tbox.alpha(th)
        if al is None:
            self.n_rejected += 1
            return False
        lo, hi = lpbox.centre_range(self.s, th)
        if not (lo - 1e-9 <= cx <= hi + 1e-9 and lo - 1e-9 <= cy <= hi + 1e-9):
            self.n_rejected += 1
            return False
        if self.hyp is not None and not self.hyp.ok(cx, cy, th):
            self.n_rejected += 1
            return False
        m = lpbox.inside_mask(self.P, cx, cy, th)
        cnt = np.bincount(self.P_orb[m], minlength=len(self.orbits))
        idx = np.nonzero(cnt)[0]
        gv = _chord_coeffs(self.lines, cx, cy, th) if self.G else np.zeros(0)
        gidx = np.nonzero(gv > 1e-12)[0]
        if len(idx) == 0 and len(gidx) == 0:
            return False
        key = hash((idx.tobytes(), cnt[idx].tobytes(), gidx.tobytes(),
                    np.round(gv[gidx], 9).tobytes(), round(al, 12)))
        if key in self.rowkeys:
            return False
        self.rowkeys.add(key)
        cols = np.concatenate([gidx, idx + self.G]).astype(np.int32)
        vals = np.concatenate([gv[gidx], cnt[idx].astype(float)])
        self.h.addRow(al, highspy.kHighsInf, len(cols), cols, vals)
        self.rows.append((float(cx), float(cy), float(th)))
        self._rowarr = None
        self.row_alpha.append(al)
        self.rowkey_list.append(key)
        self.row_strikes.append(0)
        return True

    def solve(self):
        obj = super().solve()
        full = self.w
        self.z = np.array(full[:self.G])
        self.w = np.array(full[self.G:])
        _ACTIVE.update(lines=self.lines, z=self.z)
        return obj

    def prune_cols(self, strikes=2, rc_tol=1e-4):
        """frozen prune_cols with the guard offset; guard columns are never pruned."""
        if strikes <= 0 or self.w is None or not self.orbits:
            return 0
        sol = self.h.getSolution()
        rc = np.array(sol.col_dual)[self.G:]
        cand = (self.w <= 1e-12) & (rc > rc_tol)
        cand[:self.n_protected] = False
        st = np.where(cand, np.array(self.col_strikes) + 1, 0)
        kill = np.nonzero(st >= strikes)[0]
        if len(kill) == 0:
            self.col_strikes = st.tolist()
            return 0
        self.h.deleteCols(len(kill), (kill + self.G).astype(np.int32))
        keep = np.ones(len(self.orbits), dtype=bool)
        keep[kill] = False
        for k in kill:
            self.orbkeys.discard(self.orbits[k]["key"])
        self.orbits = [o for o, kp in zip(self.orbits, keep) if kp]
        self.P = np.vstack([o["pts"] for o in self.orbits]) if self.orbits else np.zeros((0, 2))
        self.P_orb = (np.concatenate([np.full(len(o["pts"]), i)
                                      for i, o in enumerate(self.orbits)])
                      if self.orbits else np.zeros(0, dtype=int))
        self.w = self.w[keep]
        self.col_strikes = st[keep].tolist()
        self.rowkeys = set()
        self.rowkey_list = []
        for r, (cx, cy, th) in enumerate(self.rows):
            m = lpbox.inside_mask(self.P, cx, cy, th)
            cnt = np.bincount(self.P_orb[m], minlength=len(self.orbits))
            idx = np.nonzero(cnt)[0]
            key = hash((idx.tobytes(), cnt[idx].tobytes(), round(self.row_alpha[r], 12)))
            self.rowkeys.add(key)
            self.rowkey_list.append(key)
        return int(len(kill))

    def guard_report(self):
        return [dict(line=L.to_json(), cost=float(L.cost), z=float(zz))
                for L, zz in zip(self.lines, self.z)]


class GuardRowOracle(lpbox.RowOracle):
    def mass(self, cx, cy, theta):
        return (super().mass(cx, cy, theta)
                + float(_line_mass_many(np.array([[cx, cy]]), theta)[0]))

    def mass_many(self, C, theta):
        C = np.asarray(C, float).reshape(-1, 2)
        return super().mass_many(C, theta) + _line_mass_many(C, theta)


class installed:
    """`with installed(lines): solve_node(...)` -- swaps the two classes in and out."""

    def __init__(self, lines):
        self.lines = list(lines)

    def __enter__(self):
        self._M, self._R = lpbox.Model, lpbox.RowOracle
        GuardModel.LINES = self.lines
        _ACTIVE.update(lines=self.lines, z=np.zeros(len(self.lines)))
        lpbox.Model, lpbox.RowOracle = GuardModel, GuardRowOracle
        return self

    def __exit__(self, *a):
        lpbox.Model, lpbox.RowOracle = self._M, self._R
        GuardModel.LINES = []
        _ACTIVE.update(lines=[], z=None)
        return False


def attach_costs(lines, rows):
    """give each Line the rhs of its guard row (guardline.guard_row output)."""
    out = []
    for L, r in zip(lines, rows):
        L.cost = float(r["rhs"])
        L.rhs_exact = r["rhs"]
        out.append(L)
    return out
