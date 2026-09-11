import sys, time, json, os
sys.path.insert(0,'attempts/A203-csp-consistency/code')
import fast30
nid=sys.argv[1]; pad=sys.argv[2] if len(sys.argv)>2 else 'g1'
st=fast30.Stage0(nid,pad)
out=st.run()
print(out['verdict'], out['seconds'], out['leaf'])
for r in out['csp']:
    print('round',r['round'],'units',r['n_units'],'alive',r['alive_units'],'opts',r['n_opts'],'pieces',r['n_opt_pieces'],'iters',r['iterations'],'ms',r['ms'],'sat',r['sat_tests'],r['sat_dead'],'leaf',r['leaf_pairs'],'hits',r['block_hits'],'killed pieces',r['killed_pieces'],'dead unit count',r['dead_unit_count'])
    for d in r['dead_opts']: print('  dead',d['cell'],d['S'],d['rule'],d.get('nearest_maxdist'),d['n_pieces'],d.get('pairs'),d.get('pairs_dead'),d.get('ms'))
    s=r.get('settle') or {}
    print('  settle',s.get('ms'),s.get('kills'),s.get('rule_ms'),s.get('n_dead_options'))
rd=out['rounds'][-1]
print('count',rd.get('count_nochord'),rd.get('count_chord'),'witness',rd.get('witness'),'pair',rd.get('pair_stats'))
print([(s['step'],round(s['seconds'],2)) for s in out['steps']])
