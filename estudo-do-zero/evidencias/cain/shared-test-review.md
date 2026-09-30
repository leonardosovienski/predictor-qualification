# Revisão semântica dos testes CAIN

67 arquivos revisados integralmente, 65 em tests e dois POSIX .ci. Fixtures, doubles, assertions, subprocessos e skips foram examinados; nenhum teste executado neste estudo. Hash abaixo é conteúdo UTF8 lido, manifesto original preserva bytes físicos.

## tests/api/test_api.py

API TestClient/FakeLLM: saúde e oito etapas; rejeição de entrada/intenção; preferências antes da geração, reabertura e isolamento; busca indisponível não bloqueia perfil.

SHA256 conteúdo: 71cdf8eadcf322b18c22cb14ad116b276e5549c58fe18cee335e739641a56da1

## tests/cli/test_cli.py

CLI subprocesso DB inacessível: exit1, mensagem CAIN sem traceback.

SHA256 conteúdo: d38ffece73f3085fd3d73b5c03e33fe162f628e5a7599db77abd2ac4ef745962

## tests/cli/test_settings.py

Config monkeypatch ambiente: resolução relativa, provider instanciado sem inferência, tipos/chaves inválidos rejeitados.

SHA256 conteúdo: e5be5c04ffb7310b63b35f27b9226c2041a2d0765e5efefa921107d0b85b2aed

## tests/evaluation/test_functional.py

Functional FakeLLM seis etapas e correções: real_llm=false/qualidade humana desconhecida; falha auditada sem resposta nem retry; fake via CLI bloqueado.

SHA256 conteúdo: 35715ed79a153fb676e80f81bf1c24c93a9516e26210b4409f90082eb2fbca3a

## tests/evaluation/test_harness.py

Harness matriz smoke 324 respostas sintéticas: comparabilidade de entradas, cegamento metadata, isolamento A/B/C, orçamento caracteres, falhas e metadados detached; não mede convergência real/validade embedding nem qualidade humana.

SHA256 conteúdo: 6c26c70816c53f77e381bb5ed19933379722de0655877c8af294ea522ddea2ed

## tests/evaluation/test_packaged_resources.py

Recursos empacotados: bytes iguais, cwd independente, identidade de código executado/hash dependência; git_commit não adivinhado.

SHA256 conteúdo: 7861a4310027bde394c0814a41629fa4b5ce631155bbc2b8fdaf55f1970de9a8

## tests/evaluation/test_quality.py

Quality dataset 14 casos dev/holdout: dois braços entrada idêntica, JSON estrito/rotas/fatos por heurística/citações; código somente AST, inclusive retorno errado aceita sintaxe, nunca execução; winner/humanquality desconhecidos, falhas retidas.

SHA256 conteúdo: b1f3ea2dc2c14547cdfc370564acef16ff16ffeade474807d0731ed0033524a4

## tests/evaluation/test_v2.py

EvaluationV2 tipos/duplicatas/NaN e literalidade; semântica requer revisão; isolamento saída sem overwrite; attestation loopback precede mutação; controles e catálogo congelado. run v2_integrity é assertion declarada, não executada aqui.

SHA256 conteúdo: 16e5d333afe018adf5e2700a74dd0efcf19568a732288d9d2d2d4e638007df59

## tests/integration/test_agent_capabilities.py

Capabilities fixtures ResearchService e modelo instrumentado: etapas/idempotência/aprovação/retomada/revogação/cancelamento/lease expirado; relações literais; MCP allowlist e stdio subprocesso; API compartilhada e streaming mock. Não exercício real LLM.

SHA256 conteúdo: 41a6a1deeee3701465386ec6cab617b690673587ce620b3b3681a7c22f956761

## tests/integration/test_architecture_permissions.py

Permissions Path.open guard: revogação impede leitura da fonte; history redige sob política atual.

SHA256 conteúdo: cc3862ee64cc82b0d3a613d0cf366f5f0f654fcfe4c8bf1285115e1011657ca6

## tests/integration/test_archive.py

Archive DBs/documentos temporários: backup/restore identidade e unicode, sem overwrite; hash adulterado/missing document rejeitados antes conclusão.

SHA256 conteúdo: 2906e20dc6d495b82dc97a1cde0e76de86dac35ac64f755715d15ab19eadc98c

## tests/integration/test_compound_decision_lookup.py

Compound field lookup sem inferência: estado/trial/motivo/amostra completos e condicionais; identidade A72 versus A720, unicode; campos ausentes e revisões conflitantes explícitos; interpretação não redefinida como lookup.

SHA256 conteúdo: 7c39b3a97c1a46753534d3c9181d35ffe2d76a3545e4ff0f50afb3c5fc5686d8

## tests/integration/test_conversation_regressions.py

Conversation modelos dublês: cotidiano evita retrieval; aritmética exata frações e limites sem execução; informação antiga não vira citação; hipotéticos/literal output encaminhados intactos, não avalia qualidade desses outputs simulados.

SHA256 conteúdo: 7ef4d5a1e61ace2619cc3016dbdfaaecd9db6d9d6ccfd9873dc4f45cb695f344

## tests/integration/test_delivery_architecture.py

Delivery DB temporário: record_turn falha antes/depois commit recuperável sem nova geração; completion/outcome transação única; processing abandonado bloqueia rerun; dois apps concorrentes geram uma vez; os._exit subprocesso três checkpoints. Não queda física de energia.

SHA256 conteúdo: 0f77d14348e018a2c90507bd272c7b7b23f44826a725b41998594d693d1f4457

## tests/integration/test_evidence_selection.py

Evidence selection: offsets e chaves tardias, negadores e condições inteiros, identidades unicode sem substring; JSON duplicado abstém; limite indivisível omite; mock paginação; revogação impede entrega.

SHA256 conteúdo: 64d84ed2c181d5195649996436066b01d1422c49a5234e4899ef286c2f1930bb

## tests/integration/test_full_audit.py

Full audit: tipos config estritos; perfil/código lazy sem embedding; limite transport 4MiB; documento alterado rejeitado; caminhos absolutos sobrevivem cwd; servidor loopback redirect bloqueado sem segunda chamada.

SHA256 conteúdo: b101ca212cc8254bf7caba5b8ec1e173b1774e1f02aaba45c2d0f8e69beab7fb

## tests/integration/test_generation_language_preference.py

Language preference CaptureLLM: en/pt instrução chega prompt, payload original preservado, scope session/user; não comprova que modelo obedece idioma.

SHA256 conteúdo: 0fb36ab0a376c73cac3989204fbaa7d102e6c72e32ba05328c1161136f1445cd

## tests/integration/test_greetings.py

Greetings modelo proibido: respostas determinísticas seis saudações auditadas; conteúdos adicionais/intenção explícita não engolidos.

SHA256 conteúdo: d0a529d6e863ae6356e48d044cfdc71b6db531ffcac7b93b6dc35324a07525f8

## tests/integration/test_grounded_analysis.py

Grounded analysis PLAN fixtures e PointerModel: lexemas JSON escaped/offsets literais, paths identidade exata, extração sem inferência/permissão geração; unlabelled tables e duplicatas abstêm; revisão gerada não certifica semântica. Orçamento inclui provenance/preamble/header inteiros; separa seções/publicações; prior proposals omitidas antes evidência; excesso resposta rejeitado.

SHA256 conteúdo: e1c775ae3115009c5e973632b2856ed6185b6420b09aa1ffbe2aa750dcbade20

## tests/integration/test_historian_quote_choices.py

Historian quote choices enum somente campos completos literais e limitados; duplicatas/fragmentos não viram escolhas; revogação durante inferência descarta output.

SHA256 conteúdo: 9ff47f1f620e2cd1682544c92df25a72ee610227385eb2bae681a1e8cc3d974a

## tests/integration/test_historian_quote_serialization.py

Quote serialization: substring JSON exata aceita; aspas adicionadas/campo omitido/reconstrução rejeitados, sem reparação automática.

SHA256 conteúdo: 3a86bca49f96efaeb640f97b110af65a27d455b53926c96cfb69f941437f6560

## tests/integration/test_hybrid_runtime.py

Hybrid runtime modelo duas chamadas: classifier resumo depois agente; razão llm_classifier registrada. Modelo sintético.

SHA256 conteúdo: 656fd5037d11a9e317f6f2d5a502aafa7e263e805b88fd9c15e4aa7bfa8010b2

## tests/integration/test_independent_review.py

Independent review: CRLF/unicode e pointer escaped verificáveis; ausência/ambiguidade sem fallback; condições multilinha inteiras; protocolos antigos leitura/cancel idempotente, sem nova execução; orçamento abstém explicitamente.

SHA256 conteúdo: a169b72444c179a43f46cd47134a9224a1173213e4efea7c484752f250c48270

## tests/integration/test_mandate_completion.py

Mandate completion API lookup estado/trial/missing sem LLM; historian bundle metadata sem conteúdo; selection subprocesso source-first e receipt adulterado/policy revoked/pointer errado impedem verification.

SHA256 conteúdo: fbec233f596e148a7577ed69c2dd5b7fa3149392004e3427d3d690bb5ed7fff6

## tests/integration/test_persistence.py

Persistence SQLite reopen: índice lexical reconstruído reproduz ranking/filtros; snapshots detached; user mismatch rejeitado; decision SQL triggers impedem UPDATE/DELETE/REPLACE e reabertura mantém append.

SHA256 conteúdo: 375d681d9a1869b08959825a7f7aaee5c2f4c2989debecc811ed702321d8ac11

## tests/integration/test_plug_new_agent.py

Plugin UppercaseAgent registro dinâmico e intenção uppercase oito etapas/log; registry congela após execução, nova inscrição rejeitada.

SHA256 conteúdo: 60725e5aa700a40feb5492363153ca57a1f9659fa7fab5be15c8f4b83507f6a5

## tests/integration/test_preference_persistence.py

Preference persistence: correção/provenance sobrevive reopen; forget não ressurge de memória legacy; fontes retidas; index failure mantém canônico; duplicate signal rollback/revision stale; legacy JSON migra compatível; top_k/user/currentrequest isolados.

SHA256 conteúdo: c30eeee50e792c9f184e1b1da7fe189e5677c54742d829cb56903c6d471f4e58

## tests/integration/test_recent_conversation_context.py

Recent context: fatos sobrevivem reopen sem overlap lexical; usuário/projeto/sessão isolados e prefs antigas excluídas; followup usa conversa sem classifier; comandos saída não puxam resposta antiga; ordem cronológica. Modelos assertions de contexto, não qualidade geral.

SHA256 conteúdo: 5a96a5e57ac43642a6b7984e60f4af606bf25a4709923303e034278a3c579ba4

## tests/integration/test_research_completion.py

Research completion: política revoked antes/depois model failure não retorna fatos; API history reabre session própria; corrupção filtros/membership não falseia ausência e rebuild restaura; duplicate JSON output rejeita; braços synthetic duas chamadas utility INCONCLUSIVE.

SHA256 conteúdo: 86c8845380d4bea056fbeaecdc2967ec011e94ad5298df14f89f00f44ead1ce2

## tests/integration/test_research_failures.py

Research failures: projeção OSError rollback com receipt separado; audit unavailable erro explícito; JSON quotas/depth; origin adulterada rejeitada; backup WAL snapshot comprometido apenas. Windows launcher skipif fora Windows, fake python impede provider startup e serviço estranho não parado.

SHA256 conteúdo: bb3dbfc4e2b6ff8434e38305c9c14c27b6225cd84e66e23dcc8b9dce688f5b9a

## tests/integration/test_research_inspection.py

Inspection synthetic: namespaces/revisões/supersession declarada apenas, missing/cycle/status findings e UTC ordering; política scope e recheck, sem escrever histórico/LLM; offline API/CLI; quotas e corrupção explícitas.

SHA256 conteúdo: 6bda279e265141bff2d68237777a98e100509ebced78058465c039d1a56edea7

## tests/integration/test_research_l0.py

ResearchL0 fixture define grants/publications synthetic: idempotência, namespaces e concorrência 8 imports/1admitted; conflito rollback; ordenação revisões e ambiguidade preservadas; malformations/path/symlink, quotas, corruption/rebuild/backup, SQL pagination. QuoteProvider só extração literal e síntese livre rejeitada; Fake simulation explícita. Symlink test skip se privilégio indisponível.

SHA256 conteúdo: 6609098b49edf43e5511524ff5ea13a84d0898a1ab512bdd85e7bdcd5036f209

## tests/integration/test_research_roots.py

Research roots policyV2 scope-bound dois roots mesmos filenames, consulta offline após remoção produtor; root inválido/nonobject rejeita antes DB; imports duplicados ambiguous.

SHA256 conteúdo: a89b94c1e2dba1753af9d6ea82881668962af2e3f68d34e01e8780af7a0a6666

## tests/integration/test_runtime.py

Runtime RecordingLLM: oito etapas/log duplo, persistência/isolamento; falhas LLM uma chamada sem retry e index mantém fonte; corpus local sem inferência; intenção inválida auditada; preferência atual antes modelo e assistant text não aprendido; confirmação sem LLM.

SHA256 conteúdo: c75e195906458b201301c4030ead0ac7891a4f126504dc5f4fa49673d72873f2

## tests/integration/test_scoped_preferences.py

Scoped preferences clock2030 controlado: turn>session>project>user, remoção fallback; endereços exatos, expiração UTC após reopen e sem mutar revision; scope/expiry inválidos sem writes; tombstones/provenance/rebuild; legacy tabela migração sem reescrever JSON; transação rollback e stale rejection.

SHA256 conteúdo: ad8f5d8833e9a89cc4a85584324f162e923d5d4db7e7378644537e5b3d526fe6

## tests/integration/test_selection_procedure.py

Selection procedure subprocesso start/resume/checkpoint sem repetir efeitos/modelo; missing pointer impede verification; offline audit boundary bloqueia socket e escrita externa em filho. Não prova sandbox universal do sistema.

SHA256 conteúdo: 7c3efeab57ac87a9d3849bbd97f74de42410b7d1c91bf289fa11e0ff52ca99a5

## tests/integration/test_system_expansion.py

System expansion: SummaryAgent texto curto preserva literalmente negação/prazo sem modelo; historian grandes JSON relevantes identidade Unicode; policy recheck e oversized indivisible abstain, quote fora recorte rejeitado.

SHA256 conteúdo: 590d7cf5d11e8e8a41066b9999e1a0e961c25e24a9f96d4e1390441401ec3084

## tests/integration/test_v03_context_budget.py

Context budget UTF8+JSON: defaults2000 bytes, prefs intactas, history truncation indicada, auditoria separada/retida; perfil essencial maior rejeita sem truncar; char bound legacy e scopes isolados.

SHA256 conteúdo: 445849fc8c57fdec9b4ff89d8c5625191ec9573962d5571329e3bce75d876484

## tests/integration/test_v03_review_fixes.py

Review fixes threading events: delayed missing read não sobrescreve perfil recém criado; trigger snapshot rollback criação; turn_id igual decision e prefs temporárias/feedback/history; profile leitura não cria/reassign sessão alheia.

SHA256 conteúdo: 382ccaf83e9b2f5b629d406692868e48f38097f3e2e1e80d1036137bc842e160

## tests/integration/test_v03_workspace_api.py

Workspace API CaptureModel: upload path não confiável descartado, hash/dedupe/reopen, tamanho UTF8/extensions; search projeto exclusivo sem modelo; feedback owned/reason não treina prefs; perfil deterministic; origens maliciosas/Host rejeitados antes persistência, CSP/nosniff.

SHA256 conteúdo: 63d26f86befc23d789dec0d86e1514e3bb4775d2f1bc7831b55885a7d31ac43c

## tests/integration/test_verified_field_review.py

Verified fields lookup sem LLM estado/trial/ausentes; interpretações continuam unverified geração; identidade exata sample não migra vizinho; versões conflitantes preservadas; API job literal completo zero chamadas; revogação impede resolução e condições/unidades íntegras.

SHA256 conteúdo: b21f8b5c3c3ee77e51e56d8c1ce01adac6c814f022f43b06c148822f4d771fda

## tests/test_bundle_remediation.py

Bundle remediation fixture: unauthorized guess indistinguishable sem SQL entities/reservations; approval reservation antes membership; verify revogado antes CAS; external relation não concede papel; descriptor revision resolve; fsync failure no commit; raw variants quota/integrity/backup; evidência metadata sem CAS; conflitos administrativos concorrentes atomic.

SHA256 conteúdo: 5dfce5bf47e8652d12669d96a7571bf13dfd448097d8b72f42827b2e460ad829

## tests/test_hypothesis_catalog.py

Hypothesis catalog temp produtor: spans JSON/JSONL literais, chunks exaustivos, source clocks não adivinhados; Git revision mock fixture; duplicate import/drift/newrevision, output fora produtor; duplicatas/não finite rejeita antes publicação, grande objeto JSON indivisível.

SHA256 conteúdo: 155f2d9668f4282cea100bbb22fdd2dce6a7a19f05b2978215b288dbfb7958bc

## tests/test_packaged_evaluation_resources.py

Packaged resources byte SHA original=package, loaders default data_root e source identity não vazia/commitNone.

SHA256 conteúdo: b2ae3f0db1bdf05e932851261b5102ef40c5f828c050ef428ea41841df2a2c86

## tests/test_project_coverage.py

Project coverage snapshot/bundle contagens separadas e repository not_established/workflow snapshots_only; revogação scope/role; corruption não empty; CLI/API; input drift hash e clocks/receipt time não currenttruth.

SHA256 conteúdo: d5a330ec4668a06f77169009947a872f12a4a3be15c7961717e4782c9581c244

## tests/test_research_bundle.py

Research bundle fixture pré-aprova synthetic entity/artifact15bytes: CAS dedupe/offline materialize, scopes/revocation/caps/reference no fetch; hash/truncation/missing corruption; projection rebuild; injectedDB fail orphan/reencontro; concurrent1admitted1duplicate; junction; backup modes/tamper; metadata-only historian etémero DERIVED; childos._exit promoção/projeção e ENOSPC. Legacy gitshow baseline skip se shallow.

SHA256 conteúdo: 668133f58523387c84516ff8101230cb594d7ae1372fefb1e612bfc53bef6836

## tests/test_structural_diagnostics.py

Structural diagnostics: restart idempotência, generate/role revocation, scope denial, payload tamper campos actor/scope/assertion/id reject; mock total51 demonstra paginação mesma transação, não 51 bundles reais.

SHA256 conteúdo: 49003ffeba38d03159150aeff6cf28d185c954ff225c949627c8aa85cbbb2aa3

## tests/unit/test_agent_evidence_routing.py

Agent evidence routing dublês: operação solicitada versus material citado, intenção explícita evita classifier; ambiguous clarification; classifier JSON invalid falha1call; context autorizado intacto; SearchAgent evidence real corpus+citações pós geração, marker inventado bloqueado; nohit0call; isolamento/current/prefs; budget2400char e fonte precede memória, não semantic truth.

SHA256 conteúdo: f83573f8788a62101427659d3c91911839b8bd80a08708ace9c423bedf8b7620

## tests/unit/test_arithmetic_sequences.py

Arithmetic sequences frações/negativos/decimais cinco casos determinísticos; ação misturada/código/ambiguidade recusada; divisão zero/número enorme limites explícitos.

SHA256 conteúdo: fec9853402cb478d615299dcf5b1eefe37b7c88fb85614ad4cce068e820c8087

## tests/unit/test_embeddings.py

Embeddings FakeOpener: batches2+1 truncatefalse normalize, NaN/zero/types/dims recusados1call; inputguard0call; cache hash/reopen/digest/text invalidation e corrupção/dimchange fail, sem avaliar embedding real.

SHA256 conteúdo: 250fc66d0538f05894f5db6d3fded213e89b597efc42d0c934848cb1f295055f

## tests/unit/test_explicit_preferences.py

Explicit preference pureadapter: NFC/valores canônicos, quotes/docs/thirdparty/ambiguidade não aprende; correção última vence personalidade fixa; negation remove matching sem inferir opposite, tombstones; assistant/transcript notlearning; pastedbody não prefs.

SHA256 conteúdo: a34730e73623f0b34ffb28a22cf7766cbfd87fdda764db64195398f2429fa46c

## tests/unit/test_functional_generation_controls.py

Functional generation controls dataclass serialization conserva think/ctx/predict/bytes/timeout na instancia Ollama, nenhuma inferência.

SHA256 conteúdo: 74fdfc663ba6342784dcf184b43288ceeef3e49d08cbeef1f25bba34f2a9d460

## tests/unit/test_hybrid_search.py

Hybrid search vetores injetados fabricam similaridade: lexical nohit+semanticmatch; identificador exato vence score maior vizinho; tie sorting estável; arquivo edit/hash/cache refreshed; scopes/offsets/hashes/clipping; falha embedding não fallback. Não valida semântica dos embeddings reais.

SHA256 conteúdo: edff777b9888d70960b4cb3385821e8cfa64eb315ef09450516ee9f3cc779a5d

## tests/unit/test_literal_command_route.py

Literal command route conversa por instrução explícita inteira; vazio clarification, comando citado não override busca. Testa rota, não fidelidade de geração.

SHA256 conteúdo: 91c372c698bc9eb140b23a1340d8e5c0db020067c67f1dcdc3eedceb4415a9b7

## tests/unit/test_literal_json_schema.py

Literal JSON schema chaves limitadas/escaped/unicode, ambiguidades/depth recusados; tipo explícito sem constvalue; Model estruturado uma chamada/originaloutput sem retry, não semântica dos valores.

SHA256 conteúdo: 9572910f6ffbfabf9789157087c8fcff3041c1f6054ece93a5f5b1a42eb0e073

## tests/unit/test_llm.py

LLM fixtureHTTP loopback socket real backend simulado: Fake marcado/determinístico; /api/generate body/options; oversized antes request; erro503/missing/partial1call sem fake fallback. Não servidor Ollama real.

SHA256 conteúdo: 53db667012a779d82f9602be826d57a56f9e59ee089f3aaa3cc4807886a5fc9b

## tests/unit/test_preference_scopes.py

Preference scopes marcações explícitas/localized e negação extraída; untrusted quotes/docs excluídos; pureadapter scoped exigeIdentityService e striprouting mantém tarefa.

SHA256 conteúdo: 1d967410fabb295178036fcf74e1fa7628e993054a49bfe20e679baf53488886

## tests/unit/test_provider_composition.py

Provider composition AST proíbe import cli factory em dois arquivos, fake config instanciado sem modelo. Restrição sintática específica não prova arquitetura completa.

SHA256 conteúdo: 24e745042c3607763df2f042c430119ab5a72ee474462bc9fa892a13b2a9eb87

## tests/unit/test_recording_provider.py

Recording provider tool import, isinstance Ollama e model_identity HTTP resposta mock conserva digest/ctx/think. Digest real-digest é fixture literal, não verificação modelo instalado.

SHA256 conteúdo: d16ab6bea831f5a991a5195f80eb0c5e196fd049c4c6dbf626b19e5778f4d117

## tests/unit/test_routing_identity.py

Routing identity prioridade keyword versus explicit auditada; feedback não atribuído preserva fonte sem treino; contexto só usuário proprietário.

SHA256 conteúdo: 330f8a6a158b0b8e6f4880ab813c971cc55fb311ec8aa2d0d176e7a687366cce

## tests/unit/test_search_providers.py

Search providers tempdocs/serverloopback: leitura bounded/HTML strip; private IP/credentials blocked; redirects revalidated DNS pinned via socket mocks; errors/size/nontext sem retry; AutoRetriever web failure nunca vira localhit. Não internet real.

SHA256 conteúdo: f591bdd43e8a34268c9067988cf688852e82e053e1a2ac4d77af419a26c80951

## tests/unit/test_streaming.py

Streaming BytesIO mockNDJSON incremental provisional→done/metadata, falta terminal/truncation/error nunca done; localbudget/NDJSON validation; close libera stream; PIL importorskip imagens e base64/pixel limits, forwarding. Não multimodal quality.

SHA256 conteúdo: ffaeadd29894a2b6f6e406589157e3f1d3d30407a42ac4f63b4d99bb605be78a

## tests/unit/test_v03_chat_scope.py

CLI chat stdin simulado session preference mantém global e reabre session exata, literal resumo sem LLM.

SHA256 conteúdo: 59308c97419ab2c1f66e97a67a56c2a4c5ad3ac1f7703651cc4d4dbfba5c03f7

## tests/unit/test_v03_evidence_byte_budget.py

Evidence byte budget serializedUTF8 inclui idioma/instruções e reserve ctx; Unicode/escaping labels clipping auditado hashes/offsets; lowerrankomit counts, fixedinput oversize0retrieval0generation; fallback legacy chars declarado sem byteattr.

SHA256 conteúdo: 65dc7f0e5125209f3d3d20ef5fde6348405c58dc46dd9e9bde50dc0aeb3c0337

## tests/unit/test_v03_llm_contract.py

LLM contract mockurlopen: schema/options/think/timeout forward, plain sem format; malJSON/invalidschema/truncationmetadata/resetfailure/inputUTF8/reserve guard explícitos uma chamada, sem servidor real.

SHA256 conteúdo: 9868890c31089b1eb9911f51e8412cca9051c05402f9c9e2e2ccf04938c83b7e

## .ci/cain-supply/test_posix_gate.py

POSIX ordinaryLinux explicitassert/euid; unsafe nodes FIFO/symlink, dirswap TOCTOU, permission revoked before CAS, unreadableblob, injection7durabilitypoints, actual syscall ordering fsync/link/COMMIT with trace, source mutation/delete duringtransfer and hardlinkcopyindependence. Requires CAIN_CANDIDATE_ROOT; not executed Windows.

SHA256 conteúdo: b54e04c02894aebb2c54574ece24549ed1e24712069b6935417feed98a3d5dcd

## .ci/completion/test_posix_gate.py

POSIX ordinaryLinux explicitassert/euid; unsafe nodes FIFO/symlink, dirswap TOCTOU, permission revoked before CAS, unreadableblob, injection7durabilitypoints, actual syscall ordering fsync/link/COMMIT with trace, source mutation/delete duringtransfer and hardlinkcopyindependence. Requires CAIN_CANDIDATE_ROOT; not executed Windows.

SHA256 conteúdo: b54e04c02894aebb2c54574ece24549ed1e24712069b6935417feed98a3d5dcd

Limite comum: doubles, JSON fixtures e servidores de teste validam contratos de engenharia; não demonstram qualidade de modelos reais nem conclusões científicas/econômicas. Testes declarados não equivalem a testes aprovados. Dois POSIX devem ser conferidos por igualdade de hash.
