# A132 T2 -- launch the two in-vitro LP shards, BLAS-pinned, BelowNormal.
# Not a shard launch of A57: nothing is written into any campaign.
param([double]$Cap = 240, [int]$NShards = 2, [double]$BudgetS = 1e9, [int]$WarmRows = 30000)

$Base = Split-Path -Parent $PSScriptRoot
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:OMP_NUM_THREADS = "1"
$env:OPENBLAS_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
$env:VECLIB_MAXIMUM_THREADS = "1"

New-Item -ItemType Directory -Force -Path (Join-Path $Base "logs") | Out-Null
for ($i = 0; $i -lt $NShards; $i++) {
    $log = Join-Path $Base ("logs/invitro_c{0}_w{1}_nofine_s{2}.log" -f [int]$Cap, $WarmRows, $i)
    $p = Start-Process -FilePath "python" -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput $log -RedirectStandardError ($log + ".err") `
        -ArgumentList @(
            (Join-Path $PSScriptRoot "invitro132.py"),
            "--jobs", (Join-Path $Base "results/t2_jobs.json"),
            "--shard", $i, "--nshards", $NShards, "--cap", $Cap, "--budget_s", $BudgetS,
            "--warm_rows", $WarmRows)
    Start-Sleep -Milliseconds 400
    try { $p.PriorityClass = "BelowNormal" } catch { }
    Set-Content -Encoding utf8 -Path (Join-Path $Base ("logs/invitro_c{0}_w{1}_nofine_s{2}.pid" -f [int]$Cap, $WarmRows, $i)) -Value $p.Id
    "shard $i pid $($p.Id) prio $($p.PriorityClass) -> $log"
}
