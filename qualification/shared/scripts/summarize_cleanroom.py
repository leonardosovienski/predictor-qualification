"""SHARED-002: resume os fatos brutos do cleanroom-baseline (C20).

Lê <run_dir>/cleanroom-<repo>/cleanroom_facts.json (artefatos do run, sem edição)
e imprime as tabelas usadas no CLEANROOM_REPORT.md. Nenhum número do relatório
vem de outro lugar.
Uso: python summarize_cleanroom.py <run_dir>   (formato do plano V2)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ORDER = ["cain", "ecosystem-predictor", "core-predictor", "predictor-ops", "brasileirao-predictor",
         "cripto-predictor", "stocks-predictor"]


def ok(step: dict | None) -> str:
    if not step:
        return "—"
    return "OK" if step.get("exit") == 0 else f"FAIL({step.get('exit')})"


def counts(c: dict | None) -> str:
    if not c:
        return "sem junit"
    return f"{c['passed']} passed / {c['failures']} failed / {c['errors']} errors / {c['skipped']} skipped (de {c['tests']})"


def main(run_dir: str) -> None:
    run = Path(run_dir)
    facts = {r: json.loads((run / f"cleanroom-{r}" / "cleanroom_facts.json").read_text(encoding="utf-8"))
             for r in ORDER if (run / f"cleanroom-{r}" / "cleanroom_facts.json").exists()}
    envs = {json.dumps(f["environment"], sort_keys=True) for f in facts.values()}
    print("## Ambiente")
    for e in sorted(envs):
        print(e)
    print("\n## Clone, lock e download")
    print("| repo | SHA | HEAD=plano | limpo | sparse sem pacotes | uv lock --check | export | reqs | entradas locais descartadas | wheels publicadas sha256 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r, f in facts.items():
        dl = f["published_download"]
        dl_ok = f"{sum(1 for d in dl if d.get('match'))}/{len(dl)}"
        print(f"| {r} | `{f['sha'][:8]}` | {f['head_matches_plan']} | {f['clone_clean']} | "
              f"{all(f['tree_strip_paths_absent'].values())} | {ok(f['steps']['uv_lock_check'])} | "
              f"{ok(f['steps']['uv_export'])} | {f['lock_export']['requirements']} | "
              f"{len(f['lock_export']['dropped_local_entries'])} | {dl_ok} |")
    for variant in ("published", "head_build"):
        print(f"\n## Variante `{variant}`")
        print("| repo | instala lock | instala próprias | pip check | módulos do stack fora do site-packages (introspecção) | console scripts --help | plugins | pré-teste | pytest exit | contagem (junit) | guard: módulos fora do site-packages |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        for r, f in facts.items():
            v = f["variants"][variant]
            intro = v.get("introspect", {})
            mods = intro.get("modules", {})
            bad_mods = [m for m, d in mods.items() if not d.get("in_site_packages")]
            cs = v.get("console_scripts", [])
            cs_ok = f"{sum(1 for c in cs if c['exit'] == 0)}/{len(cs)}" if cs else "nenhum"
            pl = intro.get("plugins", [])
            pl_ok = f"{sum(1 for p in pl if p['load'] == 'OK')}/{len(pl)}" if pl else "nenhum"
            pre = [v[k] for k in v if k.startswith("pre_test_")]
            pre_s = ",".join(ok(p) for p in pre) or "—"
            for s in v["suites"]:
                g = s.get("guard") or {}
                guard = len(g.get("outside_site_packages", [])) if g else "sem guard"
                print(f"| {r} `{' '.join(s['paths'])}` | {ok(v.get('install_lock'))} | {ok(v.get('install_own'))} | "
                      f"{ok(v.get('pip_check'))} | {','.join(bad_mods) or '0'} | {cs_ok} | {pl_ok} | {pre_s} | "
                      f"{s['pytest']['exit']} | {counts(s.get('counts'))} | {guard} |")
    print("\n## Detalhes")
    for r, f in facts.items():
        print(f"\n### {r}")
        print("dropped:", f["lock_export"]["dropped_local_entries"])
        print("stack no lock exportado:", f["lock_export"]["stack_entries"])
        for d in f["published_vs_head_build"]:
            if d.get("head_build") is None:
                print(f"drift {d['dist']}: sem wheel do commit")
                continue
            print(f"drift {d['dist']}: {d['published']} x {d['head_build']}: iguais={d['identical_files']} "
                  f"diferentes={len(d['different_files'])} só_publicada={len(d['only_published'])} "
                  f"só_commit={len(d['only_head_build'])}")
            print("   diferentes:", d["different_files"][:15])
            print("   só_publicada:", d["only_published"][:10])
            print("   só_commit:", d["only_head_build"][:10])
        for variant in ("published", "head_build"):
            v = f["variants"][variant]
            print(f"[{variant}] own wheels:", v.get("own_wheels"))
            print(f"[{variant}] pip check:", v.get("pip_check_output"))
            intro = v.get("introspect", {})
            for name, d in sorted(intro.get("dists", {}).items()):
                du = d.get("direct_url") or {}
                print(f"[{variant}] dist {name} {d['version']} <- {du.get('url')}")
            for m, d in sorted(intro.get("modules", {}).items()):
                if not d.get("in_site_packages"):
                    print(f"[{variant}] módulo {m}: {d}")
            for c in v.get("console_scripts", []):
                print(f"[{variant}] script {c['name']} --help -> {c['exit']}")
            for p in intro.get("plugins", []):
                print(f"[{variant}] plugin {p['name']} -> {p['load']}")
            for s in v["suites"]:
                tag = f"[{variant} {' '.join(s['paths'])}]"
                print(f"{tag} pytest: {s.get('summary_line')}")
                failed = (s.get("counts") or {}).get("failed_ids", [])
                print(f"{tag} falhas ({len(failed)}):", failed[:40])
                g = s.get("guard") or {}
                print(f"{tag} guard: importados={g.get('stack_modules_imported')} "
                      f"top={g.get('top_levels_imported')} fora={g.get('outside_site_packages', [])[:5]}")
                # Assinaturas de erro (linhas 'E   ' do log bruto, caminhos do runner normalizados)
                raw = (run / f"cleanroom-{r}" / s["pytest"]["log"]).read_text(encoding="utf-8", errors="replace")
                sigs: dict[str, int] = {}
                for line in raw.splitlines():
                    if line.startswith("E   ") and ("Error" in line or "Failed:" in line or "assert" in line):
                        norm = re.sub(r"/home/runner/work/_temp/cleanroom/[^/]+/(tree|venv-[a-z_]+)/", r"<\1>/", line)
                        norm = re.sub(r"[0-9a-f]{12,}", "<hex>", norm).strip()[:160]
                        sigs[norm] = sigs.get(norm, 0) + 1
                for sig, n in sorted(sigs.items(), key=lambda x: -x[1])[:12]:
                    print(f"{tag}   {n:4d}  {sig}")


if __name__ == "__main__":
    main(sys.argv[1])
