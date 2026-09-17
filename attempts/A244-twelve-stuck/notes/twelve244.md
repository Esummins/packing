# A244 — the 12-STUCK four-crowd: does it exist, and at what side?  (PI, 2026-09-16 19:30)

The PI, at A243's addendum: *"have you started that search?  if you can't construct a ring like
that, that's a pretty big issue for k0 existence"* — the ring in question being a packing of 11
unit squares with **all twelve border cells doubly met**: the four corner boxes c00 = [0,1]² AND
the eight wall slots c01 = [0,1]×[1,2] (up c's wall) and c10 = [1,2]×[0,1] (along c's floor), in
each corner's frame (A243 `notes/wall_slot243.md`, Lemma WALL-SLOT [T] + SLOT-MET [S]).  A square
MEETS a cell iff their interiors overlap.

Code `code/{cells244,fast244,feas244,search244,probe244,verify244,stress244,hand244,draw244,
pages244,summarise244}.py` + `run244.sh`; results `results/twelve244.md`, `results/twelve244.jsonl`
(every verified candidate), `results/probe244_*.jsonl`, `results/hand244.json`; pages
`docs/residue_map/campaigns/A244-twelve-stuck/{twelve_stuck,threshold244}.svg`.
Tags as elsewhere: [T] proved here, [M] measured, [S] proof route with a gap, [C] recommendation,
[F] a claimed step that fails.

## 0. The answer in one line

PLACEHOLDER-ANSWER

## 1. What is constrained, and how

PLACEHOLDER-METHOD

## 2. The thresholds

PLACEHOLDER-THRESHOLD

## 3. The structure of a 12-stuck packing

PLACEHOLDER-STRUCTURE

## 4. What this does and does not say about k0

PLACEHOLDER-K0

## 5. Reproduce / resume

```
bash attempts/A244-twelve-stuck/code/run244.sh test          # the self-tests
bash attempts/A244-twelve-stuck/code/run244.sh A [WALL]      # structure + the descent lane
bash attempts/A244-twelve-stuck/code/run244.sh B [WALL]      # the fixed-side probe lane
bash attempts/A244-twelve-stuck/code/run244.sh pages         # summary + the two pages
# stop:   touch attempts/A244-twelve-stuck/logs/STOP
# resume: rm attempts/A244-twelve-stuck/logs/STOP   then lane A and lane B again
```
