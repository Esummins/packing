"""
Attribute running lab processes to a CAMPAIGN, for resource investigations.

Why this is not trivial (T27, refined by A60).  The lab copies code between campaigns, so a
single command line can name three different campaigns and only one of them is the right answer:

    python  ...attempts\\A54-stragglers\\code\\certify.py            <- the SCRIPT (A54's copy)
            ...attempts\\A61-window-stragglers\\results\\nodes\\k5_05.json   <- the DATA  (A61's)
            --out ...attempts\\A61-window-stragglers\\certs\\k5_05.json      <- the OUTPUT (A61's)

The work belongs to whoever the OUTPUT is written for.  Rule, in order:
    1. the `--out` target
    2. else the first data/node argument (a .json that is not the script)
    3. else the script path  (last resort, and flag it as unreliable)
NEVER the process name: `certify.py`, `verify_case.py`, `lpbox.py` exist in every campaign
directory, so a name match identifies nothing.

Usage:  python code/whose.py [--certify-only]
"""
import argparse, re, subprocess, sys, collections

PS = ("Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | "
      "Where-Object { $_.CommandLine } | ForEach-Object { "
      "'{0}|{1}|{2}' -f [math]::Round($_.PageFileUsage/1MB,2), "
      "[math]::Round($_.WorkingSetSize/1GB,2), $_.CommandLine }")
CAMP = re.compile(r"attempts[\\/](A\d+)-")


def campaign_of(cmdline):
    toks = cmdline.split()
    out = None
    for i, t in enumerate(toks):
        if t == "--out" and i + 1 < len(toks):
            out = toks[i + 1]
    if out:
        m = CAMP.search(out)
        if m:
            return m.group(1), "--out"
    for t in toks:
        if t.endswith(".json") and not t.endswith(".py"):
            m = CAMP.search(t)
            if m:
                return m.group(1), "data arg"
    for t in toks:
        if t.endswith(".py"):
            m = CAMP.search(t)
            if m:
                return m.group(1), "SCRIPT PATH (unreliable)"
    return "unattributed", "none"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--certify-only", action="store_true")
    a = ap.parse_args()
    raw = subprocess.run(["powershell.exe", "-NoProfile", "-Command", PS],
                         capture_output=True, text=True).stdout
    tot = collections.Counter(); cnt = collections.Counter(); rows = []
    for line in raw.splitlines():
        parts = line.rstrip().split("|", 2)
        if len(parts) < 3:
            continue
        try:
            commit, ws = float(parts[0]), float(parts[1])
        except ValueError:
            continue
        cl = parts[2]
        if a.certify_only and "certify.py" not in cl:
            continue
        camp, how = campaign_of(cl)
        tot[camp] += commit; cnt[camp] += 1
        rows.append((commit, ws, camp, how, cl))
    rows.sort(reverse=True)
    print("%-7s %-24s %9s %8s" % ("campaign", "attributed by", "commit GB", "WS GB"))
    for commit, ws, camp, how, cl in rows[:20]:
        print("%-7s %-24s %9.2f %8.2f" % (camp, how, commit, ws))
    print("\ntotal commit by campaign:")
    for c, v in tot.most_common():
        print("   %-13s %2d procs  %7.2f GB" % (c, cnt[c], v))


if __name__ == "__main__":
    main()
