//! Geometry and the exact discharge predicates of pair-certificate-v2 §3.
//!
//! Parametrisation (v2 §3.0, verbatim v1): t = tan(theta/2) in [0,1],
//!   C(t) = (1 - t^2)/(1 + t^2),  S(t) = 2t/(1 + t^2),  w(t) = C + S.
//! On t in [0,1]: C >= 0, S >= 0, 1 - t^2 >= 0, t >= 0 (the sign-fixedness used throughout).
//! Body frame PINNED as v1: u = C*dx + S*dy, v = -S*dx + C*dy, with d = p - c.

use crate::rat::{lemma_q_int, lemma_q_rat, quad_min_on, Rat};

// ---------------------------------------------------------------------------
// sqrt(2) brackets (v1 §3.1 / v2 §3.1). These constants are load-bearing: a
// "1.414-ish" rational BELOW sqrt(2) is UNSOUND as an upper bound for w.
// ---------------------------------------------------------------------------

/// 408/985 < t* = sqrt(2) - 1, certified by 1393^2 = 1940449 < 1940450 = 2*985^2.
pub const TSTAR_LO_N: i128 = 408;
pub const TSTAR_LO_D: i128 = 985;
/// t* < 5741/13860, certified by 19601^2 = 384199201 > 384199200 = 2*13860^2.
pub const TSTAR_HI_N: i128 = 5741;
pub const TSTAR_HI_D: i128 = 13860;
/// w_hi on any interval containing t*: 19601/13860 > sqrt(2).
pub const WMAX_N: i128 = 19601;
pub const WMAX_D: i128 = 13860;

/// Verify the two integer identities that make the sqrt(2) brackets sound.
/// Called from `--selftest` and asserted in debug builds.
pub fn check_sqrt2_constants() -> Result<(), String> {
    // 1393/985 < sqrt(2)  <=>  1393^2 < 2 * 985^2   (so 408/985 < sqrt(2) - 1)
    let a = (TSTAR_LO_N + TSTAR_LO_D) as i128; // 1393
    if !(a * a < 2 * TSTAR_LO_D * TSTAR_LO_D) {
        return Err("sqrt2 lower bracket identity FAILED".into());
    }
    // 19601/13860 > sqrt(2)  <=>  19601^2 > 2 * 13860^2
    if !(WMAX_N * WMAX_N > 2 * WMAX_D * WMAX_D) {
        return Err("sqrt2 upper bracket identity FAILED".into());
    }
    // t*_hi = w_max - 1 must hold as written in the spec.
    if TSTAR_HI_N + TSTAR_HI_D != WMAX_N || TSTAR_HI_D != WMAX_D {
        return Err("t* upper bracket inconsistent with w_max".into());
    }
    Ok(())
}

pub fn tstar_lo() -> Rat {
    Rat::new(TSTAR_LO_N, TSTAR_LO_D).unwrap()
}
pub fn tstar_hi() -> Rat {
    Rat::new(TSTAR_HI_N, TSTAR_HI_D).unwrap()
}
pub fn wmax() -> Rat {
    Rat::new(WMAX_N, WMAX_D).unwrap()
}

/// C(t) = (1 - t^2) / (1 + t^2).
///
/// With t = p/q (q > 0) this is exactly (q^2 - p^2)/(q^2 + p^2), which is one reduced
/// construction instead of a chain of rational ops — the hot path takes that form.
pub fn c_at(t: &Rat) -> Rat {
    if let Some((p, q)) = t.small() {
        if let (Some(p2), Some(q2)) = (p.checked_mul(p), q.checked_mul(q)) {
            if let (Some(num), Some(den)) = (q2.checked_sub(p2), q2.checked_add(p2)) {
                if let Some(r) = Rat::new(num, den) {
                    return r;
                }
            }
        }
    }
    let t2 = t.mul(t);
    Rat::one()
        .sub(&t2)
        .div(&Rat::one().add(&t2))
        .expect("1 + t^2 > 0")
}

/// S(t) = 2t / (1 + t^2) = 2pq / (q^2 + p^2).
pub fn s_at(t: &Rat) -> Rat {
    if let Some((p, q)) = t.small() {
        if let (Some(p2), Some(q2), Some(pq)) =
            (p.checked_mul(p), q.checked_mul(q), p.checked_mul(q))
        {
            if let (Some(num), Some(den)) = (pq.checked_mul(2), q2.checked_add(p2)) {
                if let Some(r) = Rat::new(num, den) {
                    return r;
                }
            }
        }
    }
    let t2 = t.mul(t);
    t.mul(&Rat::from_int(2))
        .div(&Rat::one().add(&t2))
        .expect("1 + t^2 > 0")
}

/// Everything derived from a factor's t-interval alone: the exact C and S ranges and the
/// w bounds. Splitting x or y leaves the t-interval untouched, so this block is computed
/// once and inherited by such children — it is the dominant per-node cost otherwise.
#[derive(Clone, Debug)]
pub struct TGeom {
    /// C over [t0,t1] (C is DECREASING on [0,1]): [C(t1), C(t0)].
    pub clo: Rat,
    pub chi: Rat,
    /// S over [t0,t1] (S is INCREASING on [0,1]): [S(t0), S(t1)].
    pub slo: Rat,
    pub shi: Rat,
    pub wlo: Rat,
    pub whi: Rat,
}

/// Build the cached t-interval geometry. Four exact divisions; w(t0) and w(t1) are then
/// recovered from the already-computed C and S endpoints without further division.
pub fn tgeom(t0: &Rat, t1: &Rat) -> TGeom {
    let c0 = c_at(t0);
    let c1 = c_at(t1);
    let s0 = s_at(t0);
    let s1 = s_at(t1);
    // w(t0) = C(t0) + S(t0), w(t1) = C(t1) + S(t1).
    let w0 = c0.add(&s0);
    let w1 = c1.add(&s1);
    let wlo = w0.min_rat(&w1);
    // Upper bound of w (v1 §3.1): exact only when the interval provably excludes
    // t* = sqrt(2) - 1; otherwise the sound constant 19601/13860 > sqrt(2).
    let whi = if t1.le(&tstar_lo()) || t0.ge(&tstar_hi()) {
        w0.max_rat(&w1)
    } else {
        wmax()
    };
    TGeom {
        clo: c1,
        chi: c0,
        slo: s0,
        shi: s1,
        wlo,
        whi,
    }
}

impl TGeom {
    pub fn c_iv(&self) -> Iv {
        Iv {
            lo: self.clo.clone(),
            hi: self.chi.clone(),
        }
    }
    pub fn s_iv(&self) -> Iv {
        Iv {
            lo: self.slo.clone(),
            hi: self.shi.clone(),
        }
    }
}
/// w(t) = C(t) + S(t) = (1 - t^2 + 2t) / (1 + t^2).
pub fn w_at(t: &Rat) -> Rat {
    c_at(t).add(&s_at(t))
}

/// Lower bound of w on [t0,t1]: min(w(t0), w(t1)).
/// Valid because w is quasiconcave on [0,1] with its single maximum at t* = sqrt(2) - 1,
/// so the minimum over a subinterval is attained at an endpoint (v1 §3.1).
pub fn w_lo(t0: &Rat, t1: &Rat) -> Rat {
    w_at(t0).min_rat(&w_at(t1))
}

/// Upper bound of w on [t0,t1] (v1 §3.1).
///
/// If the interval PROVABLY excludes t* — i.e. t1 <= 408/985 or t0 >= 5741/13860 — then
/// w is monotone on it and max(w(t0), w(t1)) is exact. Otherwise the interval may contain
/// t*, and the only sound bound is 19601/13860 > sqrt(2).
pub fn w_hi(t0: &Rat, t1: &Rat) -> Rat {
    if t1.le(&tstar_lo()) || t0.ge(&tstar_hi()) {
        w_at(t0).max_rat(&w_at(t1))
    } else {
        wmax()
    }
}

// ---------------------------------------------------------------------------
// Factor boxes
// ---------------------------------------------------------------------------

/// A factor box F = [t0,t1] x [x0,x1] x [y0,y1].
#[derive(Clone, Debug)]
pub struct Factor {
    pub t0: Rat,
    pub t1: Rat,
    pub x0: Rat,
    pub x1: Rat,
    pub y0: Rat,
    pub y1: Rat,
}

impl Factor {
    /// VACUOUS clip (v1 §3.1, verbatim): centres are restricted to
    /// [w_lo/2, s - w_lo/2]^2 with w_lo = min(w(t0), w(t1)). Returns None when the
    /// clipped box is empty (the box is then discharged VACUOUS at construction).
    ///
    /// The clip is OUTWARD: it contains every admissible placement of the box.
    pub fn clip(&self, s: &Rat, tg: &TGeom) -> Option<Factor> {
        let half = tg.wlo.mul(&Rat::half());
        let lo = half.clone();
        let hi = s.sub(&half);
        if hi.lt(&lo) {
            return None;
        }
        let nx0 = self.x0.max_rat(&lo);
        let nx1 = self.x1.min_rat(&hi);
        if nx1.lt(&nx0) {
            return None;
        }
        let ny0 = self.y0.max_rat(&lo);
        let ny1 = self.y1.min_rat(&hi);
        if ny1.lt(&ny0) {
            return None;
        }
        Some(Factor {
            t0: self.t0.clone(),
            t1: self.t1.clone(),
            x0: nx0,
            x1: nx1,
            y0: ny0,
            y1: ny1,
        })
    }

    pub fn width(&self, dim: usize) -> Rat {
        match dim {
            0 => self.t1.sub(&self.t0),
            1 => self.x1.sub(&self.x0),
            _ => self.y1.sub(&self.y0),
        }
    }

    /// Split along `dim` (0=t, 1=x, 2=y) at rational `cut`, which MUST be strictly
    /// interior to that dimension's interval. Returns (lo child, hi child).
    pub fn split_at(&self, dim: usize, cut: &Rat) -> Option<(Factor, Factor)> {
        let (lo, hi) = match dim {
            0 => (&self.t0, &self.t1),
            1 => (&self.x0, &self.x1),
            _ => (&self.y0, &self.y1),
        };
        if !(cut.gt(lo) && cut.lt(hi)) {
            return None;
        }
        let mut a = self.clone();
        let mut b = self.clone();
        match dim {
            0 => {
                a.t1 = cut.clone();
                b.t0 = cut.clone();
            }
            1 => {
                a.x1 = cut.clone();
                b.x0 = cut.clone();
            }
            _ => {
                a.y1 = cut.clone();
                b.y0 = cut.clone();
            }
        }
        Some((a, b))
    }
}

// ---------------------------------------------------------------------------
// VACUOUS-CONTAIN (spec §3.3 item 1b)
// ---------------------------------------------------------------------------

/// Does EVERY placement of this factor violate containment in [0,s]^2 on one side?
///
/// The §3.1 clip uses w_lo = min(w(t0), w(t1)), so near t in {0,1} it retains placements
/// with e.g. cx in [1/2, w(t)/2) that stick out of the container. No other clause can
/// discharge those, and splitting t regresses forever (the clip's lower bound stays 1/2
/// as long as an endpoint of the t-range is 0 or 1). This clause closes that hole.
///
/// Exact, endpoint-only test per side. Containment on the left needs cx - w(t)/2 >= 0;
/// that slack increases in cx, so it is pinned at cx = x1, and multiplying by
/// (1 + t^2) > 0 with w(t)(1 + t^2) = 1 + 2t - t^2 gives
///     q(t) = (x1 + 1/2) t^2 - t + (x1 - 1/2).
/// The leading coefficient x1 + 1/2 is positive (centres are clipped to >= w_lo/2 > 0),
/// so the supremum over [t0,t1] is attained at an endpoint: q < 0 at BOTH endpoints
/// proves every placement violates the left side. Right/bottom/top are the same with
/// s - x0, y1 and s - y0.
///
/// Soundness: (P2') quantifies only over closed unit squares contained in [0,s]^2, so a
/// box holding no contained placement carries no obligation.
pub fn vacuous_contain(f: &Factor, s: &Rat) -> bool {
    let h = Rat::half();
    // q(t) = (v + 1/2) t^2 - t + (v - 1/2), evaluated exactly at both endpoints.
    let side_violated = |v: &Rat| -> bool {
        let a = v.add(&h);
        let c = v.sub(&h);
        let at = |t: &Rat| -> Rat { a.mul(t).mul(t).sub(t).add(&c) };
        at(&f.t0).is_neg() && at(&f.t1).is_neg()
    };
    side_violated(&f.x1)
        || side_violated(&s.sub(&f.x0))
        || side_violated(&f.y1)
        || side_violated(&s.sub(&f.y0))
}

// ---------------------------------------------------------------------------
// Rational intervals (used by NONDISJOINT and the U bound, which keep the v1
// outward interval enclosures per v2 §8).
// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
pub struct Iv {
    pub lo: Rat,
    pub hi: Rat,
}

impl Iv {
    pub fn new(lo: Rat, hi: Rat) -> Iv {
        Iv { lo, hi }
    }
    pub fn add(&self, o: &Iv) -> Iv {
        Iv {
            lo: self.lo.add(&o.lo),
            hi: self.hi.add(&o.hi),
        }
    }
    pub fn sub(&self, o: &Iv) -> Iv {
        Iv {
            lo: self.lo.sub(&o.hi),
            hi: self.hi.sub(&o.lo),
        }
    }
    /// Interval product. When one operand has a fixed sign — which is always the case
    /// here, since the multiplier is a C or S range (or its negation) and C, S >= 0 on
    /// [0,1] — only two products are needed instead of four.
    pub fn mul(&self, o: &Iv) -> Iv {
        let (sl, sh) = (self.lo.sign(), self.hi.sign());
        if o.lo.sign() >= 0 {
            if sl >= 0 {
                return Iv { lo: self.lo.mul(&o.lo), hi: self.hi.mul(&o.hi) };
            }
            if sh <= 0 {
                return Iv { lo: self.lo.mul(&o.hi), hi: self.hi.mul(&o.lo) };
            }
            return Iv { lo: self.lo.mul(&o.hi), hi: self.hi.mul(&o.hi) };
        }
        if o.hi.sign() <= 0 {
            if sl >= 0 {
                return Iv { lo: self.hi.mul(&o.lo), hi: self.lo.mul(&o.hi) };
            }
            if sh <= 0 {
                return Iv { lo: self.hi.mul(&o.hi), hi: self.lo.mul(&o.lo) };
            }
            return Iv { lo: self.hi.mul(&o.lo), hi: self.lo.mul(&o.lo) };
        }
        let a = self.lo.mul(&o.lo);
        let b = self.lo.mul(&o.hi);
        let c = self.hi.mul(&o.lo);
        let d = self.hi.mul(&o.hi);
        let lo = a.min_rat(&b).min_rat(&c).min_rat(&d);
        let hi = a.max_rat(&b).max_rat(&c).max_rat(&d);
        Iv { lo, hi }
    }
    /// sup |x| over the interval.
    pub fn sup_abs(&self) -> Rat {
        self.lo.abs().max_rat(&self.hi.abs())
    }
    /// inf |x| over the interval (zero when the interval straddles 0).
    pub fn inf_abs(&self) -> Rat {
        if self.lo.sign() <= 0 && self.hi.sign() >= 0 {
            Rat::zero()
        } else {
            self.lo.abs().min_rat(&self.hi.abs())
        }
    }
}

// ---------------------------------------------------------------------------
// Per-node integer scaling (the hot path).
//
// All coordinates of a factor box and of the atom/core coordinates are put over one
// common POSITIVE denominator M. Each membership/exemption quadratic then has INTEGER
// coefficients over the common denominator 2M, and Lemma Q becomes pure integer sign
// tests with no gcd in the inner loop.
// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
pub struct Scale {
    pub ok: bool,
    pub m: i128,
    pub x0m: i128,
    pub x1m: i128,
    pub y0m: i128,
    pub y1m: i128,
    pub p0: i128,
    pub q0: i128,
    pub p1: i128,
    pub q1: i128,
    /// M / dg, where dg is the global coordinate denominator of the atom/core table.
    pub mul_coord: i128,
}

impl Scale {
    pub fn bad() -> Scale {
        Scale {
            ok: false,
            m: 1,
            x0m: 0,
            x1m: 0,
            y0m: 0,
            y1m: 0,
            p0: 0,
            q0: 1,
            p1: 1,
            q1: 1,
            mul_coord: 1,
        }
    }
}

fn lcm_checked(a: i128, b: i128) -> Option<i128> {
    let g = crate::rat::gcd_i128(a, b);
    if g == 0 {
        return None;
    }
    (a / g).checked_mul(b)
}

/// Build the integer scaling for a factor box against a global coordinate denominator.
/// Returns a `Scale` with `ok = false` when anything leaves the i128 range; callers then
/// fall back to the (always correct) rational path.
pub fn scale_for(f: &Factor, dg: i128) -> Scale {
    let get = |r: &Rat| -> Option<(i128, i128)> { r.small() };
    let (a0, b0) = match get(&f.x0) {
        Some(v) => v,
        None => return Scale::bad(),
    };
    let (a1, b1) = match get(&f.x1) {
        Some(v) => v,
        None => return Scale::bad(),
    };
    let (c0, d0) = match get(&f.y0) {
        Some(v) => v,
        None => return Scale::bad(),
    };
    let (c1, d1) = match get(&f.y1) {
        Some(v) => v,
        None => return Scale::bad(),
    };
    let (p0, q0) = match get(&f.t0) {
        Some(v) => v,
        None => return Scale::bad(),
    };
    let (p1, q1) = match get(&f.t1) {
        Some(v) => v,
        None => return Scale::bad(),
    };
    let m = match (|| -> Option<i128> {
        let m = lcm_checked(b0, b1)?;
        let m = lcm_checked(m, d0)?;
        let m = lcm_checked(m, d1)?;
        lcm_checked(m, dg)
    })() {
        Some(v) => v,
        None => return Scale::bad(),
    };
    let sc = |n: i128, d: i128| -> Option<i128> { n.checked_mul(m / d) };
    let (x0m, x1m, y0m, y1m) = match (|| -> Option<(i128, i128, i128, i128)> {
        Some((sc(a0, b0)?, sc(a1, b1)?, sc(c0, d0)?, sc(c1, d1)?))
    })() {
        Some(v) => v,
        None => return Scale::bad(),
    };
    Scale {
        ok: true,
        m,
        x0m,
        x1m,
        y0m,
        y1m,
        p0,
        q0,
        p1,
        q1,
        mul_coord: m / dg,
    }
}

// ---------------------------------------------------------------------------
// Lemma M — exact certain membership (spec §3.4)
// ---------------------------------------------------------------------------

/// The four slack quadratics of Lemma M, as integer coefficient triples over 2M.
///
/// Pinning (spec §3.4, verified independently against the sign-fixedness argument):
/// the pinning corner is where that CONSTRAINT'S SLACK is minimal.
///   g1 [u <= 1/2]  at (x0,y0)    g2 [u >= -1/2] at (x1,y1)
///   g3 [v <= 1/2]  at (x1,y0)    g4 [v >= -1/2] at (x0,y1)
#[inline]
pub fn mem_quads_int(sc: &Scale, pxm: i128, pym: i128) -> Option<[(i128, i128, i128); 4]> {
    let m = sc.m;
    let dx0 = pxm.checked_sub(sc.x0m)?;
    let dx1 = pxm.checked_sub(sc.x1m)?;
    let dy0 = pym.checked_sub(sc.y0m)?;
    let dy1 = pym.checked_sub(sc.y1m)?;
    let t2 = |v: i128| v.checked_mul(2);
    let t4 = |v: i128| v.checked_mul(4);
    // g1 at (x0,y0):  A = 1/2 + dx, B = -2dy, C = 1/2 - dx
    let g1 = (
        m.checked_add(t2(dx0)?)?,
        t4(dy0)?.checked_neg()?,
        m.checked_sub(t2(dx0)?)?,
    );
    // g2 at (x1,y1):  A = 1/2 - dx, B = 2dy,  C = 1/2 + dx
    let g2 = (
        m.checked_sub(t2(dx1)?)?,
        t4(dy1)?,
        m.checked_add(t2(dx1)?)?,
    );
    // g3 at (x1,y0):  A = 1/2 + dy, B = 2dx,  C = 1/2 - dy
    let g3 = (
        m.checked_add(t2(dy0)?)?,
        t4(dx1)?,
        m.checked_sub(t2(dy0)?)?,
    );
    // g4 at (x0,y1):  A = 1/2 - dy, B = -2dx, C = 1/2 + dy
    let g4 = (
        m.checked_sub(t2(dy1)?)?,
        t4(dx0)?.checked_neg()?,
        m.checked_add(t2(dy1)?)?,
    );
    Some([g1, g2, g3, g4])
}

/// Rational form of the four Lemma M quadratics (reference path; always correct).
pub fn mem_quads_rat(f: &Factor, px: &Rat, py: &Rat) -> [(Rat, Rat, Rat); 4] {
    let h = Rat::half();
    let two = Rat::from_int(2);
    let mk = |dx: Rat, dy: Rat, which: usize| -> (Rat, Rat, Rat) {
        match which {
            0 => (h.add(&dx), dy.mul(&two).neg(), h.sub(&dx)),
            1 => (h.sub(&dx), dy.mul(&two), h.add(&dx)),
            2 => (h.add(&dy), dx.mul(&two), h.sub(&dy)),
            _ => (h.sub(&dy), dx.mul(&two).neg(), h.add(&dy)),
        }
    };
    [
        mk(px.sub(&f.x0), py.sub(&f.y0), 0),
        mk(px.sub(&f.x1), py.sub(&f.y1), 1),
        mk(px.sub(&f.x1), py.sub(&f.y0), 2),
        mk(px.sub(&f.x0), py.sub(&f.y1), 3),
    ]
}

/// **Lemma M**: is `p` inside Q(c, theta(t)) for EVERY (t, cx, cy) in the factor box?
/// This is an IFF — certain membership fires exactly when membership is mathematically
/// certain over the whole box.
pub fn certain_member(
    f: &Factor,
    sc: &Scale,
    px: &Rat,
    py: &Rat,
    pm: Option<(i128, i128)>,
) -> bool {
    if let (true, Some((pxm, pym))) = (sc.ok, pm) {
        if let Some(qs) = mem_quads_int(sc, pxm, pym) {
            for (a, b, c) in qs.iter() {
                if !lemma_q_int(*a, *b, *c, sc.p0, sc.q0, sc.p1, sc.q1) {
                    return false;
                }
            }
            return true;
        }
    }
    let qs = mem_quads_rat(f, px, py);
    for (a, b, c) in qs.iter() {
        if !lemma_q_rat(a, b, c, &f.t0, &f.t1) {
            return false;
        }
    }
    true
}

/// Per-constraint results of Lemma M (used by COVERED-F to find single-failure witnesses).
pub fn member_flags(
    f: &Factor,
    sc: &Scale,
    px: &Rat,
    py: &Rat,
    pm: Option<(i128, i128)>,
) -> [bool; 4] {
    if let (true, Some((pxm, pym))) = (sc.ok, pm) {
        if let Some(qs) = mem_quads_int(sc, pxm, pym) {
            let mut out = [false; 4];
            for (i, (a, b, c)) in qs.iter().enumerate() {
                out[i] = lemma_q_int(*a, *b, *c, sc.p0, sc.q0, sc.p1, sc.q1);
            }
            return out;
        }
    }
    let qs = mem_quads_rat(f, px, py);
    let mut out = [false; 4];
    for (i, (a, b, c)) in qs.iter().enumerate() {
        out[i] = lemma_q_rat(a, b, c, &f.t0, &f.t1);
    }
    out
}

// ---------------------------------------------------------------------------
// Lemma E — exact core exemption (spec §3.5)
// ---------------------------------------------------------------------------

/// An axis-aligned closed core square: centre (kx, ky), half-side a >= 0.
#[derive(Clone, Debug)]
pub struct Core {
    pub kx: Rat,
    pub ky: Rat,
    pub a: Rat,
}

/// The eight Lemma E quadratics in rational form, each pinned at its worst corner.
///
/// Order (sigma 0..7): E1+, E1-, E2+, E2-, E3+, E3-, E4+, E4-.
///   E1+/- (x-axis):    (a -/+ ex)(1+t^2) + (1 - t^2 + 2t)/2 >= 0, worst cx = x1 / x0
///   E2+/- (y-axis):    same in ey,                                worst cy = y1 / y0
///   E3+/- (body u):    (1/2)(1+t^2) + a(1-t^2+2t) -/+ [ex(1-t^2) + 2t ey] >= 0,
///                      worst (x1,y1) / (x0,y0)
///   E4+/- (body v):    (1/2)(1+t^2) + a(1-t^2+2t) -/+ [-2t ex + ey(1-t^2)] >= 0,
///                      worst (x0,y1) / (x1,y0)
pub fn exempt_quads_rat(f: &Factor, k: &Core) -> [(Rat, Rat, Rat); 8] {
    let h = Rat::half();
    let two = Rat::from_int(2);
    let four = Rat::from_int(4);
    let a = k.a.clone();

    let ex_at = |x: &Rat| -> Rat { x.sub(&k.kx) };
    let ey_at = |y: &Rat| -> Rat { y.sub(&k.ky) };

    // E1/E2 shape: A = K - 1/2, B = 1, C = K + 1/2.
    let axis = |kk: Rat| -> (Rat, Rat, Rat) { (kk.sub(&h), Rat::one(), kk.add(&h)) };

    let e1p = axis(a.sub(&ex_at(&f.x1)));
    let e1m = axis(a.add(&ex_at(&f.x0)));
    let e2p = axis(a.sub(&ey_at(&f.y1)));
    let e2m = axis(a.add(&ey_at(&f.y0)));

    // E3+ at (x1,y1): A = 1/2 - a + ex, B = 2a - 2ey, C = 1/2 + a - ex
    let (ex, ey) = (ex_at(&f.x1), ey_at(&f.y1));
    let e3p = (
        h.sub(&a).add(&ex),
        a.mul(&two).sub(&ey.mul(&two)),
        h.add(&a).sub(&ex),
    );
    // E3- at (x0,y0): A = 1/2 - a - ex, B = 2a + 2ey, C = 1/2 + a + ex
    let (ex, ey) = (ex_at(&f.x0), ey_at(&f.y0));
    let e3m = (
        h.sub(&a).sub(&ex),
        a.mul(&two).add(&ey.mul(&two)),
        h.add(&a).add(&ex),
    );
    // E4+ at (x0,y1): A = 1/2 - a + ey, B = 2a + 2ex, C = 1/2 + a - ey
    let (ex, ey) = (ex_at(&f.x0), ey_at(&f.y1));
    let e4p = (
        h.sub(&a).add(&ey),
        a.mul(&two).add(&ex.mul(&two)),
        h.add(&a).sub(&ey),
    );
    // E4- at (x1,y0): A = 1/2 - a - ey, B = 2a - 2ex, C = 1/2 + a + ey
    let (ex, ey) = (ex_at(&f.x1), ey_at(&f.y0));
    let e4m = (
        h.sub(&a).sub(&ey),
        a.mul(&two).sub(&ex.mul(&two)),
        h.add(&a).add(&ey),
    );
    let _ = four;
    [e1p, e1m, e2p, e2m, e3p, e3m, e4p, e4m]
}

/// Integer form of the eight Lemma E quadratics over the common denominator 2M.
#[inline]
pub fn exempt_quads_int(
    sc: &Scale,
    kxm: i128,
    kym: i128,
    am: i128,
) -> Option<[(i128, i128, i128); 8]> {
    let m = sc.m;
    let ex1 = sc.x1m.checked_sub(kxm)?;
    let ex0 = sc.x0m.checked_sub(kxm)?;
    let ey1 = sc.y1m.checked_sub(kym)?;
    let ey0 = sc.y0m.checked_sub(kym)?;
    let t2 = |v: i128| v.checked_mul(2);
    let t4 = |v: i128| v.checked_mul(4);
    // axis shape over 2M: K given as an integer over M -> a = 2K - M, b = 2M, c = 2K + M
    let axis = |kk: i128| -> Option<(i128, i128, i128)> {
        Some((
            t2(kk)?.checked_sub(m)?,
            t2(m)?,
            t2(kk)?.checked_add(m)?,
        ))
    };
    let e1p = axis(am.checked_sub(ex1)?)?;
    let e1m = axis(am.checked_add(ex0)?)?;
    let e2p = axis(am.checked_sub(ey1)?)?;
    let e2m = axis(am.checked_add(ey0)?)?;

    let e3p = (
        m.checked_sub(t2(am)?)?.checked_add(t2(ex1)?)?,
        t4(am)?.checked_sub(t4(ey1)?)?,
        m.checked_add(t2(am)?)?.checked_sub(t2(ex1)?)?,
    );
    let e3m = (
        m.checked_sub(t2(am)?)?.checked_sub(t2(ex0)?)?,
        t4(am)?.checked_add(t4(ey0)?)?,
        m.checked_add(t2(am)?)?.checked_add(t2(ex0)?)?,
    );
    let e4p = (
        m.checked_sub(t2(am)?)?.checked_add(t2(ey1)?)?,
        t4(am)?.checked_add(t4(ex0)?)?,
        m.checked_add(t2(am)?)?.checked_sub(t2(ey1)?)?,
    );
    let e4m = (
        m.checked_sub(t2(am)?)?.checked_sub(t2(ey0)?)?,
        t4(am)?.checked_sub(t4(ex1)?)?,
        m.checked_add(t2(am)?)?.checked_add(t2(ey0)?)?,
    );
    Some([e1p, e1m, e2p, e2m, e3p, e3m, e4p, e4m])
}

/// Per-constraint results of Lemma E.
pub fn exempt_flags(
    f: &Factor,
    sc: &Scale,
    k: &Core,
    km: Option<(i128, i128, i128)>,
) -> [bool; 8] {
    if let (true, Some((kxm, kym, am))) = (sc.ok, km) {
        if let Some(qs) = exempt_quads_int(sc, kxm, kym, am) {
            let mut out = [false; 8];
            for (i, (a, b, c)) in qs.iter().enumerate() {
                out[i] = lemma_q_int(*a, *b, *c, sc.p0, sc.q0, sc.p1, sc.q1);
            }
            return out;
        }
    }
    let qs = exempt_quads_rat(f, k);
    let mut out = [false; 8];
    for (i, (a, b, c)) in qs.iter().enumerate() {
        out[i] = lemma_q_rat(a, b, c, &f.t0, &f.t1);
    }
    out
}

/// **Lemma E**: does Q(c, theta(t)) meet the core K for EVERY (t, cx, cy) in the box?
pub fn certain_exempt(
    f: &Factor,
    sc: &Scale,
    k: &Core,
    km: Option<(i128, i128, i128)>,
) -> bool {
    if let (true, Some((kxm, kym, am))) = (sc.ok, km) {
        if let Some(qs) = exempt_quads_int(sc, kxm, kym, am) {
            return qs
                .iter()
                .all(|(a, b, c)| lemma_q_int(*a, *b, *c, sc.p0, sc.q0, sc.p1, sc.q1));
        }
    }
    exempt_quads_rat(f, k)
        .iter()
        .all(|(a, b, c)| lemma_q_rat(a, b, c, &f.t0, &f.t1))
}

// ---------------------------------------------------------------------------
// NONDISJOINT (v1 §3.3, kept verbatim per v2 §3.3 item 3 and §8)
// ---------------------------------------------------------------------------

/// Certified NONDISJOINT: every placement pair in (f, g) has intersecting interiors.
///
/// SAT converse: two closed convex polygons have overlapping interiors iff EVERY edge
/// normal fails to weakly separate. For two squares the four normals are the two squares'
/// own axes, and the half-width sum is the SAME on all four: 1/2 + g/2 with
/// g = |cos(th1-th2)| + |sin(th1-th2)| >= 1, enclosed via cc = C1C2 + S1S2 and
/// ss = S1C2 - C1S2 over the two t-ranges and floored at 1.
pub fn nondisjoint(f: &Factor, g: &Factor, ftg: &TGeom, gtg: &TGeom) -> bool {
    let dcx = Iv::new(g.x0.sub(&f.x1), g.x1.sub(&f.x0));
    let dcy = Iv::new(g.y0.sub(&f.y1), g.y1.sub(&f.y0));

    // Fast sufficient pre-test: sup||dc||^2 < 1 (the inscribed open disks of radius 1/2
    // already intersect, so the squares' interiors do).
    let sx = dcx.sup_abs();
    let sy = dcy.sup_abs();
    let d2 = sx.mul(&sx).add(&sy.mul(&sy));
    if d2.lt(&Rat::one()) {
        return true;
    }

    let c1 = ftg.c_iv();
    let s1 = ftg.s_iv();
    let c2 = gtg.c_iv();
    let s2 = gtg.s_iv();

    // C, S >= 0 on [0,1], so these products are monotone in each endpoint.
    let cc = Iv::new(
        c1.lo.mul(&c2.lo).add(&s1.lo.mul(&s2.lo)),
        c1.hi.mul(&c2.hi).add(&s1.hi.mul(&s2.hi)),
    );
    let ss = Iv::new(
        s1.lo.mul(&c2.lo).sub(&c1.hi.mul(&s2.hi)),
        s1.hi.mul(&c2.hi).sub(&c1.lo.mul(&s2.lo)),
    );

    // g >= 1 always; the floor is what makes the enclosure usable near theta1 = theta2.
    let g_lo = cc.inf_abs().add(&ss.inf_abs()).max_rat(&Rat::one());
    let half_sum_lo = Rat::half().add(&g_lo.mul(&Rat::half()));

    // The four normals: (C1,S1), (-S1,C1), (C2,S2), (-S2,C2).
    let dirs: [(Iv, Iv); 4] = [
        (c1.clone(), s1.clone()),
        (
            Iv::new(s1.hi.neg(), s1.lo.neg()),
            c1.clone(),
        ),
        (c2.clone(), s2.clone()),
        (
            Iv::new(s2.hi.neg(), s2.lo.neg()),
            c2.clone(),
        ),
    ];
    for (nx, ny) in dirs.iter() {
        let proj = dcx.mul(nx).add(&dcy.mul(ny));
        if !proj.sup_abs().lt(&half_sum_lo) {
            return false;
        }
    }
    true
}

// ---------------------------------------------------------------------------
// U bound (v1 §3 item 4, verbatim per v2 §3.7)
// ---------------------------------------------------------------------------

/// An axis-aligned closed box: centre (bx, by), half-side h.
#[derive(Clone, Debug)]
pub struct BoxSq {
    pub bx: Rat,
    pub by: Rat,
    pub h: Rat,
}

/// Does some placement of `f` possibly meet the box's interior?
///
/// The negation of CERTAIN interior separation. Certainly separated iff, on some
/// coordinate axis, inf|c - b| >= h + w_hi/2, or on some body axis of Q,
/// inf|(c-b).u| >= 1/2 + h*w_hi. Using w_hi (an UPPER bound) makes more boxes possible,
/// U larger and PASS harder: conservative.
pub fn possibly_meets(f: &Factor, tg: &TGeom, b: &BoxSq) -> bool {
    let wh = tg.whi.clone();
    let dx = Iv::new(f.x0.sub(&b.bx), f.x1.sub(&b.bx));
    let dy = Iv::new(f.y0.sub(&b.by), f.y1.sub(&b.by));

    let axis_bound = b.h.add(&wh.mul(&Rat::half()));
    if dx.inf_abs().ge(&axis_bound) {
        return false;
    }
    if dy.inf_abs().ge(&axis_bound) {
        return false;
    }

    let body_bound = Rat::half().add(&b.h.mul(&wh));
    let c = tg.c_iv();
    let s = tg.s_iv();
    // u = (C, S)
    let pu = dx.mul(&c).add(&dy.mul(&s));
    if pu.inf_abs().ge(&body_bound) {
        return false;
    }
    // v = (-S, C)
    let pv = dx.mul(&Iv::new(s.hi.neg(), s.lo.neg())).add(&dy.mul(&c));
    if pv.inf_abs().ge(&body_bound) {
        return false;
    }
    true
}

/// U = #{ i : F possibly-meets B_i AND F' possibly-meets B_i }. An upper bound for m2.
pub fn u_bound(f: &Factor, g: &Factor, ftg: &TGeom, gtg: &TGeom, boxes: &[BoxSq]) -> u64 {
    let mut u = 0u64;
    for b in boxes {
        if possibly_meets(f, ftg, b) && possibly_meets(g, gtg, b) {
            u += 1;
        }
    }
    u
}

// ---------------------------------------------------------------------------
// Exact predicates at a single rational placement (DEFICIENT-EARLY, §3.8)
// ---------------------------------------------------------------------------

/// A concrete placement: angle parameter t and centre (cx, cy).
#[derive(Clone, Debug)]
pub struct Place {
    pub t: Rat,
    pub cx: Rat,
    pub cy: Rat,
}

impl Place {
    pub fn c(&self) -> Rat {
        c_at(&self.t)
    }
    pub fn s(&self) -> Rat {
        s_at(&self.t)
    }
    pub fn w(&self) -> Rat {
        w_at(&self.t)
    }
}

/// Is `p` inside the closed square Q(c, theta(t))? Exact: |u| <= 1/2 and |v| <= 1/2 with
/// the PINNED body frame u = C dx + S dy, v = -S dx + C dy, d = p - c.
pub fn point_in_square(px: &Rat, py: &Rat, pl: &Place) -> bool {
    let dx = px.sub(&pl.cx);
    let dy = py.sub(&pl.cy);
    let (c, s) = (pl.c(), pl.s());
    let u = c.mul(&dx).add(&s.mul(&dy));
    let v = s.neg().mul(&dx).add(&c.mul(&dy));
    let h = Rat::half();
    u.abs().le(&h) && v.abs().le(&h)
}

/// Is the square contained in [0,s]^2? Its axis-aligned half-width is w(t)/2.
pub fn square_in_container(pl: &Place, s: &Rat) -> bool {
    let hw = pl.w().mul(&Rat::half());
    pl.cx.sub(&hw).is_nonneg()
        && pl.cx.add(&hw).le(s)
        && pl.cy.sub(&hw).is_nonneg()
        && pl.cy.add(&hw).le(s)
}

/// Does the square meet the closed core K? (Closed intersection non-empty.)
/// True iff NO axis strictly separates.
pub fn square_meets_core(pl: &Place, k: &Core) -> bool {
    let ex = pl.cx.sub(&k.kx);
    let ey = pl.cy.sub(&k.ky);
    let (c, s) = (pl.c(), pl.s());
    let w = pl.w();
    let axis_b = k.a.add(&w.mul(&Rat::half()));
    if ex.abs().gt(&axis_b) || ey.abs().gt(&axis_b) {
        return false;
    }
    let body_b = Rat::half().add(&k.a.mul(&w));
    let u = c.mul(&ex).add(&s.mul(&ey));
    let v = s.neg().mul(&ex).add(&c.mul(&ey));
    if u.abs().gt(&body_b) || v.abs().gt(&body_b) {
        return false;
    }
    true
}

/// Do the two squares' INTERIORS meet the box's interior? (Used for m2.)
/// Interiors overlap iff every one of the four normals fails to weakly separate.
pub fn box_int_meets_square(b: &BoxSq, pl: &Place) -> bool {
    let dx = pl.cx.sub(&b.bx);
    let dy = pl.cy.sub(&b.by);
    let (c, s) = (pl.c(), pl.s());
    let w = pl.w();
    let axis_b = b.h.add(&w.mul(&Rat::half()));
    if dx.abs().ge(&axis_b) || dy.abs().ge(&axis_b) {
        return false;
    }
    let body_b = Rat::half().add(&b.h.mul(&w));
    let u = c.mul(&dx).add(&s.mul(&dy));
    let v = s.neg().mul(&dx).add(&c.mul(&dy));
    if u.abs().ge(&body_b) || v.abs().ge(&body_b) {
        return false;
    }
    true
}

/// The exact SAT gap between two placements: max over the four normals of
/// (|dc.n| - half-width sum). Interiors are disjoint iff this is >= 0.
pub fn sat_gap(p1: &Place, p2: &Place) -> Rat {
    let dcx = p2.cx.sub(&p1.cx);
    let dcy = p2.cy.sub(&p1.cy);
    let (c1, s1) = (p1.c(), p1.s());
    let (c2, s2) = (p2.c(), p2.s());
    let cc = c1.mul(&c2).add(&s1.mul(&s2));
    let ss = s1.mul(&c2).sub(&c1.mul(&s2));
    let g = cc.abs().add(&ss.abs());
    let half_sum = Rat::half().add(&g.mul(&Rat::half()));
    let dirs = [
        (c1.clone(), s1.clone()),
        (s1.neg(), c1.clone()),
        (c2.clone(), s2.clone()),
        (s2.neg(), c2.clone()),
    ];
    let mut best: Option<Rat> = None;
    for (nx, ny) in dirs.iter() {
        let proj = dcx.mul(nx).add(&dcy.mul(ny));
        let gap = proj.abs().sub(&half_sum);
        best = Some(match best {
            None => gap,
            Some(b) => b.max_rat(&gap),
        });
    }
    best.unwrap()
}

/// Interiors disjoint iff some normal weakly separates, i.e. sat_gap >= 0.
pub fn interiors_disjoint(p1: &Place, p2: &Place) -> bool {
    sat_gap(p1, p2).is_nonneg()
}

/// Minimum over [t0,t1] of a rational quadratic (re-exported for COVERED-F).
pub fn quad_min(a: &Rat, b: &Rat, c: &Rat, t0: &Rat, t1: &Rat) -> Rat {
    quad_min_on(a, b, c, t0, t1)
}
