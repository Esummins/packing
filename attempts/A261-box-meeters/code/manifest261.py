"""A261: certs/manifest.json -- sha256, sizes and leaf counts of every FINISHED certificate (the big .leaves / .tree
streams are git-ignored; this manifest and results/cert261.jsonl are what is committed).   python manifest261.py"""
import glob
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CERTS = os.path.abspath(os.path.join(HERE, '..', 'certs'))
out = {}
for sp in sorted(glob.glob(os.path.join(CERTS, '*.state.json'))):
    st = json.load(open(sp))
    if not st.get('done'):
        continue
    base = sp[:-len('.state.json')]
    row = dict(leaves=st['leaves'], boxes=st['boxes'], seconds=round(st['seconds'], 1))
    for ext in ('.json', '.tree', '.leaves'):
        b = open(base + ext, 'rb').read()
        row[ext[1:]] = dict(bytes=len(b), sha256=hashlib.sha256(b).hexdigest())
    out[os.path.basename(base)] = row
json.dump(out, open(os.path.join(CERTS, 'manifest.json'), 'w'), indent=1, sort_keys=True)
print(len(out), 'finished certificates in manifest')
