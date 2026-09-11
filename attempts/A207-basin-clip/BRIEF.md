# A207 -- NEAR-SIMPLE = SIMPLE: the basin of the FULL extension certificates as a stage-0 clip (PI, 2026-09-11 15:10)

Model: Fable. Short responses, files in pieces <= 250 lines, no interim messages, commit after every batch
(`git add -- <paths>; git commit -- <paths>`; fetch + plain merge only; never pull --rebase / autostash / reset; no
recursive deletes; PYTHONDONTWRITEBYTECODE=1; <= 2 processes, BLAS pinned to 1 thread, affinity 0xFFFF, BelowNormal;
6144 MB gate; lab ceiling 12 python processes EXCLUDING command lines containing "Claude Extensions"; never touch other
campaigns' files or processes (A206 is running); frozen verifiers byte-identical). Agent messaging is broken; report
ONCE at the end. Pages: docs/residue_map/campaigns/A207-basinclip/basinclip207_<nid>.svg per docs/residue_map/README.md.

## The PI's reading (credit by name)
Y0881 leaf R.2.3s (A206): "it's basically just setting F1 directly in a simple slot, and then using the fact that the
pads grow around corners to claim the simple square totally isn't simple."
Coordinator's numbers (G1 pad, lambda = 1.004000117): the simple TR(1,0) square of P dilates to (2.3711, 3.3751); the
surviving F1 poses on the leaf are upright with centres x in [2.3705, 2.3749], y ~ 3.371 -- within 0.004 of the dilated
simple pose -- and F1 counts as a meeter of TL(1,0), TR(1,0) and TR(0,1) only through the 0.0068 / 0.0108 pads (corner
reach 0.007).  The leaf is the ghost of the closed extension class k6_28.  The same pattern holds on Y0054 / Y0044
(BL(1,0) pairs through the pad) and every "pad-only" survivor.

## Task: Lemma BASIN (state and prove before use; any n) and the clip
1. For each FULL extension class at a forced slot of the k5_16 and k5_11 pages (k6_23, k6_27, k6_28, k6_29, k6_30 at
   k5_16's slots; the k6 classes at k5_11's slots -- docs/shadows/review*.csv and geo178.forced_items give the map),
   take its window certificate (the A114 / A61 / re-solved base certificates named in forced_items' `status`) and
   compute the BASIN of the simple pose: the largest box (centre radius r_c, tilt radius r_t) around the exact simple
   pose within which the certificate's kill still holds -- via the descent theory (docs/proofs/descent.md Theorem D2
   basin descent; attempts/A188-*/ local certificates; docs/proofs/local_certificate_s01.md; A194 corner-hurt CH-S)
   or, where the certificate is an LP, by re-verifying it with the slot square as a boxed role of radius (r_c, r_t)
   under the windows clause (A185 v4 / A190 v5) and bisecting r.  Exact rationals; every basin a certificate.
2. Lemma BASIN: a packing of the window with a non-pin square whose pose lies within the basin of a FULL slot's simple
   pose (in F's frame: the DILATED simple pose for the page's lambda range, plus the basin) does not exist.  Prove it
   from the certificate's semantics (the extension class certificate + the basin re-verification); write the exact
   statement of what "within the basin" means in F's frame (the dilation drift of the simple pose over the page's
   lambda range is a segment; the basin is around every point of it).
3. The clip: at stage 0 (A202/A203 style, closed form) and inside A204/A205/A206's cascade, cut from every role's
   pieces (H and instantiated roles) and from every anonymous option row the poses inside the basin of any FULL slot.
   Apply first to Y0881's leaf R.2.3s (from attempts/A206-named-split/certs/namedsplit206_k5_16_interior_Y0881.json),
   then to every ALIVE leaf in A206's and A205's certificates, then as a stage-0 pass over all alive k5 pages
   (docs/shadows/STATUS.md).  A kill is [C: extension certificate + Lemma BASIN + library clip trace]; say which
   certificate and which basin radius; audits by sampling as A205/A206 do.
4. Deliverables: results/basin207.jsonl (slot, class, certificate, r_c, r_t, seconds) and results/basinclip207.jsonl
   (page, pad, leaf, verdict, which basin, seconds), certs/, pages, notes/basin.md (Lemma BASIN with proof, the PI
   credited for "near-simple is simple" and for the basin/descent idea, the per-slot basin table, the kill table,
   what the basin could not do), registry row, LOG entry, docs/residue_ledger.md section 4, docs/budget.md item,
   status gallery collector block for page kills.
