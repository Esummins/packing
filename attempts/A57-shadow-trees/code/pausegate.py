"""Sentinel-file pause + orphan reaper for the A57/A96 drivers.

WHY.  The 2026-09-06 pause killed the drivers, and every in-flight verifier's work was thrown
away -- param96 (like tree57 and deepen) writes a node's row only AFTER reaping its child, so
stopping the parent discards whatever the child had done.  A 180 s grace bought nothing.  The fix
is for drivers to check a sentinel BETWEEN launches: the in-flight node finishes and is recorded,
and only then does the driver exit.

USAGE (driver side), between finishing one node and starting the next:

    from pausegate import paused, wait_or_exit
    if paused(): break          # or: wait_or_exit() to block until the sentinel is removed

The sentinel is a plain file so a human, a cron job or another agent can create it:

    PAUSE            attempts/A57-shadow-trees/PAUSE        pauses A57 drivers
                     attempts/A96-a57-parametric/PAUSE      pauses A96 drivers
    RESUME           delete the file

A57's base is used when the caller does not pass one, so a driver launched from either tree sees
its own sentinel; pass `base=` to watch a specific one.  Both are checked by default so a single
file can stop everything: set A57's PAUSE and the A96 drivers stop too (they import this module
from A57's code directory, which is already on their path).
"""
import os, time

HERE = os.path.dirname(os.path.abspath(__file__))
A57_BASE = os.path.abspath(os.path.join(HERE, ".."))
A96_BASE = os.path.abspath(os.path.join(A57_BASE, "..", "A96-a57-parametric"))
NAME = "PAUSE"


def sentinels(base=None):
    if base is not None:
        return [os.path.join(base, NAME)]
    return [os.path.join(A57_BASE, NAME), os.path.join(A96_BASE, NAME)]


def paused(base=None):
    """True if a pause sentinel exists.  Cheap: one stat per call, safe to poll per node."""
    return any(os.path.exists(p) for p in sentinels(base))


def reason(base=None):
    for p in sentinels(base):
        if os.path.exists(p):
            try:
                return open(p).read().strip()[:400] or "(no reason given)"
            except Exception:
                return "(unreadable)"
    return None


def wait_or_exit(base=None, poll=30.0, max_wait=None, log=print):
    """Block while paused.  Returns True if it waited and the pause lifted, False if not paused.
    With max_wait set, gives up and returns None so the caller can exit cleanly instead."""
    if not paused(base):
        return False
    log(f"PAUSED by sentinel: {reason(base)}")
    t0 = time.time()
    while paused(base):
        if max_wait is not None and time.time() - t0 > max_wait:
            log("pause still set at max_wait; exiting cleanly (work is recorded)")
            return None
        time.sleep(poll)
    log(f"pause lifted after {int(time.time() - t0)} s; continuing")
    return True


# ---------------------------------------------------------------- orphan reaper
def orphans(pattern="certify.py", owner_marker="A57-shadow-trees"):
    """certify.py children whose tree57 parent is gone.

    Found the hard way: a certify.py ran 11.3 h after its parent shard was restarted, burning a
    core unattributed, because nothing reaps a certify child whose tree57 parent has exited."""
    import subprocess, json as _json
    ps = r"""
Get-CimInstance Win32_Process -Filter "Name like 'python%'" | ForEach-Object {
  '{0}|{1}|{2}' -f $_.ProcessId, $_.ParentProcessId, ($_.CommandLine -replace '\|',' ')
}
"""
    try:
        out = subprocess.run(["powershell", "-NonInteractive", "-Command", ps],
                             capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return []
    procs = {}
    for ln in out.splitlines():
        parts = ln.strip().split("|", 2)
        if len(parts) == 3 and parts[0].isdigit():
            procs[int(parts[0])] = (int(parts[1]), parts[2])
    live = set(procs)
    out = []
    for pid, (ppid, cl) in procs.items():
        if pattern in cl and owner_marker in cl and ppid not in live:
            out.append(dict(pid=pid, ppid=ppid, cmd=cl[:120]))
    return out


def reap(dry_run=True, log=print):
    """Report (dry_run) or kill orphaned certify children."""
    import subprocess
    found = orphans()
    for o in found:
        log(f"{'WOULD KILL' if dry_run else 'KILLING'} orphan certify pid {o['pid']} "
            f"(dead parent {o['ppid']}): {o['cmd']}")
        if not dry_run:
            subprocess.run(["powershell", "-NonInteractive", "-Command",
                            f"Stop-Process -Id {o['pid']} -Force -ErrorAction SilentlyContinue"],
                           capture_output=True)
    if not found:
        log("no orphaned certify children")
    return found


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="pause sentinel / orphan reaper")
    ap.add_argument("--reap", action="store_true", help="kill orphaned certify children")
    ap.add_argument("--dry-run", action="store_true", default=False)
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.status or not a.reap:
        print("paused:", paused(), "| reason:", reason())
        for p in sentinels():
            print("  sentinel:", p, "exists" if os.path.exists(p) else "-")
    if a.reap:
        reap(dry_run=a.dry_run)
