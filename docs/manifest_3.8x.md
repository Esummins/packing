# Manifest: the 3.8x lower-bound certificates and their verifiers (checklist C9)

Recorded 2026-09-01 at commit **`c9980bfcda1582d1e1a20126927a8a7d34ca1bb6`**; every file
below verified **git-clean** at that commit (`git status --porcelain` empty). A reader who
checks these SHA-256 hashes is verifying the same bytes the theorems cite. Hashes computed
by A62 (`attempts/A62-trust-ledger/results/tcb_raw.md` §3 holds the raw run).

## Certificates

| claim | file | bytes | sha256 |
|---|---|---|---|
| s(11) ≥ 3.80 | `certs/measure_certificate_3.80.json` | 59684 | `d568c9bcb5add16adb9077221d6834532d59a6d2d3338f69729702841f9a5ecc` |
| s(11) ≥ 3.81 | `certs/measure_certificate_3.81.json` | 53901 | `7d220c710a550174773c2b871c2c260154ac057fbbe23760eb70b2297a277929` |
| s(11) ≥ 3.82 | `certs/measure_certificate_3.82.json` | 96398 | `10d434dd63dfd4dfef3655112674c8cc74d3c66b820a6144ce54ecd63586df80` |

## Verifier 1 — Python (exact integer/rational)

| file | bytes | sha256 |
|---|---|---|
| `certs/verify_measure.py` | 38811 | `2a735939d67f3a39a74a4bd0787df7f90d6f08b494e350bc36ae236725fa2121` |

## Verifier 2 — Lean 4 (checker + generated data)

The data files are generated from the JSON certificates by `lean/gen_measure_lean.py`;
CI (`.github/workflows/lean.yml`, packingcert job) regenerates them on every push and
diffs byte-identically, so the hash of the JSON pins the hash of the Lean data.

| file | bytes | sha256 |
|---|---|---|
| `lean/PackingCert/PackingCert/MeasureInt.lean` (the checker) | 10460 | `9c81e1807bf0cd1add3ea74a6d402a6bd909c0a60f91e60b609743266de7227f` |
| `lean/PackingCert/PackingCert/MeasureIntData.lean` (3.80) | 48304 | `3401f5d71cfbef469b5f50964675dc72c1647a9969790610724a9a885bafa986` |
| `lean/PackingCert/PackingCert/MeasureIntData381.lean` | 44081 | `7dd386517cf4df9e63e42ada44081d094e885b8ec9b2d3d55feb1b59d675025c` |
| `lean/PackingCert/PackingCert/MeasureIntData382.lean` | 77972 | `4856650ebbd2df267d97a5545ea706893778fa61b3d9499a1c0af0269654911a` |
| `lean/gen_measure_lean.py` (generator, for the CI diff) | 7924 | `a0d061cec300e988e85da6120efd90a9242e84001062baa12b541d88745ed251` |

Lean theorems: `PackingCert.MeasureI.s11_ge_3_80 / s11_ge_3_81 / s11_ge_3_82`
(`lake build PackingCertSlow{,381,382}`; axiom exactly `Lean.ofReduceBool` each — asserted
by the CI slow job).

## Upper-bound pair (for completeness of the 3.8x story)

| claim | file | bytes | sha256 |
|---|---|---|---|
| s(11) ≤ 3.877084 | `certs/trump11_certificate_int.json` | 5398 | `6505456ea2bd02c4623e2dd5aab3f2e29a1ca3954d63d4367ed98a4cde98a4d9` |
| verifier | `certs/verify_certificate.py` | 6598 | `3170bd39701455192580d1a9011b16ddbd377cf8966c19bcb975d9ae772815ce` |
| Lean checker | `lean/PackingCert/PackingCert/Checker.lean` | 3014 | `33e3c13deed94d59f96b192254401d2c405054fe038c4b45a29e1368d092c3b2` |

To re-verify a hash (PowerShell): `Get-FileHash -Algorithm SHA256 <file>`; (Linux/mac):
`shasum -a 256 <file>` / `sha256sum <file>`.
