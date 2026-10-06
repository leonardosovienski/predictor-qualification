# Suplemento: raízes alternativas Crypto e Brasileirão



Este suplemento é uma segunda época de evidência: não substitui baseline/árvore primária nem aplica achados antigos automaticamente. As raízes foram descobertas seguindo referências do coletor de qualificação; a identidade está em linked-roots.json e linked-root-manifests.json, hashes materiais específicos em evidencias/<p>/alternate-material-hashes.json. Código executado somente em arquivos puros materializados nas cópias independentes já identificadas, nunca nestas raízes originais. Os registros centrais conservam origem, SHA e momento.



| Domínio | Raiz alternativa | Versão manifest | Fonte |

|---|---|---|---|

| Crypto | C:/Cripto/qualificacao/cripto-predictor |1.2.0rc2|research_contract.py/research_runner.py/admission/execution/worker|

| Brasileirão |C:/QUALIFICACAO/repos/brasileirao-predictor|0.3.0rc2|research_runtime/*; pit.py|



As duas fontes alternativas usam Core3.2.1 hash10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3 e Ops4.2.2rc1 hash0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3 por wheels fixadas em uv.sources/uv.lock. Diferem do Ops4.2.1 primário. Crypto alternativa já não declara predictor-research-protocol; contracts de request/result agora pertencem ao domínio. Não transportar a divergência de lock primário para esta versão. CI Crypto alternativa usa dist/cripto_predictor-*.whl, portanto o caminho1.1.0 antigo foi substituído. API guard allow continua admitindo limit<=0; default/prática efetiva do perfil privado continuam não sondados.



## Mudança arquitetural observada



Crypto research_contract estabelece crypto-research-request/result/outcome/1, IDs crypto:, requester trust LOCAL_FILE_ONLY, referências protocol/dataset/baseline/cost_model/evidence por nome+versão, parâmetros limitados. Request não escolhe comando, módulo, path, URL, handler ou capital. AdmissionPolicyV2 do operador resolve allowlist/famílias fechadas/política/hash e limita pendência/recurso. Circuit e CLI cripto-research compõem process/status/results/run/reconcile/backup/restore/put-object, com journal e ResultStore autoritativo. Há separação entre operational_state, scientific_state e economic_state. **Diferença em relação primário:** não envelope/transport/signing/CAIN dentro desse contrato; não afirmar ResearchTaskV1 autenticado como interface desta época. V1 foi encontrado em paths legacy. Integração externa pode adaptar pedidos/resultados, mas consumidor e autenticação não são presumidos pelo domínio.



Brasileirão acrescenta CLI brasileirao-research→research_runtime.runner, contrato brasileirao-research-request/result/outcome/1, LOCAL_FILE_ONLY, IDs brasileirao:. Request WALKFORWARD_FORECAST_EVALUATION restringe SérieA, season2000..2100, target1X2/OU25, janela kickoffs, até400 fixtures opcionais, lead15..10080min, referências dataset/model/features/baseline/cost_model e odds opcional. Admission resolve políticas/hypotheses/competições/season labels e protege H8/H9/H14/H15/A1. Envio de request válido não autoriza trabalhar holdout protegido; admission/executor revalidam. Nenhuma coorte protegida foi executada aqui.



## Algoritmos Crypto alternativos



research_worker usa Core replay para ordenação e available_at<=data_cutoff; observa available>=observed; referência/hash/custo coerentes antes estatística. rows={observed_at,available_at,gross_return,funding_rate}; malformed/implausible/duplicate/insufficient sample têm estados próprios. directions() é **sinal longo constante1**, ou sinal aleatório placebo quando seed explícita; não usa features de HMM/LLM. Retornos assinados são custos/funding por CostModel. Bootstrap iid500/seed17/CI95 sobre média gross/net; equity/drawdown e baseline bps são relatados. SUPPORTED ocorre quando grossCI inferior>0, REFUTED quando superior<0, senão INCONCLUSIVE. WATCH exige SUPPORTED,netCI inferior>0 e economic_gate SHADOW_TRADE; capital permaneceFalse.



Isso demonstra pipeline de um handler fechado e controle placebo, não sinal preditivo genérico. IID exige hipótese de dependência apropriada; esse handler documenta observações non-overlapping mas não fornece aqui teste geral de independência. Trial registra n_trials_family/domain/ecosystem=1 fixos: não equivale a inventário geral de tentativas em outros estudos. A investigação não reestimou CI/modelos/dados reais; somente contratos puros foram executados.



## Algoritmos Brasileirão alternativos



pit.result_available_at define disponibilidade kickoff+180min; sem kickoff usa dataUTC+1dia03h. É regra conservadora de modelo, não recibo de publicação real. observation_available_at aplica a mesma regra. Worker read-only abre dataset admitido, valida hash/identidade, exclui info depois cutoff e constrói replay de informação/decisão: available_at(i)<cutoff(t), cutoff=min(kickoff-lead,data_cutoff). Fitting mensal usa só informação disponível antes do início do mês; Elo de serving usa prefixo disponível no cutoff; não lê current_elo/model_parameter caches do banco nesse fluxo. Grade NB/DC produz1X2/OU e climatologia; labels e closing prices juntam-se apenas depois que forecasts existem.



Constantes observadas: cluster bootstrap por kickoff,1000/seed13/CI95; mínimo30 avaliados,100 calibração,exclusão máxima10%; temporadas sealed incluem2025. Avaliação compara delta model-loss minus baseline-loss: IC superior<0 SUPPORTED, inferior>0 REFUTED. Métrica primária RPS1X2/BrierOU; Brier/log-loss adicionais. Mercado baseline usa Shin quando escolhido. Eventos insuficientes/sem label têm INSUFFICIENT_HISTORY/FORECAST_ONLY e contadores; amostras excluídas permanecem em qualidade.



Economia usa closing odds última pré-match, edge p_model*odd-1 em janela admitida, stake unitário e slippage só winnings, imposto anual positivo calculado separadamente. closing availability não prova oferta aceita nem possibilidade de executar todas stakes/casas. CLV está NOT_MEASURABLE por falta de preço anterior timestamped. roi_net e CI_net são antes taxa; net_after_tax_total é outro campo. Decisão WATCH requer ciência SUPPORT + CI_net inferior>0, portanto não deve ser traduzida para garantia de lucro pessoal pós impostos. CapitalFalse sempre; resultado composto não promove sozinho uma instalação.



## Evidência executada e limites



alternate-domain-probes.json preserva14 sondas PASS em Python3.13.14, stdlib, sockets bloqueados, contratos e PIT lidos integralmente. Crypto: request válido, comando proibido, client_ref opaco fora identidade lógica, IDs de outro domínio rejeitados e JSON duplicado rejeitado. Brasil: request válido, SQL/competição/lead0/offset request rejeitados, kickoff+180/data-only03UTC e naive datetime rejeitado. Essas sondas não executam admission/executor/worker, modelos, Redis, backtests ou pacote instalado.



A identidade dos módulos copiados e sua transformação está registrada. Não houve instalação pesada, acesso a credenciais, runtime de produção ou publicação. Demais arquivos alternativos não possuem revisão semântica integral certificada; alternate-coverage.json discrimina interfaces aprofundadas. As explicações primárias permanecem válidas só em suas identidades e árvores, acompanhadas deste suplemento.



Teste adicional de backup/restore: `evidencias/domain-recovery-probes.json` registra 12 PASS (6 por domínio) executados com Python 3.13.14 sobre módulos copiados e SQLite sintético dentro das cópias. Confirma preservação do SHA da origem, dados e integrity_check após restore, recusa de root não vazio e de bundle adulterado. Não testa writers concorrentes nem atomicidade global de vários bancos. Total destes probes delimitados: 22 originais + 14 contratos alternativos + 12 recovery; não são execução da suíte pytest.
