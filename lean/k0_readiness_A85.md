# k0_00 readiness note (A85, 2026-09-02) — no Lean edits

Full text: `docs/proofs/k0_route.md` §9. Summary for the Lean owner:

1. The k0_00 instance of `stratum_kill` built from Lemma K0-FREE (teleport into the MONOTONE
   k1_00 hypothesis, `teleport_packing` + `class_kill`) and the residual tree with
   (K)/(C)/(T)/(D)/(D′) leaves is a ∀-packings statement: it instantiates `stratum_kill` AS
   STATED. No selection, no `TeleportStuck`, no exact-skeleton bridge.
2. The selected form is needed only if minimality-based leaves are used (Lemma K0-ROT
   rotation-descent leaves, stuck rows). Then split the axiom:
   `stratum_kill_all` (classes in AllForm, as today) and
   `stratum_kill_min : ∀ i ∈ MinForm, ∀ s ∈ wnd, ∀ z, CfgPacking s z →
      (∀ s' z', CfgPacking s' z' → s ≤ s') → ¬InStratum i s z`.
   The hypothesis is supplied by (a) the attained minimiser z* of `attained_thm` (B.SEL) at
   the lower bound's single use of `stratum_kill` after `exists_stratum` (B.CENSUS), and
   (b) at side ŝ by the bound itself (every packing at ŝ is a minimiser) for
   `s_eleven_unique` / `unique_via_chain`'s `hstuck`. Two `have hmin` lines; no other consumer.
3. New checker clauses the k0_00 corpus replay would need: (T) leaves (a NO-family on a
   corner box ⇒ `teleport_packing` ⇒ the k1_00 instance), (D′) leaves (A37 atlas boxes as
   value certificates σ ≥ V ≥ s0 — not yet in the Lean corpus; the re-checker
   `attempts/A37-cp-atlas/code/a37_check.py` is the current arbiter), and, optionally,
   rotation-descent (a rational rotation + interval σ-decrease over the box; no derivatives).
4. Nothing here is edited in `lean/`; this note only.
