"""A145 T3 -- the resolve table and the predictor question.

Merges `results/resolves145_*.jsonl` into `results/resolves145.jsonl` and prints

  * one row per re-solved node: impossible fraction, tau before / after, eta, converged,
    certified frozen / certified v3 / alive;
  * the KILL RATE against the impossible fraction, banded -- the answer to "is the PI's reading a
    predictor?", with the control band that makes the comparison meaningful.

    set PYTHONDONTWRITEBYTECODE=1 && python code/table145.py
"""
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")


def load():
    rows = []
    for nm in ("resolves145_rank.jsonl", "resolves145_ctrl.jsonl"):
        p = os.path.join(RES, nm)
        if not os.path.exists(p):
            continue
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return rows


def status(r):
    res = r.get("result")
    if res == "PASS-FROZEN":
        return "CERT-FROZEN"
    if res == "PASS-V3":
        return "CERT-V3"
    if res in ("NO-KILL",):
        return "ALIVE"
    if res is None or res == "ERROR":
        return "ERROR"
    return f"LP-KILL-UNCERT ({res})"


def fresh(r):
    """True if the node was NOT already LP-dead before A145 -- i.e. its stored tau was at (or
    above) the budget, so the drop in tau is A145's and not a re-run of an existing kill.  The
    `FAIL` work-owing nodes were already below budget at the LP and were only missing a
    CERTIFICATE; for them A145's contribution is the certificate, not the kill."""
    tb, bd = r.get("tau_before"), r.get("budget")
    return tb is None or bd is None or tb >= bd - 1e-9


def main():
    R = load()
    R.sort(key=lambda r: (-(r.get("frac_exact") or 0.0), r["id"]))
    with open(os.path.join(RES, "resolves145.jsonl"), "w", encoding="utf-8") as fh:
        for r in R:
            fh.write(json.dumps(r) + "\n")
    print(f"{len(R)} re-solved nodes -> results/resolves145.jsonl\n")
    hdr = (f"{'node':30s} {'tag':16s} {'frac':>6} {'tauB':>12} {'tauA':>12} {'eta':>10} "
           f"{'cnv':>4} {'new?':>5} {'status':22s} {'LPs':>6} {'wall':>7}")
    print(hdr)
    print("-" * len(hdr))
    for r in R:
        ta = r.get("tau")
        tb = r.get("tau_before")
        print(f"{r['id']:30s} {str(r.get('tag'))[:16]:16s} "
              f"{(r.get('frac_exact') or 0.0):6.3f} "
              f"{(tb if tb is not None else float('nan')):12.6f} "
              f"{(ta if ta is not None else float('nan')):12.6f} "
              f"{(r.get('eta') if r.get('eta') is not None else float('nan')):10.6f} "
              f"{str(r.get('converged'))[:1]:>4} {('NEW' if fresh(r) else 'was'):>5} "
              f"{status(r):22s} "
              f"{(r.get('lp_wall_s') or 0):6.0f} {(r.get('wall_s') or 0):7.0f}")

    # ------------------------------------------------------------------ predictor
    bands = [(0.0, 0.15), (0.15, 0.30), (0.30, 0.45), (0.45, 0.60), (0.60, 0.75), (0.75, 1.01)]
    print("\nKILL RATE vs the impossible fraction")
    print(f"{'band':14s} {'n':>4} {'LP kills':>9} {'certified':>10} {'frozen':>7} {'v3':>4} "
          f"{'kill rate':>10} {'mean drop in tau':>17}")
    tot = dict(n=0, k=0, c=0)
    for lo, hi in bands:
        inb = [r for r in R if lo <= (r.get("frac_exact") or 0.0) < hi]
        if not inb:
            continue
        kills = [r for r in inb if r.get("tau") is not None and r.get("budget") is not None
                 and r["tau"] < r["budget"] - 1e-9]
        cert = [r for r in inb if r.get("result") in ("PASS-FROZEN", "PASS-V3")]
        froz = [r for r in cert if r["result"] == "PASS-FROZEN"]
        v3 = [r for r in cert if r["result"] == "PASS-V3"]
        drops = [r["tau_before"] - r["tau"] for r in inb
                 if r.get("tau") is not None and r.get("tau_before") is not None]
        tot["n"] += len(inb); tot["k"] += len(kills); tot["c"] += len(cert)
        print(f"[{lo:.2f},{hi:.2f})  {len(inb):4d} {len(kills):9d} {len(cert):10d} "
              f"{len(froz):7d} {len(v3):4d} {len(kills)/len(inb):10.2f} "
              f"{(statistics.mean(drops) if drops else float('nan')):17.6f}")
    print(f"{'TOTAL':14s} {tot['n']:4d} {tot['k']:9d} {tot['c']:10d}"
          + (f"        rate {tot['k']/tot['n']:.2f}" if tot["n"] else ""))

    # the same table restricted to nodes that were NOT already LP-dead: the clean form of the
    # predictor question, since for a work-owing FAIL node the kill was never in doubt.
    F = [r for r in R if fresh(r)]
    print("\nSAME, restricted to nodes whose stored tau was AT the budget (kill genuinely new)")
    print(f"{'band':14s} {'n':>4} {'LP kills':>9} {'certified':>10} {'kill rate':>10}")
    for lo, hi in bands:
        inb = [r for r in F if lo <= (r.get("frac_exact") or 0.0) < hi]
        if not inb:
            continue
        kills = [r for r in inb if r.get("tau") is not None
                 and r["tau"] < r["budget"] - 1e-9]
        cert = [r for r in inb if r.get("result") in ("PASS-FROZEN", "PASS-V3")]
        print(f"[{lo:.2f},{hi:.2f})  {len(inb):4d} {len(kills):9d} {len(cert):10d} "
              f"{len(kills)/len(inb):10.2f}")

    cpu = sum((r.get("wall_s") or 0.0) for r in R)
    print(f"\nrecorded job wall over the re-solves: {cpu:.0f} s = {cpu/3600:.2f} CPU-h")


if __name__ == "__main__":
    main()
