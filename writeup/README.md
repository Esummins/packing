# writeup/ — the three documents of the s(11) lab

Living documents, edited IN PLACE (no attempt agents for edits; the coordinator and the PI revise directly).
Started 2026-09-09 at the PI's request.

| file | audience | what it is |
|---|---|---|
| `01_summary.md` | anyone | 1–3 pages, plain language: the result, why it was open, how it was done, what the AI could not do alone and how the PI's systems filled the gaps, status of the certificates |
| `02_mathematics.md` | mathematicians / the certificate reader | the full mathematical write-up: definitions, every lemma the proof needs (stated for general n where possible), how they compose into s(11) = ŝ with uniqueness, what is Lean-checked, what is certificate-backed, what is pending compute |
| `03_lab_timeline.md` | AI–mathematics practitioners | the lab timeline in detail: the attempts, the dead ends, where the AI got stuck and the PI unblocked it, the visualisation loop (SVG pages → readings → leaves), and why the composite exceeded either party alone |
| `04_related_work.md` | anyone placing this work | a survey of recent AI-assisted mathematics results categorised by interaction depth, who managed the AI, the human's training, what the human contributed, and verification; where this lab sits and what is and is not novel about it |

`sources/` holds raw material copied from outside the repo (the coordinator's dated lab memory, the drawing rules,
the standing priority rules); `figures/` holds the figures the documents cite (copied, not linked, so the
directory is self-contained). Primary in-repo sources: `LOG.md`, `attempts/REGISTRY.md`, `docs/known_results.md`,
`docs/residue_ledger.md`, `docs/budget.md`, `docs/proofs/*.md`, `docs/paper/outline.md`, `lean/`.

Conventions: every mathematical claim carries its status tag ([T] proved in the notes, [L] Lean-checked,
[C] certificate-backed, [P] pending compute, [S] supported, [M] measured); every timeline claim cites the
attempt id (A###) and the date; nothing is stated as done that is not.
