"""Merge results from logs (continuations / support runs raced on the json files)."""
import json, os, re, glob
HERE = os.path.dirname(os.path.abspath(__file__))
for p in sorted(glob.glob(os.path.join(HERE, "results", "*.json"))):
    t = os.path.basename(p)[:-5]
    if "_" in t: continue
    R = json.load(open(p))
    # continuation
    cp = os.path.join(HERE, "logs", t + "_cont.out")
    if os.path.exists(cp):
        txt = open(cp, encoding="utf-8", errors="ignore").read()
        m = re.search(r"SCS: (.*?) iters (\d+) pobj ([-\d.]+) dobj ([-\d.]+) res_pri ([\d.e+-]+) res_dual ([\d.e+-]+) gap ([\d.e+-]+) t=(\d+)s", txt)
        b = re.search(r"bracket: ([\d.]+) <= theta'_G <= ([\d.]+)", txt)
        if m and b:
            R.update(theta=float(m.group(3)), theta_dual=float(m.group(4)), sdp_status=m.group(1) + " (continued)", sdp_res_pri=float(m.group(5)), sdp_res_dual=float(m.group(6)), sdp_gap=float(m.group(7)))
            R["theta_ub_cert"] = min(R.get("theta_ub_cert", 99), float(b.group(2)))
            R["theta_lb_feasible"] = max(R.get("theta_lb_feasible", 0), float(b.group(1)))
            R["sdp_iters_total"] = int(m.group(2)) + int(re.search(r"iters (\d+)", open(os.path.join(HERE, "logs", t + ".log"), encoding="utf-8").read()).group(1))
            R["sdp_time_total"] = float(R.get("sdp_time", 0)) + float(m.group(8)) if "(continued)" not in str(R.get("sdp_status_orig", "")) else R.get("sdp_time_total")
    sp = os.path.join(HERE, "logs", t + "_sub.out")
    if os.path.exists(sp):
        txt = open(sp, encoding="utf-8", errors="ignore").read()
        h = re.search(r"\|S\| = (\d+) nodes, (\d+) orbits, (\d+) edges", txt)
        b = re.search(r"bracket: ([\d.]+) <= \. <= ([\d.]+) +\(SCS (.*?), (\d+) it", txt)
        l = re.search(r"LP on G\[S\]: nu = ([\d.]+) \(maxcov ([\d.]+)\);  alpha\(G\[S\]\) = (\d+) (\w+)", txt)
        if h and b and l:
            R["support_sub"] = dict(thr=1e-3, n=int(h.group(1)), orbits=int(h.group(2)), edges=int(h.group(3)), theta_lb=float(b.group(1)), theta_ub=float(b.group(2)), scs_status=b.group(3), iters=int(b.group(4)), nu=float(l.group(1)), nu_maxcov=float(l.group(2)), alpha=int(l.group(3)), alpha_status=l.group(4))
            R["theta_lb_feasible"] = max(R.get("theta_lb_feasible", 0), float(b.group(1)))
    json.dump(R, open(p, "w"), indent=1, default=float)
    print(t, "ub", R.get("theta_ub_cert"), "lb", R.get("theta_lb_feasible"), "sub", bool(R.get("support_sub")))
