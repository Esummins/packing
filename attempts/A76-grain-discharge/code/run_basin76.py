#!/usr/bin/env python3
"""run_basin76.py -- thin wrapper around the FROZEN A66 basin-row pilot rig
(attempts/A66-corners4-pair/code/basinlp.py, imported unmodified) that redirects its output
directory to attempts/A76-grain-discharge/results/ and runs the zone-radius scan the A76 brief
asks for (P-B(R) margin vs R on k4_08).  One process, BLAS-pinned by the rig itself, its own
commit-headroom gate.  Usage: python run_basin76.py --r_z 1e-2 --d_in 3e-3 --d_out 3e-2 --tag r1e-2
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
A66 = os.path.join(HERE, '..', '..', 'A66-corners4-pair', 'code')
sys.path.insert(0, A66)
import pairlp as pl
pl.BASE = os.path.join(HERE, '..')          # results/ and logs/ under A76
os.makedirs(os.path.join(pl.BASE, 'results'), exist_ok=True)
os.makedirs(os.path.join(pl.BASE, 'logs'), exist_ok=True)
import basinlp
basinlp.main()
