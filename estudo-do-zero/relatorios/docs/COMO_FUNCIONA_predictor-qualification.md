# Como funciona predictor-qualification

Fonte local e limites no INVENTARIO. Abaixo nós OD de scripts/esquemas; BLOCKED/ABORTED do diagrama de estados são DD do núcleo, explicitamente marcados. Nenhum diagrama é observação de serviço ativo.

## qual-componentes

```mermaid
flowchart LR
 Plano[Planos JSON] --> Coletor[collect_stack_baseline]
 Git[Git e API publica] --> Coletor
 Coletor --> Baseline[Baseline JSON e logs]
 Plano --> Cleanroom[cleanroom_baseline]
 Cleanroom --> Facts[Facts JUnit e guard]
 Gates[GATES e FINDINGS] --> Attest[attest build check]
 Arquivos[Evidencias por hash] --> Attest
 Attest --> Atestado[Atestado JSON]
```


## qual-sequencia-coleta

```mermaid
sequenceDiagram
 participant Dono
 participant Coletor as collect_stack_baseline
 participant Git
 participant API as GitHub API
 participant Arquivos
 Dono->>Coletor: argumentos e raizes configuradas
 Coletor->>Git: HEAD status manifests locks
 Coletor->>API: runs releases assets publicos
 Coletor->>Coletor: comparar identidades e hashes
 Coletor->>Arquivos: baseline JSON e log
```


## qual-sequencia-atestado

```mermaid
sequenceDiagram
 participant CLI
 participant Gates as GATES e FINDINGS
 participant Attest as attest.py
 participant Evidencias
 participant JSON
 CLI->>Attest: partial ou final
 Attest->>Gates: ler estados e findings
 Attest->>Evidencias: verificar existencia e calcular hashes
 Attest->>Attest: schema e check parcial
 alt arquivo novo e check OK
 Attest->>JSON: gravar atestado
 else conflito ou problema
 Attest-->>CLI: erro e recusa escrita
 end
```


## qual-sequencia-runtime

```mermaid
sequenceDiagram
 participant Shell as runtime_cleanroom
 participant Wheel
 participant CLI as cripto-research instalado
 participant Stores as admission journal resultados
 participant Probe as e2e science soak
 Shell->>Wheel: baixar conferir hash instalar
 Probe->>CLI: pedido em novo processo
 CLI->>Stores: processamento e persistencia
 Probe->>CLI: show em novo processo
 Probe->>Stores: conferir ids hashes estado
 Probe-->>Shell: JSON logs exit
```


## qual-estados

```mermaid
stateDiagram-v2
 [*] --> IN_PROGRESS: partial
 IN_PROGRESS --> QUALIFIED: gates PASS e zero bloqueantes
 IN_PROGRESS --> NOT_QUALIFIED: gates FAIL ou findings bloqueantes
 IN_PROGRESS --> BLOCKED: DD nucleo impedimento externo
 [*] --> ABORTED: DD nucleo C0 falhou
 QUALIFIED --> [*]
 NOT_QUALIFIED --> [*]
```


## qual-schema

```mermaid
classDiagram
 class Attestation {
 string common_baseline_id
 string common_core_sha256
 array final_commits
 array final_wheels
 object gates
 object counts
 boolean capital_permission
 string result
 }
 class Gate {
 string status
 array evidence
 }
 class Evidence {
 string file
 string sha256
 }
 Attestation --> Gate
 Gate --> Evidence
```

O contexto do repositório é evidência versionada. As sequências mostram coleta, construção de atestado e prova de runtime; cada execução pode gravar artefatos e por isso exige ambiente independente. O esquema representa objetos JSON, sem banco próprio demonstrado. QUALIFIED combina estados documentais e checks de identidade; não é previsão validada nem capital autorizado.
