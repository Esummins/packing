#check Rat
#check (Rat.mk' : _)
#eval (1 : Rat) / 3 + (2:Rat)/7
#check @Rat.blt
#check (inferInstance : LT Rat)
#check (inferInstance : DecidableRel (α := Rat) (· < ·))
#check (inferInstance : Min Rat)
#eval min ((1:Rat)/3) ((1:Rat)/4)
#eval decide (((1:Rat)/3) < ((1:Rat)/2))
#print axioms Rat.add
open Lean in
#eval s!"{(3:Rat)/4}"
#check Rat.floor
#check Rat.ceil
#check @Rat.den
#check Rat.instOfNat
#eval ((7 : Rat) / 2).floor
