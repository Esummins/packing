# A50 lead verification log (Fable, independent of worker code paths)

2026-08-31, all exact rational (fractions.Fraction), lead's own throwaway scripts.

1. C3 margin: 191/50 - 5 cos(theta_T) = 42003301/15959754923050 (~ +2.6318e-6),
   POSITIVE — 5 cos theta_T misses the window's lower edge. theta_T from
   t = 194075/530594 (Trump certificate).
2. theta* quadratic: 4(cos-sin) = s0 in t = tan(theta/2) is
   (4+s0) t^2 + 8 t + (s0-4) = 0; float root => theta* ~ 1.7347 deg (corrects the
   1.7457 recon figure; matches the float scan's first exclusion edge at 1.735).
   Cluster check at theta*: 3 + 3 sin(theta*) = 3.0914 < 191/50 exactly.
3. s* window membership, exact squaring: (141/50)^2 = 7.9524 < 8 < (s0-1)^2 =
   8.277612343056 => 191/50 < 2 sqrt2 + 1 < s0. (C1 anchor.)
4. C2 Trump spine residuals (independent path): x-spine 0-1-8-2 and y-spine
   2-8-7-9-5 both give EXACT residual -5287/50000000000 (~ -1.0574e-7) against the
   A43 span identity — the certificate's uniform coordinate slack (5287e-11 per
   half-width, twice), well under the 1e-5 canary gate. The equality of the two
   residuals is itself a consistency datum (same slack enters through h at both
   ends).
5. T2.3 wording fix applied: u_geo may be degree 2 in (cos, sin) after projection
   onto a's rotating edge frame; the non-identity with sin^2 theta is a per-family
   exact divisibility check (by cos^2+sin^2-1), not a degree argument.
