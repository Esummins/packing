# A277 -- room at the FLOAT2 and indirect-jam corners: outline

Agent: Fable 5.1 theory agent. Working rule: tiny steps, one tool call per turn,
each part <= 60 lines, committed before the next.

Plan (each item becomes one or more parts):

1. part1: reading notes -- BRIEF.md, k0_knowledge.md (1,2,5,7,8), no_jam.md,
   float262.json; what NO-JAM(11) link 5d actually needs; exact definitions.
2. part2: FLOAT2 corner -- geometry of the configuration class; the precise
   "room" statement to be proved (n-general form); tags [T]/[M]/[C].
3. part3: proof attempt of the FLOAT2 room lemma from normal_room / strip_enclosure /
   strip_jam / flat_x / ring_domain / box_meeters / locked_wall; list every hypothesis.
4. part4: indirect-jam corner -- reduction to a direct-jam or room statement;
   what remains as a computation.
5. part5: certificate design (if a computation is needed): domain, price estimate,
   launch command; exact-geometry witness checks.
6. part6: status table -- what NO-JAM(11) still lacks; errors found in the brief.
7. Lean: Statements/ entry + Open/ axiom if the lemma is prose-only; audit 0 sorry.
8. Append entries to docs/proofs/k0_knowledge.md; final 12-line report.
