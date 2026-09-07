"""
A57 T18, adopted by A60: pin every worker to ONE BLAS thread.

numpy/OpenBLAS spawns roughly one thread per core (20 on this machine) in EVERY process, each
thread carrying its own allocation arenas.  Several concurrent jobs multiply that until an
allocation fails against fragmentation / arena limits rather than against free memory.  Measured
twice, independently:

  * A57: a 76.3 MiB numpy allocation and an OpenBLAS retry loop both failed with **9.9 GB free**,
    killing a tree shard and a deepen job at the same moment (notes/lemmas.md T18).
  * A60: `cover` shard 1/2 died with `Unable to allocate 66.6 MiB` at **9.1 GB free physical**
    (notes/falsifier.md §6).  Same class of failure, same day.

A54 W7 hit this too and treated the symptom by pruning columns.  These jobs are LP + numpy-oracle
work and are NOT BLAS-bound, so the thread parallelism buys nothing and the contention is pure
cost.

IMPORTANT: this module must be imported BEFORE anything that pulls in numpy (caselp, lpbox,
pinguard, pilot59, ...), because the BLAS thread pool is sized at import time.  `launch.ps1` and
A57's `run_job.ps1` set the same variables in the environment; this in-process copy exists so a
worker started by hand (`python code\tree60.py ...`, the restart lines in notes/RESUME.md) is
pinned too.  Pre-existing values are respected, so an operator can still override deliberately.
"""
import os

VARS = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS")

applied = {}
for _v in VARS:
    if _v not in os.environ:
        os.environ[_v] = "1"
        applied[_v] = "1"

if "numpy" in __import__("sys").modules:      # loud, because silence here is a slow leak
    print("WARNING blas1: numpy was already imported -- BLAS thread pinning had no effect; "
          "import blas1 earlier", flush=True)
