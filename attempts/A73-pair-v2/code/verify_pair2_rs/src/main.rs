//! verify_pair2 — compiled verifier for pair-certificate-v2.
//!
//! Clean-room implementation written FROM `docs/specs/pair_certificate_v2.md` (plus the
//! referenced v1 clauses and the v1 selftest corpus) ONLY. No verifier source was read.
//!
//! Exit codes (spec §3.8): 0 PASS, 1 FAIL, 2 malformed / (P1') violated.

mod bb;
mod bench;
mod cert;
mod geom;
mod rat;
mod selftest;

use rat::Rat;
use sha2::{Digest, Sha256};
use std::process::ExitCode;

// Source files hashed for the report's `verifier_sha256` (spec §5). Embedding them at
// compile time ties the hash to the binary rather than to whatever is on disk at runtime.
pub const SRC_FILES: [(&str, &str); 6] = [
    ("main.rs", include_str!("main.rs")),
    ("rat.rs", include_str!("rat.rs")),
    ("geom.rs", include_str!("geom.rs")),
    ("cert.rs", include_str!("cert.rs")),
    ("bb.rs", include_str!("bb.rs")),
    ("selftest.rs", include_str!("selftest.rs")),
];

pub fn sha256_hex(data: &[u8]) -> String {
    let mut h = Sha256::new();
    h.update(data);
    format!("{:x}", h.finalize())
}

/// Per-file hashes plus a combined hash over all sources in declaration order.
pub fn source_hashes() -> (Vec<(String, String)>, String) {
    let mut per = Vec::new();
    let mut combined = Sha256::new();
    for (name, body) in SRC_FILES.iter() {
        per.push((name.to_string(), sha256_hex(body.as_bytes())));
        combined.update(name.as_bytes());
        combined.update(body.as_bytes());
    }
    // bench.rs is test scaffolding, not on any decision path; hashed separately.
    (per, format!("{:x}", combined.finalize()))
}

fn usage() -> String {
    "usage: verify_pair2 CERT.json [--depth D] [--split K] [--nodes N] [--report OUT]\n\
     \x20                    [--selftest] [--jobs J] [--survey] [--faildump N]\n\
     \x20                    [--probe-stride S] [--bench] [--emit-bench PATH]\n\
     exit codes: 0 PASS, 1 FAIL, 2 malformed / (P1') violated"
        .to_string()
}

struct Args {
    cert: Option<String>,
    depth: u32,
    split: u32,
    nodes: u64,
    report: Option<String>,
    selftest: bool,
    jobs: usize,
    survey: bool,
    faildump: usize,
    probe_stride: u32,
    bench: bool,
    emit_bench: Option<String>,
}

fn parse_args() -> Result<Args, String> {
    let mut a = Args {
        cert: None,
        depth: 40,
        split: 2,
        nodes: u64::MAX,
        report: None,
        selftest: false,
        jobs: 1,
        survey: false,
        faildump: 8,
        probe_stride: 8,
        bench: false,
        emit_bench: None,
    };
    let argv: Vec<String> = std::env::args().skip(1).collect();
    let mut i = 0;
    while i < argv.len() {
        let s = &argv[i];
        let mut need = |i: &mut usize| -> Result<String, String> {
            *i += 1;
            argv.get(*i)
                .cloned()
                .ok_or_else(|| format!("missing value after {}", s))
        };
        match s.as_str() {
            "--depth" => a.depth = need(&mut i)?.parse().map_err(|_| "bad --depth")?,
            "--split" => a.split = need(&mut i)?.parse().map_err(|_| "bad --split")?,
            "--nodes" => a.nodes = need(&mut i)?.parse().map_err(|_| "bad --nodes")?,
            "--report" => a.report = Some(need(&mut i)?),
            "--jobs" => a.jobs = need(&mut i)?.parse().map_err(|_| "bad --jobs")?,
            "--faildump" => a.faildump = need(&mut i)?.parse().map_err(|_| "bad --faildump")?,
            "--probe-stride" => {
                a.probe_stride = need(&mut i)?.parse().map_err(|_| "bad --probe-stride")?
            }
            "--emit-bench" => a.emit_bench = Some(need(&mut i)?),
            "--selftest" => a.selftest = true,
            "--survey" => a.survey = true,
            "--bench" => a.bench = true,
            "-h" | "--help" => return Err(usage()),
            other => {
                if other.starts_with("--") {
                    return Err(format!("unknown option {}", other));
                }
                if a.cert.is_some() {
                    return Err("more than one certificate path given".into());
                }
                a.cert = Some(other.to_string());
            }
        }
        i += 1;
    }
    if a.split > 6 {
        return Err("--split above 6 would enumerate an unreasonable root grid".into());
    }
    Ok(a)
}

fn main() -> ExitCode {
    let args = match parse_args() {
        Ok(a) => a,
        Err(e) => {
            eprintln!("{}", e);
            return ExitCode::from(2);
        }
    };

    if args.selftest {
        match selftest::run() {
            Ok(rep) => {
                println!("{}", rep);
                if !args.bench && args.cert.is_none() && args.emit_bench.is_none() {
                    return ExitCode::SUCCESS;
                }
            }
            Err(e) => {
                eprintln!("SELFTEST FAILED: {}", e);
                eprintln!("This build is NOT citable.");
                return ExitCode::from(1);
            }
        }
    }

    if let Some(p) = &args.emit_bench {
        match bench::emit_to(p) {
            Ok(n) => println!("wrote synthetic benchmark certificate ({} atoms) to {}", n, p),
            Err(e) => {
                eprintln!("emit-bench failed: {}", e);
                return ExitCode::from(2);
            }
        }
        if args.cert.is_none() && !args.bench {
            return ExitCode::SUCCESS;
        }
    }

    if args.bench {
        match bench::run() {
            Ok(s) => {
                println!("{}", s);
                return ExitCode::SUCCESS;
            }
            Err(e) => {
                eprintln!("bench failed: {}", e);
                return ExitCode::from(2);
            }
        }
    }

    let path = match &args.cert {
        Some(p) => p.clone(),
        None => {
            eprintln!("{}", usage());
            return ExitCode::from(2);
        }
    };

    let raw = match std::fs::read(&path) {
        Ok(r) => r,
        Err(e) => {
            eprintln!("cannot read {}: {}", path, e);
            return ExitCode::from(2);
        }
    };

    let c = match cert::load(&raw, &path) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("MALFORMED: {}", e);
            return ExitCode::from(2);
        }
    };

    if c.coincident > 0 {
        // v1 §2 hard warning: a coincident atom can NEVER be collected by an
        // interior-disjoint pair; its weight is pure loss against W2.
        eprintln!(
            "WARNING (hard): {} coincident atom(s) (p == p'). These can never be collected \
             by an interior-disjoint pair; their weight counts toward W2 as pure loss.",
            c.coincident
        );
    }

    // ---- (P1') ----
    let p1_ok = c.w2.lt(&c.threshold);
    if !p1_ok {
        eprintln!(
            "MALFORMED / (P1') VIOLATED: W2 = {} is not < threshold C(N,2) + beta*m = {}",
            c.w2, c.threshold
        );
        // Still emit a report when asked, so the failure is auditable.
        if let Some(rp) = &args.report {
            let set = bb::Settings {
                depth: args.depth,
                split: args.split,
                nodes: args.nodes,
                jobs: args.jobs,
                survey: args.survey,
                faildump: args.faildump,
                probe_stride: args.probe_stride,
            };
            let _ = write_report(rp, &path, &c, &set, None, 0.0, "MALFORMED");
        }
        return ExitCode::from(2);
    }

    let set = bb::Settings {
        depth: args.depth,
        split: args.split,
        nodes: args.nodes,
        jobs: args.jobs,
        survey: args.survey,
        faildump: args.faildump,
        probe_stride: args.probe_stride,
    };

    let t0 = std::time::Instant::now();
    let out = bb::verify(&c, &set);
    let wall = t0.elapsed().as_secs_f64();

    let verdict = if out.pass { "PASS" } else { "FAIL" };
    println!(
        "{}  {}  W2 = {}  threshold = {}  examined = {}  max_depth = {}  {:.3}s",
        verdict, path, c.w2, c.threshold, out.counts.pairs_examined, out.counts.max_depth, wall
    );
    if !out.pass {
        for (i, w) in out.witnesses.iter().enumerate() {
            eprintln!(
                "  witness[{}] kind={} depth={} U={} certain_mass={} deficit={}",
                i, w.kind, w.depth, w.u, w.certain_mass, w.deficit
            );
            if let Some(cf) = &w.confirm {
                eprintln!(
                    "    confirmed counterexample: sat_gap = {} mass = {} m2 = {} need = {}",
                    cf.sat_gap, cf.mass, cf.m2, cf.need
                );
            }
        }
    }

    if let Some(rp) = &args.report {
        if let Err(e) = write_report(rp, &path, &c, &set, Some(&out), wall, verdict) {
            eprintln!("could not write report {}: {}", rp, e);
        }
    }

    if out.pass {
        ExitCode::SUCCESS
    } else {
        ExitCode::from(1)
    }
}

fn place_json(p: &geom::Place) -> serde_json::Value {
    serde_json::json!({
        "t": p.t.to_string(),
        "cx": p.cx.to_string(),
        "cy": p.cy.to_string(),
        "cos": p.c().to_string(),
        "sin": p.s().to_string(),
    })
}

fn rats(v: &[Rat]) -> Vec<String> {
    v.iter().map(|r| r.to_string()).collect()
}

fn write_report(
    path: &str,
    cert_path: &str,
    c: &cert::Cert,
    set: &bb::Settings,
    out: Option<&bb::Outcome>,
    wall: f64,
    verdict: &str,
) -> std::io::Result<()> {
    let (per_file, combined) = source_hashes();
    let counts = out.map(|o| o.counts.clone()).unwrap_or_default();
    let wit: Vec<serde_json::Value> = out
        .map(|o| {
            o.witnesses
                .iter()
                .map(|w| {
                    serde_json::json!({
                        "kind": w.kind,
                        "F": rats(&w.f),
                        "Fp": rats(&w.g),
                        "depth": w.depth,
                        "U": w.u,
                        "certain_mass": w.certain_mass.to_string(),
                        "deficit": w.deficit.to_string(),
                        "sat_margins": rats(&w.sat_margins),
                        "confirm": w.confirm.as_ref().map(|cf| serde_json::json!({
                            "note": "interiors are disjoint iff sat_gap >= 0 (exact rational)",
                            "square1": place_json(&cf.p1),
                            "square2": place_json(&cf.p2),
                            "sat_gap": cf.sat_gap.to_string(),
                            "collected_mass": cf.mass.to_string(),
                            "m2": cf.m2,
                            "required": cf.need.to_string(),
                        })),
                    })
                })
                .collect()
        })
        .unwrap_or_default();

    let n_definitive = out
        .map(|o| o.witnesses.iter().filter(|w| w.kind == "definitive").count())
        .unwrap_or(0);
    let n_cap = out
        .map(|o| o.witnesses.iter().filter(|w| w.kind == "cap").count())
        .unwrap_or(0);

    let v = serde_json::json!({
        "certificate": cert_path,
        "verifier": "verify_pair2 (Rust)",
        "verifier_impl": "attempts/A73-pair-v2/code/verify_pair2_rs",
        "verifier_sha256": combined,
        "verifier_sources": per_file.iter().map(|(n, h)| serde_json::json!({"file": n, "sha256": h})).collect::<Vec<_>>(),
        "format": c.format,
        "s": c.s.to_string(),
        "n": c.n,
        "k": c.k,
        "m": c.m,
        "N": c.n - c.k,
        "beta": c.beta.to_string(),
        "W2": c.w2.to_string(),
        "threshold": c.threshold.to_string(),
        "p1_prime_ok": c.w2.lt(&c.threshold),
        "coincident_atoms": c.coincident,
        "settings": {
            "depth": set.depth,
            "split": set.split,
            "nodes": if set.nodes == u64::MAX { serde_json::Value::Null } else { serde_json::json!(set.nodes) },
            "jobs": set.jobs,
            "survey": set.survey,
            "probe_stride": set.probe_stride,
            "arithmetic": "exact i128 with overflow-checked BigInt promotion",
            "hinted": c.hints.is_some(),
        },
        "counts": {
            "pairs_root": counts.pairs_root,
            "pairs_examined": counts.pairs_examined,
            "vacuous": counts.vacuous,
            "vacuous_contain": counts.vacuous_contain,
            "exempt_core": counts.exempt_core,
            "nondisjoint": counts.nondisjoint,
            "covered": counts.covered,
            "covered_f": counts.covered_f,
            "split": counts.split,
            "hint_misses": counts.hint_misses,
            "max_depth": counts.max_depth,
            "deficient_early": counts.deficient_early,
        },
        "witness_kinds": { "definitive": n_definitive, "cap": n_cap },
        "verdict": verdict,
        "wall_seconds": wall,
        "witnesses": wit,
    });
    std::fs::write(path, serde_json::to_string_pretty(&v).unwrap())
}
