"""one-off: certs/verify_measure.py copy -> verify_case.py with hypotheses (cores / NO-families) and budget"""
import shutil
shutil.copy('../../certs/verify_measure.py', 'verify_case.py')
src = open('verify_case.py').read()


def rep(a, b):
    global src
    assert src.count(a) == 1, ("pattern", a[:60], src.count(a))
    src = src.replace(a, b)


rep('''#!/usr/bin/env python3
"""
verify_measure.py -- exact-arithmetic verifier for MEASURE certificates (lower bounds for the
square-packing problem).''', '''#!/usr/bin/env python3
"""
verify_case.py -- A13 COPY of certs/verify_measure.py extended to CASE (conditional) measure certificates.

EXTENSION (A13-case-lp-bnb).  The certificate carries hypotheses and a budget:
    "budget": b  (= n - #cores),
    "hypotheses": {"cores":  [{"kx","ky","tm","a", ...}, ...]      rational squares K = centre (kx,ky), orientation
                                                                   theta_m with tan(theta_m/2) = tm, half-side a
                   "nofams": [{"x0","x1","y0","y1","t_intervals":[[t0,t1],...]}, ...]}
CLAIM: mu(total) < budget and mu(Q) >= 1 for every admissible closed unit square Q that is NOT exempt, where Q is
exempt iff (i) its centre lies in a NO-family zone and t = tan(theta/2) in one of the family's t-intervals (closed), or
(ii) Q meets (closed intersection) some core K.  Then no packing of n = 11 pairwise-disjoint closed unit squares in
[0,s]^2 satisfies the hypotheses "for every core K some square Q0 of the packing contains K" and "no square of the
packing lies in a NO-family" (bridge: the >= n - #cores squares other than the Q0's are non-exempt, pairwise disjoint,
each of mass >= 1, so mu(total) >= budget).  A (t,cx,cy)-box is EXEMPT (discharged) iff it is PROVABLY exempt for all
its parameters: box inside a NO-family (rational comparisons), or SAT non-separation from a core on all four axes
proven by rational interval arithmetic (see core_exempt_frac).  Boxes that are not provably exempt must be covered
or split, exactly as before.  Float pre-filter only shortlists; every exemption decision is exact.

Original header follows.
----------------------------------------------------------------------------------------------------------------
verify_measure.py -- exact-arithmetic verifier for MEASURE certificates (lower bounds for the
square-packing problem).''')

rep('''# ============================================================================= the search
class Verifier:''', '''# ============================================================================= A13: hypotheses / exempt tests
class CoreH:
    def __init__(self, kx, ky, tm, a):
        self.kx, self.ky, self.tm, self.a = kx, ky, tm, a
        self.cm, self.sm = cos_sin_t(tm)          # exact rationals, cm^2 + sm^2 = 1
        self.fkx, self.fky, self.fcm, self.fsm, self.fa = float(kx), float(ky), float(self.cm), float(self.sm), float(a)


class NoFamH:
    def __init__(self, x0, x1, y0, y1, tivs):
        self.x0, self.x1, self.y0, self.y1 = x0, x1, y0, y1
        self.tivs = tivs      # list of (t0, t1) Fractions


def core_exempt_frac(core, t0, t1, x0, x1, y0, y1):
    """True iff for EVERY (t, cx, cy) in the box the closed unit square Q(c, theta(t)) meets the core square
    (SAT: projections overlap on all four edge-normal axes; proven by outward interval arithmetic)."""
    C1_, S0 = cos_sin_t(t0)          # cos decreasing, sin increasing in t
    C0, S1 = cos_sin_t(t1)
    cm, sm, a = core.cm, core.sm, core.a
    # g = |cos(theta - theta_m)| + |sin(theta - theta_m)| >= g_inf
    Alo = C0 * cm + S0 * sm                     # lower bound of cos(theta-theta_m) = C cm + S sm (all terms >= 0)
    if Alo < 0:
        Alo = ZERO
    Blo = -S1 * cm + C0 * sm                    # B = -S cm + C sm  (= sin(theta_m - theta))
    Bhi = -S0 * cm + C1_ * sm
    if Blo <= 0 <= Bhi:
        Babs = ZERO
    else:
        Babs = min(abs(Blo), abs(Bhi))
    g_inf = Alo + Babs
    dxlo, dxhi = x0 - core.kx, x1 - core.kx
    dylo, dyhi = y0 - core.ky, y1 - core.ky
    # core axes e1 = (cm, sm), e2 = (-sm, cm): need sup |proj| <= a + g/2
    lim_e = a + g_inf / 2
    lo = dxlo * cm + dylo * sm; hi = dxhi * cm + dyhi * sm
    if max(abs(lo), abs(hi)) > lim_e:
        return False
    lo = -dxhi * sm + dylo * cm; hi = -dxlo * sm + dyhi * cm
    if max(abs(lo), abs(hi)) > lim_e:
        return False
    # Q axes f1 = (C, S), f2 = (-S, C): need sup |proj| <= 1/2 + a g
    lim_f = HALF + a * g_inf
    a0, a1 = imul4(C0, C1_, dxlo, dxhi); b0, b1 = imul4(S0, S1, dylo, dyhi)
    if max(abs(a0 + b0), abs(a1 + b1)) > lim_f:
        return False
    a0, a1 = imul4(-S1, -S0, dxlo, dxhi); b0, b1 = imul4(C0, C1_, dylo, dyhi)
    if max(abs(a0 + b0), abs(a1 + b1)) > lim_f:
        return False
    return True


def core_exempt_float(core, ft0, ft1, fx0, fx1, fy0, fy1, slack=1e-7):
    """float pre-filter: False => certainly not provably exempt (with slack); True => run the exact test"""
    C1_ = (1 - ft0 * ft0) / (1 + ft0 * ft0); S0 = 2 * ft0 / (1 + ft0 * ft0)
    C0 = (1 - ft1 * ft1) / (1 + ft1 * ft1); S1 = 2 * ft1 / (1 + ft1 * ft1)
    cm, sm, a = core.fcm, core.fsm, core.fa
    Alo = max(0.0, C0 * cm + S0 * sm)
    Blo = -S1 * cm + C0 * sm; Bhi = -S0 * cm + C1_ * sm
    Babs = 0.0 if Blo <= 0 <= Bhi else min(abs(Blo), abs(Bhi))
    g = Alo + Babs
    dxlo, dxhi = fx0 - core.fkx, fx1 - core.fkx
    dylo, dyhi = fy0 - core.fky, fy1 - core.fky
    lim_e = a + g / 2 + slack
    if max(abs(dxlo * cm + dylo * sm), abs(dxhi * cm + dyhi * sm)) > lim_e:
        return False
    if max(abs(-dxhi * sm + dylo * cm), abs(-dxlo * sm + dyhi * cm)) > lim_e:
        return False
    lim_f = 0.5 + a * g + slack
    a0, a1 = imul4(C0, C1_, dxlo, dxhi); b0, b1 = imul4(S0, S1, dylo, dyhi)
    if max(abs(a0 + b0), abs(a1 + b1)) > lim_f:
        return False
    a0, a1 = imul4(-S1, -S0, dxlo, dxhi); b0, b1 = imul4(C0, C1_, dylo, dyhi)
    if max(abs(a0 + b0), abs(a1 + b1)) > lim_f:
        return False
    return True


def nofam_exempt(fam, t0, t1, x0, x1, y0, y1):
    if not (fam.x0 <= x0 and x1 <= fam.x1 and fam.y0 <= y0 and y1 <= fam.y1):
        return False
    return any(a <= t0 and t1 <= b for (a, b) in fam.tivs)


# ============================================================================= the search
class Verifier:''')

rep('''    def __init__(self, s, atoms, weights, margin=ZERO, depth=48, tscale=2, use_float=True,
                 max_witnesses=200, verbose=True, progress_every=200000):
        self.s = s''', '''    def __init__(self, s, atoms, weights, margin=ZERO, depth=48, tscale=2, use_float=True,
                 max_witnesses=200, verbose=True, progress_every=200000, cores=(), nofams=()):
        self.s = s
        self.cores = list(cores)
        self.nofams = list(nofams)''')
rep('''        self.n_float_reject = 0
        self.hist_cov = {}''', '''        self.n_float_reject = 0
        self.n_exempt = 0
        self.n_exempt_core = 0
        self.n_exempt_nofam = 0
        self.hist_cov = {}''')
rep('''    def covered(self, T0, T1, X0, X1, Y0, Y1, known, kmass):''', '''    def exempt(self, T0, T1, X0, X1, Y0, Y1):
        """A13: True iff the box is PROVABLY inside a NO-family or PROVABLY meets a core (exact)."""
        if not self.cores and not self.nofams:
            return False
        r, D = self.T_ROOT, self.D
        t0, t1 = F(T0, r), F(T1, r)
        x0, x1, y0, y1 = F(X0, D), F(X1, D), F(Y0, D), F(Y1, D)
        for fam in self.nofams:
            if nofam_exempt(fam, t0, t1, x0, x1, y0, y1):
                self.n_exempt_nofam += 1
                return True
        if self.cores:
            ft0, ft1, fx0, fx1, fy0, fy1 = T0 / r, T1 / r, X0 / D, X1 / D, Y0 / D, Y1 / D
            for core in self.cores:
                if core_exempt_float(core, ft0, ft1, fx0, fx1, fy0, fy1) and core_exempt_frac(core, t0, t1, x0, x1, y0, y1):
                    self.n_exempt_core += 1
                    return True
        return False

    def covered(self, T0, T1, X0, X1, Y0, Y1, known, kmass):''')
rep('''                X0, X1, Y0, Y1 = clipped          # sound: contains all admissible placements of the box
                ok, known, kmass = self.covered(T0, T1, X0, X1, Y0, Y1, known, kmass)''', '''                X0, X1, Y0, Y1 = clipped          # sound: contains all admissible placements of the box
                if self.exempt(T0, T1, X0, X1, Y0, Y1):
                    self.n_exempt += 1
                    continue
                ok, known, kmass = self.covered(T0, T1, X0, X1, Y0, Y1, known, kmass)''')
rep('''        return {"boxes": self.n_boxes, "covered": self.n_cov, "vacuous": self.n_vac,''',
    '''        return {"boxes": self.n_boxes, "covered": self.n_cov, "vacuous": self.n_vac, "exempt": self.n_exempt,
                "exempt_core": self.n_exempt_core, "exempt_nofam": self.n_exempt_nofam,''')
rep('''    total = sum(weights, ZERO)
    if "total" in d and _rat(d["total"]) != total:''', '''    total = sum(weights, ZERO)
    hyp = d.get("hypotheses", {}) or {}
    cores = [CoreH(_rat(c["kx"]), _rat(c["ky"]), _rat(c["tm"]), _rat(c["a"])) for c in hyp.get("cores", [])]
    for c in cores:
        if not (0 <= c.tm <= 1) or c.a <= 0:
            raise ValueError("bad core")
    nofams = [NoFamH(_rat(f["x0"]), _rat(f["x1"]), _rat(f["y0"]), _rat(f["y1"]),
                     [(_rat(a), _rat(b)) for a, b in f["t_intervals"]]) for f in hyp.get("nofams", [])]
    budget = int(d.get("budget", n))
    if budget != n - len(cores):
        raise ValueError(f"budget {budget} != n - #cores = {n - len(cores)}")
    d["_cores"], d["_nofams"], d["_budget"] = cores, nofams, budget
    if "total" in d and _rat(d["total"]) != total:''')
rep('''    if total >= n:
        print(f"FAIL: total mass {float(total):.6f} >= n = {n}: certificate proves nothing")
        return 2''', '''    cores, nofams, budget = d["_cores"], d["_nofams"], d["_budget"]
    print(f"hypotheses: {len(cores)} cores, {len(nofams)} NO-families, budget = {budget}")
    if total >= budget:
        print(f"FAIL: total mass {float(total):.6f} >= budget = {budget}: certificate proves nothing")
        return 2''')
rep('''    v0 = Verifier(s, atoms, weights, margin=margin, depth=a.depth, tscale=F(a.tscale),
                  use_float=use_float, max_witnesses=a.max_witnesses, verbose=verbose)''', '''    v0 = Verifier(s, atoms, weights, margin=margin, depth=a.depth, tscale=F(a.tscale),
                  use_float=use_float, max_witnesses=a.max_witnesses, verbose=verbose, cores=cores, nofams=nofams)''')
rep('''        with mp.Pool(a.jobs, initializer=_worker_init,
                     initargs=(s, atoms, weights, margin, a.depth, F(a.tscale), use_float, a.max_witnesses,
                           a.max_witnesses_per_box)) as pool:''', '''        with mp.Pool(a.jobs, initializer=_worker_init,
                     initargs=(s, atoms, weights, margin, a.depth, F(a.tscale), use_float, a.max_witnesses,
                           a.max_witnesses_per_box, cores, nofams)) as pool:''')
rep('''def _worker_init(s, atoms, weights, margin, depth, tscale, use_float, max_w, per_box_cap):
    _G["v"] = Verifier(s, atoms, weights, margin=margin, depth=depth, tscale=tscale,
                       use_float=use_float, max_witnesses=max_w, verbose=False)''', '''def _worker_init(s, atoms, weights, margin, depth, tscale, use_float, max_w, per_box_cap, cores=(), nofams=()):
    _G["v"] = Verifier(s, atoms, weights, margin=margin, depth=depth, tscale=tscale,
                       use_float=use_float, max_witnesses=max_w, verbose=False, cores=cores, nofams=nofams)''')
rep('''    print(f"boxes = {stats['boxes']}  covered = {stats['covered']}  vacuous = {stats['vacuous']}  "''',
    '''    print(f"boxes = {stats['boxes']}  covered = {stats['covered']}  vacuous = {stats['vacuous']}  exempt = {stats.get('exempt',0)} "
          f"(core {stats.get('exempt_core',0)}, nofam {stats.get('exempt_nofam',0)})  "''')
rep('''        print(f"PASS: every closed unit square in [0,{s}]^2 has mass >= {ONE + margin} ; total {total} < {n}"
              f"  ==>  s({n}) >= {s} (~{float(s):.10f})")''', '''        if cores or nofams:
            print(f"PASS: every NON-EXEMPT closed unit square in [0,{s}]^2 has mass >= {ONE + margin} ; total {total} < budget {budget}"
                  f"  ==>  no packing of {n} unit squares in side <= {s} (~{float(s):.10f}) satisfies the hypotheses (node DEAD)")
        else:
            print(f"PASS: every closed unit square in [0,{s}]^2 has mass >= {ONE + margin} ; total {total} < {n}"
                  f"  ==>  s({n}) >= {s} (~{float(s):.10f})")''')
open('verify_case.py', 'w').write(src)
print("ok")
