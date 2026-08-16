# A01-literature — notes

**Goal.** Establish the true state of the art for s(11) (bounds, attributions, methods) with primary sources;
fetch PDFs; correct `docs/known_results.md`.

**Method.** Web search + direct fetch of EJC/arXiv/Springer PDFs (curl), Friedman's survey (2009 github copy +
PDF), Ellsworth's "Squares in Squares" pages and the n=11 SVG source, Wikipedia wikitext, MathWorld, OEIS,
Semantic Scholar forward-citation lists for Stromquist 2003 / Bentz 2010 / Nagamochi 2005 / Friedman DS7 /
Gensane–Ryckelynck 2005, arXiv API sweeps (7 query variants, all years). Text-extracted PDFs with PyMuPDF and
read the relevant sections. One numerical cross-check (mpmath, 40 digits): G–R's Q(√2)-polynomial in
cos(45°−θ), Ellsworth's octic and sec-θ polynomial, and `chat_history.txt`'s cos-θ polynomial all agree at
θ = 40.18193729032971646523° / s = 3.87708359002281417730789706.

**Result.**
- Lower bound: s(11) ≥ 2 + 2·sqrt(4/5) = 3.788854… (Stromquist 2003, Thm 2). No improvement anywhere
  2003–2026. Stromquist's argument: 10-point *almost*-unavoidable set + one forced box containing 3 of a
  12-point unavoidable set; the value is fixed by the unit-triangle lemma; the second stage is "not rigid"
  (Stromquist's words) — slack exists.
- Upper bound: 3.877083590022814177… = root of s⁸ − 20s⁷ + 178s⁶ − 842s⁵ + 1923s⁴ − 496s³ − 6754s² +
  12420s − 6865 (Ellsworth 2023, confirmed by Alexeev; consistent with G–R 2005's angle polynomial). Packing
  is Trump's 1979 rigid configuration; G–R 2005 only refined digits, they did not improve it. Not improved
  by the 2024–26 SA campaigns (Schadt/Ellsworth/Cantrell/Hajba). Full exact parameters incl. the equal gaps
  u1 = 0.02487453502559695… are public in `docs/papers/ellsworth_square-11.svg`.
- s(12) is also open (3.7889 ≤ s(12) ≤ 4). Wikipedia's table is misleading on this.
- The "Vienna" interval B&B = Montanher–Neumaier–Markót–Domes–Schichl, JOGO 2019: rigorous solution of
  3 unit squares in a circle (tiling constraints + GloptLab). Nothing rigorous exists for squares in a square
  beyond hand proofs; no Lean/Isabelle/Coq formalisation exists.
- Newest lower-bound-side works: Bentz 2010 (s(13)=4, s(46)=7), Bentz arXiv 2016 (s(22)=5, s(33)=6 via
  continuously varying families of unavoidable sets), Bašić–Slivková DAM 2018 (piercing number of unit squares
  in an n×n square; paywalled).
- Kearney–Shiu 2002's "duality" proof of s(6)=3 is the earliest weighted/multi-set unavoidable argument —
  a concrete precedent for the fractional (LP) approach in I-L2.

**Deliverables written.** `docs/literature.md` (annotated bibliography, URLs, per-item method paragraphs);
`docs/known_results.md` (rewritten with [verified: …] tags and corrections); `docs/papers/` (11 PDFs + text
extractions + Ellsworth pages/SVG + Wikipedia wikitext); REGISTRY line; LOG entry.

**Could not obtain.** Göbel 1979 (print only); Trump 2023 ResearchGate preprint (403; content known from
snippets); Bašić–Slivková 2018 (paywalled — worth a library request: it is the one paper about the *minimum
size of unavoidable sets*, i.e. the ceiling of I-L1); Stromquist's 1984 memoranda are image scans (no OCR).

**Leads for other attempts.**
- A02: binding constraint = Lemma 2 (unit triangle) on the middle-row spacing of Fig. 13; Fig. 14 has slack;
  compare Bentz 2010's finer case trees and Bentz 2016's parametric families for how to spend more cases.
- A05/A07: Kearney–Shiu duality shows multi-set/weighted covers work; Bašić–Slivková's piercing number τ is
  exactly the object A05 optimises (10-point sets in side s); the LP dual (fractional piercing) is the ceiling.
- A03: Ellsworth SVG gives 33-digit s, θ and all offsets; G–R's angle polynomial and Ellsworth's two-equation
  Mathematica derivation are independent checks of the exact reconstruction; Ellsworth's "analytic
  minimisation" note explains the anti-parallel-gradient trick for underdetermined contact systems.
- I-L4: the Vienna paper's tiling-constraint decomposition (each tile holds ≤ 1 centre) and iterate-on-number-
  of-squares strategy are directly transplantable to a square container.

**Next steps.** None for A01 (done). Suggested: request Bašić–Slivková PDF; OCR Stromquist memo III if A02
wants the 1984 version of the n=11 argument.
