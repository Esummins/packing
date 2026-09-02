import PackingCertMathlib.Corpus.K61
import PackingCertMathlib.Corpus.TRAP
import PackingCertMathlib.Corpus.P1
import PackingCertMathlib.Corpus.THMU

/-!
# A78 T5 -- the four DONE certificate corpora, replayed in Lean

Root of the `PackingCertCorpus` lake library (a SECOND lean_lib, so the
default target / CI is unchanged).  Build it with
`python attempts/A78-lean-wave6/code/lakeb.py PackingCertCorpus`,
or a single certificate with
`... lakeb.py PackingCertMathlib.Corpus.K61.Check_k5_06`.

* `corpus_K61` -- the 61 pin-set kills of the A53/A54/A55 cap (C.K61);
* `corpus_TRAP` -- the six trapped k6 classes (D.TRAP, a view of C.K61);
* `corpus_P1` -- the trump5 interior residual (D.P1);
* `corpus_THMU` -- the 11 Theorem-U re-insertion certificates (A.THMU).
-/
