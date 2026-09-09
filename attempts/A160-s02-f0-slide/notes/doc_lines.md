# A160 — the two doc lines the brief names (staged here, appended verbatim)

## `docs/budget.md` §D — one paragraph (appended after A151's)

> *A160 (`PENDING`, 2026-09-08) — the pinwheel's two extra directions, and the finding that the local
> certificate is a UNION, not a growable box:* S02's `f0` is a **rattler with a one-parameter slide** —
> the ten-square core minimises at the same 3.886746028606 to twelve digits with `f0` deleted, and
> `f0`'s admissible set there is an exact segment of **length 0.298419** along its own body axis at a
> FIXED tilt (area and width vanish linearly in the relaxation, the tilt window like its square root),
> running from a `BR(0,1)` stop to an `f1` stop with `BL(1,0)` and `f3` as rails. **`f3` is not a
> rattler** — it is the shadow's most load-bearing square (Δs\* 0.1190); the second rattler is the
> *slot* square `BR(0,0)` (slide 0.5357). Putting `f0`'s slide-cover box into `N` is a **net loss** —
> one more clause takes A151-B's 96 in-N nodes / 42 alive to **15 / 8**, recovering only when the box
> reaches ±0.50/±0.47/±45° — and the tree with `f0` as a fifth free body **caps** (wall cap at 420 s and
> still 0 witnesses / 0 unresolved at 1024 s, certified min 3.8770844 > s₀), so no `N` with `f0` was
> certified in a 4 CPU-h cap. The **common-tilt chain is cheap and works**: `s*(θ)` on the shared tilt of
> `f1 f2 f3` is above s₀ everywhere, 24 links of half-width 1.25° certify a **60.0°-wide** shared-tilt
> range at a median 7 s a link, and 4 links of half-width 10° cover **80.0°** at 55–285 s — but its
> consumer ceiling is the count of nodes whose support tilt SPREAD is ≤ 2h (**63/27 at 1.25°, 91/40 at
> 5°, 124/53 at 10°**), and of the 20 alive nodes outside A151-B **`f2`'s tilt binds 14 and `f3`'s binds
> 10, 9 by those two alone** — INDEPENDENT windows a common tilt cannot open. Slicing those windows
> instead **works and is nearly free**: with `f1` at A116's own box, **all eight axis slices certify with
> zero failures in 348 s total**, extending `f2`'s and `f3`'s tilt windows independently over the whole
> fundamental domain [−1.56°, 98.44°], and the corner slices of the 5 × 5 product certify at 2–188 s
> each. **The load-bearing discovery is that the directions TRADE OFF**: `f2`'s upward slice certifies
> at `f1`'s base box in 108 s but is **REFUTED BY A WITNESS** together with A151-B's grown `f1` (the
> witness puts `f1` at 83.44°, a pose only the ±40° window admits; side 3.869337946 < s₀, re-verified),
> and growing all four centre boxes together is refuted by witnesses at **r = 0.25 already** (certified
> at Δθ = 0 and −10°, witness at +10°; r = 0.30 witness at 0°; r = 0.40 witness everywhere) — the first
> LIVE-LOW witnesses anywhere in the A116/A151/A160 line, all ten re-verified from scratch. So
> A151's "compute-limited, not geometry-limited" holds for single knobs and **fails for compounded
> ones**, and the right object for A136's YES leaf is a `N_boxes` **LIST whose hypothesis is a
> disjunction**: A151-B ∪ the common-tilt chain ∪ the independent tilt slices reaches **114 of 184
> in-N nodes / 50 alive against A151-B's 96/42 and A116's 72/32**, for ≈ 0.9 CPU-h of tree time in 50+
> certified boxes, every refusal in the union either a wall cap (labelled) or a drawn witness.

## `docs/residue_ledger.md` §1b — one sentence (appended)

> **(7) The pinwheel's two extra directions, and why its basin is a UNION (A160
> `attempts/A160-s02-f0-slide`, after the PI's f0-slide reading and the coordinator's common-tilt
> reading):** `f0` is an exact one-parameter rattler slide of length 0.298419 along its own body axis at
> the fixed tilt 48.4351° (rails `BL(1,0)`/`f3`, stops `BR(0,1)`/`f1`; `f3` by contrast is the shadow's
> most load-bearing square, Δs\* 0.1190, and `BR(0,0)` is a second rattler at 0.5357), and the
> common-tilt chain certifies a 60–80° shared-tilt range in cheap links with every refusal labelled —
> but adding `f0` as a required box costs 96/42 → 15/8 and caps the tree, the chain's own ceiling is the
> tilt SPREAD of a node's support (63/27 at half-width 1.25°, 124/53 at 10°), and the coordinate that
> actually binds is `f2`'s and `f3`'s tilt INDEPENDENTLY (14 and 10 of the 20 alive nodes outside
> A151-B), which slices certify with zero failures in 348 s at `f1`'s base box yet a **LIVE-LOW
> witness** refutes together with A151-B's grown `f1` — so the growth directions trade off, the basin is
> a DISJUNCTION of differently shaped certified boxes, and that union reaches **114 of 184 in-N nodes,
> 50 alive**.
