# A251 -- POCKET(11) on the family-stuck ring family, certified: the pocket of every all-ADJ type-T ring on the
# window holds at most one square, so 8 + 1 < 11 (from A249/A250, 2026-09-17 16:00).
Opus. LAUNCH-AND-EXIT -- NEVER wait for a detached run: launch, write the report from what is finished, exit; a
cheap follow-up reads the rows later.  Ops: short responses, files <= 250 lines, no monitors, explicit-pathspec
commits, PYTHONDONTWRITEBYTECODE=1, at most 2 python processes (BelowNormal, affinity 0xFFFF; the k5 frontier,
A238, A241, A244 lanes, A247 triples, A249's finisher and A250's lanes are running -- never touch them).
Read first: docs/proofs/type_t_chase.md (A249: the all-ADJ type-T RING exists at s-hat -- 8 tilted wall touchers, a
14.6-deg pinwheel, all 12 border cells doubly met, family-stuck as an incidence structure with one poking free
square (A250's exact minimum 9); its pocket: PIERCE(1) residual 0 in a pilot => capacity <= 1 => 8 + 1 = 9 < 11:
"the ring dies by the room, not by a wall inequality"; T-CELLS / T-TIP / T-SLOTS closed forms; the ladder rows in
results/ and logs/finish249.log), family250.md (FAMILY-STUCK; at s >= 4 a theorem; below 4 the count minimum is 9;
the family-stuck search finds nothing on [3.82, 4.6]), pocket_waste.md (A237: Lemma PIERCE in Lean
capacity_le_of_pierce; PIERCE(k): k points such that every unit square inside the pocket contains one of them =>
capacity <= k; the coverable-set sandwich per tilt bin), ring_capacity.md (Lemma TWO: a square region of side < 2
holds one unit square -- PIERCE(1) with the centre), A242/A243 (why pose-box trees died: the product law; the
over-approximation direction: the ACTUAL pocket is inside container minus the ring squares' CORES over a box, so
capacity(actual) <= capacity(container minus cores)), A171 multibox (cores), A244's verify244 (exact 12-cell test).

## The statement
RING-POCKET(11): for every family-stuck packing structure on [3.82, 4) whose eight corner meeters are the wall
touchers of an all-ADJ ring (A249's family: each wall's two touchers serve each other's slots; every c00 met by its
two touchers; T-CELLS conditions), the pocket -- the container minus the eight touchers -- holds at most TWO unit
squares (we need < 3; A249's pilot says <= 1).  With A249's T-SLOTS (the only other suppliers of slots are free
squares, which must lie in the pocket) and A250's count, that leaves 8 + 2 < 11: no family-stuck 11-packing of
this family below 4.  Together with A248's TWO-POKERS (type-F corners) and A250's theorem at s >= 4 this is the
family-stuck existence obligation on the window, unless a mixed / non-ring family-stuck structure survives A249's
enumeration (say which remain).

## Task
1. PARAMETRISE the ring family exactly (per corner: the two touchers' offsets and tilts under T-CELLS, the
   mutual-service inequalities, the D4 quotient if sound), s in [3.82, 4): a bounded box in <= 16 coordinates.
2. CERTIFY capacity <= 2 over the family with PIERCE made BOX-VALID: choose piercing points p1, p2 (the centre, and
   a second where needed) and prove, over each parameter box, that every unit square interior-disjoint from the
   eight touchers' CORES (over the box) contains p1 or p2 -- a statement about the pocket's over-approximation, so
   it is sound in the right direction; branch the box where it fails; PIERCE(1) where it holds.  Measure: the
   pilot's residual 0 means no margin at the sampled ring -- report the margin distribution over the family and
   the box count; if the product law reappears (cores empty at usable box widths), say so with numbers and stop
   at the price (benchmark from the first 200 boxes; stop if > ~200 CPU-h).
3. Alternatively / additionally the ANALYTIC pocket: the ring's inner boundary is eight inner edges at tilts
   theta_i; the pocket lies inside the centre square [1 + iota_min, s - 1 - iota_min]^2 plus notches; prove
   capacity <= 2 from Lemma TWO + the notch bound (A237's WEDGE / sealed regions) as a closed-form inequality in
   the tilts and offsets, if the notch bound closes -- that would make RING-POCKET(11) a theorem without boxes.
4. Cross-check on A249's ring witnesses (exact rational ring at s-hat; the ladder's rings at 3.85-4.0): the
   certified capacity vs the exact region search (A226/A237 code).
5. Say plainly: RING-POCKET(11) proved [T] / certified [T-computed] / open [C] and its dependencies; whether the
   family-stuck existence obligation is now closed on the window (list the remaining non-ring structures from
   A249/A250 if any); Lean: Statements/Open/RingPocket.lean (the statement + the consequence chain to k0_00 via
   FamilyStuck.lean / CELLS / K0-FREE; build + audit, 0 sorry).  Deliverables: code, results/pocket251.md (+jsonl,
   certificates), notes, pages (the ring at s-hat with its pocket and the piercing points; a failing box if any),
   registry row, LOG entry, ledger s.4 note.  Report once (<= 15 lines) and EXIT.
