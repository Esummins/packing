//! Throughput benchmark. Not on any verdict path.
//!
//! Regimes measured (A73 T2 brief):
//!   (A) synthetic, ~3000 atoms + 3 cores, 6-digit denominators, DENSE packing — every
//!       node carries a large certain-membership shortlist, so Lemma M dominates.
//!   (A2) the same certificate at a realistic atom density.
//!   (B) toy corpus `pair_toy_s199.json` at a large root grid — NONDISJOINT-heavy,
//!       no atoms, exercising the rational interval machinery.
//!
//! All regimes run with `--survey` and a hard `--nodes` budget, so the node count is
//! fixed regardless of verdict, and with DEFICIENT-EARLY off, so the figure measures the
//! branch-and-bound rather than how fast a refutable certificate is refuted.

use crate::bb;
use crate::cert;
use serde_json::json;

/// Synthetic certificate: `n_side^2` atoms on a rational grid with 6-digit denominators,
/// 3 axis cores, inside a container of side `side`.
pub fn synth_cert(side: i64, n_side: i64, step_micro: i64) -> String {
    const DEN: i64 = 1_000_000;
    let mut atoms = String::from("[");
    for i in 0..n_side {
        for j in 0..n_side {
            let px = 1_500_000 + i * step_micro;
            let py = 1_500_000 + j * step_micro;
            let qx = px + 3_100_007;
            let qy = py + 3_100_007;
            if i != 0 || j != 0 {
                atoms.push(',');
            }
            atoms.push_str(&format!(
                r#"{{"px":"{}/{}","py":"{}/{}","qx":"{}/{}","qy":"{}/{}","w":"1/16"}}"#,
                px, DEN, py, DEN, qx, DEN, qy, DEN
            ));
        }
    }
    atoms.push(']');
    let c = side * 1_000_000 / 2;
    format!(
        r#"{{"format":"pair-certificate-v2","s":"{}","n":90,"k":3,"m":0,"beta":"0",
"cores":[{{"kx":"{}/1000000","ky":"{}/1000000","a":"3/8"}},
         {{"kx":"{}/1000000","ky":"{}/1000000","a":"5/16"}},
         {{"kx":"{}/1000000","ky":"{}/1000000","a":"5/16"}}],
"boxes":[],
"atoms":{},
"provenance":{{"purpose":"A73 T2 Rust throughput benchmark (synthetic; not a real claim)"}}}}"#,
        side,
        c + 1,
        c + 1,
        c / 2 + 3,
        c * 3 / 2 + 2,
        c * 3 / 2 + 2,
        c / 2 + 3,
        atoms
    )
}

pub fn emit_to(path: &str) -> Result<usize, String> {
    let src = synth_cert(12, 55, 170_003);
    let c = cert::load(src.as_bytes(), path).map_err(|e| e.to_string())?;
    std::fs::write(path, &src).map_err(|e| e.to_string())?;
    Ok(c.atoms.len())
}

struct Bench {
    name: String,
    note: String,
    nodes: u64,
    seconds: f64,
    rate: f64,
    counts: bb::Counts,
    atoms: usize,
    verdict: String,
}

fn time_cert(
    name: &str,
    note: &str,
    src: &[u8],
    label: &str,
    set: &bb::Settings,
) -> Result<Bench, String> {
    let c = cert::load(src, label).map_err(|e| e.to_string())?;
    let t0 = std::time::Instant::now();
    let out = bb::verify(&c, set);
    let secs = t0.elapsed().as_secs_f64();
    Ok(Bench {
        name: name.to_string(),
        note: note.to_string(),
        nodes: out.nodes,
        seconds: secs,
        rate: if secs > 0.0 {
            out.nodes as f64 / secs
        } else {
            0.0
        },
        counts: out.counts,
        atoms: c.atoms.len(),
        verdict: if out.pass { "PASS".into() } else { "FAIL".into() },
    })
}

fn bench_json(b: &Bench) -> serde_json::Value {
    json!({
        "regime": b.name,
        "note": b.note,
        "atoms": b.atoms,
        "nodes_examined": b.nodes,
        "wall_seconds": b.seconds,
        "nodes_per_second": b.rate,
        "verdict": b.verdict,
        "counts": {
            "pairs_root": b.counts.pairs_root,
            "pairs_examined": b.counts.pairs_examined,
            "vacuous": b.counts.vacuous,
            "exempt_core": b.counts.exempt_core,
            "nondisjoint": b.counts.nondisjoint,
            "covered": b.counts.covered,
            "covered_f": b.counts.covered_f,
            "split": b.counts.split,
            "max_depth": b.counts.max_depth,
        }
    })
}

pub fn run() -> Result<String, String> {
    const BUDGET: u64 = 1_200_000;
    let base = bb::Settings {
        depth: 40,
        split: 2,
        nodes: BUDGET,
        jobs: 1,
        survey: true,
        faildump: 1,
        probe_stride: 0,
        ..Default::default()
    };
    let mut results = Vec::new();

    // (A) dense synthetic: ~35 atom endpoints per unit area.
    let dense = synth_cert(12, 55, 170_003);
    results.push(time_cert(
        "synthetic_atoms_dense",
        "3025 atoms at 0.17 spacing in a side-12 container (~35 endpoints/unit^2); \
         every node carries a large certain-membership shortlist, so exact Lemma M \
         evaluation dominates",
        dense.as_bytes(),
        "synthetic-dense",
        &base,
    )?);

    // (A2) same atom count spread at a realistic density.
    let sparse = synth_cert(28, 55, 460_000);
    results.push(time_cert(
        "synthetic_atoms_realistic",
        "3025 atoms at 0.46 spacing in a side-28 container (~4.7 endpoints/unit^2)",
        sparse.as_bytes(),
        "synthetic-sparse",
        &base,
    )?);

    // (B) toy corpus at a large root grid.
    let corpus = [
        "attempts/A66-corners4-pair/certs/pair_toy_s199.json",
        "../A66-corners4-pair/certs/pair_toy_s199.json",
        "../../A66-corners4-pair/certs/pair_toy_s199.json",
        "../../../A66-corners4-pair/certs/pair_toy_s199.json",
        "../../../../attempts/A66-corners4-pair/certs/pair_toy_s199.json",
    ]
    .iter()
    .map(std::path::PathBuf::from)
    .find(|p| p.exists());

    if let Some(p) = corpus {
        let raw = std::fs::read(&p).map_err(|e| e.to_string())?;
        let set_b = bb::Settings {
            depth: 48,
            split: 5,
            ..base.clone()
        };
        results.push(time_cert(
            "toy_corpus_s199_split5",
            "pair_toy_s199 at a 32x32 root grid: no atoms, NONDISJOINT-heavy, exercising \
             the exact rational interval enclosures",
            &raw,
            &p.to_string_lossy(),
            &set_b,
        )?);
    }

    // Repeat the atom-bearing regimes multi-threaded (root pairs are independent).
    let jobs = std::thread::available_parallelism()
        .map(|n| n.get().min(8))
        .unwrap_or(1);
    if jobs > 1 {
        let par = bb::Settings { jobs, ..base.clone() };
        results.push(time_cert(
            "synthetic_atoms_dense_parallel",
            "as synthetic_atoms_dense, multi-threaded over root pairs",
            dense.as_bytes(),
            "synthetic-dense-par",
            &par,
        )?);
        results.push(time_cert(
            "synthetic_atoms_realistic_parallel",
            "as synthetic_atoms_realistic, multi-threaded over root pairs",
            sparse.as_bytes(),
            "synthetic-sparse-par",
            &par,
        )?);
    }

    let min_rate = results.iter().map(|b| b.rate).fold(f64::INFINITY, f64::min);
    let max_rate = results.iter().map(|b| b.rate).fold(0.0f64, f64::max);
    let target = 100_000.0;

    let v = json!({
        "benchmark": "A73 T2 verify_pair2 (Rust) throughput",
        "host_target": "x86_64-pc-windows-gnu",
        "profile": "release (opt-level 3, lto, codegen-units 1)",
        "threads_used_for_parallel_regimes": std::thread::available_parallelism().map(|n| n.get().min(8)).unwrap_or(1),
        "arithmetic": "exact i128 fast path with overflow-checked BigInt promotion",
        "node_budget_per_regime": BUDGET,
        "target_nodes_per_second": target,
        "regimes": results.iter().map(bench_json).collect::<Vec<_>>(),
        "min_nodes_per_second": min_rate,
        "max_nodes_per_second": max_rate,
        "meets_target_all_regimes": min_rate >= target,
        "meets_target_any_regime": max_rate >= target,
        "note": "A node is one pair box examined (`pairs_examined`). Rate in the \
                 atom-bearing regimes is governed by how many atoms fall in a node's \
                 certain-membership shortlist, which is why density is reported \
                 alongside each figure.",
    });
    Ok(serde_json::to_string_pretty(&v).unwrap())
}
