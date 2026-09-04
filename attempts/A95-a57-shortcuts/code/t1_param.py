"""A95 T1: parametric re-emission of 20 finished A57 k5_11 G1 level-1 nodes.

For each selected node: convert its fixed-side case-measure certificate to
parametric-kill-certificate-v1 with A57's `to_param.py` (the relaxed core anchoring that
cover_invariance.md tool-gap 1 asks for), then run the FROZEN verifier
`attempts/A56-sparametric/code/verify_param.py` over the whole window [191/50, 969271/250000].

Records per node: fixed-side LP+cert wall (from A57's own rows) vs parametric wall, verdict,
box count, and -- on a FAIL that ran to completion -- the s-sub-window the certificate DOES
cover (every 4-D cell not touched by a witness was discharged, so W minus the union of the
witness s-ranges is certified; this claim is void if the run timed out or hit --max-witnesses).

One process at a time, BLAS pinned, jobs=1 (verify_param takes its in-process branch and
spawns nothing).  Read-only over A57: every output goes under A95.
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
A57 = os.path.abspath(os.path.join(HERE, "..", "..", "A57-shadow-trees"))
VP = os.path.abspath(os.path.join(HERE, "..", "..", "A56-sparametric", "code", "verify_param.py"))
OUT = os.path.abspath(os.path.join(HERE, "..", "results"))
PARAM = os.path.join(OUT, "param")
SLO, SHI = "191/50", "969271/250000"
SLO_F, SHI_F = 3.82, 3.877084
NODE_CAP = float(os.environ.get("A95_NODE_CAP", 1500))
GLOBAL_CAP = float(os.environ.get("A95_GLOBAL_CAP", 18000))

sys.path.insert(0, os.path.join(A57, "code"))
import to_param


def interleave(sel):
    g = {}
    for s in sel:
        g.setdefault(s["group"], []).append(s)
    order, i = [], 0
    while any(g.values()):
        for k in ("easy_pass", "marginal_pass", "cert_fail"):
            if g.get(k):
                order.append(g[k].pop(0))
        i += 1
        if i > 1000:
            break
    return order


def covered_window(witfile, complete):
    """W minus the union of witness s-ranges.  Only meaningful if the search completed."""
    if not complete or not os.path.exists(witfile):
        return None
    W = json.load(open(witfile))["witnesses"]
    iv = sorted([w["s_range_float"] for w in W if "s_range_float" in w])
    if not iv:
        return None
    merged = []
    for a, b in iv:
        if merged and a <= merged[-1][1] + 1e-15:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    gaps, cur = [], SLO_F
    for a, b in merged:
        if a > cur:
            gaps.append([cur, min(a, SHI_F)])
        cur = max(cur, b)
    if cur < SHI_F:
        gaps.append([cur, SHI_F])
    width = sum(b - a for a, b in gaps)
    return dict(certified_subwindows=gaps, certified_width=width,
                window_width=SHI_F - SLO_F, certified_frac=width / (SHI_F - SLO_F),
                unproven=merged)


def main():
    os.makedirs(PARAM, exist_ok=True)
    sel = json.load(open(os.path.join(OUT, "t1_selection.json")))["selection"]
    order = interleave(sel)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    res_path = os.path.join(OUT, "t1_param.jsonl")
    done = set()
    if os.path.exists(res_path):
        for ln in open(res_path):
            try:
                done.add(json.loads(ln)["id"])
            except Exception:
                pass
    t_all = time.time()
    for s in order:
        if s["id"] in done:
            continue
        if time.time() - t_all > GLOBAL_CAP:
            print("global cap reached; stopping", flush=True)
            break
        pj = os.path.join(PARAM, s["id"] + ".param.json")
        rec = dict(id=s["id"], group=s["group"], atoms=s["atoms"], eta=s["eta"],
                   eps_geo_used=s["eps_geo_used"], fixed_wall_s=s["fixed_wall_s"],
                   lp_seconds=s["lp_seconds"], cert_seconds=s["cert_seconds"],
                   epsgeo_seconds=s["epsgeo_seconds"], src_cert=s["cert_file"])
        try:
            d = to_param.convert(s["cert_file"], pj)
            rec["param_atoms"] = len(d["atoms"]); rec["param_cores"] = len(d["hypotheses"]["cores"])
        except Exception as e:
            rec.update(verdict="EMIT-ERROR", error=repr(e)[:200], param_wall_s=0.0)
            with open(res_path, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(json.dumps(rec), flush=True)
            continue
        rp = os.path.join(PARAM, s["id"] + ".report.json")
        wf = os.path.join(PARAM, s["id"] + ".witnesses.json")
        cmd = [sys.executable, VP, pj, "--slo", SLO, "--shi", SHI, "--depth", "48",
               "--jobs", "1", "--strict-margin", "0", "--report", rp, "--witness-file", wf,
               "--max-witnesses", "2000", "--max-witnesses-per-box", "1", "--quiet"]
        t0 = time.time()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=NODE_CAP)
            rc, tail = p.returncode, (p.stdout or "")[-1500:]
        except subprocess.TimeoutExpired:
            rc, tail = None, "TIMEOUT"
        wall = round(time.time() - t0, 1)
        rec["param_wall_s"] = wall
        rec["timeout_cap_s"] = NODE_CAP
        if rc is None:
            rec.update(verdict="TIMEOUT", coverage=None)
        else:
            rec["verdict"] = {0: "PASS", 1: "FAIL", 2: "MALFORMED"}.get(rc, f"rc={rc}")
            if os.path.exists(rp):
                r = json.load(open(rp))
                rec["boxes"] = r["stats"]["boxes"]
                rec["s_cells"] = r["stats"].get("s_cells")
                rec["witnesses"] = r["stats"].get("witnesses")
                rec["witness_s_range"] = r.get("witness_s_range")
                complete = rc == 0 or (r["stats"].get("witnesses", 0) < 2000)
                rec["search_complete"] = bool(complete)
                rec["coverage"] = (dict(certified_subwindows=[[SLO_F, SHI_F]],
                                        certified_width=SHI_F - SLO_F,
                                        window_width=SHI_F - SLO_F, certified_frac=1.0,
                                        unproven=[]) if rc == 0
                                   else covered_window(wf, complete))
        rec["ratio_vs_4_fixed_sides"] = (round(wall / (4 * s["fixed_wall_s"]), 4)
                                         if s["fixed_wall_s"] else None)
        rec["tail"] = tail[-400:]
        with open(res_path, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"{s['group']:14s} {s['id']:22s} atoms={s['atoms']:4d} "
              f"fixed={s['fixed_wall_s']:8.1f}s param={wall:8.1f}s -> {rec['verdict']}"
              + (f" cover={rec['coverage']['certified_frac']:.3f}"
                 if rec.get("coverage") else ""), flush=True)
    print("T1 done", flush=True)


if __name__ == "__main__":
    main()
