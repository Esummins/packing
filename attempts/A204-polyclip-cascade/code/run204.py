"""A204 driver: per page, the polygon-clip cascade to a fixed point at the g1 pad (the page's window), then -- if ALIVE --
at pad 0 (s0-only, WINDOW-PENDING); wall 900 s per pad; the page docs/residue_map/campaigns/A204-polyclip/
polyclip204_<nid>.svg redrawn after EVERY round; certificate certs/polyclip204_<nid>.json (every round's snapshot, every
exact test); one slim row per (nid, pad) in results/polyclip204.jsonl.       python run204.py <nid> [--wall 900] [--pads g1,zero]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
RES = os.path.abspath(os.path.join(HERE, "..", "results", "polyclip204.jsonl"))
sys.path.insert(0, HERE)
import poly204 as P                                            # noqa: E402
import poly204b as PB                                          # noqa: E402
import fig204                                                  # noqa: E402

FP, QP, MB = P.FP, P.QP, P.MB
VERIFIER = "[C: library clip trace] A171/A172/A173 polygon + lonely clip, A161 exact miss, A198/A200 caps + Theorem FC + count; start = A203's closed-form trace; no verifier clause"


def belownormal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetCurrentProcess()
        k.SetPriorityClass(h, 0x00004000)
        k.SetProcessAffinityMask(h, 0xFFFF)
    except Exception:
        pass


def save(doc, cert):
    os.makedirs(os.path.dirname(cert), exist_ok=True)
    tmp = cert + ".tmp"
    json.dump(doc, open(tmp, "w", encoding="utf-8"), indent=1, default=str)
    os.replace(tmp, cert)


def draw(doc):
    try:
        return fig204.render(doc)
    except Exception as e:                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("   fig204 failed: %r" % (e,), flush=True)


def row_of(doc, pad, cert):
    d = doc["pads"][pad]
    slim = dict(nid=doc["nid"], cls=doc["cls"], pad=pad, lam=d.get("lam"), verdict=d.get("verdict"), leaf=d.get("leaf"), clip=d.get("clip"),
                step_killed=d.get("step_killed"), killed_round=d.get("killed_round"), n_rounds=len(d.get("round_times") or []),
                round_seconds=[r.get("seconds") for r in d.get("round_times") or []], seconds=d.get("seconds"), kept=d.get("kept"),
                forced_H=d.get("forced_H"), roles=d.get("roles"), role_slots=d.get("role_slots"), fixed_point=d.get("fixed_point"),
                wall=d.get("wall"), window_pending=d.get("window_pending"), verifier=VERIFIER, start=d.get("start"),
                noroom=(d.get("noroom") or {}).get("verdict"), cert=os.path.relpath(cert, ROOT).replace("\\", "/"),
                prior_tau=doc.get("prior_tau"), record=doc.get("record"), row=doc.get("row"), when=time.strftime("%Y-%m-%d %H:%M:%S"))
    os.makedirs(os.path.dirname(RES), exist_ok=True)
    with open(RES, "a", encoding="utf-8") as f:
        f.write(json.dumps(slim, default=str) + "\n")
    return slim


def run_pad(doc, nid, pad, wall, cert, log=print):
    start = P.load_start(nid, pad)
    T = FP.Trace(wall=wall)
    rec, cls, row = FP.load_page(nid)
    doc["cls"], doc["row"] = cls, dict(family=row.get("family"), camp=row.get("camp"), tau=row.get("tau"))
    doc["record"] = (row.get("record") or "").replace(chr(92), "/")
    try:
        doc["prior_tau"] = float(row.get("tau"))
    except (TypeError, ValueError):
        doc["prior_tau"] = None
    pg = P.PolyPage(rec, cls, nid, T, pad=pad, start=start)
    doc.setdefault("cells", [FP.rect_f(c["rect"]) for c in pg.cells])
    doc.setdefault("slots", list(pg.slots))
    doc.setdefault("wbox", {p: FP.rect_f(pg.item[p]["wb"]) for p in pg.slots})
    doc.setdefault("wbox_pad", {})[pad] = {p: FP.rect_f(pg.item[p]["wb"]) for p in pg.slots}    # the pad's own boxes
    doc.setdefault("H_record", [round(v, 6) for v in pg.record_H])
    d = doc["pads"][pad] = dict(pad=pad, lam=float(pg.lam), start=start, verdict="RUNNING", snapshots=pg.snapshots, round_times=pg.round_times,
                                verifier=VERIFIER)
    log("== %s (%s) at the %s pad: start %s, H %s, forced H %s, H units %s/%s; %d slots; free squares %d" % (
        nid, cls, pad, start.get("source"), [round(v, 3) for v in pg.roles[pg.H]], sorted(pg.forced_H), start.get("n_units_alive"), start.get("n_units"),
        len(pg.slots), pg.n_free))

    def on_round(page):
        d.update(verdict="DEAD" if page.dead else "RUNNING", leaf=page.dead, seconds=round(T.now(), 1), forced_H=sorted(page.forced_H),
                 role_slots={k: list(v) for k, v in page.role_slots.items()})
        save(doc, cert)
        draw(doc)
        r = page.round_times[-1] if page.round_times else {}
        log("   round %s: %s s (fix %s s, %s passes) kept %s changed %s%s" % (
            r.get("round"), r.get("seconds"), r.get("fix"), (page.fix_rep or {}).get("passes"), {k: v for k, v in (r.get("kept") or {}).items() if not k.startswith("P")},
            r.get("changed"), ("; DEAD: " + str(page.dead)) if page.dead else ""))
        if page.rounds:
            rd = page.rounds[-1]
            log("      alive cells %s; caps %s; H reaches %s; forced_H %s; roles %s; instantiated %s; clips %s" % (
                {p: len(v) for p, v in rd.get("single", {}).items()}, rd.get("caps"), rd.get("H_reach"), rd.get("forced_H"), rd.get("forced_role"),
                rd.get("instantiated"), {k: (v.get("n_pieces"), round(v.get("vol", 0), 5)) for k, v in (rd.get("clips") or {}).items()}))

    out = PB.run(pg, on_round=on_round)
    out["step_killed"] = "propagation" if out["verdict"] == "DEAD" else None
    out["clip"] = None
    if out["verdict"] == "DEAD":
        rt = pg.round_times[-1] if pg.round_times else {}
        out["clip"] = rt.get("dead") or ((pg.rounds[-1].get("clip") if pg.rounds else None) or "EmptyBox")
        out["killed_round"] = rt.get("round")
    else:
        nr = QP.noroom_leaf(pg, log)
        out["noroom"] = nr
        if nr and nr.get("verdict") == "DEAD":
            out.update(verdict="DEAD", leaf="no-room (A189 Lemma 1): %s" % nr.get("reason"), step_killed="noroom", clip="NOROOM", killed_round=len(pg.round_times))
    out["fixed_point"] = bool(pg.rounds and pg.rounds[-1].get("fixed_point"))
    out["wall"] = bool(pg.rounds and pg.rounds[-1].get("wall")) or T.out_of_time()
    out["kept"] = (pg.fix_rep or {}).get("kept")
    out["window_pending"] = (pad == "zero") and out["verdict"] == "DEAD"
    if out["window_pending"]:
        out["leaf"] = (out["leaf"] or "") + " [pad 0: s0-only, WINDOW-PENDING]"
    out["tests"], out["steps"], out["seconds"] = T.tests, T.steps, round(T.now(), 1)
    out["role_slots"] = {k: list(v) for k, v in pg.role_slots.items()}
    d.update({k: v for k, v in out.items() if k not in ("snapshots",)})
    save(doc, cert)
    draw(doc)
    log("   => %s at the %s pad in %.1f s, %d rounds%s%s" % (out["verdict"], pad, out["seconds"], len(pg.round_times),
                                                              " (fixed point)" if out["fixed_point"] else (" (WALL)" if out["wall"] else ""),
                                                              ("; " + str(out["leaf"])) if out["leaf"] else ""))
    return row_of(doc, pad, cert)


if __name__ == "__main__":
    belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--wall", type=float, default=900)
    ap.add_argument("--pads", default="g1,zero")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    cert = os.path.join(CERTS, "polyclip204_%s.json" % a.nid)
    doc = dict(nid=a.nid, pads={})
    if os.path.exists(cert) and not a.force:
        try:
            doc = json.load(open(cert, encoding="utf-8"))
        except Exception:
            doc = dict(nid=a.nid, pads={})
    for pad in a.pads.split(","):
        prev = doc["pads"].get(pad)
        if prev and prev.get("verdict") in ("DEAD", "ALIVE") and not a.force:
            print("   %s pad: cached %s" % (pad, prev["verdict"]), flush=True)
            if prev["verdict"] == "DEAD":
                break
            continue
        r = run_pad(doc, a.nid, pad, a.wall, cert)
        if r["verdict"] == "DEAD":
            break
    try:
        print("   gallery: %s" % fig204.gallery(), flush=True)
    except Exception as e:                                        # noqa: BLE001
        print("   gallery failed: %r" % (e,), flush=True)
