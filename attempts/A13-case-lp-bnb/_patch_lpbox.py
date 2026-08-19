"""one-off patch script: lp_measure_box.py (A12 copy) -> lpbox.py with C1 symmetry, hypothesis filter, log hook"""
src = open('lpbox.py').read()
n0 = len(src)

def rep(a, b):
    global src
    assert src.count(a) == 1, ("pattern not unique/found", a[:60], src.count(a))
    src = src.replace(a, b)

rep('''    def __init__(self, kind, s):
        assert kind in ("D4", "C4")
        self.kind, self.s = kind, s
        self.n_img = 8 if kind == "D4" else 4

    def point_images(self, x, y):
        s = self.s
        rot = [(x, y), (s - y, x), (s - x, s - y), (y, s - x)]
        if self.kind == "C4":
            return rot
        return rot + [(s - a, b) for (a, b) in rot]''',
'''    def __init__(self, kind, s):
        assert kind in ("D4", "C4", "C1")
        self.kind, self.s = kind, s
        self.n_img = {"D4": 8, "C4": 4, "C1": 1}[kind]
        # lower corner of the row (centre) domain: quadrant for C4/D4, whole square for C1
        self.dom_lo = s / 2 if kind != "C1" else 0.0

    def point_images(self, x, y):
        s = self.s
        if self.kind == "C1":
            return [(x, y)]
        rot = [(x, y), (s - y, x), (s - x, s - y), (y, s - x)]
        if self.kind == "C4":
            return rot
        return rot + [(s - a, b) for (a, b) in rot]''')

rep('''    def placement_images(self, cx, cy, th):
        s = self.s
        out = []''', '''    def placement_images(self, cx, cy, th):
        s = self.s
        if self.kind == "C1":
            return [(cx, cy, th)]
        out = []''')

rep('''    def canon_point(self, x, y):
        s = self.s
        if self.kind == "D4":''', '''    def canon_point(self, x, y):
        s = self.s
        if self.kind == "C1":
            return x, y
        if self.kind == "D4":''')

rep('''        s = self.s
        xs = np.arange(s / 2, s + 1e-9, grid)''', '''        s = self.s
        xs = np.arange(self.dom_lo, s + 1e-9, grid)''')

rep('''        m = (pts[:, 0] >= s / 2 - 1e-9) & (pts[:, 1] >= s / 2 - 1e-9)''',
    '''        m = (pts[:, 0] >= self.dom_lo - 1e-9) & (pts[:, 1] >= self.dom_lo - 1e-9)''')

rep('''    def __init__(self, s, n, sym, tbox, verbose=False):
        self.s, self.n = s, n
        self.sym, self.tbox = sym, tbox''', '''    def __init__(self, s, n, sym, tbox, verbose=False, hyp=None):
        self.s, self.n = s, n
        self.sym, self.tbox = sym, tbox
        self.hyp = hyp              # optional hypothesis filter with .ok(cx,cy,th) and .ok_many(C, th)''')
rep('''        if not (lo - 1e-9 <= cx <= hi + 1e-9 and lo - 1e-9 <= cy <= hi + 1e-9):
            self.n_rejected += 1
            return False
        m = inside_mask(self.P, cx, cy, th)''', '''        if not (lo - 1e-9 <= cx <= hi + 1e-9 and lo - 1e-9 <= cy <= hi + 1e-9):
            self.n_rejected += 1
            return False
        if self.hyp is not None and not self.hyp.ok(cx, cy, th):
            self.n_rejected += 1
            return False
        m = inside_mask(self.P, cx, cy, th)''')

rep('''    def __init__(self, s, P, w, tbox, delta=0.002, cstep=0.02, n_theta=91, exact=True):
        self.s = s
        self.exact = exact
        self.tbox = tbox''', '''    def __init__(self, s, P, w, tbox, delta=0.002, cstep=0.02, n_theta=91, exact=True, hyp=None, dom_lo=None):
        self.s = s
        self.exact = exact
        self.tbox = tbox
        self.hyp = hyp
        self.dom_lo = s / 2 if dom_lo is None else dom_lo''')
rep('''        xs = np.linspace(lo, hi, n + 1)
        xs = xs[xs >= s / 2 - 1e-12]
        X, Y = np.meshgrid(xs, xs, indexing="ij")
        C = np.stack([X.ravel(), Y.ravel()], axis=1)
        U = rot_coords(self.P, theta)
        d = self.delta''', '''        xs = np.linspace(lo, hi, n + 1)
        xs = xs[xs >= self.dom_lo - 1e-12]
        X, Y = np.meshgrid(xs, xs, indexing="ij")
        C = np.stack([X.ravel(), Y.ravel()], axis=1)
        U = rot_coords(self.P, theta)
        d = self.delta''')
rep('''        # admissible domain [lo,hi] x [lo,hi] intersected with the quadrant [s/2, hi]^2 -> corners in the rotated frame
        dom = np.array([[s / 2, s / 2], [hi, s / 2], [hi, hi], [s / 2, hi]])''', '''        # admissible domain [lo,hi] x [lo,hi] intersected with [dom_lo, hi]^2 -> corners in the rotated frame
        dl = max(lo, self.dom_lo)
        dom = np.array([[dl, dl], [hi, dl], [hi, hi], [dl, hi]])''')
rep('''        ok = (cx >= s / 2 - tol) & (cx <= hi + tol) & (cy >= s / 2 - tol) & (cy <= hi + tol)''',
    '''        ok = (cx >= dl - tol) & (cx <= hi + tol) & (cy >= dl - tol) & (cy <= hi + tol)''')
rep('''            x = np.clip(x, max(lo, s / 2), hi); y = np.clip(y, max(lo, s / 2), hi)''',
    '''            x = np.clip(x, dl, hi); y = np.clip(y, dl, hi)''')
rep('''        C = np.vstack(pts)
        m = self.mass_many(C, theta)
        keep = m < thresh - 1e-12
        C, m = C[keep], m[keep]''', '''        C = np.vstack(pts)
        if self.hyp is not None:
            C = C[self.hyp.ok_many(C, theta)]
            if len(C) == 0:
                return np.zeros((0, 2)), np.zeros(0)
        m = self.mass_many(C, theta)
        keep = m < thresh - 1e-12
        C, m = C[keep], m[keep]''')
rep('''                x = min(max(cx + dcx * step_c, lo), hi); y = min(max(cy + dcy * step_c, lo), hi)
                m = self.mass(x, y, th)
                if m < best - 1e-12:''', '''                x = min(max(cx + dcx * step_c, lo), hi); y = min(max(cy + dcy * step_c, lo), hi)
                if self.hyp is not None and not self.hyp.ok(x, y, th):
                    continue
                m = self.mass(x, y, th)
                if m < best - 1e-12:''')
rep('''        Cc = C[cand]
        return Cc, self.mass_many(Cc, theta)''', '''        Cc = C[cand]
        if self.hyp is not None:
            Cc = Cc[self.hyp.ok_many(Cc, theta)]
        return Cc, self.mass_many(Cc, theta)''')

rep('''def initial_rows(s, tbox, cstep=0.1):
    out = []
    for th, k in tbox.theta_grid(5 * DEG):
        lo, hi = centre_range(s, th)
        n = int(math.ceil((hi - lo) / cstep))
        xs = np.linspace(lo, hi, n + 1)
        xs = xs[xs >= s / 2 - 1e-12]''', '''def initial_rows(s, tbox, cstep=0.1, dom_lo=None):
    out = []
    if dom_lo is None:
        dom_lo = s / 2
    for th, k in tbox.theta_grid(5 * DEG):
        lo, hi = centre_range(s, th)
        n = int(math.ceil((hi - lo) / cstep))
        xs = np.linspace(lo, hi, n + 1)
        xs = xs[xs >= dom_lo - 1e-12]''')
rep('''        extra_rows=None, meta=None, prune=2):
    t0 = time.time()
    M = Model(s, n, sym, tbox)''', '''        extra_rows=None, meta=None, prune=2, hyp=None, log=None):
    t0 = time.time()
    M = Model(s, n, sym, tbox, hyp=hyp)
    if log is None:
        log = lambda *a: print(*a, flush=True)''')
rep('''    for (cx, cy, th) in (init_rows if init_rows is not None else initial_rows(s, tbox)):
        M.add_row(cx, cy, th)
    if init_rows is not None:
        for (cx, cy, th) in initial_rows(s, tbox):
            M.add_row(cx, cy, th)''', '''    for (cx, cy, th) in (init_rows if init_rows is not None else initial_rows(s, tbox, dom_lo=sym.dom_lo)):
        M.add_row(cx, cy, th)
    if init_rows is not None:
        for (cx, cy, th) in initial_rows(s, tbox, dom_lo=sym.dom_lo):
            M.add_row(cx, cy, th)''')
rep('''        ro = RowOracle(s, M.P, wp, tbox, **rkw)''', '''        ro = RowOracle(s, M.P, wp, tbox, hyp=hyp, dom_lo=sym.dom_lo, **rkw)''')
rep('''            rof = RowOracle(s, M.P, wp, tbox, **fine_row_kw)''', '''            rof = RowOracle(s, M.P, wp, tbox, hyp=hyp, dom_lo=sym.dom_lo, **fine_row_kw)''')
rep('''        h0 = s / N0
        for i in range(N0 // 2 + 1):
            for j in range(N0 // 2 + 1):
                M.add_orbit(i * h0, j * h0)''', '''        h0 = s / N0
        rng0 = range(N0 + 1) if sym.kind == "C1" else range(N0 // 2 + 1)
        for i in rng0:
            for j in rng0:
                M.add_orbit(i * h0, j * h0)''')
rep('''    if verbose:
        print(f"[s={s} n={n} sym={sym.kind} box={tbox.describe()}] init orbits={len(M.orbits)} points={len(M.P)} "
              f"rows={len(M.rows)} (rejected {M.n_rejected})", flush=True)''', '''    if verbose:
        log(f"[s={s} n={n} sym={sym.kind} box={tbox.describe()}] init orbits={len(M.orbits)} points={len(M.P)} "
            f"rows={len(M.rows)} (rejected {M.n_rejected})")''')
rep('''            if verbose:
                print(f"    fine row search: minmass={violf[0][3]/violf[0][4] if violf else 1.0:.6f} +rows={nr}", flush=True)''',
    '''            if verbose:
                log(f"    fine row search: minmass={violf[0][3]/violf[0][4] if violf else 1.0:.6f} +rows={nr}")''')
rep('''        if verbose:
            print(f"  it {it:3d} tau={obj:.6f} rows={len(M.rows)} orbs={len(M.orbits)} atoms>0={int((wp>1e-9).sum())} "
                  f"minmass={minmass:.6f} maxcov={maxcov:.6f} +rows={nr} -rows={npr} +cols={nc} t={time.time()-t0:.0f}s", flush=True)''',
    '''        if verbose:
            log(f"  it {it:3d} tau={obj:.6f} rows={len(M.rows)} orbs={len(M.orbits)} atoms>0={int((wp>1e-9).sum())} "
                f"minmass={minmass:.6f} maxcov={maxcov:.6f} +rows={nr} -rows={npr} +cols={nc} t={time.time()-t0:.0f}s")''')
rep('''        if time_limit and time.time() - t0 > time_limit:
            print("  time limit", flush=True); break''', '''        if time_limit and time.time() - t0 > time_limit:
            log("  time limit"); break''')
rep('''    if verbose:
        print(f"DONE s={s} n={n} sym={sym.kind} tau={obj:.6f} nu={res['nu']:.6f} conv={res['converged']} "
              f"minmass={res['minmass']:.6f} maxcov={res['maxcov']:.6f} rows={len(M.rows)} "
              f"orbits={len(M.orbits)} atoms_nz={len(res['atoms'])} packing_support={len(res['packing'])} "
              f"time={time.time()-t0:.0f}s", flush=True)''', '''    if verbose:
        log(f"DONE s={s} n={n} sym={sym.kind} tau={obj:.6f} nu={res['nu']:.6f} conv={res['converged']} "
            f"minmass={res['minmass']:.6f} maxcov={res['maxcov']:.6f} rows={len(M.rows)} "
            f"orbits={len(M.orbits)} atoms_nz={len(res['atoms'])} packing_support={len(res['packing'])} "
            f"time={time.time()-t0:.0f}s")''')
rep('"""\nA10-angle-box-lp: orientation-restricted measure LP  (modified COPY of A07\'s lp_measure2.py).',
    '"""\nA13 lpbox.py = A12/A10 lp_measure_box.py + (i) symmetry C1 (no symmetry, rows over the whole square), (ii) an\n'
    'optional hypothesis filter `hyp` (rows/oracle candidates with hyp.ok(cx,cy,th) False are dropped), (iii) log hook,\n'
    '(iv) run(..., hyp=, log=).  Original header follows.\n\n'
    'A10-angle-box-lp: orientation-restricted measure LP  (modified COPY of A07\'s lp_measure2.py).')
open('lpbox.py', 'w').write(src)
print("patched", n0, "->", len(src))
