import PackingCert.MeasureExample
import PackingCert.MeasureData
import PackingCert.MeasureInt
import PackingCert.MeasureIntData
import PackingCert.MeasureIntDataA05
import PackingCert.MeasureIntData382
open PackingCert.Measure PackingCert.Measure.Example

/-- Scaling test only (NOT a meaningful bound): atoms on a grid of spacing `1/k`
in `[0,side]²`, all of weight `w`, `n` huge.  Exercises the box recursion with
many atoms. -/
def gridCert (side : Rat) (k : Nat) (w : Rat) (fuel : Nat) : MCert :=
  let m := (side * k).floor.toNat
  let pts := (List.range (m + 1)).flatMap fun (i : Nat) =>
    (List.range (m + 1)).map fun (j : Nat) =>
      (Atom.mk ((Int.ofNat i : Rat) / (Int.ofNat k : Rat)) ((Int.ofNat j : Rat) / (Int.ofNat k : Rat)) w)
  { n := 1000000, side := side, atoms := pts, fuel := fuel }

def run (label : String) (c : MCert) : IO Unit := do
  let t0 ← IO.monoMsNow
  let r ← IO.lazyPure fun _ => checkMeasureCount c
  let t1 ← IO.monoMsNow
  IO.println s!"{label}: atoms={c.atoms.length} ok={r.1} boxes={r.2} time={t1-t0}ms"

/-- `lake exe measure_bench goebel <sideNum> <sideDen> <epsNum> <epsDen> <fuel>`
    `lake exe measure_bench grid <sideNum> <sideDen> <k> <wNum> <wDen> <fuel>`
    `lake exe measure_bench data <fuel>`   (the certificate in PackingCert/MeasureData.lean) -/
def main (args : List String) : IO UInt32 := do
  match args with
  | ["goebel", sn, sd, en, ed, f] =>
    let side : Rat := (sn.toInt!) / (sd.toInt!)
    let eps : Rat := (en.toInt!) / (ed.toInt!)
    run s!"goebel side={side} eps={eps} fuel={f}" (goebelPert side eps f.toNat!)
    return 0
  | ["grid", sn, sd, k, wn, wd, f] =>
    let side : Rat := (sn.toInt!) / (sd.toInt!)
    let w : Rat := (wn.toInt!) / (wd.toInt!)
    run s!"grid side={side} k={k} w={w} fuel={f}" (gridCert side k.toNat! w f.toNat!)
    return 0
  | ["data", f] =>
    let c := { Data.a05_10pt with fuel := f.toNat! }
    run s!"data side={c.side} n={c.n} fuel={f}" c
    return 0
  | ["int_a05", f] =>
    let c := { PackingCert.MeasureI.Data.a05_10pt_int with depth := f.toNat! }
    let t0 ← IO.monoMsNow
    let r ← IO.lazyPure fun _ => PackingCert.MeasureI.checkMeasureICount c
    let t1 ← IO.monoMsNow
    IO.println s!"int_a05 s={c.sNum}/{c.sDen} n={c.n} depth={f}: atoms={c.atoms.length} ok={r.1} boxes={r.2} time={t1-t0}ms"
    return 0
  | ["int_3_82", f] =>
    let c := { PackingCert.MeasureI.Data.cert_3_82 with depth := f.toNat! }
    let t0 ← IO.monoMsNow
    let r ← IO.lazyPure fun _ => PackingCert.MeasureI.checkMeasureICount c
    let t1 ← IO.monoMsNow
    IO.println s!"int_3_82 s={c.sNum}/{c.sDen} n={c.n} depth={f}: atoms={c.atoms.length} ok={r.1} boxes={r.2} time={t1-t0}ms"
    return 0
  | ["int_3_80", f] =>
    let c := { PackingCert.MeasureI.Data.cert_3_80 with depth := f.toNat! }
    let t0 ← IO.monoMsNow
    let r ← IO.lazyPure fun _ => PackingCert.MeasureI.checkMeasureICount c
    let t1 ← IO.monoMsNow
    IO.println s!"int_3_80 s={c.sNum}/{c.sDen} n={c.n} depth={f}: atoms={c.atoms.length} ok={r.1} boxes={r.2} time={t1-t0}ms"
    return 0
  | _ => IO.println "usage: measure_bench goebel sN sD eN eD fuel | grid sN sD k wN wD fuel | data fuel | int_a05 depth | int_3_80 depth"; return 1
