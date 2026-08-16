# Lab notebook (append-only, newest at bottom)

## 2026-08-16 — advisor — project start
- Repo initialised. Only prior artefact: `chat_history.txt` (a previous Claude session that derived
  the exact algebraic description of the Trump/Gensane–Ryckelynck 11-square packing and produced a rational
  certificate; those files were not saved, only the transcript).
- Environment: Python 3.14 (numpy/scipy/mpmath/sympy/matplotlib/shapely installed), 20 CPUs, no Lean yet.
- Wrote README, docs/known_results.md (seeded, unverified), docs/ideas.md, attempts/REGISTRY.md.
- Dispatching A01–A07 in parallel (see REGISTRY).

## 2026-08-16 — A01-literature (lit agent) — done
- Sweep of Friedman DS7 (2009), Stromquist 2003 (+1984 memos), Gensane–Ryckelynck 2005, Nagamochi 2005,
  Kearney–Shiu 2002, Bentz 2010/2016, Montanher–Neumaier–Markót–Domes–Schichl 2019, Ellsworth's "Squares in
  Squares" (to Feb 2026), Wikipedia/MathWorld/OEIS, arXiv API, Semantic Scholar forward citations.
- Outcome: bounds confirmed — 2+2·sqrt(4/5) = 3.788854 (Stromquist 2003, Thm 2; nothing newer exists) ≤ s(11)
  ≤ 3.877083590022814 (Trump 1979; exact octic s⁸−20s⁷+178s⁶−842s⁵+1923s⁴−496s³−6754s²+12420s−6865 published by
  Ellsworth 2023, agrees with G–R 2005's angle polynomial and with chat_history.txt). Attribution corrected: G–R
  did not improve Trump's packing, only its digits. s(12) is also open. "Vienna" interval B&B = JOGO 2019 paper
  (3 unit squares in a circle). No LP/SDP bounds and no Lean/Isabelle/Coq formalisations exist for this problem.
- Files: docs/literature.md (new), docs/known_results.md (rewritten, [verified] tags), docs/papers/ (11 PDFs +
  txt extractions + Ellsworth pages + n=11 SVG with exact parameters), attempts/A01-literature/notes.md, REGISTRY.

## 2026-08-16 — advisor — session-limit interruption
- All six computational/analysis agents (A02–A07) were killed mid-run by an API session limit; partial code and
  data survived on disk. Resumed each agent from its transcript with pointers to its partial work.
- Correction broadcast to A04: its "CANDIDATE" files (s ≈ 3.87708359224) are re-discoveries of Trump's packing,
  2.2e-9 ABOVE the exact record 3.877083590022814 (the threshold had been my rounded 3.877084).

## 2026-08-16 — advisor — second interruption (OAuth expiry) and re-dispatch
- All agents died again (401). Partial results on disk before death: A07 LP logs show τ*(3.7071)=10.000 for the
  n=10 calibration (LP method reproduces Stromquist's exact s(10)), and for n=11 τ*(3.65)≈9.37, τ*(3.80)≈10.43,
  τ*(3.85)≈11.07 (grid LP, row generation, not yet rigorous). A05: best pure 10-point unavoidable set s0≈3.751
  (< 3.7889) ⇒ point method alone cannot beat Stromquist. A04: Trump packing rediscovered repeatedly, nothing below.
- Re-dispatched A02–A07; spawned A08-measure-verify (independent exact-rational verifier for measure certificates)
  and asked A06 to prototype the Lean checker for measure certificates (I-C2). Critical path: A07 → A08 → A06.
