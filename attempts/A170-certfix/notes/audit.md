# A170 §1 — the AUDIT: which emission lanes carry stock cores, measured on every certificate on disk

Method (`code/scan170.py`, results `results/scan170.json` + `results/scan170_sub.json`): for **every**
`case-measure-certificate-v1` file under `attempts/*/certs/` and `attempts/*/certs/*/`, read the cores
the certificate carries **together with the box each core carries**, and recompute both

* the STOCK half-side `caselp.Box.core().a` — what `Hyp.from_json` rebuilds inside
  `caselp.make_certificate`, and
* the EXACT half-side `exactcore.exact_a(box)` — what A135 certifies and what an `ExactHyp` LP's row
  filter (`Hyp.ok_many`) actually used.

3,378 certificates were classified (`exact` = every carried `a` equals the exact `a`; `stock` = every
carried `a` equals the stock `a`; `mixed` = neither uniformly). This is an empirical test of the
emitted file, not a reading of intent, and it agrees with the code reading in every lane.

## The table

| lane | emitter | file : line | cores written | FAIL certs | verdict |
|---|---|---|---|---|---|
| **A135** polycore-verifier | own `emit135.make_cert` (a copy of `caselp.make_certificate` that takes the LIVE `Hyp`) | `attempts/A135-polycore-verifier/code/emit135.py:93`, cores at `:119`; `ExactHyp` at `:61`, exact core installed at `:83` | **exact** 3/4 (1 `mixed` = the poly arm's extra clause) | 0 | **NOT AFFECTED** |
| **A137** night re-emission | `emit135.make_cert` via `node137.py:50` | `attempts/A137-night-shift-2/code/node137.py:50` → `emit135.py:201` | **exact 241/241** | 44 | **NOT AFFECTED** |
| **A140** exact-core arm | own `make_cert(res, cores, …)` (cores passed in) | `attempts/A140-k0-residue-gallery/code/exactcore140.py:72`, call at `:204`, `ExactHyp` at `:56` | **exact** (1 cert, PASS) | 0 | **NOT AFFECTED** |
| **A145** impossible-weight | `emit135.make_cert` | `attempts/A145-impossible-weight/code/resolve145.py:154` | **exact 18/18** | 9 | **NOT AFFECTED** |
| **A149** a57 lane (`__exall`) | `emit135.make_cert` via A137's `node137.py` verbatim | `attempts/A149-a57-reprice/code/run149.py:259` → `node137.py:50` | **exact 137/137** | 43 | **NOT AFFECTED** |
| **A149** a60 lane (`__exH`) | `emit135.make_cert` | `attempts/A149-a57-reprice/code/node_a60.py:123`, exact H core at `:64` | **mixed 96/96 by design** — H exact, pins keep the corpus core (`node_a60.py:10-14`) | 14 | **NOT AFFECTED** (see §Metadata) |
| **A156** day-shift | `emit135.make_cert` via `node137.py` verbatim | `attempts/A156-day-shift/code/run156.py:212` → `node137.py:50` | **exact 302/302** | 31 (+1 `v3_candidates156.jsonl` row, the same node) | **NOT AFFECTED** |
| **A150** four-corner-product | `caselp.make_certificate` (A150's `lp150.py` driver) | `attempts/A57-shadow-trees/code/caselp.py:384` | **stock 9/9** while the LP ran on `ExactHyp` | 5 | **AFFECTED** |
| **A165** cascade `l1_104` | `caselp.make_certificate` — `lp5165.py` imports A150's driver (`lp5165.py:49`) and states the LP runs "on A135's certified EXACT axis cores" (`lp5165.py:3`) | same | **stock 4/4** | 3 | **AFFECTED** |
| **A166** nearest-corner-subtree | `caselp.make_certificate` before the fix; `lp166.certify` after it | `attempts/A166-nearest-corner-subtree/code/lp166.py:130-138` (fixed in place) | **stock 20 (pre-fix) / exact 25 (post-fix)** | 17 | **AFFECTED, already repaired in its own lane** |
| **A158** slot-split | `emit135`-family | — | **exact 2/2** | 0 | NOT AFFECTED |
| **A168** cascade-fable (live) | `caselp.make_certificate` **plus the A166 patch inline** | `attempts/A168-cascade-fable/code/lp168.py:86-88` | exact | — | **already carries the fix** |

**Headline.** The `Hyp.from_json` reversion reaches exactly the lanes that call
`caselp.make_certificate` (or `caselp92.make_certificate`) *directly* with an `ExactHyp`: **A150,
A165, A166**. Every lane that goes through A135's `emit135.make_cert` is clean, because that function
exists precisely to avoid the round-trip — its docstring (`emit135.py:94-100`) names this bug as the
reason the copy was written. So the brief's premise "A149 patches the cores after emission" is not
what happened: A149's cores were **born exact**, they were never stock.

## Counts

Over all 3,378 certificates (`kind` × recorded frozen-verifier verdict):

| | PASS | FAIL | no verdict |
|---|---|---|---|
| `exact` cores | 593 | 127 | 8 |
| `mixed` | 82 | 14 | 16 |
| `stock` | 1,581 | 401 | 319 |

Of the 401 stock-cored FAILs, only **36** sit in an `ExactHyp` lane and are therefore genuine victims
of the reversion: A150 5, A165 3, A166 17, A57's own `certs/` 9 (of which 2 fail on
`total ≥ budget`, which no core can repair), plus 2 in `A57/certs/epsgeo`. The other 365 are
certificates whose LP genuinely used the stock cores — for them the exact core is not a *repair*, it
is a free *upgrade*. §2 measures what that buys, and it is not nothing: **34 of A59/A60's zero-atom
VACUITY certificates flip FAIL → PASS**, because a vacuity certificate's entire content is "every
admissible square is exempt", so a wider certified core is exactly the lever. Total recovery **59
certificates, 59/59 independently re-checked**: 25 repairs in the three `ExactHyp` lanes and 34
upgrades on A59/A60's ladder.

## Metadata gap found in passing (cosmetic, not soundness)

`attempts/A149-a57-reprice/code/node_a60.py:64` mutates `hyp.cores` on a plain `caselp.Hyp`, which has
no `.scope` / `.a_report` attributes, so `emit135.make_cert`'s `getattr(hyp, "scope", "stock")`
(`emit135.py:133`) writes `provenance.core_scope = "stock"` and `cores_exact = null` on **all 95**
`certs/a60/*__exH.json` certificates — even though the H core in them **is** exact. The true
`a_report` survives in the lane's jsonl and in `results/superseded_by_exactcore_a60_A149.jsonl`. No
certificate is wrong; only its provenance line is. A170's scan classifies these `mixed` from the
numbers, not from the provenance string, which is why it did not inherit the mislabel.

## Why the exact core can be substituted into ANY certificate

`exactcore.exact_a` returns the largest half-side on a rational grid whose four corners pass A132's
exact rational vertex test against **every** pose of the box, i.e. it certifies `K(B) ⊆ Q(p)` for all
`p ∈ B`. A packing square distinct from the conditioned one is interior-disjoint from the conditioned
square, hence from its core, so exempting placements that meet the *exact* core is legitimate whatever
the LP did. Enlarging a certified core only **removes** verification obligations, so the substitution
can turn FAIL into PASS and never the reverse — and an old PASS was already sound, because the buggy
certificate made a *stronger* claim than the LP proved. `code/certwrap170.py` therefore never shrinks
a core (`a_new = a_exact` only when `a_exact > a_carried`) and refuses the substitution unless the
vertex test reports `cert_ok` and `(kx, ky, tm)` are unchanged.
