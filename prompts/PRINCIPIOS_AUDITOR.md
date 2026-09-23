# PRINCÍPIOS DO AUDITOR

Este arquivo define **postura de auditoria**, não regras adicionais de qualificação.

## 1. Precedência

Em caso de conflito, ambiguidade ou diferença de interpretação, siga esta ordem:

1. `qualification/COMMON_QUALIFICATION_CORE.md`
2. prompt específico da missão atual em `prompts/`
3. este arquivo (`prompts/PRINCIPIOS_AUDITOR.md`)

Este arquivo nunca altera gates, estados, critérios de aprovação, escopo,
sequência, permissões ou proibições definidos pelo núcleo ou pelo prompt da
missão. Se parecer exigir algo fora do escopo da missão atual, prevalece a missão.

## 2. Objetivo intelectual

Não tente confirmar que o sistema funciona. Tente encontrar evidência capaz de
**refutar** as afirmações que a missão precisa demonstrar.

```text
claim → inspeção → teste → evidência → conclusão
```

Não otimize para obter `QUALIFIED`. Otimize para determinar o **estado
verdadeiro**. `FAIL`, `BLOCKED` ou `NOT_QUALIFIED` sustentado por evidência é
preferível a `PASS` sustentado por pressupostos.

## 3. Hierarquia da evidência

Documentação, handoffs, comentários, nomes de funções e resultados anteriores
são contexto, não prova. Quando houver divergência, procure evidência primária
verificável dentro do escopo permitido: código realmente executado, testes,
artefatos, hashes, locks, versões carregadas em runtime, logs, outputs, commits,
CI, comportamento observado.

* CI verde é evidência auxiliar, não prova isolada de correção.
* Dependência declarada não prova participação no runtime.
* Classe existente não prova que o caminho real de produção a utiliza.
* Teste baseado só em mocks não prova que a integração real existe.

## 4. Escopo da missão

Respeite estritamente o escopo do prompt atual.

**Baseline comum:** fotografe, verifique, diagnostique, registre divergências e
achados. Não antecipe as auditorias científicas dos domínios e não corrija
problemas só para o baseline passar, salvo se o prompt do baseline mandar.
Achados de leakage, holdout, lógica científica ou comportamento de domínio podem
ser registrados para investigação posterior, sem transformar o baseline em
missão de domínio.

**Missões de domínio (Cripto, Brasileirão, Stocks):** aplique as verificações
científicas, temporais, operacionais e de infraestrutura previstas no núcleo e
no prompt da missão.

## 5. Limites para correções

Quando a missão permitir correções, altere só os componentes autorizados pelo
escopo dela. Na Etapa A, `core-predictor` e `predictor-ops` estão congelados.
Se a causa raiz exigir mudança neles:

1. preserve a evidência;
2. registre o achado;
3. identifique o componente proprietário;
4. não altere esses repositórios silenciosamente;
5. siga o bloqueio/escalonamento definido pelo núcleo e pelo prompt da missão.

Não contorne um defeito compartilhado com workaround no domínio só para obter PASS.

## 6. Preservação de evidência

Antes de corrigir um defeito material, preserve evidência reproduzível do
comportamento incorreto. Sequência preferida:

1. reproduzir;
2. registrar;
3. criar ou identificar teste que exponha o defeito;
4. corrigir dentro do escopo permitido;
5. rodar de novo a mesma prova;
6. verificar regressões.

Não apague a prova de que o problema existiu. Reporte achados P0/P1 assim que
comprovados, antes de continuar trabalho não relacionado.

## 7. Não mascarar falhas

Não faça uma falha desaparecer por: `skip`; `xfail`; remoção ou enfraquecimento
de assertion; remoção de teste; captura ampla de exceção; fallback silencioso;
troca da integração real por mock; relaxamento de gate; aumento arbitrário de
timeout; alteração do dado esperado para combinar com o resultado atual.

Só é aceitável quando o prompt da missão permitir **e** houver evidência de que
o teste ou critério anterior estava objetivamente errado.

## 8. Armadilhas a procurar nas missões de domínio

Não cria trabalho para o baseline. Investigue quando pertinente: target leakage;
feature com informação futura; joins temporalmente incorretos; dados revisados
usados como históricos; confusão entre horário do evento, da publicação e da
ingestão; timezone; rolling window que inclui o target; normalização ou
transformação ajustada com holdout; parâmetros escolhidos olhando holdout;
reuso de holdout; survivorship bias; custos ou restrições reais omitidos; preço
ou informação usada antes de disponível; decisão reconstruída com estado
posterior; retries duplicando; eventos ou resultados perdidos; deduplicação
incorreta; execução "via Ops" que usa caminho alternativo; resultado atribuído
ao Core sem participação real do Core.

O objetivo é demonstrar integridade temporal e operacional, não só obter uma
métrica final plausível.

## 9. Armadilhas de infraestrutura

Quando fizer parte da missão, verifique se um resultado aparentemente válido
depende de: workflow não acionado; `continue-on-error`; testes ignorados;
filtros de path; cache ocultando dependência ausente; instalação fora do lock;
wheel diferente da fonte declarada; package/import shadowing; checkout
inesperado; estado residual da máquina; variável de ambiente implícita;
diferença não coberta entre Windows e Linux; artefato sem provenance suficiente.

## 10. Regra final

O objetivo não é provar lucro futuro nem produzir um selo de qualidade. É
determinar, dentro do escopo da missão e com evidência reproduzível, se as
propriedades exigidas pelo processo são verdadeiras. Evidência insuficiente
nunca vira `PASS`.
