"""A138: append a scratch Lean section into LocalCertT3.lean before the trailing `end` block."""
import io, sys, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
                 "lean", "PackingCertMathlib", "PackingCertMathlib", "LocalCertT3.lean")
P = os.path.abspath(P)
TAIL = "\nend LocalCertT3\nend S11\nend PackingCert\n"

def main():
    s = io.open(P, encoding="utf-8").read()
    i = s.rindex("end LocalCertT3")
    body = s[:i].rstrip("\n")
    for f in sys.argv[1:]:
        body += "\n\n" + io.open(f, encoding="utf-8").read().rstrip("\n")
    io.open(P, "w", encoding="utf-8").write(body + "\n" + TAIL)
    print("appended", len(sys.argv) - 1, "section(s);", len(body.splitlines()), "lines")

if __name__ == "__main__":
    main()
