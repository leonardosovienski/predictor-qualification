# Scripts, avaliação e CI CAIN/Stocks

Escopo: CAIN HEAD original e configurações preexistentes; testes descritos são ET-SRC quando não indicado ET-HIST. Nenhum destes scripts foi executado nos originais. Hashs originais e leituras em REGISTRO.log; notas estruturadas em evidencias/cain/root-operations-notes.json.

## CI Linux histórico

prepare_ci restaura overlays hashados em clones; restore_candidate confina caminhos e testa HEAD/status. Supply usa file_hashes, Completion overlay_files. Não executados nesta investigação.

## run_linux

Linux não root e filesystem nativo; matriz Supply3.13–3.14, Completion3.11–3.14, integrado apenas>=3.13. Constrói wheels e instala fora checkout; versão CAIN fixa0.4.7 representa candidato histórico, não HEAD0.4.12.

## POSIX ET-SRC

Symlink/FIFO, race troca diretório, revogação sem observar blobs, chmod, falhas mkdir/write/fsync/link/DB, ordem syscall antes commit, hardlinks não compartilhados. Orphans esperados após falhas tardias; testes preparados não ETRUN Windows.

## Exportadores reais ET-SRC

linux_real_export hashes relatórios públicos e charter/trials/atestados preexistentes; preserva grants mudando raízes descartáveis; Snapshot/bundle query+offlinebackup/materialize. Arquivo real não transforma relatório em experimento científico reproduzido.

## finite_runner

Sem shell/modelos, CLI bundle por args declarados; lock exclusive x e checkpoint identidade código/runner/policy/corpus/config. Cap outputs/bytes/tempo/casos/disco, SIGINT/SIGTERM+terminate/kill child; erro preservado LAST_FAILURE. Oráculo status/counts, não entailment; retomada exige mesmos bytes. Estatística RSS UNKNOWN.

## start-cain.ps1

Cria venv/instalação se ausente; lê configuração local sem imprimir valores; pode iniciar Ollama eAPI, grava logs/PID; loopback health exige service+api_contract. Não foi executado original nem cópia para não iniciar serviço compartilhado.

## cain.toml

Ollama qwen3.5:4b; embedding qwen3-embedding:0.6b e digest; budgets/seed/temperature explícitos; routingLLM true e hybrid. Configuração observada não modelo instalado/ativo.

## L0/API/hybrid

L0 baseline documental e histórico recebem mesmo filtroID, budget6000; utilidadeINCONCLUSIVE/human_timeNone. verify-api sintético exige checks mecânicos, sourcehash/offset e preferência/reopen, sem browser ou semântica. verify-hybrid6fontes6queries5positivas, ausência excluída métricas; cache/ordem confundem latência; --execute obrigatória.

## selection-comparison

Origem SQLite mode=ro backup para isolado, audit hook bloqueia sockets/subprocess/escritas fora root; Timer30s. sourcehash+JSONpointer+quoteoffset compara campo literal; não sandboxgeral nem juízo semântico. Resume verifica receiptSHA e identidade sem repetir efeito.

## Catálogo

prepare_hypothesis_catalog pinsha origens, decodifica JSON sem duplicates/nonfinite, spansUnicode exact, chunkdocument12000 e publications40; clocks somente explícitos timezone; publica fora source exclusive e dedupbytes. Occurrences não hipótesesúnicas, curadoria não producerautenticado.

## Verificadores IA

agent_capabilities e grounded_workflows iniciam ResearchService em db fornecido antes backup: podem migrar origem, não usar original. individual_models usa mode=ro. Protocolosdev, exactcitations/literalstate/embedding pair não métricasfactuais; streams/red64x64 probes restritos. Exceções conservadas; completed pode coexistir erros nos registros.

## Entrega/cobertura

verify_research_delivery/inspection usam contagensfixas15/1/3 e offline recuperação; query registra receipts. verify_project_coverage pagina classes separadas, limitesfiles32MB, roots explicitados, declara filenameinventory não completude e currenttruth nãoestablished. Política hash inalterada não bloqueia writesDB.

## Wheel

verify_wheel tempvenv install--no-index vendor, -I e importorigins em sys.prefix, recursosweb/contracts, Workspace CRUD e pipcheck. ET-SRC não execuçãoagora, não provaverdadeLLM.

## Stocks CI

uv0.12.1, locked extras3.13/3.14,doctor/lint/type/R6R7R8/handoffs/tests/buildtwice+wheeloutside+250kload; secret scan controles sintéticos. CI-export stdlib3.12–3.14 e contractsSHAfixado. Matriz export não prova runtimeStocks compat3.12.

## Stocks CI remoto ET-HIST

Run36719558172 commit3ec7e413bdcaedccfc1c2ed65c2822dddccb5cee ambosquality3.13/3.14 falham Current R8 operational evidence identities. Tests/build/wheels seguintes skipped; secrets success. Metadadosjobs confirmam passo, causa internaNV semlog bruto/coorteprivada. AnexoA5 parcialmente confirmado.