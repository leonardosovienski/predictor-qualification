# Caracterização preliminar — predictor-qualification

Salva antes do confronto com README, COMMON_QUALIFICATION_CORE, decisões ou relatórios. Base: scripts Python/shell/PowerShell e workflows lidos nesta investigação. O Anexo A foi visto ao ler o pedido, mas não usado como fonte destas conclusões.

A árvore não apresenta pyproject.toml ou uv.lock na listagem Git examinada. É uma coleção de scripts e arquivos de evidência, acionados por argumentos posicionais, argparse e Actions, e não um pacote installável demonstrado. Scripts demandam Python com tomllib; attest.py usa jsonschema; sondas dependem de predictor_ops e do domínio instalado.

collect_stack_baseline.py lê clones de sete projetos, Git, manifests, locks e API via gh; grava JSON/log. cleanroom_baseline.py clona fontes, resolve lock, instala wheels, cria variantes published/head_build, roda testes fora dos pacotes e compara arquivos das wheels. O guard registra módulos fora do site-packages, mas não muda o exitstatus da suíte. Caminhos e integrações fazem esses executores potencialmente mutáveis e inadequados ao original.

attest.py constrói documentos a partir de GATES/FINDINGS, SHA256 das evidências, core e baseline. check valida schema, conta findings, compara hashes de gate e combina statuses; não reexecuta domínio nem avalia verdade científica. write recusa sobrescrever. d16_finalize.py exige decisão D-16 APPROVED, cruza target com env.log e resume evidências para gates; move attestation anterior via git mv e grava GATES.

evidence_numbers.py recomputa contagens de XML/log/JSONL e grava EVIDENCE_NUMBERS; summarize_cleanroom.py lê facts/logs e imprime resumo. Ambos descrevem runs históricos: executá-los agora não é repetir testes de domínio. analyze_ops_failure.py distingue setup_failed mas algumas agregações excluem setup_failed do denominador; isto deve permanecer explícito.

Fluxo Crypto: build_real_dataset baixa Binance com checksum; real_env cria CAS/policy/vetores; e2e_runtime aciona CLI instalada, relê resultados e cruza admission/journal/Core/Ops; science_real gera controles e métricas; soak intercala duplicatas/restarts/faults e confere effects/store. Dados semanais e retornos de sinal long fixo são sondas técnicas; não demonstram capacidade preditiva de uma estratégia. science_real.separated_with_ci verifica apenas limites inferiores não nulos, um critério parcial frente à promessa de IC completo.

Persistência própria: JSON, JSONL, XML e texto versionados; os scripts de teste leem SQLite criado por domínios em runtime. Não há DDL próprio observado nos 22 Python, 13 shell/PowerShell e 6 workflows examinados. Ausência limitada a esse espaço.

Governança implementada: capital_permission=False e training_started=False nos construtores de atestados/baselines; guard D-16 é local ao executor. Não confundir QUALIFIED operacional com edge ou autorização de capital. Alguns shells sem errexit anotam erros intermediários e podem terminar com exit0; interpretar logs/artifacts, não apenas job verde.
