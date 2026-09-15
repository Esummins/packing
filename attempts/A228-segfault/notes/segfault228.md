# A228 -- the pass-5 crash of `k5_16_interior_Y0402` (rc 139), what it really was, and the guards

## 0. The fact, corrected

The BRIEF (and the worker line it was read from) says the **pad-0** run crashed and "the g1 run of the same page
then ran to rc=0".  **Both halves are wrong**, and the correction matters because it says where the ~500 s of
silence before the crash was spent.

Read from the certificate that the crashed process itself left behind
(`attempts/A211-coarse-tree/certs/coarsetree211_k5_16_interior_Y0402.json`, mtime 23:49:59):

| run | verdict in the cert | seconds | nodes |
|---|---|---|---|
| `zero_page` | `ALIVE` (wall) | 1818.7 | 86 |
| `g1_page`   | **`RUNNING`**  | 977.1  | 75 |

and from the log (`logs/coarsetree211_k5_16_interior_Y0402.log`): the pass-5 **pad-zero** segment starts at line
384 and RUNS TO COMPLETION (`start R.4 ... => ... t = 1818 s`), and the pass-5 **g1** segment starts at line 616
(`pad g1: cached ALIVE was WALL-limited (14 undecided) -- RESUMING`) and its last line, line 831, is

```
   node R.3.4.p1   d1 pocket<-[0]: INTERNAL (24.3 s, 1 rounds; t=977.1)
```

Arithmetic: the worker started at 23:03:18 and reported `rc=139 3326s` at 23:58:44.  1818.7 s of pad zero + stage 0
+ inherit puts the g1 pad at t = 977 around 23:50:20; the process then lived a further **~8.5 minutes producing no
output at all** and died of SIGSEGV.  So:

* the crash is in the **g1 pad**, not pad 0.  Pad 0's certificate is complete; the g1 pad lost 75 nodes of work;
* the "`g1 ... rc=0 4408s`" on the worker line is the PASS-2 run of 17:08 -- `worker211.sh` greps the whole log
  file for the verdict line, so a crashed run reprints the last SUCCESSFUL run's verdict.  That is itself part of
  why the crash was invisible (s.3);
* the crash is **not** in the pocket instantiation at `R.3.4` (k = 9, m = 2, 2 pockets) -- that one printed fine at
  t = 939.7.  The process died in whatever `R.3.4.p1` (k = 10, **m = 1**) did next, which is the **no-room leaf**.

## 1. Where 500 s can go in a leaf whose cap is 150 s

`tree211` calls `N9.noroom_at(pg, min(wall_left, NOROOM_CAP + 30))` with `NOROOM_CAP = 120`, so
`bud["total_deadline"] <= 120` and `noroom221.noroom` gets `dl = t0 + 120`.  Every *search* in that leaf honours
`dl`: `NR.bisect_free` checks it per level, `pocket_pass` per pocket, `pocket221.cover_rect` every 256 pieces.

**Two steps in the leaf are not searches and see no deadline at all.**

1. `noroom221.noroom` -> `NR.pockets_of(pieces, s, bud)` on the *global* bisection residue.  `pockets_of` is A189
   and READ-ONLY.  Its cost is (a) a grid-cell hull dict, one entry per cell each piece touches, and (b)

   ```python
   while len(pk) > budget["max_pockets"]:      # max_pockets = 8
       best = None
       for a in range(len(pk)):
           for b in range(a + 1, len(pk)):     # rescans EVERY pair, every iteration
               ...
   ```

   which is **O(components^3)**.  At `grid = 0.0625` the container `[1/2, s-1/2]^2` holds 46 x 46 = 2116 cells, so
   a residue that is *spread* (many small components rather than a few blobs) costs up to ~1.6e9 inner steps --
   tens of minutes of pure Python, after the 120 s cap has already expired, with nothing logged.  A node whose
   residue is a couple of blobs (the normal case, and every case A221 benchmarked) costs microseconds here, which
   is why this never showed up before.

2. `pocket221.pocket_dead` -> on EVERY give-up path (`deadline`, `piece cap`, `open cap`) `cover_rect` did
   `open_.extend([... for ... in stack])` with `pk_max_pieces = 200000`, then summed the volume of all of them,
   then handed all of them to `pockets_of` **on a 4x finer grid** (`0.015625`, i.e. 16x the cells).  Same shape of
   unbounded work, again strictly after the pocket's own deadline had passed.

That is the only place in the leaf where the observed signature -- 500+ s of silence inside a 150 s budget -- can
be produced, and `R.3.4.p1` is an m = 1 node, i.e. exactly the path that runs (1).

**Honest statement of what is and is not established.**  (1) and (2) are *proved* unbounded by reading the code and
they *fit* the timing exactly; the step from "runs away" to "SIGSEGV" is **not** proved.  A Python-level runaway
normally ends in `MemoryError`, not rc 139.  A reproduction was launched (s.4) and its outcome is recorded there.
The other two suspects named in the BRIEF were checked and **cleared**:

* **deep Python recursion** (the BRIEF's first guess: "pocket-rooted depth-first clip ... deep Python recursion
  overflowing the C stack").  There is none.  `pocket221.cover_rect` is an explicit `stack`/`while` loop;
  `noroom189._components` is an explicit stack; `multibox._clip_rect_obstacle`'s inner `rec` is a one-line trace
  appender, not a recursion; `pinclip._bisect_boundary` is a bounded `for`; the only recursion in the path,
  `multibox.lonely_clip.refine_piece`, is bounded by `refine` (<= 2).  No `sys.setrecursionlimit` is raised
  anywhere in this chain.
* **the A214 C kernel.**  Its arithmetic envelope is guarded (`fits93` / `a214_box_ok` / `vert_ok_range`) and the
  DLL imports nothing (checked by reading its PE import table: empty).  **One genuine out-of-bounds write was found
  in it** and is fixed by an input guard (s.2c) -- but it is not reachable from this node, because the batch is
  only ever called with <= 16 vertices.

## 2. The fix (all three flag-neutral; a guard may only ever return UNDECIDED)

The soundness rule for every guard below: **each one replaces a residue by a SUPERSET of it**, so a cover stays a
cover and Lemma POCKET-DEAD / POCKET-INHERIT / Lemma CN keep their hypotheses.  A superset can only make a node
UNDECIDED that would otherwise have been DEAD -- never the other way round.  No guard can produce a verdict.

### (a) `attempts/A221-lane-cover/code/pocket221.py`

* `_dump(open_, stack, cap)`: the undischarged frontier appended on a give-up is bounded by `pk_max_dump = 4096`
  (was: the whole 2e5-entry stack).  `cert["n_undumped"]` records what was dropped.
* `cert["exhausted"]` is now written, and `pocket_dead` returns `dead = (not pieces) and cert["exhausted"]` --
  i.e. **a cover that gave up can never be read as DEAD**, which is what makes truncating the dump sound.  (It was
  already true implicitly, because a give-up always dumped something; it is now true by construction.)
* `cert["root_out"]`: the cover's root rectangle as floats nudged OUTWARD (`math.nextafter` + 1e-9), so the float
  rectangle brackets the rational one it came from.
* new `repocket(pieces, s0, bud, root, grid)`: A189's `pockets_of`, guarded.  It measures the two costs first
  (both linear -- the piece count, the cell count, and `NR._components`, which is an explicit-stack flood fill) and
  when any of `pk_max_repocket = 20000` pieces / `pk_max_cells = 400000` cells / `pk_max_comps = 64` components is
  exceeded it returns **`root`**, the cover's own root, instead of paying for the O(n^3) merge.  `root` contains
  every open piece by construction, so it is a cover.  The record says which branch was taken (`"repocket"`).

### (b) `attempts/A221-lane-cover/code/noroom221.py`

`noroom` now calls `PK.repocket(pieces, s, bud, [1/2, s-1/2, 1/2, s-1/2])` instead of `NR.pockets_of(...)`.  The
fallback rectangle is the container's CENTRE BOX, which contains the centre of every pose of a unit square inside
the container -- so it is a cover of the free centres whatever the residue looks like.  A189 itself is untouched.

### (c) `attempts/A214-c-kernel/code/ckernel214.py` -- a real out-of-bounds write, guarded on the Python side

`a214_cert_batch` addresses its output buffer with

```c
int i0 = i * nb;          /* ckernel214.c:231 -- a C int */
...
out[i0 + j] = ...;
```

At `nv * nb >= 2^31` that product overflows, `i0` goes negative, and the kernel writes **outside** the ctypes
buffer: an access violation, or silent heap corruption.  The Python caller is the only party that knows the true
product (it allocates `(c_ubyte * (nv * nb))()` with Python's exact arithmetic), so `certify_h` now refuses the
batch at `nv * nb >= 2^30` and runs A213's unbounded-integer path -- gate (2') of the module's own documented
FALLBACK PROTOCOL.  **The C source and the DLL are untouched** (no rebuild, the sha256 stands).  This is a
latent-bug fix, not the crash: on this population `nv <= 16` and `nb` is a piece count, so the product is small.

## 3. Worker hygiene (`attempts/A211-coarse-tree/code/worker211.sh`)

The crash left **no row in `results/coarsetree211.jsonl` and no mark in `results/progress.md`**: the worker wrote a
row only for `rc == 137`.  Worse, its verdict line `V=$(grep -o "== $NID: g1 ..." $LOG | tail -1)` matched the
PASS-2 run's summary further up the same log, so the worker cheerfully logged `g1 ALIVE | pad0 ALIVE rc=0 4408s`
next to `rc=139`.  Now:

* a row is written for **every** non-zero rc, tagged `"rc": <rc>` and `"killed": true`, with a `leaf` naming the
  cause (`CRASHED: SIGSEGV (rc 139) -- see A228`, `abort`, wall kill, or `run211 exited rc=N`).  The row is
  `verdict: ALIVE` + `killed` -- a crashed run is undecided, never a verdict;
* the nid is appended to `attempts/A211-coarse-tree/logs/requeue.txt` (with its wall), and for a CRASH (not for
  the 137 wall kill, which would re-run pages that legitimately ran out of clock) the `logs/claims/<nid>` claim is
  released so a sibling worker still walking the same queue picks the page up again.

**How it was installed.**  `worker211.sh` is being executed right now by p5a and p5b, and bash re-reads a running
script from a saved byte offset -- editing it in place can make the running shell execute garbage when the loop
ends.  The new text was therefore written to `worker211.sh.new`, checked with `bash -n`, and `mv`-ed over the old
path: the rename swaps the inode, the two running bashes keep reading the old one, and the next launch gets the
new one.  Both worker pids were verified still alive afterwards.  No worker was restarted.

## 4. Reproduction and verification -- RESUME BLOCK

Nothing here waits; both lanes are detached and resumable.

```
bash attempts/A228-segfault/code/repro228.sh [wall] [pads] [tag] [nid]
      # default: 1200 g1 g1 k5_16_interior_Y0402 -- the crashed page and pad, SAME flags
      #   (A220_NOROOM_INHERIT=1 A221_LANE=1), python -X faulthandler + PYTHONFAULTHANDLER=1 so a SIGSEGV prints
      #   a traceback, isolated --cert-dir attempts/A228-segfault/certs, isolated --results, --no-fig.
      # -> attempts/A228-segfault/logs/repro228_<tag>.log
bash attempts/A228-segfault/code/verify228.sh [<pid to wait for>]
      # the closed-page verdict-agreement lane (A221's own `closed` lane: every recorded no-room node of
      #   Y0500 g1 and Y0460 g1, replayed through the PATCHED leaf), re-pointed at results/verify228.jsonl so
      #   A221's bench file is not written.  Waits for the given pid first: at most ONE python of our own.
      # -> attempts/A228-segfault/logs/verify228.log, results/verify228.jsonl
python attempts/A221-lane-cover/code/noroom221.py       # A189's STEP 34 regression through the patched path
```

The STEP 34 regression is **PASS** after the patch, with `"repocket": "pockets_of"` -- i.e. on a normal node the
guard does not fire and the leaf is byte-for-byte the old computation.

Caveat on the reproduction: the isolated cert dir means the run starts from the A203 root and re-derives its start
nodes from the (read-only) prior certificates, which have moved on since 23:03 -- the crashed run's own partial
`g1_page` record is now in the A211 certificate.  So the reproduction walks a similar but not identical tree, and
a clean run does NOT clear the code: this crash has happened exactly ONCE in the whole campaign (one
`Segmentation fault` line across every `attempts/*/logs/*`).  The guards of s.2 are therefore written to be sound
and cheap independent of whether the reproduction fires, and s.3 makes the next one visible in the ledger instead
of silent.
