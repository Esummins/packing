#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""status_gallery.py -- the shadow-gallery status board (A162).

Collects EVERY kill record in the repo into one table

    (camp, tree tag, node id)  ->  (dead?, leaf, attempt, certificate path, date)

then decides ALIVE / DEAD for every page of every gallery under docs/shadows/,
moves the DEAD pages into docs/shadows/<gallery>/killed/ with `git mv` (never a
delete), and writes docs/shadows/STATUS.md -- the checklist the PI reads first.

    python docs/shadows/status_gallery.py            # collect, move, write STATUS.md
    python docs/shadows/status_gallery.py --dry-run  # collect and print, write nothing

Rerunnable and idempotent: a second run with the same records is a no-op.

SAFETY (enforced, not documented):
  * NO LP is solved.  Every verdict is READ from an existing record.
  * NOTHING outside docs/shadows/ is written, moved or deleted -- see _guard().
  * No recursive delete anywhere.  DEAD pages are `git mv`d into killed/.
  * PYTHONDONTWRITEBYTECODE is set in-process.

SOUNDNESS (why a record counts as a kill):
  * a kill needs a CONVERGED bound (tau < budget with converged/minmass sound) or
    a certificate whose result is PASS.  A124/A158: records with
    `converged = false, dead_unconverged = true` whose stored tau < budget were
    NEVER a bound (A140's l1_148 / l2_p65_101 / l2_p65_111 are exactly this).
  * 'kill-candidate', 'NO-KILL', 'LOST-KILL-ON-RESOLVE', 'TOO-TIGHT',
    'WALL-CAP', 'FAIL(...)' are NOT kills.  WALL-CAP is never a verdict
    (A137 D.5).
  * A158's yescert158 rows say `verdict = "KILL"` with `kill = false` -- the
    conditional lane leaf reached 1 + LANE + M = 2 on every measured cell, so
    they are NOT kills.  In particular c0_Y0076's NO child is NOT a kill.
  * `*__exall.json` under any certs/ tree is NOT a kill record (A148's rule: it
    exists on LOST-KILL / TOO-TIGHT / FAIL too).  `*.clipkill.json` IS one.
  * A137 C.3 -- AN ID IS NOT A NODE.  k5_11_interior_Y0041_D02 is a node of the
    L1 tree (eps-fat pins) AND a different node of the G1 tree (delta = 1e-2
    slack pins).  A kill transfers only DOWNWARD in the pin core, so a record is
    attributed to a tree tag by, in order:
        (1) its own applies_to_tags / not_applicable_to_tags (A137's fold137),
        (2) its recorded prior tau (tau_before / prior_tau) matched against the
            canonical per-(tag, id) tau in A57's tree jsonl,
        (3) the id occurring in exactly one tree,
        (4) otherwise UNRESOLVED -- the record is REFUSED and listed in
            STATUS.md.  A refusal never kills a page.
  * Monotonicity: a killed node kills its descendants (A57 `<id>_Dnn` children,
    k0 `l2_pNN_xxx` under `l1_0NN` / `node_NN`, `l3_ppNNN_a_b` under
    `l2_pNNN_a`).
"""

from __future__ import annotations

import argparse
import collections
import csv
import glob
import io
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

HERE = os.path.dirname(os.path.abspath(__file__))          # <repo>/docs/shadows
SHADOWS = HERE
ROOT = os.path.dirname(os.path.dirname(HERE))              # <repo>

# ---------------------------------------------------------------------------
# write guard: nothing outside docs/shadows/ may be touched by this script
# ---------------------------------------------------------------------------


def _guard(path):
    """Refuse any write/move target outside docs/shadows/."""
    p = os.path.abspath(path)
    if not (p == SHADOWS or p.startswith(SHADOWS + os.sep)):
        raise SystemExit(
            "REFUSED: status_gallery.py may only write inside docs/shadows/ "
            "(target was %s)" % p
        )
    return p


def rel(path):
    return os.path.relpath(os.path.abspath(path), ROOT).replace("\\", "/")


def jl(path):
    """Stream a .jsonl file, skipping blanks and unparseable lines."""
    if not os.path.exists(path):
        return
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line[0] != "{":
                continue
            try:
                yield json.loads(line)
            except ValueError:
                continue


def jf(path):
    if not os.path.exists(path):
        return None
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            return json.load(fh)
    except ValueError:
        return None


def fdate(path):
    """mtime as a date string, for records that carry no date of their own."""
    try:
        import datetime

        return datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime(
            "%Y-%m-%d"
        )
    except OSError:
        return ""


def day(s):
    return (str(s) or "")[:10]


_ROOT_N = os.path.normcase(os.path.abspath(ROOT))


def norm_cert(p):
    """Recorded certificate paths are absolute Windows paths; show them repo-relative."""
    if not isinstance(p, str) or not p:
        return ""
    q = p.replace("\\", "/")
    if os.path.normcase(os.path.abspath(p)).startswith(_ROOT_N + os.sep):
        return os.path.relpath(os.path.abspath(p), ROOT).replace("\\", "/")
    return q


# ---------------------------------------------------------------------------
# verdict vocabulary
# ---------------------------------------------------------------------------

DEAD_CERT_PREFIXES = ("PASS", "KILL-BY-LOGIC", "KILL BY", "DEAD BY")
NOT_A_KILL = (
    "NO-KILL",
    "LOST-KILL-ON-RESOLVE",
    "TOO-TIGHT",
    "WALL-CAP",
    "FAIL",
    "ALIVE",
    "kill-candidate",
    "NOT-RUN",
    "SKIP",
)


def cert_is_dead(cert):
    """A tree-jsonl / record `cert` string that means the node is dead."""
    if not isinstance(cert, str):
        return False
    c = cert.strip()
    if any(c.startswith(w) for w in NOT_A_KILL):
        return False
    return any(c.startswith(w) for w in DEAD_CERT_PREFIXES)


# ---------------------------------------------------------------------------
# node keys and ancestry
# ---------------------------------------------------------------------------

D_SUFFIX = re.compile(r"_D\d+$")


def a57_ancestors(nid):
    """k5_11_interior_Y0041_D02_D05 -> [..._D02, k5_11_interior_Y0041]."""
    out, cur = [], nid
    while True:
        nxt = D_SUFFIX.sub("", cur)
        if nxt == cur:
            break
        out.append(nxt)
        cur = nxt
    return out


def k0_ancestors(cell):
    """l3_ppNNN_a_b -> l2_pNNN_a -> l1_0NN / node_NN."""
    m = re.match(r"^l3_pp(\d+)_(\w+)_(\w+)$", cell)
    if m:
        parent = "l2_p%s_%s" % (m.group(1), m.group(2))
        return [parent] + k0_ancestors(parent)
    m = re.match(r"^l2_p(\d+)_(\w+)$", cell)
    if m:
        n = int(m.group(1))
        return ["l1_%03d" % n, "node_%d" % n]
    return []


def k0_aliases(cell):
    """The k0 corpus writes the same cell as l1_071 / node_71 / l1_071_plain_warm."""
    out = {cell}
    m = re.match(r"^l1_0*(\d+)$", cell)
    if m:
        out.add("node_%d" % int(m.group(1)))
        out.add("l1_%03d" % int(m.group(1)))
    m = re.match(r"^node_(\d+)$", cell)
    if m:
        out.add("l1_%03d" % int(m.group(1)))
    return out


K0_SUFFIXES = (
    "_plain_warm",
    "_sh1_warm",
    "_sh2adj_warm",
    "_sh2dia_warm",
    "_sh3_warm",
    "_warm",
)


def k0_strip(nid):
    for s in K0_SUFFIXES:
        if nid.endswith(s):
            return nid[: -len(s)]
    return nid


# ---------------------------------------------------------------------------
# the canonical A57 tree corpus -- (tag, id) -> record; the tag authority
# ---------------------------------------------------------------------------


def load_a57_corpus():
    """Read A57's canonical tree jsonl.  Returns

        corpus[(tag, id)] = {'cert', 'tau', 'converged', 'files', 'cert_path'}
        tags_of[id]       = set of tags the id exists in

    The tag is the filename's tree tag with the shard/window suffix removed:
    tree_k5_11_interior_G1_s3.jsonl -> k5_11_interior_G1;
    tree_k5_11_interior_G1_D2_s0.jsonl -> k5_11_interior_G1_D2.
    """
    corpus, tags_of = {}, collections.defaultdict(set)
    pat = os.path.join(ROOT, "attempts", "A57-shadow-trees", "results", "tree_*.jsonl")
    for path in sorted(glob.glob(pat)):
        stem = os.path.basename(path)[len("tree_") : -len(".jsonl")]
        # strip a trailing shard/window marker: _s<digits>
        tag = re.sub(r"_s\d+$", "", stem)
        for d in jl(path):
            nid = d.get("id")
            if not isinstance(nid, str):
                continue
            tags_of[nid].add(tag)
            key = (tag, nid)
            cur = corpus.setdefault(
                key,
                {
                    "cert": None,
                    "tau": None,
                    "converged": None,
                    "files": [],
                    "cert_path": None,
                    "budget": None,
                },
            )
            cur["files"].append(rel(path))
            # last write wins per tag, but a dead cert is sticky (monotone)
            if d.get("tau") is not None:
                cur["tau"] = d.get("tau")
            cur["converged"] = d.get("converged")
            cur["budget"] = d.get("budget")
            if cert_is_dead(d.get("cert")) or not cert_is_dead(cur["cert"]):
                cur["cert"] = d.get("cert")
            if cert_is_dead(d.get("cert")):
                cur["cert"] = d.get("cert")
                cur["cert_path"] = d.get("cert_path")
    return corpus, tags_of


# ---------------------------------------------------------------------------
# the kill table
# ---------------------------------------------------------------------------


class Table(object):
    """node -> kill records, with A137's tag rule applied at attribution time."""

    def __init__(self, corpus, tags_of):
        self.corpus = corpus
        self.tags_of = tags_of
        self.rows = []           # every record scanned (kill or not)
        self.refused = []        # records whose tree tag could not be resolved
        self.by_source = collections.OrderedDict()

    # -- attribution -------------------------------------------------------
    def resolve_tags(self, camp, nid, rec):
        """Return (tags, how) -- the tree tags this record kills, or (None, why)."""
        if camp != "A57":
            return ({"trump5_j0"} if camp == "A60" else {"k0_00"}), "single-tree camp"

        appl = rec.get("applies_to_tags")
        nappl = rec.get("not_applicable_to_tags") or []
        if isinstance(appl, list) and appl:
            return set(appl) - set(nappl), "applies_to_tags (A137 fold137)"

        prior = rec.get("tau_before")
        if prior is None:
            prior = rec.get("prior_tau")
        if isinstance(prior, (int, float)):
            hits = set()
            for tag in self.tags_of.get(nid, ()):
                tau = self.corpus[(tag, nid)]["tau"]
                if isinstance(tau, (int, float)) and abs(tau - prior) <= 1e-6 * max(
                    1.0, abs(prior)
                ):
                    hits.add(tag)
            if len(hits) == 1:
                return hits, "prior tau matched the tree record"
            if len(hits) > 1:
                return hits, "prior tau matched %d trees (all)" % len(hits)

        tags = self.tags_of.get(nid) or set()
        if len(tags) == 1:
            return set(tags), "id occurs in exactly one tree"
        if not tags:
            return set(), "id in no A57 tree corpus"
        return None, "AMBIGUOUS id over %d trees, no tag and no prior tau" % len(tags)

    def add(self, source, camp, nid, dead, leaf, attempt, cert, date, note=""):
        tags, how = (None, "")
        if dead:
            tags, how = self.resolve_tags(camp, nid, {})
        row = {
            "source": source,
            "camp": camp,
            "id": nid,
            "dead": bool(dead),
            "leaf": leaf,
            "attempt": attempt,
            "cert": cert,
            "date": date,
            "note": note,
            "tags": sorted(tags) if tags else [],
            "how": how,
        }
        self.rows.append(row)
        return row

    def add_rec(self, source, camp, nid, dead, leaf, attempt, cert, date, rec, note=""):
        tags, how = self.resolve_tags(camp, nid, rec) if dead else (set(), "")
        if dead and tags is None:
            self.refused.append(
                {
                    "source": source,
                    "camp": camp,
                    "id": nid,
                    "leaf": leaf,
                    "attempt": attempt,
                    "why": how,
                }
            )
            tags = set()
        row = {
            "source": source,
            "camp": camp,
            "id": nid,
            "dead": bool(dead),
            "leaf": leaf,
            "attempt": attempt,
            "cert": norm_cert(cert),
            "date": date,
            "note": note,
            "tags": sorted(tags or ()),
            "how": how,
        }
        self.rows.append(row)
        self.by_source.setdefault(source, {"rows": 0, "kills": 0})
        self.by_source[source]["rows"] += 1
        if dead:
            self.by_source[source]["kills"] += 1
        return row

    # -- lookup ------------------------------------------------------------
    def kills_for(self, camp, tag, nid, aliases=None):
        want = set(aliases or ()) | {nid}
        out = []
        for r in self.rows:
            if not r["dead"] or r["camp"] != camp:
                continue
            if r["id"] not in want:
                continue
            if camp == "A57" and tag not in r["tags"]:
                continue
            out.append(r)
        return out


# ---------------------------------------------------------------------------
# the collectors, one per named source
# ---------------------------------------------------------------------------

A = lambda *p: os.path.join(ROOT, "attempts", *p)


def collect(table, corpus):
    # (0) A57's canonical tree jsonl -- the corpus's own verdicts ------------
    for (tag, nid), v in sorted(corpus.items()):
        if not cert_is_dead(v["cert"]):
            continue
        leaf = v["cert"]
        if leaf.startswith("PASS"):
            leaf = "PASS -- case-measure-certificate-v1 in A57's own tree certs (%s)" % tag
        r = table.add_rec(
            "A57 tree jsonl (%s) -- dead rows only" % tag,
            "A57",
            nid,
            True,
            leaf,
            "A57 tree",
            v["cert_path"] or (v["files"][-1] if v["files"] else ""),
            fdate(os.path.join(ROOT, v["files"][-1])) if v["files"] else "",
            {"applies_to_tags": [tag]},
        )
        r["tags"] = [tag]
        r["how"] = "the record's own tree jsonl (tag is the file)"

    # (1) A137 -- fresh-emission clip kills ---------------------------------
    p = A("A137-night-shift-2", "results", "clipkills137.jsonl")
    for d in jl(p):
        cp = d.get("cert_path") or ""
        table.add_rec(
            "A137 clipkills137.jsonl",
            "A57",
            d.get("id", ""),
            str(d.get("verdict", "")).startswith("KILL"),
            d.get("verdict", ""),
            "A137",
            cp,
            day(d.get("when")),
            d,
        )

    # (2) the supersession ledgers (A137's fold-in of A131/A135/A141/A142/A145)
    LEDGERS = [
        ("A57-shadow-trees/results/superseded_by_backlog_A137.jsonl", "A57", "A137"),
        ("A57-shadow-trees/results/superseded_by_exactcore_A137.jsonl", "A57", "A137"),
        ("A57-shadow-trees/results/superseded_by_tight_core.jsonl", "A57", "A96"),
        ("A60-trump5-campaign/results/superseded_by_backlog_A137.jsonl", "A60", "A137"),
        ("A149-a57-reprice/results/superseded_by_exactcore_A149.jsonl", "A57", "A149"),
        ("A149-a57-reprice/results/superseded_by_exactcore_v3_A149.jsonl", "A57", "A149"),
        ("A149-a57-reprice/results/superseded_by_exactcore_a60_A149.jsonl", "A60", "A149"),
        ("A149-a57-reprice/results/superseded_by_exactcore_a60_v3_A149.jsonl", "A60", "A149"),
    ]
    for relp, camp, att in LEDGERS:
        path = os.path.join(ROOT, "attempts", *relp.split("/"))
        for d in jl(path):
            c = d.get("camp") or camp
            table.add_rec(
                "ledger %s" % os.path.basename(relp),
                c,
                d.get("id", ""),
                True,  # a supersession ledger row IS a recorded certified kill
                d.get("leaf") or d.get("superseded_by") or "",
                d.get("folded_by") or att,
                d.get("cert") or "",
                day(d.get("recorded")),
                d,
            )

    # (3) A149's day-shift records (exact / poly / a60 re-emission) ----------
    for path in sorted(
        glob.glob(A("A149-a57-reprice", "results", "exact_reemit_*.jsonl"))
        + glob.glob(A("A149-a57-reprice", "results", "poly149.jsonl"))
        + glob.glob(A("A149-a57-reprice", "results", "a60_reemit_*.jsonl"))
    ):
        camp = "A60" if "a60_" in os.path.basename(path) else "A57"
        for d in jl(path):
            table.add_rec(
                "A149 %s" % os.path.basename(path),
                d.get("camp") or camp,
                d.get("id", ""),
                d.get("result") == "PASS",
                "case-measure-certificate-v1 (exact cores, FROZEN verify_case)",
                "A149",
                d.get("cert") or "",
                day(d.get("when")),
                d,
            )

    # (4) A156's day-shift emission LP records ------------------------------
    for path in sorted(glob.glob(A("A156-day-shift", "results", "lp156_*.jsonl"))):
        for d in jl(path):
            table.add_rec(
                "A156 %s" % os.path.basename(path),
                "A57",
                d.get("id", ""),
                d.get("result") == "PASS",
                "case-measure-certificate-v1 (emission LP, FROZEN verify_case)",
                "A156",
                d.get("cert") or "",
                day(d.get("when")),
                d,
            )

    # (5) A136 / A96 closures ----------------------------------------------
    for d in jl(A("A136-a120-resume", "results", "closures136.jsonl")):
        table.add_rec(
            "A136 closures136.jsonl",
            "A57",
            d.get("node", ""),
            d.get("status") == "CLOSED",
            "A120 composition (YES local cert + all NO children)",
            d.get("attempt") or "A136",
            ((d.get("hD") or {}).get("certificate") or {}).get("file", ""),
            day(d.get("generated")),
            d,
        )
    for d in jl(A("A96-a57-parametric", "results", "a120_closures.jsonl")):
        table.add_rec(
            "A96 a120_closures.jsonl",
            "A57",
            d.get("id", ""),
            d.get("status") == "CLOSED",
            "A120 composition",
            "A96",
            d.get("cert") or "",
            "",
            d,
            note=d.get("reason") or "",
        )

    # (6) A140's k0 exact-core arm -- cert PASS ONLY ------------------------
    for d in jl(A("A140-k0-residue-gallery", "results", "exactcore140.jsonl")):
        cert = d.get("cert") or {}
        ok = isinstance(cert, dict) and cert.get("result") == "PASS"
        dead = bool(d.get("kills")) and bool(d.get("kills_converged")) and ok
        table.add_rec(
            "A140 exactcore140.jsonl",
            "k0",
            d.get("cell", ""),
            dead,
            "LP kill on exact certified-maximal cores (FROZEN verify_case)",
            "A140",
            (cert.get("cert") if isinstance(cert, dict) else "") or "",
            fdate(A("A140-k0-residue-gallery", "results", "exactcore140.jsonl")),
            d,
            note=""
            if dead
            else "kills=%s converged=%s cert=%s -- tau was never a bound (A124)"
            % (d.get("kills"), d.get("kills_converged"), (cert or {}).get("result")),
        )

    # (7) A141's polycore lane kills (k0 cells + A57/A60 slots) -------------
    for d in jl(A("A141-polycore-lane", "results", "polycore_lane_kills.jsonl")):
        cls = d.get("cls") or ""
        camp = "k0" if cls == "k0_00" else ("A60" if cls.startswith("trump5") else "A57")
        nid = k0_strip(d.get("nid", "")) if camp == "k0" else d.get("nid", "")
        cert = (d.get("cert") or {}).get("path", "") if isinstance(d.get("cert"), dict) else ""
        table.add_rec(
            "A141 polycore_lane_kills.jsonl",
            camp,
            nid,
            str(d.get("verdict", "")).startswith("DEAD BY"),
            "%s [%s]" % (d.get("leaf") or "polycore lane", d.get("corner") or ""),
            "A141",
            cert,
            fdate(A("A141-polycore-lane", "results", "polycore_lane_kills.jsonl")),
            d,
        )

    # (7b) A161's chord-limited lane kills (A57 k5_16 + A60 trump5 wall slots) ----
    for d in jl(A("A161-chord-lane", "results", "t3_dedup.jsonl")):
        if str(d.get("verdict", "")) != "KILL":
            continue
        cls = d.get("cls") or ""
        camp = "A60" if cls.startswith("trump5") else "A57"
        slot = str(d.get("slot") or "")
        cert = os.path.join("attempts", "A161-chord-lane", "certs",
                            "cl_%s__%s.json" % (d.get("nid", ""), slot.replace("(", "").replace(",", "_").replace(")", "")))
        table.add_rec(
            "A161 t3_dedup.jsonl",
            camp,
            d.get("nid", ""),
            True,
            "chord-limited lane [%s]" % slot,
            "A161",
            cert,
            fdate(A("A161-chord-lane", "results", "t3_dedup.jsonl")),
            d,
        )

    # (7c) A167's conditional chord-limited lane kills ------------------------
    for shard in ("pass_s0.jsonl", "pass_s1.jsonl"):
        for d in jl(A("A167-condlane-pass", "results", shard)):
            if str(d.get("verdict", "")) != "KILL":
                continue
            cls = d.get("cls") or ""
            camp = "A60" if cls.startswith("trump5") else "A57"
            slot = str(d.get("slot") or "")
            cert = os.path.join("attempts", "A167-condlane-pass", "certs",
                                "cond_%s__%s.json" % (d.get("nid", ""), slot.replace("(", "").replace(",", "_").replace(")", "")))
            table.add_rec(
                "A167 %s" % shard,
                camp,
                d.get("nid", ""),
                True,
                "conditional chord-limited lane [%s]" % slot,
                "A167",
                cert,
                fdate(A("A167-condlane-pass", "results", shard)),
                d,
            )

    # (7e) A188's S01 LINE-basin closures (docs/proofs/local_certificate_s01.md Theorem S01-LINE).
    #      results/consumed188.jsonl lists every page whose conditioned box is inside a certified
    #      band; only verdict == "RETIRED" (a k = 3 line: the page itself dead by the chord sum, or a
    #      LocalCompose closure with a citeable NO side) is a kill -- CONTAINED_YES_LEAF rows still
    #      owe their NO children and are NOT collected (A187 s5: containment is necessary, not sufficient).
    for d in jl(A("A188-s01-basin", "results", "consumed188.jsonl")):
        if str(d.get("verdict", "")) != "RETIRED":
            continue
        cls = d.get("cls") or ""
        camp = "A60" if cls.startswith("trump5") else "A57"
        table.add_rec(
            "A188 consumed188.jsonl",
            camp,
            d.get("nid", ""),
            True,
            "S01 LINE basin [%s, k=%s]" % (d.get("line", ""), d.get("k", "")),
            "A188",
            d.get("cert_path") or "",
            fdate(A("A188-s01-basin", "results", "consumed188.jsonl")),
            d,
        )

    # (7g) A190's GUARD-LINE kills (docs/proofs/guardline_clause.md Theorem G): the chord-sum column in the
    #      node LP and the `guardlines` clause of verify_case_v5 (over A185's v4 over v3 over v1, shas
    #      asserted).  results/run190.jsonl is resumable: the LAST row per id is the verdict; only
    #      "DEAD(LP, v5 certified)" rows are kills, and every one is [C] under v5 ONLY -- the frozen v1
    #      chain does not read `guardlines` (flagged "v5" in the leaf and the note).
    last190 = {}
    for d in jl(A("A190-guardline-clause", "results", "run190.jsonl")):
        if d.get("id"):
            last190[d["id"]] = d
    for nid, d in sorted(last190.items()):
        if not str(d.get("verdict", "")).startswith("DEAD(LP, v5 certified)"):
            continue
        cls = d.get("cls") or ""
        camp = "A60" if cls.startswith("trump5") else "A57"
        act = [z for z in (d.get("z") or []) if float(z.get("z") or 0) > 1e-6]
        lines = ", ".join("%s=%.4f" % (z["line"]["orient"], z["line"]["off_float"]) for z in act) or "-"
        table.add_rec(
            "A190 run190.jsonl",
            camp,
            nid,
            True,
            "guard-line clause v5 [%s; tau %.4f < %s]" % (lines, float(d.get("tau") or 0), d.get("budget")),
            "A190",
            d.get("cert") or "",
            fdate(A("A190-guardline-clause", "results", "run190.jsonl")),
            dict(d, tau_before=d.get("tau_stored")),
            note="[C] under verify_case_v5 ONLY (guardlines clause; v1/v3/v4 imported unchanged)",
        )

    # (7d) A178's geometry-cascade kills (forced-corner / forced-slot roles, multibox pair leaf)
    #      results/geopass178.jsonl is resumable: the LAST row per nid is the verdict.
    last178 = {}
    for d in jl(A("A178-gallery-geometry", "results", "geopass178.jsonl")):
        if d.get("nid"):
            last178[d["nid"]] = d
    for nid, d in sorted(last178.items()):
        if str(d.get("verdict", "")) != "DEAD":
            continue
        camp = "k0" if d.get("gallery") == "k0v4" else ("A60" if str(d.get("camp")) == "A60" else "A57")
        table.add_rec(
            "A178 geopass178.jsonl",
            camp,
            nid,
            True,
            "geometry cascade: %s (forced_corners.md Theorem FC; A171 multibox pair leaf)" % (d.get("leaf") or ""),
            "A178",
            d.get("cert") or "",
            fdate(A("A178-gallery-geometry", "results", "geopass178.jsonl")),
            d,
            note=("CONDITIONAL on K0-O1 (k1_00's tree): the k0 corner pairs are the K0-BLOCKED hypothesis"
                  if camp == "k0" else ""),
        )

    # (7e) A182's forced-first ASSIGNMENT kills (A180 resumed after the 15:46 crash): six forced cells x
    #      two distinct meeters from {H, F1..F5}, unit propagation then branching; multibox pair leaf,
    #      chord-row kill or multi-box case LP.  results/assign182.jsonl is resumable: the LAST row per
    #      nid is the verdict; the per-page node journal is results/journal/<nid>.jsonl.
    last182 = {}
    for d in jl(A("A180-forced-first-assignment", "results", "assign182.jsonl")):
        if d.get("nid"):
            last182[d["nid"]] = d
    for nid, d in sorted(last182.items()):
        if str(d.get("verdict", "")) != "DEAD":
            continue
        camp = "k0" if d.get("gallery") == "k0v4" else ("A60" if str(d.get("camp")) == "A60" else "A57")
        cert = str(d.get("cert") or ("attempts/A180-forced-first-assignment/results/trees/%s.json" % nid))
        table.add_rec(
            "A182 assign182.jsonl",
            camp,
            nid,
            True,
            "forced-first assignment: %s (notes/assignment.md Theorem ASSIGN; %d multibox nodes)"
            % (d.get("leaf") or "every assignment node dead", int(d.get("n_nodes") or 0)),
            "A182",
            cert.split(";")[0],
            fdate(A("A180-forced-first-assignment", "results", "assign182.jsonl")),
            d,
        )

    # (7i) A198's FASTPROP kills (the PI's cheap exact propagation over the page node, 2026-09-10): per forced slot
    #      (forced_corners.md Theorem FC: two DISTINCT non-pin meeters of the widened open box) the meeter's centre
    #      cells of a grid of side < 1/sqrt2 (Lemma A1: one centre per cell) are bisected with multibox's exact
    #      dead test against every role's K', A161's exact miss test and (corners only) A173's lonely clip; the
    #      JOINT count asks whether H + the free squares can cover every slot twice with pairwise-distinct cells,
    #      the exact joint reach on window intersections, and the open-chord rows; H barred from a slot and
    #      infeasible => H forced there and clipped (A161 exact) -- a page is DEAD when the count is infeasible, H
    #      is forced to slots it cannot meet jointly, a slot H misses has < 2 alive cells, or multibox raises
    #      EmptyBox at the re-normalisation.  results/fastprop198.jsonl is resumable: the LAST row per nid is the
    #      verdict; the certificate (certs/fp198_<nid>.json) is the list of exact tests.  [C: geometry, fastprop] --
    #      the frozen LP verifier is NOT involved.
    last198 = {}
    for d in jl(A("A198-fastprop", "results", "fastprop198.jsonl")):
        if d.get("nid"):
            last198[d["nid"]] = d
    for nid, d in sorted(last198.items()):
        if str(d.get("verdict", "")) != "DEAD":
            continue
        cls = d.get("cls") or ""
        camp = "A60" if cls.startswith("trump5") else "A57"
        table.add_rec(
            "A198 fastprop198.jsonl",
            camp,
            nid,
            True,
            "fastprop: %s (Theorem FC + Lemma A1 cells + exact reach + chord rows)" % (d.get("leaf") or ""),
            "A198",
            d.get("cert") or os.path.join("attempts", "A198-fastprop", "certs", "fp198_%s.json" % nid),
            fdate(A("A198-fastprop", "results", "fastprop198.jsonl")),
            d,
            note="[C: geometry, fastprop] A171 multibox exact dead test / A161 exact miss test / A1 cells / open-chord rows; no LP",
        )

    # (7f) A189's NO-ROOM leaf on A182's recorded assignment nodes.  At a node with k boxed roles the
    #      remaining 11 - k free unit squares must fit in the container clear of every K' (A132), and
    #      A189 bounds how many can: #free <= sum over the residue pockets of A141/A161's LANE.  A node
    #      with sum < 11 - k is DEAD, and so is its whole subtree: the leaf refutes the NODE's own
    #      hypothesis from the node's fixed-point hull (a sound contraction of it), and A182's tree is a
    #      case tree, so every descendant's hypothesis IMPLIES its ancestor's.  Hence a dead label kills
    #      every label it is a prefix of -- no box monotonicity is needed for this.
    #
    #      A PAGE is retired only when its whole assignment search closes, which needs BOTH:
    #        (i) every ALIVE leaf of A182's journal (the `subtree` records whose verdict starts ALIVE,
    #            plus the UNDECIDED ones) has an A189-DEAD ancestor (label prefix), AND
    #       (ii) A182's own run of that page was EXHAUSTIVE -- `assign182.jsonl`'s last record for the
    #            page must not be a budget/deadline stop, since unexplored branches are unexamined
    #            leaves.  A page whose alive leaves all die but whose search stopped on budget is NOT
    #            retired here; it is reported as "leaves cleared, search incomplete".
    n189 = {}
    for d in jl(A("A189-noroom", "results", "noroom189.jsonl")):
        # only the A182 assignment journals carry a page whose closure this block can decide;
        # A189's A183 rows (the k0 cascade's S3 nodes) are cells, not gallery pages.
        if d.get("page") and d.get("label") and d.get("source") == "A182 journal":
            n189.setdefault(d["page"], []).append(d)
    if n189:
        last182b = {}
        for d in jl(A("A180-forced-first-assignment", "results", "assign182.jsonl")):
            if d.get("nid"):
                last182b[d["nid"]] = d
        for page in sorted(n189):
            recs = n189[page]
            deadlab = [r["label"] for r in recs if r.get("verdict") == "DEAD"]
            jpath = A("A180-forced-first-assignment", "results", "journal", page + ".jsonl")
            leaves = []
            for d in jl(jpath):
                if d.get("kind") != "subtree":
                    continue
                res = d.get("result") or {}
                v = str(res.get("verdict") or "")
                if v.startswith("ALIVE") or v == "UNDECIDED":
                    leaves.append(d.get("label") or res.get("label") or "")
            covered = [L for L in leaves
                       if any(L == dl or L.startswith(dl + "/") for dl in deadlab)]
            pd = last182b.get(page) or {}
            stop = str(pd.get("leaf") or "")
            exhaustive = bool(pd) and ("budget exhausted" not in stop) and ("deadline" not in stop) \
                and int((pd.get("summary") or {}).get("undecided") or 0) == 0
            retired = bool(leaves) and len(covered) == len(leaves) and exhaustive
            camp = "k0" if pd.get("gallery") == "k0v4" else ("A60" if str(pd.get("camp")) == "A60"
                                                             else "A57")
            note = ("A189 NO-ROOM: %d of %d recorded assignment nodes DEAD; %d of %d alive/undecided "
                    "leaves covered by a dead ancestor; A182's search of the page was %s (%s)"
                    % (len(deadlab), len(recs), len(covered), len(leaves),
                       "EXHAUSTIVE" if exhaustive else "INCOMPLETE", stop or "no assign182 record"))
            table.add_rec(
                "A189 noroom189.jsonl",
                camp,
                page,
                retired,                      # a kill row ONLY when the whole page closes
                "NO-ROOM leaf: no room for the 11 - k free squares at every alive assignment node "
                "(A189 Lemma 1; sum of pocket LANE < 11 - k)",
                "A189",
                os.path.join("attempts", "A189-noroom", "results", "noroom189.jsonl"),
                fdate(A("A189-noroom", "results", "noroom189.jsonl")),
                dict(page=page, n_dead=len(deadlab), n_nodes=len(recs), n_leaves=len(leaves),
                     n_covered=len(covered), exhaustive=exhaustive),
                note=note,
            )

    # (7h) A197's FORCED-CELL PAIR kills (docs/proofs/forced_corners.md Theorem FC + Corollaries
    #      FC-slot / FC-count, sideband.md Lemma A1).  At a forced cell two DISTINCT non-pin squares
    #      meet the widened open slot box; the non-pin squares are H and the free squares, so the case
    #      is (H-meets) H + one free, or (two-free) two free.  Both branches are split over a Lemma A1
    #      grid of side 0.70 < 1/sqrt2 (two meeter centres never share a closed cell) and every cell
    #      pair is a multibox node at nsub 8 / refine 4.  A page is DEAD when SOME forced cell has no
    #      surviving pair -- A178's (7d) pass ran the same idea at 4/2 with an UNSPLIT H-meets node and
    #      caps that declared ALIVE on exhaustion, so it retired nobody.  results/slotpair197.jsonl is
    #      resumable: the LAST row per nid is the verdict.  A row that hit a cap or the 900 s wall is
    #      ALIVE-untested and is never collected as a kill.
    last197 = {}
    for d in jl(A("A197-slot-pair-pass", "results", "slotpair197.jsonl")):
        if d.get("nid"):
            last197[d["nid"]] = d
    for nid, d in sorted(last197.items()):
        if str(d.get("verdict", "")) != "DEAD":
            continue
        camp = "k0" if d.get("gallery") == "k0v4" else ("A60" if str(d.get("camp")) == "A60" else "A57")
        table.add_rec(
            "A197 slotpair197.jsonl",
            camp,
            nid,
            True,
            "forced-cell pair test [%s]: %s" % (d.get("kill_cell") or "-", d.get("leaf") or ""),
            "A197",
            d.get("cert") or "",
            fdate(A("A197-slot-pair-pass", "results", "slotpair197.jsonl")),
            d,
            note="[C] library geometry (A171 multibox at nsub %s / refine %s, Lemma A1 grid side %s); "
                 "the frozen verifier is not involved" % (d.get("nsub"), d.get("refine"), d.get("side")),
        )

    # (7j) A199's CORNER-SEAL kills (docs/proofs/corner_seal.md: Lemma SEAL, Lemma WEDGE, Cor. SIDES; the PI's
    #      reading of Y0491, 2026-09-10 13:15).  At a pinned corner whose two neighbours along the walls are both
    #      forced (Theorem FC), a FREE meeter F of the slot ABOVE the pin that reaches around the pin's corner
    #      is rotated and seals the slot BESIDE the pin except a wedge no unit square can use; the chain is exact:
    #      F's reach (multibox dead test + A161 miss test), the (FH) miss tests, the node {pins, H, F, G} with G a
    #      further free meeter of A (EmptyBox(G)).  results/seal199.jsonl (s0, pad 0) and results/seal199_slabs.jsonl
    #      (the slab chain of corner_seal.md section 5) are resumable: the LAST row per (page, s, lam) is the verdict.
    #      A kill at s0 only is a statement about side s0 (lam = 1): it is flagged WINDOW-PENDING until every slab
    #      of [3.82, s0] is dead in the slab file.  [C: geometry, SEAL] -- no LP, no frozen verifier.
    seal_s0, seal_slab = {}, {}
    for d in jl(A("A199-corner-seal", "results", "seal199.jsonl")):
        if d.get("page") and abs(float(d.get("lam", 1)) - 1.0) < 1e-12 and abs(float(d.get("s", 0)) - 3.877084) < 1e-9:
            seal_s0[d["page"]] = d
    for d in jl(A("A199-corner-seal", "results", "seal199_slabs.jsonl")):
        if d.get("page"):
            seal_slab.setdefault(d["page"], {})[(round(float(d.get("s", 0)), 9), round(float(d.get("lam", 1)), 9))] = d
    for nid, d in sorted(seal_s0.items()):
        if str(d.get("verdict", "")) != "DEAD":
            continue
        cls = d.get("cls") or ""
        camp = "A60" if cls.startswith("trump5") else "A57"
        slabs = seal_slab.get(nid, {})
        n_slab = len(slabs)
        n_dead = sum(1 for v in slabs.values() if str(v.get("verdict", "")) == "DEAD")
        covered = n_slab > 0 and n_dead == n_slab and min(float(v["s"]) / float(v["lam"]) for v in slabs.values()) <= 3.82 + 1e-9
        k = d.get("kill") or {}
        table.add_rec(
            "A199 seal199.jsonl",
            camp,
            nid,
            True,
            "corner seal [%s: F meets %s, %s unmet] %s" % (k.get("corner", "-"), k.get("B", "-"), k.get("A", "-"),
                                                          ("(window: %d slabs DEAD)" % n_slab) if covered else
                                                          ("(s0-only; WINDOW-PENDING%s)" % (", slabs %d/%d dead" % (n_dead, n_slab) if n_slab else ""))),
            "A199",
            os.path.join("attempts", "A199-corner-seal", "results", "seal199.jsonl"),
            fdate(A("A199-corner-seal", "results", "seal199.jsonl")),
            d,
            note="[C: geometry, SEAL] A171 multibox exact dead test / A161 exact miss test; corner_seal.md section 4; "
                 + ("the slab chain covers [3.82, s0]" if covered else "s0 only (lam = 1): WINDOW-PENDING"),
        )

    # (7k) A200's COMPOSED / QUICK killer (attempts/A200-k516-quick; the PI's directive of 2026-09-10 15:10).  On top
    #      of A198's fastprop engine: per forced slot the UNION of the surviving free-meeter pieces is tested by Lemma CN
    #      (diameter < 1), Lemma A1 (l-inf < 1/sqrt2) and the open-chord row (fixed chords + 2 x min chord > s0) -- at
    #      most ONE anonymous meeter; Theorem FC then FORCES H / the instantiated roles (A161 miss test per piece) to a
    #      fixed point across all slots (A171 multibox re-normalisation), the joint count with the caps, A199's corner
    #      SEAL chain with the clipped H, the no-room leaf.  results/quick200.jsonl is resumable: the LAST row per nid is
    #      the verdict.  A kill at the WINDOW pad is valid on the page's window; a kill at PAD 0 (lam = 1) is a statement
    #      at side s0 only and is flagged WINDOW-PENDING.  [C: geometry, quick200] -- no LP, no frozen verifier.
    last200 = {}
    for d in jl(A("A200-k516-quick", "results", "quick200.jsonl")):
        if d.get("nid"):
            last200[d["nid"]] = d
    for nid, d in sorted(last200.items()):
        if str(d.get("verdict", "")) != "DEAD":
            continue
        cls = d.get("cls") or ""
        camp = "A60" if cls.startswith("trump5") else "A57"
        pend = bool(d.get("window_pending")) or str(d.get("pad", "window")) != "window"
        table.add_rec(
            "A200 quick200.jsonl",
            camp,
            nid,
            True,
            "quick killer [%s; %s pad]: %s%s" % (d.get("step_killed") or "-", d.get("pad", "window"), (d.get("leaf") or "")[:160],
                                                 " (s0-only; WINDOW-PENDING)" if pend else ""),
            "A200",
            d.get("cert") or os.path.join("attempts", "A200-k516-quick", "results", "quick200.jsonl"),
            fdate(A("A200-k516-quick", "results", "quick200.jsonl")),
            d,
            note="[C: geometry, quick200] A171 multibox exact dead test / A161 exact miss test / Lemma CN / Lemma A1 / open-chord "
                 "rows / Theorem FC; " + ("pad 0 (lam = 1): s0 only, WINDOW-PENDING" if pend else "the window pad (lambda_max): valid on the window"),
        )

    # (8) A158 -- the slot split.  NOT a kill, recorded so the PI can see why.
    for d in jl(A("A158-slot-split", "results", "yescert158.jsonl")):
        table.add_rec(
            "A158 yescert158.jsonl",
            "A57" if str(d.get("nid", "")).startswith("k5_") else "A60",
            d.get("nid", ""),
            False,  # verdict='KILL' but kill=False: 1 + LANE + M = 2
            "conditional lane leaf (YES child of the slot split)",
            "A158",
            "",
            "",
            d,
            note="verdict=%s but kill=%s (1 + LANE + M = 2); 0 of 141 cells kill "
            "the YES child" % (d.get("verdict"), d.get("kill")),
        )
    for d in jl(A("A158-slot-split", "results", "no158.jsonl")):
        table.add_rec(
            "A158 no158.jsonl",
            "A57" if str(d.get("nid", d.get("id", ""))).startswith("k5_") else "A60",
            d.get("nid") or d.get("id", ""),
            False,  # the NO child alone is not a kill: the YES child survives
            "NoFam(S) on the near-simple slot box (NO child only)",
            "A158",
            "",
            "",
            d,
            note="NO child only -- A158b: the YES child converges at tau = budget, "
            "eta = 0, so the split is not a kill (c0_Y0076 included)",
        )

    # (9) every *.clipkill.json under attempts/*/certs/**  (A148's rule) ----
    #     *__exall.json is NOT a kill record and is deliberately not scanned.
    n_clip = 0
    for path in sorted(
        glob.glob(os.path.join(ROOT, "attempts", "*", "certs", "**", "*.clipkill.json"),
                  recursive=True)
    ):
        n_clip += 1
        base = os.path.basename(path)[: -len(".clipkill.json")]
        att = os.path.basename(
            path[: path.index(os.sep + "certs" + os.sep)]
        ).split("-")[0]
        camp = "A60" if base.startswith(("c0_", "f1_", "slack")) else "A57"
        table.add_rec(
            "clipkill certs (attempts/*/certs/**)",
            camp,
            base,
            True,
            "T5''' pin-clip kill certificate (pin-clip-kill-certificate-v1)",
            att,
            rel(path),
            fdate(path),
            {},
        )
    return n_clip


# ---------------------------------------------------------------------------
# galleries
# ---------------------------------------------------------------------------

GALLERIES = [
    {
        "name": "k0v4",
        "csv": "review_k0v4.csv",
        "title": "the k0 residue gallery v4 (converged-alive k0_00 cells)",
    },
    {
        "name": "a57v4",
        "csv": "review_a57v4.csv",
        "title": "the A57 / A60 review gallery v4",
    },
]


def tree_tag_of(row):
    """The tree tag the gallery page's record was drawn from (A137 C.3)."""
    rec = (row.get("record") or "").replace("\\", "/")
    if "/results/tree/" in rec:
        return rec.split("/results/tree/", 1)[1].split("/", 1)[0]
    camp = row.get("camp") or ""
    if camp == "A60":
        return "trump5_j0"
    return "k0_00"


def load_galleries():
    out = []
    for g in GALLERIES:
        path = os.path.join(SHADOWS, g["name"], g["csv"])
        if not os.path.exists(path):
            continue
        with io.open(path, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        pages = []
        for r in rows:
            camp = r.get("camp") or "k0"
            if camp not in ("A57", "A60"):
                camp = "k0"
            pages.append(
                {
                    "file": r.get("file") or (r.get("node", "") + ".svg"),
                    "node": r.get("node", ""),
                    "camp": camp,
                    "tag": tree_tag_of(r),
                    "cls": r.get("cls", ""),
                    "level": r.get("level", ""),
                    "family": (r.get("family") or "none"),
                    "rank_a142": r.get("rank_a142", ""),
                    "cost": r.get("subtree_cost_cpuh", ""),
                    "csv_verdict": r.get("verdict", ""),
                    "csv_tau": r.get("tau", ""),
                    "csv_eta": r.get("eta", ""),
                    "csv_budget": r.get("budget", ""),
                    "killed_banner": r.get("killed_banner", ""),
                }
            )
        out.append(dict(g, pages=pages))
    return out


def decide(table, page):
    """ALIVE / DEAD for one gallery page, with the killing record."""
    camp, tag, nid = page["camp"], page["tag"], page["node"]
    aliases = k0_aliases(nid) if camp == "k0" else {nid}
    direct = table.kills_for(camp, tag, nid, aliases)
    if direct:
        # prefer a certificate-bearing row, then the earliest date
        direct.sort(key=lambda r: (0 if r["cert"] else 1, r["date"] or "9999"))
        r = direct[0]
        return "DEAD", r, "direct kill record", direct

    ancs = k0_ancestors(nid) if camp == "k0" else a57_ancestors(nid)
    for anc in ancs:
        al = k0_aliases(anc) if camp == "k0" else {anc}
        hits = table.kills_for(camp, tag, anc, al)
        if hits:
            hits.sort(key=lambda r: (0 if r["cert"] else 1, r["date"] or "9999"))
            r = dict(hits[0])
            r["leaf"] = "monotone descendant of %s -- %s" % (anc, r["leaf"])
            return "DEAD", r, "monotonicity (ancestor %s)" % anc, hits
    return "ALIVE", None, "", []


# ---------------------------------------------------------------------------
# residue-left inputs (read, never computed)
# ---------------------------------------------------------------------------


def read_paused():
    """Pull the A57 work-owing and the alive-node census out of PAUSED.md."""
    path = A("A57-shadow-trees", "PAUSED.md")
    out = {"path": rel(path), "version": "", "work_owing": None, "census": {}}
    if not os.path.exists(path):
        return out
    txt = io.open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"PAUSED\s+(v\d+)", txt)
    if m:
        out["version"] = m.group(1)
    m = re.search(r"work-owing population is\s*([\d,]+)\s*(?:->|\u2192)\s*([\d,]+)", txt)
    if m:
        out["work_owing"] = int(m.group(2).replace(",", ""))
        out["work_owing_before"] = int(m.group(1).replace(",", ""))
    m = re.search(
        r"([\d,]+)\s+alive A57/A60 records\s*\(([\d,]+)\s+distinct nodes:\s*"
        r"k5_11\s*([\d,]+),\s*k5_16\s*([\d,]+),\s*trump5\s*([\d,]+)\)",
        txt,
    )
    if m:
        out["census"] = {
            "alive_records": int(m.group(1).replace(",", "")),
            "distinct_nodes": int(m.group(2).replace(",", "")),
            "k5_11": int(m.group(3).replace(",", "")),
            "k5_16": int(m.group(4).replace(",", "")),
            "trump5": int(m.group(5).replace(",", "")),
        }
    return out


# ---------------------------------------------------------------------------
# moves
# ---------------------------------------------------------------------------


def git_mv(src, dst, dry):
    _guard(src)
    _guard(dst)
    if dry:
        return "would git mv %s -> %s" % (rel(src), rel(dst))
    d = os.path.dirname(dst)
    _guard(d)
    if not os.path.isdir(d):
        os.makedirs(d)
    p = subprocess.run(
        ["git", "mv", "--", os.path.relpath(src, ROOT), os.path.relpath(dst, ROOT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if p.returncode != 0:
        # untracked page: a plain rename, still never a delete
        os.replace(src, dst)
        return "moved (untracked) %s -> %s" % (rel(src), rel(dst))
    return "git mv %s -> %s" % (rel(src), rel(dst))


# ---------------------------------------------------------------------------
# STATUS.md
# ---------------------------------------------------------------------------


def md_escape(s):
    return str(s or "").replace("|", "\\|").replace("\n", " ")


def write_status(galleries, verdicts, table, paused, clip_n, dry):
    import datetime

    L = []
    w = L.append
    w("# Shadow-gallery STATUS -- the checklist (generated, do not hand-edit)")
    w("")
    w(
        "Generated `%s` by `docs/shadows/status_gallery.py` (A162).  Rerun it at every "
        "pause:" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    w("")
    w("```")
    w("python docs/shadows/status_gallery.py            # move DEAD pages, rewrite this file")
    w("python docs/shadows/status_gallery.py --dry-run  # print the plan, write nothing")
    w("```")
    w("")
    w(
        "**DEAD pages live in `docs/shadows/<gallery>/killed/`** -- they are `git mv`d there, "
        "never deleted.  ALIVE pages stay in place.  A page is DEAD only where a record gives a "
        "converged bound or a certificate `PASS`, at the page's **own tree tag** (A137 §C.3, "
        "\"an id is not a node\"), or where an ancestor is dead (monotonicity)."
    )
    w("")

    # ---- residue left --------------------------------------------------
    tot_alive = sum(
        1 for g in galleries for p in g["pages"] if verdicts[(g["name"], p["file"])][0] == "ALIVE"
    )
    tot_dead = sum(
        1 for g in galleries for p in g["pages"] if verdicts[(g["name"], p["file"])][0] == "DEAD"
    )
    cen = paused.get("census") or {}
    wo = paused.get("work_owing")
    w("## Residue left")
    w("")
    para = (
        "Of the %d gallery pages the PI reviews, **%d are still ALIVE and %d are now DEAD**. "
        % (tot_alive + tot_dead, tot_alive, tot_dead)
    )
    for g in galleries:
        a = sum(1 for p in g["pages"] if verdicts[(g["name"], p["file"])][0] == "ALIVE")
        d = sum(1 for p in g["pages"] if verdicts[(g["name"], p["file"])][0] == "DEAD")
        para += "`%s` is %d alive / %d dead; " % (g["name"], a, d)
    if wo:
        para += (
            "behind them the A57 tree still owes work on **%d nodes** (%s §B, %s: %d -> %d after "
            "the fold-in and the exact-core re-emission)"
            % (
                wo,
                paused["path"],
                paused.get("version") or "latest",
                paused.get("work_owing_before", 0),
                wo,
            )
        )
    if cen:
        para += (
            ", out of %s alive A57/A60 records -- %s distinct nodes, k5_11 %s, k5_16 %s, "
            "trump5 (A60) %s -- and the k0 lane holds its %d converged-alive `k0_00` cells"
            % (
                "{:,}".format(cen["alive_records"]),
                "{:,}".format(cen["distinct_nodes"]),
                "{:,}".format(cen["k5_11"]),
                "{:,}".format(cen["k5_16"]),
                "{:,}".format(cen["trump5"]),
                sum(1 for g in galleries if g["name"] == "k0v4" for _ in g["pages"]),
            )
        )
    para += (
        ".  So the galleries are a **%.1f %% sample of the live A57/A60 board** and the whole of "
        "the k0 residue: the pages are where the residue is *looked at*, not where it is *counted* "
        "-- the count is the work-owing number above.  Nothing in either gallery is dead by an "
        "unconverged LP: every DEAD page below carries a certificate."
        % (
            100.0
            * (tot_alive + tot_dead - sum(1 for g in galleries if g["name"] == "k0v4" for _ in g["pages"]))
            / max(1, cen.get("distinct_nodes", 1))
        )
    )
    w(para)
    w("")

    # ---- counts --------------------------------------------------------
    w("## Counts")
    w("")
    w("### Per gallery")
    w("")
    w("| gallery | pages | ALIVE | DEAD |")
    w("|---|---|---|---|")
    for g in galleries:
        a = sum(1 for p in g["pages"] if verdicts[(g["name"], p["file"])][0] == "ALIVE")
        d = sum(1 for p in g["pages"] if verdicts[(g["name"], p["file"])][0] == "DEAD")
        w("| `%s` | %d | %d | %d |" % (g["name"], len(g["pages"]), a, d))
    w("| **total** | **%d** | **%d** | **%d** |" % (tot_alive + tot_dead, tot_alive, tot_dead))
    w("")

    fam = collections.defaultdict(lambda: [0, 0])
    leaf = collections.defaultdict(int)
    for g in galleries:
        for p in g["pages"]:
            st, rec, _, _ = verdicts[(g["name"], p["file"])]
            fam[p["family"]][0 if st == "ALIVE" else 1] += 1
            if st == "DEAD":
                leaf["%s -- %s" % (rec["attempt"], rec["leaf"])] += 1
    w("### By family (A107/A128 shadow family of the page's panel N)")
    w("")
    w("| family | ALIVE | DEAD |")
    w("|---|---|---|")
    for k in sorted(fam, key=lambda x: (x == "none", x)):
        w("| `%s` | %d | %d |" % (k, fam[k][0], fam[k][1]))
    w("")
    w("### By killing leaf")
    w("")
    if leaf:
        w("| attempt -- leaf | pages killed |")
        w("|---|---|")
        for k, n in sorted(leaf.items(), key=lambda kv: (-kv[1], kv[0])):
            w("| %s | %d |" % (md_escape(k), n))
    else:
        w("No gallery page is killed by any recorded leaf.")
    w("")

    # ---- checklists ----------------------------------------------------
    for g in galleries:
        w("## Checklist -- `%s`: %s" % (g["name"], g["title"]))
        w("")
        w(
            "| page | node | class | level | family | status | leaf | attempt | date | "
            "subtree cost (CPU-h, A142 rank) |"
        )
        w("|---|---|---|---|---|---|---|---|---|---|")
        for p in sorted(
            g["pages"], key=lambda q: (verdicts[(g["name"], q["file"])][0] != "DEAD", q["node"])
        ):
            st, rec, how, _ = verdicts[(g["name"], p["file"])]
            here = "killed/" + p["file"] if st == "DEAD" else p["file"]
            box = "[x]" if st == "DEAD" else "[ ]"
            w(
                "| %s [`%s`](%s) | `%s` | `%s` | %s | `%s` | **%s** | %s | %s | %s | %s%s |"
                % (
                    box,
                    p["file"],
                    here,
                    p["node"],
                    p["cls"],
                    p["level"],
                    p["family"],
                    st,
                    md_escape(rec["leaf"]) if rec else "--",
                    rec["attempt"] if rec else "--",
                    rec["date"] if rec else "--",
                    p["cost"] or "--",
                    (" (rank %s)" % p["rank_a142"]) if p["rank_a142"] else "",
                )
            )
        w("")
        deads = [
            (p, verdicts[(g["name"], p["file"])])
            for p in g["pages"]
            if verdicts[(g["name"], p["file"])][0] == "DEAD"
        ]
        if deads:
            w("**The kills, with their certificates.**")
            w("")
            for p, (st, rec, how, allrecs) in deads:
                other = ""
                if p["camp"] == "A57":
                    live = sorted(
                        t
                        for t in table.tags_of.get(p["node"], ())
                        if t != p["tag"]
                        and not table.kills_for("A57", t, p["node"], {p["node"]})
                    )
                    if live:
                        other = (
                            "  **An id is not a node (A137 §C.3): the %s node of this id is still "
                            "ALIVE** -- only the `%s` node is dead, and this page was drawn from "
                            "the `%s` record."
                            % (", ".join("`%s`" % x for x in live), p["tag"], p["tag"])
                        )
                w(
                    "* `%s` (tree tag `%s`) -- %s, **%s** by `%s`; certificate `%s`; "
                    "attributed by *%s*; %d record(s) agree.%s"
                    % (
                        p["node"],
                        p["tag"],
                        how,
                        rec["attempt"],
                        md_escape(rec["leaf"]),
                        md_escape(rec["cert"]) or "(none recorded)",
                        md_escape(rec["how"]) or "single-tree camp",
                        len(allrecs) or 1,
                        other,
                    )
                )
            w("")

        # gallery-CSV consistency: a page whose own review row already showed
        # tau < budget but is labelled ALIVE.  Not a verdict -- a flag.
        odd = []
        for p in g["pages"]:
            try:
                eta = float(p["csv_eta"])
            except (TypeError, ValueError):
                continue
            # -1e-6, not -0: eta of order 1e-9 is LP round-off on a knife-edge
            # node, not a bound below the budget.
            if eta < -1e-6 and "ALIVE" in (p["csv_verdict"] or ""):
                odd.append(p)
        if odd:
            w(
                "**Review-sheet flag.** %d page(s) in `%s` carry `eta < 0` (that is "
                "`tau < budget`, a kill) while the review sheet's `verdict` column says "
                "`ALIVE-at-LP`: %s.  The `verdict` column is stale for these; the status above is "
                "taken from the campaign records, not from that column."
                % (
                    len(odd),
                    g["csv"],
                    ", ".join(
                        "`%s` (tau %s, budget %s, eta %s, now **%s**)"
                        % (
                            q["node"],
                            q["csv_tau"],
                            q["csv_budget"],
                            q["csv_eta"],
                            verdicts[(g["name"], q["file"])][0],
                        )
                        for q in odd
                    ),
                )
            )
            w("")

    # ---- provenance ----------------------------------------------------
    w("## Where the verdicts came from")
    w("")
    w("| source | records read | of which kills |")
    w("|---|---|---|")
    for src, v in sorted(table.by_source.items()):
        w("| `%s` | %d | %d |" % (md_escape(src), v["rows"], v["kills"]))
    w("")
    w(
        "`*__exall.json` is **not** a kill record (A148's rule: it exists on LOST-KILL / "
        "TOO-TIGHT / FAIL too) and is not scanned.  A158's `yescert158.jsonl` rows say "
        "`verdict = \"KILL\"` with `kill = false` and are counted as **not** kills; in particular "
        "**`c0_Y0076`'s NO child is NOT a kill** (A158b: the YES child converges at "
        "`tau = budget`, `eta = 0`).  A140's `exactcore140.jsonl` kills only where "
        "`kills_converged` and the certificate `PASS` -- `l1_148`, `l2_p65_101` and `l2_p65_111` "
        "have `kills = true` with `converged = false` and are **not** kills (A124: a "
        "non-converged `tau` was never a bound)."
    )
    w("")
    if table.refused:
        applied = {}
        for r in table.rows:
            if r["dead"] and r["tags"]:
                applied.setdefault(r["id"], set()).update(r["tags"])
        unattributed = [r for r in table.refused if r["id"] not in applied]
        w("### Records REFUSED -- tree tag unresolved (A137 §C.3)")
        w("")
        w(
            "%d record(s) name an id that exists in more than one tree and carry neither an "
            "`applies_to_tags` field nor a prior `tau` to match, so the tree they belong to cannot "
            "be read off them.  **%d of them are redundant** -- the same id is killed with an "
            "explicit tag by another record -- and **%d leave a node unattributed**.  A refusal "
            "never kills a page: the certificate is correct for the node it names, but this script "
            "will not guess which tree that is."
            % (len(table.refused), len(table.refused) - len(unattributed), len(unattributed))
        )
        w("")
        w("| source | id | leaf | why refused | redundant? |")
        w("|---|---|---|---|---|")
        for r in table.refused[:300]:
            w(
                "| `%s` | `%s` | %s | %s | %s |"
                % (
                    md_escape(r["source"]),
                    r["id"],
                    md_escape(r["leaf"]),
                    md_escape(r["why"]),
                    "yes -- also killed at `%s`" % ", ".join(sorted(applied[r["id"]]))
                    if r["id"] in applied
                    else "**no -- unattributed**",
                )
            )
        w("")
    else:
        w("No kill record was refused: every one resolved to a tree tag.")
        w("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# README notes
# ---------------------------------------------------------------------------

README_HEADER = "## Status: killed pages and the checklist"

README_NOTE = (
    README_HEADER
    + """

*Maintained by `docs/shadows/status_gallery.py` (A162) — this section is regenerated, do not
hand-edit it.*

* **`../STATUS.md` is the checklist** — page, node, class, level, family, status, killing leaf,
  attempt, date and A142 subtree cost for every page of every gallery, with the alive/dead counts
  per gallery, by family and by leaf, and the "residue left" paragraph. **Read it first.**
* **A page whose node is now DEAD lives in [`killed/`](killed/)**, moved there with `git mv` —
  never deleted. A page still in this directory is ALIVE as of the last run, and the links in the
  tables above are repointed to `killed/` when a page moves.
* **The tables above are the frozen A148 build-time state.** Where they disagree with `STATUS.md`
  — including the "no node in this set is killed" lines, which are statements about the *drawing*,
  not about the campaign records — **`STATUS.md` wins.**
* Regenerate with `python docs/shadows/status_gallery.py` (`--dry-run` prints the plan and writes
  nothing). It solves no LP; it only reads existing kill records, and it writes nothing outside
  `docs/shadows/`.
"""
)


def ensure_readme_note(path, dry, pages=None):
    """Append the status note (once) and keep the README's page links pointing at
    wherever the page now lives.  Both halves are idempotent."""
    _guard(path)
    if not os.path.exists(path):
        return "no README at %s" % rel(path)
    txt = io.open(path, encoding="utf-8", errors="replace").read()
    orig = txt
    notes = []
    if README_HEADER in txt:
        head = txt[: txt.index(README_HEADER)].rstrip("\n")
        if txt[txt.index(README_HEADER) :] != README_NOTE:
            txt = head + "\n\n" + README_NOTE
            notes.append("status note refreshed")
    else:
        txt = txt.rstrip("\n") + "\n\n" + README_NOTE
        notes.append("status note appended")
    n_links = 0
    for fname, st in (pages or {}).items():
        live, dead = "](%s)" % fname, "](killed/%s)" % fname
        if st == "DEAD" and live in txt:
            txt = txt.replace(live, dead)
            n_links += 1
        elif st == "ALIVE" and dead in txt:
            txt = txt.replace(dead, live)
            n_links += 1
    if n_links:
        notes.append("%d page link(s) repointed" % n_links)
    if txt == orig:
        return "README already current: %s" % rel(path)
    if dry:
        return "would update %s (%s)" % (rel(path), ", ".join(notes))
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(txt)
    return "updated %s (%s)" % (rel(path), ", ".join(notes))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="collect and print; move nothing and write nothing",
    )
    ap.add_argument(
        "--json",
        metavar="PATH",
        default=None,
        help="also dump the machine-readable table here (any path; the only "
        "option that may write outside docs/shadows/, and only if you pass it)",
    )
    args = ap.parse_args(argv)
    dry = args.dry_run

    print("status_gallery.py -- repo %s" % ROOT)
    corpus, tags_of = load_a57_corpus()
    print(
        "A57 tree corpus: %d (tag, id) records over %d distinct ids, %d ids in more "
        "than one tree" % (
            len(corpus),
            len(tags_of),
            sum(1 for k, v in tags_of.items() if len(v) > 1),
        )
    )

    table = Table(corpus, tags_of)
    clip_n = collect(table, corpus)
    n_kill = sum(1 for r in table.rows if r["dead"])
    print(
        "kill table: %d records scanned, %d kills, %d refused for an unresolved tree tag, "
        "%d clipkill certificates" % (len(table.rows), n_kill, len(table.refused), clip_n)
    )

    galleries = load_galleries()
    verdicts = {}
    for g in galleries:
        for p in g["pages"]:
            verdicts[(g["name"], p["file"])] = decide(table, p)

    # ---- moves ---------------------------------------------------------
    actions = []
    for g in galleries:
        gdir = os.path.join(SHADOWS, g["name"])
        kdir = os.path.join(gdir, "killed")
        for p in g["pages"]:
            st = verdicts[(g["name"], p["file"])][0]
            live = os.path.join(gdir, p["file"])
            dead = os.path.join(kdir, p["file"])
            if st == "DEAD":
                if os.path.exists(dead) and not os.path.exists(live):
                    actions.append("already in killed/: %s/%s" % (g["name"], p["file"]))
                elif os.path.exists(live):
                    actions.append(git_mv(live, dead, dry))
                else:
                    actions.append("MISSING page (neither place): %s/%s" % (g["name"], p["file"]))
            else:
                if os.path.exists(dead) and not os.path.exists(live):
                    # a page that came back alive: bring it out of killed/
                    actions.append(git_mv(dead, live, dry))
    for a in actions:
        print("  " + a)

    # ---- STATUS.md -----------------------------------------------------
    paused = read_paused()
    md = write_status(galleries, verdicts, table, paused, clip_n, dry)
    status = os.path.join(SHADOWS, "STATUS.md")
    _guard(status)
    if dry:
        print("  would write %s (%d bytes)" % (rel(status), len(md.encode("utf-8"))))
    else:
        with io.open(status, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(md)
        print("  wrote %s (%d bytes)" % (rel(status), len(md.encode("utf-8"))))

    for g in galleries:
        pmap = {p["file"]: verdicts[(g["name"], p["file"])][0] for p in g["pages"]}
        print(
            "  "
            + ensure_readme_note(
                os.path.join(SHADOWS, g["name"], "README.md"), dry, pmap
            )
        )

    # ---- optional machine dump ----------------------------------------
    if args.json and not dry:
        dump = {
            "generated": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
            "paused": paused,
            "kill_table": table.rows,
            "refused": table.refused,
            "by_source": table.by_source,
            "clipkill_certs": clip_n,
            "galleries": [
                {
                    "name": g["name"],
                    "pages": [
                        dict(
                            p,
                            status=verdicts[(g["name"], p["file"])][0],
                            killed_by=verdicts[(g["name"], p["file"])][1],
                            how=verdicts[(g["name"], p["file"])][2],
                        )
                        for p in g["pages"]
                    ],
                }
                for g in galleries
            ],
        }
        d = os.path.dirname(os.path.abspath(args.json))
        if d and not os.path.isdir(d):
            os.makedirs(d)
        with io.open(args.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(dump, fh, indent=1, sort_keys=True, default=str)
        print("  wrote %s" % args.json)

    # ---- summary -------------------------------------------------------
    print("")
    for g in galleries:
        a = sum(1 for p in g["pages"] if verdicts[(g["name"], p["file"])][0] == "ALIVE")
        d = sum(1 for p in g["pages"] if verdicts[(g["name"], p["file"])][0] == "DEAD")
        print("%-8s %3d pages   ALIVE %3d   DEAD %3d" % (g["name"], len(g["pages"]), a, d))
        for p in g["pages"]:
            st, rec, how, _ = verdicts[(g["name"], p["file"])]
            if st == "DEAD":
                print(
                    "         DEAD %-28s tag %-22s %s / %s"
                    % (p["node"], p["tag"], rec["attempt"], rec["leaf"][:60])
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
