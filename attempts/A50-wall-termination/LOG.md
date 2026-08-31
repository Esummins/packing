# A50 LOG

2026-08-31 (Fable lead)
- Context loaded: A49 report + flush-acquisition map, A48 cascade_theory C1-C6',
  A47 T1 + theory notes, structure_lemmas L6/L7, A46 w1_theory, A43 span-identity
  conventions, Trump certificate (exact tilt t = 194075/530594).
- Recon (float, design only): at Trump's exact tilt 5 cos theta_T misses 191/50 by
  ~2.6e-6 (exact-arithmetic stress case); equal-class monotone menu excludes ~6 deg
  of (0,45], including a near-flush interval (0, ~1.75 deg). All table boundaries are
  roots of rational quadratics in t = tan(theta/2) => table computable EXACTLY (no
  grid): finite union of intervals with quadratic-surd endpoints.
- notes/span_semigroup.md written: P-chain definition, step ledger S1, quantization
  S2, window gap S3 (window = [191/50, s0] exactly, zero end offsets, derived),
  variants V1 (window-class + near-flush theta*), V2 (signed), E1 (mixed-normal),
  hypothesis labels H-MONO, H-L6CAP; canaries C1-C4 specified.
- Opus compute worker launched (span_table.py + canary_span.py + checker_span.py,
  corruption-gated, all exact rational). One background agent; no heavy compute.
- notes/wall_termination.md written: T2.1 near-flush wall-termination exclusion
  (theta*), T2.2 tilt pinning, T2.3 overdetermination theorem (branch (i) CC-pinned
  presser proved; branch (ii) free presser = GAP A50-G1 with 3 routes), T2.4 collapse
  mechanism interpretation of the A49 map.
- Lead spot-checks done (notes/verification_log.md): theta* corrected to 1.7347 deg; Trump spine residuals exact -5287/5e10 both spines; s* membership exact. Waiter armed on results/.
- Worker returned clean: table exact (8 gaps, 5.982138 deg excluded at L<=6; L<=8
  column 5.426659), theta* = 1.7346504 deg sharp, near-flush audit 0 hits over all
  multisets incl. E1; canaries 4/4; checker gate PASS 5/5; runtime ~6 s.
- E1 finding: one mixed-normal link dissolves all interior gaps (admitted =
  [theta*, 45]) — near-flush gap is the only rigidity-robust exclusion. V2 keeps
  3.747 deg incl. gaps 6,7 verbatim.
- Canary datum: theta_T admitted via (0,6,0) six sin-steps; 5 cos theta_T misses
  lo by exactly 42003301/15959754923050.
- Post-compute addenda written into both notes; results/a50_report.md finalized;
  REGISTRY row closed (done-mixed). A29 untouched; 1 background agent total, no
  heavy processes.
