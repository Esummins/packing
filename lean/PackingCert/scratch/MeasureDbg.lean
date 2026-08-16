import PackingCert.MeasureExample
open PackingCert.Measure PackingCert.Measure.Example

def goFind (side : Rat) (atoms : List Atom) : Nat → Box → Option Box
  | 0, b =>
    match clipBox side b with
    | none => none
    | some b' => if massInside (cosIvl b') (sinIvl b') b' atoms ≥ 1 then none else some b'
  | fuel + 1, b =>
    match clipBox side b with
    | none => none
    | some b' =>
      if massInside (cosIvl b') (sinIvl b') b' atoms ≥ 1 then none
      else
        let p := split b'
        match goFind side atoms fuel p.1 with
        | some x => some x
        | none => goFind side atoms fuel p.2

def c := g26 14
#eval goFind c.side c.atoms c.fuel ⟨0, 1, 0, c.side, 0, c.side⟩
#eval let b : Box := ⟨0, 1, 0, c.side, 0, c.side⟩; clipBox c.side b
#eval let b : Box := ⟨0, 1/1024, 0, 1, 0, 1⟩; (clipBox c.side b, cosIvl b, sinIvl b)
#eval c.atoms
