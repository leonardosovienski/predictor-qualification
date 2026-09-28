"""integration-crypto: acrescenta ao IC-F012 a decisão do dono sobre o soak ("Soak conta a recusa"), idempotente."""
import json
from pathlib import Path
p = Path("/home/superleo13/predictors/work/integration-crypto-predictor-qualification/qualification/integration-crypto/FINDINGS.json")
doc = json.loads(p.read_text(encoding="utf-8"))
f = next(x for x in doc["findings"] if x["id"] == "IC-F012")
if isinstance(f["owner_decision_taken"], dict):
    first = f["owner_decision_taken"]
    f["description"] += (" Efeito no soak, achado depois (runtime da rc11 e soak local com a correção do orçamento, "
                         "cain#75): quando o modelo escolhe a QUAL-SHADOW-001, o domínio recusa, e duas conferências de "
                         "tolerância zero contavam a recusa como tarefa não admitida e resultado perdido; no CI da rc10 "
                         "o modelo de 0,5B não a escolheu (passou por acaso nesse ponto).")
    f["owner_decision_taken"] = [first, {
        "date": "2026-09-28", "by": "dono", "channel": "chat da sessão cripto (pergunta com opções)",
        "words": "Soak conta a recusa (Recomendado)",
        "option_text": ("Ajusto as duas conferências do harness do soak para aceitar a recusa do domínio com código fechado "
                        "(ex.: HYPOTHESIS_NOT_ADMITTED) como desfecho terminal registrado, e não como resultado perdido. "
                        "Emitidas = admitidas + recusadas. As demais conferências de tolerância zero ficam iguais."),
        "applied": ("scripts/soak.py: uma recusa só conta quando os dois lados a registram (TERMINAL_REFUSAL/REJECTED no "
                    "CAIN e REJECTED com código fechado na admissão do domínio, para o request_id da própria task); "
                    "conferência nova: hipótese recusada nunca é emitida de novo (R15)")}]
    p.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("IC-F012 atualizado")
