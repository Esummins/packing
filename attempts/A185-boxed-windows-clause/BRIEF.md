# A185 — the BOXED-WINDOWS clause of the case-measure certificate (Fable lead, 2026-09-09 ~19:40)

## The problem (PI)
The case-measure certificate (v1 = frozen `attempts/A57-shadow-trees/code/verify_case.py`, sha `521cb01f...`;
A135's `verify_case_v3.py` adds the polygon-core clause; A144 `notes/spec.md` §4 specifies a v4 that imports both
and adds the guard-line clause) constrains the adversary only through the FREE squares: every admissible non-exempt
pose must carry ≥ 1 unit of measure.  A boxed square enters only through its core (exempting the free poses that
meet it), so the budget is `n − #cores` and a node with every square boxed has budget 0 and a VACUOUS certificate.
A182's eight complete assignments of `c0_Y1033` at budget 0 (`attempts/A180-forced-first-assignment/results/trees/
c0_Y1033.json`, journal `results/journal/c0_Y1033.jsonl`) and A183's `root/D0/S1` on `l1_104` (`lp183.py`,
τ = budget = 8, ALIVE(LP)) are exactly this.

## The fix (PI)
Confine each boxed adversary square to its designated WINDOW (the role's surviving pieces) and require it to cover
≥ 1 unit of measure at EVERY pose of its window, so n confined squares must carry n units against a total below n.
The core exemption stays on top: measure on a core is inside every pose of that window for certain; the exact
combination (no double counting) is Theorem W of `docs/proofs/boxed_windows.md`.

## Build
1. `docs/proofs/boxed_windows.md` — the `windows` field, Theorem W [T] (with cores), the n-general form, the Lean shape.
2. `code/verify_case_v4.py` — NEW file importing v1 verbatim and A135's v3 (shas asserted), adding the `windows`
   clause: the same exact pose enumeration v1 runs over the container, restricted to the window's pieces (cheaper).
   Guard-line clause: stub with the spec pointer (A144 §4; `guardline.minchord_box` exists, the emitter does not).
   Regression `code/regress185.py`: 50 PASS + 50 FAIL v1 certificates from A149/A57 give the identical verdict AND
   identical box-tree statistics under v4 (windows absent ⇒ v1 byte-for-byte behaviour).
3. `code/winlp185.py` + `code/run185.py` — the emitter: multi-box case LP (lp183/lp168 pattern) where a boxed role
   contributes its window rows (poses in its pieces, exempt only by OTHER windows' cores) AND its grown core; runs on
   A183's `root/D0/S1` (before: τ = 8 = budget) and A182's eight budget-0 assignments + its ALIVE(LP) node.  Every
   kill is [C] under v4 ONLY — the frozen v1 chain is untouched and stays byte-identical.
4. `docs/residue_map/boxed_windows_S1.svg` — one node before/after (support, windows dashed, cores filled, worst
   pose per window, τ and budget printed).
5. Ledger §5 paragraph, budget §D item, registry row, LOG entry, known_results line; commit at every milestone.

## Rules
≤ 2 python processes at BelowNormal / affinity 0xFFFF; box ceiling 12 pythons counted by image name with relative
command lines (the four `windows-mcp` venv pythons of the Claude desktop are not lab workers and are excluded from
the count; A183 ×3, A184 ×2, A182 ×1, A177 ×2 were running at start); 6144 MB commit + > 3 GB free physical before
each LP; 1,500 s wall per node killing the process tree; read-only on every other attempt; frozen verifiers never
edited; no recursive deletes; `PYTHONDONTWRITEBYTECODE=1`.  Labels [T]/[S]/[M]/[F]/[C].
