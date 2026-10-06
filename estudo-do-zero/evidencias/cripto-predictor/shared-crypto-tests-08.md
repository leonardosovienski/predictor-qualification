# Revisão semântica dos testes Crypto — bloco 08

Leitura integral de fixtures, mocks e assertions; nenhuma execução. Os cenários demonstram contratos sintéticos ou reconciliação de artefatos, sem estabelecer lucro futuro, autorização ou execução real.

## tests/test_hypothesis_loop.py

Proposerfake e DSL fixtures conservam propostas inválidas/malformed/duplicadas no denominador; prompt inclui vocab causal/histórico, injectionunknown rejeitado, recipehashcanônico/dedupcontraarquivo. Tracesappend preserva/corruptloadfalha, .jsontracked deliberado; warmupNone/samplecurta semrho. Evaluate só nota nãoveredito, código textual não referencia register_trial; run_roundnão toca trialsreal e markdownfence tolerada. Não demonstra LLM obedecer mecanismo nem causalidade real.

## tests/test_hypothesis_loop_runner.py

FeatureVectors8h sintéticos cincofields e logforward24h/últimosNone; teste nomeado close-não-positivo apenas testa horizon0 ValueError, NÃO testa close0 para horizonteválido. Evaluationsappend e nonexistentempty, runnerfakeproposer avalia sóaccepted; dryrun escreve arquivos.dryrun separados semLLMreal. Não valida efeitos econômicos.

## tests/test_immediate_audit.py

Protocolo físico commarketfixtures: reconstruçãoDecimalindependente compara cálculoFloat1e-7 e ordena stress<adverse<base; missing/dup/NaN/badclose rejeita e cutoffunclosedhigh/low/close nãoafeta. HTTPfakeGETpublic/authabsent, privateendpointrecusa,429uma tentativa salva. Sem preços ou execução real.

## tests/test_integration_audit_receipt.py

Receiptsfakecomandos/logs completion determinam globalFAILexpiração preservando contractPASS, currentvalidityBLOCKED; exitsuccesssemresultFAIL e completoPASS currentNOT_DETERMINED/economicfalse. Logtamper/traversal rejeitados. Subprocessowrapperclonado/childexit7 preserva código/receipt e secondrunrecusa. Não atesta currentvalidity por exit0.

## tests/test_jobs_operations.py

Jobconfigs instalados-módulo/cwdNone/stateRoot; dailycollectiononlynãoPaperpropaga7fake, phase1exit1PARTIAL exclusivooutrosFAILED, exit0fakechildrenSUCCEEDED. CLIstatuspropaga; filhos reais printskeyfake validam redactionlogs, sleepstimeout124heartbeatFAILED/shutdown130, thread/childbarrier garanteduplicateSKIPPED. Renewalcondicional/expirywindowmissingcorrupt, qualitysnapshotartifactNone/discoverexpecteddb/H8nãoautoagendado. Não executadosaqui, configs não provam agendamento nem integridade artefato.

## tests/test_judge.py

Fakekeysjudge_signatureprovider:model:hash12 e multi-partitiondeterminística/subsetsignatureprovider, missingassetmultiValueError. prompt_hash==itself é tautologia, hexcheck sóformato semconteúdorehash. SQLite historyguarda juiz/uppercase e replaynãoinflan. Não calibra LLM.

## tests/test_judge_calibration.py

Scorefixturesagrupa provider ignorandomodel/hash, statsmeanmedian/threshold e missingexcluded/unknownlabel; spread2providers40 e renderdeclara concordâncianãocomputável partiçãofixa. Estatística distribuição de score, não calibração preditiva contra truth.

## tests/test_kelly_sweep_cli.py

WFAstub e openSweep/registermocks verificam taxa12.5/slippage7encaminhadasdoisKelly e signaturecompatívelCLI. Frozenfamily bypass explícito stub, resultadosNO-GO, semWFAreal.

## tests/test_local_runtime.py

Subprocessos isolam pathvars e CRIPTO_ROOTtmpspaces, paths/settings/tempfile/events/stateconfinados; overridesexternos/relativeescape/CLIflag recusam antesdirs e redigem outsidepath. pipeline.envfake carrega semexportkeys, markerprofilefunciona. Symlinkescape pode pytest.skip por privilégioWindows. Não executado neste estudo.

## tests/test_manual_dependencies.py

Calendarfixtures só dia inteirohalt explica, parcial/unknownnão; não inventacandles nemeligiblehistoricalsignal, overlap/grid/count/naivetime/no-source rejeita. Registrationfuture2030 clona custoscaptital84days novaemptydir, past/imminentrecusa, rehashalterandocustos aindaEconomicRulesfalha, unobservedmissed, launcherfreezechangeantesnetworkmock e statusreadonly sourcecorrupt/futureledger recusa. Não autentica anúncio sourceexample.comnem autorização.