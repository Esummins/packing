# A170 §3 — the FIX going forward

## The wrapper

`attempts/A170-certfix/code/certwrap170.py`. `caselp.py` is **not** edited (frozen-adjacent driver);
lanes call the wrapper instead.

```python
from certwrap170 import make_certificate_exact, carry_exact_cores, run_frozen_verifier

# A150/A165/A166-style driver: replace
#     cert = make_certificate(res, S_RAT, scale=scale)
# with
cert = make_certificate_exact(res, S_RAT, scale=scale, hyp=H)   # H is the LIVE ExactHyp
```

* `make_certificate_exact(res, s_rat, scale=…, hyp=None, boxes=None)` — calls
  `caselp.make_certificate` verbatim, then carries the exact cores through. Pass `hyp` (the live
  hypothesis the LP was solved with) whenever it is in hand: then the certificate carries *exactly*
  the cores the row filter `Hyp.ok_many` used. With no `hyp`, the exact core is recomputed from the
  box each core carries, which is what lets the same call repair a certificate written months ago.
* `carry_exact_cores(cert, cores=None, boxes=None)` — the post-processing form, for a certificate
  already on disk. Returns a per-core report (`carried`, `exact`, `stock`, `applied`, `ratio`).
* `run_frozen_verifier(path, …)` — the frozen `verify_case.py`, with its sha256 asserted
  (`521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`) before every run.

Two guards make the wrapper safe to point at **any** certificate, including one whose LP genuinely
used the stock cores:

1. **A core is only ever ENLARGED.** `a_new = a_exact` only when `a_exact > a_carried`; when the
   carried core is already at least as large the certificate is left byte-identical
   (`result = NO-CHANGE`). Enlarging a *certified* core only removes verification obligations, so it
   can turn FAIL into PASS and never the reverse. A cert whose cores the LP used at a *larger*
   half-side than `exact_a` finds (an `ExactHyp` may install a core certified by a different exact
   route) keeps its own cores — that is why `cores` beats the box recompute when it is bigger.
2. **The substitution is refused** unless `exactcore.exact_a` reports `cert_ok` (the A132 rational
   vertex test passed on all four corners against every pose of the box) **and** `(kx, ky, tm)` are
   unchanged, so the core stays the same square, only wider.

Soundness of the enlargement itself: `exact_a` certifies `K(B) ⊆ Q(p)` for every pose `p ∈ B`, and a
packing square distinct from the conditioned one is interior-disjoint from the conditioned square,
hence from its core. The frozen `verify_case.py` validates whatever cores the certificate carries, so
nothing frozen changes.

## The regression test

`attempts/A170-certfix/code/test_cores170.py`, result `results/test_cores170.json`.

On **50 boxes** — 25 lifted verbatim from certificates on disk (so the test tracks the deployed
corpus) and 25 pseudo-random with a fixed seed, spanning pins (`th0 == th1 == 0`), narrow tilted
windows and wide-tilt k0 cells — it asserts three things per box:

1. `make_certificate_exact(..., hyp=…)` writes `a == exactcore.exact_a(box)`;
2. the no-`hyp` form, recomputing from the box the certificate itself carries, writes the same `a`;
3. **the guarded regression**: the *unwrapped* `caselp.make_certificate` writes `a == Box.core().a`,
   the stock core — i.e. the test fails loudly if the reversion is ever silently fixed or changed
   upstream, instead of quietly passing.

```
50/50 OK  (50 of them witness the bug the wrapper repairs: exact core strictly larger than the
stock core `make_certificate` would have written)
```

No LP is solved: `make_certificate` reads only `res["atoms_all"]`, `res["hyp"]`, `res["budget"]`,
`res["tau"]` and `res["s"]`, so a synthetic single-atom measure exercises the whole emission path.
Runtime ≈ 40 s.

## Which lanes need to change

| lane | action |
|---|---|
| A150 `lp150.py`, A165 `lp5165.py` (imports A150's driver) | switch the `make_certificate` call to `make_certificate_exact(..., hyp=H)` at resume |
| A166 `lp166.py` | already fixed inline (`lp166.py:130-138`) — no change |
| A168 `lp168.py` | already carries the patch (`lp168.py:86-88`) — no change |
| A135 `emit135.make_cert` and everything routed through it (A137, A140, A145, A149, A156) | **no change** — `emit135.make_cert` takes the live `Hyp` and was written for exactly this reason |
| any NEW lane | call `certwrap170.make_certificate_exact`, never `caselp.make_certificate` |

`caselp.py` and `caselp92.py` keep the bug. Both are frozen-adjacent and both are still correct for a
genuinely stock-core LP; the wrapper is the seam.
