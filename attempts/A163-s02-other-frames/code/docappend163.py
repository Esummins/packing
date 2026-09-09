"""A163 -- append the two doc lines the brief names, and nothing else.

  * `docs/residue_ledger.md` section 1b: one sentence, inserted immediately BEFORE the `### 1c.`
    heading (so it stays inside 1b), after A160's paragraph;
  * `docs/budget.md` section D: one sentence, inserted immediately BEFORE the `## E.` heading (so it
    stays inside section D), after A160's paragraph.

The text is read from `notes/doc_lines.md` between the fenced markers, so the staged text and the
appended text cannot drift.  Idempotent: if the A163 marker is already present the file is untouched.
Modelled on A160's `docappend160.py` (read-only import of its shape, not its text).

    python docappend163.py [--dry-run]
"""
from __future__ import annotations

import argparse, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
STAGE = os.path.join(BASE, "notes", "doc_lines.md")
MARK = "A163-s02-other-frames"


def block(name):
    """The blockquote paragraph under the staged heading whose text contains `name`."""
    txt = open(STAGE, encoding="utf-8").read()
    for p in re.split(r"^## ", txt, flags=re.M):
        if name in p.split("\n")[0]:
            lines = [ln[2:] if ln.startswith("> ") else (ln[1:] if ln.startswith(">") else ln)
                     for ln in p.split("\n") if ln.startswith(">")]
            return "\n".join(lines).strip()
    raise SystemExit("no staged block for %s" % name)


def insert_before(path, heading_re, text, dry):
    s = open(path, encoding="utf-8").read()
    if MARK in s:
        print("SKIP %s -- an A163 mention is already present" % os.path.basename(path))
        return False
    m = re.search(heading_re, s, flags=re.M)
    if not m:
        raise SystemExit("heading %r not found in %s" % (heading_re, path))
    new = s[:m.start()] + text.rstrip() + "\n\n" + s[m.start():]
    print("--- %s : inserting %d chars before %r"
          % (os.path.basename(path), len(text), s[m.start():m.end()].strip()))
    if not dry:
        open(path, "w", encoding="utf-8").write(new)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    insert_before(os.path.join(ROOT, "docs", "residue_ledger.md"), r"^### 1c\.",
                  block("residue_ledger.md"), a.dry_run)
    insert_before(os.path.join(ROOT, "docs", "budget.md"), r"^## E\.",
                  block("budget.md"), a.dry_run)
    print("done" + (" (dry run)" if a.dry_run else ""))


if __name__ == "__main__":
    main()
