# A131 T4 — deployment shape for the pin-clip (T5‴). NOT DEPLOYED.

One page, as briefed. Nothing in this attempt edits `tree57.py`, `trim57.py`, `pinguard.py`,
`caselp.py` or any verifier; the clipper is `attempts/A131-pin-clip/code/pinclip.py` and is
imported by nothing outside this attempt.

## 1. Where in emission the clip applies

`tree57.build_children` produces, per parent, a list of `(kind, box, budget)` children. The order
of the emission-time screens is today

```
    build_children
      -> pinguard.classify(box, pin_boxes, pin_slots)      # T5 parent / T5' contradictory
      -> trim57.trim_box(box, slots)                       # T5''  (tilt sub-intervals)
      -> LP  (caselp.solve_node) -> certify.py -> verify_case.py
```

The clip goes **after T5″ and before the LP**, on each surviving trimmed sub-box:

```
      -> pinguard.classify(...)                            # UNCHANGED, and it must stay FIRST
      -> trim57.trim_box(...)               -> [(sub-box, tilt sub-bin)]
      -> pinclip.clip_node(sub-box, slots)  -> clipped centre rect per sub-bin, or EMPTY
      -> LP on the clipped box
```

Three ordering facts, all load-bearing:

* **`pinguard.classify` must run first.** The clip's justification is "Q(c, θ) meets pin core K_i,
  and Q is not that pin, so the hypotheses are contradictory". The second clause fails exactly in
  pinguard's `parent` case (a pin placement `(px, py, 0°)` inside the box, remembering θ = 90 is
  the same square as θ = 0). `pinclip.clip_node` carries its own `realizes_pin` guard and refuses
  such a node outright (`refused=True, reason="parent"`), so the rule is safe even if the order is
  changed; A57's interior census has zero parent boxes, so it never fires there, but the protected
  tier has zones that contain pins and it will.
* **The clip subsumes T5″ but does not replace it.** Measured on the 1,744 open boxes of the
  corpus: every one of the 159 boxes T5″ empties, the clip also empties (0 lost), and the clip
  empties 21 more. But T5″ *also* narrows the tilt bin, which the clip does not; the two are
  complementary and both should run.
* **The clip is idempotent and monotone in the sub-bin count**: clipping an already-clipped box
  changes nothing, and finer sub-bins clip at least as much (conservatism (b) of `pinclip.py` is
  gone, but each sub-bin's *union over tilts* of admissible centres is smaller the narrower the
  sub-bin). `nsub = 1` already captures the bulk (12.10 % of open nodes vs 12.96 % at `nsub = 8`,
  in the schedule model of `notes/measurement.md`); `nsub = 1` is the recommended default because
  it keeps ONE child per trimmed bin and therefore one certificate per node.

## 2. Record fields — PERSISTED, unlike `trim_excluded`

A123's MUST-FIX (PAUSED.md v2 §6) is that `trim_excluded` / `trim_from` are built in
`build_children` and never written to disk, so the commonest T5″ outcome leaves *no marker at all*
and had to be recovered geometrically from the θ-width. The clip must not repeat that. On every
emitted child record (`rec` in `tree57.py`, i.e. the `.jsonl` row):

| field | type | meaning |
|---|---|---|
| `clip_from` | box json or `null` | the centre box **before** the clip (`null` = untouched) |
| `clip_kept` | float | kept centre-area fraction, `area(clipped)/area(clip_from)` |
| `clip_nsub` | int | sub-bin count used (1 in the recommended default) |
| `clip_pins` | list[int] | indices of the pins that actually removed a slab (the witnesses) |
| `clip_delta` | str | the pin slack the clip was computed at (`"1/100"`) — the clip is only valid for the `a_P` it was computed with |
| `pin_info` | `"clip"` | on a FULL kill, exactly as T5″ uses `"trim"` |

One implementation detail that belongs in the record, not in a comment: `pinclip.clip_node` works
on the rational **outer** box (endpoints rounded outward onto the 10⁻⁹ grid) so that "dead on the
whole slab" is proved for a superset of the true box. Its output can therefore sit 10⁻⁹ *outside*
the original box on an untouched side. The emitted child box must be
`clipped ∩ original` — sound (the intersection only drops centres the node never hypothesised) and
it keeps the emitted coordinates on the cover's own grid.

`clip_from` + the box on the record makes the coverage claim auditable from the results alone —
"original box = clipped box ∪ (dead region, witnessed by pins `clip_pins`)" — which is what §6 of
PAUSED.md says the T5″ ledger should have been. `clip_kept == 1.0` is the "untouched" marker, so a
single-piece clip is visible without the θ-width reconstruction trick.

## 3. Verifier implications — none

A clipped child is an **ordinary, smaller centre box**. Its core `Box.core()` is computed from the
smaller box, its certificate is the ordinary `case-measure-certificate-v1`, and
`verify_case.py` / `verify_param.py` / `verify_param_v2.py` see nothing new. No new leaf kind, no
new exemption clause, no change to the frozen chain — exactly T5″'s situation (lemmas.md T5″:
"the trimmed child is a SUB-BOX, so its certificate is the ordinary one").

Two second-order effects, both favourable and both worth measuring at deployment:

* the clipped box's `Box.core()` is **larger** (half-side `a = (1/2 − h_d)/(1 + (t1 − t0))` with a
  smaller half-diagonal `h_d`) — measured over the 349 touched boxes at `nsub = 1`, `a_new/a_old`
  runs **1.0007 – 1.2453, median 1.0449**, the same shape as A96's
  `a_tight_gain_on_trimmed_bin`. **It buys nothing extra**: re-running `pinguard.classify` with the
  tight core on the clipped boxes yields **0** additional logic kills. The clip's kill power is
  fully expressed by the clip itself; do not expect a second harvest from re-applying T5′ after it;
* a smaller core box exempts fewer LP rows, so `τ` can only rise; the clip cannot make a node
  *harder* to kill in the LP's own terms, only in the columns it needs.

### 3a. What a certificate on a clipped box actually proves

A PASS on the clipped box is a frozen-verifier proof of "no packing satisfies (pins + CLIPPED
box)". The node's statement is "no packing satisfies (pins + ORIGINAL box)", and getting from one
to the other needs the pin-clip lemma for the discarded part:

    original box  =  clipped box  ∪  (discarded region, dead by T5‴)

So **every kill obtained on a clipped box is a two-part argument**: the frozen certificate, plus
one T5‴ leaf per discarded slab. That is exactly T5″'s situation ("node == trimmed child(ren) +
k excluded tilt intervals", lemmas.md), and exactly why the leaf must be persisted (§2) and
formalised (§4). Until the leaf is in Lean, a clip-based kill sits at the same level of rigour as
a T5″-trimmed kill: sound by an argument on file, machine-checked only in its certificate half.

## 4. The Lean shape

The discarded region is a finite union, over pins, of sets of the form

    D_i(t0, t1) = { d : |d_x| < w_min/2 + a_P, |d_y| < w_min/2 + a_P,
                        max_θ (±d·u(θ) − a_P w(θ)) < 1/2,
                        max_θ (±d·v(θ) − a_P w(θ)) < 1/2 }

and each of the four `max_θ` conditions is `max over [θ0, θ1] of (P cos θ + Q sin θ) < 1/2` with
`P, Q` **affine in `d`** — a single sinusoid, whose maximum is at an endpoint or at the interior
critical point (value `√(P² + Q²)`). So the Lean obligation is a **T5-type logic leaf carrying a
tilt range and a centre sub-box**, with exactly the shape of the existing `core_meet_same_square`
(node C.T5T11) plus a range:

```
theorem pinclip_dead
    (hpin  : ∀ p ∈ pins, IsPinnedSquare p)          -- the class hypothesis
    (hnotpin : ¬ RealizesPin B pins)                -- pinguard's parent guard
    (hd   : d ∈ D i t0 t1)                          -- decidable, rational
    (hQ   : Q.centre = slot i + d ∧ Q.tilt ∈ [t0,t1])
  : ¬ (Q ∈ P ∧ InteriorDisjoint Q (pin i))
```

The arithmetic is already in the tree: A117's `tcleaf.py` needed a rational lower bound on
`(1 + cos Δ + sin Δ)/2` and used a truncated alternating Taylor series at a 50-digit π enclosure.
**The pin-clip needs none of that.** Working in `t = tan(θ/2)`, which is how A57's cover is built
(lemmas.md T2), `cos θ = (1 − t²)/(1 + t²)` and `sin θ = 2t/(1 + t²)` are exact rationals at every
sub-bin endpoint, so every quantity above — `w_min`, `A`, the four sinusoid maxima, the comparison
`√(P²+Q²) < 1/2` done as `P² + Q² < 1/4` — is a rational inequality. `pinclip.dead_q` is that
decision procedure and has no epsilon in it. The Lean leaf is therefore a `decide` over `ℚ` in the
same style as A117's TC leaf, one level simpler.

Sanity obligation for the leaf, discharged here: 674/674 of the tree's existing
"core meets pin core" kills come out EMPTY under `dead_q` at `nsub = 1`
(`results/t1_check.json`), i.e. the leaf's decision procedure dominates T5′ on the deployed corpus.

## 5. The n-general statement

> **Lemma T5‴ (pin-clip).** Let `P` be a packing of `n` pairwise interior-disjoint unit squares in
> `[0,s]²` and let a conditioning node fix `k` of them ("pins") to lie within slack boxes of
> half-width `δ/√2` about slots `p_1 … p_k`, and hypothesise a further square `Q₀` with
> `(centre, tilt) ∈ B = R × [θ₀, θ₁]`. Write `K_i` for the axis-aligned square of half-side
> `1/2 − δ` at `p_i` (contained in pin `i` wherever it sits). If no pin placement lies in `B`,
> then `B` may be replaced by `B' = (R \ ⋃_i D_i(θ₀, θ₁)) × [θ₀, θ₁]` without losing any packing,
> where `D_i(θ₀,θ₁)` is the set of centres at which the unit square at EVERY tilt in `[θ₀,θ₁]`
> meets `K_i`'s interior. The discarded centres are also those outside
> `[w_min/2, s − w_min/2]²` (container).

Nothing in that statement is about `n = 11`, about `k = 5`, or about A57's classes. It is the
**class-pin analogue of the container clip**: the container clip discards centres at which the
square leaves `[0,s]²` at every admissible tilt (`caselp.Box.vacuous` is the box-wise version of
it); the pin clip discards centres at which the square hits a *fixed* obstacle at every admissible
tilt. Any obstacle known to be occupied does the job, so the rule applies verbatim to

* every conditioning tree in the **protected tier** (15 classes, budget.md row 3, 3,800 CPU-h) —
  same box/pin geometry, and A57's measured 10.3 % outright-kill rate is the natural first estimate
  there, the same reasoning §D uses for the tight core and trimming;
* `trump5`'s residual tree;
* the **k0_00** frame residue — with the caveat that the k0 tree has *zero* pins at depth 0 and
  therefore zero clip until the first YES child is taken, which is exactly why budget.md §D item 5
  says k0 is not a compute question;
* a second conditioned square, once a node carries two boxes (A112's load-path branching): the
  clip's obstacle need only be a set contained in every admissible pose, i.e. any box's core, so
  `D` is the same octagon intersection with `a_P` replaced by the other box's core half-side. That
  is the **box-vs-forced-neighbour kill** listed third in budget.md §D item 1, and it comes free
  with this machinery.

## 6. Resume-block line for PAUSED.md

Add under §8 "Optional levers, only if wanted", and to the §6 MUST-FIX list:

> **T5‴ pin-clip (A131, measured, NOT deployed).** After `trim57.trim_box` and before the LP,
> replace each surviving centre box by `pinclip.clip_node(box, slots, nsub=1)["union_rect"]`
> (EMPTY ⇒ a logic kill, `pin_info="clip"`). Measured over the 1,744 open boxes of the corpus:
> 10.32 % clip to EMPTY (of which 21 are incremental over T5″ — and 0 of T5″'s 159 are lost),
> 26.1 % are narrowed and survive, 63.6 % untouched; median 0.71 free levels among those narrowed
> (L4: 85.7 % emptied). **Persist `clip_from`, `clip_kept`, `clip_nsub`, `clip_pins`, `clip_delta`
> on the emitted record** — do not repeat the `trim_excluded` gap of §6. Frozen verifiers unchanged
> (a clipped child is an ordinary smaller box). The clip is valid only for the `pin_delta` it was
> computed at, so re-run it if `--pin_delta` changes. `pinguard.classify` must still run first (the
> parent case).
