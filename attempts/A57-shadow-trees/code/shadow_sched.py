"""Shadow-slack scheduling: spend LP time where a kill is plausible, split where it is not.

OFF BY DEFAULT (ENABLED = False).  Nothing reads this unless a driver is started with the flag.

A107's `results/shadow_nodes.json` groups A57 nodes under shadow ids S01..S08 with the node's
`tau` and its conditioned square.  The slack of a node against its budget,

    slack = budget - tau        (> 0 means the LP already sees room: a kill is plausible)

is the cheapest available predictor of whether more LP time will finish the job.  A109 measured
that 28 of 46 ALIVE nodes were merely UNCONVERGED at the 240 s cap, so the caps, not the
mathematics, decided many of those verdicts.

POLICY (deliberately blunt, because the predictor is one number):

    slack >= HI_SLACK      predicted DEAD    -> LP cap x LONG_MULT, verify depth + DEPTH_BONUS
    slack <= LO_SLACK      predicted ALIVE   -> LP cap x SHORT_MULT, split immediately
    otherwise                                -> unchanged

This only moves budget between nodes; it never changes a hypothesis, a certificate or a verdict,
so it is a completeness/scheduling choice and cannot affect soundness.  A wrong prediction costs
wall-time and nothing else.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
A107 = os.path.abspath(os.path.join(HERE, "..", "..", "A107-shadow-gallery"))

ENABLED = False          # scheduling is OFF unless a driver turns it on
HI_SLACK = 0.25          # budget - tau at or above this: worth a long LP
LO_SLACK = -0.50         # at or below this: do not spend more LP, split
LONG_MULT = 3.75         # 240 s -> 900 s
SHORT_MULT = 0.5
DEPTH_BONUS = 8

_TABLE = None


def table():
    """{node id: dict(shadow, tau, budget, slack)} from A107's shadow_nodes.json."""
    global _TABLE
    if _TABLE is not None:
        return _TABLE
    _TABLE = {}
    p = os.path.join(A107, "results", "shadow_nodes.json")
    if os.path.exists(p):
        try:
            d = json.load(open(p))
            for sid, nodes in d.items():
                for n in nodes:
                    tau, bud = n.get("tau"), n.get("budget")
                    if tau is None or bud is None:
                        continue
                    _TABLE[n["nid"]] = dict(shadow=sid, tau=tau, budget=bud,
                                            slack=bud - tau)
        except Exception:
            pass
    return _TABLE


def predict(node_id):
    """-> ('dead' | 'alive' | 'unknown', slack or None)"""
    r = table().get(node_id)
    if r is None:
        return "unknown", None
    if r["slack"] >= HI_SLACK:
        return "dead", r["slack"]
    if r["slack"] <= LO_SLACK:
        return "alive", r["slack"]
    return "unknown", r["slack"]


def lp_cap(node_id, base_cap):
    if not ENABLED:
        return base_cap
    k, _ = predict(node_id)
    if k == "dead":
        return base_cap * LONG_MULT
    if k == "alive":
        return base_cap * SHORT_MULT
    return base_cap


def split_now(node_id):
    """True when the node should go straight to depth 2 without spending its LP budget."""
    if not ENABLED:
        return False
    return predict(node_id)[0] == "alive"


def verify_depth(node_id, base_depth):
    if not ENABLED:
        return base_depth
    return base_depth + DEPTH_BONUS if predict(node_id)[0] == "dead" else base_depth


if __name__ == "__main__":
    t = table()
    print(f"shadow table: {len(t)} nodes from A107")
    if t:
        import collections, statistics
        by = collections.Counter(v["shadow"] for v in t.values())
        sl = sorted(v["slack"] for v in t.values())
        print("  by shadow:", dict(sorted(by.items())))
        print("  slack: min %.3f median %.3f max %.3f" % (sl[0], statistics.median(sl), sl[-1]))
        k = collections.Counter(predict(n)[0] for n in t)
        print("  predictions at the current thresholds:", dict(k))
    print("ENABLED =", ENABLED)
