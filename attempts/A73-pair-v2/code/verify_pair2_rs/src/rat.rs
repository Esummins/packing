//! Exact rational arithmetic: i128 fast path with overflow-CHECKED promotion to BigInt.
//!
//! Spec pair-certificate-v2 §3.0: "Implementations MAY use machine integers (e.g. i128)
//! with OVERFLOW-CHECKED promotion to arbitrary precision; silent wraparound is unsound."
//!
//! Every arithmetic operation here uses `checked_*`; on `None` the operands are promoted
//! to `BigInt` and the operation redone exactly. There is no unchecked multiply or add on
//! any decision path.

use num_bigint::BigInt;
use num_integer::Integer as _;
use num_traits::{One, Signed, ToPrimitive, Zero};
use std::cmp::Ordering;
use std::fmt;

/// Binary GCD on u64: shifts and subtractions only.
///
/// This matters a great deal here. On x86-64 there is no native 128-bit division, so
/// `%` on i128 lowers to a `__umodti3` libcall costing hundreds of cycles; the rational
/// hot path performs one gcd per multiply. Almost every value in a pair-box computation
/// fits in 64 bits, so the u64 binary algorithm carries essentially all of the traffic.
#[inline]
fn gcd_u64(mut a: u64, mut b: u64) -> u64 {
    debug_assert!(a != 0 && b != 0);
    let shift = (a | b).trailing_zeros();
    a >>= a.trailing_zeros();
    loop {
        b >>= b.trailing_zeros();
        if a > b {
            core::mem::swap(&mut a, &mut b);
        }
        b -= a;
        if b == 0 {
            break;
        }
    }
    a << shift
}

#[inline]
pub fn gcd_i128(a: i128, b: i128) -> i128 {
    let (mut x, mut y) = (a.unsigned_abs(), b.unsigned_abs());
    if x == 0 {
        return y as i128;
    }
    if y == 0 {
        return x as i128;
    }
    if x <= u64::MAX as u128 && y <= u64::MAX as u128 {
        return gcd_u64(x as u64, y as u64) as i128;
    }
    while y != 0 {
        let t = x % y;
        x = y;
        y = t;
    }
    x as i128
}

/// Exact rational. Invariants: denominator > 0, gcd(|num|, den) == 1.
#[derive(Clone, Debug)]
pub enum Rat {
    /// Small: (numerator, denominator), den > 0, reduced.
    S(i128, i128),
    /// Big: (numerator, denominator), den > 0, reduced.
    B(BigInt, BigInt),
}

impl Rat {
    pub fn zero() -> Rat {
        Rat::S(0, 1)
    }
    pub fn one() -> Rat {
        Rat::S(1, 1)
    }
    pub fn half() -> Rat {
        Rat::S(1, 2)
    }
    pub fn from_int(n: i128) -> Rat {
        Rat::S(n, 1)
    }

    /// Construct from i128 parts, normalising. Returns None if den == 0.
    pub fn new(n: i128, d: i128) -> Option<Rat> {
        if d == 0 {
            return None;
        }
        // Guard the one value whose negation overflows.
        if n == i128::MIN || d == i128::MIN {
            return Some(Rat::big_new(BigInt::from(n), BigInt::from(d)));
        }
        // Fast exits that skip the gcd entirely — by far the common cases in the
        // interval arithmetic of NONDISJOINT and the U bound.
        if n == 0 {
            return Some(Rat::S(0, 1));
        }
        if d == 1 {
            return Some(Rat::S(n, 1));
        }
        if d == -1 {
            return Some(Rat::S(-n, 1));
        }
        let (mut n, mut d) = (n, d);
        if d < 0 {
            n = -n;
            d = -d;
        }
        // Reduce in 64-bit arithmetic when possible: on x86-64 a 128-bit divide is a
        // libcall, so staying in i64 here is worth an explicit branch.
        const LIM: i128 = i64::MAX as i128;
        if n.abs() <= LIM && d <= LIM {
            let g = gcd_u64((n.unsigned_abs() as u64).max(1), d as u64) as i128;
            if g > 1 {
                let (n64, d64) = ((n as i64) / (g as i64), (d as i64) / (g as i64));
                return Some(Rat::S(n64 as i128, d64 as i128));
            }
            return Some(Rat::S(n, d));
        }
        let g = gcd_i128(n, d);
        if g > 1 {
            n /= g;
            d /= g;
        }
        Some(Rat::S(n, d))
    }

    fn big_new(n: BigInt, d: BigInt) -> Rat {
        debug_assert!(!d.is_zero());
        let (mut n, mut d) = (n, d);
        if d.is_negative() {
            n = -n;
            d = -d;
        }
        let g = n.gcd(&d);
        if !g.is_one() {
            n /= &g;
            d /= &g;
        }
        Rat::demote(n, d)
    }

    /// Collapse a big value back into the i128 representation when it fits.
    fn demote(n: BigInt, d: BigInt) -> Rat {
        match (n.to_i128(), d.to_i128()) {
            (Some(a), Some(b)) if a != i128::MIN && b != i128::MIN => Rat::S(a, b),
            _ => Rat::B(n, d),
        }
    }

    pub fn num_big(&self) -> BigInt {
        match self {
            Rat::S(n, _) => BigInt::from(*n),
            Rat::B(n, _) => n.clone(),
        }
    }
    pub fn den_big(&self) -> BigInt {
        match self {
            Rat::S(_, d) => BigInt::from(*d),
            Rat::B(_, d) => d.clone(),
        }
    }
    /// (num, den) as i128 when the value is in the fast representation.
    pub fn small(&self) -> Option<(i128, i128)> {
        match self {
            Rat::S(n, d) => Some((*n, *d)),
            Rat::B(_, _) => None,
        }
    }
    pub fn is_small(&self) -> bool {
        matches!(self, Rat::S(_, _))
    }

    pub fn sign(&self) -> i32 {
        match self {
            Rat::S(n, _) => {
                if *n > 0 {
                    1
                } else if *n < 0 {
                    -1
                } else {
                    0
                }
            }
            Rat::B(n, _) => {
                if n.is_positive() {
                    1
                } else if n.is_negative() {
                    -1
                } else {
                    0
                }
            }
        }
    }
    pub fn is_zero(&self) -> bool {
        self.sign() == 0
    }
    pub fn is_neg(&self) -> bool {
        self.sign() < 0
    }
    pub fn is_pos(&self) -> bool {
        self.sign() > 0
    }
    pub fn is_nonneg(&self) -> bool {
        self.sign() >= 0
    }

    pub fn neg(&self) -> Rat {
        match self {
            Rat::S(n, d) => {
                if *n == i128::MIN {
                    Rat::B(-BigInt::from(*n), BigInt::from(*d))
                } else {
                    Rat::S(-n, *d)
                }
            }
            Rat::B(n, d) => Rat::demote(-n.clone(), d.clone()),
        }
    }

    pub fn abs(&self) -> Rat {
        if self.is_neg() {
            self.neg()
        } else {
            self.clone()
        }
    }

    fn add_small(n1: i128, d1: i128, n2: i128, d2: i128) -> Option<Rat> {
        // Shared denominator: no cross-multiply, no gcd of denominators.
        if d1 == d2 {
            return Rat::new(n1.checked_add(n2)?, d1);
        }
        // Direct form first: this costs ONE gcd (inside Rat::new) rather than two.
        if let (Some(a), Some(b), Some(den)) =
            (n1.checked_mul(d2), n2.checked_mul(d1), d1.checked_mul(d2))
        {
            if let Some(num) = a.checked_add(b) {
                return Rat::new(num, den);
            }
        }
        // Overflowed: reduce the denominators first to keep intermediates small.
        let g = gcd_i128(d1, d2);
        let d1g = d1 / g;
        let d2g = d2 / g;
        let a = n1.checked_mul(d2g)?;
        let b = n2.checked_mul(d1g)?;
        let num = a.checked_add(b)?;
        let den = d1.checked_mul(d2g)?;
        Rat::new(num, den)
    }

    pub fn add(&self, o: &Rat) -> Rat {
        if let (Rat::S(n1, d1), Rat::S(n2, d2)) = (self, o) {
            if let Some(r) = Rat::add_small(*n1, *d1, *n2, *d2) {
                return r;
            }
        }
        let (n1, d1) = (self.num_big(), self.den_big());
        let (n2, d2) = (o.num_big(), o.den_big());
        Rat::big_new(&n1 * &d2 + &n2 * &d1, &d1 * &d2)
    }

    pub fn sub(&self, o: &Rat) -> Rat {
        self.add(&o.neg())
    }

    pub fn mul(&self, o: &Rat) -> Rat {
        if let (Rat::S(n1, d1), Rat::S(n2, d2)) = (self, o) {
            if *n1 == 0 || *n2 == 0 {
                return Rat::S(0, 1);
            }
            // Direct product first: ONE gcd (inside Rat::new) instead of the three that
            // cross-reduction costs. Cross-reduction is kept as the overflow fallback.
            if let (Some(a), Some(b)) = (n1.checked_mul(*n2), d1.checked_mul(*d2)) {
                if let Some(r) = Rat::new(a, b) {
                    return r;
                }
            }
            let res = (|| -> Option<Rat> {
                let g1 = gcd_i128(*n1, *d2);
                let g2 = gcd_i128(*n2, *d1);
                if g1 == 0 || g2 == 0 {
                    return Rat::new(0, 1);
                }
                let a = (n1 / g1).checked_mul(n2 / g2)?;
                let b = (d1 / g2).checked_mul(d2 / g1)?;
                Rat::new(a, b)
            })();
            if let Some(r) = res {
                return r;
            }
        }
        let (n1, d1) = (self.num_big(), self.den_big());
        let (n2, d2) = (o.num_big(), o.den_big());
        Rat::big_new(&n1 * &n2, &d1 * &d2)
    }

    /// Exact division. Returns None when `o` is zero.
    pub fn div(&self, o: &Rat) -> Option<Rat> {
        if o.is_zero() {
            return None;
        }
        let inv = match o {
            Rat::S(n, d) => Rat::new(*d, *n)?,
            Rat::B(n, d) => Rat::big_new(d.clone(), n.clone()),
        };
        Some(self.mul(&inv))
    }

    pub fn cmp_rat(&self, o: &Rat) -> Ordering {
        // Fast path: compare n1*d2 vs n2*d1 (denominators positive).
        if let (Rat::S(n1, d1), Rat::S(n2, d2)) = (self, o) {
            if let (Some(a), Some(b)) = (n1.checked_mul(*d2), n2.checked_mul(*d1)) {
                return a.cmp(&b);
            }
        }
        let (n1, d1) = (self.num_big(), self.den_big());
        let (n2, d2) = (o.num_big(), o.den_big());
        (&n1 * &d2).cmp(&(&n2 * &d1))
    }

    pub fn lt(&self, o: &Rat) -> bool {
        self.cmp_rat(o) == Ordering::Less
    }
    pub fn le(&self, o: &Rat) -> bool {
        self.cmp_rat(o) != Ordering::Greater
    }
    pub fn gt(&self, o: &Rat) -> bool {
        self.cmp_rat(o) == Ordering::Greater
    }
    pub fn ge(&self, o: &Rat) -> bool {
        self.cmp_rat(o) != Ordering::Less
    }
    pub fn eq_rat(&self, o: &Rat) -> bool {
        self.cmp_rat(o) == Ordering::Equal
    }

    pub fn min_rat(&self, o: &Rat) -> Rat {
        if self.le(o) {
            self.clone()
        } else {
            o.clone()
        }
    }
    pub fn max_rat(&self, o: &Rat) -> Rat {
        if self.ge(o) {
            self.clone()
        } else {
            o.clone()
        }
    }

    /// Midpoint (self + o) / 2.
    pub fn mid(&self, o: &Rat) -> Rat {
        self.add(o).mul(&Rat::S(1, 2))
    }

    /// Float image. NEVER used on a decision path — reporting and shortlisting only.
    pub fn to_f64(&self) -> f64 {
        match self {
            Rat::S(n, d) => (*n as f64) / (*d as f64),
            Rat::B(n, d) => {
                let nf = n.to_f64().unwrap_or(f64::NAN);
                let df = d.to_f64().unwrap_or(f64::NAN);
                nf / df
            }
        }
    }

    /// Parse an exact rational from `"p/q"` or `"p"`. Rejects anything float-shaped.
    pub fn parse(s: &str) -> Result<Rat, String> {
        let t = s.trim();
        if t.is_empty() {
            return Err("empty rational string".into());
        }
        if t.contains('.') || t.contains('e') || t.contains('E') {
            return Err(format!("float-shaped rational literal: {:?}", s));
        }
        let (ns, ds) = match t.split_once('/') {
            Some((a, b)) => (a, b),
            None => (t, "1"),
        };
        let nb: BigInt = ns
            .trim()
            .parse()
            .map_err(|_| format!("bad numerator in {:?}", s))?;
        let db: BigInt = ds
            .trim()
            .parse()
            .map_err(|_| format!("bad denominator in {:?}", s))?;
        if db.is_zero() {
            return Err(format!("zero denominator in {:?}", s));
        }
        Ok(Rat::big_new(nb, db))
    }
}

impl fmt::Display for Rat {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Rat::S(n, d) => {
                if *d == 1 {
                    write!(f, "{}", n)
                } else {
                    write!(f, "{}/{}", n, d)
                }
            }
            Rat::B(n, d) => {
                if d.is_one() {
                    write!(f, "{}", n)
                } else {
                    write!(f, "{}/{}", n, d)
                }
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Integer sign tests (the hot path).
//
// Every predicate in §3.4/§3.5 reduces to the sign of an integer expression once
// the quadratic's coefficients are expressed over a common POSITIVE denominator and
// the interval endpoint is written t = p/q with q > 0. These helpers do that in i128
// with checked arithmetic, falling back to BigInt on overflow.
// ---------------------------------------------------------------------------

#[inline]
fn sgn_i128(v: i128) -> i32 {
    if v > 0 {
        1
    } else if v < 0 {
        -1
    } else {
        0
    }
}

/// sign of `a*p^2 + b*p*q + c*q^2`, i.e. of q(t) at t = p/q scaled by q^2 > 0.
#[inline]
pub fn sgn_quad_at(a: i128, b: i128, c: i128, p: i128, q: i128) -> i32 {
    let fast = (|| -> Option<i128> {
        let p2 = p.checked_mul(p)?;
        let pq = p.checked_mul(q)?;
        let q2 = q.checked_mul(q)?;
        let t1 = a.checked_mul(p2)?;
        let t2 = b.checked_mul(pq)?;
        let t3 = c.checked_mul(q2)?;
        t1.checked_add(t2)?.checked_add(t3)
    })();
    match fast {
        Some(v) => sgn_i128(v),
        None => {
            let (ab, bb, cb) = (BigInt::from(a), BigInt::from(b), BigInt::from(c));
            let (pb, qb) = (BigInt::from(p), BigInt::from(q));
            let v = &ab * &pb * &pb + &bb * &pb * &qb + &cb * &qb * &qb;
            if v.is_positive() {
                1
            } else if v.is_negative() {
                -1
            } else {
                0
            }
        }
    }
}

/// sign of `2*a*p + b*q` — the derivative test `2*A*t + B` at t = p/q, scaled by q > 0.
#[inline]
pub fn sgn_deriv_at(a: i128, b: i128, p: i128, q: i128) -> i32 {
    let fast = (|| -> Option<i128> {
        let x = a.checked_mul(2)?.checked_mul(p)?;
        let y = b.checked_mul(q)?;
        x.checked_add(y)
    })();
    match fast {
        Some(v) => sgn_i128(v),
        None => {
            let v: BigInt = BigInt::from(a) * BigInt::from(2) * BigInt::from(p)
                + BigInt::from(b) * BigInt::from(q);
            if v.is_positive() {
                1
            } else if v.is_negative() {
                -1
            } else {
                0
            }
        }
    }
}

/// sign of the discriminant expression `4*a*c - b^2`.
#[inline]
pub fn sgn_disc(a: i128, b: i128, c: i128) -> i32 {
    let fast = (|| -> Option<i128> {
        let ac = a.checked_mul(c)?.checked_mul(4)?;
        let b2 = b.checked_mul(b)?;
        ac.checked_sub(b2)
    })();
    match fast {
        Some(v) => sgn_i128(v),
        None => {
            let v: BigInt = BigInt::from(a) * BigInt::from(4) * BigInt::from(c)
                - BigInt::from(b) * BigInt::from(b);
            if v.is_positive() {
                1
            } else if v.is_negative() {
                -1
            } else {
                0
            }
        }
    }
}

/// **Lemma Q** (spec §3.4), exact, integer form.
///
/// For rationals A, B, C given as integers `a, b, c` over a common POSITIVE denominator,
/// and `0 <= t0 <= t1` given as `p0/q0`, `p1/q1` with `q0, q1 > 0`:
///
/// `q(t) = A t^2 + B t + C >= 0` for all `t` in `[t0, t1]` **iff**
/// `q(t0) >= 0 && q(t1) >= 0 && (A <= 0 || 2*A*t0 + B >= 0 || 2*A*t1 + B <= 0 || 4AC - B^2 >= 0)`.
#[inline]
pub fn lemma_q_int(a: i128, b: i128, c: i128, p0: i128, q0: i128, p1: i128, q1: i128) -> bool {
    debug_assert!(q0 > 0 && q1 > 0);
    if sgn_quad_at(a, b, c, p0, q0) < 0 {
        return false;
    }
    if sgn_quad_at(a, b, c, p1, q1) < 0 {
        return false;
    }
    if a <= 0 {
        return true;
    }
    if sgn_deriv_at(a, b, p0, q0) >= 0 {
        return true;
    }
    if sgn_deriv_at(a, b, p1, q1) <= 0 {
        return true;
    }
    sgn_disc(a, b, c) >= 0
}

/// BigInt form of Lemma Q, used when coefficients or endpoints leave the i128 range.
pub fn lemma_q_big(a: &BigInt, b: &BigInt, c: &BigInt, t0: &Rat, t1: &Rat) -> bool {
    let ev = |t: &Rat| -> BigInt {
        let (p, q) = (t.num_big(), t.den_big());
        a * &p * &p + b * &p * &q + c * &q * &q
    };
    if ev(t0).is_negative() || ev(t1).is_negative() {
        return false;
    }
    if !a.is_positive() {
        return true;
    }
    let d0: BigInt = a * BigInt::from(2) * t0.num_big() + b * t0.den_big();
    if !d0.is_negative() {
        return true;
    }
    let d1: BigInt = a * BigInt::from(2) * t1.num_big() + b * t1.den_big();
    if !d1.is_positive() {
        return true;
    }
    !(a * BigInt::from(4) * c - b * b).is_negative()
}

/// lcm with overflow check.
#[inline]
fn lcm_ck(a: i128, b: i128) -> Option<i128> {
    let g = gcd_i128(a, b);
    if g == 0 {
        return None;
    }
    (a / g).checked_mul(b)
}

/// Lemma Q on rational coefficients: put A, B, C over a common positive denominator and
/// dispatch to the integer routine (single implementation, no duplicated logic).
pub fn lemma_q_rat(a: &Rat, b: &Rat, c: &Rat, t0: &Rat, t1: &Rat) -> bool {
    // i128 fast path. COVERED-F calls this many times per node, and going through BigInt
    // here would allocate roughly ten heap values per call.
    if let (Some((an, ad)), Some((bn, bd)), Some((cn, cd)), Some((p0, q0)), Some((p1, q1))) = (
        a.small(),
        b.small(),
        c.small(),
        t0.small(),
        t1.small(),
    ) {
        if let Some(d) = lcm_ck(ad, bd).and_then(|x| lcm_ck(x, cd)) {
            if let (Some(ai), Some(bi), Some(ci)) = (
                an.checked_mul(d / ad),
                bn.checked_mul(d / bd),
                cn.checked_mul(d / cd),
            ) {
                return lemma_q_int(ai, bi, ci, p0, q0, p1, q1);
            }
        }
    }
    // Common denominator D = lcm(den a, den b, den c) > 0; scale each numerator by D.
    let da = a.den_big();
    let db = b.den_big();
    let dc = c.den_big();
    let l1 = da.lcm(&db);
    let d = l1.lcm(&dc);
    let ai = a.num_big() * (&d / a.den_big());
    let bi = b.num_big() * (&d / b.den_big());
    let ci = c.num_big() * (&d / c.den_big());
    if let (Some(x), Some(y), Some(z), Some((p0, q0)), Some((p1, q1))) = (
        ai.to_i128(),
        bi.to_i128(),
        ci.to_i128(),
        t0.small(),
        t1.small(),
    ) {
        return lemma_q_int(x, y, z, p0, q0, p1, q1);
    }
    lemma_q_big(&ai, &bi, &ci, t0, t1)
}

/// Exact minimum of `q(t) = A t^2 + B t + C` over `[t0, t1]` (rational coefficients).
///
/// Used by COVERED-F check 2, which needs the minimum VALUE rather than just its sign.
pub fn quad_min_on(a: &Rat, b: &Rat, c: &Rat, t0: &Rat, t1: &Rat) -> Rat {
    let at = |t: &Rat| -> Rat { a.mul(t).mul(t).add(&b.mul(t)).add(c) };
    let v0 = at(t0);
    let v1 = at(t1);
    let mut best = v0.min_rat(&v1);
    if a.is_pos() {
        // Vertex t* = -B / (2A); interior minimum value is (4AC - B^2) / (4A).
        let two_a = a.mul(&Rat::from_int(2));
        if let Some(tstar) = b.neg().div(&two_a) {
            if tstar.gt(t0) && tstar.lt(t1) {
                let four_ac = a.mul(c).mul(&Rat::from_int(4));
                let b2 = b.mul(b);
                let num = four_ac.sub(&b2);
                let den = a.mul(&Rat::from_int(4));
                if let Some(v) = num.div(&den) {
                    best = best.min_rat(&v);
                }
            }
        }
    }
    best
}
