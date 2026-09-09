"""A182 -- the per-page NODE JOURNAL that makes the assignment search resumable.

results/journal/<nid>.jsonl is append-only: one line per multibox node as it completes (label, roles,
verdict, hulls, the exact miss test per forced cell, chord/lane results) and one "subtree" line per
finished branch of the search tree.  On resume the search re-walks its deterministic order and every
node whose label AND roles match a journal line is REPLAYED from the line (no computation): a
crash costs at most the node in flight.  A "subtree" line short-circuits a whole finished branch.
A heartbeat file logs/heartbeat_<nid>.json carries the node in flight (watch182.ps1 kills the
process tree when it is older than the per-node wall).
"""
import json
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
LOGS = os.path.abspath(os.path.join(HERE, "..", "logs"))
JDIR = os.path.join(RES, "journal")


def _same_roles(a, b, tol=1e-9):
    if set(a) != set(b):
        return False
    return all(len(a[k]) == len(b[k]) and all(abs(float(u) - float(v)) <= tol for u, v in zip(a[k], b[k])) for k in a)


class _Hull:
    def __init__(self, h):
        self.x0, self.x1, self.y0, self.y1, self.th0, self.th1 = h


class _StubBox:
    def __init__(self, h):
        self._h = h

    def union_box(self):
        return _Hull(self._h)


class StubNode:
    """what the search needs of a replayed node: .boxes[k].union_box() and .misses_cell(wbox)."""

    def __init__(self, rec):
        self.rec = rec
        self.boxes = {k: _StubBox(h) for k, h in (rec.get("hull") or {}).items()}
        self.misses = rec.get("misses") or {}
        self.replayed = True

    def misses_cell(self, wbox):
        key = _cellkey(wbox)
        m = self.misses.get(key)
        if m is None:
            raise KeyError("journal replay: no miss record for cell %s at %s" % (key, self.rec.get("label")))
        return {k: dict(misses=bool(v)) for k, v in m.items()}


def _cellkey(wbox):
    return ",".join("%.6f" % float(v) for v in wbox[:4])


class Journal:
    def __init__(self, nid, wall=1500.0):
        os.makedirs(JDIR, exist_ok=True)
        os.makedirs(LOGS, exist_ok=True)
        self.nid, self.wall = nid, wall
        self.path = os.path.join(JDIR, nid + ".jsonl")
        self.hb = os.path.join(LOGS, "heartbeat_%s.json" % nid)
        self.nodes, self.subtrees, self.lanes = {}, {}, {}
        self.n_replayed = 0
        if os.path.exists(self.path):
            for l in open(self.path, encoding="utf-8"):
                if not l.strip():
                    continue
                try:
                    d = json.loads(l)
                except ValueError:
                    continue                                     # a torn last line (crash mid-write)
                k = d.get("kind")
                if k == "subtree":
                    self.subtrees[d["label"]] = d["result"]
                elif k == "lane":
                    self.lanes[(d["label"], d["cell"])] = d
                else:
                    self.nodes[d["label"]] = d

    # ------------------------------------------------------------------ append
    def _write(self, d):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(d) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def node_done(self, rec):
        self.nodes[rec["label"]] = rec
        self._write(rec)

    def subtree_done(self, label, result):
        self.subtrees[label] = result
        self._write(dict(kind="subtree", label=label, result=result, when=time.strftime("%Y-%m-%d %H:%M:%S")))

    def lane_done(self, label, cell, d):
        d = dict(d, kind="lane", label=label, cell=cell)
        self.lanes[(label, cell)] = d
        self._write(d)

    # ------------------------------------------------------------------ replay
    def replay(self, label, roles, cfg=None):
        r = self.nodes.get(label)
        if r is None:
            return None
        if not _same_roles(r.get("roles_in") or {}, {k: list(v) for k, v in roles.items()}):
            return None                                          # same label, different geometry: recompute
        if cfg is not None and r.get("cfg") != cfg:
            return None                                          # written at another nsub/refine/sharp setting
        self.n_replayed += 1
        return r

    # ------------------------------------------------------------------ heartbeat
    def beat(self, label, kind):
        try:
            json.dump(dict(nid=self.nid, label=label, kind=kind, t0=time.time(), pid=os.getpid(), wall=self.wall,
                           when=time.strftime("%Y-%m-%d %H:%M:%S")), open(self.hb, "w"))
        except OSError:
            pass

    def idle(self):
        try:
            json.dump(dict(nid=self.nid, label=None, kind="idle", t0=time.time(), pid=os.getpid(), wall=self.wall),
                      open(self.hb, "w"))
        except OSError:
            pass


def git_commit(paths, msg, tries=6):
    """`git commit -- <pathspecs>` after `git add`; retries on index.lock (another committer).  Never
    fails the caller."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    rel = [os.path.relpath(p, ROOT).replace("\\", "/") for p in paths]
    for k in range(tries):
        try:
            a = subprocess.run(["git", "add", "--"] + rel, cwd=ROOT, capture_output=True, text=True, env=env, timeout=120)
            if a.returncode != 0 and "index.lock" in (a.stderr or ""):
                time.sleep(5 + 7 * k)
                continue
            c = subprocess.run(["git", "commit", "-q", "-m", msg, "--"] + rel, cwd=ROOT, capture_output=True,
                               text=True, env=env, timeout=120)
            if c.returncode == 0 or "nothing to commit" in (c.stdout + c.stderr):
                return True
            if "index.lock" in (c.stderr or ""):
                time.sleep(5 + 7 * k)
                continue
            return False
        except Exception:                                        # noqa: BLE001
            time.sleep(5)
    return False
