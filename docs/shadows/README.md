# docs/shadows -- file structure (binding for every agent from 2026-09-10 on)

    STATUS.md, review.csv, status_gallery.py   the live status board and its collector (status loop every 10 min)
    a57v4/   the CURRENT A57/A60 review gallery (one page per k>=1 node); a57v4/killed/ = pages of nodes now dead
    k0v4/    the CURRENT k0 residue gallery; k0v4/killed/ likewise
    archive/ superseded galleries kept for the write-up: a57v3/, k0v3/, v1/ (the K-pages), s_family/ (S24-S53)

Rules: a new gallery version vN goes to docs/shadows/<family>vN/ and the previous version moves to archive/ in the
same commit; the collector (status_gallery.py) is pointed at the new directory; killed nodes' pages move to
<gallery>/killed/ by the status loop, never deleted.  Per-node analysis pages of a checking campaign do NOT go here:
they go to docs/residue_map/campaigns/<Ann-name>/ (see docs/residue_map/README.md); current/ there is the browse point.
