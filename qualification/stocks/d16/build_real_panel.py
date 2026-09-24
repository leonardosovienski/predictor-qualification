"""stocks / D-16: construtor versionado `dados reais públicos → stocks-pit-panel/1` (só stdlib).

Fontes (URL oficial + sha256 fixados em SOURCES.json ANTES da execução; o build confere
cada hash e falha fechado se divergir; nada é versionado nem publicado como artefato, D-11):
  * B3 COTAHIST anual (https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A<ano>.ZIP):
    preços e volume por pregão. Anos fechados são imutáveis; o do ano corrente é um snapshot
    (sha256 e data fixados no SOURCES.json).
  * CVM dados abertos, FCA (https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_<ano>.zip):
    identidade do emissor (código de negociação → CNPJ) com a data de recebimento do documento.
  * B3, eventos acionários por emissor (API pública de "Empresas listadas",
    GetListedSupplementCompany): fatores oficiais de desdobramento, grupamento e bonificação,
    com data de aprovação e "data com".
  * CVM dados abertos, VLMO do ano corrente: só como fonte oficial das coletas COLLECTION_ONLY
    do soak (nunca entra no painel nem em trial).

Regras (congeladas em RULES e repetidas em SOURCES.json; o build recusa divergência):
  * instrumento: mercado à vista (TPMERC 010) e lote-padrão (CODBDI 02), a mesma regra de
    `stocks_predictor.cotahist.is_avista`; só ações e units (ESPECI ON, PN, PNA..PNH, UNT) —
    BDR, ETF, fundos e índices ficam de fora (tipo do instrumento, conhecido na listagem);
  * janela: pregões ≥ 2021-01-04; security_id = ISIN (CODISI);
  * barra: close = PREULT / (100 × FATCOT) (preço por ação), volume_fin = VOLTOT / 100 (R$);
    available_at = próximo dia de semana após o pregão, 00:00 America/Sao_Paulo (03:00Z) —
    COTAHIST = PIT_RECONSTRUCTED, disponível no dia útil seguinte (feriado tratado como útil,
    o que só atrasa a disponibilidade);
  * listagem: listed_on = primeiro pregão com barra na janela (censurado à esquerda para quem
    já negociava), listing_available_at = disponibilidade dessa barra; deslistagem não é
    informada pelo COTAHIST: delisted_on = null e a saída do universo é pela janela de liquidez
    (inatividade), com o retorno medido até a última barra e depois caixa (research_pit.label_close);
  * ticker: evento a cada troca de código de negociação do mesmo ISIN, efetivo no primeiro pregão
    com o código novo e disponível junto com essa barra;
  * emissor (CNPJ): linhas de fca_cia_aberta_valor_mobiliario ligadas ao índice do FCA pelo
    ID_DOC; available_at = DT_RECEB + 1 dia, 00:00 America/Sao_Paulo (regra de
    stocks_predictor.cvm_pit.receipt_dates: data sem hora vale no dia seguinte);
    effective_on = Data_Inicio_Negociacao (ou DT_REFER se vazio); a linha vale para o ISIN que
    usou aquele código até a data de início declarada (Data_Fim_Negociacao não é usada: vem
    errada em algumas FCAs); para o mesmo (ISIN, CNPJ, effective_on) fica o recebimento mais
    antigo. Reserva, só para ISIN sem identidade assim: raiz do ticker → codeCVM da resposta
    oficial da B3 → CNPJ do índice do FCA (CD_CVM), effective_on = listed_on. Classe
    PIT_RECONSTRUCTED;
  * eventos acionários: DESDOBRAMENTO/BONIFICACAO multiplicam as ações por (1 + fator/100),
    GRUPAMENTO por fator; a data ex é o primeiro pregão do ISIN depois da "data com"; o preço
    ajustado de toda barra anterior à data ex entra como REVISÃO da mesma barra (republicação,
    PIT-09), available_at = max(disponibilidade da barra ex, aprovação + 1 dia 00:00 BRT);
    close revisado com 10 algarismos significativos. Proventos em dinheiro, subscrições e
    cisões NÃO são ajustados (retorno só-preço, rota (b) da H1); os saltos > 30% que sobram
    (limiar [H1-FROZEN] jump_detector) são listados no manifesto;
  * pré-filtro de liquidez PIT: em cada pregão, mediana do volume financeiro nos 126 pregões
    anteriores (sessão sem negócio = 0, a regra de research_pit.Panel.universe); o ISIN entra
    no painel se ficou entre os 100 primeiros em algum pregão. Só usa passado; o painel
    completo também é gravado e verify_prefilter.py prova, pela wheel instalada, que o universo
    PIT de cada rebalance é idêntico nos dois;
  * data_cutoff (as_of) = disponibilidade do último pregão do snapshot; registro com
    available_at posterior fica fora (contado no manifesto);
  * o objeto final tem de caber no limite do ReferenceStore do stocks-predictor (32 MiB).

Uso:
  python build_real_panel.py pin   <cache> <SOURCES.json>          (baixa e fixa URL + sha256)
  python build_real_panel.py build <cache> <SOURCES.json> <saída>  (confere hashes e constrói)
"""

from __future__ import annotations

import base64
import csv
import hashlib
import http.client
import io
import json
import sys
import time
import urllib.error
import urllib.request
import zipfile
from bisect import bisect_left
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RULES = {
    "builder": "qualification/stocks/d16/build_real_panel.py",
    "panel_schema": "stocks-pit-panel/1",
    "window_start": "2021-01-04",
    "cotahist_years": [2021, 2022, 2023, 2024, 2025, 2026],
    "fca_years": [2021, 2022, 2023, 2024, 2025, 2026],
    "vlmo_year": 2026,
    "tpmerc": "010",
    "codbdi": "02",
    "especi_types": ["ON", "PN", "PNA", "PNB", "PNC", "PND", "PNE", "PNF", "PNG", "PNH", "UNT"],
    "availability_clock_utc": "03:00:00",
    "bar_availability": "next weekday after the session, 00:00 America/Sao_Paulo",
    "cvm_availability": "DT_RECEB + 1 calendar day, 00:00 America/Sao_Paulo",
    "security_id": "ISIN (CODISI); a new ISIN is a new security_id",
    "identity_primary": "CVM FCA valor_mobiliario Codigo_Negociacao used by the ISIN -> CNPJ; effective_on = "
                        "Data_Inicio_Negociacao (else DT_REFER); available_at = DT_RECEB + 1 day; Data_Fim_Negociacao unused",
    "identity_fallback": "only for an ISIN without a primary identity: ticker root -> codeCVM in the B3 payload -> "
                         "CNPJ in the FCA index (CD_CVM); effective_on = listed_on; available_at = DT_RECEB + 1 day",
    "corporate_event_labels": ["DESDOBRAMENTO", "GRUPAMENTO", "BONIFICACAO"],
    "prefilter_liquidity_lookback": 126,
    "prefilter_top_k": 100,
    "residual_jump_threshold": 0.30,
    "revised_close_significant_digits": 10,
    "max_object_bytes": 32 * 1024 * 1024,
    "pit_classes": {"securities": "PIT_RECONSTRUCTED", "ticker_events": "PIT_RECONSTRUCTED",
                    "identity_events": "PIT_RECONSTRUCTED", "bars": "PIT_RECONSTRUCTED"},
}
COTAHIST_URL = "https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{year}.ZIP"
FCA_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_{year}.zip"
VLMO_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/VLMO/DADOS/vlmo_cia_aberta_{year}.zip"
B3_EVENTS_URL = ("https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/"
                 "GetListedSupplementCompany/{token}")
USER_AGENT = "Mozilla/5.0 (stocks-qualification-d16; public data)"


# ----------------------------------------------------------------------------- utils
def canonical(value) -> bytes:
    """O mesmo canonical do stocks_predictor.research_contract (chaves ordenadas, sem espaço)."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def b3_token(issuer: str) -> str:
    raw = json.dumps({"issuingCompany": issuer, "language": "pt-br"}, separators=(",", ":"))
    return base64.b64encode(raw.encode("ascii")).decode("ascii")


def fetch(url: str, *, tries: int = 12) -> tuple[int, bytes]:
    """GET com retomada: a conexão cortada no meio (IncompleteRead, reset) continua de onde parou
    com `Range: bytes=N-` e `If-Range: <ETag>` (se o arquivo mudou no servidor, recomeça do zero).
    O tamanho total é conferido; a integridade final é o sha256 fixado (conferido por quem chama)."""
    data = bytearray()
    etag = total = None
    status = None
    last = None
    for attempt in range(tries):
        headers = {"User-Agent": USER_AGENT}
        if data and etag:
            headers["Range"] = f"bytes={len(data)}-"
            headers["If-Range"] = etag
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                resumed = response.status == 206 and bool(data)
                if resumed:
                    content_range = response.headers.get("Content-Range", "")
                    if not content_range.startswith(f"bytes {len(data)}-"):
                        raise http.client.HTTPException(f"unexpected Content-Range {content_range!r}")
                else:
                    data = bytearray()
                    status = response.status
                    etag = response.headers.get("ETag")
                    length = response.headers.get("Content-Length")
                    total = int(length) if length and length.isdigit() else None
                while True:
                    chunk = response.read(1 << 20)
                    if not chunk:
                        break
                    data += chunk
            if total is not None and len(data) != total:
                raise http.client.IncompleteRead(bytes(), total - len(data))
            return status, bytes(data)
        except urllib.error.HTTPError as exc:
            if exc.code < 500 and exc.code != 416:
                return exc.code, exc.read()
            last = exc
            if exc.code == 416:
                data = bytearray()
        except (urllib.error.URLError, http.client.HTTPException, OSError) as exc:
            last = exc
        time.sleep(min(5 * (attempt + 1), 30))
    raise RuntimeError(f"download failed after {tries} tries: {url}: {last!r} ({len(data)} bytes kept)")


def cached(cache: Path, name: str, url: str, expected: str | None, log: list) -> bytes:
    """Arquivo do cache se o sha256 bater; senão baixa da URL oficial. Com `expected`, falha fechado."""
    path = cache / name
    if path.is_file() and expected is not None and sha(path.read_bytes()) == expected:
        raw = path.read_bytes()
        log.append({"name": name, "url": url, "sha256": expected, "bytes": len(raw), "from": "cache"})
        return raw
    status, raw = fetch(url)
    observed = sha(raw)
    log.append({"name": name, "url": url, "http_status": status, "sha256": observed, "bytes": len(raw),
                "from": "download", "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    if expected is not None and observed != expected:
        raise SystemExit(f"SHA256 MISMATCH {name}: pinned {expected} observed {observed} ({url})")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def next_weekday(day: str) -> str:
    current = date.fromisoformat(day) + timedelta(days=1)
    while current.weekday() >= 5:
        current += timedelta(days=1)
    return current.isoformat()


def avail_day(day: str) -> str:
    return f"{day}T{RULES['availability_clock_utc']}Z"


def bar_available(session: str) -> str:
    return avail_day(next_weekday(session))


def cvm_available(received: str) -> str:
    return avail_day((date.fromisoformat(received) + timedelta(days=1)).isoformat())


def br_date(text: str) -> str:
    return datetime.strptime(text.strip(), "%d/%m/%Y").date().isoformat()


def iso_or_none(text: str | None) -> str | None:
    text = (text or "").strip()[:10]
    if not text:
        return None
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        return None


def median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    if n == 0:
        return 0.0
    m = n // 2
    return ordered[m] if n % 2 else (ordered[m - 1] + ordered[m]) / 2.0


def significant(value: float, digits: int) -> float:
    return float(f"{value:.{digits}g}")


# --------------------------------------------------------------------------- parsing
def parse_cotahist(raw: bytes, stats: dict) -> list[tuple]:
    keep = set(RULES["especi_types"])
    tpmerc, codbdi = RULES["tpmerc"].encode(), RULES["codbdi"].encode()
    out = []
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != 1:
            raise SystemExit(f"COTAHIST: expected one member, got {names}")
        with archive.open(names[0]) as stream:
            for line in stream:
                if line[:2] != b"01":
                    continue
                stats["quote_records"] += 1
                line = line.rstrip(b"\r\n")
                if len(line) != 245:
                    stats["malformed"] += 1
                    continue
                if line[24:27] != tpmerc or line[10:12] != codbdi:
                    continue
                especi = line[39:49].decode("latin-1").strip()
                if (especi.split()[0] if especi else "") not in keep:
                    stats["excluded_instrument_type"] += 1
                    continue
                d = line[2:10].decode("ascii")
                session = f"{d[:4]}-{d[4:6]}-{d[6:]}"
                if session < RULES["window_start"]:
                    continue
                isin = line[230:242].decode("latin-1").strip()
                fatcot = int(line[210:217])
                preult = int(line[108:121])
                if len(isin) != 12 or not isin.startswith("BR") or fatcot <= 0:
                    stats["invalid_identity_or_factor"] += 1
                    continue
                if preult <= 0:
                    stats["non_positive_close"] += 1
                    continue
                out.append((session, isin, line[12:24].decode("latin-1").strip(), preult / (100 * fatcot),
                            int(line[170:188]) / 100, especi, int(line[242:245])))
    return out


def csv_rows(archive: zipfile.ZipFile, name: str) -> list[dict]:
    with archive.open(name) as stream:
        return list(csv.DictReader(io.TextIOWrapper(stream, encoding="latin-1"), delimiter=";"))


def parse_fca_index(raw: bytes, year: int) -> list[dict]:
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        rows = csv_rows(archive, f"fca_cia_aberta_{year}.csv")
    out = []
    for row in rows:
        received = iso_or_none(row["DT_RECEB"])
        if received is None or not row["CD_CVM"].strip().isdigit():
            continue
        out.append({"cnpj": row["CNPJ_CIA"].strip(), "code_cvm": int(row["CD_CVM"]), "received": received,
                    "id_doc": row["ID_DOC"], "fca_year": year})
    return out


def parse_fca(raw: bytes, year: int) -> list[dict]:
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        index = {row["ID_DOC"]: row for row in csv_rows(archive, f"fca_cia_aberta_{year}.csv")}
        rows = csv_rows(archive, f"fca_cia_aberta_valor_mobiliario_{year}.csv")
    out = []
    for row in rows:
        ticker = (row.get("Codigo_Negociacao") or "").strip().upper()
        doc = index.get(row["ID_Documento"])
        if not ticker or doc is None or doc["CNPJ_CIA"] != row["CNPJ_Companhia"]:
            continue
        received = iso_or_none(doc["DT_RECEB"])
        if received is None:
            continue
        out.append({"ticker": ticker, "cnpj": row["CNPJ_Companhia"].strip(), "received": received,
                    "start": iso_or_none(row.get("Data_Inicio_Negociacao")),
                    "end": iso_or_none(row.get("Data_Fim_Negociacao")),
                    "refer": iso_or_none(doc["DT_REFER"]), "id_doc": row["ID_Documento"], "fca_year": year})
    return out


def parse_b3_payload(raw: bytes) -> tuple[list[dict], set[int]]:
    """(eventos acionários, códigos CVM) da resposta oficial; resposta vazia/inválida → nada."""
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [], set()
    items = value if isinstance(value, list) else [value]
    events, codes = [], set()
    for item in items:
        if not isinstance(item, dict):
            continue
        events += item.get("stockDividends") or []
        code = str(item.get("codeCVM") or "").strip()
        if code.isdigit() and int(code) > 0:
            codes.add(int(code))
    return events, codes


# ----------------------------------------------------------------------------- build
def load_sources(cache: Path, sources: dict | None, log: list) -> dict:
    pinned = {s["name"]: s for s in (sources or {}).get("files", [])}
    raw = {}

    def get(name: str, url: str) -> bytes:
        entry = pinned.get(name)
        if sources is not None and entry is None:
            raise SystemExit(f"source {name} is not pinned in SOURCES.json")
        if entry is not None and entry["url"] != url:
            raise SystemExit(f"source {name}: URL differs from the pinned one")
        return cached(cache, name, url, entry["sha256"] if entry else None, log)

    for year in RULES["cotahist_years"]:
        raw[f"COTAHIST_A{year}.ZIP"] = get(f"COTAHIST_A{year}.ZIP", COTAHIST_URL.format(year=year))
    for year in RULES["fca_years"]:
        raw[f"fca_cia_aberta_{year}.zip"] = get(f"fca_cia_aberta_{year}.zip", FCA_URL.format(year=year))
    name = f"vlmo_cia_aberta_{RULES['vlmo_year']}.zip"
    raw[name] = get(name, VLMO_URL.format(year=RULES["vlmo_year"]))
    raw["_get"] = get
    return raw


def build(cache: Path, sources: dict | None, log: list, *, pin_issuers: bool = False) -> dict:
    raw = load_sources(cache, sources, log)
    get = raw.pop("_get")
    stats = defaultdict(int)
    records: dict[tuple[str, str], tuple] = {}
    for year in RULES["cotahist_years"]:
        for rec in parse_cotahist(raw[f"COTAHIST_A{year}.ZIP"], stats):
            key = (rec[0], rec[1])
            if key in records:
                if records[key][2:5] != rec[2:5]:
                    raise SystemExit(f"conflicting duplicate COTAHIST record {key}")
                stats["identical_duplicates"] += 1
                continue
            records[key] = rec
    calendar = sorted({session for session, _ in records})
    last_session = calendar[-1]
    cutoff = bar_available(last_session)
    series: dict[str, list[tuple]] = defaultdict(list)
    for rec in records.values():
        series[rec[1]].append(rec)
    for rows in series.values():
        rows.sort()

    # PIT liquidity prefilter (superset of any universe the handler can build)
    lookback, top_k = RULES["prefilter_liquidity_lookback"], RULES["prefilter_top_k"]
    index = {s: i for i, s in enumerate(calendar)}
    positions = {isin: [index[r[0]] for r in rows] for isin, rows in series.items()}
    volumes = {isin: [r[4] for r in rows] for isin, rows in series.items()}
    best_rank: dict[str, int] = {}
    for i in range(lookback, len(calendar) + 1):
        lo = i - lookback
        scored = []
        for isin, pos in positions.items():
            a, b = bisect_left(pos, lo), bisect_left(pos, i)
            if b > a:
                window = volumes[isin][a:b]
                scored.append((-median(window + [0.0] * (lookback - len(window))), isin))
        scored.sort()
        for rank, (_neg, isin) in enumerate(scored[:top_k], 1):
            if rank < best_rank.get(isin, 1 << 30):
                best_rank[isin] = rank
    kept = sorted(best_rank)

    # identity (CVM FCA)
    fca_rows = []
    for year in RULES["fca_years"]:
        fca_rows += parse_fca(raw[f"fca_cia_aberta_{year}.zip"], year)
    ticker_ranges: dict[str, dict[str, list[str]]] = defaultdict(dict)
    for isin, rows in series.items():
        for rec in rows:
            span = ticker_ranges[isin].setdefault(rec[2], [rec[0], rec[0]])
            span[1] = rec[0]
    by_ticker: dict[str, list[str]] = defaultdict(list)
    for isin, spans in ticker_ranges.items():
        for ticker in spans:
            by_ticker[ticker].append(isin)
    # (1) CVM FCA: código de negociação → CNPJ. Data_Fim_Negociacao não é usada: vem preenchida
    # errado por algumas companhias (ex.: CEAB3 com fim = início em 2019 e negociando até hoje).
    identity: dict[tuple[str, str, str], tuple[str, str]] = {}
    identity_stats = defaultdict(int)
    for row in fca_rows:
        for isin in by_ticker.get(row["ticker"], ()):
            first, last = ticker_ranges[isin][row["ticker"]]
            if row["start"] and row["start"] > last:
                identity_stats["fca_rows_start_after_last_trade"] += 1
                continue
            available = cvm_available(row["received"])
            if available > cutoff:
                identity_stats["fca_rows_after_cutoff"] += 1
                continue
            effective = row["start"] or row["refer"]
            key = (isin, row["cnpj"], effective)
            if key not in identity or available < identity[key][0]:
                identity[key] = (available, "CVM_FCA")

    # corporate events and CVM codes (B3) for the issuers of the kept securities
    issuers = sorted({ticker[:4] for isin in kept for ticker in ticker_ranges[isin]})
    if sources is not None and not pin_issuers:
        pinned_issuers = sorted(s["issuer"] for s in sources["files"] if s.get("kind") == "b3_corporate_events")
        if pinned_issuers != issuers:
            raise SystemExit(f"issuer list differs from the pinned one: +{sorted(set(issuers) - set(pinned_issuers))}"
                             f" -{sorted(set(pinned_issuers) - set(issuers))}")
    events_by_isin: dict[str, list[dict]] = defaultdict(list)
    codes_by_root: dict[str, set[int]] = {}
    event_payload_status = {}
    for issuer in issuers:
        name = f"b3_events_{issuer}.json"
        payload = get(name, B3_EVENTS_URL.format(token=b3_token(issuer)))
        events, codes = parse_b3_payload(payload)
        event_payload_status[issuer] = {"stock_events": len(events), "code_cvm": sorted(codes), "bytes": len(payload)}
        codes_by_root[issuer] = codes
        if log and log[-1]["name"] == name and log[-1]["from"] == "download":
            time.sleep(0.4)  # uma chamada por vez à API pública da B3
        for event in events:
            events_by_isin[(event.get("isinCode") or "").strip()].append(event)

    # (2) reserva, só para ISIN sem identidade em (1): raiz do ticker → codeCVM (B3) → CNPJ no
    # índice do FCA (CD_CVM), disponível no recebimento de cada FCA; effective_on = listed_on.
    fca_index = []
    for year in RULES["fca_years"]:
        fca_index += parse_fca_index(raw[f"fca_cia_aberta_{year}.zip"], year)
    by_code: dict[int, list[dict]] = defaultdict(list)
    for row in fca_index:
        by_code[row["code_cvm"]].append(row)
    with_identity = {key[0] for key in identity}
    for isin in sorted(set(series) - with_identity):
        codes = set()
        for ticker in ticker_ranges[isin]:
            codes |= codes_by_root.get(ticker[:4], set())
        for code in sorted(codes):
            for row in by_code.get(code, ()):
                available = cvm_available(row["received"])
                if available > cutoff:
                    identity_stats["fallback_rows_after_cutoff"] += 1
                    continue
                key = (isin, row["cnpj"], series[isin][0][0])
                if key not in identity or available < identity[key][0]:
                    identity[key] = (available, "B3_CODE_CVM+CVM_FCA")

    kept_set = set(kept)
    securities, tickers, identities, bars = [], [], [], []
    adjustments, skipped_events, residual_jumps = [], [], []
    dropped_after_cutoff = defaultdict(int)
    labels = set(RULES["corporate_event_labels"])
    digits = RULES["revised_close_significant_digits"]
    full = {"securities": [], "ticker_events": [], "identity_events": [], "bars": []}
    for isin in sorted(series):
        rows = series[isin]
        sessions = [r[0] for r in rows]
        sec = {"security_id": isin, "listed_on": rows[0][0], "listing_available_at": bar_available(rows[0][0]),
               "delisted_on": None, "delisting_available_at": None}
        tick = []
        previous = None
        for rec in rows:
            if rec[2] != previous:
                tick.append({"security_id": isin, "ticker": rec[2], "effective_on": rec[0],
                             "available_at": bar_available(rec[0])})
                previous = rec[2]
        ident = [{"security_id": isin, "issuer_cnpj": cnpj, "effective_on": eff, "available_at": av,
                  "source": src} for (i, cnpj, eff), (av, src) in sorted(identity.items()) if i == isin]
        # corporate events → PIT revisions
        steps: dict[str, list[tuple[str, float]]] = defaultdict(list)  # revision time -> [(ex, multiplier)]
        seen_events = set()
        for event in events_by_isin.get(isin, ()):
            label = (event.get("label") or "").strip().upper()
            key = json.dumps(event, sort_keys=True)
            if label not in labels or key in seen_events:
                continue
            seen_events.add(key)
            detail = {"security_id": isin, "label": label, "factor": event.get("factor"),
                      "approvedOn": event.get("approvedOn"), "lastDatePrior": event.get("lastDatePrior"),
                      "assetIssued": event.get("assetIssued")}
            try:
                factor = float((event.get("factor") or "").replace(".", "").replace(",", "."))
                prior = br_date(event["lastDatePrior"])
                approved = br_date(event["approvedOn"])
            except (ValueError, KeyError, AttributeError):
                skipped_events.append({**detail, "reason": "unparseable"})
                continue
            if (event.get("assetIssued") or isin).strip() != isin:
                skipped_events.append({**detail, "reason": "asset issued differs from the holder ISIN"})
                continue
            multiplier = factor if label == "GRUPAMENTO" else 1.0 + factor / 100.0
            if not multiplier > 0 or multiplier == 1.0:
                skipped_events.append({**detail, "reason": "non-positive or neutral multiplier"})
                continue
            j = bisect_left(sessions, (date.fromisoformat(prior) + timedelta(days=1)).isoformat())  # 1º pregão após a data com
            if j >= len(sessions):
                skipped_events.append({**detail, "reason": "ex date after the last session"})
                continue
            if j == 0:
                skipped_events.append({**detail, "reason": "ex date at/before the first session of the window"})
                continue
            ex = sessions[j]
            when = max(bar_available(ex), cvm_available(approved))
            if when > cutoff:
                dropped_after_cutoff["corporate_event_revisions"] += 1
                continue
            steps[when].append((ex, multiplier))
            observed = rows[j][3] / rows[j - 1][3]
            adjustments.append({**detail, "ex_session": ex, "revision_available_at": when, "multiplier": multiplier,
                                "price_ratio_ex_over_prior": round(observed, 6),
                                "implied_price_move": round(observed * multiplier - 1.0, 6)})
        bar_rows = [{"security_id": isin, "session": r[0], "close": r[3], "volume_fin": r[4],
                     "available_at": bar_available(r[0])} for r in rows]
        applied: list[tuple[str, float]] = []
        last_factor = [1.0] * len(rows)
        for when in sorted(steps):
            applied += steps[when]
            for k, r in enumerate(rows):
                factor = 1.0
                for ex, multiplier in applied:
                    if r[0] < ex:
                        factor /= multiplier
                if factor != last_factor[k]:  # só republica a barra cujo fator mudou neste instante
                    last_factor[k] = factor
                    bar_rows.append({"security_id": isin, "session": r[0], "close": significant(r[3] * factor, digits),
                                     "volume_fin": r[4], "available_at": when})
        # residual jumps after adjustment (as known at the cutoff), diagnostic only
        final_factor = []
        for r in rows:
            factor = 1.0
            for ex, multiplier in applied:
                if r[0] < ex:
                    factor /= multiplier
            final_factor.append(r[3] * factor)
        for k in range(1, len(rows)):
            move = final_factor[k] / final_factor[k - 1] - 1.0
            if abs(move) > RULES["residual_jump_threshold"]:
                residual_jumps.append({"security_id": isin, "ticker": rows[k][2], "session": rows[k][0],
                                       "move": round(move, 4), "especi": rows[k][5],
                                       "dismes_changed": rows[k][6] != rows[k - 1][6], "kept_in_panel": isin in kept_set})
        target = [full]
        panel_rows = (sec, tick, ident, bar_rows)
        for doc in target:
            doc["securities"].append(panel_rows[0])
            doc["ticker_events"] += panel_rows[1]
            doc["identity_events"] += panel_rows[2]
            doc["bars"] += panel_rows[3]
        if isin in kept_set:
            securities.append(sec)
            tickers += tick
            identities += ident
            bars += bar_rows

    def panel(version: str, secs, ticks, idents, bar_list) -> dict:
        return {"schema": RULES["panel_schema"], "dataset_version": version, "data_cutoff": cutoff,
                "pit_classes": dict(RULES["pit_classes"]), "securities": secs, "ticker_events": ticks,
                "identity_events": idents, "bars": bar_list}

    snapshot = next((e for e in log if e["name"] == f"COTAHIST_A{RULES['cotahist_years'][-1]}.ZIP"), {})
    version = f"b3-cvm-real-{RULES['window_start']}_{last_session}-cotahist{str(snapshot.get('sha256', ''))[:12]}-k{top_k}"
    prefiltered = panel(version, securities, tickers, identities, bars)
    complete = panel(version + "-full", full["securities"], full["ticker_events"], full["identity_events"], full["bars"])
    for doc in (prefiltered, complete):
        for record in doc["ticker_events"] + doc["identity_events"] + doc["bars"] + doc["securities"]:
            for field in ("available_at", "listing_available_at"):
                if record.get(field) and record[field] > cutoff:
                    raise SystemExit(f"record available after the cutoff: {record}")
    covered = {i["security_id"] for i in identities}
    net: dict[tuple[str, str], dict] = {}
    for a in adjustments:  # eventos no mesmo pregão ex se compõem (ex.: desdobramento + grupamento)
        entry = net.setdefault((a["security_id"], a["ex_session"]), {"security_id": a["security_id"],
                               "ex_session": a["ex_session"], "labels": [], "multiplier": 1.0,
                               "price_ratio_ex_over_prior": a["price_ratio_ex_over_prior"]})
        entry["labels"].append(a["label"])
        entry["multiplier"] *= a["multiplier"]
    for entry in net.values():
        entry["implied_price_move"] = round(entry["price_ratio_ex_over_prior"] * entry["multiplier"] - 1.0, 6)
    manifest = {
        "schema": "stocks/D16_BUILD_MANIFEST/1",
        "rules": RULES,
        "rules_sha256": sha(canonical(RULES)),
        "sources": log,
        "calendar": {"sessions": len(calendar), "first": calendar[0], "last": last_session},
        "data_cutoff": cutoff,
        "dataset_version": version,
        "cotahist_stats": dict(stats),
        "securities_total": len(series),
        "securities_kept": len(kept),
        "prefilter_best_rank_max_kept": max(best_rank.values()) if best_rank else None,
        "counts": {k: len(prefiltered[k]) for k in ("securities", "ticker_events", "identity_events", "bars")},
        "counts_full": {k: len(complete[k]) for k in ("securities", "ticker_events", "identity_events", "bars")},
        "identity": {**identity_stats, "fca_rows": len(fca_rows), "kept_without_identity":
                     sorted(i for i in kept if i not in covered)},
        "issuers_queried": issuers,
        "issuer_event_counts": event_payload_status,
        "corporate_adjustments": adjustments,
        "corporate_adjustments_net_by_ex_session": sorted(net.values(), key=lambda e: (e["security_id"], e["ex_session"])),
        "identity_sources": {src: sum(1 for i in identities if i["source"] == src)
                             for src in sorted({i["source"] for i in identities})},
        "corporate_events_skipped": skipped_events,
        "residual_jumps": residual_jumps,
        "dropped_after_cutoff": dict(dropped_after_cutoff),
    }
    return {"panel": prefiltered, "full": complete, "manifest": manifest,
            "vlmo": raw[f"vlmo_cia_aberta_{RULES['vlmo_year']}.zip"]}


def pin(cache: Path, out: Path) -> int:
    log: list = []
    result = build(cache, None, log, pin_issuers=True)
    files = []
    for entry in log:
        item = {"name": entry["name"], "url": entry["url"], "sha256": entry["sha256"], "bytes": entry["bytes"],
                "fetched_at": entry.get("at"), "http_status": entry.get("http_status")}
        if entry["name"].startswith("b3_events_"):
            item["kind"] = "b3_corporate_events"
            item["issuer"] = entry["name"][len("b3_events_"):-len(".json")]
        elif entry["name"].startswith("COTAHIST"):
            item["kind"] = "b3_cotahist"
        elif entry["name"].startswith("fca_"):
            item["kind"] = "cvm_fca"
        else:
            item["kind"] = "cvm_vlmo"
        files.append(item)
    document = {"schema": "stocks/D16_SOURCES/1", "pinned_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "rules": RULES, "rules_sha256": sha(canonical(RULES)), "files": files,
                "expected": {"data_cutoff": result["manifest"]["data_cutoff"],
                             "dataset_version": result["manifest"]["dataset_version"],
                             "panel_sha256": sha(canonical(result["panel"])),
                             "panel_bytes": len(canonical(result["panel"]))}}
    out.write_text(json.dumps(document, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(document["expected"]))
    return 0


def run_build(cache: Path, sources_path: Path, out: Path) -> int:
    sources = json.loads(sources_path.read_text(encoding="utf-8"))
    if sources["rules"] != RULES or sources["rules_sha256"] != sha(canonical(RULES)):
        raise SystemExit("builder RULES differ from the pinned SOURCES.json rules")
    log: list = []
    result = build(cache, sources, log)
    out.mkdir(parents=True, exist_ok=True)
    panel_raw = canonical(result["panel"])
    full_raw = canonical(result["full"])
    manifest = result["manifest"]
    manifest["panel"] = {"sha256": sha(panel_raw), "bytes": len(panel_raw),
                         "fits_reference_store": len(panel_raw) <= RULES["max_object_bytes"]}
    manifest["panel_full"] = {"sha256": sha(full_raw), "bytes": len(full_raw)}
    manifest["expected_from_pin"] = sources.get("expected")
    manifest["matches_pin"] = sources.get("expected", {}).get("panel_sha256") == manifest["panel"]["sha256"]
    vlmo = result["vlmo"]
    source_object = {"schema": "stocks-ei-source/1", "collector": "cvm-vlmo",
                     "file_name": f"vlmo_cia_aberta_{RULES['vlmo_year']}.zip",
                     "payload_b64": base64.b64encode(vlmo).decode("ascii"), "payload_sha256": sha(vlmo)}
    (out / "panel.json").write_bytes(panel_raw)
    (out / "panel_full.json").write_bytes(full_raw)
    (out / "vlmo_source.json").write_bytes(canonical(source_object))
    (out / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n",
                                             encoding="utf-8", newline="\n")
    print(json.dumps({"panel_sha256": manifest["panel"]["sha256"], "panel_bytes": len(panel_raw),
                      "fits": manifest["panel"]["fits_reference_store"], "matches_pin": manifest["matches_pin"],
                      "counts": manifest["counts"], "cutoff": manifest["data_cutoff"]}))
    if not manifest["panel"]["fits_reference_store"]:
        return 2
    return 0 if manifest["matches_pin"] else 3


def main() -> int:
    mode = sys.argv[1]
    cache = Path(sys.argv[2])
    cache.mkdir(parents=True, exist_ok=True)
    if mode == "pin":
        return pin(cache, Path(sys.argv[3]))
    if mode == "build":
        return run_build(cache, Path(sys.argv[3]), Path(sys.argv[4]))
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main())
