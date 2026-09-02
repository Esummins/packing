#!/usr/bin/env python3
"""A78 lake wrapper: SERIALISED, LOW-PRIORITY `lake build` for lean/PackingCertMathlib.

Several A78 agents build concurrently while the A57/A60/A61/A76/A77 campaigns own the
CPU.  This wrapper (1) takes a repo-wide lock so only ONE lake process runs at a time,
(2) starts lake at BELOW-NORMAL priority, (3) never rebuilds the isolated
`Measure382Check` module (it refuses if that module's olean is missing so that a
missing cache is reported instead of triggering the 40-minute evaluation).

Usage:  python attempts/A78-lean-wave6/code/lakeb.py [lake build args...]
        python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.Census
        python attempts/A78-lean-wave6/code/lakeb.py --env scratch/Axioms.lean   (lake env lean FILE)
        python attempts/A78-lean-wave6/code/lakeb.py --nolock <targets>            (lead only: light module builds
                                                                                   concurrent with a long corpus run)
"""
import os, subprocess, sys, time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PROJ = os.path.join(REPO, "lean", "PackingCertMathlib")
LOCK = os.path.join(REPO, "attempts", "A78-lean-wave6", ".lake_lock")
M382 = os.path.join(PROJ, ".lake", "build", "lib", "lean", "PackingCertMathlib", "Measure382Check.olean")


def acquire():
    t0 = time.time()
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return
        except FileExistsError:
            # stale lock (older than 3 h) -> remove
            try:
                if time.time() - os.path.getmtime(LOCK) > 3 * 3600:
                    os.remove(LOCK)
                    continue
            except OSError:
                pass
            if time.time() - t0 > 4 * 3600:
                print("lakeb: gave up waiting for lock", file=sys.stderr)
                sys.exit(3)
            time.sleep(5)


def release():
    try:
        os.remove(LOCK)
    except OSError:
        pass


def main():
    args = sys.argv[1:]
    nolock = False
    if args and args[0] == "--nolock":
        nolock = True
        args = args[1:]
    if not os.path.exists(M382):
        print("lakeb: REFUSING - Measure382Check.olean missing (would trigger the 40 min rebuild)",
              file=sys.stderr)
        sys.exit(4)
    if args and args[0] == "--env":
        cmd = ["lake", "env", "lean"] + args[1:]
    else:
        cmd = ["lake", "build"] + args
    if not nolock:
        acquire()
    try:
        t0 = time.time()
        if os.name == "nt":
            flags = subprocess.BELOW_NORMAL_PRIORITY_CLASS
            p = subprocess.run(cmd, cwd=PROJ, creationflags=flags)
        else:
            p = subprocess.run(["nice", "-n", "10"] + cmd, cwd=PROJ)
        print("lakeb: %s -> exit %d in %.1f s" % (" ".join(cmd), p.returncode, time.time() - t0))
        return p.returncode
    finally:
        if not nolock:
            release()


if __name__ == "__main__":
    sys.exit(main())
