//! `--selftest` (spec §5): MANDATORY once per build before any citable run.
//!
//! 1. >= 2000 random draws per predicate (Lemma M, Lemma E, NONDISJOINT) cross-checked
//!    against direct float SAT/membership sampling over the box.
//! 2. Lemma Q fuzz vs dense sampling.
//! 3. Toy corpus verdicts.
//! 4. Corruption gates.
//!
//! FLOATS ARE PERMITTED IN THIS FILE ONLY. It is the cross-check harness; nothing here
//! runs on a verdict path.

use crate::bb;
use crate::cert;
use crate::geom::*;
use crate::rat::{gcd_i128, lemma_q_rat, Rat};

/// lcm over i128 (saturating: a huge value simply forces the rational path).
fn lcm_i(a: i128, b: i128) -> i128 {
    let g = gcd_i128(a, b);
    if g == 0 { return a.max(b); }
    (a / g).saturating_mul(b)
}
fn den_of(r: &Rat) -> i128 {
    r.small().map(|(_, d)| d).unwrap_or(1)
}
/// Scale an exact rational to the node's integer frame. Requires den(r) | dg | m,
/// which is exactly how `cert::load` and `scale_for` establish `dg` in production.
fn scale_coord(r: &Rat, dg: i128, mul: i128) -> Option<i128> {
    let (n, d) = r.small()?;
    debug_assert_eq!(dg % d, 0, "dg must be a multiple of every coordinate denominator");
    n.checked_mul(dg / d)?.checked_mul(mul)
}
use serde_json::json;

const DRAWS: usize = 2500;
const SAMPLES: usize = 16;
const TOL: f64 = 1e-9;

// ---------------------------------------------------------------------------
// A small deterministic PRNG (xorshift64*), so selftest runs are reproducible.
// ---------------------------------------------------------------------------
struct Rng(u64);
impl Rng {
    fn new(seed: u64) -> Rng {
        Rng(seed | 1)
    }
    fn next_u64(&mut self) -> u64 {
        let mut x = self.0;
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        self.0 = x;
        x.wrapping_mul(0x2545_F491_4F6C_DD1D)
    }
    fn below(&mut self, n: u64) -> u64 {
        if n == 0 {
            0
        } else {
            self.next_u64() % n
        }
    }
    fn f01(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 / (1u64 << 53) as f64
    }
    /// A rational in [0,1] with a modest denominator.
    fn rat01(&mut self) -> Rat {
        let d = 1 + self.below(64) as i128;
        let n = self.below(d as u64 + 1) as i128;
        Rat::new(n, d).unwrap()
    }
    /// A rational in [lo, hi] with a modest denominator.
    fn rat_in(&mut self, lo: f64, hi: f64) -> Rat {
        let d = 1 + self.below(240) as i128;
        let span = hi - lo;
        let n = (lo * d as f64 + self.f01() * span * d as f64).round() as i128;
        Rat::new(n, d).unwrap()
    }
}

// ---------------------------------------------------------------------------
// Float reference geometry (the independent check)
// ---------------------------------------------------------------------------

fn cs_f(t: f64) -> (f64, f64) {
    let d = 1.0 + t * t;
    ((1.0 - t * t) / d, 2.0 * t / d)
}

fn in_square_f(px: f64, py: f64, t: f64, cx: f64, cy: f64) -> f64 {
    // Returns the minimum slack; negative means outside.
    let (c, s) = cs_f(t);
    let (dx, dy) = (px - cx, py - cy);
    let u = c * dx + s * dy;
    let v = -s * dx + c * dy;
    (0.5 - u.abs()).min(0.5 - v.abs())
}

fn meets_core_f(t: f64, cx: f64, cy: f64, kx: f64, ky: f64, a: f64) -> f64 {
    // Returns the minimum overlap slack across the 4 SAT axes; negative means separated.
    let (c, s) = cs_f(t);
    let w = c + s;
    let (ex, ey) = (cx - kx, cy - ky);
    let m1 = a + w / 2.0 - ex.abs();
    let m2 = a + w / 2.0 - ey.abs();
    let u = c * ex + s * ey;
    let v = -s * ex + c * ey;
    let m3 = 0.5 + a * w - u.abs();
    let m4 = 0.5 + a * w - v.abs();
    m1.min(m2).min(m3).min(m4)
}

fn sat_gap_f(t1: f64, x1: f64, y1: f64, t2: f64, x2: f64, y2: f64) -> f64 {
    let (c1, s1) = cs_f(t1);
    let (c2, s2) = cs_f(t2);
    let cc = c1 * c2 + s1 * s2;
    let ss = s1 * c2 - c1 * s2;
    let g = cc.abs() + ss.abs();
    let half = 0.5 + g / 2.0;
    let (dx, dy) = (x2 - x1, y2 - y1);
    let dirs = [(c1, s1), (-s1, c1), (c2, s2), (-s2, c2)];
    let mut best = f64::NEG_INFINITY;
    for (nx, ny) in dirs.iter() {
        let p = (dx * nx + dy * ny).abs() - half;
        if p > best {
            best = p;
        }
    }
    best
}

fn rand_factor(r: &mut Rng, small: bool) -> Factor {
    let t0 = r.rat01();
    let dt = if small {
        Rat::new(1, 4 + r.below(200) as i128).unwrap()
    } else {
        Rat::new(1, 1 + r.below(12) as i128).unwrap()
    };
    let t1 = t0.add(&dt).min_rat(&Rat::one());
    let (t0, t1) = if t0.le(&t1) {
        (t0, t1)
    } else {
        (t1.clone(), t1)
    };
    let x0 = r.rat_in(0.5, 3.5);
    let y0 = r.rat_in(0.5, 3.5);
    let dx = if small {
        Rat::new(1, 4 + r.below(200) as i128).unwrap()
    } else {
        Rat::new(1, 1 + r.below(12) as i128).unwrap()
    };
    let dy = if small {
        Rat::new(1, 4 + r.below(200) as i128).unwrap()
    } else {
        Rat::new(1, 1 + r.below(12) as i128).unwrap()
    };
    Factor {
        x1: x0.add(&dx),
        y1: y0.add(&dy),
        t0,
        t1,
        x0,
        y0,
    }
}

fn sample_in(f: &Factor, r: &mut Rng) -> (f64, f64, f64) {
    let (t0, t1) = (f.t0.to_f64(), f.t1.to_f64());
    let (x0, x1) = (f.x0.to_f64(), f.x1.to_f64());
    let (y0, y1) = (f.y0.to_f64(), f.y1.to_f64());
    let pick = |lo: f64, hi: f64, r: &mut Rng| -> f64 {
        match r.below(4) {
            0 => lo,
            1 => hi,
            2 => 0.5 * (lo + hi),
            _ => lo + r.f01() * (hi - lo),
        }
    };
    (
        pick(t0, t1, r),
        pick(x0, x1, r),
        pick(y0, y1, r),
    )
}

struct Stats {
    draws: usize,
    fired: usize,
    violations: usize,
    incomplete: usize,
}

impl Stats {
    fn new() -> Stats {
        Stats {
            draws: 0,
            fired: 0,
            violations: 0,
            incomplete: 0,
        }
    }
    fn json(&self) -> serde_json::Value {
        json!({
            "draws": self.draws,
            "predicate_fired": self.fired,
            "soundness_violations": self.violations,
            "completeness_misses": self.incomplete,
        })
    }
}

// ---------------------------------------------------------------------------
// 1a. Lemma M
// ---------------------------------------------------------------------------

fn fuzz_lemma_m(r: &mut Rng) -> Result<(Stats, usize), String> {
    let mut st = Stats::new();
    let mut path_disagreements = 0usize;
    for _ in 0..DRAWS {
        let sm = r.below(2) == 0;
        let f = rand_factor(r, sm);
        let cx = f.x0.to_f64();
        let cy = f.y0.to_f64();
        let px = Rat::new((cx * 64.0).round() as i128 + r.below(90) as i128 - 45, 64).unwrap();
        let py = Rat::new((cy * 64.0).round() as i128 + r.below(90) as i128 - 45, 64).unwrap();
        st.draws += 1;

        let dg = lcm_i(den_of(&px), den_of(&py));
        let sc = scale_for(&f, dg);
        let pm = if sc.ok {
            match (
                scale_coord(&px, dg, sc.mul_coord),
                scale_coord(&py, dg, sc.mul_coord),
            ) {
                (Some(x), Some(y)) => Some((x, y)),
                _ => None,
            }
        } else {
            None
        };
        let fast = certain_member(&f, &sc, &px, &py, pm);
        // Cross-check the i128 fast path against the always-correct rational path.
        let slow = certain_member(&f, &Scale::bad(), &px, &py, None);
        if fast != slow {
            path_disagreements += 1;
        }

        let (pxf, pyf) = (px.to_f64(), py.to_f64());
        let mut worst = f64::INFINITY;
        for _ in 0..SAMPLES {
            let (t, x, y) = sample_in(&f, r);
            let m = in_square_f(pxf, pyf, t, x, y);
            if m < worst {
                worst = m;
            }
        }
        if fast {
            st.fired += 1;
            if worst < -TOL {
                st.violations += 1;
            }
        } else if worst > TOL {
            // Predicate said "not certain" but no sample disagreed (log-only: the box
            // may fail certainty only at unsampled parameters).
            st.incomplete += 1;
        }
    }
    Ok((st, path_disagreements))
}

// ---------------------------------------------------------------------------
// 1b. Lemma E
// ---------------------------------------------------------------------------

fn fuzz_lemma_e(r: &mut Rng) -> Result<(Stats, usize), String> {
    let mut st = Stats::new();
    let mut path_disagreements = 0usize;
    for _ in 0..DRAWS {
        let sm = r.below(2) == 0;
        let f = rand_factor(r, sm);
        let k = Core {
            kx: r.rat_in(0.5, 3.5),
            ky: r.rat_in(0.5, 3.5),
            a: Rat::new(1 + r.below(96) as i128, 64).unwrap(),
        };
        st.draws += 1;

        let dg = lcm_i(lcm_i(den_of(&k.kx), den_of(&k.ky)), den_of(&k.a));
        let sc = scale_for(&f, dg);
        let km = if sc.ok {
            (|| -> Option<(i128, i128, i128)> {
                Some((
                    scale_coord(&k.kx, dg, sc.mul_coord)?,
                    scale_coord(&k.ky, dg, sc.mul_coord)?,
                    scale_coord(&k.a, dg, sc.mul_coord)?,
                ))
            })()
        } else {
            None
        };
        let fast = certain_exempt(&f, &sc, &k, km);
        let slow = certain_exempt(&f, &Scale::bad(), &k, None);
        if fast != slow {
            path_disagreements += 1;
        }

        let (kxf, kyf, af) = (k.kx.to_f64(), k.ky.to_f64(), k.a.to_f64());
        let mut worst = f64::INFINITY;
        for _ in 0..SAMPLES {
            let (t, x, y) = sample_in(&f, r);
            let m = meets_core_f(t, x, y, kxf, kyf, af);
            if m < worst {
                worst = m;
            }
        }
        if fast {
            st.fired += 1;
            if worst < -TOL {
                st.violations += 1;
                if std::env::var("PAIR_DEBUG").is_ok() && st.violations <= 4 {
                    eprintln!(
                        "LEMMA-E VIOLATION worst={:e}
  F: t=[{},{}] x=[{},{}] y=[{},{}]
  K: kx={} ky={} a={}",
                        worst, f.t0, f.t1, f.x0, f.x1, f.y0, f.y1, k.kx, k.ky, k.a
                    );
                    for _ in 0..400 {
                        let (t, x, y) = sample_in(&f, r);
                        if meets_core_f(t, x, y, kxf, kyf, af) < -TOL {
                            eprintln!("    separating sample: t={} cx={} cy={} slack={:e}",
                                t, x, y, meets_core_f(t, x, y, kxf, kyf, af));
                            break;
                        }
                    }
                }
            }
        } else if worst > TOL {
            st.incomplete += 1;
        }
    }
    Ok((st, path_disagreements))
}

// ---------------------------------------------------------------------------
// 1c. NONDISJOINT
// ---------------------------------------------------------------------------

fn fuzz_nondisjoint(r: &mut Rng) -> Result<Stats, String> {
    let mut st = Stats::new();
    for _ in 0..DRAWS {
        let sm = r.below(2) == 0;
        let f = rand_factor(r, sm);
        let sm2 = r.below(2) == 0;
        let mut g = rand_factor(r, sm2);
        // Bias toward nearby boxes, where the predicate is interesting.
        if r.below(2) == 0 {
            let sh = Rat::new(r.below(120) as i128 - 60, 64).unwrap();
            g.x0 = f.x0.add(&sh);
            g.x1 = f.x1.add(&sh);
            let sh2 = Rat::new(r.below(120) as i128 - 60, 64).unwrap();
            g.y0 = f.y0.add(&sh2);
            g.y1 = f.y1.add(&sh2);
        }
        st.draws += 1;
        let ftg = tgeom(&f.t0, &f.t1);
        let gtg = tgeom(&g.t0, &g.t1);
        let pred = nondisjoint(&f, &g, &ftg, &gtg);
        let mut worst = f64::NEG_INFINITY; // max SAT gap over samples
        for _ in 0..SAMPLES {
            let (t1, x1, y1) = sample_in(&f, r);
            let (t2, x2, y2) = sample_in(&g, r);
            let gap = sat_gap_f(t1, x1, y1, t2, x2, y2);
            if gap > worst {
                worst = gap;
            }
        }
        if pred {
            st.fired += 1;
            // Predicate claims EVERY pair overlaps; a sample with gap >= 0 is separated.
            if worst > TOL {
                st.violations += 1;
            }
        } else if worst < -TOL {
            st.incomplete += 1;
        }
    }
    Ok(st)
}

// ---------------------------------------------------------------------------
// 1d. VACUOUS-CONTAIN (spec 3.3 item 1b)
// ---------------------------------------------------------------------------

/// Signed containment slack at a placement: negative means the square leaves [0,s]^2.
fn contain_slack_f(t: f64, cx: f64, cy: f64, s: f64) -> f64 {
    let (c, sn) = cs_f(t);
    let hw = (c + sn) / 2.0;
    (cx - hw).min(s - cx - hw).min(cy - hw).min(s - cy - hw)
}

fn fuzz_vacuous_contain(r: &mut Rng) -> Result<Stats, String> {
    let mut st = Stats::new();
    for _ in 0..DRAWS {
        let sm = r.below(2) == 0;
        let mut f = rand_factor(r, sm);
        // Bias hard toward the container boundary, where this clause lives.
        let side = r.below(4);
        let eps = Rat::new(1 + r.below(40) as i128, 64).unwrap();
        let sv = Rat::from_int(3);
        match side {
            0 => {
                f.x0 = Rat::new(1, 2).unwrap();
                f.x1 = f.x0.add(&eps);
            }
            1 => {
                f.y0 = Rat::new(1, 2).unwrap();
                f.y1 = f.y0.add(&eps);
            }
            2 => {
                f.x1 = sv.sub(&Rat::new(1, 2).unwrap());
                f.x0 = f.x1.sub(&eps);
            }
            _ => {
                f.y1 = sv.sub(&Rat::new(1, 2).unwrap());
                f.y0 = f.y1.sub(&eps);
            }
        }
        st.draws += 1;
        let pred = vacuous_contain(&f, &sv);
        let sf = 3.0f64;
        let mut best = f64::NEG_INFINITY; // max containment slack over samples
        for _ in 0..SAMPLES {
            let (t, x, y) = sample_in(&f, r);
            let v = contain_slack_f(t, x, y, sf);
            if v > best {
                best = v;
            }
        }
        if pred {
            st.fired += 1;
            // Predicate claims EVERY placement leaves the container; a sample with
            // non-negative slack would be a contained placement, i.e. unsound.
            if best > TOL {
                st.violations += 1;
            }
        } else if best < -TOL {
            st.incomplete += 1;
        }
    }
    Ok(st)
}

// ---------------------------------------------------------------------------
// 2. Lemma Q fuzz
// ---------------------------------------------------------------------------

fn fuzz_lemma_q(r: &mut Rng) -> Result<Stats, String> {
    let mut st = Stats::new();
    for _ in 0..DRAWS {
        let den = 1 + r.below(32) as i128;
        let mk = |r: &mut Rng| Rat::new(r.below(81) as i128 - 40, den).unwrap();
        let a = mk(r);
        let b = mk(r);
        let c = mk(r);
        let t0 = r.rat01();
        let t1 = t0.add(&r.rat01()).min_rat(&Rat::one());
        let (t0, t1) = if t0.le(&t1) { (t0, t1) } else { (t1, t0) };
        st.draws += 1;
        let pred = lemma_q_rat(&a, &b, &c, &t0, &t1);
        let (af, bf, cf) = (a.to_f64(), b.to_f64(), c.to_f64());
        let (l, h) = (t0.to_f64(), t1.to_f64());
        let mut worst = f64::INFINITY;
        let n = 400;
        for i in 0..=n {
            let t = l + (h - l) * (i as f64) / (n as f64);
            let q = af * t * t + bf * t + cf;
            if q < worst {
                worst = q;
            }
        }
        if pred {
            st.fired += 1;
            if worst < -1e-9 {
                st.violations += 1;
            }
        } else if worst > 1e-9 {
            st.incomplete += 1;
        }
    }
    Ok(st)
}

// ---------------------------------------------------------------------------
// 3. Toy corpus
// ---------------------------------------------------------------------------

fn find_corpus() -> Option<std::path::PathBuf> {
    if let Ok(p) = std::env::var("PAIR_CORPUS") {
        let pb = std::path::PathBuf::from(p);
        if pb.join("pair_toy_s199.json").exists() {
            return Some(pb);
        }
    }
    let cands = [
        "attempts/A66-corners4-pair/certs",
        "../A66-corners4-pair/certs",
        "../../A66-corners4-pair/certs",
        "../../../A66-corners4-pair/certs",
        "../../../attempts/A66-corners4-pair/certs",
        "../../../../attempts/A66-corners4-pair/certs",
    ];
    for c in cands.iter() {
        let pb = std::path::PathBuf::from(c);
        if pb.join("pair_toy_s199.json").exists() {
            return Some(pb);
        }
    }
    None
}

fn run_cert_file(
    path: &std::path::Path,
    set: &bb::Settings,
) -> Result<(String, String, String, bb::Counts), String> {
    let raw = std::fs::read(path).map_err(|e| format!("read {:?}: {}", path, e))?;
    let c = cert::load(&raw, &path.to_string_lossy())
        .map_err(|e| format!("load {:?}: {}", path, e))?;
    if !c.w2.lt(&c.threshold) {
        return Ok((
            "MALFORMED".into(),
            c.w2.to_string(),
            c.threshold.to_string(),
            bb::Counts::default(),
        ));
    }
    let out = bb::verify(&c, set);
    Ok((
        if out.pass { "PASS".into() } else { "FAIL".into() },
        c.w2.to_string(),
        c.threshold.to_string(),
        out.counts,
    ))
}

// ---------------------------------------------------------------------------
// 4. Corruption gates
// ---------------------------------------------------------------------------

/// A certificate whose COVERED discharge is genuinely MASS-DEPENDENT, used for gates
/// (a) and (b).
///
/// NOTE (documented deviation, see the A73 report): gates (a)/(b) are specified against
/// "the toy PASS cert", but `pair_toy_s199.json` has an EMPTY atom list — its PASS is by
/// NONDISJOINT (no admissible disjoint pair exists below s(2) = 2), so halving or
/// deleting an atom is a no-op there. A mass-load-bearing PASS certificate cannot exist
/// at toy scale either: obligations first appear at exactly s = 2, where the covering
/// atoms must sit ON the square boundary — the tangency case §8 declares uncertifiable.
/// The gates are therefore applied to the COVERED CLAUSE directly (the v1 precedent:
/// "the branch is exercised by unit tests", v1 §5).
fn covered_unit_cert(w1: &str, w2: &str, include_first: bool) -> String {
    let mut atoms = String::new();
    if include_first {
        atoms.push_str(&format!(
            r#"{{"px":"3","py":"3","qx":"6","qy":"6","w":"{}"}},"#,
            w1
        ));
    }
    atoms.push_str(&format!(
        r#"{{"px":"3001/1000","py":"3001/1000","qx":"6001/1000","qy":"6001/1000","w":"{}"}}"#,
        w2
    ));
    format!(
        r#"{{"format":"pair-certificate-v2","s":"10","n":13,"k":0,"m":0,"beta":"0",
            "cores":[],"boxes":[],"atoms":[{}]}}"#,
        atoms
    )
}

fn covered_unit_boxes() -> (Factor, Factor) {
    let f = Factor {
        t0: Rat::zero(),
        t1: Rat::new(1, 100).unwrap(),
        x0: Rat::from_int(3),
        x1: Rat::new(301, 100).unwrap(),
        y0: Rat::from_int(3),
        y1: Rat::new(301, 100).unwrap(),
    };
    let g = Factor {
        t0: Rat::zero(),
        t1: Rat::new(1, 100).unwrap(),
        x0: Rat::from_int(6),
        x1: Rat::new(601, 100).unwrap(),
        y0: Rat::from_int(6),
        y1: Rat::new(601, 100).unwrap(),
    };
    (f, g)
}

fn gate_covered(desc: &str, src: String, expect_fires: bool) -> Result<serde_json::Value, String> {
    let c = cert::load(src.as_bytes(), desc).map_err(|e| format!("{}: {}", desc, e))?;
    let (f, g) = covered_unit_boxes();
    let (mass, fires) = bb::covered_probe(&c, &f, &g);
    if fires != expect_fires {
        return Err(format!(
            "gate {}: COVERED fired = {} (expected {}), certain mass = {}",
            desc, fires, expect_fires, mass
        ));
    }
    Ok(json!({"gate": desc, "certain_mass": mass.to_string(),
              "covered_fires": fires, "expected": expect_fires, "ok": true}))
}

// ---------------------------------------------------------------------------

pub fn run() -> Result<String, String> {
    let mut r = Rng::new(0x5EED_A73_u64);
    let mut report = serde_json::Map::new();

    // ---- sqrt(2) bracket identities ----
    check_sqrt2_constants()?;
    report.insert(
        "sqrt2_constants".into(),
        json!({
            "t_star_lower": "408/985", "t_star_upper": "5741/13860",
            "w_upper_bound": "19601/13860",
            "identity_1393sq_lt_2x985sq": 1393i64*1393 < 2*985*985,
            "identity_19601sq_gt_2x13860sq": 19601i64*19601 > 2*13860*13860,
            "ok": true
        }),
    );

    // ---- 1. predicate fuzz ----
    let (m_st, m_path) = fuzz_lemma_m(&mut r)?;
    let (e_st, e_path) = fuzz_lemma_e(&mut r)?;
    let nd_st = fuzz_nondisjoint(&mut r)?;
    let vc_st = fuzz_vacuous_contain(&mut r)?;
    let q_st = fuzz_lemma_q(&mut r)?;

    for (name, st) in [
        ("lemma_m", &m_st),
        ("lemma_e", &e_st),
        ("nondisjoint", &nd_st),
        ("vacuous_contain", &vc_st),
        ("lemma_q", &q_st),
    ] {
        if st.violations > 0 {
            return Err(format!(
                "{}: {} SOUNDNESS VIOLATIONS in {} draws — unsound build, aborting",
                name, st.violations, st.draws
            ));
        }
    }
    if m_path > 0 || e_path > 0 {
        return Err(format!(
            "i128 fast path disagreed with the rational path (lemma_m: {}, lemma_e: {}) \
             — unsound build, aborting",
            m_path, e_path
        ));
    }
    report.insert("lemma_m".into(), m_st.json());
    report.insert("lemma_e".into(), e_st.json());
    report.insert("nondisjoint".into(), nd_st.json());
    report.insert("vacuous_contain".into(), vc_st.json());
    report.insert("lemma_q".into(), q_st.json());
    report.insert(
        "fastpath_vs_rational".into(),
        json!({"lemma_m_disagreements": m_path, "lemma_e_disagreements": e_path, "ok": true}),
    );

    // ---- 3. toy corpus ----
    let mut corpus = serde_json::Map::new();
    let mut corpus_ok = true;
    match find_corpus() {
        None => {
            corpus.insert("status".into(), json!("CORPUS NOT FOUND"));
            corpus_ok = false;
        }
        Some(dir) => {
            corpus.insert("dir".into(), json!(dir.to_string_lossy()));
            let set = bb::Settings {
                depth: 44,
                split: 2,
                ..Default::default()
            };
            for (name, expect) in [
                ("pair_toy_s199.json", "PASS"),
                ("pair_control_s201.json", "FAIL"),
                // Smoke has no v1 report; the cross-validation criterion for it is
                // AGREEMENT between the two v2 implementations at comparable budgets.
                ("pair_smoke_paths.json", "?"),
            ] {
                let p = dir.join(name);
                if !p.exists() {
                    corpus.insert(name.into(), json!({"status": "missing"}));
                    if expect != "?" {
                        corpus_ok = false;
                    }
                    continue;
                }
                let (verdict, w2, th, counts) = run_cert_file(&p, &set)?;
                let ok = expect == "?" || verdict == expect;
                if !ok {
                    corpus_ok = false;
                }
                corpus.insert(
                    name.into(),
                    json!({
                        "verdict": verdict, "expected": expect, "ok": ok,
                        "W2": w2, "threshold": th,
                        "pairs_examined": counts.pairs_examined,
                        "max_depth": counts.max_depth,
                        "nondisjoint": counts.nondisjoint,
                        "exempt_core": counts.exempt_core,
                        "covered": counts.covered,
                        "covered_f": counts.covered_f,
                        "vacuous": counts.vacuous,
                        "deficient_early": counts.deficient_early,
                    }),
                );
            }
        }
    }
    // ---- A73 anchors: the mass-load-bearing positive path (PASS via COVERED) ----
    {
        let anchors = ["anchor_grid05_s3.json", "anchor_grid06_s3.json"];
        let dirs = [
            "attempts/A73-pair-v2/certs",
            "../certs",
            "../../certs",
            "../../../certs",
        ];
        let adir = dirs
            .iter()
            .map(std::path::PathBuf::from)
            .find(|d| d.join(anchors[0]).exists());
        match adir {
            None => {
                corpus.insert("anchors".into(), json!("ANCHOR CERTS NOT FOUND"));
                corpus_ok = false;
            }
            Some(d) => {
                let set = bb::Settings {
                    depth: 40,
                    split: 2,
                    ..Default::default()
                };
                for name in anchors.iter() {
                    let (verdict, w2, th, counts) = run_cert_file(&d.join(name), &set)?;
                    let ok = verdict == "PASS";
                    if !ok {
                        corpus_ok = false;
                    }
                    corpus.insert(
                        (*name).into(),
                        json!({
                            "verdict": verdict, "expected": "PASS", "ok": ok,
                            "W2": w2, "threshold": th,
                            "pairs_examined": counts.pairs_examined,
                            "max_depth": counts.max_depth,
                            "covered": counts.covered,
                            "covered_f": counts.covered_f,
                            "vacuous_contain": counts.vacuous_contain,
                        }),
                    );
                }
            }
        }
    }

    if !corpus_ok {
        return Err(format!(
            "toy corpus verdicts did not match: {}",
            serde_json::to_string(&corpus).unwrap()
        ));
    }
    report.insert("toy_corpus".into(), serde_json::Value::Object(corpus));

    // ---- 4. corruption gates ----
    let mut gates = Vec::new();
    // baseline: 3/4 + 1/2 = 5/4 >= 1 -> COVERED fires
    gates.push(gate_covered(
        "baseline (mass 5/4 >= 1)",
        covered_unit_cert("3/4", "1/2", true),
        true,
    )?);
    // (a) one atom weight halved: 3/8 + 1/2 = 7/8 < 1 -> must NOT fire
    gates.push(gate_covered(
        "(a) atom weight halved",
        covered_unit_cert("3/8", "1/2", true),
        false,
    )?);
    // (b) atom deleted: 1/2 < 1 -> must NOT fire
    gates.push(gate_covered(
        "(b) atom deleted",
        covered_unit_cert("3/4", "1/2", false),
        false,
    )?);

    // VACUOUS-CONTAIN unit checks: a clause that never fires would pass the fuzz
    // vacuously, so pin one box that must be discharged and one that must not.
    {
        let sv = Rat::from_int(3);
        // Every placement pokes out of the left wall: cx <= 51/100 while w(t)/2 > 0.52
        // across t in [2/5, 3/5].
        let out = Factor {
            t0: Rat::new(2, 5).unwrap(),
            t1: Rat::new(3, 5).unwrap(),
            x0: Rat::new(1, 2).unwrap(),
            x1: Rat::new(51, 100).unwrap(),
            y0: Rat::new(3, 2).unwrap(),
            y1: Rat::new(3, 2).unwrap(),
        };
        if !vacuous_contain(&out, &sv) {
            return Err("VACUOUS-CONTAIN failed to fire on a wholly-uncontained box".into());
        }
        // Comfortably interior: must NOT fire.
        let inside = Factor {
            t0: Rat::zero(),
            t1: Rat::one(),
            x0: Rat::new(5, 4).unwrap(),
            x1: Rat::new(7, 4).unwrap(),
            y0: Rat::new(5, 4).unwrap(),
            y1: Rat::new(7, 4).unwrap(),
        };
        if vacuous_contain(&inside, &sv) {
            return Err("VACUOUS-CONTAIN fired on a fully contained box (UNSOUND)".into());
        }
        gates.push(json!({"gate": "VACUOUS-CONTAIN fires iff no contained placement",
                          "uncontained_box_discharged": true,
                          "contained_box_kept": true, "ok": true}));
    }

    // (c) a float literal anywhere -> exit 2 (malformed)
    let float_src = r#"{"format":"pair-certificate-v2","s":"10","n":13,"k":0,"m":0,
        "beta":"0","cores":[],"boxes":[],"atoms":[],
        "provenance":{"note":"harmless","value":1.5}}"#;
    match cert::load(float_src.as_bytes(), "float-gate") {
        Ok(_) => return Err("gate (c): a float literal in provenance was ACCEPTED".into()),
        Err(e) => gates.push(json!({"gate": "(c) float literal in provenance",
                                    "result": "malformed (exit 2)",
                                    "detail": e.to_string(), "ok": true})),
    }
    // and a bare float as a top-level number
    let float_src2 = r#"{"format":"pair-certificate-v2","s":"10","n":13,"k":0,"m":0,
        "beta":"0","cores":[],"boxes":[],"atoms":[],"total":0.0}"#;
    match cert::load(float_src2.as_bytes(), "float-gate-2") {
        Ok(_) => return Err("gate (c2): a float `total` was ACCEPTED".into()),
        Err(_) => gates.push(json!({"gate": "(c2) float total", "result": "malformed (exit 2)",
                                    "ok": true})),
    }

    // (d) total != sum(w) -> exit 2
    let bad_total = r#"{"format":"pair-certificate-v2","s":"10","n":13,"k":0,"m":0,
        "beta":"0","cores":[],"boxes":[],
        "atoms":[{"px":"3","py":"3","qx":"6","qy":"6","w":"1/2"}],"total":"3/4"}"#;
    match cert::load(bad_total.as_bytes(), "total-gate") {
        Ok(_) => return Err("gate (d): total != sum(w) was ACCEPTED".into()),
        Err(e) => gates.push(json!({"gate": "(d) total != sum(w)",
                                    "result": "malformed (exit 2)",
                                    "detail": e.to_string(), "ok": true})),
    }

    // (e) W2 >= threshold -> (P1') violated, exit 2
    let bad_p1 = r#"{"format":"pair-certificate-v2","s":"10","n":2,"k":0,"m":0,
        "beta":"0","cores":[],"boxes":[],
        "atoms":[{"px":"3","py":"3","qx":"6","qy":"6","w":"5"}]}"#;
    let c = cert::load(bad_p1.as_bytes(), "p1-gate").map_err(|e| e.to_string())?;
    if c.w2.lt(&c.threshold) {
        return Err(format!(
            "gate (e): W2 = {} unexpectedly < threshold = {}",
            c.w2, c.threshold
        ));
    }
    gates.push(json!({"gate": "(e) W2 >= threshold", "W2": c.w2.to_string(),
                      "threshold": c.threshold.to_string(),
                      "result": "(P1') violated -> exit 2", "ok": true}));

    // (f) hint cut point outside its interval -> fallback, verdict unchanged
    let hinted = r#"{"format":"pair-certificate-v2","s":"199/100","n":2,"k":0,"m":0,
        "beta":"0","cores":[],"boxes":[],"atoms":[],
        "hints":{"trees":{"0,0":{"cut":{"f":0,"d":"t","at":"7/2"},
                                "lo":{"leaf":{"clause":"NONDISJOINT"}},
                                "hi":{"leaf":{"clause":"NONDISJOINT"}}}}}}"#;
    let ch = cert::load(hinted.as_bytes(), "hint-gate").map_err(|e| e.to_string())?;
    let set = bb::Settings {
        depth: 44,
        split: 2,
        ..Default::default()
    };
    let outh = bb::verify(&ch, &set);
    if !outh.pass {
        return Err("gate (f): hinted toy did not still PASS".into());
    }
    if outh.counts.hint_misses == 0 {
        return Err("gate (f): an out-of-interval hint cut was not counted as a miss".into());
    }
    gates.push(json!({"gate": "(f) hint cut outside interval",
                      "verdict": "PASS (unchanged)",
                      "hint_misses": outh.counts.hint_misses, "ok": true}));

    report.insert("corruption_gates".into(), json!(gates));
    report.insert(
        "gates_note".into(),
        json!("Gates (a)/(b) are applied to the COVERED clause directly: the v1 toy PASS \
               certificate has an empty atom list (its PASS is by NONDISJOINT), and no \
               mass-load-bearing PASS certificate exists at toy scale (obligations begin \
               at exactly s = 2, which is the tangency case spec §8 calls uncertifiable). \
               This follows the v1 precedent that the COVERED branch is exercised by unit \
               tests (v1 §5)."),
    );

    let (per_file, combined) = crate::source_hashes();
    report.insert(
        "verifier_sha256".into(),
        json!({
            "combined": combined,
            "files": per_file.iter().map(|(n,h)| json!({"file": n, "sha256": h}))
                       .collect::<Vec<_>>()
        }),
    );
    report.insert("selftest".into(), json!("PASS"));
    report.insert(
        "draws_per_predicate".into(),
        json!({"predicate_draws": DRAWS, "samples_per_draw": SAMPLES,
               "lemma_q_dense_samples": 401}),
    );

    Ok(serde_json::to_string_pretty(&serde_json::Value::Object(report)).unwrap())
}
