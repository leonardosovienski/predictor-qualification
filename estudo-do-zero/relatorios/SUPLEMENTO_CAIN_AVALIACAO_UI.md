# Avaliação e UI CAIN

Fonte primária local. Categoria OD para implementações; INF nos riscos concorrência, efeitos de abort e limites metodológicos. `cain-product-evaluation/2.0` é versão do instrumento de avaliação, não envelope V2 do anexo.

## src/cain/evaluation/functional.py

Seis etapas explícitas preferência/reabertura/correção/outro usuário/busca. Estado, roteamento e contexto enviado são comparados; corpus sintético. CLI exige Ollama; injected-test marcado. subprocesso por etapa; para ao primeiro erro, preserva not_run/raw. Functional success exige todas etapas e checks, porém não certifica resposta/código gerado/forma nem construto científico. Consulta digest backend é observação e pode ser None.

## src/cain/evaluation/functional_worker.py

Lê request JSON, execute_stage, grava result, exit1 quando failed; qualquer execução escreve DB/arquivos.

## src/cain/evaluation/harness.py

Scaffold smoke A prompt fixo, B histórico anterior, C runtime que pode ter exposição sessão corrente: comparação assimétrica documentada no próprio código. Character cap não é tokens. _prepare exist_ok=False, design hashes e bloqueios formais. Blind export randomiza ordem e pseudônimos por cenário; chave privada separada. Pilot Ollama requer ratings independentes; sem geração fake rotulada real.

## src/cain/evaluation/metrics.py

Confusion matrix três agentes mantém unknown em n. Perfil vetor codifica preferência explícita de duas categorias, não aprendizagem latente. Euclidean reduction, cosine finite/nonzero checks e exact Likert agreement; não chance-corrected nem valida construto.

## src/cain/evaluation/quality.py

Dataset 12-16 unique dev/holdout; model input só prompt/context/schema oculta gabarito. _strict_json rejeita NaN/key duplicada; _schema_valid é subconjunto simples object/string/enum, não validador JSONSchema geral. required/forbidden regex e citations only membership não entailment. Sintaxe AST não execução. Error/truncated mantidos attempts/status; rates condicionais completed. Registro hash input/backend/tempo/metadata; ordem um modelo por vez, mesmo shuffled casos; sem vencedor qualidade automático.

## src/cain/evaluation/resources.py

Recursos embarcados no pacote sem fallback checkout; executed_package_bytes hash fonte/deps e metadata version, commit=None. Distinga hash arquivo importado vs package_version declarada; nenhum serviço ativo prova.

## src/cain/evaluation/v2.py

Protocolo de AVALIAÇÃO cain-product-evaluation/2.0 não envelope ResearchTaskV2. local_url restringe loopback HTTP origem sem credentials/path/query. isolate confere DB dedicado, sem sources/urls e runtime sem symlink/junction. prepare cria runtime novo e config transformada. serve proxy127.0.0.1:11436 cap de generations baseado transport completado, API uvicorn normal factory. Request/response em base64+hash, active.json identifica caso; dispatch vs transport diferindo => countNone. Runner só A/C; replayB e browserD separados. Exact/json type/value ou review_required por padrão, sem regex semantic certification. Plan series_only declarado, proxy threaded sem lock atômico de cap => risco concorrência. inference_policy é logada, não vi enforcement no runner que transforma chamadas proibidas em falha automática. Report inclui attempted/not_executed/error/unknown_counts; last answer rubric somente último turn.

## src/cain/evaluation/v2_controls.py

Controles HTTP scope user/project/session/turn expiração20s e canary user/project. Não requests inferência; connection-refusal em porta11439 verifica desocupação e subprocesso CLI QA. Success não prova cancelamento de inferência parcial nem adherence natural language. Config possui paths explícitos e realiza escritas.

## src/cain/evaluation/v2_integrity.py

Real storage/contratos com fixture snapshot e ForbiddenGeneration sentinel nunca invocado. Revisions preservadas e supersession, idempotency/conflito, denial sem novos protectedrecords, workspace boundaries, checkpoint/cancel/revocation; SQLite integrity_check. Catch registra quality fail mas execution completed, distingue eixo. Não mata processo/crash midtransaction.

## src/cain/evaluation/v2_replay.py

Reenvia bytes capturados só caminho C/api/generate do case, hash do input confere; backend CLI não valida local_url explicitamente. diagnostic_overrideTrue, rep1; preserva original response, erro e duração. Não postprocessing/memória nem prova roteamento.

## src/cain/evaluation/v2_research.py

Casos A01/H4 Crypto,A02 Stocks retorno,A03 ClaimBR em QA archive. Attest storage, source_preflight, coverage e até3 advances com approve_generation. Quote offsets equality verificada, semantic_support not_certified. Blocked sources e operational_error registrados; transport/dispatch countNone quando divergem. Não valida significado fontes.

## src/cain/evaluation/v2_utility.py

A12 tarefa JSON sintética duas facts; comparação CAIN API -> hybrid -> structuredlookup mesma fonte autorizada, ordem fixa/cache aquecida. Tempo esforço humano não medido; semanticreview implementingassistant unblinded; não generaliza utilidade. Escreve documento/DB/caches QA.

## src/cain/web/app.js

UI de usuário/project/session/preferências/docs/chat/research. Renderiza via textContent/createTextNode, fences texto sem executar HTML. Filtra arquivos texto256KiB e imagens2MB, client-side limites com servidor necessário. Pending request run_id UUID localStorage, manual resend mesma payload/scope; recovery /runs lê sem LLM. Histórico e pesquisa scope explícito; cancellation job async fora busy, API server precisa permission atual. research generation mostra fonte/quotes/suporte não certificado e abstention; jobs até6 etapas e operatorapprove/recover. Lab streaming provisional tokens NDJSON, abort localcontroller e terminal done/error; cancel request UI não prova provider stopped. Optional WebMCP getprofile/send com mesmos efeitos; user ID seleção não autenticação por si. Não houve teste browser/UI.
