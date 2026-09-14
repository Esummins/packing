"""A212 -- the children of a Tree212 node (tree212.py split for the 250-line rule): apply the step, the GATE on the pieces the
child was branched INTO (before its cascade), the cascade, the record, the recursion; A211 tree211._expand with the hooks."""
import time

import tree205b as TB
import tree206 as N6
import tree209 as N9
import rsplit211 as RS
import trump212 as TR


def apply_child(T, lab, br):
    """apply the branch step; -> None, or the DEAD record when an rsplit half is empty."""
    pg = T.pg
    if str(br.get("kind", "")).startswith("ns-"):
        N6.apply_ns(pg, br)
    elif br.get("kind") == "rsplit":
        RS.apply_rsplit(pg, br)
    elif br.get("kind") == "pocket":
        return N9.apply_pocket(pg, br["pocket_raw"], br["rows"][0])       # the UNROUNDED pocket (a rounded rect could be smaller: unsound)
    else:
        TB.apply_branch(pg, br)
    return None

def aligned_branches(T, sp):
    md = round(TR.MB.deg_of_t(sp["m"]), 4) if sp["dim"] == "t" else round(float(sp["m"]), 6)
    return [dict(slot=sp["role"], kind="rsplit", rows=["%s%s%s" % (sp["dim"], "<=" if side == "lo" else ">=", md)], named=None, role=sp["role"], dim=sp["dim"],
                 side=side, m=sp["m"], m_f=md, aligned=True, square=sp["square"], excess=sp["excess"], with_image=(side == sp["side"])) for side in ("lo", "hi")]

def pocket_branches(T, depth, label, pk, res):
    pg = T.pg
    T.pocket_splits += 1
    T.nodes[-1].update(branch_slot="pocket", n_branches=len(pk), branch_rows=[[j] for j in range(len(pk))], pockets=pk, verdict="INTERNAL", reason=None)
    T.log("   Lemma POCKET at %s: %d pockets (k=%d, m=%d)" % (label, len(pk), res["k"], res["m"]))
    st = N6.save_state(pg)
    branches = [dict(slot="pocket", kind="pocket", rows=[j], named=None, pocket=[round(v, 6) for v in p], pocket_raw=list(p), diam=round(N9.diam(p), 4)) for j, p in enumerate(pk)]
    T.run_children(depth, label, branches, st, ".p")
    N6.restore_state(pg, st)

def run_children(T, depth, label, branches, st, sep="."):
    pg = T.pg
    for i, br in enumerate(branches):
        lab = "%s%s%d" % (label, sep, i + 1)
        info, _q, p = T.child_path(lab, label, br)
        if info is not None:
            T.record_inherited(lab, depth + 1, br, info, p)
            continue
        if not T.on_path(lab):
            T.undecided(lab, depth + 1, br, "undecided: skipped (not on the requested path %s)" % T.only)
            continue
        if pg.T.out_of_time() or T.n_nodes >= T.node_cap:
            T.undecided(lab, depth + 1, br, "undecided: %s before this branch ran" % ("wall" if pg.T.out_of_time() else "node cap"))
            continue
        N6.restore_state(pg, st)
        T.fresh_child()
        t0 = time.time()
        try:
            role = T.apply_child(lab, br)
        except ValueError as e:
            pg.dead = "Lemma ROLE-SPLIT at %s: %s -- the role has no pose in this half" % (label, e)
            T.n_nodes += 1
            T.rsplit_kills += 1
            T._pre_gate = None
            T.record(lab, depth + 1, br, "DEAD", "RSPLIT-EMPTY", None, t0)
            continue
        T._pre_gate = T.gate_now(lab, "after-apply")
        clip, rnd = N6.cascade(pg, T.rounds, log=T.log)
        T.n_nodes += 1
        r = T.record(lab, depth + 1, br, "DEAD" if pg.dead else "INTERNAL", clip, rnd, t0)
        if role:
            r["pocket_role"] = role
        if r.get("verdict") == "INTERNAL":
            T.expand(depth + 1, lab)

def _expand(T, depth, label):
    pg = T.pg
    ns = rs = None
    while True:
        ch = TB.candidates(pg)
        n_stale = 0
        while ch == "stale" and n_stale < 4:
            t0 = time.time()
            T._pre_gate = (T.nodes[-1].get("trump_gate") or None)
            clip, rnd = N6.cascade(pg, 1, log=T.log)
            T.n_nodes += 1
            n_stale += 1
            r = T.record(label + "r%d" % n_stale, depth, dict(slot=None, kind="refresh", rows=None, named=None), "DEAD" if pg.dead else "INTERNAL", clip, rnd, t0)
            if r.get("verdict") != "INTERNAL":
                return
            ch = TB.candidates(pg)
        if ch == "stale":
            return T.alive("undecided: the option table stayed stale after 4 refresh rounds")
        if ch is None:
            r = T.leaf_rules(depth, label)
            if r == "NS":
                ns = T._ns
                break
            if r == "RSPLIT":
                rs = T._rs
                break
            if r == "CONTINUE":
                continue
            return
        if not ch["branches"]:
            T.kill(label, depth, "S-PAIR", "S-PAIR at %s: no rule-S / A1 compatible pair among its %d alive rows %s (excluded %s)" % (ch["slot"], len(ch["rows"]), ch["rows"], ch["excluded"]))
            return
        if len(ch["branches"]) > 1:
            break
        br = ch["branches"][0]
        t0 = time.time()
        TB.apply_branch(pg, br)
        T.fresh_child()
        T._pre_gate = T.gate_now(label + "u", "after-apply")
        clip, rnd = N6.cascade(pg, T.rounds, log=T.log)
        T.n_nodes += 1
        r = T.record(label + "u", depth, dict(br, unit=True), "DEAD" if pg.dead else "INTERNAL", clip, rnd, t0)
        if r.get("verdict") != "INTERNAL":
            return
    if ns is not None:
        branches = N6.ns_branches(ns)
        T.ns_splits += 1
        T.nodes[-1].update(branch_slot=ns["slot"], branch_role=ns["role"], n_branches=2, branch_rows=["meets", "misses"], ns=ns, verdict="INTERNAL")
        T.log("   Rule NS at %s: split %s at %s (meeting fraction %s)" % (label, ns["role"], ns["slot"], ns["frac"]))
    elif rs is not None:
        branches = T.aligned_branches(rs) if rs.get("aligned") else RS.branches(rs)
        T.rsplits += 1
        if rs.get("aligned"):
            T.aligned_cuts += 1
        T.nodes[-1].update(branch_slot=rs["role"], branch_role=rs["role"], n_branches=2, branch_rows=[b["rows"][0] for b in branches],
                              rsplit=dict(rs, m=str(rs["m"])), verdict="INTERNAL")
        T.log("   %s at %s: cut %s on %s at %s (%s)" % ("ALIGNED split" if rs.get("aligned") else "Lemma ROLE-SPLIT", label, rs["role"], rs["dim"], branches[0]["m_f"],
                                                          ("excess %s x radius, image on the %s side" % (rs.get("excess"), rs.get("side"))) if rs.get("aligned") else "midpoint"))
    else:
        if T.eff_depth(depth, label) >= T.depth_cap or T.n_nodes >= T.node_cap or pg.T.out_of_time():
            why = "depth cap" if T.eff_depth(depth, label) >= T.depth_cap else ("node cap" if T.n_nodes >= T.node_cap else "wall")
            return T.alive("undecided (%s) before branching on %s over %s" % (why, ch["slot"], [b["rows"] for b in ch["branches"]]))
        branches = ch["branches"]
        T.nodes[-1].update(branch_slot=ch["slot"], n_branches=len(branches), branch_rows=[b["rows"] for b in branches])
    st = N6.save_state(pg)
    T.run_children(depth, label, branches, st)
    N6.restore_state(pg, st)

