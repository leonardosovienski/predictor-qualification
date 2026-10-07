# 21 — Checklist de publicação (privado; executar só com aprovação humana)

Pré-condições (todas humanas)
- [ ] Confirmar que os oito repositórios privados estão privados (EXTERNAL_VALIDATION_REQUIRED).
- [ ] Decidir sobre remoção do PII e dos patches/dumps dos repositórios privados (06_, EVID-ECO-013/015, EVID-QUAL-008).
- [ ] Confirmar disponibilidade do nome `ecosystem-predictor` ou escolher alternativa.
- [ ] Escolher licença dos textos (LICENSE-NOTICE.md).
- [ ] Revisar manualmente `public-draft/` linha a linha contra 15_, 16_ e 17_.
- [ ] Decidir se os três atestados não revalidáveis serão reemitidos antes da publicação (recomendado) ou publicados como limitação (já redigido).

Antes do primeiro commit público
- [ ] Criar repositório vazio, histórico novo; copiar só `public-draft/` (renomeando para a raiz).
- [ ] Rodar varredura de segredos e de PII no conteúdo final.
- [ ] Verificar que nenhum arquivo contém URL, caminho local ou nome de repositório privado.
- [ ] Adicionar contato em FUNDING.md e SECURITY.md.
- [ ] Carimbar externamente (timestamping) o `EVIDENCE_PACK.md` e registrar a prova no próprio repositório (converte INTERNAL_TIMESTAMP_ONLY em EXTERNAL_TIMESTAMP para o pack).

Depois
- [ ] Registrar em `predictor-qualification/showcase-audit/` o commit público inicial e a data.
- [ ] Não sincronizar automaticamente nada do privado para o público; toda atualização passa por esta checklist.
