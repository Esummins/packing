# A57 — the shadow trees: kill k5_11 and k5_16 (Opus)

Goal: close the two surviving non-Trump k=5 strata by A54's priced rung-3 route. Context: A54
results (rung-3 pricing: NO-children free, YES-children alive at coarse cores; the A24(iii) kill
threshold — core half-width a >= 0.35 kills, <= 0.28 alive; needs centre boxes <= 0.1 and theta
windows <= 15 deg => ~612 children per side zone, ~6000 interior; notes/lemmas.md S0-S5), A53/A54/
A55 machinery + ALL banked levers (merged warm start + checkpoint folding — see A55 k3_ext/ E1-E5:
interrupted passes lose nothing, atoms are the progress variable; lifted scale ceiling; column-only
pruning; cheap-cert every round; detached Start-Process for >55min jobs), A54's Trump-ghost
characterization of these two strata (their optima ARE Trump's ghost re-decorated — expect the
hard children where the ghost's interior/side mass lives).
Protocol per stratum: sub-stratify the residual on ONE additional square (the A24 interior-first
zone scheme adapted to the residual region); breadth-first with easiest-first ordering; every kill
exact-certified; children that stay at budget get one more level (depth <= 2 total); D4/symmetry
transfers machine-checked where applicable. Trump canary: trump5 never touched; k5_16's corners4
parentage means its interior children overlap A14 lore — reuse rows. Budget: this is the ~2
desktop-day item — checkpoint everything, run detached, report per-level progress files (no
heartbeat turns). <= 3 heavy processes while A56's sweep runs, 5 after it completes. Registry, LOG,
scoreboard report: killed / alive-characterized per child, the stratum verdicts.
