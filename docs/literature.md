# Literature sweep for s(11) — annotated bibliography

Compiled by A01-literature, 2026-08-16. Local copies of everything downloadable are in `docs/papers/`
(PDF plus a `.txt` text extraction where the PDF has a text layer). Items are grouped by role. Each entry
says what it proves and how, and how it bears on n = 11.

**Bottom line (verified against primary sources):**

| bound | value | source | status |
|---|---|---|---|
| s(11) ≥ 2 + 2·sqrt(4/5) = 2 + 4/√5 = 3.788854… | Stromquist, EJC 10 (2003) #R8, Thm 2 | proven | no later improvement found anywhere (2003–2026) |
| s(11) ≤ 3.877083590022814177… (root of an octic) | Trump 1979 (found by hand + HP-67); same packing re-found numerically by Gensane–Ryckelynck 2005; exact octic by Ellsworth 2023 (confirmed by Alexeev) | rigorous as a packing (rigid; exact algebraic description known) | no improvement 1979–2026 despite modern SA/G–R style searches (Schadt/Ellsworth 2025–26 improved n = 29, 51, 54, 55, … but not 11) |

Also: s(12) is open too (3.7889 ≤ s(12) ≤ 4; the "12 → 4" row in Wikipedia's table is *not* a proven value —
Wikipedia's own list of proven n omits 12, and Ellsworth's page has no "proved" tag for 12).

---

## A. Primary sources on n = 11

### A1. W. Stromquist, "Packing 10 or 11 Unit Squares in a Square", Electron. J. Combin. 10 (2003) #R8.
- URL: https://www.combinatorics.org/ojs/index.php/eljc/article/view/v10i1r8 (open access; DOI 10.37236/1701).
- Local: `docs/papers/stromquist2003.pdf`, `stromquist2003.txt`.
- **Proves:** (Thm 1) s(10) = 3 + 1/√2; (Thm 2) s(11) ≥ 2 + 2·sqrt(4/5) ≈ 3.789; (Thm 3) among packings whose
  squares are tilted only 0° or 45°, 11 squares need side ≥ 2 + (4/3)√2 ≈ 3.886 (attained by Hämäläinen's 45°
  packing), so the true optimum for 11 requires a "generic" tilt (Gardner's conjecture).
- **How (Thm 2, the s(11) bound):** works with "boxes" (open squares of side > 1) inside the closed square
  S = [0,s]², s = 2+2·sqrt(4/5). Uses six "nonavoidance lemmas" (if a box's centre lies in a region, the box
  meets specified parts of the region's boundary): L1 corner rectangle [0,a]×[0,b] (a,b ≤ 1) ⇒ meets an axis
  or (a,b); L2 triangle with sides ≤ 1 ⇒ contains a vertex; L3 rectangle [0,a]×[0,b] with a+2b ≤ 2√2 ⇒ meets
  x-axis, (0,b) or (a,b); L4 a quadrilateral version with an explicitly computed threshold f(a) (a cubic in
  cos θ*); L5, L6 ad-hoc pentagons for n = 10 and 11. Fig. 13: ten points — (1,1), (s/2,1), (3/2−s/4, s/2),
  (1/2+s/4, s/2) and their images under the symmetries of S — are unavoidable on all of S *except two
  rectangles at the top and bottom*. Hence in an 11-box packing at least one box sits in such a rectangle;
  Lemmas 4 and 6 force that box to contain all three points A = {(1,.9), (s/2,.9), (1+sqrt(1/5), 1.12)}, and
  the 12-point set A ∪ {B,…,J} of Fig. 14 is unavoidable, so 11 boxes would need ≥ 12 + 2 = 14 distinct
  points — contradiction. **Where the value comes from:** the triangles in Fig. 13 have sloping sides of length
  exactly 1 (Lemma 2 is tight): (s/4 − 1/2)² + (s/2 − 1)² = 1 ⇔ s = 2 + 2·sqrt(4/5). Stromquist says
  explicitly that Fig. 14 "is not rigid; any point could be moved a small amount", and "the critical distances
  are all in Figure 13". So the slack is entirely in the 10-point Fig.-13 configuration and Lemma 2 (unit
  triangles). Note that this is *not* a pure 10-point unavoidable set — it is a 10-point *almost*-unavoidable
  set plus a one-case argument. **Directly relevant to A02, A05, A07.**
- Earlier versions of these results: Stromquist's Daniel H. Wagner Associates internal memoranda I (six
  squares, 1984), II (ten squares, 1984), III (n ≤ 65 and Gardner's conjecture for n = 11, Nov 15 1984),
  scanned at http://www.walterstromquist.com/papers/squares{1,2,3}.pdf — local copies
  `docs/papers/stromquist1984_memo{1,2,3}_squares{1,2,3}.pdf` (image-only scans, no text layer).

### A2. E. Friedman, "Packing Unit Squares in Squares: A Survey and New Results", Electron. J. Combin. Dynamic Survey DS7 (v1 1998 … v5 Aug 14 2009).
- URL (latest, 2009): https://erich-friedman.github.io/papers/squares/squares.html ; PDF
  https://erich-friedman.github.io/papers/squares.pdf ; EJC page https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS7 (DOI 10.37236/28).
- Local: `docs/papers/friedman_DS7_survey_2009.pdf`, `friedman_survey_github.{html,txt}`.
- **Content:** history; best known packings n ≤ 100 (Table 1) and best lower bounds (Table 2); proofs by
  unavoidable point sets of s(2)=s(3)=2, s(5)=2+1/√2, s(8)=3, s(15)=4, s(24)=5, s(35)=6, and by
  "almost unavoidable sets" + case analysis of s(7)=3 and s(14)=4. Seven technical lemmas (Lemma 1 corner
  point (1,1); Lemma 2 rectangle [1,1+x]×[0,y] with x+2y < 2√2; Lemma 3 unit triangle; Lemma 4 rectangle
  [0,1]×[0,.4]; Lemmas 5–7 about how much of a line/side a square must cover). Formal statement of the method
  (Sec. 5): a set P of n−1 points in S=[0,k]² is *unavoidable* if every unit square in S contains a point of P
  (boundary allowed); shrinking by (1−ε/k) turns boundary contact into interior containment ⇒ s(n) ≥ k.
- **n = 11 in the survey:** upper bound "s(11) < 3.8771", Fig. 6, Walter Trump 1979 ("many people have
  independently discovered this packing"; misattributed to Gustafson–Thule), middle squares tilted ≈ 40.182°,
  packing is rigid; lower bound Thm 11: s(11) ≥ 2 + 4/√5 (Stromquist). Table 2 lists 3.7888 as the best lower
  bound for both n = 11 and n = 12; also lists s(13) ≥ 3.8437 (Friedman), superseded by Bentz's s(13)=4.
- The survey is frozen at 2009. Its packing tables have been superseded by Ellsworth's page (A4).

### A3. T. Gensane, P. Ryckelynck, "Improved Dense Packings of Congruent Squares in a Square", Discrete Comput. Geom. 34 (2005) 97–109. DOI 10.1007/s00454-004-1129-z.
- URL: https://doi.org/10.1007/s00454-004-1129-z (publisher PDF was retrievable; local
  `docs/papers/gensane_ryckelynck2005_DCG.pdf`, `.txt`).
- **Method:** links s_n to the supremum of the "maximal inflation" of admissible configurations; a
  billiard-like / stochastic inflation algorithm (perturb, inflate, repeat) — the first effective computer
  method for squares. Improved best known packings for n = 11 (numerically), 29, 37; alternative optimum for 18.
- **n = 11 (their Sec. 7):** "The best known packing is due to Trump and apparently to many other people. In
  [Friedman] we find s11 ≤ 3.8772 … We have obtained this packing several times with s11 = 3.87708359…, a
  result which is slightly better." So G–R did **not** find a new arrangement: they re-found Trump's rigid
  configuration and computed its side more precisely than the survey's rounded 3.8772 (Trump himself had
  3.8770835903 in 1979, see A5). They give the exact algebraic condition: cos φ (φ = angle of the five central
  squares measured from the diagonal, i.e. φ = 45° − θ) is a root of the Q(√2)-polynomial
  80z⁸ − 128√2 z⁷ − 32z⁶ + 144√2 z⁵ + 72z⁴ − 112√2 z³ + 40z² − 12√2 z − 7, obtained by elimination from a
  14-equation tangency system, and s = 4z/(2√2 + 5z − sqrt(1−z²)) — actually a formula for 2/s (Ellsworth's
  remark). **Checked in A01:** with θ = 40.18193729032971646523° the polynomial vanishes at z = cos(45°−θ)
  to 30 digits.

### A4. D. Ellsworth (maintainer, since 2023 succeeding Friedman's "Erich's Packing Center"), "Squares in Squares", https://kingbird.myphotos.cc/packing/squares_in_squares.html (last updates Feb 2026).
- Local: `docs/papers/ellsworth_squares_in_squares.{html,txt}`, `…__triangular_table.*`, `…__rigid.*`,
  `…__analytic_minimization.*`, and the n = 11 SVG `docs/papers/ellsworth_square-11.svg`.
- **n = 11 entry:** s = 3.87708359002281, root of
  **s⁸ − 20s⁷ + 178s⁶ − 842s⁵ + 1923s⁴ − 496s³ − 6754s² + 12420s − 6865 = 0**, "Rigid. Found by Walter Trump in 1979."
  The SVG source is a self-contained exact description: s = Root[…octic…, 2] (33 digits given:
  3.87708359002281417730789706010096), tilt a = 40.1819372903297164652303423680606° with
  a = ArcSec[Root[5 − 12x + 8x² + 2x³ − x⁴ − 2x⁷ + x⁸, 1]] (i.e. cos a is a root of
  5c⁸ − 12c⁷ + 8c⁶ + 2c⁵ − c⁴ − 2c + 1 — matches `chat_history.txt`), closed form s = 2 + (2 + sin a)/(cos a + sin a),
  the two-equation Mathematica derivation, and all placement parameters (x0, r1, u1 = 0.0248745350255969…
  the small gap, v1, v2). History note: exact root form first by G–R 2004 (unreduced), reduced octic by
  Ellsworth June 4 2023, independently confirmed by Boris Alexeev the same day. Also confirms Gustafsson &
  Thulin's independent 1980 rediscovery ("Problem Ronden").
- **Status of upper-bound search (important negative evidence):** the page documents an active 2024–2026
  campaign (Cantrell, Hajba, Ellsworth, Schadt, Brendberg, DeVincentis) using new simulated-annealing programs
  (Schadt's reimplementation of the G–R algorithm and Ellsworth's modifications) that improved many records
  (n = 29 to 5.93383…, 51, 54, 55, 69, 87, 110–200+). n = 11 was not improved. Ellsworth's
  "analytic minimization" page explains how to turn an underdetermined contact system into a square system
  (minimise s along the constraint curve: gradient/anti-parallel condition) — useful for A03/I-U2.
- Ellsworth's page has **no lower-bound table**; the only lower-bound source for n = 11 remains Stromquist.

### A5. W. Trump, "Packing of 11 unit squares in a square with minimum size", preprint (ResearchGate, March 2023), https://www.researchgate.net/publication/368988287 ; and Wikimedia Commons file "Packing 11 unit squares in a square with side length 3.87708359....svg" (Trump, 7 Mar 2023).
- Could not download (ResearchGate 403 for automated fetch); content known from search snippets: the densest
  known packing is still his 1979 one; the value 3.8770835903 was sent to Gardner in 1979 (11 digits, "too much
  for an HP-67"); the packing is exactly determined by vertex-on-edge contacts and is rigid; "cannot be improved
  by computer programs as long as the same geometrical arrangement is used"; first correctly published (with an
  imprecise drawing) in Gardner's book *Fractal Music, Hypercards and More* (1991). Settles the "Trump vs
  Gensane–Ryckelynck" attribution question raised in
  https://github.com/erich-friedman/erich-friedman.github.io/issues/3 : same packing, G–R only refined digits.

### A6. Wikipedia, "Square packing", https://en.wikipedia.org/wiki/Square_packing (wikitext saved as `docs/papers/wikipedia_square_packing.wikitext`).
- States 3.789 ≤ s(11) and best packing ≈ 3.877084 (Trump; digits from G–R 2005). Proven-n list: squares and
  2, 3, 5, 6, 7, 8, 10, 13, 14, 15, 24, 34, 35, 46, 47, 48 (misses 22, 23, 33 and Nagamochi's whole family
  n²−1, n²−2; and its table row "12,…,16 → 4" wrongly implies s(12) is known). Reference list is a useful
  DOI index (Brass–Moser–Pach; Nagamochi; Bentz 2010; Friedman DS7; Stromquist; G–R; Erdős–Graham; Chung–Graham;
  Wang–Dong–Li; McClenagan; Roth–Vaughan; Abrahamsen–Stade). Nothing newer on n = 11.
- MathWorld "Square Packing" (https://mathworld.wolfram.com/SquarePacking.html): table credited to Friedman
  and Ellsworth; n = 11 "3.877…" not marked optimal; proven list includes 22, 33 (Bentz). No methods.
- OEIS: no sequence for s(n) values found (A081287 is a different rectangle-packing sequence).

## B. Exact values and general lower-bound machinery

### B1. F. Göbel, "Geometrical packing and covering problems", in *Packing and Covering in Combinatorics* (A. Schrijver ed.), Math. Centre Tracts 106 (1979) 179–199.
- Not online. First paper on the problem: s(2)=s(3)=2, s(5)=2+1/√2, the diagonal-strip family
  s(a²+a+3+⌊(a−1)√2⌋) ≤ a+1+1/√2 (gives n = 5, 10, 27, 38, …) and the 45°-block family. Cited via Friedman.

### B2. M. Kearney, P. Shiu, "Efficient packing of unit squares in a square", Electron. J. Combin. 9 (2002) #R14.
- URL: https://www.combinatorics.org/ojs/index.php/eljc/article/view/v9i1r14 ; local `kearney_shiu2002_R14.pdf/.txt`.
- **Proves** s(6) = 3 (first published proof) and re-proves s(7) = 3, by a **"duality" method**: take
  Friedman's 7-point unavoidable set for [0,3]² ("green lattice") and its 90° rotation ("red lattice"; also
  unavoidable); every unit square must contain a green *and* a red point; the two lattices share the centre
  C. Lemma 1: any unit square covering C also covers one of the four "B" points at distance 1/2 from C (proved
  by an arc-length argument). For 7 squares each must use exactly one point of each lattice, impossible with C
  shared ⇒ s(7)=3; for 6 squares a short case analysis (configurations (a)/(b)) finishes s(6)=3. **This is the
  earliest instance of a *weighted/multi-set* unavoidable argument — precisely the flavour of I-L2 (fractional
  unavoidable sets): several unavoidable sets used simultaneously, plus a local lemma that a square hitting a
  particular point must hit a second one.** Also: asymptotic constructions for s(n²+1) via Pell equations.

### B3. H. Nagamochi, "Packing Unit Squares in a Rectangle", Electron. J. Combin. 12 (2005) #R37.
- URL: https://www.combinatorics.org/ojs/index.php/eljc/article/view/v12i1r37 ; local `nagamochi2005_R37.pdf/.txt`.
- **Proves:** for real a, b ≥ 2, fewer than ab − (a+1−⌈a⌉) − (b+1−⌈b⌉) unit squares fit in any a'×b' rectangle
  with a' < a, b' < b. Corollaries: s(n²−1) = s(n²−2) = n for all n ≥ 2, and the general lower bound
  s(N) ≥ min{⌈√N⌉, sqrt(N − 2⌊√N⌋ + 1) + 1} > √N. For N = 11 this gives only sqrt(6)+1 ≈ 3.449.
- **How:** an explicit unavoidable set U for the rectangle (a lattice-like set with modified boundary rows),
  proved unavoidable through a series of technical lemmas (Sec. 4–5); i.e. the same point-hitting method,
  but organised for general size.

### B4. W. Bentz, "Optimal Packings of 13 and 46 Unit Squares in a Square", Electron. J. Combin. 17 (2010) #R126.
- URL: https://www.combinatorics.org/ojs/index.php/eljc/article/view/v17i1r126 (DOI 10.37236/398);
  local `bentz2010_13and46_R126.pdf/.txt`.
- **Proves** s(13) = 4, s(46) = 7 (i.e. s(m²−3) = m for m = 4, 7). **How:** Stromquist's "boxes";
  a catalogue of non-avoidance lemmas (Nagamochi/Stromquist Lemma 1: a box centred in [0,1]² avoiding the
  axes contains (1,1), (.9,1), (1,.9); unit-triangle lemma; corollary for rectangles of height < √3/2 via the
  midpoint; Stromquist's L3/L4/f(a) lemma) plus "boxes of restricted movement" lemmas; then a case tree: a
  first (almost-)unavoidable set forces one box T* into a small region, subcases by the region R1–R4 of its
  centre, each closed by a "small enough" unavoidable set listed explicitly (coordinates like (2.5,1),
  (3.1,1), (2.5,1.6), …). Same style as Stromquist's Thm 2 but with deeper case analysis. Good template for
  I-L5 (structure theorem + finish by point sets).

### B5. W. Bentz, "Optimal Packings of 22 and 33 Unit Squares in a Square", arXiv:1606.03746 (June 2016); Ellsworth's page dates the proof "October 2018" (no journal version located in Crossref — treat as a preprint that the community accepts).
- URL: https://arxiv.org/abs/1606.03746 ; local `bentz2018_22and33_arXiv1606.03746.pdf`.
- **Proves** s(22) = 5, s(33) = 6 (m²−3 for m = 5, 6). **Method novelty:** "we modify the well-known method of
  sets of unavoidable points by replacing them with *continuously varying families* of such sets" — i.e. the
  unavoidable set is allowed to depend on a parameter (a position of one forced box), which is exactly the
  kind of parametric argument a computer-assisted (interval) approach could systematise. Latest published
  exact-value result in this line (nothing newer found on arXiv through Aug 2026).

### B6. B. Bašić, A. Slivková, "On optimal piercing of a square", Discrete Appl. Math. 247 (2018) 242–251, DOI 10.1016/j.dam.2018.03.048.
- Paywalled (ScienceDirect blocked automated download; no arXiv version found). From the abstract: they study
  the piercing number τ(U_n) of the family U_n of open unit squares inside an n×n square (= minimum size of an
  unavoidable point set with *interior* hitting), show τ(U_n) = n² for n ≤ 7, give an asymptotic upper bound
  (abstract as indexed reads "asymptotically equal to (2/3)n²", which cannot be literally right since the n²
  grid cells force τ ≥ n²; read the paper before quoting), extend to rectangles and to non-integer side x, and
  claim "a general framework based on which we are able to reprove many results on [s(n)] … and also obtain a
  new result on packing 61 unit squares" (Ellsworth's page does not mark 61 as proved, so probably a bound).
  **Relevance:** it is the only paper that treats "how small can an unavoidable set be" as the primary
  object — exactly the ceiling question for I-L1/A05 (is a 10-point unavoidable set possible in side
  s > 3.7889?). Worth obtaining through a library.

### B7. S. El Moumni, "Optimal packings of unit squares in a square", Studia Sci. Math. Hungar. 35 (1999) 281–290. Proves s(7)=s(8)=3, s(15)=4 (independently, little-known). Not online.

## C. Computer-assisted / rigorous-numerics approaches (the "Vienna" reference)

### C1. T. Montanher, A. Neumaier, M. C. Markót, F. Domes, H. Schichl, "Rigorous packing of unit squares into a circle", J. Global Optim. 73 (2019) 547–565, DOI 10.1007/s10898-018-0711-5 (Univ. of Vienna / Wolfgang Pauli Institute; FWF P25648).
- URLs: https://pmc.ncbi.nlm.nih.gov/articles/PMC6394747/ (open access), preprint
  https://optimization-online.org/2018/04/6556/ ; local
  `montanher_neumaier_markot_domes_schichl_2019_squares_in_circle_JOGO.pdf`, `montanher2019_squares_in_circle.txt`.
- **This is what "the interval-arithmetic branch-and-bound approach being used in Vienna" in `chat_history.txt`
  refers to.** They rigorously solve the smallest-circle problem for n = 3 unit squares (r₃ ∈
  [1.28847050800547, 1.28847050800553]) — only n = 1, 2 were known before. **Method:** CSP formulation
  (containment via convexity of the circle; non-overlap via a "sentinel" method with nine points per square);
  interval branch-and-bound with forward–backward constraint propagation in the rigorous solver GloptLab; the
  key trick is *tiling constraints* — the disc is split into 36 isosceles triangles, each of which can hold at
  most one square centre (centres are ≥ 1 apart), giving a finite set of subproblems, and they iterate on the
  number of squares (solve all 1-square subproblems, keep the survivors, extend to 2, then 3) to prune early;
  symmetric subproblems discarded. n = 3 needed 6 + 43 + 12 subproblems. They state the method generalises but
  is computationally practical only for small n. **Take-away for I-L4:** even the state of the art in fully
  rigorous B&B handled 3 rotating squares; 11 squares in a square (33 dims) is far out of reach without
  massive combinatorial pre-reduction (which is what I-L2/I-L5 would supply).
- Related lineage (circles, not squares): M. C. Markót & T. Csendes, "A new verified optimization technique for
  the 'packing circles in a unit square' problems", SIAM J. Optim. 16 (2005) 193–219 (rigorous optimality for
  28, 29, 30 circles; 42^n tile combinations; ~50 CPU-hours); Markót 2007 "Interval methods for verifying
  structural optimality of circle packing configurations"; Markót 2021 "Improved interval methods for solving
  circle packing problems in the unit square" (J. Global Optim.); Szabó–Markót–Csendes–Specht–Casado–García,
  *New Approaches to Circle Packing in a Square* (Springer 2007). These are the methodological source for
  tiling + interval B&B; none treats squares in a square.

### C2. Global-optimisation modelling (non-rigorous): J. Kallrath's work (BASF) on cutting circles/polygons/ellipses from
area-minimising rectangles uses NLP/MINLP solvers (BARON, LINDOGlobal) to get good packings and, for tiny
instances, global-optimality certificates in floating point — not proofs. Not specific to unit squares in a
square; no paper on s(11). (Not downloaded.)

### C3. Formalisation. No Lean/Isabelle/Coq formalisation of any square-in-square packing result was found
(searched Lean/Mathlib, arXiv, general web). Closest: the Kepler conjecture (Flyspeck, HOL Light/Isabelle
2014) and the 2025–26 Lean formalisation of the 8/24-dimensional sphere packing proofs. Our `lean/`
certificate would be the first in this problem family.

## D. Upper-bound search machinery (context for A03/A04)

- Gensane–Ryckelynck 2005 (A3): inflation/billiard algorithm — the classical computer method.
- Ellsworth's page (A4): 2024–26 record-setting simulated annealing (T. Schadt) + exact "analytic
  minimisation" of contact systems (Mathematica FindRoot / Solve / RootReduce); every record packing comes
  with an SVG carrying exact parameters and the polynomial root. Best practice for our certificates.
- M. Z. Arslanov, S. A. Mustafin, Z. K. Shangitbayev, "Improved Packings of n(n−1) Unit Squares in a Square",
  Electron. J. Combin. 28 (2021), DOI 10.37236/8586 (open access): s(n²−n) < n for all n ≥ 12 (Friedman's
  s(n²−n)=n conjecture fails from n = 12 on; Ellsworth/Cantrell 2025–26 pushed to n = 11 not-yet-analytic).
- Asymptotics (not directly relevant to n=11 itself, but see §F for the A33 sweep with exact statements
  verified against primary sources — including a 2025 erratum in the Chung–Graham 2020 chain that the
  literature had not yet flagged as of this A01 pass): Erdős–Graham 1975 W(s)=O(s^{7/11}); Roth–Vaughan 1978
  lower bound; Chung–Graham 2009 (O(s^{0.631})) and 2020 DCG "Efficient packings of unit squares in a large
  square" (claimed O(s^{0.6}), later shown flawed); Wang–Dong–Li arXiv:1603.02368 (O(s^{0.625})); McClenagan
  arXiv:2602.01484 (O(s^{0.6}), independent correct proof); H. D. Bui arXiv:2504.09489, arXiv:2508.04603
  (O(x^{0.6}) construction, 2025–26, also an independent correct proof); Praton math/0504341,
  Baek–Koizumi–Ueoro arXiv:2411.07274, A. R. Singh arXiv:2506.23284/2601.22163 (Erdős's square-packing
  conjecture, a different problem — packing squares of total area 1 in a square).
- Complexity: Abrahamsen–Stade, FOCS 2024 (packing simple polygons with unit squares is NP-hard);
  Abrahamsen–Miltzow–Seiferth 2020 (∃R-completeness of 2D packing with rotations, cites G–R).

## E. What was searched and not found

- arXiv API (math.CO/math.MG, all years) for "unit squares"+"square"+packing, "squares in a square",
  "packing unit squares", "congruent squares", "unavoidable" + squares, "square packing lower bound":
  no paper on s(11) or on any improved lower bound for small n beyond Bentz 2016.
- Semantic Scholar forward citations of Stromquist 2003 (11), Bentz 2010 (4), Nagamochi 2005 (11),
  Friedman DS7 (33), G–R 2005 (17): none improves s(11); the only new lower-bound-side works are Bentz 2016/18
  and Bašić–Slivková 2018.
- Web: "s(11) square packing lower bound", "eleven unit squares", "packing 11 unit squares", "unavoidable set
  squares", Lean/Isabelle/Coq + square packing, SDP/LP dual bounds for finite square containers: nothing.
  No LP/SDP-duality lower bound for finite-container square packing exists in the literature that I could
  find; the closest relatives are Kearney–Shiu's two-lattice "duality" (B2) and the piercing-number viewpoint
  (B6).

## F. Wastage asymptotics for unit squares in a large square (A33 sweep, 2026-08-26)

Not directly about n = 11, but A33/T3(a) wants the exact state of the asymptotic question: how does
W(x) = x² − s(x) (wasted area when packing unit squares into a side-x square) grow as x → ∞? All entries
below were checked against the primary PDF (arXiv or the authors' own site), not against blog/Wikipedia
summaries. Local copies of the papers I could pull past a captcha/paywall are in `docs/papers/`:
`erdos_graham1975_JCTA.pdf`, `chung_graham2009_JCTA.pdf`, `chung_graham2020_DCG_flawed.pdf`,
`bui2025_good_squares_arXiv2504.09489.pdf`, `bui2025_Ox06_arXiv2508.04603.pdf`,
`mcclenagan2026_arXiv2602.01484.pdf` (the last is metadata-only extractable, see F10; Roth–Vaughan 1978 and
the Arslanov–Bui 2025 erratum note are paywalled with no open copy found, see F4/F7).

**Exponent chain (all upper bounds on W(x), decreasing = better):**

| year | exponent | value | source |
|---|---|---|---|
| 1975 | 7/11 | 0.636364… | Erdős–Graham |
| — | (3−√3)/2 | 0.633975… | Montgomery (unpublished) |
| 2009 | (3+√2)/7, with a log x factor | 0.630601… | Chung–Graham |
| 2016 | 5/8, no log factor | 0.625 | Wang–Dong–Li |
| 2020 (claimed) / 2025–26 (actually proved) | 3/5 | 0.6 | Chung–Graham claimed it in 2020; the proof had a bug found in 2025 (Arslanov–Bui); reproved correctly, independently, by Bui and by McClenagan in 2025–26 |

Lower bound (Roth–Vaughan 1978, still the only one): W(x) ≫ x^{1/2} when x is bounded away from an integer —
**the 1/2-vs-0.6 gap is still open**, and has been since 1978. No paper found narrows it from either side.

### F1. P. Erdős, R. L. Graham, "On Packing Squares with Equal Squares", J. Combin. Theory (A) 19 (1975) 119–123.
- URL: https://mathweb.ucsd.edu/~fan/ron/papers/75_06_squares.pdf (Graham's own site; the older
  `math.ucsd.edu/~fan/...` URL 302-redirects here — WebFetch chokes on the redirected host's cert, curl -kL
  works). Local `docs/papers/erdos_graham1975_JCTA.pdf`.
- **Proves (the Theorem, verbatim):** W(α) = O(α^{7/11}), where W(α) = α² − sup_𝒫|𝒫| over packings 𝒫 of
  unit squares into S(α). (They also phrase it as a circle-inscribing-squares corollary: f(k²+[cα^{7/11}]) > 4k
  for f(l) = max total circumference of l nonoverlapping squares in a unit square — the packing question was
  originally motivated by that circumference problem and by "multidimensional stock cutting".)
- **Construction:** first fill S(α) with an axis-aligned N×N block (N = α − α^{8/11}), leaving two border
  rectangles of width β = α − N ≈ α^{8/11}; tile each with *tilted* stacks of unit squares (angle
  θ = Ω(α^{-4/11})) so the stacks touch both long edges, leaving two right trapezoids per rectangle of base
  β and height ≈ α^{2/11}/α^{4/11}; recursively subdivide each trapezoid into strips of base m = α^{4/11} and
  pack those with more tilted stacks, at each stage accounting for the small border triangles. This is exactly
  the "one global tilt angle per stack, staircase of trapezoids" scheme that all later improvements (Chung–
  Graham, Wang–Dong–Li, McClenagan, Bui) still use as the skeleton — they only change the exponents at which
  the strip widths/tilt angles are set and add extra levels of recursion.
- **Explicitly flags the open lower-bound question** at the end: "It is rather annoying that we do not at
  present have any nontrivial lower estimate for W(α)... Perhaps the correct bound is O(α^{1/2})" — i.e. they
  themselves guessed the 1/2 exponent that Roth–Vaughan later made rigorous as a *lower* bound (not, as E–G
  guessed, an upper bound — the truth is presumably strictly between 1/2 and the current 3/5 upper bound).
- **Relevance to A33 grain conjecture:** this is the origin of the "single global tilt, staircase of strips"
  picture — i.e. optimal-ish packings are conjectured/constructed as one dominant "grain" (a big block of
  axis-aligned squares) plus boundary strips at a small number of distinct tilts, not a fine mosaic of many
  differently-oriented grains. Every later paper in this chain keeps that same qualitative picture; none
  produces (or needs) more than O(1) distinct tilt angles.

### F2. H. Montgomery, unpublished (cited only as "personal communication" in Chung–Graham 2009, ref [8] there).
- **Claim (as reported by Chung–Graham):** W(x) = O(x^{(3−√3)/2}) = O(x^0.633975…). No preprint, no arXiv id,
  no journal version found anywhere (searched arXiv, Google Scholar, MathSciNet-adjacent search); this is a
  citation to an oral/private communication only, exactly as Erdős–Graham's own paper cites Montgomery-style
  personal communications for other facts. Treat as unverifiable folklore, cited only because Chung–Graham
  built on it.

### F3. F. Chung, R. Graham, "Packing Equal Squares into a Large Square", J. Combin. Theory (A) 116 (2009) 1167–1175.
- URL: https://mathweb.ucsd.edu/~ronspubs/09_03_square_packing.pdf (authors' site; also
  https://www.sciencedirect.com/science/article/pii/S0097316509000272). Local `docs/papers/chung_graham2009_JCTA.pdf`.
- **Proves (Thm 1):** W(x) = O(x^{(3+√2)/7} log x), (3+√2)/7 = 0.630601…, improving Erdős–Graham's 7/11 and
  Montgomery's (3−√3)/2. Also (Thm 2) a matching cover bound s′(x) = x² + O(x^{(3+√2)/7} log x), and (Thm 3) a
  general trapezoid-angle result Wθ(x) = O(x^{1−δ/(2+√2)}) for tilt θ = 1/x^δ.
- **Quotes Roth–Vaughan's theorem verbatim (their eq. (1)):** "if x(x−⌊x⌋) > 1/6, then
  W(x) > 10^{-100}√(x·|x−⌊x+1/2⌋|)" — this is the exact form of the lower bound (see F4); Chung–Graham note it
  gives W(x) ≫ x^{1/2−ε} for x bounded away from an integer.
- **Method:** an induction on three parametrized shapes — Type-1 rectangle, Type-2 trapezoid (tilt
  θ ≤ √(2/x)), Type-3 trapezoid (tilt θ ≤ 1/x) — each packed by tilted unit-square stacks with the recursion
  bottoming out in O(x^{2−2α}) sized subproblems, α = (3+√2)/7. Genuinely a refinement of Erdős–Graham's
  scheme with a second level of recursion (Type-2/Type-3 shapes calling each other) rather than a new idea.
- Poses "Challenge ($100): improve (3+√2)/7" and "Conjecture ($1000): W(x) ≫ x^{1/2+c}" (i.e. they
  explicitly *don't* believe the truth is 1/2, contra their 1975 paper's own guess) — both bounties still
  formally open as far as I could tell (no claim of payout found).

### F4. K. F. Roth, R. C. Vaughan, "Inefficiency in Packing Squares with Unit Squares", J. Combin. Theory (A) 24 (1978) 170–186.
- URL: https://www.sciencedirect.com/science/article/pii/0097316578900055 (paywalled; ScienceDirect blocked
  automated fetch, no open-access or arXiv copy found). **Not independently re-verified against the original
  text** — the statement below is quoted verbatim from two independent later papers that cite it (Chung–Graham
  2009 §1 and Chung–Graham's own 2020 note §1, both reproducing the same inequality with the same "10^{-100}"
  constant), so it is reliable but technically a secondary-source confirmation, not primary.
- **Proves:** if x(x − ⌊x⌋) > 1/6, then W(x) > 10^{-100}·√(x·‖x‖) where ‖x‖ = |x − ⌊x+1/2⌋| is the distance
  from x to the nearest integer. Corollary: W(x) ≫ x^{1/2} for x bounded away from any integer (constant
  depends on the distance). **This is still the only nontrivial lower bound in the literature** — nothing
  published since 1978 improves the exponent 1/2, weakens the "bounded away from an integer" hypothesis, or
  improves the (astronomically bad) 10^{-100} constant.
- **2025 simplification of the proof technique (not the bound):** H. D. Bui, "Square Packing with
  Asymptotically Smallest Waste Only Needs Good Squares", arXiv:2504.09489 (13 Apr 2025), CCCG 2025 — see F8.

### F5. S. Wang, T. Dong, J. Li, "A New Result on Packing Unit Squares into a Large Square", arXiv:1603.02368 (8 Mar 2016, rev. 9 Apr 2016).
- URL: https://arxiv.org/abs/1603.02368.
- **Proves:** W(x) = O(x^{5/8}) = O(x^0.625), improving Chung–Graham 2009's O(x^{(3+√2)/7} log x) — note this
  removes the log factor too, not just the exponent (0.625 < 0.630601, and no log x). Also improves the dual
  cover bound to s′(x) = x² + O(x^{5/8}).
- Abstract states explicitly it "improved the earlier results of Erdős-Graham, Roth-Vaughan, and
  Karabash-Soifer" via the Chung–Graham 2009 baseline. Construction not independently checked in detail
  (paper not fully read past the abstract/citation chain) but the exponent and its position in the chain is
  confirmed by every later paper (Bui 2025, McClenagan 2026) citing it identically.

### F6. F. Chung, R. Graham, "Efficient Packings of Unit Squares in a Large Square", Discrete Comput. Geom. 64(3) (2020) 690–699 — **claim later shown flawed, see F7.**
- URL (preprint, identical content to published version): https://fanchung.ucsd.edu/wp/spacking.pdf.
  DOI 10.1007/s00454-019-00088-9.
- **Claims (Theorem 1, as stated in the paper):** W(x) = O(x^{3/5}), improving their own 2009 bound
  O(x^{(3+√2)/7} log x) (they do not cite or compare against Wang–Dong–Li's intervening O(x^{5/8})).
  **This claim was invalidated in 2025 — see F7 — the exponent 3/5 turned out to be correct, but this specific
  paper's proof of it is broken.**
- **Method (verified by full read of the PDF):** three-stage construction. Stage 1: partition S(x) into an
  integral-side square plus two rectangles of short side x^{4/5}. Stage 2: pack the rectangles with tilted
  stacks of M+1 unit squares (tilt θ ~ 1/√M ~ x^{-2/5}), leaving trapezoids with top edge x^{2/5}. Stage 3:
  subdivide each trapezoid into ~x^{2/5} sub-trapezoids B_i of height ~x^{2/5}, "serrate" the right-hand edge
  by removing x^{1/5} small triangles per B_i, then fill with stacks of height m = ⌈b_0⌉+1, tracking nine
  named waste terms W1,…,W9(x), each separately bounded O(x^{3/5}).
- **The bug (per Arslanov–Bui, F7):** it is in the computation of **W5(x)**, defined on p. 8 of the PDF — the
  term bounding "the elongated triangle between two [tilted stacks with slightly different tilt] within a
  serrated B_i" (their Fig. 9). Arslanov–Bui show the angle-difference computation there is wrong and,
  worse, give a triangle-inequality argument that the true bound the authors' own method can support is
  weaker than O(x^{3/5}) as stated — so Theorem 1 as proved in this paper does not follow from the argument
  given (whether some other repair of the same skeleton recovers 3/5 is exactly what F8–F10 settle, in the
  affirmative, by different means).

### F7. M. Z. Arslanov, H. D. Bui, "Note on 'Efficient Packings of Unit Squares in a Large Square'", Discrete Comput. Geom. (2025), DOI 10.1007/s00454-025-00767-w, published online 3 Aug 2025.
- URL: https://link.springer.com/article/10.1007/s00454-025-00767-w (Springer paywall — blocked automated
  fetch; content below is reconstructed from the citing sentence in Bui's own arXiv:2508.04603 v2 §1, which
  quotes it directly: **"[Chung and Graham (2019)] claims W(x) ∈ O(x^{0.6}), but [Arslanov and Bui (2025)]
  shows that there is a technical error in the calculation of W₅, with W₅ defined on [Chung and Graham, 2019],
  p. 8."** — matches exactly the W5/Fig.9 term identified independently by reading the Chung–Graham PDF
  itself (F6). Also per web search of the abstract: the note illustrates the error "by directly analyzing
  where the mistake arose in an angle computation, and by checking against a simple geometric argument using
  the triangle inequality" — **not independently read in full (paywalled); treat the mechanism description as
  secondary-source-confirmed, but the *existence* and *location* (W5, p.8) of the error is corroborated by two
  independent sources (the citing sentence in Bui 2025, and my own read of the flawed Fig. 9 argument in the
  original PDF).**
- M. Z. Arslanov is the same author as Arslanov–Mustafin–Shangitbayev (already in §D, EJC 28 (2021)
  #P4.22, on s(n²−n) < n) — i.e. this is a group that also works on small-n exact packings, not purely
  asymptotics.
- **This appears to be new information relative to the existing docs/literature.md §D one-liner** ("Chung–
  Graham 2020... O(s^{0.6})"), which did not flag that the 2020 paper's proof was subsequently retracted/
  corrected in the technical sense — the *statement* W(x)=O(x^{3/5}) survives (reproved independently below),
  but *this specific paper* should no longer be cited as its proof.

### F8. H. D. Bui, "Square Packing with Asymptotically Smallest Waste Only Needs Good Squares", arXiv:2504.09489 (13 Apr 2025), CCCG 2025.
- URL: https://arxiv.org/abs/2504.09489 / https://arxiv.org/pdf/2504.09489. Local
  `docs/papers/bui2025_good_squares_arXiv2504.09489.pdf` (full text read).
- **Proves (Theorem 1):** W(x) ∈ Θ(W*(x)), where W*(x) is the minimum waste restricted to packings using only
  "good" unit squares — a *good square* (definition taken directly from Roth–Vaughan 1978) is one whose tilt
  relative to the container is ≤ c = 10^{-10}. I.e., **up to a constant factor, only near-axis-aligned squares
  matter for the asymptotics; "bad" (more-tilted) squares can always be surgically removed at a cost that's
  absorbed into the same Θ-class.**
- **Method:** an explicit max-flow/min-cut argument (§3, Prop. 19: a set of "marked" grid cells containing all
  bad squares can be covered by rectangles of total perimeter O(f), where f is the max number of
  vertex-disjoint paths from marked cells to the grid boundary — a genuinely new combinatorial tool, credited
  as a strengthening of Roth–Vaughan's own √|M|-row/column pigeonhole argument) combined with a generalized
  version of Roth–Vaughan's "Lemma 4" fundamental lemma (angle-difference between two squares forces wasted
  area nearby, Prop. 21) extended to handle squares arbitrarily far apart via a path/disk-chaining argument.
  A surgery procedure then cuts out all bad-square regions at O(f) = O(W(A)) extra cost.
- **Direct relevance to A33's grain conjecture (η(n) trend):** this is the closest thing in the literature to
  a formal "grain" theorem. It does **not** show a packing is one single grain — it shows the opposite
  direction is *unnecessary to worry about*: any near-optimal packing can be assumed WLOG to consist entirely
  of squares within 10^{-10} radians of one fixed axis (the container's), with no asymptotic loss. This
  formalizes (for the *asymptotic*, large-x regime — not finite n like our n=11 problem) the intuition that
  "many small oddly-tilted grains" cannot be asymptotically efficient; it does not by itself say how many
  large axis-aligned grains are needed or whether they must all share literally one tilt vs. O(1) many. Open
  problems section explicitly asks (Discussion 6.2) whether the tilt bound can be sharpened from the constant
  10^{-10} to O(1/log x) or O(x^{-ε}) — i.e. whether "good" packings are forced to be *even more* uniformly
  aligned than just "roughly axis-aligned", which is exactly the kind of quantitative grain-purity statement
  A33 would want. Not answered in this paper.

### F9. H. D. Bui, "Square Packing with O(x^{0.6}) Wasted Area", arXiv:2508.04603 (6 Aug 2025, v2 15 Mar 2026).
- URL: https://arxiv.org/abs/2508.04603 / https://arxiv.org/pdf/2508.04603.
- **Proves:** W(x) = O(x^{3/5}) = O(x^{0.6}) — a *correct* independent re-proof of the exponent Chung–Graham
  had claimed (and Arslanov–Bui, F7, had shown their proof of, did not establish). Abstract: "We show a new
  construction for square packing, and prove that it is more efficient than previous results."
- **Explicitly cites the error it is fixing** (v2 §1, quoted in F7 above) and **explicitly acknowledges
  McClenagan's simultaneous independent discovery**: "After putting this manuscript on arXiv, we learnt that
  an equivalent result was independently discovered by McClenagan..., with a somewhat different method."
- Not fully read past the introduction (24 pages, 20 figures; time-boxed). No mention found of fractional/LP
  relaxation or explicit "grain" terminology — purely a geometric tiling construction (continuing the
  Erdős–Graham → Chung–Graham lineage of tilted-stack recursions).

### F10. R. McClenagan, "Optimally Packing a Large Square by Unit Squares", arXiv:2602.01484 (1 Feb 2026).
- URL: https://arxiv.org/abs/2602.01484 / https://arxiv.org/pdf/2602.01484 / https://arxiv.org/html/2602.01484.
  Local `docs/papers/mcclenagan2026_arXiv2602.01484.pdf` (PDF text layer would not extract cleanly through
  either WebFetch or the PDF reader here — compressed/embedded content streams; only metadata-level info
  obtained, flagged below as **not fully verified**).
- **Abstract (verified, exact text):** "A large square of sidelength x can be packed by unit squares in a
  manner so that the wasted space W(x) = O(x^{3/5})." Independent proof of the same exponent as F9, "with a
  somewhat different method" per Bui's acknowledgment (F9). States the work originated in McClenagan's 2024
  doctoral thesis (University of Northern British Columbia).
- **Not verified:** the internal construction/method detail (the extraction tool could only read compressed
  PDF object streams, not render them; one general-purpose secondary extraction pass claimed a "two
  alternating sub-algorithms... horizontal stacks and vertical stacks" structure with parameters φ, ψ, θ′, m′,
  but this should be treated as unconfirmed until the PDF is read properly, e.g. by downloading and running a
  real PDF-to-text tool rather than the lossy extraction attempted here). Also unverified: whether it discusses
  the lower-bound side, fractional/LP methods, or grain structure — a first-pass secondary summary said no to
  all three, but this is not confirmed against primary text.

### F11. What was searched and not found in this sweep
- **No post-2020 improvement below the 3/5 exponent.** Searched arXiv (math.CO, math.MG, cs.CG) for
  "packing unit squares", "square packing wasted area", "wastage exponent" combined with 2021–2026: nothing
  found beating O(x^{3/5}); the two 2025–26 papers (F9, F10) both land exactly on 3/5, not below it.
- **The lower-bound gap (1/2 vs. current-best ~0.6 upper bound) is still open.** No paper found that improves
  Roth–Vaughan's exponent 1/2 in either direction (no better lower bound, no proof that 1/2 is tight). Chung–
  Graham 2009 explicitly bet ($1000, apparently unclaimed) that it is *not* tight, i.e. that
  W(x) ≫ x^{1/2+c} for some c > 0 — the opposite of Erdős–Graham's own 1975 guess.
- **No fractional-packing / LP-relaxation treatment of this problem found anywhere** — confirms and extends
  §E's earlier finding (which was scoped to the finite-n / s(11)-adjacent literature): searched specifically
  for "LP relaxation unit square packing", "fractional packing duality square container" and found only
  generic 2D bin-packing/cutting-stock LP-relaxation literature (item-area/container-area continuous bound,
  online rectangle packing LP duality) with no connection to this x²-vs-⌊x⌋² asymptotic problem or to finite
  n like s(11).
- **No formal "grain"/crystalline-structure paper.** The closest is Bui's "good squares" reduction (F8),
  which is a *removal* result (bad-tilt squares can be surgically deleted at no asymptotic cost) rather than a
  positive structural theorem about grain count, grain size distribution, or grain-boundary energy. No
  physics-style heuristic/crystalline literature on this specific discrete problem was found (searched
  "square packing crystalline defects", "grain boundary unit square tiling" — only returned unrelated
  materials-science hits).
