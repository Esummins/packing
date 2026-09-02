//! The pair branch-and-bound: clause table (§3.3), splitting (§3.2, Lemma S),
//! hints (§4), and FAIL semantics (§3.8).

use crate::cert::Cert;
use crate::geom::*;
use crate::rat::{lemma_q_rat, Rat};
use serde_json::Value;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering as AtOrd};

#[derive(Clone, Debug)]
pub struct Settings {
    pub depth: u32,
    pub split: u32,
    pub nodes: u64,
    pub jobs: usize,
    pub survey: bool,
    pub faildump: usize,
    /// DEFICIENT-EARLY probe stride (probe when depth % stride == 0).
    pub probe_stride: u32,
}

impl Default for Settings {
    fn default() -> Self {
        Settings {
            depth: 40,
            split: 2,
            nodes: u64::MAX,
            jobs: 1,
            survey: false,
            faildump: 8,
            probe_stride: 8,
        }
    }
}

#[derive(Clone, Debug, Default)]
pub struct Counts {
    pub pairs_root: u64,
    pub pairs_examined: u64,
    pub vacuous: u64,
    pub vacuous_contain: u64,
    pub exempt_core: u64,
    pub nondisjoint: u64,
    pub covered: u64,
    pub covered_f: u64,
    pub split: u64,
    pub hint_misses: u64,
    pub max_depth: u32,
    pub deficient_early: u64,
}

impl Counts {
    fn merge(&mut self, o: &Counts) {
        self.pairs_examined += o.pairs_examined;
        self.vacuous += o.vacuous;
        self.vacuous_contain += o.vacuous_contain;
        self.exempt_core += o.exempt_core;
        self.nondisjoint += o.nondisjoint;
        self.covered += o.covered;
        self.covered_f += o.covered_f;
        self.split += o.split;
        self.hint_misses += o.hint_misses;
        self.deficient_early += o.deficient_early;
        if o.max_depth > self.max_depth {
            self.max_depth = o.max_depth;
        }
    }
}

/// A concrete admissible interior-disjoint placement pair that collects too little mass.
#[derive(Clone, Debug)]
pub struct Confirm {
    pub p1: Place,
    pub p2: Place,
    pub sat_gap: Rat,
    pub mass: Rat,
    pub m2: u64,
    pub need: Rat,
}

#[derive(Clone, Debug)]
pub struct Witness {
    /// "definitive" (a concrete counterexample) or "cap" (undischarged at the depth/node cap).
    pub kind: &'static str,
    pub f: [Rat; 6],
    pub g: [Rat; 6],
    pub depth: u32,
    pub u: u64,
    pub certain_mass: Rat,
    pub deficit: Rat,
    pub sat_margins: Vec<Rat>,
    pub confirm: Option<Confirm>,
}

pub struct Outcome {
    pub pass: bool,
    pub counts: Counts,
    pub witnesses: Vec<Witness>,
    /// Total FAIL witnesses found (may exceed the number stored under `--faildump`).
    pub n_witnesses: u64,
    /// Total pair boxes examined across all threads (the throughput measure).
    pub nodes: u64,
}

// ---------------------------------------------------------------------------
// Root enumeration (v2 §3.1 = v1 §3, verbatim)
// ---------------------------------------------------------------------------

/// Root factor boxes: t in [0,1] unsplit, centres on a 2^k x 2^k grid over
/// [w_min/2, s - w_min/2]^2 with w_min = min over t in [0,1] of w(t) = 1.
pub fn build_roots(s: &Rat, split_k: u32) -> Vec<Factor> {
    let t0 = Rat::zero();
    let t1 = Rat::one();
    let wmin = w_lo(&t0, &t1); // = 1
    let lo = wmin.mul(&Rat::half());
    let hi = s.sub(&lo);
    if hi.lt(&lo) {
        return Vec::new();
    }
    let g = 1u32 << split_k;
    let span = hi.sub(&lo);
    let step = span.div(&Rat::from_int(g as i128)).unwrap_or(span.clone());
    let mut xs = Vec::with_capacity(g as usize + 1);
    for i in 0..=g {
        xs.push(lo.add(&step.mul(&Rat::from_int(i as i128))));
    }
    let mut out = Vec::with_capacity((g * g) as usize);
    for iy in 0..g {
        for ix in 0..g {
            out.push(Factor {
                t0: t0.clone(),
                t1: t1.clone(),
                x0: xs[ix as usize].clone(),
                x1: xs[ix as usize + 1].clone(),
                y0: xs[iy as usize].clone(),
                y1: xs[iy as usize + 1].clone(),
            });
        }
    }
    out
}

// ---------------------------------------------------------------------------
// Scaled-coordinate helpers for the integer fast path
// ---------------------------------------------------------------------------

#[inline]
fn atom_pt_scaled(cert: &Cert, sc: &Scale, i: usize, ep: usize) -> Option<(i128, i128)> {
    if !sc.ok || cert.dg == 0 {
        return None;
    }
    let a = cert.atom_scaled.get(i)?;
    let (x, y) = if ep == 0 { (a[0], a[1]) } else { (a[2], a[3]) };
    Some((x.checked_mul(sc.mul_coord)?, y.checked_mul(sc.mul_coord)?))
}

#[inline]
fn core_scaled(cert: &Cert, sc: &Scale, j: usize) -> Option<(i128, i128, i128)> {
    if !sc.ok || cert.dg == 0 {
        return None;
    }
    let c = cert.core_scaled.get(j)?;
    Some((
        c[0].checked_mul(sc.mul_coord)?,
        c[1].checked_mul(sc.mul_coord)?,
        c[2].checked_mul(sc.mul_coord)?,
    ))
}

/// The (px, py) of atom `i` for orientation `o` and endpoint `ep`.
/// Orientation 0 sends p -> first factor, q -> second; orientation 1 swaps them.
#[inline]
fn atom_endpoint(o: usize, ep: usize) -> usize {
    // returns 0 for the atom's p, 1 for its q
    if o == 0 {
        ep
    } else {
        1 - ep
    }
}

// ---------------------------------------------------------------------------
// Shortlisting (float; §3.0 permits it — a miss can only cost mass)
// ---------------------------------------------------------------------------

fn aabb_of(f: &Factor, tg: &TGeom) -> (f64, f64, f64, f64) {
    let hw = tg.whi.to_f64() * 0.5;
    let pad = 1e-9 + hw * 1e-12;
    (
        f.x0.to_f64() - hw - pad,
        f.y0.to_f64() - hw - pad,
        f.x1.to_f64() + hw + pad,
        f.y1.to_f64() + hw + pad,
    )
}

#[inline]
fn in_rect(x: f64, y: f64, r: (f64, f64, f64, f64)) -> bool {
    x >= r.0 && x <= r.2 && y >= r.1 && y <= r.3
}

/// Per-thread scratch buffers, so the hot loop allocates nothing.
struct Scratch {
    cand: Vec<u32>,
    seen: Vec<u32>,
    gen: u32,
    collected: Vec<(u32, u8)>,
    evals: Vec<AtomEval>,
}

impl Scratch {
    fn new(natoms: usize) -> Scratch {
        Scratch {
            cand: Vec::with_capacity(256),
            seen: vec![0; natoms],
            gen: 0,
            collected: Vec::with_capacity(64),
            evals: Vec::with_capacity(128),
        }
    }
    #[inline]
    fn bump(&mut self) {
        self.gen = self.gen.wrapping_add(1);
        if self.gen == 0 {
            for v in self.seen.iter_mut() {
                *v = 0;
            }
            self.gen = 1;
        }
    }
    #[inline]
    fn first_time(&mut self, i: usize) -> bool {
        if self.seen[i] == self.gen {
            false
        } else {
            self.seen[i] = self.gen;
            true
        }
    }
}

/// A MEM witness: an oriented atom plus its FAILING SET (spec §3.6). Each element is
/// (endpoint, g-index) with endpoint 0 = first factor, 1 = second factor.
#[derive(Clone, Debug)]
struct MemCand {
    atom: u32,
    orient: u8,
    sigmas: Vec<(u8, u8)>,
    w: Rat,
}

/// An EXC witness: a core/factor pair plus its failing set over {E1+..E4-}.
#[derive(Clone, Debug)]
struct ExcCand {
    core: u32,
    factor: u8,
    sigmas: Vec<u8>,
}

// ---------------------------------------------------------------------------
// COVERED: certain collected mass (Lemma M per atom and orientation)
// ---------------------------------------------------------------------------

/// One oriented atom's Lemma M constraint results over the pair box, computed ONCE per
/// node and shared by COVERED, COVERED-F and the split heuristic.
#[derive(Clone, Debug)]
struct AtomEval {
    atom: u32,
    orient: u8,
    /// Lemma M flags against the first factor (endpoint 0) and the second (endpoint 1).
    ff: [bool; 4],
    gf: [bool; 4],
    nfail: u8,
    /// §6 gate: possibly collectable in BOTH factors. Only such atoms are eligible
    /// targets for the margin-aware split.
    possible: bool,
}

/// Half-diagonal of a unit square, rounded UP so derived rectangles stay outward.
const HALF_DIAG: f64 = 0.7071067811865476 + 1e-12;

/// The set of points that could be CERTAIN members over the whole factor box.
///
/// Q(c, theta) is contained in the closed disk of radius sqrt(2)/2 about c, so a point
/// inside for EVERY centre in the rectangle lies within that radius of every centre, and
/// hence within it of the farthest corner. The resulting rectangle is
/// [x1 - r, x0 + r] x [y1 - r, y0 + r]; note the reversed endpoints, which make it EMPTY
/// as soon as the centre rectangle is wider than sqrt(2). That emptiness test is what
/// keeps large boxes off the atom path entirely.
///
/// This is a float shortlist in the sense of §3.0: an outward superset of the true
/// certain-membership region, so it can only ever cost mass, never grant it.
fn certain_rect(f: &Factor, expand: f64) -> Option<(f64, f64, f64, f64)> {
    let r = HALF_DIAG + expand;
    let (x0, x1) = (f.x0.to_f64(), f.x1.to_f64());
    let (y0, y1) = (f.y0.to_f64(), f.y1.to_f64());
    let (ax, bx) = (x1 - r, x0 + r);
    let (ay, by) = (y1 - r, y0 + r);
    if ax > bx || ay > by {
        return None;
    }
    const E: f64 = 1e-9;
    Some((ax - E, ay - E, bx + E, by + E))
}

/// A factor box's corners in f64, for the pre-screen below.
#[derive(Clone, Copy)]
struct FBox {
    t0: f64,
    t1: f64,
    x0: f64,
    x1: f64,
    y0: f64,
    y1: f64,
}

impl FBox {
    fn of(f: &Factor) -> FBox {
        FBox {
            t0: f.t0.to_f64(),
            t1: f.t1.to_f64(),
            x0: f.x0.to_f64(),
            x1: f.x1.to_f64(),
            y0: f.y0.to_f64(),
            y1: f.y1.to_f64(),
        }
    }
}

/// Slack margin below which a float evaluation is treated as a DEFINITE failure. The
/// quantities here are O(1), so this sits far above f64 rounding error.
const PRESCREEN_EPS: f64 = 1e-9;

/// Lower bound, computed in f64, on how many of a point's four Lemma M constraints fail
/// over the factor box.
///
/// Each pinned slack quadratic satisfies min over [t0,t1] <= min(q(t0), q(t1)), so a
/// clearly-negative endpoint value PROVES that constraint fails. Counting those gives a
/// lower bound on the size of the exact failing set.
///
/// This is a §3.0 float shortlist used only to SKIP atoms: an atom wrongly skipped
/// contributes no mass and yields no witness, which makes PASS harder, never easier.
#[inline]
fn prescreen_fail_count(b: &FBox, px: f64, py: f64) -> u32 {
    let ev = |a: f64, bb: f64, c: f64| -> f64 {
        let v0 = a * b.t0 * b.t0 + bb * b.t0 + c;
        let v1 = a * b.t1 * b.t1 + bb * b.t1 + c;
        if v0 < v1 {
            v0
        } else {
            v1
        }
    };
    let mut n = 0u32;
    // g1 at (x0,y0)
    let (dx, dy) = (px - b.x0, py - b.y0);
    if ev(0.5 + dx, -2.0 * dy, 0.5 - dx) < -PRESCREEN_EPS {
        n += 1;
    }
    // g2 at (x1,y1)
    let (dx, dy) = (px - b.x1, py - b.y1);
    if ev(0.5 - dx, 2.0 * dy, 0.5 + dx) < -PRESCREEN_EPS {
        n += 1;
    }
    // g3 at (x1,y0)
    let (dx, dy) = (px - b.x1, py - b.y0);
    if ev(0.5 + dy, 2.0 * dx, 0.5 - dy) < -PRESCREEN_EPS {
        n += 1;
    }
    // g4 at (x0,y1)
    let (dx, dy) = (px - b.x0, py - b.y1);
    if ev(0.5 - dy, -2.0 * dx, 0.5 + dy) < -PRESCREEN_EPS {
        n += 1;
    }
    n
}

/// The four Lemma M slack quadratics in f64, pinned at an arbitrary centre corner.
/// Same coefficients as `mem_quad_at`; floats are fine here because everything below
/// this point is heuristic (Lemma S makes soundness independent of the split rule).
#[inline]
fn mem_quad_f(sigma: u8, px: f64, py: f64, cx: f64, cy: f64) -> (f64, f64, f64) {
    let (dx, dy) = (px - cx, py - cy);
    match sigma {
        0 => (0.5 + dx, -2.0 * dy, 0.5 - dx),
        1 => (0.5 - dx, 2.0 * dy, 0.5 + dx),
        2 => (0.5 + dy, 2.0 * dx, 0.5 - dy),
        _ => (0.5 - dy, -2.0 * dx, 0.5 + dy),
    }
}

/// Lemma M's slack-MINIMISING corner (§3.4).
#[inline]
fn min_corner_f(sigma: u8, b: &FBox) -> (f64, f64) {
    match sigma {
        0 => (b.x0, b.y0),
        1 => (b.x1, b.y1),
        2 => (b.x1, b.y0),
        _ => (b.x0, b.y1),
    }
}

/// The OPPOSITE corner, which maximises that constraint's slack over the centre
/// rectangle (§6's possible-collectability test).
#[inline]
fn max_corner_f(sigma: u8, b: &FBox) -> (f64, f64) {
    match sigma {
        0 => (b.x1, b.y1),
        1 => (b.x0, b.y0),
        2 => (b.x0, b.y1),
        _ => (b.x1, b.y0),
    }
}

/// min of A t^2 + B t + C over [t0,t1] (endpoints, plus the interior vertex when A > 0).
#[inline]
fn quad_min_f(a: f64, bb: f64, c: f64, t0: f64, t1: f64) -> f64 {
    let ev = |t: f64| a * t * t + bb * t + c;
    let mut m = ev(t0).min(ev(t1));
    if a > 0.0 {
        let ts = -bb / (2.0 * a);
        if ts > t0 && ts < t1 {
            m = m.min(ev(ts));
        }
    }
    m
}

/// max of A t^2 + B t + C over [t0,t1] — Lemma Q's max analogue: endpoints, plus the
/// interior vertex when A < 0 (the concave case).
#[inline]
fn quad_max_f(a: f64, bb: f64, c: f64, t0: f64, t1: f64) -> f64 {
    let ev = |t: f64| a * t * t + bb * t + c;
    let mut m = ev(t0).max(ev(t1));
    if a < 0.0 {
        let ts = -bb / (2.0 * a);
        if ts > t0 && ts < t1 {
            m = m.max(ev(ts));
        }
    }
    m
}

/// §6 possible-collectability: is the point inside Q for at least ONE placement in the
/// box? Necessary condition — every one of the four membership constraints must be
/// satisfiable somewhere, i.e. its slack pinned at the OPPOSITE (maximising) corner has
/// max over [t0,t1] >= 0.
///
/// An atom reachable in only one factor can never reach COVERED, and chasing one
/// collapses that factor to a point while the other stays unsplit — a 40-depth thrash.
#[inline]
fn possibly_collectable(b: &FBox, px: f64, py: f64) -> bool {
    for sigma in 0u8..4 {
        let (cx, cy) = max_corner_f(sigma, b);
        let (qa, qb, qc) = mem_quad_f(sigma, px, py, cx, cy);
        if quad_max_f(qa, qb, qc, b.t0, b.t1) < 0.0 {
            return false;
        }
    }
    true
}

/// Cap on evaluated atoms per node (completeness-only: a truncated list can only fail to
/// find a discharge, never admit an unsound one).
const MAX_EVALS: usize = 512;

/// Evaluate Lemma M for every shortlisted oriented atom, filling `s.evals`, and return
/// the CERTAIN collected mass (the atoms with an empty failing set). Each atom counts at
/// most once, per (P2').
fn gather_evals(
    cert: &Cert,
    f: &Factor,
    g: &Factor,
    scf: &Scale,
    scg: &Scale,
    s: &mut Scratch,
    expand: f64,
) -> Rat {
    s.evals.clear();
    s.collected.clear();
    let mut mass = Rat::zero();
    if cert.atoms.is_empty() {
        return mass;
    }
    let rf = match certain_rect(f, expand) {
        Some(r) => r,
        None => return mass,
    };
    let rg = match certain_rect(g, expand) {
        Some(r) => r,
        None => return mass,
    };
    let fb = FBox::of(f);
    let gb = FBox::of(g);
    s.bump();
    for orient in 0u8..2 {
        let wf = atom_endpoint(orient as usize, 0);
        let wg = atom_endpoint(orient as usize, 1);
        s.cand.clear();
        cert.grid.query(wf, rf.0, rf.1, rf.2, rf.3, &mut s.cand);
        let cands = std::mem::take(&mut s.cand);
        for &ai in cands.iter() {
            let i = ai as usize;
            if s.evals.len() >= MAX_EVALS {
                break;
            }
            if !s.first_time(i) {
                continue;
            }
            let a = &cert.atoms[i];
            let (gx, gy) = if wg == 0 { (a.pxf, a.pyf) } else { (a.qxf, a.qyf) };
            if !in_rect(gx, gy, rg) {
                s.seen[i] = 0;
                continue;
            }
            // Float pre-screen: an atom already proven to fail more than CF_MAX_SIGMA
            // constraints is useful neither to COVERED nor to COVERED-F.
            let (fx, fy) = if wf == 0 { (a.pxf, a.pyf) } else { (a.qxf, a.qyf) };
            let pre = prescreen_fail_count(&fb, fx, fy) + prescreen_fail_count(&gb, gx, gy);
            if pre as usize > CF_MAX_SIGMA {
                s.seen[i] = 0;
                continue;
            }
            let (fpx, fpy) = if wf == 0 { (&a.px, &a.py) } else { (&a.qx, &a.qy) };
            let (gpx, gpy) = if wg == 0 { (&a.px, &a.py) } else { (&a.qx, &a.qy) };
            let ff = member_flags(f, scf, fpx, fpy, atom_pt_scaled(cert, scf, i, wf));
            let nf_f = ff.iter().filter(|b| !**b).count();
            // Early exit before touching the second factor.
            if nf_f > CF_MAX_SIGMA {
                s.seen[i] = 0;
                continue;
            }
            let gf = member_flags(g, scg, gpx, gpy, atom_pt_scaled(cert, scg, i, wg));
            let nfail = (nf_f + gf.iter().filter(|b| !**b).count()) as u8;
            if nfail == 0 {
                mass = mass.add(&a.w);
                s.collected.push((ai, orient));
            } else {
                // Leave the atom available to the other orientation.
                s.seen[i] = 0;
            }
            let possible = possibly_collectable(&fb, fx, fy)
                && possibly_collectable(&gb, gx, gy);
            s.evals.push(AtomEval {
                atom: ai,
                orient,
                ff,
                gf,
                nfail,
                possible,
            });
        }
        s.cand = cands;
    }
    mass
}

// ---------------------------------------------------------------------------
// Quadratics pinned at an ARBITRARY centre corner (needed by COVERED-F check 2)
// ---------------------------------------------------------------------------

/// Lemma M slack quadratic `sigma` for point (px,py) pinned at centre corner (cx,cy).
fn mem_quad_at(sigma: u8, px: &Rat, py: &Rat, cx: &Rat, cy: &Rat) -> (Rat, Rat, Rat) {
    let h = Rat::half();
    let two = Rat::from_int(2);
    let dx = px.sub(cx);
    let dy = py.sub(cy);
    match sigma {
        0 => (h.add(&dx), dy.mul(&two).neg(), h.sub(&dx)),
        1 => (h.sub(&dx), dy.mul(&two), h.add(&dx)),
        2 => (h.add(&dy), dx.mul(&two), h.sub(&dy)),
        _ => (h.sub(&dy), dx.mul(&two).neg(), h.add(&dy)),
    }
}

/// Lemma E slack quadratic `sigma` for core `k` pinned at centre corner (cx,cy).
fn exc_quad_at(sigma: u8, k: &Core, cx: &Rat, cy: &Rat) -> (Rat, Rat, Rat) {
    let h = Rat::half();
    let two = Rat::from_int(2);
    let a = k.a.clone();
    let ex = cx.sub(&k.kx);
    let ey = cy.sub(&k.ky);
    let axis = |kk: Rat| -> (Rat, Rat, Rat) { (kk.sub(&h), Rat::one(), kk.add(&h)) };
    match sigma {
        0 => axis(a.sub(&ex)),
        1 => axis(a.add(&ex)),
        2 => axis(a.sub(&ey)),
        3 => axis(a.add(&ey)),
        4 => (
            h.sub(&a).add(&ex),
            a.mul(&two).sub(&ey.mul(&two)),
            h.add(&a).sub(&ex),
        ),
        5 => (
            h.sub(&a).sub(&ex),
            a.mul(&two).add(&ey.mul(&two)),
            h.add(&a).add(&ex),
        ),
        6 => (
            h.sub(&a).add(&ey),
            a.mul(&two).add(&ex.mul(&two)),
            h.add(&a).sub(&ey),
        ),
        _ => (
            h.sub(&a).sub(&ey),
            a.mul(&two).sub(&ex.mul(&two)),
            h.add(&a).add(&ey),
        ),
    }
}

/// The worst (slack-minimising) centre corner for a Lemma M constraint.
fn mem_worst_corner(sigma: u8, f: &Factor) -> (Rat, Rat) {
    match sigma {
        0 => (f.x0.clone(), f.y0.clone()),
        1 => (f.x1.clone(), f.y1.clone()),
        2 => (f.x1.clone(), f.y0.clone()),
        _ => (f.x0.clone(), f.y1.clone()),
    }
}

/// The worst centre corner for a Lemma E constraint (E1+/- and E2+/- have one free
/// coordinate; any value works, so a box corner is used).
fn exc_worst_corner(sigma: u8, f: &Factor) -> (Rat, Rat) {
    match sigma {
        0 => (f.x1.clone(), f.y0.clone()),
        1 => (f.x0.clone(), f.y0.clone()),
        2 => (f.x0.clone(), f.y1.clone()),
        3 => (f.x0.clone(), f.y0.clone()),
        4 => (f.x1.clone(), f.y1.clone()),
        5 => (f.x0.clone(), f.y0.clone()),
        6 => (f.x0.clone(), f.y1.clone()),
        _ => (f.x1.clone(), f.y0.clone()),
    }
}

/// One designated constraint belonging to a witness's failing set.
#[derive(Clone)]
enum CItem<'a> {
    Mem {
        px: &'a Rat,
        py: &'a Rat,
        sigma: u8,
        factor: u8,
    },
    Exc {
        core: &'a Core,
        sigma: u8,
        factor: u8,
    },
}

impl<'a> CItem<'a> {
    fn factor_idx(&self) -> u8 {
        match self {
            CItem::Mem { factor, .. } => *factor,
            CItem::Exc { factor, .. } => *factor,
        }
    }
    fn quad_at(&self, cx: &Rat, cy: &Rat) -> (Rat, Rat, Rat) {
        match self {
            CItem::Mem { px, py, sigma, .. } => mem_quad_at(*sigma, px, py, cx, cy),
            CItem::Exc { core, sigma, .. } => exc_quad_at(*sigma, core, cx, cy),
        }
    }
    fn worst_corner(&self, f: &Factor) -> (Rat, Rat) {
        match self {
            CItem::Mem { sigma, .. } => mem_worst_corner(*sigma, f),
            CItem::Exc { sigma, .. } => exc_worst_corner(*sigma, f),
        }
    }
}

/// COVERED-F check 2 for ONE cross pair: `min over P of (g_sigma + g_sigma') >= 0`, exact.
///
/// SAME factor: at each fixed t the sum is affine in (cx,cy), so its minimum over the
/// centre rectangle sits at a corner; requiring Lemma Q nonnegativity at all four corners
/// gives exactly min over corners of min over t.
///
/// DIFFERENT factors: the variables are independent, so min(sum) = sum(mins), and each
/// constraint's min is attained at its own pinned worst corner (sign-fixedness, Lemmas M/E).
fn cross_ok(w1: &CItem, w2: &CItem, f: &Factor, g: &Factor) -> bool {
    if w1.factor_idx() == w2.factor_idx() {
        let fac = if w1.factor_idx() == 0 { f } else { g };
        let corners = [
            (fac.x0.clone(), fac.y0.clone()),
            (fac.x1.clone(), fac.y0.clone()),
            (fac.x0.clone(), fac.y1.clone()),
            (fac.x1.clone(), fac.y1.clone()),
        ];
        for (cx, cy) in corners.iter() {
            let (a1, b1, c1) = w1.quad_at(cx, cy);
            let (a2, b2, c2) = w2.quad_at(cx, cy);
            let a = a1.add(&a2);
            let b = b1.add(&b2);
            let c = c1.add(&c2);
            if !lemma_q_rat(&a, &b, &c, &fac.t0, &fac.t1) {
                return false;
            }
        }
        true
    } else {
        let fa = if w1.factor_idx() == 0 { f } else { g };
        let fb = if w2.factor_idx() == 0 { f } else { g };
        let (c1x, c1y) = w1.worst_corner(fa);
        let (c2x, c2y) = w2.worst_corner(fb);
        let (a1, b1, cc1) = w1.quad_at(&c1x, &c1y);
        let (a2, b2, cc2) = w2.quad_at(&c2x, &c2y);
        let m1 = quad_min(&a1, &b1, &cc1, &fa.t0, &fa.t1);
        let m2 = quad_min(&a2, &b2, &cc2, &fb.t0, &fb.t1);
        m1.add(&m2).is_nonneg()
    }
}

/// A handoff pair (W, W') is valid iff EVERY cross pair of their failing sets satisfies
/// check 2 (spec §3.6, failing-set form). The proof's case split needs all of Sigma_W'
/// to be forced whenever any single sigma of Sigma_W fails, which is exactly this
/// quantification over the full cross product.
fn handoff_ok(wa: &[CItem], wb: &[CItem], f: &Factor, g: &Factor) -> bool {
    if wa.is_empty() || wb.is_empty() {
        return false;
    }
    for x in wa.iter() {
        for y in wb.iter() {
            if !cross_ok(x, y, f, g) {
                return false;
            }
        }
    }
    true
}

// ---------------------------------------------------------------------------
// DEFICIENT-EARLY (§3.8): exact evaluation at a rational placement pair.
// Accelerates FAIL only; it can never affect a PASS.
// ---------------------------------------------------------------------------

fn candidate_places(f: &Factor) -> Vec<Place> {
    let tm = f.t0.mid(&f.t1);
    let xm = f.x0.mid(&f.x1);
    let ym = f.y0.mid(&f.y1);
    vec![
        Place {
            t: f.t0.clone(),
            cx: f.x0.clone(),
            cy: f.y0.clone(),
        },
        Place {
            t: f.t0.clone(),
            cx: f.x1.clone(),
            cy: f.y1.clone(),
        },
        Place {
            t: tm.clone(),
            cx: xm.clone(),
            cy: ym.clone(),
        },
        Place {
            t: f.t1.clone(),
            cx: f.x0.clone(),
            cy: f.y0.clone(),
        },
        Place {
            t: f.t1.clone(),
            cx: f.x1.clone(),
            cy: f.y1.clone(),
        },
    ]
}

/// Exact collected mass at a concrete placement pair (grid-shortlisted, exactly decided).
fn mass_at(cert: &Cert, p1: &Place, p2: &Place, s: &mut Scratch) -> Rat {
    if cert.atoms.is_empty() {
        return Rat::zero();
    }
    let hw = p1.w().to_f64() * 0.5 + 1e-9;
    let r1 = (
        p1.cx.to_f64() - hw,
        p1.cy.to_f64() - hw,
        p1.cx.to_f64() + hw,
        p1.cy.to_f64() + hw,
    );
    s.bump();
    let mut mass = Rat::zero();
    for which in 0usize..2 {
        s.cand.clear();
        cert.grid.query(which, r1.0, r1.1, r1.2, r1.3, &mut s.cand);
        let cands = std::mem::take(&mut s.cand);
        for &ai in cands.iter() {
            let i = ai as usize;
            if !s.first_time(i) {
                continue;
            }
            let a = &cert.atoms[i];
            let (ax, ay, bx, by) = if which == 0 {
                (&a.px, &a.py, &a.qx, &a.qy)
            } else {
                (&a.qx, &a.qy, &a.px, &a.py)
            };
            if point_in_square(ax, ay, p1) && point_in_square(bx, by, p2) {
                mass = mass.add(&a.w);
            } else {
                s.seen[i] = 0;
            }
        }
        s.cand = cands;
    }
    mass
}

fn m2_at(cert: &Cert, p1: &Place, p2: &Place) -> u64 {
    let mut c = 0u64;
    for b in &cert.boxes {
        if box_int_meets_square(b, p1) && box_int_meets_square(b, p2) {
            c += 1;
        }
    }
    c
}

/// Try to find a concrete admissible interior-disjoint placement pair in this box whose
/// exactly-computed collected mass is below `1 + beta*m2`. Such a pair falsifies (P2').
fn deficient_early(cert: &Cert, f: &Factor, g: &Factor, s: &mut Scratch) -> Option<Confirm> {
    let ca = candidate_places(f);
    let cb = candidate_places(g);
    for p1 in &ca {
        if !square_in_container(p1, &cert.s) {
            continue;
        }
        if cert.cores.iter().any(|k| square_meets_core(p1, k)) {
            continue;
        }
        for p2 in &cb {
            if !square_in_container(p2, &cert.s) {
                continue;
            }
            if cert.cores.iter().any(|k| square_meets_core(p2, k)) {
                continue;
            }
            let gap = sat_gap(p1, p2);
            if !gap.is_nonneg() {
                continue; // interiors overlap: not an obligation
            }
            let m2 = m2_at(cert, p1, p2);
            let need = Rat::one().add(&cert.beta.mul(&Rat::from_int(m2 as i128)));
            let mass = mass_at(cert, p1, p2, s);
            if mass.lt(&need) {
                return Some(Confirm {
                    p1: p1.clone(),
                    p2: p2.clone(),
                    sat_gap: gap,
                    mass,
                    m2,
                    need,
                });
            }
        }
    }
    None
}

// ---------------------------------------------------------------------------
// Splitting (§3.2): free rational cuts, margin-aware.
// ---------------------------------------------------------------------------

/// Bisect toward a sign change of the pinned quadratic inside [t0,t1] using EXACT sign
/// tests, returning a rational cut strictly interior to the interval. This is the
/// margin-aware free cut of §6 for the t dimension: it places the cut at the constraint
/// frontier instead of the midpoint.
fn margin_cut_t(a: &Rat, b: &Rat, c: &Rat, t0: &Rat, t1: &Rat) -> Option<Rat> {
    let ev = |t: &Rat| -> Rat { a.mul(t).mul(t).add(&b.mul(t)).add(c) };
    let s0 = ev(t0).sign();
    let s1 = ev(t1).sign();
    if s0 == 0 || s1 == 0 || s0 == s1 {
        return None;
    }
    let (mut lo, mut hi) = (t0.clone(), t1.clone());
    let mut slo = s0;
    for _ in 0..8 {
        let mid = lo.mid(&hi);
        if !(mid.gt(t0) && mid.lt(t1)) {
            break;
        }
        let sm = ev(&mid).sign();
        if sm == 0 {
            return Some(mid);
        }
        if sm == slo {
            lo = mid;
        } else {
            hi = mid;
        }
        slo = ev(&lo).sign();
    }
    let cut = lo.mid(&hi);
    if cut.gt(t0) && cut.lt(t1) {
        Some(cut)
    } else {
        None
    }
}

/// Widest-dimension fallback (v1 §3 item 5) with t-widths weighted by `tscale` = 2.
fn widest_dim(f: &Factor, g: &Factor) -> (u8, usize) {
    let two = Rat::from_int(2);
    let mut best = (0u8, 0usize);
    let mut bw = Rat::from_int(-1);
    for (fi, fac) in [(0u8, f), (1u8, g)] {
        for d in 0usize..3 {
            let w = if d == 0 {
                fac.width(0).mul(&two)
            } else {
                fac.width(d)
            };
            if w.gt(&bw) {
                bw = w;
                best = (fi, d);
            }
        }
    }
    best
}

// ---------------------------------------------------------------------------
// Per-node clause evaluation
// ---------------------------------------------------------------------------

enum Discharge {
    Vacuous,
    VacuousContain,
    Exempt,
    Nondisjoint,
    Covered,
    CoveredF,
    None,
}

struct NodeEval {
    discharge: Discharge,
    u: u64,
    mass: Rat,
    need: Rat,
}

fn eval_node(
    cert: &Cert,
    f: &Factor,
    g: &Factor,
    ftg: &TGeom,
    gtg: &TGeom,
    scf: &Scale,
    scg: &Scale,
    s: &mut Scratch,
) -> NodeEval {
    // ---- 1b. VACUOUS-CONTAIN ----
    // Cheap and exact; placed first because it discharges the container-boundary sliver
    // that no later clause can reach.
    if vacuous_contain(f, &cert.s) || vacuous_contain(g, &cert.s) {
        return NodeEval {
            discharge: Discharge::VacuousContain,
            u: 0,
            mass: Rat::zero(),
            need: Rat::zero(),
        };
    }

    // ---- 2. EXEMPT (Lemma E) ----
    for (j, k) in cert.cores.iter().enumerate() {
        let km = core_scaled(cert, scf, j);
        if certain_exempt(f, scf, k, km) {
            return NodeEval {
                discharge: Discharge::Exempt,
                u: 0,
                mass: Rat::zero(),
                need: Rat::zero(),
            };
        }
        let km = core_scaled(cert, scg, j);
        if certain_exempt(g, scg, k, km) {
            return NodeEval {
                discharge: Discharge::Exempt,
                u: 0,
                mass: Rat::zero(),
                need: Rat::zero(),
            };
        }
    }

    // ---- 3. NONDISJOINT ----
    if nondisjoint(f, g, ftg, gtg) {
        return NodeEval {
            discharge: Discharge::Nondisjoint,
            u: 0,
            mass: Rat::zero(),
            need: Rat::zero(),
        };
    }

    // ---- 4. COVERED ----
    let beta_active = cert.beta.is_pos() && !cert.boxes.is_empty();
    let u = if beta_active {
        u_bound(f, g, ftg, gtg, &cert.boxes)
    } else {
        0
    };
    let need = if beta_active {
        Rat::one().add(&cert.beta.mul(&Rat::from_int(u as i128)))
    } else {
        Rat::one()
    };
    // One Lemma M pass per node; COVERED, COVERED-F and choose_split all read it.
    // The shortlist is the TIGHT certain-membership rectangle, which is empty whenever a
    // centre rectangle is wider than sqrt(2) — so large boxes skip the atom path whole.
    let mass = gather_evals(cert, f, g, scf, scg, s, 0.0);
    if mass.ge(&need) {
        return NodeEval {
            discharge: Discharge::Covered,
            u,
            mass,
            need,
        };
    }

    // ---- 5. COVERED-F (Lemma F) ----
    if covered_f(cert, f, g, scf, scg, s, &mass, &need) {
        return NodeEval {
            discharge: Discharge::CoveredF,
            u,
            mass,
            need,
        };
    }

    NodeEval {
        discharge: Discharge::None,
        u,
        mass,
        need,
    }
}

/// Bounds on the greedy COVERED-F search. These are COMPLETENESS-only limits: a smaller
/// budget can only fail to find a discharge (causing a split), never admit a bad one.
const CF_MAX_MEM: usize = 12;
const CF_MAX_EXC: usize = 6;
/// Largest failing set considered. Failing sets of size > 1 are the norm near axis
/// orientations (§3.6), so this must be > 1; the cross-product cost is |S| * |S'|.
const CF_MAX_SIGMA: usize = 4;

/// Search-mode COVERED-F: build a base set B (the certainly-collected atoms, already in
/// `s.collected`) and greedily pair up single-failure witnesses per §3.6/§6.
fn covered_f(
    cert: &Cert,
    f: &Factor,
    g: &Factor,
    scf: &Scale,
    scg: &Scale,
    s: &mut Scratch,
    base_mass: &Rat,
    need: &Rat,
) -> bool {
    if cert.atoms.is_empty() {
        return false;
    }

    // ---- MEM witness candidates, read off the shared Lemma M cache ----
    let mut mems: Vec<MemCand> = Vec::new();
    for e in s.evals.iter() {
        if e.nfail == 0 || e.nfail as usize > CF_MAX_SIGMA {
            continue;
        }
        let a = &cert.atoms[e.atom as usize];
        if a.w.is_zero() {
            continue;
        }
        let mut sigmas: Vec<(u8, u8)> = Vec::new();
        for (k, ok) in e.ff.iter().enumerate() {
            if !*ok {
                sigmas.push((0u8, k as u8));
            }
        }
        for (k, ok) in e.gf.iter().enumerate() {
            if !*ok {
                sigmas.push((1u8, k as u8));
            }
        }
        mems.push(MemCand {
            atom: e.atom,
            orient: e.orient,
            sigmas,
            w: a.w.clone(),
        });
    }
    if mems.is_empty() {
        return false;
    }
    // Atom indices across B and R must be pairwise DISTINCT (§3.6): drop any candidate
    // whose atom is already collected outright in the base set, and keep at most one
    // witness per atom.
    let base: Vec<u32> = s.collected.iter().map(|(a, _)| *a).collect();
    mems.retain(|m| !base.contains(&m.atom));
    mems.sort_by(|a, b| b.w.cmp_rat(&a.w));
    let mut seen_atoms: Vec<u32> = Vec::new();
    mems.retain(|m| {
        if seen_atoms.contains(&m.atom) {
            false
        } else {
            seen_atoms.push(m.atom);
            true
        }
    });
    mems.truncate(CF_MAX_MEM);
    if mems.is_empty() {
        return false;
    }

    // Cheap bail-out: even collecting every candidate at full weight misses `need`.
    {
        let mut ceiling = base_mass.clone();
        for m in mems.iter() {
            ceiling = ceiling.add(&m.w);
        }
        if ceiling.lt(need) {
            return false;
        }
    }

    // ---- EXC witness candidates with their failing sets ----
    let mut excs: Vec<ExcCand> = Vec::new();
    for (j, k) in cert.cores.iter().enumerate() {
        let mut done = false;
        for (fi, (fac, sc)) in [(f, scf), (g, scg)].iter().enumerate() {
            let km = core_scaled(cert, sc, j);
            let fl = exempt_flags(fac, sc, k, km);
            let sig: Vec<u8> = fl
                .iter()
                .enumerate()
                .filter(|(_, ok)| !**ok)
                .map(|(i, _)| i as u8)
                .collect();
            // An empty failing set means EXEMPT already fired for this factor.
            if sig.is_empty() || sig.len() > CF_MAX_SIGMA {
                continue;
            }
            excs.push(ExcCand {
                core: j as u32,
                factor: fi as u8,
                sigmas: sig,
            });
            if excs.len() >= CF_MAX_EXC {
                done = true;
                break;
            }
        }
        if done {
            break;
        }
    }

    // ---- greedy pairing (§6 guidance; Lemma S makes soundness independent of it) ----
    let mut used = vec![false; mems.len()];
    let mut total = base_mass.clone();

    let items_of_mem = |c: &MemCand| -> Vec<CItem> {
        let a = &cert.atoms[c.atom as usize];
        c.sigmas
            .iter()
            .map(|(ep, sg)| {
                let which = atom_endpoint(c.orient as usize, *ep as usize);
                let (px, py) = if which == 0 {
                    (&a.px, &a.py)
                } else {
                    (&a.qx, &a.qy)
                };
                CItem::Mem {
                    px,
                    py,
                    sigma: *sg,
                    factor: *ep,
                }
            })
            .collect()
    };
    let items_of_exc = |c: &ExcCand| -> Vec<CItem> {
        let k = &cert.cores[c.core as usize];
        c.sigmas
            .iter()
            .map(|sg| CItem::Exc {
                core: k,
                sigma: *sg,
                factor: c.factor,
            })
            .collect()
    };

    // (MEM, EXC) pairs contribute the FULL atom weight: at an admissible (core-free)
    // point an established EXC witness would mean core overlap, so the MEM witness is
    // the established one.
    for i in 0..mems.len() {
        if used[i] {
            continue;
        }
        let wa = items_of_mem(&mems[i]);
        for ec in excs.iter() {
            let wb = items_of_exc(ec);
            if handoff_ok(&wa, &wb, f, g) {
                used[i] = true;
                total = total.add(&mems[i].w);
                break;
            }
        }
        if total.ge(need) {
            return true;
        }
    }

    // (MEM, MEM) pairs contribute min(w_i, w_j).
    for i in 0..mems.len() {
        if used[i] {
            continue;
        }
        let wa = items_of_mem(&mems[i]);
        for j in (i + 1)..mems.len() {
            if used[j] || mems[i].atom == mems[j].atom {
                continue;
            }
            let wb = items_of_mem(&mems[j]);
            if handoff_ok(&wa, &wb, f, g) {
                used[i] = true;
                used[j] = true;
                total = total.add(&mems[i].w.min_rat(&mems[j].w));
                break;
            }
        }
        if total.ge(need) {
            return true;
        }
    }
    total.ge(need)
}

// ---------------------------------------------------------------------------
// Hints (§4)
// ---------------------------------------------------------------------------

fn hint_for_root(cert: &Cert, i: usize, j: usize) -> Option<&Value> {
    let h = cert.hints.as_ref()?;
    let trees = h.get("trees")?;
    trees.get(format!("{},{}", i, j))
}

/// Structural check of a COVERED_F hint against the §4 failing-SET schema:
///   WIT = ["mem", atom, orient, FAILS]  with FAILS a non-empty list of [endpoint, sigma]
///   WIT = ["exc", core, factor, FAILS]  with FAILS a non-empty list of sigma
/// A hint using the superseded scalar-sigma form fails here and is counted as a miss.
fn covered_f_hint_shape_ok(leaf: &Value) -> bool {
    let pairs = match leaf.get("pairs") {
        Some(Value::Array(a)) => a,
        None => return true, // no witness data supplied; nothing to validate
        _ => return false,
    };
    let wit_ok = |w: &Value| -> bool {
        let a = match w.as_array() {
            Some(a) => a,
            None => return false,
        };
        if a.len() != 4 {
            return false;
        }
        let fails = match a[3].as_array() {
            Some(f) if !f.is_empty() => f,
            _ => return false,
        };
        match a[0].as_str() {
            Some("mem") => fails.iter().all(|e| {
                e.as_array().map_or(false, |q| {
                    q.len() == 2
                        && q[0].as_u64().map_or(false, |v| v <= 1)
                        && q[1].as_u64().map_or(false, |v| v <= 3)
                })
            }),
            Some("exc") => fails
                .iter()
                .all(|e| e.as_u64().map_or(false, |v| v <= 7)),
            _ => false,
        }
    };
    pairs.iter().all(|pr| {
        pr.as_array()
            .map_or(false, |q| q.len() == 2 && wit_ok(&q[0]) && wit_ok(&q[1]))
    })
}

/// Verify a hinted leaf claim EXACTLY. Returns true when the claimed clause really holds.
/// Hint witness data is untrusted guidance: everything is re-proved here.
fn verify_hint_leaf(
    cert: &Cert,
    leaf: &Value,
    f: &Factor,
    g: &Factor,
    ftg: &TGeom,
    gtg: &TGeom,
    scf: &Scale,
    scg: &Scale,
    s: &mut Scratch,
) -> bool {
    let clause = match leaf.get("clause").and_then(|v| v.as_str()) {
        Some(c) => c,
        None => return false,
    };
    match clause {
        "NONDISJOINT" => nondisjoint(f, g, ftg, gtg),
        "EXEMPT" => {
            let ci = leaf.get("core").and_then(|v| v.as_u64()).unwrap_or(u64::MAX) as usize;
            let fi = leaf.get("factor").and_then(|v| v.as_u64()).unwrap_or(2);
            if ci >= cert.cores.len() || fi > 1 {
                return false;
            }
            let (fac, sc) = if fi == 0 { (f, scf) } else { (g, scg) };
            let km = core_scaled(cert, sc, ci);
            certain_exempt(fac, sc, &cert.cores[ci], km)
        }
        "COVERED" | "COVERED_F" => {
            // The clause is re-decided from scratch by the ordinary machinery; hinted
            // witness lists are advisory and cannot make a claim true. The shape is still
            // validated so that a hint written against the pre-2026-09-02 scalar-sigma
            // schema is reported as version skew rather than silently ignored.
            if clause == "COVERED_F" && !covered_f_hint_shape_ok(leaf) {
                return false;
            }
            let ev = eval_node(cert, f, g, ftg, gtg, scf, scg, s);
            matches!(ev.discharge, Discharge::Covered | Discharge::CoveredF)
        }
        _ => false,
    }
}

// ---------------------------------------------------------------------------
// The search
// ---------------------------------------------------------------------------

struct Frame {
    f: Factor,
    g: Factor,
    /// Cached t-interval geometry, inherited unchanged by x/y splits.
    ftg: TGeom,
    gtg: TGeom,
    depth: u32,
    hint: Option<Value>,
}

struct RootRun<'a> {
    cert: &'a Cert,
    set: &'a Settings,
    counts: Counts,
    witnesses: Vec<Witness>,
    /// Total FAIL witnesses seen, including those beyond the `--faildump` storage cap.
    n_witnesses: u64,
    failed: bool,
    scratch: Scratch,
    nodes_global: &'a AtomicU64,
    stop: &'a AtomicBool,
}

impl<'a> RootRun<'a> {
    /// Record a FAIL witness, storing at most `--faildump` of them but always counting.
    fn push_witness(&mut self, w: Witness) {
        self.n_witnesses += 1;
        self.failed = true;
        if self.witnesses.len() < self.set.faildump.max(1) {
            self.witnesses.push(w);
        }
    }

    fn intervals(f: &Factor) -> [Rat; 6] {
        [
            f.t0.clone(),
            f.t1.clone(),
            f.x0.clone(),
            f.x1.clone(),
            f.y0.clone(),
            f.y1.clone(),
        ]
    }

    fn sat_margins(f: &Factor, g: &Factor, ftg: &TGeom, gtg: &TGeom) -> Vec<Rat> {
        // bound - sup|dc.n| on each of the four normals (negative => no separation proof)
        let dcx = Iv::new(g.x0.sub(&f.x1), g.x1.sub(&f.x0));
        let dcy = Iv::new(g.y0.sub(&f.y1), g.y1.sub(&f.y0));
        let c1 = ftg.c_iv();
        let s1 = ftg.s_iv();
        let c2 = gtg.c_iv();
        let s2 = gtg.s_iv();
        let cc = Iv::new(
            c1.lo.mul(&c2.lo).add(&s1.lo.mul(&s2.lo)),
            c1.hi.mul(&c2.hi).add(&s1.hi.mul(&s2.hi)),
        );
        let ss = Iv::new(
            s1.lo.mul(&c2.lo).sub(&c1.hi.mul(&s2.hi)),
            s1.hi.mul(&c2.hi).sub(&c1.lo.mul(&s2.lo)),
        );
        let g_lo = cc.inf_abs().add(&ss.inf_abs()).max_rat(&Rat::one());
        let bound = Rat::half().add(&g_lo.mul(&Rat::half()));
        let dirs: [(Iv, Iv); 4] = [
            (c1.clone(), s1.clone()),
            (Iv::new(s1.hi.neg(), s1.lo.neg()), c1.clone()),
            (c2.clone(), s2.clone()),
            (Iv::new(s2.hi.neg(), s2.lo.neg()), c2.clone()),
        ];
        dirs.iter()
            .map(|(nx, ny)| {
                let proj = dcx.mul(nx).add(&dcy.mul(ny));
                bound.sub(&proj.sup_abs())
            })
            .collect()
    }

    fn run_pair(&mut self, f0: Factor, g0: Factor, hint: Option<Value>) -> bool {
        let s = &self.cert.s;
        let mut stack: Vec<Frame> = Vec::new();
        let ftg0 = tgeom(&f0.t0, &f0.t1);
        let gtg0 = tgeom(&g0.t0, &g0.t1);
        // Clip at construction (§3.1); an empty clip is VACUOUS.
        match (f0.clip(s, &ftg0), g0.clip(s, &gtg0)) {
            (Some(a), Some(b)) => stack.push(Frame {
                f: a,
                g: b,
                ftg: ftg0,
                gtg: gtg0,
                depth: 0,
                hint,
            }),
            _ => {
                self.counts.vacuous += 1;
                return true;
            }
        }

        while let Some(fr) = stack.pop() {
            if self.stop.load(AtOrd::Relaxed) {
                return false;
            }
            let n = self.nodes_global.fetch_add(1, AtOrd::Relaxed) + 1;
            self.counts.pairs_examined += 1;
            if fr.depth > self.counts.max_depth {
                self.counts.max_depth = fr.depth;
            }

            let (f, g) = (&fr.f, &fr.g);
            let (ftg, gtg) = (fr.ftg.clone(), fr.gtg.clone());
            // The integer scaling is only consulted by the atom/core predicates; skip its
            // gcd chain entirely for certificates with neither.
            let need_scale = !self.cert.atoms.is_empty() || !self.cert.cores.is_empty();
            let dgv = if self.cert.dg > 0 { self.cert.dg } else { 1 };
            let (scf, scg) = if need_scale {
                (scale_for(f, dgv), scale_for(g, dgv))
            } else {
                (Scale::bad(), Scale::bad())
            };

            // ---- hinted leaf? ----
            let mut hinted_children: Option<(Value, Value, u8, usize, Rat)> = None;
            if let Some(h) = &fr.hint {
                if let Some(leaf) = h.get("leaf") {
                    if verify_hint_leaf(self.cert, leaf, f, g, &ftg, &gtg, &scf, &scg, &mut self.scratch) {
                        let cl = leaf.get("clause").and_then(|v| v.as_str()).unwrap_or("");
                        match cl {
                            "NONDISJOINT" => self.counts.nondisjoint += 1,
                            "EXEMPT" => self.counts.exempt_core += 1,
                            "COVERED" => self.counts.covered += 1,
                            _ => self.counts.covered_f += 1,
                        }
                        continue;
                    } else {
                        self.counts.hint_misses += 1;
                        // fall through to search mode from this node
                    }
                } else if let Some(cut) = h.get("cut") {
                    let fi = cut.get("f").and_then(|v| v.as_u64()).unwrap_or(2);
                    let dim = match cut.get("d").and_then(|v| v.as_str()) {
                        Some("t") => Some(0usize),
                        Some("x") => Some(1usize),
                        Some("y") => Some(2usize),
                        _ => None,
                    };
                    let at = cut
                        .get("at")
                        .and_then(|v| v.as_str())
                        .and_then(|t| Rat::parse(t).ok());
                    match (fi, dim, at) {
                        (fi, Some(d), Some(a)) if fi <= 1 => {
                            let lo = h.get("lo").cloned().unwrap_or(Value::Null);
                            let hi = h.get("hi").cloned().unwrap_or(Value::Null);
                            hinted_children = Some((lo, hi, fi as u8, d, a));
                        }
                        _ => {
                            self.counts.hint_misses += 1;
                        }
                    }
                }
            }

            // ---- clause table ----
            if hinted_children.is_none() {
                let ev = eval_node(self.cert, f, g, &ftg, &gtg, &scf, &scg, &mut self.scratch);
                match ev.discharge {
                    Discharge::Vacuous => {
                        self.counts.vacuous += 1;
                        continue;
                    }
                    Discharge::VacuousContain => {
                        self.counts.vacuous_contain += 1;
                        continue;
                    }
                    Discharge::Exempt => {
                        self.counts.exempt_core += 1;
                        continue;
                    }
                    Discharge::Nondisjoint => {
                        self.counts.nondisjoint += 1;
                        continue;
                    }
                    Discharge::Covered => {
                        self.counts.covered += 1;
                        continue;
                    }
                    Discharge::CoveredF => {
                        self.counts.covered_f += 1;
                        continue;
                    }
                    Discharge::None => {}
                }

                // ---- DEFICIENT-EARLY: a concrete counterexample ends the run ----
                // probe_stride == 0 disables DEFICIENT-EARLY entirely (used by the
                // throughput benchmark, which measures the B&B rather than refutation).
                let probe = self.set.probe_stride > 0
                    && (fr.depth % self.set.probe_stride == 0
                        || fr.depth + 1 >= self.set.depth);
                if probe {
                    if let Some(cf) =
                        deficient_early(self.cert, f, g, &mut self.scratch)
                    {
                        self.counts.deficient_early += 1;
                        let deficit = ev.need.sub(&ev.mass);
                        self.push_witness(Witness {
                            kind: "definitive",
                            f: Self::intervals(f),
                            g: Self::intervals(g),
                            depth: fr.depth,
                            u: ev.u,
                            certain_mass: ev.mass.clone(),
                            deficit,
                            sat_margins: Self::sat_margins(f, g, &ftg, &gtg),
                            confirm: Some(cf),
                        });
                        if !self.set.survey {
                            self.stop.store(true, AtOrd::Relaxed);
                            return false;
                        }
                        continue;
                    }
                }

                // ---- node budget: a hard stop for the whole search ----
                if n >= self.set.nodes {
                    let deficit = ev.need.sub(&ev.mass);
                    self.push_witness(Witness {
                        kind: "cap",
                        f: Self::intervals(f),
                        g: Self::intervals(g),
                        depth: fr.depth,
                        u: ev.u,
                        certain_mass: ev.mass.clone(),
                        deficit,
                        sat_margins: Self::sat_margins(f, g, &ftg, &gtg),
                        confirm: None,
                    });
                    self.stop.store(true, AtOrd::Relaxed);
                    return false;
                }

                // ---- depth cap: an undischarged leaf is a FAIL witness ----
                if fr.depth >= self.set.depth {
                    let deficit = ev.need.sub(&ev.mass);
                    let cf = deficient_early(self.cert, f, g, &mut self.scratch);
                    self.push_witness(Witness {
                        kind: "cap",
                        f: Self::intervals(f),
                        g: Self::intervals(g),
                        depth: fr.depth,
                        u: ev.u,
                        certain_mass: ev.mass.clone(),
                        deficit,
                        sat_margins: Self::sat_margins(f, g, &ftg, &gtg),
                        confirm: cf,
                    });
                    if !self.set.survey {
                        self.stop.store(true, AtOrd::Relaxed);
                        return false;
                    }
                    self.failed = true;
                    continue;
                }
            }

            // ---- split ----
            let (fi, dim, cut, hl, hh) = match hinted_children {
                Some((lo, hi, fi, d, at)) => {
                    (fi, d, Some(at), Some(lo), Some(hi))
                }
                None => {
                    let (fi, d) = self.choose_split(f, g);
                    (fi, d, None, None, None)
                }
            };
            let fac = if fi == 0 { f } else { g };
            let cut = match cut {
                Some(c) => c,
                None => self.margin_aware_cut(fac, fi, dim),
            };
            let children = match fac.split_at(dim, &cut) {
                Some(c) => c,
                None => {
                    // A hinted cut point outside its interval is a malformed hint:
                    // fall back to a midpoint split (verdict unaffected).
                    if hl.is_some() {
                        self.counts.hint_misses += 1;
                    }
                    let mid = match dim {
                        0 => fac.t0.mid(&fac.t1),
                        1 => fac.x0.mid(&fac.x1),
                        _ => fac.y0.mid(&fac.y1),
                    };
                    match fac.split_at(dim, &mid) {
                        Some(c) => c,
                        None => {
                            // Degenerate interval: cannot split further.
                            let ev = eval_node(self.cert, f, g, &ftg, &gtg, &scf, &scg, &mut self.scratch);
                            self.push_witness(Witness {
                                kind: "cap",
                                f: Self::intervals(f),
                                g: Self::intervals(g),
                                depth: fr.depth,
                                u: ev.u,
                                certain_mass: ev.mass.clone(),
                                deficit: ev.need.sub(&ev.mass),
                                sat_margins: Self::sat_margins(f, g, &ftg, &gtg),
                                confirm: None,
                            });
                            self.stop.store(true, AtOrd::Relaxed);
                            return false;
                        }
                    }
                }
            };
            self.counts.split += 1;

            let mk = |child: Factor, hint: Option<Value>| -> Option<Frame> {
                // Only a t-split invalidates the cached trig block.
                let ctg = if dim == 0 {
                    tgeom(&child.t0, &child.t1)
                } else if fi == 0 {
                    ftg.clone()
                } else {
                    gtg.clone()
                };
                let (nf, ng, nftg, ngtg) = if fi == 0 {
                    (child.clip(s, &ctg), Some(g.clone()), ctg, gtg.clone())
                } else {
                    (Some(f.clone()), child.clip(s, &ctg), ftg.clone(), ctg)
                };
                match (nf, ng) {
                    (Some(a), Some(b)) => Some(Frame {
                        f: a,
                        g: b,
                        ftg: nftg,
                        gtg: ngtg,
                        depth: fr.depth + 1,
                        hint,
                    }),
                    _ => None,
                }
            };
            for (child, hint) in [(children.0, hl), (children.1, hh)] {
                let hint = hint.filter(|v| !v.is_null());
                match mk(child, hint) {
                    Some(fr2) => stack.push(fr2),
                    None => self.counts.vacuous += 1,
                }
            }
        }
        true
    }

    /// §6 margin-aware choice: possible-collectability gate + weight-per-needed-shrink.
    ///
    /// Two things keep this from thrashing, both learned the hard way on the A73 anchors:
    ///
    /// 1. Only atoms POSSIBLY collectable in BOTH factors are eligible. One reachable on
    ///    a single side can never reach COVERED, and chasing it collapses that factor to
    ///    a point while the other stays unsplit.
    /// 2. Candidates are ranked by weight per NEEDED SHRINK, not by weight alone. A
    ///    tangentially-reachable atom (pinned min stuck at, say, -1/4 no matter how the
    ///    t-range is halved) has an enormous needed shrink, so it ranks last instead of
    ///    being chased forever while x and y collapse for vanishing gains.
    ///
    /// Finally, if no dimension's halving strictly improves the target constraint, the
    /// v1 widest-dimension rule takes over so the box always makes progress.
    fn choose_split(&mut self, f: &Factor, g: &Factor) -> (u8, usize) {
        let fb = FBox::of(f);
        let gb = FBox::of(g);

        // Worst (most negative) pinned constraint minimum for one eval.
        let worst_of = |e: &AtomEval, a: &crate::cert::Atom| -> Option<(f64, u8, u8)> {
            let mut worst: Option<(f64, u8, u8)> = None;
            for (which, flags) in [(0u8, &e.ff), (1u8, &e.gf)] {
                let b = if which == 0 { &fb } else { &gb };
                let pt = atom_endpoint(e.orient as usize, which as usize);
                let (px, py) = if pt == 0 { (a.pxf, a.pyf) } else { (a.qxf, a.qyf) };
                for (k, ok) in flags.iter().enumerate() {
                    if *ok {
                        continue;
                    }
                    let sigma = k as u8;
                    let (cx, cy) = min_corner_f(sigma, b);
                    let (qa, qb, qc) = mem_quad_f(sigma, px, py, cx, cy);
                    let m = quad_min_f(qa, qb, qc, b.t0, b.t1);
                    if worst.map_or(true, |(bm, _, _)| m < bm) {
                        worst = Some((m, which, sigma));
                    }
                }
            }
            worst
        };

        let mut best: Option<(f64, usize, f64, u8, u8)> = None; // score, idx, min, which, sigma
        for (idx, e) in self.scratch.evals.iter().enumerate() {
            if e.nfail == 0 || !e.possible {
                continue;
            }
            let a = &self.cert.atoms[e.atom as usize];
            if a.w.is_zero() {
                continue;
            }
            let (m, which, sigma) = match worst_of(e, a) {
                Some(w) => w,
                None => continue,
            };
            // Needed shrink is proxied by how negative the pinned minimum is.
            let score = a.wf / (1e-12 + (-m).max(0.0));
            if best.map_or(true, |(bs, _, _, _, _)| score > bs) {
                best = Some((score, idx, m, which, sigma));
            }
        }

        let (_, idx, _, which, sigma) = match best {
            Some(b) => b,
            None => return widest_dim(f, g),
        };
        let e = self.scratch.evals[idx].clone();
        let a = &self.cert.atoms[e.atom as usize];

        // Halve each of the three dimensions; keep whichever most improves the target
        // constraint's pinned minimum (measured on the better of the two halves).
        let b = if which == 0 { fb } else { gb };
        let pt = atom_endpoint(e.orient as usize, which as usize);
        let (px, py) = if pt == 0 { (a.pxf, a.pyf) } else { (a.qxf, a.qyf) };
        let pinned_min = |bx: &FBox| -> f64 {
            let (cx, cy) = min_corner_f(sigma, bx);
            let (qa, qb, qc) = mem_quad_f(sigma, px, py, cx, cy);
            quad_min_f(qa, qb, qc, bx.t0, bx.t1)
        };
        let base = pinned_min(&b);
        let mut best_dim: Option<(f64, usize)> = None;
        for d in 0usize..3 {
            let (lo, hi) = match d {
                0 => (b.t0, b.t1),
                1 => (b.x0, b.x1),
                _ => (b.y0, b.y1),
            };
            if !(hi > lo) {
                continue;
            }
            let mid = 0.5 * (lo + hi);
            let mut lo_half = b;
            let mut hi_half = b;
            match d {
                0 => {
                    lo_half.t1 = mid;
                    hi_half.t0 = mid;
                }
                1 => {
                    lo_half.x1 = mid;
                    hi_half.x0 = mid;
                }
                _ => {
                    lo_half.y1 = mid;
                    hi_half.y0 = mid;
                }
            }
            let v = pinned_min(&lo_half).max(pinned_min(&hi_half));
            if best_dim.map_or(true, |(bv, _)| v > bv) {
                best_dim = Some((v, d));
            }
        }
        // Require the halving to close a MEANINGFUL fraction of the remaining gap, not
        // merely to be positive. Shrinking an already-tiny centre interval buys an
        // improvement of order its own width, which stays strictly positive forever while
        // the constraint is really blocked by the unsplit t-range — that is precisely the
        // observed 40-depth collapse. Below this bar the v1 widest-dimension rule takes
        // over, which splits t (weighted x2) and actually unblocks the box.
        let gap = (-base).max(0.0);
        let needed = 0.01 * gap.max(1e-9);
        match best_dim {
            Some((v, d)) if v - base > needed => (which, d),
            _ => widest_dim(f, g),
        }
    }

    /// Free rational cut (§3.2): any rational point strictly interior to the chosen
    /// dimension's interval is admissible, so the cut is placed at the constraint
    /// frontier when one is bracketed, and at the midpoint otherwise.
    ///
    /// Candidates come from the per-node Lemma M cache; on boxes where no atom is even a
    /// possible certain member the cache is empty and the midpoint is used directly.
    fn margin_aware_cut(&mut self, fac: &Factor, which: u8, dim: usize) -> Rat {
        let mid = match dim {
            0 => fac.t0.mid(&fac.t1),
            1 => fac.x0.mid(&fac.x1),
            _ => fac.y0.mid(&fac.y1),
        };
        if dim != 0 || self.scratch.evals.is_empty() {
            return mid;
        }
        // Find one failing membership constraint on this factor and cut at the rational
        // point where its pinned slack quadratic changes sign (exact sign bisection).
        for e in self.scratch.evals.iter() {
            let flags = if which == 0 { &e.ff } else { &e.gf };
            let sigma = match flags.iter().position(|ok| !*ok) {
                Some(k) => k as u8,
                None => continue,
            };
            let a = &self.cert.atoms[e.atom as usize];
            let ep = if which == 0 { 0usize } else { 1usize };
            let pt = atom_endpoint(e.orient as usize, ep);
            let (px, py) = if pt == 0 {
                (&a.px, &a.py)
            } else {
                (&a.qx, &a.qy)
            };
            let (cx, cy) = mem_worst_corner(sigma, fac);
            let (qa, qb, qc) = mem_quad_at(sigma, px, py, &cx, &cy);
            if let Some(cut) = margin_cut_t(&qa, &qb, &qc, &fac.t0, &fac.t1) {
                return cut;
            }
        }
        mid
    }
}

// ---------------------------------------------------------------------------
// Driver
// ---------------------------------------------------------------------------

pub fn verify(cert: &Cert, set: &Settings) -> Outcome {
    let roots = build_roots(&cert.s, set.split);
    let nf = roots.len();
    let mut pairs: Vec<(usize, usize)> = Vec::with_capacity(nf * (nf + 1) / 2);
    for i in 0..nf {
        for j in i..nf {
            pairs.push((i, j));
        }
    }
    let nodes_global = AtomicU64::new(0);
    let stop = AtomicBool::new(false);
    let next = AtomicU64::new(0);

    let jobs = set.jobs.max(1).min(64);
    let mut all_counts = Counts::default();
    all_counts.pairs_root = pairs.len() as u64;
    let mut all_wit: Vec<Witness> = Vec::new();
    let mut ok = true;
    let mut n_wit: u64 = 0;

    let work = |slot: &mut Slot| {
        let mut run = RootRun {
            cert,
            set,
            counts: Counts::default(),
            witnesses: Vec::new(),
            n_witnesses: 0,
            failed: false,
            scratch: Scratch::new(cert.atoms.len()),
            nodes_global: &nodes_global,
            stop: &stop,
        };
        loop {
            let idx = next.fetch_add(1, AtOrd::Relaxed) as usize;
            if idx >= pairs.len() {
                break;
            }
            if stop.load(AtOrd::Relaxed) {
                break;
            }
            let (i, j) = pairs[idx];
            let hint = hint_for_root(cert, i, j).cloned();
            let cont = run.run_pair(roots[i].clone(), roots[j].clone(), hint);
            if !cont && !set.survey {
                break;
            }
        }
        slot.counts = run.counts;
        slot.witnesses = run.witnesses;
        slot.failed = run.failed;
        slot.n_witnesses = run.n_witnesses;
    };

    if jobs == 1 {
        let mut slot = Slot::default();
        work(&mut slot);
        all_counts.merge(&slot.counts);
        all_wit.extend(slot.witnesses);
        n_wit += slot.n_witnesses;
        ok &= !slot.failed;
    } else {
        let mut slots: Vec<Slot> = (0..jobs).map(|_| Slot::default()).collect();
        std::thread::scope(|sc| {
            for slot in slots.iter_mut() {
                sc.spawn(|| work(slot));
            }
        });
        for slot in slots {
            all_counts.merge(&slot.counts);
            all_wit.extend(slot.witnesses);
            n_wit += slot.n_witnesses;
            ok &= !slot.failed;
        }
    }

    all_wit.truncate(set.faildump.max(1));
    Outcome {
        pass: ok,
        counts: all_counts,
        witnesses: all_wit,
        n_witnesses: n_wit,
        nodes: nodes_global.load(AtOrd::Relaxed),
    }
}

/// Test hook: certain collected mass over one pair box, and whether COVERED fires.
/// Used by the `--selftest` corruption gates to exercise the mass-dependent branch.
pub fn covered_probe(cert: &Cert, f: &Factor, g: &Factor) -> (Rat, bool) {
    let dg = if cert.dg > 0 { cert.dg } else { 1 };
    let scf = scale_for(f, dg);
    let scg = scale_for(g, dg);
    let ftg = tgeom(&f.t0, &f.t1);
    let gtg = tgeom(&g.t0, &g.t1);
    let mut s = Scratch::new(cert.atoms.len());
    let mass = gather_evals(cert, f, g, &scf, &scg, &mut s, 0.0);
    let beta_active = cert.beta.is_pos() && !cert.boxes.is_empty();
    let u = if beta_active {
        u_bound(f, g, &ftg, &gtg, &cert.boxes)
    } else {
        0
    };
    let need = Rat::one().add(&cert.beta.mul(&Rat::from_int(u as i128)));
    let need = if beta_active { need } else { Rat::one() };
    let fires = mass.ge(&need);
    (mass, fires)
}

#[derive(Default)]
struct Slot {
    counts: Counts,
    witnesses: Vec<Witness>,
    failed: bool,
    n_witnesses: u64,
}
