# Known results relevant to s(11)  (seeded from advisor memory; each item to be verified against sources)

Notation: s(n) = side of smallest square containing n unit squares, rotations allowed.

## Exact values known
- s(n²) = n (trivial). s(n²−1) = n, s(n²−2) = n for n ≥ 2 (Nagamochi 2005 for the general statement;
  small cases earlier). Hence s(2)=s(3)=2, s(7)=s(8)=3, s(14)=s(15)=4, ...
- s(5) = 2 + 1/√2 ≈ 2.7071 (Göbel 1979).
- s(6) = 3 (Kearney–Shiu 2002).
- s(10) = 3 + 1/√2 ≈ 3.7071 (Stromquist 2003).
- General lower bounds: s(n) ≥ √n; Nagamochi: s(n) ≥ ... (check).

## n = 11
- Upper bound: Walter Trump (1979) found by hand a packing with s ≈ 3.8772 (six upright squares + a
  strip of five squares tilted by θ ≈ 40.18°). Gensane & Ryckelynck (2005, Discrete Comput. Geom.)
  report 3.877084 via stochastic search. Prior Claude session (see `chat_history.txt`) derived that the
  side is a root of s⁸ − 20s⁷ + 178s⁶ − 842s⁵ + 1923s⁴ − 496s³ − 6754s² + 12420s − 6865
  with s ≈ 3.877084, and tan(θ/2) is a root of 5t⁸ + 10t⁷ − 2t⁶ − 14t⁵ + 12t⁴ + 6t³ + 2t² − 2t − 1.
  (Both to be re-derived and re-verified in this repo — the artifacts of that session were not saved.)
- Lower bound: Stromquist 2003 ("Packing 10 or 11 unit squares in a square", EJC 10, R8):
  s(11) ≥ 2 + 2√(4/5) ≈ 3.788854. Same paper: with orientations restricted to 0° / 45°, the optimum
  for 11 is 2 + 2√(8/9) ≈ 3.8856 > 3.877, so a non-45° tilt is required (Gardner's conjecture).
- Method for lower bounds ("unavoidable sets", Friedman survey): exhibit n−1 points in the side-s
  square such that every unit square inside contains one of them ⇒ s(n) ≥ s. Plus geometric
  lemmas about which region a square's centre may lie in.

## Sources to fetch
- E. Friedman, "Packing Unit Squares in Squares: A Survey and New Results", EJC Dynamic Survey DS7.
- W. Stromquist, "Packing 10 or 11 unit squares in a square", EJC 10 (2003) R8.
- T. Gensane, P. Ryckelynck, "Improved dense packings of congruent squares in a square", DCG 34 (2005).
- H. Nagamochi, "Packing unit squares in a rectangle", EJC 12 (2005) R37.
- F. Göbel, "Geometrical packing and covering problems", 1979.
- Anything 2005–2026 (arXiv) on s(11), computer-assisted lower bounds, formalisation.
