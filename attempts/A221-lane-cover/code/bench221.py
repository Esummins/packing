"""A221 -- the standalone benchmark: replay recorded no-room nodes through noroom221 and report verdict + seconds
against what A189 recorded.  Read-only on every certificate; runs no tree.

  python bench221.py --cert <path> [--run zero_page] [--verdict UNDECIDED|DEAD|any] [--label L]... [--inherit]
                     [--cap 120] [--pk-deadline 45] [--out results/bench221.jsonl] [--tag four]

`--inherit` runs `noroom221.noroom_child` on the nearest recorded ANCESTOR's pocket list (Lemma POCKET-INHERIT);
without it the node runs the full A221 leaf (global bisection, then the pocket cover).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import nodeload221 as NL                                                     # noqa: E402
import noroom221 as N221                                                     # noqa: E402
import noroom189 as NR189                                                    # noqa: E402  READ-ONLY (A189), the control


def one(node, args, inherited):
    t = time.time()
    bud = dict(total_deadline=args.cap, pk_deadline=args.pk_deadline, pk_depth=args.pk_depth,
               pk_tsub=args.pk_tsub, pk_max_pieces=args.pk_max_pieces, pk_max_open=args.pk_max_open,
               pk_deadline_inherit=args.pk_deadline_inherit)
    try:
        if args.engine == "a189":
            # the CONTROL: A189's own leaf on exactly the boxes this replay loaded, so that a verdict A221 reaches
            # and the certificate did not can be attributed to the COVER rather than to tighter replayed boxes.
            r = NR189.noroom(node["roles"], budget=dict(total_deadline=args.cap), name=node["label"][-30:], n=args.n)
            r["step"] = "a189-control"
        elif inherited:
            r = N221.noroom_child(node["roles"], inherited, budget=bud, name=node["label"][-30:], n=args.n)
        else:
            r = N221.noroom(node["roles"], budget=bud, name=node["label"][-30:], n=args.n)
    except Exception as e:                                                   # noqa: BLE001
        r = dict(verdict="ERROR", reason=repr(e)[:240], seconds=round(time.time() - t, 1), step="error")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cert", action="append", required=True)
    ap.add_argument("--run", action="append", default=[])
    ap.add_argument("--label", action="append", default=[])
    ap.add_argument("--verdict", default="UNDECIDED")
    ap.add_argument("--inherit", action="store_true")
    ap.add_argument("--n", type=int, default=11)
    ap.add_argument("--cap", type=float, default=120.0)
    ap.add_argument("--pk-deadline", type=float, default=45.0)
    ap.add_argument("--pk-depth", type=int, default=N221.DEFAULTS["pk_depth"])
    ap.add_argument("--pk-tsub", type=int, default=N221.DEFAULTS["pk_tsub"])
    ap.add_argument("--pk-max-pieces", type=int, default=N221.DEFAULTS["pk_max_pieces"])
    ap.add_argument("--pk-max-open", type=int, default=N221.DEFAULTS["pk_max_open"])
    ap.add_argument("--pk-deadline-inherit", type=float, default=N221.DEFAULTS["pk_deadline_inherit"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tag", default="bench")
    ap.add_argument("--engine", choices=["a221", "a189"], default="a221")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "bench221.jsonl"))
    args = ap.parse_args()

    print("A213/A214 kernels installed:", N221.install_kernels(), flush=True)
    vs = None if args.verdict.lower() == "any" else (args.verdict,)
    todo, pool = [], []
    for c in args.cert:
        p = c if os.path.isabs(c) else os.path.join(ROOT, c)
        allv = NL.noroom_nodes(p, verdicts=None, runs=args.run or None)
        pool += allv
        todo += [x for x in allv
                 if (vs is None or x["rec"]["verdict"] in vs)
                 and (not args.label or x["label"] in set(args.label))]
    if args.limit:
        todo = todo[:args.limit]
    print("%d node(s) to replay (%d recorded no-room nodes in the certificates)" % (len(todo), len(pool)), flush=True)
    agree = dis = 0
    with open(args.out, "a") as f:
        for i, nd_ in enumerate(todo):
            anc, pk = (NL.parent_pockets(pool, nd_) if args.inherit else (None, None))
            r = one(nd_, args, pk)
            row = dict(tag=args.tag, page=nd_["page"], run=nd_["run"], node=nd_["label"], k=nd_["rec"]["k"],
                       m=nd_["rec"]["m"], recorded=nd_["rec"]["verdict"], recorded_seconds=nd_["rec"]["seconds"],
                       recorded_clip=("NOROOM-CN" if nd_["rec"]["cn_bound"] else None),
                       a221=r.get("verdict"), a221_clip=r.get("clip"), a221_seconds=r.get("seconds"),
                       step=r.get("step"), inherited_from=anc, n_inherited=(len(pk) if pk else 0),
                       t_build=r.get("t_build"), t_bisect=r.get("t_bisect"), n_pockets=len(r.get("pockets") or []),
                       n_alive=len(r.get("alive") or []), reason=str(r.get("reason"))[:200],
                       pockets=r.get("pockets"), alive=r.get("alive"),
                       pocket_seconds=[q.get("seconds") for q in (r.get("pocket_recs") or [])],
                       pocket_dead=[q.get("dead") for q in (r.get("pocket_recs") or [])],
                       pocket_stop=[(q.get("cert") or {}).get("stop") for q in (r.get("pocket_recs") or [])],
                       pocket_depth=[(q.get("cert") or {}).get("depth") for q in (r.get("pocket_recs") or [])],
                       pocket_nopen=[(q.get("cert") or {}).get("n_open") for q in (r.get("pocket_recs") or [])],
                       pocket_dropped=[(q.get("cert") or {}).get("dropped_fraction") for q in (r.get("pocket_recs") or [])],
                       pocket_openvol=[(q.get("cert") or {}).get("open_volume") for q in (r.get("pocket_recs") or [])],
                       pocket_rootvol=[(q.get("cert") or {}).get("root_volume") for q in (r.get("pocket_recs") or [])],
                       when=time.strftime("%Y-%m-%d %H:%M:%S"))
            ok = not (nd_["rec"]["verdict"] == "DEAD" and r.get("verdict") != "DEAD")
            row["regression"] = not ok
            agree += bool(ok)
            dis += bool(not ok)
            f.write(json.dumps(row) + "\n")
            f.flush()
            print("[%d/%d] %s %s %-22s k=%s  A189 %-9s %6ss  ->  A221 %-9s %6ss  %s%s"
                  % (i + 1, len(todo), nd_["page"][-28:], nd_["run"][:4], nd_["label"][-22:], row["k"],
                     row["recorded"], row["recorded_seconds"], row["a221"], row["a221_seconds"],
                     row["step"], "  *** REGRESSION" if not ok else ""), flush=True)
    print("\n%d node(s): %d no regression, %d REGRESSION (a recorded DEAD that A221 does not kill)"
          % (len(todo), agree, dis), flush=True)


if __name__ == "__main__":
    main()
