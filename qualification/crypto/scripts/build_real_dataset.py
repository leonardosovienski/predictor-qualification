"""crypto / fase science: dataset real (Binance USDⓈ-M públicos) para o runtime Windows.

Congelado em FROZEN_PARAMETERS.json → real_dataset_windows. D-16 pendente: estes dados
NÃO vão para o repositório público nem para o Linux/Actions; ficam só em
C:\\Cripto\\qualificacao\\data (regra local do Cripto), com sha256 origem → cópia.

Passos:
  1. baixa os zips mensais/diários de klines 1d e fundingRate do BTCUSDT e o .CHECKSUM
     publicado de cada um; confere o sha256 do zip contra o .CHECKSUM (falha fechada);
  2. grava MANIFEST.json (url, sha256 publicado, sha256 da cópia, bytes, baixado_em);
  3. deriva observações semanais não sobrepostas (abertura de segunda 00:00 UTC →
     abertura da segunda seguinte), funding = taxa vigente na abertura (fundingTime 00:00);
     observed_at = available_at = fim da semana (fechamento conhecido nesse instante);
  4. escreve os objetos de dataset (in-sample até o cutoff; canário pós-cutoff) e imprime
     os sha256.

Uso: python build_real_dataset.py <dir_destino>
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

BASE = "https://data.binance.vision/data/futures/um"
SYMBOL = "BTCUSDT"
IN_SAMPLE_START = datetime(2025, 9, 1, tzinfo=UTC)
CUTOFF = datetime(2026, 8, 31, tzinfo=UTC)
CANARY_END = datetime(2026, 9, 21, tzinfo=UTC)
CANARY = "FUTURE_CANARY_CRYPTO_001"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "cripto-qualification/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def monthly(kind: str, year: int, month: int) -> str:
    if kind == "klines":
        return f"{BASE}/monthly/klines/{SYMBOL}/1d/{SYMBOL}-1d-{year}-{month:02d}.zip"
    return f"{BASE}/monthly/fundingRate/{SYMBOL}/{SYMBOL}-fundingRate-{year}-{month:02d}.zip"


def daily_klines(day: date) -> str:
    return f"{BASE}/daily/klines/{SYMBOL}/1d/{SYMBOL}-1d-{day.isoformat()}.zip"


def download(url: str, root: Path, manifest: list) -> bytes:
    name = url.rsplit("/", 1)[1]
    target = root / "raw" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    published = fetch(url + ".CHECKSUM").decode().split()[0].lower()
    raw = target.read_bytes() if target.exists() else fetch(url)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != published:
        raise SystemExit(f"CHECKSUM divergente: {url} publicado={published} obtido={digest}")
    if not target.exists():
        target.write_bytes(raw)
    manifest.append({"url": url, "published_sha256": published, "copy": str(target), "copy_sha256": digest,
                     "bytes": len(raw), "downloaded_at": datetime.now(UTC).isoformat(timespec="seconds")})
    return raw


def rows_from_zip(raw: bytes) -> list[list[str]]:
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        (member,) = archive.namelist()
        text = archive.read(member).decode()
    rows = [r for r in csv.reader(text.splitlines()) if r]
    return [r for r in rows if r[0][:1].isdigit()]  # descarta cabeçalho quando existe


def z(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def main() -> None:
    root = Path(sys.argv[1])
    root.mkdir(parents=True, exist_ok=True)
    manifest: list = []
    opens: dict[date, float] = {}
    funding: dict[datetime, float] = {}
    months = [(2025, m) for m in range(9, 13)] + [(2026, m) for m in range(1, 9)]
    for year, month in months:
        for row in rows_from_zip(download(monthly("klines", year, month), root, manifest)):
            opened = datetime.fromtimestamp(int(row[0]) / 1000, tz=UTC)
            opens[opened.date()] = float(row[1])
        for row in rows_from_zip(download(monthly("funding", year, month), root, manifest)):
            funding[datetime.fromtimestamp(int(row[0]) // 1000, tz=UTC)] = float(row[2])
    day = date(2026, 9, 1)
    while day <= CANARY_END.date():
        for row in rows_from_zip(download(daily_klines(day), root, manifest)):
            opened = datetime.fromtimestamp(int(row[0]) / 1000, tz=UTC)
            opens[opened.date()] = float(row[1])
        day += timedelta(days=1)
    # funding de setembro/2026 (canário) vem do arquivo mensal quando publicado; senão fica sem canário de funding
    try:
        for row in rows_from_zip(download(monthly("funding", 2026, 9), root, manifest)):
            funding[datetime.fromtimestamp(int(row[0]) // 1000, tz=UTC)] = float(row[2])
    except Exception as exc:  # noqa: BLE001 - registrado no manifesto
        manifest.append({"url": monthly("funding", 2026, 9), "unavailable": type(exc).__name__})

    def weeks(start: datetime, end: datetime, *, missing_funding: float | None = None) -> list[dict]:
        out, current = [], start
        while current + timedelta(days=7) <= end:
            nxt = current + timedelta(days=7)
            if current.date() not in opens or nxt.date() not in opens:
                raise SystemExit(f"abertura ausente em {current.date()} ou {nxt.date()}")
            rate = funding.get(current, missing_funding)
            if rate is None:
                raise SystemExit(f"funding ausente em {current}")
            out.append({"observed_at": z(nxt), "available_at": z(nxt),
                        "gross_return": opens[nxt.date()] / opens[current.date()] - 1.0,
                        "funding_rate": rate})
            current = nxt
        return out

    in_sample = weeks(IN_SAMPLE_START, CUTOFF)
    dataset = {"dataset_version": "binance-um-btcusdt-weekly-2025-09-01_2026-08-31-v1", "data_cutoff": z(CUTOFF),
               "label_start": in_sample[0]["observed_at"], "label_end": in_sample[-1]["available_at"],
               "source": "data.binance.vision futures/um klines 1d + fundingRate (MANIFEST.json)",
               "rows": in_sample}
    objects = {"dataset-real-in-sample.json": dataset}
    try:
        # O canário existe para ser recusado: funding de set/2026 ainda não publicado → 0.0 declarado.
        post = weeks(CUTOFF, CANARY_END, missing_funding=0.0)
        canary = dict(dataset, dataset_version="binance-um-btcusdt-weekly-canary-v1",
                      canary={"token": CANARY, "rows_after_cutoff": len(post),
                              "funding_policy": "funding pós-cutoff ausente na fonte na coleta; linhas canário usam 0.0"},
                      rows=in_sample + post,
                      label_end=post[-1]["available_at"])
        objects["dataset-real-future-canary.json"] = canary
    except SystemExit as exc:
        manifest.append({"canary_dataset": "not built", "reason": str(exc)})
    out = {}
    for name, value in objects.items():
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
        (root / name).write_bytes(raw)
        out[name] = {"sha256": hashlib.sha256(raw).hexdigest(), "rows": len(value["rows"])}
    (root / "MANIFEST.json").write_text(json.dumps({"files": manifest, "objects": out}, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
