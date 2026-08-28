#!/usr/bin/env python
"""a37_batchB.py -- production batch B driver (families 18..31).

Thin wrapper around the pilot's a37_pipeline.py.  Changes NOTHING in the
pipeline itself (batch A runs it concurrently); it only

  (1) redirects the certificate directory to results/certs_batchB so that the
      re-checker globs exactly this batch's certificates (batch A writes into
      results/certs at the same time), and
  (2) enforces cookbook AMENDMENT A7's variant cap (256): a family whose
      branch product exceeds the cap falls back to the branch-free structure
      (only [V]-safe rows usable; variants with no multiplier fall back to
      omega = 0), which is SOUND, and the refusal is recorded as a surprise.

Usage:  python a37_batchB.py --fam 18 19 ... [--atlas <path>]
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a37_pipeline as P                                       # noqa: E402

VARIANT_CAP = 256

P.CERTDIR = os.path.join(P.RESULTS, 'certs_batchB')

_orig_variant_structure = P.variant_structure


def capped_variant_structure(zh, aud, rows, meta, h):
    branched, nvar, axis_rows, kill = _orig_variant_structure(
        zh, aud, rows, meta, h)
    if nvar > VARIANT_CAP:
        print('  ** A7 VARIANT CAP: %d variants > %d -> REFUSED; falling '
              'back to the branch-free structure ([V]-safe rows only, '
              'omega = 0 where the LP is infeasible).  Sound, weaker.'
              % (nvar, VARIANT_CAP))
        aud.setdefault('surprises', []).append(
            'A7 variant cap: branch product %d > %d -> branching refused; '
            'certificate uses the branch-free ([V]-safe only) structure'
            % (nvar, VARIANT_CAP))
        return [], 1, axis_rows, kill
    return branched, nvar, axis_rows, kill


P.variant_structure = capped_variant_structure

if __name__ == '__main__':
    sys.argv[0] = 'a37_pipeline.py'
    sys.exit(P.main())
