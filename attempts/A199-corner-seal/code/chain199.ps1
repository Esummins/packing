# A199: the a57v4 pass at s0, then the pad sweep on Y0491 -- ONE python at a time (BelowNormal, affinity 0xFFFF).
# run from attempts/A199-corner-seal
$env:PYTHONDONTWRITEBYTECODE = "1"
function Run($args, $log) {
    $p = Start-Process -FilePath python -ArgumentList ("-u code/run199.py " + $args) -RedirectStandardOutput $log -RedirectStandardError ($log + ".err") -PassThru -WindowStyle Hidden
    $p.PriorityClass = "BelowNormal"
    $p.ProcessorAffinity = 0xFFFF
    $p.Id | Out-File -Append logs/pids.txt
    $p.WaitForExit()
}
Run "--all --out results/seal199.jsonl --depth 20 --page-wall 300" "logs/pass_s0.log"
Run "--pages k5_16_interior_Y0491 --sweep 1.0005,1.001,1.002,1.003,1.004,1.006,1.008,1.0149426 --out results/seal199_sweep.jsonl --depth 20 --page-wall 300" "logs/sweep_y0491.log"
