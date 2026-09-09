"""A182 -- A180's forced-first assignment search made RESUMABLE and sharper (successor of assign180).

Subclass of assign180.Search:
 * every multibox node is journaled as it completes (journal182) and REPLAYED on resume when its label
   and input roles match; a finished branch is memoised as a "subtree" line; the journal is committed
   after every branch (a crash never costs more than the node in flight);
 * nodes that survive the 4/2 pass are re-normalised at nsub 8 / refine 3 (tree nodes; `--sharp 2`
   also the single/pair option tests) -- both passes are sound, the sharper result is kept;
 * the chord-row kill at every tree node: sum of the roles' exact min-chords on a guard line > s is
   impossible for pairwise-distinct squares (A144 rows via multibox.chord_rows / A161 chordlane);
 * the lane prune of the "new" options: A141/A161's LANE cover of the cell's meeting window against
   the node's grown cores -- lane 0: no unnamed square can meet the cell; lane 1: not two.
Soundness of the search itself: notes/assignment.md (Theorem ASSIGN).
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "attempts", "A161-chord-lane", "code"))
import assign180 as A                                            # noqa: E402  (A180, this directory)
import geo178 as G                                               # noqa: E402  READ-ONLY (A178)
import journal182 as J                                           # noqa: E402

TREE_KINDS = ("base", "forced", "branch")
OPTION_KINDS = ("single", "pair")


class Search(A.Search):
    def __init__(self, rec, cls, journal, sharp=1, chords=1, lanes=1, lane_s=30.0, commit_branches=1,
                 sharp_nsub=8, sharp_refine=3, **kw):
        super().__init__(rec, cls, **kw)
        self.J, self.sharp, self.chords, self.lanes, self.lane_s = journal, sharp, chords, lanes, lane_s
        self.commit_branches, self.sharp_nsub, self.sharp_refine = commit_branches, sharp_nsub, sharp_refine
        self.n_fresh, self.compute_s = 0, 0.0
        self._lines = None
        self._lane_block = {}

    # ------------------------------------------------------------------ one multibox node (journaled)
    def _budget(self):
        if self.n_fresh >= self.max_nodes or (self.deadline and self.compute_s > self.deadline):
            raise A.Budget("node budget exhausted (%d fresh + %d replayed nodes, %.0f s compute)"
                           % (self.n_fresh, self.J.n_replayed, self.compute_s))

    def node(self, roles, corners, label, kind, **extra):
        cfg = "%d/%d/s%d" % (self.nsub, self.refine, self.sharp if (kind in TREE_KINDS or (self.sharp >= 2 and kind in OPTION_KINDS)) else 0)
        r = self.J.replay(label, roles, cfg)
        if r is not None:
            self.n_nodes += 1
            rec = {k: v for k, v in r.items() if k not in ("roles_in", "capture")}
            rec["i"], rec["replayed"] = self.n_nodes, True
            self.steps.append(rec)
            info = dict(dead=r.get("dead"), hull=r.get("hull"), kept=r.get("kept"), seconds=0.0,
                        passes=r.get("passes"), invariant=r.get("invariant"))
            return (None if r.get("dead") else J.StubNode(r)), info, rec
        self._budget()
        self.n_nodes += 1
        self.n_fresh += 1
        self.J.beat(label, kind)
        t0 = time.time()
        nd, info = G.run_node(roles, corners=corners or None, nsub=self.nsub, refine=self.refine, label=label)
        sharp = None
        if not info["dead"] and self.sharp and (kind in TREE_KINDS or (self.sharp >= 2 and kind in OPTION_KINDS)):
            k42 = {k: v for k, v in info["kept"].items() if not k.startswith("P")}
            nd2, info2 = G.run_node(roles, corners=corners or None, nsub=self.sharp_nsub, refine=self.sharp_refine,
                                    label=label)
            sharp = dict(kept42=k42, s42=info["seconds"], s83=info2["seconds"],
                         kept83={k: v for k, v in (info2.get("kept") or {}).items() if not k.startswith("P")},
                         dead83=info2["dead"])
            nd, info = nd2, info2                                 # [T] both passes sound; keep the sharper
        misses, chord = {}, None
        if not info["dead"]:
            for it in self.items.values():
                m = nd.misses_cell(tuple(it["wbox"]))
                misses[J._cellkey(it["wbox"])] = {k: bool(v["misses"]) for k, v in m.items()}
            if self.chords and kind in TREE_KINDS:
                chord = self.chord_kill(nd)
                if chord.get("dead"):
                    info["dead"] = chord["dead"]
        self.compute_s += time.time() - t0
        rec = dict(i=self.n_nodes, label=label, kind=kind, roles=list(roles), corners=dict(corners or {}),
                   roles_in={k: list(v) for k, v in roles.items()}, cfg=cfg, dead=info.get("dead"),
                   seconds=round(time.time() - t0, 2), passes=info.get("passes"), invariant=info.get("invariant"),
                   kept={k: v for k, v in (info.get("kept") or {}).items() if not k.startswith("P")},
                   hull=info.get("hull"), misses=misses, chord=chord, sharp=sharp, **extra)
        if kind in TREE_KINDS and G.CAPTURE:
            rec["capture"] = G.CAPTURE[-1].get("boxes")
        self.J.node_done(rec)
        self.steps.append({k: v for k, v in rec.items() if k not in ("roles_in", "capture")})
        return (None if info["dead"] else nd), info, rec

    # ------------------------------------------------------------------ chord rows
    def chord_kill(self, nd):
        """A144 guard rows on the normalised node: rhs = s - sum_j minchord(B_j, l) < 0 kills."""
        import chordlane as CL                                   # READ-ONLY (A161)
        if self._lines is None:
            self._lines = CL.line_candidates("v", n=24) + CL.line_candidates("h", n=24)
        t0 = time.time()
        try:
            rows = nd.chord_rows(self._lines)
        except Exception as e:                                   # noqa: BLE001
            return dict(error=repr(e)[:120], seconds=round(time.time() - t0, 2))
        worst = min(rows, key=lambda r: r["rhs_float"])
        out = dict(n_lines=len(rows), min_rhs=worst["rhs_float"], line="%s=%s" % (worst["orient"], worst["off"]),
                   beta=worst["beta"], seconds=round(time.time() - t0, 2))
        if worst["rhs_float"] < 0:
            out["dead"] = "chord row: sum of min-chords on %s exceeds s by %.4f" % (out["line"], -worst["rhs_float"])
            out["row"] = worst
        return out

    # ------------------------------------------------------------------ lanes
    def lane_of(self, st, cell):
        key = (st["label"], cell)
        d = self.J.lanes.get(key)
        if d is not None:
            return d.get("lane")
        nd = st.get("nd")
        if nd is None or getattr(nd, "replayed", False) or not self.lanes:
            return None
        it = self.items[cell]
        t0 = time.time()
        try:
            r = nd.lane(tuple(it["wbox"]), None, deadline=time.time() + self.lane_s)
            d = dict(lane=r.get("lane"), ok=r.get("ok"), reason=r.get("reason"), depth=r.get("depth"),
                     n_open=len(r.get("open") or []), n_leaves=len(r.get("leaves") or []))
        except Exception as e:                                   # noqa: BLE001
            d = dict(lane=None, error=repr(e)[:120])
        d["seconds"] = round(time.time() - t0, 2)
        self.compute_s += d["seconds"]
        self.J.lane_done(st["label"], cell, d)
        self.log("      lane %s at %s: %s (%.0fs%s)" % (cell, st["label"], d.get("lane"), d["seconds"],
                                                       ("; " + str(d.get("reason"))) if d.get("reason") else ""))
        return d.get("lane")

    def options(self, st, cell):
        L = self.lane_of(st, cell) if self.lanes else None
        self._lane_block[(st["label"], cell)] = L
        return super().options(st, cell)

    def test_members(self, st, members, cell, kind):
        L = self._lane_block.get((st["label"], cell))
        if L == 0 and "new" in members:
            lab = st["label"] + "/?%s:%s" % (cell, "+".join(members))
            self.steps.append(dict(label=lab, kind=kind, cell=cell, members=list(members),
                                   dead="lane 0: no unnamed square can meet %s against the grown cores" % cell))
            return False, None
        return super().test_members(st, members, cell, kind)

    def test_two_new(self, st, cell, hullB):
        L = self._lane_block.get((st["label"], cell))
        if L == 1:
            self.steps.append(dict(label=st["label"] + "/?%s:new+new" % cell, kind="pair-split", cell=cell,
                                   dead="lane 1: at most one unnamed square can meet %s" % cell))
            self.log("      %s new+new excluded by lane 1" % cell)
            return []
        return super().test_two_new(st, cell, hullB)

    # ------------------------------------------------------------------ the search (memoised)
    def normalise(self, st, kind):
        ok = super().normalise(st, kind)
        if not ok:
            last = self.steps[-1] if self.steps else {}
            st["dead_reason"] = last.get("dead") or "EmptyBox"
        return ok

    def search(self, st, depth=0):
        memo = self.J.subtrees.get(st["label"])
        if memo is not None:
            self.log("  MEMO %s: %s" % (st["label"], memo.get("verdict")))
            return memo
        label0 = st["label"]
        try:
            kind, o = self.propagate(st)
        except A.Budget as e:
            return dict(label=st["label"], verdict="UNDECIDED", leaf=str(e))
        if kind == "dead":
            r = dict(label=st["label"], verdict="DEAD", leaf="no admissible meeter assignment at %s" % o["cell"],
                     detail={k: v for k, v in o.items() if k != "opts"})
            if o.get("note") == "the forced node is dead":
                r["leaf"] = "forced node dead at %s (%s)" % (o["cell"], st.get("dead_reason"))
            self.J.subtree_done(label0, r)
            return r
        if kind == "complete":
            r = dict(label=st["label"], verdict="ALIVE(geometry)", leaf=None, roles=st["roles"], assign=st["assign"],
                     nF=st["nF"], kept=st.get("kept"))
            if self.leaf_fn is not None:
                r.update(self.leaf_fn(self, st))
            self.J.subtree_done(label0, r)
            return r
        opts = sorted(o["opts"], key=lambda t: (t[:2].count("new"), tuple(t[:2])))
        kids = []
        for k, opt in enumerate(opts):
            st2 = self.apply(st, o["cell"], opt, "b%d:" % (k + 1))
            self.log("  BRANCH %s <- %s (%d/%d)" % (o["cell"], "+".join(str(m) for m in opt[:2]), k + 1, len(opts)))
            if st2["label"] in self.J.subtrees:
                kids.append(self.J.subtrees[st2["label"]])
                self.log("  MEMO %s: %s" % (st2["label"], kids[-1].get("verdict")))
                continue
            if not self.normalise(st2, "branch"):
                kids.append(dict(label=st2["label"], verdict="DEAD", leaf="branch node dead (%s)" % st2.get("dead_reason")))
                self.J.subtree_done(st2["label"], kids[-1])
            else:
                kids.append(self.search(st2, depth + 1))
            if self.commit_branches:
                J.git_commit([self.J.path], "A182: %s journal after branch %s (%s)" % (self.J.nid, st2["label"][-60:],
                                                                                        kids[-1].get("verdict")))
            if kids[-1].get("verdict") == "UNDECIDED" and "budget exhausted" in str(kids[-1].get("leaf")):
                return dict(label=st["label"], verdict="UNDECIDED", branch=o["cell"], n_children=len(kids),
                            children=kids, leaf=kids[-1]["leaf"])
        v = ("DEAD" if all(c["verdict"] == "DEAD" for c in kids) else
             ("ALIVE" if any(c["verdict"].startswith("ALIVE") for c in kids) else "UNDECIDED"))
        r = dict(label=st["label"], verdict=v, branch=o["cell"], n_children=len(kids), children=kids)
        self.J.subtree_done(label0, r)
        return r

    def run(self):
        st = self.root
        if not self.normalise(st, "base"):
            return dict(verdict="DEAD", leaf="base node dead (%s)" % st.get("dead_reason"), tree=None)
        tree = self.search(st)
        return dict(verdict=tree["verdict"], leaf=tree.get("leaf"), tree=tree)
