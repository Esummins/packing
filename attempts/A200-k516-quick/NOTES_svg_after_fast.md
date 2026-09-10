# A200 -- pages AFTER THE FAST STEPS (coordinator, 2026-09-10 14:15)

PI request (14:00): "run the fast steps, then write an svg showing what the fast steps got it to, then it can do the
longer steps" -- so the PI can look for more shortcuts while the slow leaves (SEAL, pair test) run.

What is in place now (no change to the running code):
- quick200.py already emits each pad's certificate (certs/q200_<nid>[_pad0].json) right after the propagation phase
  (normalise / options / union / count), BEFORE seal_leaf / deep_pair, and re-emits after the slow leaves.
- code/live200.py renders every certificate into docs/residue_map/quick200_fast_<nid>.svg (one panel per pad: the
  clipped H box and the record box, pins, instantiated meeters, the forced slots with their meeter-centre union boxes
  and caps/diam/l-inf/chord row, the cells where some slot still has surviving centres as GREY STIPPLE, the count's
  witness cells, the step list with each step's seconds, the verdict) and a contact sheet quick200_fast_gallery.svg.
  It runs as a 180 s loop (scratch pidfile live200.pid) and rewrites only pages whose content changed.
  Hypothesis squares: box centre / mid-tilt if that pose fits the container and misses the pins, else the first sampled
  pose that does (container + pins only), else dashed schematic with a note -- no extremal outlines are drawn.

For the successor (the same engine over the k5_16 tree frontier, or a re-run): emit the page from inside the run
(fig200.draw(pg, outs, <svg>_fast_<pad>.svg) right after the first emit() of each pad, i.e. before seal_leaf /
deep_pair) so the poses come from the pieces; keep live200 as the reader-side fallback.  Never draw a slow-leaf
result on a "fast" page without saying so on the page.
