//! Certificate loading (spec §2), float-literal rejection, and the atom spatial index.

use crate::geom::{BoxSq, Core};
use crate::rat::{gcd_i128, Rat};
use serde_json::Value;

/// Outcome of loading: `Malformed` maps to exit code 2.
#[derive(Debug)]
pub enum LoadErr {
    Malformed(String),
}

impl std::fmt::Display for LoadErr {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            LoadErr::Malformed(m) => write!(f, "{}", m),
        }
    }
}

macro_rules! bad {
    ($($a:tt)*) => { return Err(LoadErr::Malformed(format!($($a)*))) };
}

// ---------------------------------------------------------------------------
// Float literal rejection (spec §2: "JSON float literals are rejected ANYWHERE in
// the file, including inside `provenance`").
//
// This is a RAW-BYTE pre-parse scan, deliberately independent of serde_json's number
// representation: a post-parse type check would have to trust how the parser chose to
// represent `1.0` or `1e5`. String contents are skipped (a rational "p/q" is a string,
// and a provenance string may legitimately contain a decimal point).
// ---------------------------------------------------------------------------

pub fn scan_for_float_literals(src: &[u8]) -> Result<(), String> {
    let n = src.len();
    let mut i = 0usize;
    while i < n {
        let ch = src[i];
        if ch == b'"' {
            // Skip a string literal, honouring backslash escapes.
            i += 1;
            while i < n {
                if src[i] == b'\\' {
                    i += 2;
                    continue;
                }
                if src[i] == b'"' {
                    i += 1;
                    break;
                }
                i += 1;
            }
            continue;
        }
        // A JSON number token starts with '-' or a digit. Keywords (true/false/null)
        // start with a letter and are stepped over one byte at a time, so the 'e' in
        // "true" is never mistaken for an exponent.
        if ch == b'-' || ch.is_ascii_digit() {
            let start = i;
            let mut float_shaped = false;
            while i < n {
                let c = src[i];
                if c.is_ascii_digit() {
                    i += 1;
                } else if c == b'.' || c == b'e' || c == b'E' {
                    float_shaped = true;
                    i += 1;
                } else if (c == b'+' || c == b'-') && i > start {
                    // Only legal inside an exponent; either way it stays in the token.
                    let prev = src[i - 1];
                    if prev == b'e' || prev == b'E' {
                        i += 1;
                    } else {
                        break;
                    }
                } else if c == b'-' && i == start {
                    i += 1;
                } else {
                    break;
                }
            }
            if float_shaped {
                let tok = String::from_utf8_lossy(&src[start..i]).to_string();
                return Err(format!(
                    "JSON float literal `{}` at byte offset {} (spec §2: floats rejected anywhere)",
                    tok, start
                ));
            }
            continue;
        }
        i += 1;
    }
    Ok(())
}

// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
pub struct Atom {
    pub px: Rat,
    pub py: Rat,
    pub qx: Rat,
    pub qy: Rat,
    pub w: Rat,
    // Float images for shortlisting only (never on a decision path).
    pub pxf: f64,
    pub pyf: f64,
    pub qxf: f64,
    pub qyf: f64,
    pub wf: f64,
}

pub struct Cert {
    pub format: String,
    pub s: Rat,
    pub n: i64,
    pub k: i64,
    pub m: i64,
    pub beta: Rat,
    pub cores: Vec<Core>,
    pub boxes: Vec<BoxSq>,
    pub atoms: Vec<Atom>,
    pub total_field: Option<Rat>,
    pub hints: Option<Value>,
    pub w2: Rat,
    pub threshold: Rat,
    pub coincident: usize,
    /// Global coordinate denominator for the integer fast path (0 = unavailable).
    pub dg: i128,
    /// Atom coordinates scaled by `dg` (px, py, qx, qy). Empty when `dg == 0`.
    pub atom_scaled: Vec<[i128; 4]>,
    /// Core (kx, ky, a) scaled by `dg`. Empty when `dg == 0`.
    pub core_scaled: Vec<[i128; 3]>,
    pub grid: Grid,
}

fn get_rat(o: &Value, key: &str, ctx: &str) -> Result<Rat, LoadErr> {
    match o.get(key) {
        Some(Value::String(s)) => {
            Rat::parse(s).map_err(|e| LoadErr::Malformed(format!("{}: {}", ctx, e)))
        }
        Some(Value::Number(nn)) => {
            // Integers are permitted as JSON numbers; floats were already rejected by
            // the raw scan, so anything arriving here is integral.
            let t = nn.to_string();
            Rat::parse(&t).map_err(|e| LoadErr::Malformed(format!("{}: {}", ctx, e)))
        }
        Some(v) => Err(LoadErr::Malformed(format!(
            "{}: field `{}` must be an exact rational string, got {}",
            ctx, key, v
        ))),
        None => Err(LoadErr::Malformed(format!(
            "{}: missing required field `{}`",
            ctx, key
        ))),
    }
}

fn get_int(o: &Value, key: &str, def: Option<i64>) -> Result<i64, LoadErr> {
    match o.get(key) {
        Some(Value::Number(nn)) => match nn.as_i64() {
            Some(v) => Ok(v),
            None => bad!("field `{}` is not an integer", key),
        },
        Some(Value::String(s)) => match s.trim().parse::<i64>() {
            Ok(v) => Ok(v),
            Err(_) => bad!("field `{}` is not an integer", key),
        },
        Some(_) => bad!("field `{}` is not an integer", key),
        None => match def {
            Some(d) => Ok(d),
            None => bad!("missing required field `{}`", key),
        },
    }
}

/// lcm with overflow check; returns None on overflow.
fn lcm_ck(a: i128, b: i128) -> Option<i128> {
    let g = gcd_i128(a, b);
    if g == 0 {
        return None;
    }
    (a / g).checked_mul(b)
}

/// Cap on the global coordinate denominator. Above this the integer fast path stops
/// paying for itself and we use the (always correct) rational path instead.
const DG_CAP: i128 = 1_000_000_000_000_000;

pub fn load(src: &[u8], path_label: &str) -> Result<Cert, LoadErr> {
    scan_for_float_literals(src).map_err(LoadErr::Malformed)?;
    let v: Value = serde_json::from_slice(src)
        .map_err(|e| LoadErr::Malformed(format!("{}: JSON parse error: {}", path_label, e)))?;
    if !v.is_object() {
        bad!("{}: top level must be a JSON object", path_label);
    }

    let format = match v.get("format") {
        Some(Value::String(s)) => s.clone(),
        _ => bad!("{}: missing/!string `format`", path_label),
    };
    // A v2 verifier MUST also accept v1 certificates (spec §2).
    if format != "pair-certificate-v2" && format != "pair-certificate-v1" {
        bad!(
            "{}: unsupported format {:?} (accepted: pair-certificate-v1, pair-certificate-v2)",
            path_label,
            format
        );
    }

    let s = get_rat(&v, "s", path_label)?;
    if !s.is_pos() {
        bad!("{}: side s must be positive", path_label);
    }
    let n = get_int(&v, "n", Some(11))?;
    let k = get_int(&v, "k", None)?;
    let m = get_int(&v, "m", None)?;
    let beta = get_rat(&v, "beta", path_label)?;
    if beta.is_neg() {
        bad!("{}: beta must be >= 0", path_label);
    }

    let mut cores = Vec::new();
    if let Some(Value::Array(a)) = v.get("cores") {
        for (i, c) in a.iter().enumerate() {
            let ctx = format!("{}: cores[{}]", path_label, i);
            let core = Core {
                kx: get_rat(c, "kx", &ctx)?,
                ky: get_rat(c, "ky", &ctx)?,
                a: get_rat(c, "a", &ctx)?,
            };
            if core.a.is_neg() {
                bad!("{}: core half-side a must be >= 0", ctx);
            }
            cores.push(core);
        }
    }
    if cores.len() as i64 != k {
        bad!(
            "{}: k = {} but {} cores present",
            path_label,
            k,
            cores.len()
        );
    }

    let mut boxes = Vec::new();
    if let Some(Value::Array(a)) = v.get("boxes") {
        for (i, b) in a.iter().enumerate() {
            let ctx = format!("{}: boxes[{}]", path_label, i);
            boxes.push(BoxSq {
                bx: get_rat(b, "bx", &ctx)?,
                by: get_rat(b, "by", &ctx)?,
                h: get_rat(b, "h", &ctx)?,
            });
        }
    }
    if boxes.len() as i64 != m {
        bad!(
            "{}: m = {} but {} boxes present",
            path_label,
            m,
            boxes.len()
        );
    }

    let mut atoms = Vec::new();
    let mut w2 = Rat::zero();
    let mut coincident = 0usize;
    if let Some(Value::Array(a)) = v.get("atoms") {
        for (i, at) in a.iter().enumerate() {
            let ctx = format!("{}: atoms[{}]", path_label, i);
            let px = get_rat(at, "px", &ctx)?;
            let py = get_rat(at, "py", &ctx)?;
            let qx = get_rat(at, "qx", &ctx)?;
            let qy = get_rat(at, "qy", &ctx)?;
            let w = get_rat(at, "w", &ctx)?;
            if w.is_neg() {
                bad!("{}: atom weight w must be >= 0", ctx);
            }
            if px.eq_rat(&qx) && py.eq_rat(&qy) {
                coincident += 1;
            }
            w2 = w2.add(&w);
            atoms.push(Atom {
                pxf: px.to_f64(),
                pyf: py.to_f64(),
                qxf: qx.to_f64(),
                qyf: qy.to_f64(),
                wf: w.to_f64(),
                px,
                py,
                qx,
                qy,
                w,
            });
        }
    }

    // `total` is optional; must equal sum(w) exactly when present. Computed value governs.
    let total_field = match v.get("total") {
        Some(Value::String(t)) => {
            Some(Rat::parse(t).map_err(|e| LoadErr::Malformed(format!("{}: {}", path_label, e)))?)
        }
        Some(Value::Number(nn)) => Some(
            Rat::parse(&nn.to_string())
                .map_err(|e| LoadErr::Malformed(format!("{}: {}", path_label, e)))?,
        ),
        Some(_) => bad!("{}: `total` must be an exact rational string", path_label),
        None => None,
    };
    if let Some(t) = &total_field {
        if !t.eq_rat(&w2) {
            bad!(
                "{}: `total` = {} but sum(w) = {} (spec §2)",
                path_label,
                t,
                w2
            );
        }
    }

    // Threshold = C(N,2) + beta*m with N = n - k.
    let nn = n - k;
    let cn2 = if nn >= 2 {
        Rat::new((nn as i128) * ((nn - 1) as i128), 2).unwrap()
    } else {
        Rat::zero()
    };
    let threshold = cn2.add(&beta.mul(&Rat::from_int(m as i128)));

    let hints = v.get("hints").cloned();

    // ---- global coordinate denominator for the integer fast path ----
    let mut dg: i128 = 1;
    let mut dg_ok = true;
    {
        let mut acc = |r: &Rat| {
            if !dg_ok {
                return;
            }
            match r.small() {
                Some((_, d)) => match lcm_ck(dg, d) {
                    Some(x) if x <= DG_CAP => dg = x,
                    _ => dg_ok = false,
                },
                None => dg_ok = false,
            }
        };
        for a in &atoms {
            acc(&a.px);
            acc(&a.py);
            acc(&a.qx);
            acc(&a.qy);
        }
        for c in &cores {
            acc(&c.kx);
            acc(&c.ky);
            acc(&c.a);
        }
    }

    let (atom_scaled, core_scaled) = if dg_ok {
        let mut asc = Vec::with_capacity(atoms.len());
        let mut csc = Vec::with_capacity(cores.len());
        let sc = |r: &Rat| -> Option<i128> {
            let (n, d) = r.small()?;
            n.checked_mul(dg / d)
        };
        let mut ok = true;
        for a in &atoms {
            match (sc(&a.px), sc(&a.py), sc(&a.qx), sc(&a.qy)) {
                (Some(x), Some(y), Some(z), Some(w)) => asc.push([x, y, z, w]),
                _ => {
                    ok = false;
                    break;
                }
            }
        }
        if ok {
            for c in &cores {
                match (sc(&c.kx), sc(&c.ky), sc(&c.a)) {
                    (Some(x), Some(y), Some(z)) => csc.push([x, y, z]),
                    _ => {
                        ok = false;
                        break;
                    }
                }
            }
        }
        if ok {
            (asc, csc)
        } else {
            dg_ok = false;
            (Vec::new(), Vec::new())
        }
    } else {
        (Vec::new(), Vec::new())
    };

    let grid = Grid::build(&atoms);

    Ok(Cert {
        format,
        s,
        n,
        k,
        m,
        beta,
        cores,
        boxes,
        atoms,
        total_field,
        hints,
        w2,
        threshold,
        coincident,
        dg: if dg_ok { dg } else { 0 },
        atom_scaled,
        core_scaled,
        grid,
    })
}

// ---------------------------------------------------------------------------
// Uniform grid over atom endpoints — a FLOAT shortlist.
//
// Spec §3.0 explicitly permits this: "Floats MAY shortlist candidates whose acceptance
// is decided exactly (a missed shortlist can cause spurious FAIL, never spurious PASS)."
// An atom dropped by the shortlist simply does not contribute mass, which makes PASS
// harder. Query rectangles are padded OUTWARD so a drop is in practice impossible.
// ---------------------------------------------------------------------------

pub struct Grid {
    pub ox: f64,
    pub oy: f64,
    pub cell: f64,
    pub nx: usize,
    pub ny: usize,
    /// cells_p[c] = atom indices whose p endpoint lies in cell c.
    pub cells_p: Vec<Vec<u32>>,
    /// cells_q[c] = atom indices whose q endpoint lies in cell c.
    pub cells_q: Vec<Vec<u32>>,
    pub empty: bool,
}

impl Grid {
    pub fn build(atoms: &[Atom]) -> Grid {
        if atoms.is_empty() {
            return Grid {
                ox: 0.0,
                oy: 0.0,
                cell: 1.0,
                nx: 1,
                ny: 1,
                cells_p: vec![Vec::new()],
                cells_q: vec![Vec::new()],
                empty: true,
            };
        }
        let mut minx = f64::INFINITY;
        let mut miny = f64::INFINITY;
        let mut maxx = f64::NEG_INFINITY;
        let mut maxy = f64::NEG_INFINITY;
        for a in atoms {
            for (x, y) in [(a.pxf, a.pyf), (a.qxf, a.qyf)] {
                if x < minx {
                    minx = x;
                }
                if y < miny {
                    miny = y;
                }
                if x > maxx {
                    maxx = x;
                }
                if y > maxy {
                    maxy = y;
                }
            }
        }
        // Cell ~ 1 unit: a unit square spans at most ~1.42 units, so a query rectangle
        // touches only a handful of cells.
        let cell = 1.0f64;
        let nx = (((maxx - minx) / cell).ceil() as isize + 2).max(1) as usize;
        let ny = (((maxy - miny) / cell).ceil() as isize + 2).max(1) as usize;
        let nx = nx.min(4096);
        let ny = ny.min(4096);
        let mut cells_p = vec![Vec::new(); nx * ny];
        let mut cells_q = vec![Vec::new(); nx * ny];
        let idx = |x: f64, y: f64| -> usize {
            let cx = (((x - minx) / cell).floor() as isize).clamp(0, nx as isize - 1) as usize;
            let cy = (((y - miny) / cell).floor() as isize).clamp(0, ny as isize - 1) as usize;
            cy * nx + cx
        };
        for (i, a) in atoms.iter().enumerate() {
            cells_p[idx(a.pxf, a.pyf)].push(i as u32);
            cells_q[idx(a.qxf, a.qyf)].push(i as u32);
        }
        Grid {
            ox: minx,
            oy: miny,
            cell,
            nx,
            ny,
            cells_p,
            cells_q,
            empty: false,
        }
    }

    /// Append candidate atom indices whose `which` endpoint (0 = p, 1 = q) may lie in
    /// the axis-aligned rectangle. The rectangle is treated as inclusive and is expected
    /// to have been padded outward by the caller.
    pub fn query(&self, which: usize, x0: f64, y0: f64, x1: f64, y1: f64, out: &mut Vec<u32>) {
        if self.empty {
            return;
        }
        let cx0 = (((x0 - self.ox) / self.cell).floor() as isize).clamp(0, self.nx as isize - 1);
        let cx1 = (((x1 - self.ox) / self.cell).floor() as isize).clamp(0, self.nx as isize - 1);
        let cy0 = (((y0 - self.oy) / self.cell).floor() as isize).clamp(0, self.ny as isize - 1);
        let cy1 = (((y1 - self.oy) / self.cell).floor() as isize).clamp(0, self.ny as isize - 1);
        let cells = if which == 0 { &self.cells_p } else { &self.cells_q };
        for cy in cy0..=cy1 {
            for cx in cx0..=cx1 {
                let c = (cy as usize) * self.nx + (cx as usize);
                out.extend_from_slice(&cells[c]);
            }
        }
    }
}
