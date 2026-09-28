"""Paráfrases de hipóteses fechadas do cripto contra `cain findings check` (a verdade é o estado em 341d270)."""
import json, os, subprocess, sys
from datetime import UTC, datetime
O = sys.argv[1]
DB = f"{O}/findings.db"
NOW = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
CASES = [
    ("H1 quase literal, com família", "HMM de regimes com z-score do funding em janela de 90 dias e open interest para prever o BTCUSDT perpétuo", {"hypothesis-family": "funding_oi_hmm_v3"}, "fechada"),
    ("H1 parafraseada, sem família", "Modelo oculto de Markov que usa a taxa de financiamento e o interesse em aberto para decidir a posição em bitcoin perpétuo", {}, "fechada"),
    ("H2 parafraseada", "Mesma estratégia de regimes por funding, mas com janela curta de 21 dias para o z-score", {}, "fechada"),
    ("H9 parafraseada", "Usar a razão entre open interest e volume negociado como feature de um HMM de regimes no BTC", {}, "fechada"),
    ("H6 parafraseada", "Inverter o sinal do preditor e operar o contrário com horizonte de 7 dias", {}, "fechada"),
    ("H4 parafraseada", "Um LLM (Gemini) lê indicadores técnicos e notícias e prevê a direção do BTC em 7 dias", {}, "fechada"),
    ("H9 por ID", "qualquer texto", {"hypothesis-id": "crypto:H9"}, "fechada"),
    ("trial por ID", "qualquer texto", {"trial-id": "v3-hmm-funding-oi-fr90"}, "fechada"),
    ("nova de verdade", "Arbitragem de basis entre spot e futuro trimestral de ETH, capturando o carry até o vencimento", {}, "nova"),
    ("fora do domínio", "Prever o número de gols por partida no Campeonato Brasileiro com Poisson", {}, "nova"),
]
rows = []
for name, statement, extra, truth in CASES:
    argv = [os.environ["CAIN_BIN"], "findings", "--db", DB, "check", "--domain", "crypto", "--statement", statement,
            "--as-of", NOW]
    for k, v in extra.items():
        argv += ["--" + k, v]
    done = subprocess.run(argv, capture_output=True, text=True)
    try:
        out = json.loads(done.stdout)
    except ValueError:
        out = {"raw": done.stdout[-600:], "stderr": done.stderr[-600:]}
    rows.append({"case": name, "truth": truth, "exit": done.returncode, "out": out})
json.dump(rows, open(f"{O}/check_results.json", "w"), ensure_ascii=False, indent=1)
for r in rows:
    o = r["out"]
    verdict = o.get("verdict") or o.get("decision") or o.get("equivalent") or o.get("status")
    matches = o.get("matches") or o.get("closed_matches") or []
    print(f"{r['case']:34s} verdade={r['truth']:7s} exit={r['exit']} veredito={verdict} matches={[m.get('subject') or m.get('id') or m.get('finding_id') for m in matches][:3] if isinstance(matches, list) else matches}")
