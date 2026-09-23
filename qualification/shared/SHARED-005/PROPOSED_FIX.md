# SHARED-005 — proposta de correção (predictor-ops, NÃO aplicada)

`predictor-ops` está congelado na Etapa A. Esta é só a proposta; aplicar exige decisão
do dono → release nova do Ops → `STACK_BASELINE_V1.<n>` → C14 nas três missões.

## Defeito

`src/predictor_ops/runtime.py`, `_mutation_guard` (predictor-ops 4.2.1, commit `7bd99eb`):

```python
    with path.open("a+b") as handle:
        if path.stat().st_size == 0:
            handle.write(b"0")
            handle.flush()          # ← PermissionError no Windows se outro processo já travou o byte 0
        deadline = time.monotonic() + 30
        while True:
            try:
                ...msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
```

Dois processos veem o arquivo vazio. O primeiro escreve e trava o byte 0. O segundo
escreve e dá `flush` sobre o byte travado. No Windows o lock de `msvcrt` é obrigatório, e
isso levanta `PermissionError` fora do laço de retry. A exceção escapa de
`LocalBackend.acquire` e de `run_job`.

## Correção proposta

Tratar a inicialização como idempotente e tolerar a corrida. Só um dos processos
precisa gravar o byte, e o travamento funciona mesmo além do EOF.

```diff
     with path.open("a+b") as handle:
         if path.stat().st_size == 0:
-            handle.write(b"0")
-            handle.flush()
+            try:
+                handle.write(b"0")
+                handle.flush()
+            except PermissionError:
+                # Outro processo inicializou a guarda e já tem o byte 0 travado
+                # (lock obrigatório do Windows). O laço abaixo espera por ele.
+                pass
         deadline = time.monotonic() + 30
```

Detalhe: se o `flush` falhar, o buffer do `BufferedRandom` ainda guarda o byte e tenta
gravá-lo de novo no `close()`. Uma alternativa mais limpa é inicializar a guarda com
`os.open(path, O_CREAT | O_EXCL | O_WRONLY)` (quem cria escreve o byte; quem perde
recebe `FileExistsError`) antes de abrir em `a+b`.

## Teste que deve acompanhar

- Determinístico (Windows): um processo trava o byte 0 de uma guarda **vazia**, e outro
  entra em `_mutation_guard`. Deve esperar e entrar depois da liberação, sem
  `PermissionError`. É o caso A de `qualification/crypto/scripts/ops_lock_guard_ab.py`,
  que hoje levanta `PermissionError` 3/3.
- `test_local_lock_has_one_winner_across_processes` em laço (≥ 50×) no `windows-latest`.
