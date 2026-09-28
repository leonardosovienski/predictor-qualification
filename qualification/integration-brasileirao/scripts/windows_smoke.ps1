# integration-brasileirao, fase windows-smoke (WINDOWS_SMOKE: E2E + restart no Windows secundário local, PC 2).
#
# Adaptado de qualification/integration-crypto/scripts/windows_smoke.ps1. PC 2 do dono, pasta autorizada
# C:\QUALIFICACAO\runtime\integration-brasileirao\ (prompt da sessão §5.3). Só PowerShell escreve no Windows, só nesta
# pasta; nada de PATH ou variável persistente, Registro, Python do sistema ou instalação global (variáveis só neste
# processo; o git só com -c por comando, nada no config global).
#   1. uv e Python 3.13 gerenciados já em tools\ (zip do uv conferido contra o .sha256).
#   2. stage: cópia de <StageSrc> (preparado por windows_stage.sh no WSL) conferida contra STAGE_SHA256SUMS.txt.
#   3. venvs só dos uv.lock (requisitos exportados com hashes, --require-hashes) + wheels publicadas (sha256).
#   4. dado real: SÓ a cópia conferida do WSL (~/predictors/runtime/integration-brasileirao/data/), sha256 antes e
#      depois da cópia; operador (objetos, datasets real e canário) pelo operator_env.py, num clone do bundle.
#   5. E2E pelo mesmo cenário do Linux (e2e.py: restart do consumidor e do CAIN no meio), pelos entrypoints .exe.
#   6. Fim: tudo o que tem dado real (data\, w\) é transferido para <Back> no WSL, cada arquivo conferido em bytes e
#      sha256, e só então removido do Windows; a pasta raiz, tools\, logs\ e out\ ficam. out\ e logs\ não têm dado real
#      (no_data_rows_check no WSL antes de virar evidência).
# Uso: powershell -NoProfile -ExecutionPolicy Bypass -File windows_smoke.ps1 -StageSrc <UNC do stage> -Back <UNC>
#   StageSrc: \\wsl.localhost\Ubuntu-24.04\home\superleo13\predictors\runtime\integration-brasileirao\priv\<run>\windows-stage
#   Back:     \\wsl.localhost\Ubuntu-24.04\home\superleo13\predictors\runtime\integration-brasileirao\priv\<run>\windows-back
param([Parameter(Mandatory = $true)][string]$StageSrc, [Parameter(Mandatory = $true)][string]$Back)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$Root = "C:\QUALIFICACAO\runtime\integration-brasileirao"
$DataSrc = "\\wsl.localhost\Ubuntu-24.04\home\superleo13\predictors\runtime\integration-brasileirao\data\matches_source_copy.sqlite3"
$DataSha = "31f30a4dcf33867d1f3aa3d12337a9a66047e6bff10b9a3fa86aae9ef06c9e43"
foreach ($d in @("logs", "stage", "data", "wheels", "w", "out", "repo")) {
  if (Test-Path "$Root\$d") { throw "$Root\$d ja existe: rode numa pasta limpa (exceto tools)" }
}
New-Item -ItemType Directory -Force -Path "$Root\logs", "$Root\stage", "$Root\data", "$Root\wheels", "$Root\w", "$Root\out" | Out-Null
$Log = "$Root\logs\windows_smoke.log"
function Say([string]$m) { $line = "$(Get-Date -Format o) $m"; Add-Content -Path $Log -Value $line -Encoding utf8; Write-Host $line }
function Sha([string]$p) { (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower() }
Say "windows-smoke start host=$env:COMPUTERNAME (PC 2 do dono, Windows local secundario) os=$([Environment]::OSVersion.VersionString) root=$Root"
# ---------------------------------------------------------------- 1. uv e Python gerenciados (tools\)
$expected = (Get-Content "$Root\tools\uv-x86_64-pc-windows-msvc.zip.sha256").Split(" ")[0].Trim().ToLower()
$got = Sha "$Root\tools\uv-x86_64-pc-windows-msvc.zip"
if ($got -ne $expected) { throw "uv zip sha256 $got != $expected" }
$uvExe = "$Root\tools\uv\uv.exe"
$env:UV_PYTHON_INSTALL_DIR = "$Root\tools\python"
$env:UV_CACHE_DIR = "$Root\tools\uv-cache"
$env:UV_PYTHON_PREFERENCE = "only-managed"
$env:UV_PYTHON_DOWNLOADS = "never"
$py = (& $uvExe python find 3.13).Trim()
if (-not $py.StartsWith("$Root\tools\python", [StringComparison]::OrdinalIgnoreCase)) { throw "python fora da pasta: $py" }
Say "uv zip sha256 OK $got; uv=$(& $uvExe --version) python=$py version=$(& $py --version 2>&1)"
# ---------------------------------------------------------------- 2. stage conferido
Copy-Item -Recurse -Path "$StageSrc\*" -Destination "$Root\stage\"
$n = 0
foreach ($line in (Get-Content "$Root\stage\STAGE_SHA256SUMS.txt")) {
  $parts = $line.Trim() -split "\s+", 2
  $rel = $parts[1].TrimStart("*").Substring(2).Replace("/", "\")
  if ((Sha "$Root\stage\$rel") -ne $parts[0]) { throw "stage diverge: $rel" }
  $n++
}
Say "stage conferido: $n arquivos"
$Mission = "$Root\stage\qualification\integration-brasileirao"
$targets = Get-Content "$Root\stage\runtime_targets.json" -Raw | ConvertFrom-Json
# ---------------------------------------------------------------- 3. venvs (locks + wheels publicadas)
function Wheel($t) {
  $name = Split-Path $t.url -Leaf
  $dest = "$Root\wheels\$name"
  if (-not (Test-Path $dest)) { Invoke-WebRequest -UseBasicParsing -Uri $t.url -OutFile $dest }
  $h = Sha $dest
  if ($h -ne $t.sha256) { throw "wheel $name sha256 $h != $($t.sha256)" }
  Say "wheel $name sha256 OK"
  return $dest
}
& $py -m venv "$Root\venv-cain"; & $py -m venv "$Root\venv-consumer"
$cainPy = "$Root\venv-cain\Scripts\python.exe"; $conPy = "$Root\venv-consumer\Scripts\python.exe"
& $cainPy -m pip install -q --require-hashes -r "$Root\stage\req-cain.txt"; if ($LASTEXITCODE) { throw "pip cain deps" }
& $cainPy -m pip install -q --no-deps (Wheel $targets.cain); if ($LASTEXITCODE) { throw "pip cain" }
& $conPy -m pip install -q --require-hashes -r "$Root\stage\req-brasileirao.txt"; if ($LASTEXITCODE) { throw "pip brasileirao deps" }
foreach ($k in @("brasileirao", "transport", "protocol")) { & $conPy -m pip install -q --no-deps (Wheel $targets.$k); if ($LASTEXITCODE) { throw "pip $k" } }
& $cainPy -m pip check | Tee-Object -FilePath "$Root\logs\pip_check_cain.txt"
& $conPy -m pip check | Tee-Object -FilePath "$Root\logs\pip_check_consumer.txt"
& $cainPy -m pip freeze | Set-Content -Encoding utf8 "$Root\logs\pip_freeze_cain.txt"
& $conPy -m pip freeze | Set-Content -Encoding utf8 "$Root\logs\pip_freeze_consumer.txt"
& $cainPy -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('brasileirao_predictor') is None else 1)"
if ($LASTEXITCODE) { throw "venv do CAIN tem o dominio instalado" }
# ---------------------------------------------------------------- 4. dado real (cópia conferida do WSL) + operador
$before = Sha $DataSrc
if ($before -ne $DataSha) { throw "origem do dado com sha256 diferente" }
Copy-Item -LiteralPath $DataSrc -Destination "$Root\data\matches_source_copy.sqlite3"
$after = Sha "$Root\data\matches_source_copy.sqlite3"
$srcAfter = Sha $DataSrc
if ($after -ne $DataSha -or $srcAfter -ne $DataSha) { throw "copia do dado diverge" }
Add-Content -Path "$Root\logs\data_copy.tsv" -Value "matches_source_copy.sqlite3`t$DataSha`t$before`t$after`t$srcAfter" -Encoding utf8
Say "dado copiado da copia conferida do WSL: sha256 origem antes=$before depois=$srcAfter copia=$after"
& git -c core.autocrlf=false clone -q "$Root\stage\brasileirao-predictor.bundle" "$Root\repo"; if ($LASTEXITCODE) { throw "clone do bundle" }
New-Item -ItemType Directory -Force -Path "$Root\w\elsewhere" | Out-Null
Push-Location "$Root\w\elsewhere"
& $conPy -I "$Mission\scripts\operator_env.py" --script "$Root\venv-consumer\Scripts\brasileirao-research.exe" `
  --repo "$Root\repo" --commit $targets.brasileirao.commit --dataset "$Root\data\matches_source_copy.sqlite3" `
  --dataset-sha256 $DataSha --work "$Root\w\op" | Set-Content -Encoding utf8 "$Root\logs\operator_env.json"
$op = $LASTEXITCODE
Pop-Location
if ($op) { throw "operator_env exit $op" }
# ---------------------------------------------------------------- 5. E2E (restart do consumidor e do CAIN)
$env:CAIN_BIN = "$Root\venv-cain\Scripts\cain.exe"; $env:CAIN_PY = $cainPy
$env:CONSUMER_BIN = "$Root\venv-consumer\Scripts\predictor-research-consumer.exe"; $env:CONSUMER_PY = $conPy
$env:BRASILEIRAO_RESEARCH_BIN = "$Root\venv-consumer\Scripts\brasileirao-research.exe"
$env:OP_POLICY = "$Root\w\op\policy.json"; $env:OP_OBJECTS = "$Root\w\op\obj"; $env:REAL_ENV = "$Root\w\op\REAL_ENV.json"
Push-Location "$Mission\scripts"
& $py e2e.py "$Mission" "$Root\w\e2e" "$Root\out\e2e" 2>&1 | Tee-Object -FilePath "$Root\logs\e2e_stdout.log"
$e2e = $LASTEXITCODE
Pop-Location
Say "e2e exit=$e2e"
# ---------------------------------------------------------------- 6. dado real de volta ao WSL, conferido; nada fica no Windows
$moved = 0
foreach ($dir in @("data", "w")) {
  foreach ($f in Get-ChildItem -Recurse -File -Force "$Root\$dir") {
    $rel = $f.FullName.Substring($Root.Length + 1)
    $dest = Join-Path $Back $rel
    New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
    Copy-Item -LiteralPath $f.FullName -Destination $dest -Force
    $hs = Sha $f.FullName; $hd = Sha $dest
    if ($hs -ne $hd -or (Get-Item -LiteralPath $dest).Length -ne $f.Length) { throw "transferencia diverge: $rel" }
    Add-Content -Path "$Root\logs\transfer_back.tsv" -Value "$($rel.Replace('\', '/'))`t$($f.Length)`t$hs" -Encoding utf8
    $moved++
  }
}
foreach ($dir in @("data", "w")) { Remove-Item -Recurse -Force -LiteralPath "$Root\$dir" }
$left = @(Get-ChildItem -Recurse -File -Force "$Root" | Where-Object { $_.Extension -in @(".sqlite", ".sqlite3", ".db") -and -not $_.FullName.StartsWith("$Root\tools") -and -not $_.FullName.StartsWith("$Root\venv-") })
Say "dado real transferido ao WSL e conferido (bytes e sha256): $moved arquivos; bancos restantes no Windows fora de tools/venv: $($left.Count)"
if ($left.Count) { throw "banco restante no Windows: $($left | ForEach-Object FullName)" }
Say "windows-smoke end"
exit $e2e
