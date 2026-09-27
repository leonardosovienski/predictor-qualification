# integration-crypto, fase windows-smoke (WINDOWS_SMOKE: E2E + restart no Windows secundário local).
#
# PC 2 do dono, pasta autorizada C:\Cripto\qualificacao\runtime\integration-crypto\ (decisão do dono de
# 2026-09-27 no prompt da sessão; D-23 em PR). Só PowerShell escreve no Windows, só nesta pasta; nada de PATH ou
# variável persistente, Registro, Python do sistema ou instalação global (variáveis só neste processo).
#   1. uv: zip copiado de C:\QUALIFICACAO\runtime\brasileirao2\tools\ e conferido contra o .sha256; extraído aqui.
#   2. Python 3.13 gerenciado copiado da mesma origem para tools\python (uv com only-managed).
#   3. venvs só dos uv.lock (requisitos exportados com hashes, --require-hashes) + wheels publicadas (sha256).
#   4. dados: só as cópias públicas verificadas de ~/predictors/data/d16/cripto/ (SHA256SUMS.txt), sha256 antes e
#      depois da cópia.
#   5. E2E pelo mesmo cenário do Linux (e2e.py: restart do consumidor e do CAIN no meio), pelos entrypoints .exe.
# Uso: powershell -NoProfile -ExecutionPolicy Bypass -File windows_smoke.ps1 -Stage <Root>\stage -DataSrc <UNC do WSL>
#   Stage: runtime_targets.json, req-cain.txt, req-cripto.txt e a cópia de qualification/integration-crypto (mission)
#   DataSrc: \\wsl.localhost\Ubuntu-24.04\home\superleo13\predictors\data\d16 (com SHA256SUMS.txt)
param([Parameter(Mandatory = $true)][string]$Stage, [Parameter(Mandatory = $true)][string]$DataSrc)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$Root = "C:\Cripto\qualificacao\runtime\integration-crypto"
$ToolsSrc = "C:\QUALIFICACAO\runtime\brasileirao2\tools"
$Forbidden = @("C:\Cripto\operacao", "C:\Cripto\pesquisa-20260909", "C:\Cripto\restaurado-20260908", "C:\CAIN")
foreach ($f in $Forbidden) { if ($Root.StartsWith($f, [StringComparison]::OrdinalIgnoreCase)) { throw "pasta proibida" } }
New-Item -ItemType Directory -Force -Path "$Root\tools", "$Root\logs", "$Root\data", "$Root\wheels", "$Root\w" | Out-Null
$Log = "$Root\logs\windows_smoke.log"
function Say([string]$m) { $line = "$(Get-Date -Format o) $m"; Add-Content -Path $Log -Value $line -Encoding utf8; Write-Host $line }
function Sha([string]$p) { (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower() }
Say "windows-smoke start host=$env:COMPUTERNAME (PC 2 do dono, Windows local secundario) os=$([Environment]::OSVersion.VersionString) root=$Root"
# ---------------------------------------------------------------- 1. uv
Copy-Item -LiteralPath "$ToolsSrc\uv-x86_64-pc-windows-msvc.zip", "$ToolsSrc\uv-x86_64-pc-windows-msvc.zip.sha256" -Destination "$Root\tools\" -Force
$expected = (Get-Content "$Root\tools\uv-x86_64-pc-windows-msvc.zip.sha256").Split(" ")[0].Trim().ToLower()
$got = Sha "$Root\tools\uv-x86_64-pc-windows-msvc.zip"
if ($got -ne $expected) { throw "uv zip sha256 $got != $expected" }
Say "uv zip sha256 OK $got"
if (Test-Path "$Root\tools\uv") { Remove-Item -Recurse -Force "$Root\tools\uv" }
Expand-Archive -LiteralPath "$Root\tools\uv-x86_64-pc-windows-msvc.zip" -DestinationPath "$Root\tools\uv" -Force
$uvExe = Get-ChildItem -Recurse -Filter uv.exe "$Root\tools\uv" | Select-Object -First 1
# ---------------------------------------------------------------- 2. Python gerenciado
$pyName = "cpython-3.13.15-windows-x86_64-none"
if (-not (Test-Path "$Root\tools\python\$pyName")) {
  New-Item -ItemType Directory -Force -Path "$Root\tools\python" | Out-Null
  Copy-Item -Recurse -LiteralPath "$ToolsSrc\python\$pyName" -Destination "$Root\tools\python\$pyName"
}
$env:UV_PYTHON_INSTALL_DIR = "$Root\tools\python"
$env:UV_CACHE_DIR = "$Root\tools\uv-cache"
$env:UV_PYTHON_PREFERENCE = "only-managed"
$env:UV_PYTHON_DOWNLOADS = "never"
$py = (& $uvExe.FullName python find 3.13).Trim()
if (-not $py.StartsWith("$Root\tools\python", [StringComparison]::OrdinalIgnoreCase)) { throw "python fora da pasta: $py" }
Say "uv=$(& $uvExe.FullName --version) python=$py version=$(& $py --version 2>&1)"
# ---------------------------------------------------------------- 3. venvs (locks + wheels publicadas)
$targets = Get-Content "$Stage\runtime_targets.json" -Raw | ConvertFrom-Json
function Wheel($t) {
  $name = Split-Path $t.url -Leaf
  $dest = "$Root\wheels\$name"
  if (-not (Test-Path $dest)) { Invoke-WebRequest -UseBasicParsing -Uri $t.url -OutFile $dest }
  $h = Sha $dest
  if ($h -ne $t.sha256) { throw "wheel $name sha256 $h != $($t.sha256)" }
  Say "wheel $name sha256 OK"
  return $dest
}
foreach ($v in @("venv-cain", "venv-consumer")) { if (Test-Path "$Root\$v") { Remove-Item -Recurse -Force "$Root\$v" } }
& $py -m venv "$Root\venv-cain"; & $py -m venv "$Root\venv-consumer"
$cainPy = "$Root\venv-cain\Scripts\python.exe"; $conPy = "$Root\venv-consumer\Scripts\python.exe"
& $cainPy -m pip install -q --require-hashes -r "$Stage\req-cain.txt"; if ($LASTEXITCODE) { throw "pip cain deps" }
& $cainPy -m pip install -q --no-deps (Wheel $targets.cain); if ($LASTEXITCODE) { throw "pip cain" }
& $conPy -m pip install -q --require-hashes -r "$Stage\req-cripto.txt"; if ($LASTEXITCODE) { throw "pip cripto deps" }
foreach ($k in @("cripto", "transport", "protocol")) { & $conPy -m pip install -q --no-deps (Wheel $targets.$k); if ($LASTEXITCODE) { throw "pip $k" } }
& $cainPy -m pip check | Tee-Object -FilePath "$Root\logs\pip_check_cain.txt"
& $conPy -m pip check | Tee-Object -FilePath "$Root\logs\pip_check_consumer.txt"
& $cainPy -m pip freeze | Set-Content -Encoding utf8 "$Root\logs\pip_freeze_cain.txt"
& $conPy -m pip freeze | Set-Content -Encoding utf8 "$Root\logs\pip_freeze_consumer.txt"
& $cainPy -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('GarimpoInvestimentos') is None else 1)"
if ($LASTEXITCODE) { throw "venv do CAIN tem o dominio instalado" }
# ---------------------------------------------------------------- 4. dados (cópias públicas verificadas)
$sums = @{}
foreach ($line in (Get-Content "$DataSrc\SHA256SUMS.txt")) {
  $parts = $line.Trim() -split "\s+", 2
  if ($parts.Count -eq 2) { $sums[$parts[1].TrimStart("*").Replace("\", "/")] = $parts[0].ToLower() }
}
$copied = 0
$cripto = "$DataSrc\cripto\binance-um-btcusdt"
foreach ($f in Get-ChildItem -Recurse -File $cripto) {
  $rel = $f.FullName.Substring($cripto.Length + 1).Replace("\", "/")
  $want = $sums["cripto/binance-um-btcusdt/$rel"]
  if (-not $want) { throw "arquivo fora do SHA256SUMS: $rel" }
  $before = Sha $f.FullName
  if ($before -ne $want) { throw "origem diverge do SHA256SUMS: $rel" }
  $dest = Join-Path "$Root\data" ($rel.Replace("/", "\"))
  New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
  Copy-Item -LiteralPath $f.FullName -Destination $dest -Force
  $after = Sha $dest
  if ($after -ne $want) { throw "copia diverge: $rel" }
  Add-Content -Path "$Root\logs\data_copy.tsv" -Value "$rel`t$want`t$before`t$after" -Encoding utf8
  $copied++
}
Say "dados copiados e conferidos antes/depois: $copied arquivos"
# ---------------------------------------------------------------- 5. operador + E2E (restart do consumidor e do CAIN)
if (Test-Path "$Root\w") { Remove-Item -Recurse -Force "$Root\w" }
New-Item -ItemType Directory -Force -Path "$Root\w\op" | Out-Null
& $conPy -I "$Stage\mission\scripts\operator_env.py" "$Root\w\op" "$Root\data" | Set-Content -Encoding utf8 "$Root\logs\operator_env.json"
$env:CAIN_BIN = "$Root\venv-cain\Scripts\cain.exe"; $env:CAIN_PY = $cainPy
$env:CONSUMER_BIN = "$Root\venv-consumer\Scripts\predictor-research-consumer.exe"; $env:CONSUMER_PY = $conPy
$env:CRIPTO_RESEARCH_BIN = "$Root\venv-consumer\Scripts\cripto-research.exe"
$env:OP_POLICY = "$Root\w\op\policy.json"; $env:OP_OBJECTS = "$Root\w\op\objects"
Push-Location "$Stage\mission\scripts"
& $py e2e.py "$Stage\mission" "$Root\w\e2e" "$Root\out\e2e" 2>&1 | Tee-Object -FilePath "$Root\logs\e2e_stdout.log"
$e2e = $LASTEXITCODE
Pop-Location
Say "e2e exit=$e2e"
Say "windows-smoke end"
exit $e2e
