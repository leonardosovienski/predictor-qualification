import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
notes={
'cain':{
'src/cain/agents/__init__.py':'Registry frozen; busca prioriza documentos antes histórico isolado user/project; orçamento2400 chars mais ajuste bytes; geração opcional; CodeAgent somente texto; Conversation aritmética/LLM; resumo literal curto e preferências.',
'src/cain/agents/arithmetic.py':'AST limitado64 nós e160 chars, Fraction, operações whitelist, sequência16 passos, números bound1e18; sem eval.',
'src/cain/api.py':'FastAPI bounds Pydantic, Host/Origin loopback e headers CSP; Lock por processo; idempotência run_id por usuário; receipt completed com outcome atômico e recuperação UI; health não verifica provedor.',
'src/cain/archive.py':'SQLite snapshots independentes workspace/research com hashes docs/CAS; restore destino novo e ativação manual; não garante snapshot conjunto atômico.',
'src/cain/runtime.py':'Composition root escolhe SQLite e agentes; índice lexical reconstruído; retriever lazy; FakeLLM default da biblioteca vs Ollama settings.',
'src/cain/orchestrator/__init__.py':'8 passos, observação identidade antes rota, registryfreeze, mediated->identity update->completed; falha registra failed sem retries.',
'src/cain/common/__init__.py':'Dataclasses Message/IdentityState/Signal/ScopedPreference/DecisionRecord/RunResult; PersonalityState stub declarada.',
'src/cain/identity/explicit.py':'Regex conservadora de preferências, ignora quoted/pasted dados, ambiguidade/negação sem inferir inverso; usa só user_input, provenance e tombstones.',
'src/cain/identity/scopes.py':'Identidades contexto bounds200 e dependências escopo; timestamps timezone obrigatória e expiration futura.',
'src/cain/llm/__init__.py':'Ollama geração bounded sem redirect/retry/fakefallback, JSONparse, truncation error partial, HTTPerror bounded; FakeLLM hash determinístico.',
'src/cain/persistence/__init__.py':'Protocolos IdentityStore MemoryIndex DecisionLog com atualização concorrente explícita.',
'src/cain/research/objects.py':'CAS local hash sha256; staging flush fsync antes metadata; hardlink publicação exclusiva; órfãos possíveis; no_links e safe_open.',
'src/cain/research/bundle_backup.py':'Reachable objects mode=ro e validações archives/reservations/projection, cópia CAS verificada.',
'src/cain/research/service.py':'Política versions1/2/3; scopes user/project/collection; autorização produtor e receptor; namespace+source+revision hashes, conflitos duráveis, raw autoritativo e projeções; query escreve queries; recall reautoriza; backup/restore exclusivos.',
'src/cain/research/workflows.py':'Workflow19 steps6, fingerprint e modelo fixados; aprovação generation, lease600seg; etapas e tentativas gravadas; abstain operador conserva falha; contagem modelo só receipts concluídos.',
'src/cain/settings.py':'cain.toml discovery cwd ou bundled; overridesCAIN_DB/PROVIDER/MODEL/OLLAMA_URL; schema rejectsunknowns; validates modelo endpoint bytes seed temperature.',
'src/cain/workspace.py':'Projetos ownership; arquivos imutáveis hashes eUUID; run_receipts processing/ready/failed; restores sem geração; ui_turn idempotente e feedback sem alteração fatos.',
'src/cain/providers.py':'Fake/Ollama factory; embeddings tags digest verificado, se modo hybrid; importa sem I/O mas factory pode acessar rede.',
'src/cain/profile_answers.py':'Respostas perfil determinísticas para perguntas estreitas; impede perguntas documentais.',
'src/cain/research/coverage.py':'Snapshot eBundle contados separados, workflow snapshotsonly; counts não experimentos; fingerprintpolicy.',
'src/cain/research/diagnostics.py':'Derivação experimental structural-counts/1 gera records persistidos, opt-in; limites1000 metadata entities; reautoriza e invalida identity/code/policy.'},
'stocks-predictor':{
'stocks_predictor/operations.py':'CLI init/inspect/ingest/snapshot/restore/profile/evidence/simulate-selected/external, entrada JSON strict dupkeys/finite; lock error retryable; sem broker.',
'stocks_predictor/operational_store.py':'WAL/application_id/schema1 exato, appendonly triggers, BEGINIMMEDIATE, archive hash, consistentinspect snapshot/restore novos dirs incomplete receipts.',
'stocks_predictor/ecosystem_plugin.py':'PluginV1 healthWAITING capabilities scientificDISCOVERY_INCONCLUSIVE economicNO_GO capitalFORBIDDEN constantes; não consulta DB.',
'stocks_predictor/economic_gate.py':'Normal approximation lower mean-zSEM, maturity responsabilidade caller; HOLD/REBALANCE com capitalfalse; mínimos e finitechecks.',
'stocks_predictor/research_profile.py':'Decimal inputs completeness, reserva custos/time opportunity separados, sem confirmar lucro capitalfalse.',
'stocks_predictor/temporal_evidence.py':'DatedOutcome chronology decision<matured<=observed eobserved<asof; duplicados/future rejeitados, não certifica timestamps/independência.',
'stocks_predictor/execution.py':'D+1 estritamente posterior, custos lados; turnover por conjuntos ou pesos; primitive requer série ordenada caller.',
'stocks_predictor/portfolio.py':'Seleção quintil top/bottom equiponderada, inversevol e doublefilter interseção; não arbitra execução.',
'stocks_predictor/returns.py':'Monthend e retorno closeclose, assume dates ordenado e positivos.',
'stocks_predictor/validation.py':'ISOday canonical epositiveinteger typebool rejeitado.',
'stocks_predictor/universe.py':'Liquidez janela calendário antesasof, missing volumezero, quarentena resolutiontime; ticker4prefix heurística emissor, snapshotsconflitos não sobrescrevem.',
'stocks_predictor/dataset_selection.py':'Sources explícitas únicas ecutoffobserved, read snapshot eviewmemory, hash selection, eventoscorp explícitos simulateselected sem verdict.',
'stocks_predictor/source_catalog.py':'Source_id inclui payloadhash publisherdatasetversionpolicy; sourceversion declarada changedpayloadfail; local archive snapshotbeforeparse eSavepoint.',
'stocks_predictor/factor.py':'Momentum252skip21, realizedvol, preço cru×shares valor; legacy embargoestimado para julgadas, accruals/EP/BM current delega cvm_pit; Revenuegrowthgap anual não verifica12m.',
'stocks_predictor/cotahist.py':'245chars parser positional,fatcot>0 ISOdate, spot010/BDI02; malformedskip contabilizado legacy, strictcatalogaborta; batches1000 conflitos bytes, Savepoint rollback.',
'stocks_predictor/trials_gate.py':'Judge positivo plantado econtrole nulo; fingerprintharness obrigatório trialnova; preserva sharpeexisting; DSRstrict ICpositive+DSRthreshold+deflationapplied eextra_failures.',
'stocks_predictor/rj_families.py':'9 métricas registry, contemporaneousvolume descriptiveonly,8 predictive; ownership/trigger knownat; point-in-time lookbacks e missingNone.',
'stocks_predictor/rj_families_next.py':'Cinco famílias nextgen separadas colisãoforbidden; maxlottery/issuance/retailmigration/Altman/CHS; retail refdate não comprova publicação.',
'stocks_predictor/rj_judge.py':'Umaobservação/company,bootstrapcluster,permutation plusone, BH-FDR predictiveonly; categoricalCramersV; LOCO é influência, não predição.',
'stocks_predictor/rj_judge_robust.py':'JointmaxT sharedperm identicalcompanieslabels; aliasromanowolf_stepdown chama jointmaxT; haircut0.36 heurístico, sem OOSreal.',
'stocks_predictor/rj_outcomes.py':'Rally marketadjusted multiplicativo, forwardwindow; walkforwardordered se reconhece datas; genericfit/score supplied.',
'stocks_predictor/rj_pipeline.py':'Universo humanoapproved, firstcausalcandidateprimary; censored/nocandidate/excluded separados;ownershipNone por cobertura; secundarios repetidos bloqueiaminference; persistoverwrites por tickertrough/asof sem run_id.',
'stocks_predictor/rj_power.py':'Poder simulado sob labels pareadas famílias,predictiveFDR, syntheticplanted gaussian; MDEgrid não poder empírico.'}}
for project,ns in notes.items():
 index=json.loads(study.read(project,study.ROOT/'evidencias'/project/'source-index.json'))
 coverage=[{'path':i['path'],'mechanically_read':True,'depth':'revisado semanticamente' if i['path'] in ns else 'leitura mecânica e índice; aprofundamento pendente','notes':ns.get(i['path'],''),'lines':i['lines']} for i in index]
 study.save('evidencias/'+project+'/coverage.json',coverage);study.save('evidencias/'+project+'/module-notes.json',ns)
 study.log(project,study.ROOT,'Progresso salvo por módulo; revisão semântica vs leitura mecânica diferenciada',0,str(len(ns))+' módulos com notas semânticas',limits='Pendente restante código próprio/fixtures/scripts; não declarar integral',artifacts=project+'/coverage.json;'+project+'/module-notes.json')
