# Known results relevant to s(11)

Seeded from advisor memory 2026-08-16; verified/corrected by A01-literature (2026-08-16) against the primary
sources listed in `docs/literature.md` (local copies in `docs/papers/`). Tags: [verified: …] = checked in the
cited source by A01; [unverified] = not checked against a primary source.

Notation: s(n) = side of smallest square containing n unit squares, rotations allowed.

## Exact values known
- s(n²) = n (trivial). s(n²−1) = s(n²−2) = n for all n ≥ 2 [verified: Nagamochi 2005, EJC 12 #R37, Thm 2(i)];
  small cases earlier (Göbel 1979: n=2,3; Friedman DS7: 8, 15, 24, 35, and 7, 14; El Moumni 1999: 7, 8, 15).
- s(5) = 2 + 1/√2 ≈ 2.7071 (Göbel 1979) [verified: Friedman DS7 Thm 2 gives the unavoidable-set proof].
- s(6) = 3 [verified: Kearney–Shiu 2002, EJC 9 #R14, Thm 1, "duality" method]. s(7) = 3 [verified: Friedman
  DS7 Thm 7; Kearney–Shiu §2 give a shorter proof].
- s(10) = 3 + 1/√2 ≈ 3.7071 [verified: Stromquist 2003, EJC 10 #R8, Thm 1].
- s(13) = 4, s(46) = 7 [verified: Bentz 2010, EJC 17 #R126]; s(22) = 5, s(33) = 6 [verified: Bentz,
  arXiv:1606.03746 (2016)]. So s(m²−3) = m is proved for m = 3,…,7.
- Complete list of n ≤ 100 with s(n) proved: 1–10, 13–16, 22–25, 33–36, 46–49, 62–64, 79–81, 98–100 (plus the
  n²−1, n²−2 family beyond) [verified: Ellsworth's page + the papers above]. **s(11) and s(12) are the two
  smallest open cases** (s(12) is NOT known: 3.7889 ≤ s(12) ≤ 4; the Wikipedia table row "12–16 → 4" is
  misleading).
- General lower bounds: s(n) ≥ √n; Nagamochi 2005 Thm 2(ii): s(N) ≥ min{⌈√N⌉, sqrt(N − 2⌊√N⌋ + 1) + 1}
  [verified]. For N = 11 this gives only sqrt(6)+1 ≈ 3.449.
- Friedman DS7 Table 2 (2009) lists best lower bounds for n ≤ 85, e.g. s(11)=s(12) ≥ 3.7888 (Stromquist),
  s(17),s(18) ≥ (40√2+19)/17 ≈ 4.4452 (Green), s(19),s(20) ≥ 6√2−4 ≈ 4.4852 [verified]. Its s(13) ≥ 3.8437 is
  superseded by Bentz.

## n = 11
- **Upper bound (best known packing): s(11) ≤ 3.877083590022814177…**, the second real root of
  s⁸ − 20s⁷ + 178s⁶ − 842s⁵ + 1923s⁴ − 496s³ − 6754s² + 12420s − 6865 [verified: Ellsworth "Squares in
  Squares" page and the SVG source `docs/papers/ellsworth_square-11.svg`, exact derivation by D. Ellsworth June
  2023, confirmed independently by B. Alexeev; consistent with Gensane–Ryckelynck 2005 §7 who give
  cos(45°−θ) as a root of 80z⁸ − 128√2z⁷ − 32z⁶ + 144√2z⁵ + 72z⁴ − 112√2z³ + 40z² − 12√2z − 7 — A01 checked
  numerically to 30 digits that both descriptions agree]. Configuration: six upright squares + a rigid strip
  of five squares tilted θ = 40.18193729032971646523…° with cos θ a root of 5c⁸ − 12c⁷ + 8c⁶ + 2c⁵ − c⁴ − 2c + 1
  (equivalently sec θ a root of x⁸ − 2x⁷ − x⁴ + 2x³ + 8x² − 12x + 5) [verified: same SVG]; closed form
  s = 2 + (2 + sin θ)/(cos θ + sin θ); the two small internal gaps are equal, u1 = 0.0248745350255969539…
  [verified: SVG parameter u1]. Everything in `chat_history.txt` (octic, tan(θ/2) polynomial
  5t⁸ + 10t⁷ − 2t⁶ − 14t⁵ + 12t⁴ + 6t³ + 2t² − 2t − 1, equal gaps) is consistent with these public data —
  the tan(θ/2) polynomial itself is not published anywhere I found, so A03 should re-derive it.
- **Attribution (corrected):** the packing was found by hand by Walter Trump in 1979 (HP-67 calculator, value
  3.8770835903 sent to Gardner; published in Gardner's *Fractal Music, Hypercards and More*, 1991); independently
  by Gustafsson & Thulin 1980 ("Problem Ronden") and others. Gensane–Ryckelynck 2005 did **not** find a new
  arrangement: their inflation algorithm re-found Trump's rigid configuration and reported s11 = 3.87708359…,
  "slightly better" only than the survey's rounded 3.8772 [verified: G–R 2005 §7 text; Trump 2023 preprint
  abstract; Ellsworth SVG history note]. Friedman DS7 says "s(11) < 3.8771 … rigid" [verified].
- **No improvement since 1979** despite the 2024–2026 simulated-annealing campaign (Schadt, Ellsworth, Cantrell,
  Hajba) that improved n = 29, 51, 54, 55, 69, 87, … [verified: Ellsworth page, updates to Feb 2026].
- **Lower bound: s(11) ≥ 2 + 2·sqrt(4/5) = 2 + 4/√5 = 3.788854…** [verified: Stromquist 2003 Thm 2].
  **No later improvement exists** (checked: arXiv 2003–2026, forward citations of Stromquist/Bentz/Nagamochi/
  Friedman/G–R, Wikipedia, MathWorld, Ellsworth, OEIS) — the bound is 23 years old and, per Stromquist's own
  remark, "not rigid" in its second stage.
- Same paper, Thm 3: with orientations restricted to 0°/45°, 11 squares need side ≥ 2 + (4/3)√2 = 3.8856 >
  3.877, attained by Hämäläinen's packing ⇒ Gardner's conjecture that n = 11 is the first case needing a
  generic tilt [verified]. (Advisor's seed wrote "2 + 2√(8/9)"; that equals 2 + (4/3)√2 — same number.)
- **How Stromquist's s(11) proof works (for A02):** 10 points (Fig. 13: (1,1), (s/2,1), (3/2−s/4, s/2),
  (1/2+s/4, s/2) + symmetric images) are unavoidable everywhere except two top/bottom rectangles; a box in
  such a rectangle must (Lemmas 4, 6) contain three specified points A; the 12-point set of Fig. 14 is
  unavoidable ⇒ ≤ 10 boxes. The value is fixed by the unit-triangle lemma (sloping triangle sides in Fig. 13
  have length exactly 1: (s/4−1/2)² + (s/2−1)² = 1). It is an *almost*-unavoidable-set + one-case argument,
  not a pure 10-point unavoidable set [verified: paper text].
- Method for lower bounds ("unavoidable sets", Friedman DS7 §5): exhibit n−1 points in the side-k square such
  that every unit square inside contains one (boundary allowed; shrink by (1−ε/k)) ⇒ s(n) ≥ k [verified].
  Extensions in the literature: "almost unavoidable sets" + case analysis (Friedman s(7), s(14); Stromquist;
  Bentz 2010), *continuously varying families* of unavoidable sets (Bentz 2016), *two unavoidable sets used
  simultaneously* — Kearney–Shiu's "duality" (2002), and the piercing-number viewpoint (Bašić–Slivková 2018,
  DAM 247). No LP/SDP-dual bound for finite square containers exists in the literature.
- Rigorous computer-assisted packing proofs with rotating squares: only Montanher–Neumaier–Markót–Domes–Schichl
  (Vienna, JOGO 2019): 3 unit squares in a circle, interval B&B with tiling constraints (this is the "Vienna"
  approach in `chat_history.txt`) [verified]. Nothing for squares in a square. No formalisation (Lean/Isabelle/
  Coq) of any result in this family exists.

## Sources (all fetched unless noted; see `docs/literature.md` for annotations)
- E. Friedman, "Packing Unit Squares in Squares: A Survey and New Results", EJC DS7, v5 Aug 2009 — `docs/papers/friedman_DS7_survey_2009.pdf`.
- W. Stromquist, "Packing 10 or 11 unit squares in a square", EJC 10 (2003) #R8 — `docs/papers/stromquist2003.pdf`; 1984 memoranda I–III scans `stromquist1984_memo*.pdf`.
- T. Gensane, P. Ryckelynck, "Improved dense packings of congruent squares in a square", DCG 34 (2005) 97–109 — `docs/papers/gensane_ryckelynck2005_DCG.pdf`.
- H. Nagamochi, "Packing unit squares in a rectangle", EJC 12 (2005) #R37 — `docs/papers/nagamochi2005_R37.pdf`.
- M. Kearney, P. Shiu, EJC 9 (2002) #R14 — `docs/papers/kearney_shiu2002_R14.pdf`.
- W. Bentz, EJC 17 (2010) #R126 and arXiv:1606.03746 — `docs/papers/bentz2010_13and46_R126.pdf`, `bentz2018_22and33_arXiv1606.03746.pdf`.
- Montanher et al., JOGO 73 (2019) — `docs/papers/montanher_neumaier_markot_domes_schichl_2019_squares_in_circle_JOGO.pdf`.
- D. Ellsworth, "Squares in Squares" (2023–2026) — `docs/papers/ellsworth_squares_in_squares.*`, `ellsworth_square-11.svg`.
- F. Göbel 1979 (Math. Centre Tracts 106) — not online. W. Trump 2023 ResearchGate preprint — not downloadable
  (403). B. Bašić, A. Slivková, DAM 2018 — paywalled.
