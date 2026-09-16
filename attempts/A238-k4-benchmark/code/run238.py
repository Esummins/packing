"""A238 driver -- the k5 TOOLKIT on one node of a PROTECTED CLASS's tree (a Trump-parent k <= 4 class), PAD 0 ONLY:

    python run238.py page <nid> [--wall 300] [--depth 6] [--nodes 600] [--force] [--no-fig]

  nid = "<cls>_root"          the A84-P1 node (H = the whole interior zone [1.1, s0 - 1.1]^2 x [0, 90));
        "<cls>_c0_Y<i>"       cover cell i of A100's level-1 census of the class (the SAME boxes A100 priced by LP).

Stage 0 (A203's Stage0 + CSP, cached in THIS attempt's certs/), then Tree238 (= A212's gate + tube leaf + aligned
split with the CLASS tube direction, on A211's coarse tree with the pass flag set + Rule SNAP at gated leaves).
One certificate per node certs/k4bench238_<nid>.json, one row per run in results/bench238.jsonl, the page
docs/residue_map/campaigns/A238-k4-benchmark/k4bench238_<nid>.svg.

WHAT THE CERTIFICATE CERTIFIES (carried verbatim on the doc as `hypothesis`, and in the verifier clause):
the page's hypothesis is M_S(m) & YES(H) of load238.py -- an 11-square packing in [0, m]^2 with an axis-aligned unit
square centred at every slot of class S, some non-pin square of its s0-dilate in H.  A DEAD verdict is an instance of
`stratum_kill` for THIS class S restricted to H (Lemma K1 / Lemma P-TREE (c), obligation O1 of
docs/proofs/protected_trees.md s.5), and nothing else; a TRUMP-TUBE leaf is Lemma TUBE-LEAF/S (tube238.py), a (D)
discharge in the slot(I_g) direction; a SNAP HAND-OFF moves the branch to the k+1 stratum's queue (trump5 when the
snapped slot is Trump's fifth simple square, else a closed k5 class -- DEAD by Lemma K1, recorded by A224's rule).

A211 / A212 / A224 / A100 / A84 are imported READ-ONLY and never written: this driver rebinds `tree212.Tree212` to
Tree238, `tree212.TR` to tube238, `stage209.CERTS` and the result / certificate paths to this attempt's own dirs."""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A238 = os.path.abspath(os.path.join(HERE, ".."))
CERTS = os.path.join(A238, "certs")
RES = os.path.join(A238, "results", "bench238.jsonl")
PAGES = os.path.join(ROOT, "docs", "residue_map", "campaigns", "A238-k4-benchmark")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "attempts", "A212-trump5-tree", "code"))
import load238                                                  # noqa: E402
load238.install()
import stage209                                                 # noqa: E402
import rows212 as RW                                            # noqa: E402
import tree212 as N12                                           # noqa: E402
import tube238 as TU                                            # noqa: E402
import tree238 as T238                                          # noqa: E402
import run212                                                   # noqa: E402

load238.install()                                               # stage209 re-installs load211 at import: re-install ours
stage209.CERTS = CERTS                                          # never write A211's cert dir
N12.Tree212 = T238.Tree238                                      # run212 builds Tree238 (a subclass; base bound already)
run212.TR = TU
FLAGS = dict(A220_NOROOM_INHERIT=os.environ.get("A220_NOROOM_INHERIT"), A221_LANE=os.environ.get("A221_LANE"),
             A224_SNAP=os.environ.get("A224_SNAP"), A230_EPS=os.environ.get("A230_EPS"),
             A238_SNAP_AT_GATE=os.environ.get("A238_SNAP_AT_GATE", "1"), A238_DELTA_PIN=load238.DELTA_PIN)
A238_CLAUSE = (
    "  [A238: this page is a node of the PROTECTED CLASS %s's tree at s0 (attempts/A238-k4-benchmark/code/load238.py). "
    "The hypothesis is M_S(m) & YES(H): an 11-square packing in [0, m]^2 with an axis-aligned unit square centred at "
    "every slot of %s (slack pin cores, delta_pin = %s) and some non-pin square of its s0-dilate in H = %s.  DEAD is "
    "the instance of `stratum_kill` for %s restricted to H (Lemma K1 / Lemma P-TREE (c), obligation O1, "
    "docs/proofs/protected_trees.md); TRUMP-TUBE is Lemma TUBE-LEAF/S in the class direction slot(I_g) "
    "(attempts/A238-k4-benchmark/code/tube238.py + Theorem T1 on %s); a SNAP HAND-OFF is A224's Rule SNAP into the "
    "k+1 stratum (docs/proofs/snap_rule.md).  Flag set %s.]")


def clause(rec, cls):
    try:
        cert = TU.radii(image_I(cls))["cert"]
    except Exception:                                             # noqa: BLE001
        cert = "certs/tube_I_*_landing_*.json (per image)"
    return RW.VERIFIER + A238_CLAUSE % (cls, cls, rec.get("delta_pin"), [round(v, 6) for v in rec["H"][0]], cls, cert, json.dumps(FLAGS))


def image_I(cls):
    """the class's distinct Trump-frame pin sets (A84's tier table); the first is used for the cfg / clause."""
    f = os.path.join(ROOT, "attempts", "A84-protected-trees", "results", "tier84_classes.json")
    d = json.load(open(f, encoding="utf-8")).get(cls) or {}
    sets = d.get("distinct_trump_frame_pin_sets") or [[]]
    return sets[0]


def main():
    run212.belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("page",))
    ap.add_argument("nid")
    ap.add_argument("--pads", default="zero")
    ap.add_argument("--wall", type=float, default=300)
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--depth", type=int, default=6)
    ap.add_argument("--nodes", type=int, default=600)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-inherit", dest="no_inherit", action="store_true", default=True)
    ap.add_argument("--cert-dir", dest="cert_dir", default=CERTS)
    ap.add_argument("--results", default=RES)
    ap.add_argument("--no-fig", dest="no_fig", action="store_true")
    a = ap.parse_args()
    run212.RES = os.path.join(A238, "results", "rows212_raw.jsonl")   # A212's slim row; the canonical
    # benchmark row (with the SNAP / EPS counters) is bench_row's, written to --results below
    RW.NOFIG[0] = bool(a.no_fig)
    rec, cls, row = load238.FP.load_page(a.nid)
    TU.CLS[0] = cls
    TU.IG[0] = image_I(cls)
    RW.VERIFIER = clause(rec, cls)
    RW.CERTS = os.path.abspath(a.cert_dir)
    cert = os.path.join(os.path.abspath(a.cert_dir), "k4bench238_%s.json" % a.nid)
    doc = dict(nid=a.nid, runs={})
    if os.path.exists(cert) and not a.force:
        try:
            doc = json.load(open(cert, encoding="utf-8"))
            doc.setdefault("runs", {})
        except Exception:                                         # noqa: BLE001
            doc = dict(nid=a.nid, runs={})
    doc.update(camp="A238", cls=cls, hypothesis=rec["hypothesis"], h_meta=rec.get("h_meta"), delta_pin=rec.get("delta_pin"),
               budget=rec.get("budget"), flags=FLAGS, a100_baseline=a100_row(cls), tube_direction=TU.radii(image_I(cls)),
               statement=("A238 certificate for the STRATUM %s: every verdict here is a statement about packings "
                          "satisfying M_%s (Lemma P-TREE s.1), not about any other class." % (cls, cls)))
    t0 = time.time()
    run212.run_page(doc, a, cert)
    doc["seconds_total"] = round(time.time() - t0, 1)
    RW.save(doc, cert)
    bench_row(doc, a, cert, cls, rec)
    print("== A238 %s [%s]: %s in %.1f s" % (a.nid, cls, doc.get("verdicts"), doc["seconds_total"]), flush=True)


def a100_cell(cls, nid):
    """A100's own LP verdict and wall on the SAME cover cell (the head-to-head baseline)."""
    if "_c0_Y" not in nid:
        return None
    i = int(nid.rsplit("_c0_Y", 1)[1])
    f = os.path.join(ROOT, "attempts", "A100-protected-pilot", "results", "a84_%s_cover_j0.jsonl" % cls)
    if not os.path.exists(f):
        return None
    for ln in open(f, encoding="utf-8", errors="replace"):
        try:
            r = json.loads(ln)
        except Exception:                                         # noqa: BLE001
            continue
        if r.get("tag") == "c0_Y%04d" % i:
            return dict(tag=r["tag"], verdict=r.get("verdict"), lp_s=r.get("lp_s"), cert_s=r.get("cert_s"),
                        tau=r.get("tau"), eta=r.get("eta"), budget=r.get("budget"))
    return None


def bench_row(doc, a, cert, cls, rec):
    """ONE canonical benchmark row per node -- everything the report needs, including the SNAP / EPS counters that
    rows212's slim row does not carry."""
    d = (doc.get("runs") or {}).get("zero_page") or {}
    # run212's aggregator carries A212's key list only, so the A224 / A230 counters are read off the node records
    nodes = d.get("nodes") or []
    snaps = [dict(n.get("snap") or {}, label=n.get("label")) for n in nodes if n.get("snap")]
    epss = [n.get("eps") for n in nodes if n.get("eps")]
    S = dict(runs=len(snaps), kills=sum(1 for s in snaps if s.get("verdict") == "DEAD"),
             handoffs=sum(1 for s in snaps if s.get("verdict") == "HANDOFF"),
             cands=sum(s.get("n_cands") or 0 for s in snaps),
             seconds=round(sum(s.get("seconds") or 0.0 for s in snaps), 2),
             gated=sum(1 for s in snaps if s.get("where") == "gated-leaf"))
    E = dict(runs=len(epss), kills=sum(1 for e in epss if e.get("verdict") == "DEAD"),
             seconds=round(sum(e.get("seconds") or 0.0 for e in epss), 2))
    row = dict(nid=doc["nid"], cls=cls, camp="A238", kind=rec.get("kind"), index=rec.get("index"),
               h=[round(v, 6) for v in rec["H"][0]], state=(rec.get("h_meta") or {}).get("state"),
               ghost=(rec.get("h_meta") or {}).get("ghost"), budget=rec.get("budget"), delta_pin=rec.get("delta_pin"),
               verdict=d.get("verdict") or (doc.get("verdicts") or {}).get("zero"), leaf=str(d.get("leaf") or "")[:400],
               seconds=d.get("seconds"), seconds_total=doc.get("seconds_total"), wall=d.get("wall"),
               n_nodes=d.get("n_nodes"), max_depth=d.get("max_depth"), dead_leaves=d.get("dead_leaves"),
               alive_leaves=d.get("alive_leaves"), kills_by_rule=d.get("kills_by_rule"),
               gate_hits=d.get("gate_hits"), gate_conflicts=d.get("gate_conflicts"), gate_root=d.get("gate_root"),
               tube_leaves=d.get("tube_leaves"), tube_depths=d.get("tube_depths"), tube_nodes=d.get("tube_nodes"),
               aligned_cuts=d.get("aligned_cuts"), gated_snaps=S["gated"],
               snap=dict(S, targets=[dict(label=s.get("label"), verdict=s.get("verdict"), kind=s.get("kind"),
                                          where=s.get("where"), target=(s.get("target") or {}).get("stratum"),
                                          full=(s.get("target") or {}).get("full"),
                                          snapped=[dict(role=c.get("role"), slot=c.get("slot")) for c in (s.get("snapped") or [])])
                                     for s in snaps if s.get("verdict") in ("DEAD", "HANDOFF")][-12:]),
               eps=E,
               ns_splits=d.get("ns_splits"), pocket_splits=d.get("pocket_splits"), rsplits=d.get("rsplits"),
               stage0=dict((doc.get("stage0") or {}).get("zero") or {}, csp=None) if doc.get("stage0") else None,
               a100=a100_cell(cls, doc["nid"]), flags=FLAGS, hypothesis=doc.get("hypothesis"),
               tube_direction=(doc.get("tube_direction") or {}).get("cert"),
               cert=os.path.relpath(cert, ROOT).replace("\\", "/"), when=time.strftime("%Y-%m-%d %H:%M:%S"))
    res = os.path.abspath(a.results)
    os.makedirs(os.path.dirname(res), exist_ok=True)
    with open(res, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, default=str) + "\n")
    return row


def a100_row(cls):
    """A100's measured per-class numbers, for the certificate to carry its own baseline."""
    f = os.path.join(ROOT, "attempts", "A100-protected-pilot", "results", "a100_projection.json")
    if not os.path.exists(f):
        return None
    d = json.load(open(f, encoding="utf-8"))["per_class"].get(cls)
    if not d:
        return None
    return {k: d[k] for k in ("cells", "budget", "sample", "w_node_asrun_s", "w_node_eta_gated_s", "f1_first_pass",
                              "level1_cpu_h", "total_measured_cpu_h", "D_leaves") if k in d}


if __name__ == "__main__":
    main()
