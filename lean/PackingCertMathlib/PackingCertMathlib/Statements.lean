import PackingCertMathlib.Statements.Attainment
import PackingCertMathlib.Statements.LowerBound382
import PackingCertMathlib.Statements.Parametrization
import PackingCertMathlib.Statements.Dilation
import PackingCertMathlib.Statements.CaseVerifier
import PackingCertMathlib.Statements.WindowsClause
import PackingCertMathlib.Statements.GuardLines
import PackingCertMathlib.Statements.Stratification
import PackingCertMathlib.Statements.Tube
import PackingCertMathlib.Statements.Basin
import PackingCertMathlib.Statements.UniqueTransfer
import PackingCertMathlib.Statements.SlotCrowd
import PackingCertMathlib.Statements.NoRoom
import PackingCertMathlib.Statements.Composition
import PackingCertMathlib.Statements.Open.StratumKill
import PackingCertMathlib.Statements.Open.TrumpResidual
import PackingCertMathlib.Statements.Open.A22ExactStructure
import PackingCertMathlib.Statements.Open.TheoremFC
import PackingCertMathlib.Statements.Open.TheoremCOUNT
import PackingCertMathlib.Statements.Open.ClipTree
import PackingCertMathlib.Statements.Open.RoleSplit
import PackingCertMathlib.Statements.Open.NoRoom189
import PackingCertMathlib.Statements.Open.CornerCover
import PackingCertMathlib.Statements.Open.BasinLemma
import PackingCertMathlib.Statements.Open.TubeLeaf
import PackingCertMathlib.Statements.Open.K0Count
import PackingCertMathlib.Statements.Open.LemmaCEIL
import PackingCertMathlib.Statements.Open.TwoContact
import PackingCertMathlib.Statements.Open.OneTilted
import PackingCertMathlib.Statements.Open.RingSwap
import PackingCertMathlib.Statements.Open.TwoGrains
import PackingCertMathlib.Statements.Open.OneFlush
import PackingCertMathlib.Statements.Open.LemmaEps
import PackingCertMathlib.Statements.Open.Realign
import PackingCertMathlib.Statements.Open.LocalLock
import PackingCertMathlib.Statements.Open.NoVV
import PackingCertMathlib.Statements.Open.RingCapacity
import PackingCertMathlib.Statements.Open.PocketWaste
import PackingCertMathlib.Statements.Open.WedgedSeal
import PackingCertMathlib.Statements.Open.Cross
import PackingCertMathlib.Statements.Open.Stuck4
import PackingCertMathlib.Statements.Open.SnapDown
import PackingCertMathlib.Statements.Open.StuckExist
import PackingCertMathlib.Statements.Open.PerimeterWalk
import PackingCertMathlib.Statements.Open.CornerChase
import PackingCertMathlib.Statements.Open.TypeTChase
import PackingCertMathlib.Statements.Open.FamilyStuck
import PackingCertMathlib.Statements.Open.RingPocket
import PackingCertMathlib.Statements.Open.CentreDisc
import PackingCertMathlib.Statements.Open.Peel
import PackingCertMathlib.Statements.SnapRule
import PackingCertMathlib.Statements.SwapLeaf

/-!
# The readable layer, one import (A216)

`Statements/` — one small file per key result (statement, prose docstring, proof imported,
`#print axioms`); `Statements/Open/` — the obligations that are still prose or certificates,
as named axioms (or, where the logical core is trivial, one-line theorems) with pointers.
`lean/audit.py` builds this module and `Main.lean` and writes `lean/AUDIT.md`.
-/
