import PackingCertMathlib.Windows
import PackingCertMathlib.WindowsCheck
import PackingCertMathlib.WindowsCore
import PackingCertMathlib.GuardLine
import PackingCertMathlib.NoRoom
import PackingCertMathlib.ForcedCorners
-- import PackingCertMathlib.LocalCertS33T   (built separately; see A192AxiomsS33.lean)

-- A192: axiom rosters of the new theorems.
-- run: python attempts/A78-lean-wave6/code/lakeb.py --env scratch/A192Axioms.lean

#print axioms PackingCert.S11.WindowsW.windowed_counted
#print axioms PackingCert.S11.WindowsW.windowed_dead
#print axioms PackingCert.S11.WindowsW.windowed_no_family
#print axioms PackingCert.S11.WindowsW.checkWindowsI_kill
#print axioms PackingCert.S11.GuardLineW.chord_sum_le_side
#print axioms PackingCert.S11.GuardLineW.guarded_dead
#print axioms PackingCert.S11.NoRoom.noroom_dead
#print axioms PackingCert.S11.ForcedCorners.slot_crowd
#print axioms PackingCert.S11.WindowsW.checkCoreInBox_sound
#print axioms PackingCert.S11.WindowsW.checkWindowsI_kill_of_check
