# docs/residue_map -- file structure (binding for every agent from 2026-09-10 on)

    current/                       the NEWEST checker's page for every node (copies, refreshed by refresh_current.py
                                   from CURRENT.json) + its gallery.  Look here first.  Never write here by hand.
    campaigns/<Ann-name>/          every per-node page a campaign draws (pattern <prefix>_<nid>.svg + its gallery).
                                   Superseded campaigns stay here for the write-up; nothing is deleted.
    *.svg, gen_*.py (top level)    one-off thematic figures with their generators (basin map, descent, sideband,
                                   pinwheel, atlas ...).  A per-node page never goes here.
    CURRENT.json                   {"checker": "<Ann>", "patterns": ["campaigns/<Ann-name>/<prefix>_{nid}.svg", ...]}
                                   in priority order; refresh_current.py copies the first existing page per node.

Rules for a new campaign Ann:
1. Pages: docs/residue_map/campaigns/Ann-<name>/<prefix>_<nid>.svg; gallery: campaigns/Ann-<name>/<prefix>_gallery.svg.
2. When Ann becomes the running checker, set CURRENT.json to it (keep the previous checker's pattern after it as a
   fallback for nodes Ann has not drawn yet) and run refresh_current.py; the status loop reruns it every 10 min.
3. Drawing rules unchanged (memory: present-problems-spatially): hypothesis squares at the box centre / mid-tilt with
   extremal outlines only at admissible poses, pins as pins, schematic objects thin dashed, undecided grey stipple
   never green, a note on every panel saying what it IS, times per step, verifier label on every verdict.
4. Killed nodes' gallery pages move to docs/shadows/a57v4/killed/ by the status loop (unchanged).
A203 finished 20:05; its pages are in campaigns/A203-csp/.
A212 (2026-09-14, the trump5 tree): pages campaigns/A212-trump5tree/trump5tree212_<nid>.svg + trump5tree212_gallery.svg; CURRENT.json stays A211
(the trump5 pages are A60's, not in current/).
