"""A99: turn the measured jsonl into the tables of notes/report99.md.  Reads only A99 results."""
import json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))


def load(name):
    p = os.path.join(RES, name)
    if not os.path.exists(p):
        return []
    out = []
    for ln in open(p):
        try:
            out.append(json.loads(ln))
        except Exception:
            pass
    return out


def r1():
    R = load("r1_ladder.jsonl")
    H = {}
    hp = os.path.join(RES, "r1_holes.json")
    if os.path.exists(hp):
        for h in json.load(open(hp)):
            H[(h["tag"], h["depth"])] = h
    print("\n## R1 -- depth ladder on A85's FAILed certificates (frozen verify_case, jobs 1, split 3)\n")
    print("| certificate | d56 | d64 | d88 | holes 56/64/88 | REAL holes (non-exempt, admissible) | closes? |")
    print("|---|---|---|---|---|---|---|")
    closed = 0
    for r in R:
        st = {s["depth"]: s for s in r["steps"]}
        def cell(d):
            s = st.get(d)
            if not s:
                return "-"
            return f"{'PASS' if s['rc']==0 else ('rc2' if s['rc']==2 else 'FAIL')} {s['wall_s']:.1f}s"
        hs = "/".join(str(st[d]["kinds"].get("hole", 0)) if d in st else "-" for d in (56, 64, 88))
        real = "/".join(str(H[(r["cert"][:-5], d)]["n_hole_real"]) if (r["cert"][:-5], d) in H
                        else "-" for d in (56, 64, 88))
        ok = r["verdict"] == "PASS"
        closed += ok
        print(f"| {r['cert'][:-5]} | {cell(56)} | {cell(64)} | {cell(88)} | {hs} | {real} | "
              f"{'YES d%s' % r['depth_closed'] if ok else 'no'} |")
    print(f"\n**{closed}/{len(R)} FAILed certificates close by re-verification alone.**")
    return closed, len(R)


def r3a():
    R = load("r3a_jobs.jsonl")
    if not R:
        return
    print("\n## R3(a) -- certification wall, --jobs 1 vs --jobs 4 (same certificate, depth 56)\n")
    print("| certificate | j1 wall | j4 wall | speed-up | same rc | same stats | same witnesses |")
    print("|---|---|---|---|---|---|---|")
    sp = []
    for r in R:
        a, b = r["runs"][0], r["runs"][-1]
        sp.append(r["speedup"])
        print(f"| {r['cert'][:-5]} | {a['wall_s']:.2f}s | {b['wall_s']:.2f}s | x{r['speedup']} | "
              f"{r['same_rc']} | {r['same_stats']} | {r['same_witnesses']} |")
    print(f"\nmedian speed-up **x{statistics.median(sp):.2f}** over {len(sp)} certificates "
          f"(min x{min(sp):.2f}, max x{max(sp):.2f}); wall only -- 4 workers, so CPU-seconds do "
          f"not fall.")


def r3b():
    W = {(r["idx"]): r for r in load("r2_screen.jsonl")
         if r.get("pattern") == "plain" and r.get("start") == "warm"}
    C = {(r["idx"]): r for r in load("r3b_cold.jsonl")
         if r.get("pattern") == "plain" and r.get("start") == "cold"}
    both = sorted(set(W) & set(C))
    if not both:
        return
    print("\n## R3(b) -- LP cold vs warm (sibling/parent column pool), identical nodes, same time limit\n")
    print("| cell | tau cold | tau warm | minmass cold | minmass warm | rows c/w | orbits c/w |")
    print("|---|---|---|---|---|---|---|")
    dmm, dtau = [], []
    for i in both:
        c, w = C[i], W[i]
        if c.get("tau") is None or w.get("tau") is None:
            continue
        dtau.append(w["tau"] - c["tau"])
        dmm.append(w["minmass"] - c["minmass"])
        print(f"| {i} | {c['tau']:.4f} | {w['tau']:.4f} | {c['minmass']:.4f} | {w['minmass']:.4f} "
              f"| {c['n_rows']}/{w['n_rows']} | {c['n_orbits']}/{w['n_orbits']} |")
    if dtau:
        print(f"\nmedian tau(warm) - tau(cold) = {statistics.median(dtau):+.4f}; "
              f"median minmass(warm) - minmass(cold) = {statistics.median(dmm):+.4f} "
              f"over {len(dtau)} cells at the same wall budget.")


def r2():
    R = load("r2_screen.jsonl") + load("r2_patterns.jsonl")
    by = {}
    for r in R:
        by.setdefault(r["idx"], {})[r["pattern"] + ":" + r["start"]] = r
    if not by:
        return
    pats = ["plain:warm", "sh1:warm", "sh2dia:warm", "sh2adj:warm", "sh3:warm"]
    have = [p for p in pats if any(p in v for v in by.values())]
    print("\n## R2 -- level-1 cells with Lemma ID's exempt boxes (delta = 0.3, window-valid a_win)\n")
    print("| cell | A38 status | " + " | ".join(f"tau {p.split(':')[0]}" for p in have)
          + " | best eta | decides (eta <= -1.0)? |")
    print("|---|---|" + "---|" * (len(have) + 2))
    dec = 0
    tot = 0
    for i in sorted(by):
        v = by[i]
        if "plain:warm" not in v:
            continue
        tot += 1
        cells = []
        best = None
        for p in have:
            r = v.get(p)
            if r is None or r.get("tau") is None:
                cells.append(r.get("verdict", "-")[:12] if r else "-")
                continue
            cells.append(f"{r['tau']:.4f}")
            if p != "plain:warm" and (best is None or r["tau"] < best):
                best = r["tau"]
        bud = v["plain:warm"]["budget"]
        eta = (best - bud) if best is not None else None
        d = eta is not None and eta <= -1.0
        dec += d
        print(f"| {i} | {v['plain:warm']['a38_status']} | " + " | ".join(cells)
              + f" | {eta if eta is None else round(eta,4)} | {'YES' if d else 'no'} |")
    print(f"\n**{dec}/{tot} sampled level-1 cells reach the eta <= -1.0 screening threshold under "
          f"the best shallow pattern.**  (Calibration on A85's 8 budget-10 rows: 3/4 of the rows "
          f"with eta <= -1.0 certified, 0/4 of the rows with eta > -1.0 did.)")


def r3c():
    R = load("r3c_param99.jsonl")
    if not R:
        return
    print("\n## R3(c) -- parametric re-emission of A85's k0_00 kills over [3.82, s0]\n")
    print("| A85 certificate | emitted | atoms | fixed-side cert wall | parametric wall | factor | verdict | window covered |")
    print("|---|---|---|---|---|---|---|---|")
    for r in R:
        cov = r.get("coverage") or {}
        print(f"| {r['tag']} | {r.get('emitted')} | {r.get('param_atoms','-')} | "
              f"{r['fixed_wall_s']:.2f}s | {r.get('param_wall_s',0):.1f}s | "
              f"{r.get('window_factor_vs_fixed','-')} | {r.get('verdict')} | "
              f"{cov.get('certified_frac','-')} |")


if __name__ == "__main__":
    which = sys.argv[1:] or ["r1", "r2", "r3a", "r3b", "r3c"]
    for w in which:
        globals()[w]()
