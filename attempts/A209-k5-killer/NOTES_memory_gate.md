# Coordinator note (2026-09-12): the memory gate
The ops rule "6144 MB commit gate and > 3 GB free physical before each LP" means: an LP process may commit up to
6144 MB, and an LP is started only with > 3 GB free physical.  worker209.sh applied 6144 MB as a FREE-PHYSICAL floor,
which the PI's desktop (a game, Discord, Arc, Obsidian, Steam: ~22 GB in use of 32) leaves at ~5.9 GB, so the four
gallery workers sat idle at the gate.  Corrected to 3072 MB free physical (the chain runs geometry, not LPs).
The running worker loop re-reads the script only on restart: if the workers are still idle, restart worker209.sh.
