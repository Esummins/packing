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
- Asymptotics (not directly relevant): Erdős–Graham 1975 W(s)=O(s^{7/11}); Roth–Vaughan 1978 lower bound;
  Chung–Graham 2009 (O(s^{0.631})) and 2019 DCG "Efficient packings of unit squares in a large square";
  Wang–Dong–Li arXiv:1603.02368 (O(s^{0.625})); McClenagan 2024 thesis / arXiv:2602.01484 (O(s^{0.6}));
  H. D. Bui arXiv:2504.09489, arXiv:2508.04603 (O(x^{0.6}) construction, 2025–26); Praton math/0504341,
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
