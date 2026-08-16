import PackingCert.Measure

/-!
# Measure-certificate examples

Göbel's 4-point unavoidable set for `s(5)` is `(1,1), (1,s−1), (s−1,1), (s−1,s−1)`
(each weight 1, total 4 < 5), unavoidable iff `s ≤ 2 + 1/√2`.  **As stated it is
degenerate for every `s`**: an upright unit square flush against the left wall
has its right edge on `x = 1`, so the atom lies on the boundary of the closed
square with zero margin, and no interval method can certify it.  We therefore
use the inward-perturbed set `(1−ε, ·), (s−1+ε, ·)` with `ε = 1/50` at
`s = 26/10`, which has margin ≈ 0.02 everywhere (checked numerically), and
proves `s(5) > 2.6`.
-/

namespace PackingCert.Measure.Example

def goebelPert (side eps : Rat) (fuel : Nat) : MCert :=
  let a := 1 - eps
  let b := side - 1 + eps
  { n := 5, side := side, fuel := fuel
    atoms := [⟨a, a, 1⟩, ⟨a, b, 1⟩, ⟨b, a, 1⟩, ⟨b, b, 1⟩] }

def g26 (fuel : Nat) : MCert := goebelPert (26/10) (1/50) fuel

end PackingCert.Measure.Example
