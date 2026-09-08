# A154 T1 — (R6) exactly: the row, its soundness, its Lean shape, and what the frozen verifier can take

## 1. The row, exactly

Fix the certified side `s0 = 969271/250000 = 3.877084` and write `F = Δ_λ P` for a packing `P` of
eleven unit squares at side `m ∈ [3.82, s0]` dilated (centres only) to `s0`, `λ = s0/m ≤ λ_max =
969271/955000`. For a corner `c` let `g_c` be the D4 map sending `c` to the origin with the
container in the positive quadrant and

    mu_c(Q) = min over p in Q of max(p_x, p_y)      (corner85.f_min_max, exact)

so `Q` meets the closed box `[0,a]²` in `c`'s frame iff `mu_c(Q) ≤ a`. The **widened** corner box
is `B_c^w = [0, a_w]²` in that frame, with (Lemma K0-WIDEN, `docs/proofs/k0_route.md` §4.1)

    a_w = a_w(0) = λ_max + (λ_max − 1)/√2 = 12819/12500 = 1.025520   (exact, rounded up to 1e-5).

**(R6).** For every K0-BLOCKED packing (`k0_route.md` §3: every corner box met by ≥ 2 squares —
the complement K0-FREE is a (T) leaf by `teleport_packing`, consuming k1_00, obligation K0-O1),

    sum over the eleven squares Q of  [ mu_c(Q) ≤ a_w for some corner c ]   ≥   8 .

**Soundness.** Two facts and one count.

* *(i) Separation.* `s0 − 2 a_w = 3.877084 − 2·1.025520 = 1.826044 > √2 = diam(unit square)`, so a
  unit square whose closure meets two of the four widened corner boxes would have diameter `> √2`.
  Hence each square carries **at most one** corner incidence — `r_G(Q) ∈ {0,1}` (CC-1(ii) with the
  widening, `k0_route.md` §4.2). This is A150 (R6)(i) and it is what makes the count exact.
* *(ii) Blockedness.* Each of the four corners contributes ≥ 2 distinct squares (K0-BLOCKED), and
  by (i) the four contributing families are pairwise disjoint. Summing: ≥ 8 distinct squares.
* Therefore ≤ 3 of the eleven squares are free of all four corner boxes, and the incidence sum is
  ≥ 8. ∎

**The conditioned squares are counted on the left.** At a node of the k0 tree with `k` conditioned
boxes `B_1..B_k` the LP pays only for `budget0 = 11 − k` squares; a conditioned square is one of
the eleven and may itself be one of the eight, so the row that the LP can use is

    sum over the (11 − k) NON-conditioned squares of [meets some B_c^w]  ≥  B,
    B = 8 − Σ_{j=1..k} r_max(B_j⁺),        r_max ∈ {0,1} by (i),

where `B_j⁺` is the (over-)set of poses of a unit square CONTAINING the caselp core `K(B_j)`
(`a115lib.core_plus`: `a(cos D + sin D) ≤ 1/2` and `|k − q| ≤ √2(1/2 − a)`) and `r_max(B_j⁺)` is
the max of the dilated corner test over a ≤ 0.01 / 0.5° grid of `B_j⁺` with the sample half-cell
added to the zone tolerance — so it can only OVER-count, the sound direction. In this corpus
`B ∈ {7, 8}` at every k0 node.

## 2. How the row enters the case-LP (there is no `x_p` in it)

The k0 node LP is the MEASURE LP, not a placement LP: it minimises `mu(total)` over atomic
measures subject to `mu(Q) ≥ 1` for every admissible pose `Q` disjoint from the cores, and a node
dies when `τ = min mu(total) < budget0`. A counting row on the squares is therefore imposed as a
**right-hand-side lift plus a budget bonus** (Lemma CW, `docs/proofs/k0_blocked_side.md` §2.4; the
engine hook is `lpbox92.RHS_MULT`, A92's single engine change):

    rhs(Q) = 1 + e · [ Q ∈ G(a_w) ]          (G ⊇ ∪_c F_c(a_w), the dilated outer cover)
    budget = budget0 + floor(e · B)
    KILL   iff  τ(e) < budget.

Composition (why this is the row): every non-conditioned square `Q_i` of a K0-BLOCKED packing has
`mu(Q_i) ≥ 1`, and ≥ B of them have `mu(Q_i) ≥ 1 + e`; summing, `mu(total) ≥ (11 − k) + eB >
τ(e)` — a contradiction. Because `r_max ≤ 1` by (i), the same measure `mu` needs only **two**
levels (`1` and `1 + e`), i.e. `r_max = 1` in A94's `1 + r_max`-run scheme.

**This is exactly A115's `d0` configuration, not a new row.** `attempts/A115-k0-corner-rows/
notes/method.md` states it verbatim (`rhs(Q) = 1 + e·[Q ∈ G]`, `budget = budget0 + floor(eB)`,
`B = 8 − Σ r_max`, and the same `s0 − 2a_w = 1.826 > √2` separation paragraph as the reason the
budget is exact). **A150 §6 item 1 is wrong on one point of record**: it contrasts (R6) with "the
four separate `≥ 2` rows A115 tried". A115 ran the single aggregate weight-8 row. And the contrast
would run the other way in any case: in LP terms four per-corner rows `Σ_{Q meets B_c^w} ≥ 2` (four
independent `e_c`) DOMINATE their sum `Σ_c` — the aggregate is the diagonal `e_1 = … = e_4` of the
four-parameter family, so (R6) is **weaker than or equal to** what A115 measured, never stronger.

## 3. The decision rule, and the zero-cost screen A154 adds

`τ(e) = max { (b + e·a)'y : A'y ≤ 1, y ≥ 0 }` is a maximum of affine functions of `e`, hence convex
and non-decreasing, and **any** optimal dual `y*` at `e = 0` supplies a subgradient:

    τ(e)  ≥  τ0 + e · c,     c := Σ_Q a_Q y*_Q   (the corner incidence the fractional packing realises)
    η(e)  =  τ(e) − budget0 − floor(eB)  ≥  η0 + e(c − B).

**So `c ≥ B` at any stored optimal dual of a CONVERGED node LP is a proof that (R6) cannot lower
that node's `η` at any `e > 0`.** No LP is needed; the stored `packing` array of the node's own
record decides it. `c < B` is inconclusive (a different optimum on the same face, or the
re-optimised dual at `e > 0`, may realise more) and needs the LP — and in this corpus it always
does realise more (§ report). The screen is exact: `c` is computed with the exact functional
`mu_c ≤ a_w` while the LP's rhs uses the DILATED cover `G ⊇ ∪_c F_c(a_w)`, so the LP's own `c` is
`≥` the screened one and the "PROVED-USELESS" direction is conservative.

## 4. Lean shape

Against `docs/proofs/k0_route.md` and `k0_blocked_side.md` §2.4, (R6) needs no new geometry beyond
what K0-WIDEN already carries:

```lean
-- the corner-meeting predicate (exact; corner85.f_min_max is `muCorner`)
def MeetsCorner (s aw : ℝ) (Q : Square) : Prop := ∃ c : Corner, muCorner s c Q ≤ aw

-- (i) SEPARATION: no unit square meets two widened corner boxes
theorem corner_boxes_separated (h : s - 2*aw > Real.sqrt 2) :
    ∀ Q : Square, ∀ c d : Corner, c ≠ d →
      ¬ (muCorner s c Q ≤ aw ∧ muCorner s d Q ≤ aw)

-- (ii) the row itself, on the K0-BLOCKED branch
theorem R6_row (P : Packing 11 s) (hB : K0Blocked s aw P) :
    8 ≤ (Finset.univ.filter (fun i => MeetsCorner s aw (P.sq i))).card
```
Obligations: `K0Blocked` is `k0_route.md` §3's dichotomy (already the k0 tree's standing
hypothesis; open obligation **K0-O1**, k1_00's tree), `K0Widen` gives `aw = a_w(0)` for the whole
window, and `corner_boxes_separated` is one `Real.sqrt 2 < 1.826` numeric fact plus the diameter
bound `diam Q = √2`. The consuming certificate lemma is `crowd_sound`'s corner instance
(`k0_blocked_side.md` §2.4, A93): from `R6_row` plus two verifier PASSes,
`mu(total) ≥ (11 − k) + eB > τ`, contradiction. **No new Lean object is needed for (R6) that
`K0Widen` + `teleport_packing` do not already provide** — which is exactly why the row was
already available to A115.

## 5. What `verify_case.py` needs: nothing (and it has been exercised)

The FROZEN verifier (sha256 `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`)
has **no counting clause and needs none**. It checks three things: `budget == n − #cores` (a hard
assertion, line 714), `total < budget`, and `mu(Q) ≥ 1 + margin` for every admissible non-exempt
`Q` — with `--strict-margin m` (line 821) supplying the margin and `hypotheses.nofams` (line 711)
supplying an exempt cover. Those two options are exactly the `1 + r_max`-run composition A92/A94
built and A109/A115 ran:

| run | file | `n`, `budget` | cores | nofams | margin | certifies |
|---|---|---|---|---|---|---|
| **A** | `runA_<tag>.json` | `n = 11 + eB`, `budget = n − #cores` | the node's cores | — | 0 | `mu(Q) ≥ 1` off the cores and `mu(total) < budget0 + eB` |
| **B₁** | `runB1_<tag>.json` | dummy `n = budget = 1000` | — | `E` = an exactly-certified cover of the COMPLEMENT of `∪_c F_c(a_w)` | `e` (or weights ÷ (1+e)) | `mu(Q) ≥ 1 + e` for every `Q` not provably outside the corner family |

and because (R6)'s `r_max = 1` (separation, §1(i)) the scheme needs exactly **two** runs — the
minimum possible. `e` must make `eB` an integer (`budget` is an `int` in the schema), so `e = 1/B`
with `B ∈ {7,8}` and bonus 1, which is what A115 and A154 both run.

**So there is no "v4-type counting clause" to build.** What is not free is the second run: `E` is a
*sound inner cover of the complement*, and the exactness of that cover is the whole difficulty —
A94 (root, k5 slots) certified **0**, A109 (A57 nodes, slot rows) certified **0 of 10** with
holes in every `B_r`, and A115 (k0 nodes, this very row) certified **2 of 11 attempted, only 1
attributable to the rows**. The failure is always the same: `verify_case` resolves a box that
straddles `∂E` only when the WHOLE box carries mass `≥ 1 + e`, so the `B` run reports holes on
boundary boxes that the `A` run never sees. A154 emits no certificate it does not need: every
in-vitro verdict below is an LP verdict, and where the LP kills, the record says **"LP-dead under
R6, certificate pending"** with the two-run form named.
