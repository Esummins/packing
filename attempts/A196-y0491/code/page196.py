"""A196 orchestrator: one page through steps 1-4, each STAGE a child process under its own 1,500 s wall (the process
TREE is killed on timeout), the <= 3 own-pythons rule and the box ceiling checked before every launch.

    python page196.py <nid> [--stages geo,rows,waste,lpa,lpb] [--wall 1500] [--cap 300] [--deadline 700]

Writes results/page_<nid>.json (the stage verdicts) and appends results/pages196.jsonl.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
os.makedirs(RES, exist_ok=True); os.makedirs(LOGS, exist_ok=True)
sys.path.insert(0, HERE)
import prio196                                                   # noqa: E402

ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1")


def child(args, log_path, wall):
    """run `python -u <args>` with the wall; kill the tree on timeout.  Returns (rc, seconds)."""
    prio196.wait_mine(limit=3, max_wait=3600)
    prio196.wait_box(own=1, max_wait=3600)
    t0 = time.time()
    with open(log_path, "a", encoding="utf-8") as fh:
        p = subprocess.Popen([sys.executable, "-u"] + args, stdout=fh, stderr=subprocess.STDOUT, env=ENV, cwd=HERE)
        try:
            p.wait(timeout=wall)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
            rc = -9
            fh.write("\n== WALL %.0f s: process tree killed\n" % wall)
    return rc, round(time.time() - t0, 1)


def case_key(label):
    return label.replace(":", "_").replace("+", "-")


def run_rows(nid, case):
    import rows196 as RW
    node = case["node"]
    lines = RW.pin_lines(sweep=24)
    rws = RW.rows(node["pieces"], lines, free=11 - len(node["pieces"]))
    out = dict(nid=nid, case=case["label"], n_lines=len(lines), rows=rws, summary=RW.summary(rws))
    json.dump(out, open(os.path.join(RES, "rows_%s__%s.json" % (nid, case_key(case["label"]))), "w", encoding="utf-8"), indent=0)
    return out


def run_waste(nid, case, pitch=0.01, ntilt=36):
    import waste196 as WS
    node = case["node"]
    rec = WS.uncoverable_node("%s__%s" % (nid, case_key(case["label"])), node, pitch=pitch, ntilt=ntilt)
    rec["zone_rects_nofam"] = WS.nofam_rects(rec["zone_rects"])
    json.dump(rec, open(os.path.join(RES, "waste_%s__%s.json" % (nid, case_key(case["label"]))), "w", encoding="utf-8"), indent=0)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--stages", default="geo,rows,waste,lpa,lpb")
    ap.add_argument("--wall", type=float, default=1500.0)
    ap.add_argument("--cap", type=float, default=300.0)
    ap.add_argument("--deadline", type=float, default=700.0)
    ap.add_argument("--pitch", type=float, default=0.01)
    ap.add_argument("--stop-on-kill", type=int, default=1)
    a = ap.parse_args()
    nid = a.nid
    stages = a.stages.split(",")
    log = os.path.join(LOGS, "page_%s.log" % nid)
    page = dict(nid=nid, when=time.strftime("%Y-%m-%d %H:%M"), stages={}, wall=a.wall)
    t0 = time.time()
    if "geo" in stages:
        rc, s = child(["node196b.py", nid, "--deadline", str(a.deadline)], log, a.wall)
        page["stages"]["geo"] = dict(rc=rc, seconds=s)
    np_ = os.path.join(RES, "node_%s.json" % nid)
    if not os.path.exists(np_):
        page.update(verdict="UNDECIDED", leaf="geometry stage produced no record (rc %s)" % page["stages"].get("geo", {}).get("rc"))
    else:
        nodes = json.load(open(np_, encoding="utf-8"))
        page["geo"] = dict(verdict=nodes["verdict"], leaf=nodes.get("leaf"), n_cases=len(nodes.get("cases", [])),
                           cases={c["label"]: dict(verdict=c["verdict"], leaf=c.get("leaf")) for c in nodes.get("cases", [])})
        if nodes["verdict"] == "DEAD":
            page.update(verdict="DEAD", leaf=nodes["leaf"], where="geometry")
        else:
            verdicts = {}
            for case in [c for c in nodes["cases"] if c["verdict"] != "DEAD"]:
                cv = dict(label=case["label"])
                if "rows" in stages:
                    t1 = time.time()
                    r = run_rows(nid, case)
                    sm = r["summary"]
                    cv["rows"] = dict(n_negative=sm["n_negative"], n_beta_le1=sm["n_beta_le1"], tightest=sm["tightest"], seconds=round(time.time() - t1, 1))
                    if sm["n_negative"]:
                        cv.update(verdict="DEAD", leaf="chord row negative: %s rhs %.4f" % (sm["negative"][0]["tag"], sm["negative"][0]["rhs_float"]))
                if "waste" in stages and cv.get("verdict") != "DEAD":
                    rc, s = child(["-c", "import page196 as P, json, os; nodes=json.load(open(os.path.join(P.RES,'node_%s.json'))); "
                                   "case=[c for c in nodes['cases'] if c['label']=='%s'][0]; r=P.run_waste('%s', case, pitch=%s); "
                                   "print('waste |U| %%.4f (%%.1f%%%% of B0) kill=%%s zone %%d rects %%.0fs' %% (r['area_U'], 100*r['ratio_B0'], r['kill'], r['zone_n_rects'], r['seconds']))"
                                   % (nid, case["label"], nid, a.pitch)], log, a.wall)
                    wp = os.path.join(RES, "waste_%s__%s.json" % (nid, case_key(case["label"])))
                    w = json.load(open(wp, encoding="utf-8")) if os.path.exists(wp) else None
                    cv["waste"] = dict(rc=rc, seconds=s, area_U=(w or {}).get("area_U"), ratio_B0=(w or {}).get("ratio_B0"),
                                       kill=(w or {}).get("kill"), zone_n_rects=(w or {}).get("zone_n_rects"), bands=(w or {}).get("bands"))
                    if w and w.get("kill"):
                        cv.update(verdict="DEAD", leaf="Leaf WASTE: |U| = %.4f > %.4f" % (w["area_U"], w["B0"]))
                for leg in ("a", "b"):
                    if ("lp" + leg) in stages and cv.get("verdict") != "DEAD":
                        rc, s = child(["lp196b.py", nid, "--leg", leg, "--case", case["label"], "--cap", str(a.cap), "--wall", str(a.wall)], log, a.wall)
                        lp = os.path.join(RES, "lp_%s__%s_%s.json" % (nid, case_key(case["label"]), leg))
                        r = json.load(open(lp, encoding="utf-8")) if os.path.exists(lp) else {}
                        cv["lp" + leg] = dict(rc=rc, seconds=s, verdict=r.get("verdict"), tau=r.get("tau"), budget=r.get("budget"),
                                             converged=r.get("converged"), n_active=r.get("n_active"), certified=r.get("certified"),
                                             cert=r.get("cert"), support=(r.get("support") or {}).get("kind"))
                        if str(r.get("verdict", "")).startswith("DEAD"):
                            cv.update(verdict="DEAD", leaf=r["verdict"] + " " + str(r.get("cert")))
                            if a.stop_on_kill:
                                break
                cv.setdefault("verdict", "ALIVE")
                verdicts[case["label"]] = cv
            page["cases"] = verdicts
            dead = all(v["verdict"] == "DEAD" for v in verdicts.values()) and verdicts
            page["verdict"] = "DEAD" if dead else "ALIVE"
            page["leaf"] = "; ".join("%s: %s" % (k, v.get("leaf")) for k, v in verdicts.items()) if dead else None
    page["seconds"] = round(time.time() - t0, 1)
    json.dump(page, open(os.path.join(RES, "page_%s.json" % nid), "w", encoding="utf-8"), indent=1)
    with open(os.path.join(RES, "pages196.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(page) + "\n")
    print("== %s: %s %s (%.0f s)" % (nid, page["verdict"], page.get("leaf") or "", page["seconds"]), flush=True)


if __name__ == "__main__":
    main()
