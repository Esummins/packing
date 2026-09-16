"""A233 write-up: append the LOG entry and insert the ledger s.4 note (idempotent).  python writeup233.py"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
LOG = os.path.join(ROOT, 'LOG.md')
LEDGER = os.path.join(ROOT, 'docs', 'residue_ledger.md')

LOG_ENTRY = """
## 2026-09-15 20:xx -- A233-local-lock (Fable) -- DONE (launch-and-exit; no long runs: the arm census + tests take 30 s, the Lean build 230 s + audit): **the extremal route is n-general and gives ONE-FLUSH(n) in its VALUE form from ONE residue (a retreat-free four-crowd at the optimum); the brief's per-corner LOCAL-LOCK is refuted by Trump's own TL corner; LOCALITY holds but the lock problem is not local -- every retreat cluster leaves the arm; Lemma RADIAL / Corollary CHAIN make the PI's gear rule a theorem for all n (A219's RING 193/193 included) and exclude nothing**
- PI, 17:50: *"an analytical reason for at least one simple square, since that would generalise up and allow us to ignore k0 for higher n without re-searching."*
- **[T] Theorem EXTREMAL(n)** (`docs/proofs/local_lock.md` s.1): at s(n) < ceil(sqrt n) take the Psi-minimal packing among the
  optimal ones (Psi = total corner intrusion); nothing RETREATS there (Lean `no_retreat_of_psiMin`), so either a corner is singly
  met -- K0-FREE settles it and s(n) is attained WITH A FLUSH CORNER, the census of n squares starts from a settled corner --
  or the optimum is a four-crowd all of whose meeters are retreat-free (hence LOCKED, Lemma ROT/ROT-W).  The residue
  **LOCKED-CROWD-FREE(n)** [C]: Lean axiom `locked_crowd_free`; `exists_optimal_singly_met` = ONE-FLUSH(n) (value) from it;
  `optimal_psiMin_not_stuck` the n = 11 corollary.  Weaker than LOCK-FREE+ (optimal packings only).  Table of which pieces
  are proved n-general (D1, teleport, k-maximal, Psi-minimal, NOCRIT-SEL, ROT, ROT-W, PUSH/HOLD/TWO-CONTACT/ONE-TILTED, all
  for s >= 2 + sqrt2) and which are n = 11 (Theorem U, basin, k1-b: uniqueness only).
- **[F] the per-corner target** "no corner doubly met by locked meeters at a k-maximal minimiser below ceil(sqrt n)": Trump's
  TL (sq4 nick + sq6 carrier, 5/5 LOCKED in `lockfree.md`) is exactly that at a k-maximal minimiser below 4.  Locked corners
  are how a load path ends; ONE-FLUSH is about a corner where none ends.  Nothing per corner can prove it.
- **[T] LOCALITY** (s.2): a meeter's centre is in [1/2, 1 + 1/sqrt2)^2, a row partner's within sqrt2 of it, so the lock's
  Gordan certificate reads poses inside the ARM [0, 1 + 2 sqrt2]^2 (centres [1/2, 1 + 3/sqrt2)^2); the four locks live on
  disjoint square sets for s >= 2 + 3 sqrt2 = 6.243 (n >= 39), the arms are disjoint for s >= 7.657 (n >= 59); at n = 11 the
  arm is the container.  [M] 1,227/1,227 doubly-met corners (A217's 486 witnesses + Trump): every holder inside the arm.
  **[T] but not local:** NOCRIT-SEL's retreat cluster of a locked meeter is wall- or crowd-anchored, both outside the arm for
  s > 2 + 2 sqrt2 = 4.83 -- the chain always leaves the arm (the PI's gear rule, exactly).  [M] 3,955/4,908 clusters anchored,
  all but 8 leave the arm.
- **[T] Lemma RADIAL** (s.3, any n, any FJ point): for any set U of squares, the rows joining U to the outside carry a net
  CORNER-WARD push equal to minus a positive combination of the internal loads (dot the centre balance with the position
  vectors from the corner; a pair row contributes n.(c_j - c_i) = 1/2 + g_j(n) >= 1, a corner-wall row c_u >= 1/2).
  **Corollary CHAIN:** the loaded component of a loaded crowd reaches a far wall -- A219's RING (193/193 measured) is a
  one-line theorem for all n; [M] 1,013/1,013 loaded crowds here, identity residual <= 5e-7.  **NO-SELF-STRESS:** lam0 = 1
  at every FJ point.  All satisfied by Trump (TL's chain is the strip; pushers sq7 0.199 + sq9 0.317 = the internal load
  0.516) and by the ring (BL's pushers are the adjacent crowds' meeters): they describe a load path, they exclude nothing.
- **[M] the local census:** 75 realised arm signatures; the abstract list (cells x wall rows x depth type x partner x holder
  rows) is 3.75e5 (H = 3) .. 1.65e6 (H = 5) labelled row lists per arm vs A219's 2.6e11 -- finite and small, and it decides
  LOCKED only.  **Verdict: the route does NOT reduce to a finite local obligation**; LOCKED-CROWD-FREE(n) is a global frame
  statement at the optimum whose proof must couple the four chains through s < ceil(sqrt n), and no length lemma for a
  pressed chain exists (a loaded contact can advance arbitrarily little along a wall).  At n = 11 it is RAISE(0 -> 1) /
  STEP as A222/A231 left it; k0_00 unchanged.
- Files: `attempts/A233-local-lock/{code,results,logs}`, `docs/proofs/local_lock.md`,
  `docs/residue_map/campaigns/A233-local-lock/` (2 pages, 11 panels, geometry check printed per panel),
  `lean/.../Statements/Open/LocalLock.lean` (+ one import line in `Statements.lean`; build + audit exit 0, no sorry),
  registry row, ledger s.4 note.
"""

LEDGER_NOTE = """
**[T]/[F]/[M]/[C] A233 (2026-09-15 night) — LOCAL-LOCK: the extremal route for every n, the corner arm, Lemma RADIAL (`docs/proofs/local_lock.md`).**  [T] Theorem EXTREMAL(n): the Ψ-minimal optimal packing has no retreating square (Lean `no_retreat_of_psiMin`), so ONE-FLUSH(n) in its VALUE form — s(n) attained with a flush corner, the census starts from a settled corner — follows from ONE residue, LOCKED-CROWD-FREE(n) (no optimal packing below ⌈√n⌉ is a retreat-free four-crowd; Lean axiom `locked_crowd_free`, weaker than LOCK-FREE⁺), everything else in the route (teleport, k-maximal, NOCRIT-SEL, ROT, ROT-W) being n-general for s ≥ 2 + √2 and only Theorem U / the basin n = 11.  [F] The brief's per-corner target is refuted by Trump's TL (a LOCKED 2-crowd at a k-maximal minimiser below 4).  [T] LOCALITY: the lock is decided inside the arm [0, 1 + 2√2]² (1,227/1,227 corners), the four locks are independent for n ≥ 39 — but every retreat cluster leaves the arm for s > 4.83 (NOCRIT-SEL), so the problem is not local.  [T] Lemma RADIAL / Corollary CHAIN: a loaded arm needs a corner-ward push from outside; the loaded component of a crowd reaches a far wall (A219's RING 193/193 is now a theorem, all n); NO-SELF-STRESS (λ₀ = 1).  [M] the local census: 75 realised signatures, ≤ 1.7·10⁶ row lists per arm vs 2.6·10¹¹ — it decides LOCKED, which does not contradict optimality per corner.  **This row is unchanged**: the residue is a global frame question at the optimum, not a finite local obligation; at n = 11 it is RAISE(0 → 1) / STEP.
"""


def main():
    log = open(LOG, encoding='utf-8').read()
    if 'A233-local-lock (Fable)' not in log:
        open(LOG, 'a', encoding='utf-8').write(LOG_ENTRY)
    s = open(LEDGER, encoding='utf-8').read()
    marker = '\n## 5. Lean / TCB'
    assert marker in s
    if 'A233 (2026-09-15 night)' not in s:
        s = s.replace(marker, LEDGER_NOTE + marker, 1)
        open(LEDGER, 'w', encoding='utf-8').write(s)
    print('ok')


if __name__ == '__main__':
    main()
