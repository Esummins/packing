"""A238 -- Tree238 = A212's Tree212 (gate + tube leaf + aligned split) on a PROTECTED-CLASS page, with

  1. the CLASS tube direction: `trump212` is replaced inside tree212 by `tube238` (Lemma TUBE-LEAF/S, the slot(I_g)
     certificate of A84 s.4 instead of trump5's scale ray, and the pins exempt because M_S pins them exactly);
  2. Rule SNAP run at the GATED fully named leaf too (A224): on a Trump-parent class the fifth simple square is
     exactly what a near-simple role snaps to, and the target stratum decides -- trump5 (the OPEN k5 stratum: a
     HAND-OFF, the node leaves this class's tree and joins trump5's queue) or a closed k5 class (DEAD by Lemma K1).
     A SNAP claiming DEAD on a gated node is refused by Tree212.kill as a gate conflict, as it must be;
  3. per-node bookkeeping of WHICH rule decided the node (`a238`), so the benchmark can be read rule by rule.

Nothing in A211 / A212 / A224 is edited: the modules are imported read-only and `tree212.TR` is rebound to the shim."""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (os.path.join(ROOT, "attempts", "A212-trump5-tree", "code"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import tree211 as N11                                           # noqa: E402  READ-ONLY (A211)
import tree212 as N12                                           # noqa: E402  READ-ONLY (A212)
import tube238 as TU                                            # noqa: E402

N12.TR = TU                                                     # the class tube direction, everywhere tree212 uses it
BASE = N12.Tree212                                              # captured BEFORE run238 rebinds N12.Tree212 to Tree238
SNAP_AT_GATE = (os.environ.get("A238_SNAP_AT_GATE") or "1") == "1"


class Tree238(BASE):
    def __init__(self, pg, **kw):
        BASE.__init__(self, pg, **kw)
        self.gated_snaps = 0
        self.rule_log = []

    def trump_leaf(self, depth, label, tg):
        """A212's gated leaf, with Rule SNAP first: the fifth simple square is the whole point on a Trump parent."""
        if SNAP_AT_GATE and not self.pg.T.out_of_time():
            s = self.snap_try(depth, label, "gated-leaf")
            if s != "OK":
                self.gated_snaps += 1
                return s
        return BASE.trump_leaf(self, depth, label, tg)

    def record(self, label, depth, br, verdict, clip, rnd, t0, reason=None):
        r = BASE.record(self, label, depth, br, verdict, clip, rnd, t0, reason=reason)
        r["a238"] = dict(rule=r.get("clip"), verdict=r.get("verdict"), depth=depth, seconds=r.get("seconds"),
                         gated=bool((r.get("trump_gate") or {}).get("contains")),
                         snap=(r.get("snap") or {}).get("verdict"), eps=(r.get("eps") or {}).get("verdict"))
        self.rule_log.append(dict(label=label, **r["a238"]))
        return r

    def result(self):
        out = BASE.result(self)
        out.update(gated_snaps=self.gated_snaps, rule_log=self.rule_log[-600:])
        return out
