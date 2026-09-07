"""--region-tree: hand a twice-stalled node to A112's region tree, else fall through.

OFF BY DEFAULT (ENABLED = False).  Resumable.  Nothing launches this; it is wired so a driver
started with --region-tree can use it.

TRIGGER.  A node qualifies when the ordinary route has already failed it twice:
  * ALIVE-at-LP recorded twice for the same node id (two independent solves), or
  * still unconverged after the 900 s re-check (recheck96.jsonl: converged is false).
Anything else goes down the ordinary path untouched.

ORDERING.  'loadpath' when the node has a matched shadow in A107's shadow_nodes.json (the load
path is the shadow's own branch order, so it is only meaningful when a shadow matched), else
'hybrid'.

FALL-THROUGH.  The Runner gets a wall cap W.  If it does not come back with transfers=True inside
W, the node goes to the ordinary 8-way split exactly as before: nothing is lost and no verdict is
weakened.  A region tree that runs out of wall leaves CAP-UNPROCESSED leaves, which fail C3, so a
timed-out run simply does not transfer -- the failure mode is inert.

WHAT A TRANSFER RECORDS.  A112's containment() checks three obligations and we store the whole
record next to the kill:
  C1  the region-tree root hypothesis IS the old node's hypothesis (same boxes, nofams, budget,
      side) -- the tree covers the old box exactly, not a relaxation;
  C2  every split is tautologous (the same branch box appears as a core child at budget-1 and as
      a NO-family child at budget);
  C3  every leaf is dead.
The kill is then written as "old box X dead by region tree", never as an ordinary certificate.

NO-SIDE CERTIFICATES ARE FIXED-SIDE until A117's verify_param_v2 lands; a transferred kill is
therefore s0-only on its NO side and must be re-verified parametrically afterwards.  That is
recorded on every transfer record as `no_side_window = "s0-only, pending A117"` so the scoreboard
cannot silently count it as full-window.
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A57 = os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees"))
A107 = os.path.abspath(os.path.join(BASE, "..", "A107-shadow-gallery"))
A112 = os.path.abspath(os.path.join(BASE, "..", "A112-dual-branching"))

ENABLED = False          # --region-tree turns this on
WALL = 1800.0            # W: per-node wall cap for the region tree
LP_CAP = 900.0
DEPTH_CAP = 6
NODE_CAP = 40
LEDGER = os.path.join(BASE, "results", "regionopt96.jsonl")

_SHADOW = None


def shadow_match(node_id):
    """Does this node have a matched shadow in A107's gallery?  -> shadow id or None."""
    global _SHADOW
    if _SHADOW is None:
        _SHADOW = {}
        p = os.path.join(A107, "results", "shadow_nodes.json")
        if os.path.exists(p):
            try:
                for sid, nodes in json.load(open(p)).items():
                    for n in nodes:
                        _SHADOW[n["nid"]] = sid
            except Exception:
                pass
    return _SHADOW.get(node_id)


def ordering_for(node_id):
    return "loadpath" if shadow_match(node_id) else "hybrid"


def _alive_twice(node_id, rows):
    return sum(1 for r in rows
               if r.get("id") == node_id and str(r.get("cert") or "").startswith("ALIVE")) >= 2


def qualifies(node_id, tree_rows=None, recheck_path=None):
    """True if the ordinary route has already failed this node twice."""
    if tree_rows and _alive_twice(node_id, tree_rows):
        return True, "ALIVE-at-LP twice"
    p = recheck_path or os.path.join(BASE, "results", "recheck96.jsonl")
    if os.path.exists(p):
        for ln in open(p):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("id") == node_id and r.get("converged") is False:
                return True, "unconverged at the 900 s re-check"
    return False, None


def done_ids():
    out = set()
    if os.path.exists(LEDGER):
        for ln in open(LEDGER):
            try:
                r = json.loads(ln)
                out.add((r.get("cls"), r["id"]))
            except Exception:
                pass
    return out


def try_region_tree(node_id, cls, root_res, root_src, wall=None, log=print):
    """Run A112's Runner on one node.  -> (transferred: bool, record).

    Never raises into the caller: any failure is a non-transfer, and the caller falls through to
    the ordinary 8-way split."""
    rec = dict(id=node_id, cls=cls, ordering=ordering_for(node_id),
               shadow=shadow_match(node_id), wall_cap=(wall or WALL),
               started=time.strftime("%Y-%m-%d %H:%M:%S"))
    t0 = time.time()
    try:
        if os.path.join(A112, "code") not in sys.path:
            sys.path.insert(0, os.path.join(A112, "code"))
        import regiontree as RT
        runner = RT.Runner(region=node_id, ordering=rec["ordering"], s=root_res["s"],
                           budget0=root_res["budget"], log=log, lp_cap=LP_CAP,
                           depth_cap=DEPTH_CAP, node_cap=NODE_CAP, wall=(wall or WALL),
                           kind="a57")
        out = runner.run(root_res)
        leaves = out.get("leaves", []) if isinstance(out, dict) else []
        internal = out.get("internal", []) if isinstance(out, dict) else []
        con = RT.containment(node_id, rec["ordering"], leaves, internal, root_res, root_src)
        rec["containment"] = con
        rec["transfers"] = bool(con.get("transfers"))
        rec["stats"] = getattr(runner, "stats", None)
    except Exception as e:
        rec["error"] = repr(e)[:300]
        rec["transfers"] = False
    rec["wall_s"] = round(time.time() - t0, 1)
    if rec["transfers"]:
        rec["claim"] = f"old box {node_id} dead by region tree"
        rec["no_side_window"] = "s0-only, pending A117 verify_param_v2 re-verification"
    else:
        rec["fallthrough"] = "ordinary 8-way split (nothing lost)"
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
    return rec["transfers"], rec


def control_replay(log=print):
    """Control: re-run A112's containment() over its OWN stored region trees and confirm this
    option reproduces their transfer verdicts.  Reads only; runs no LP."""
    sys.path.insert(0, os.path.join(A112, "code"))
    import regiontree as RT
    import glob
    out = []
    for d in sorted(glob.glob(os.path.join(A112, "results", "rt*", "*", "*"))):
        if not os.path.isdir(d):
            continue
        region = os.path.basename(os.path.dirname(d))
        ordering = os.path.basename(d)
        recs = []
        for f in sorted(glob.glob(os.path.join(d, "*.json"))):
            try:
                recs.append(json.load(open(f)))
            except Exception:
                pass
        if not recs:
            continue
        leaves = [r for r in recs if r.get("status") in
                  ("DEAD-LOGIC", "DEAD-CERT", "DEAD-CLASS", "DEAD-CHAIN-LP", "CAP-UNPROCESSED",
                   "ALIVE")]
        internal = [r for r in recs if r.get("status") == "SPLIT"]
        root = next((r for r in recs if r.get("key") == "R"), None)
        if root is None:
            continue
        rr = dict(hyp=root.get("hyp"), budget=root.get("budget"), s=root.get("s"))
        try:
            con = RT.containment(region, ordering, leaves, internal, rr, "control-replay")
            out.append(dict(region=region, ordering=ordering, transfers=con["transfers"],
                            C1=con["C1_root_is_old_hypothesis"]["ok"],
                            C2=con["C2_tautologous_split"]["ok"],
                            C3=con["C3_all_leaves_dead"]["ok"],
                            leaves=len(leaves), internal=len(internal)))
        except Exception as e:
            out.append(dict(region=region, ordering=ordering, error=repr(e)[:160]))
    for r in out:
        log(json.dumps(r))
    return out


# ---------------------------------------------------------------- A116 local certificates
# When a stalled node's support lies inside a CERTIFIED neighbourhood N of the S02 or S07 minimum
# (docs/proofs/local_certificate.md, 74a34f96), the YES region can be taken to BE N: A116 has
# already certified that no packing exists in N, so the YES child needs no LP at all and only the
# NO children go through the solver.  Off by default with everything else here.
#
#   S02  k5_11 frame,   L = f1 f2 f3 BR(0,1),  (r, rho) = (0.2, 10 deg)      72/184 nodes inside
#   S07  trump5 frame,  L = f0 f2 f4, cut F_T(theta) > s0,
#                                          (0.1, 40 deg) and (0.2, 10 deg)    2/18 nodes inside
# 10^4-sample confirmed by A116, Trump outside every N.
#
# The YES kill is recorded as "dead by local certificate A116 <N id>" and is PENDING A119's
# rational/Lean form -- it is a prose+numeric certificate today, not a replayable one, so it is
# tagged and must not be counted with the frozen-verifier kills.
A116 = os.path.abspath(os.path.join(BASE, "..", "A116-local-selection-tree"))
HEADLINE_N = (("S02", 0.2, 10.0), ("S07", 0.1, 40.0), ("S07", 0.2, 10.0))
_A116 = None


def n_id(N):
    return "%s/%s/r%g/rho%g%s" % (N["tag"], N["cls"], N["r"], N["rho"],
                                  "/cut" if N.get("cut") else "")


def a116_table():
    """{node id: N record} for nodes whose support is inside a headline certified N."""
    global _A116
    if _A116 is None:
        _A116 = {}
        p = os.path.join(A116, "results", "t3_consumer.json")
        if os.path.exists(p):
            try:
                d = json.load(open(p))
                for e in d.get("per_N", []):
                    N = e["N"]
                    if (N["tag"], N["r"], N["rho"]) not in HEADLINE_N:
                        continue
                    for n in e.get("nodes", []):
                        if n.get("inside"):
                            _A116.setdefault(n["nid"], N)
            except Exception:
                pass
    return _A116


def local_certificate(node_id):
    """-> (N record, claim string) when the YES side is free, else (None, None)."""
    N = a116_table().get(node_id)
    if N is None:
        return None, None
    return N, ("dead by local certificate A116 %s (pending A119 rational/Lean form)" % n_id(N))


def plan_node(node_id):
    """What the --region-tree option would do with this node, without running anything."""
    N, claim = local_certificate(node_id)
    return dict(id=node_id, ordering=ordering_for(node_id), shadow=shadow_match(node_id),
                yes_side=("A116 local certificate" if N else "LP"),
                local_N=(n_id(N) if N else None), yes_claim=claim,
                no_side="LP (fixed-side certificates until A117 verify_param_v2)")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", action="store_true", help="replay A112's stored region trees")
    a = ap.parse_args()
    print("ENABLED =", ENABLED, "| wall cap", WALL, "s")
    if a.control:
        r = control_replay()
        print(f"regions replayed: {len(r)}; transfers: {sum(1 for x in r if x.get('transfers'))}")