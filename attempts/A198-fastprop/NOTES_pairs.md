# Coordinator note (2026-09-10 12:25): two millisecond pair exclusions (PI), verified on Y0054 / BL(1,0)

After the per-cell exact dead tests, take the UNION of all surviving centre pieces of a slot's free-meeter cells:
(1) CENTRE DISTANCE: two interior-disjoint unit squares have centres at l-inf distance >= 1/sqrt2 (Lemma A1,
    sideband.md) and Euclidean distance >= 1 (Lemma CN, A153 / residue_ledger section 1). If the union's l-inf
    diameter is < 1/sqrt2, or its Euclidean diameter is < 1, the slot admits AT MOST ONE free meeter.
    Y0054 / BL(1,0): union x [1.500, 2.377], y [0.500, 0.619]: Euclidean diameter 0.885 < 1 -> at most one.
(2) CHORD ROW: on any axis-parallel line, the pins' chords + the minimum OPEN chord of a surviving meeter pose,
    doubled, must fit in s0. Y0054 / BL(1,0), line y = 1/2: pins 2, remaining 1.877, every surviving pose has open
    chord 1.000 -> two meeters need 2.000 > 1.877 -> at most one.
Either one kills the two-free case at BL(1,0) in milliseconds; A178's fine pair test needed 1,310 s to say the same.
Then H MUST be the second meeter -> the forced H clip (hclip step) -> continue. Use both as the first tests in
the engine, on the union of survivors per slot and per pair of slots (for the joint count).
