import asyncio
import os
import statistics
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

import httpx

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
TOTAL_REQUESTS = int(os.getenv("TOTAL_REQUESTS", "1000"))
CONCURRENCY = int(os.getenv("CONCURRENCY", "5"))
TIMEOUT_SECONDS = float(os.getenv("TIMEOUT", "60"))
VERBOSE = os.getenv("VERBOSE", "0") == "1"
MAX_ERROR_SAMPLES = int(os.getenv("MAX_ERROR_SAMPLES", "12"))

HEALTH_URL = f"{BASE_URL}/health"
ORDERS_URL = f"{BASE_URL}/orders"


def _print_connection_refused_help(exc: Exception) -> None:
    print(
        f"\nNão foi possível conectar a {HEALTH_URL}\n"
        f"  Erro: {type(exc).__name__}: {exc}\n"
        "  Causa provável: nada escuta nesse host/porta, ou a API ainda não subiu.\n"
        f"  Ajuste BASE_URL se o serviço estiver noutro endereço (atual: {BASE_URL!r}).\n"
        "  Exemplos:\n"
        "    - local:  uv run uvicorn app.main:app --host 0.0.0.0 --port 8000\n"
        "    - Docker: use a mesma porta que APP_PORT no .env, p.ex. "
        "BASE_URL=http://127.0.0.1:8000\n",
        file=sys.stderr,
    )


def _truncate(s: str, n: int = 200) -> str:
    s = s.replace("\n", " ").strip()
    if len(s) <= n:
        return s
    return s[: n - 3] + "..."


@dataclass
class LoadTestResults:
    latencies: list[float] = field(default_factory=list)
    success_count: int = 0
    http_failures: int = 0
    transport_failures: int = 0
    status_hits: Counter[int] = field(default_factory=Counter)
    httpx_error_hits: Counter[str] = field(default_factory=Counter)
    http_samples: list[tuple[int, int, str]] = field(
        default_factory=list
    )  # (request_num, code, body)
    transport_samples: list[tuple[int, str, str]] = field(
        default_factory=list
    )  # (request_num, exc_type, message)

    @property
    def failed(self) -> int:
        return self.http_failures + self.transport_failures

    @property
    def succeeded(self) -> int:
        return self.success_count

    def record_ok(self, req_num: int, elapsed_ms: float) -> None:
        _ = req_num
        self.success_count += 1
        self.latencies.append(elapsed_ms)

    def record_http_error(
        self, req_num: int, code: int, body: str, elapsed_ms: float
    ) -> None:
        self.http_failures += 1
        self.status_hits[code] += 1
        snippet = _truncate(body, 200)
        if len(self.http_samples) < MAX_ERROR_SAMPLES:
            self.http_samples.append((req_num, code, snippet))
        if VERBOSE:
            print(
                f"Request {req_num} failed after {elapsed_ms:.2f} ms: "
                f"HTTP {code} - {snippet}"
            )

    def record_transport_error(
        self, req_num: int, exc: BaseException, elapsed_ms: float
    ) -> None:
        self.transport_failures += 1
        name = type(exc).__name__
        self.httpx_error_hits[name] += 1
        msg = str(exc) or repr(exc)
        if len(self.transport_samples) < MAX_ERROR_SAMPLES:
            self.transport_samples.append((req_num, name, _truncate(msg, 200)))
        if VERBOSE:
            print(
                f"Request {req_num} failed after {elapsed_ms:.2f} ms: {name}: {msg!r}"
            )


def percentile(values: list[float], percent: float) -> float:
    if not values:
        return 0.0

    ordered = sorted(values)
    position = (len(ordered) - 1) * (percent / 100)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)

    if lower == upper:
        return ordered[lower]

    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


async def check_health(client: httpx.AsyncClient) -> None:
    try:
        response = await client.get(HEALTH_URL, timeout=TIMEOUT_SECONDS)
    except httpx.RequestError as exc:
        _print_connection_refused_help(exc)
        raise SystemExit(1) from exc
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(
            f"Health check falhou: HTTP {exc.response.status_code} - "
            f"{exc.response.text!r}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
    print(f"Health check OK: {response.status_code} - {response.text}")


def print_error_diagnostics(r: LoadTestResults) -> None:
    if r.http_failures == 0 and r.transport_failures == 0:
        return

    print("\n--- Diagnóstico de erros ---")

    if r.http_failures:
        print("Respostas HTTP não-sucesso (contagem):")
        for code in sorted(r.status_hits.keys()):
            print(f"  {code}: {r.status_hits[code]}")
        if r.http_samples and not VERBOSE:
            print("Amostras (req #, status, corpo):")
            for n, code, body in r.http_samples:
                print(f"  #{n} -> {code}: {body!r}")

    if r.transport_failures:
        print("Exceções de transporte/HTTPX (contagem):")
        for name, count in sorted(
            r.httpx_error_hits.items(), key=lambda x: (-x[1], x[0])
        ):
            print(f"  {name}: {count}")
        if r.transport_samples and not VERBOSE:
            print("Amostras (req #, tipo, mensagem):")
            for n, t, msg in r.transport_samples:
                print(f"  #{n} -> {t}: {msg!r}")

    print(
        "Dica: rode com VERBOSE=1 para log linha a linha; MAX_ERROR_SAMPLES=N para mais amostras."
    )


def print_report(results: LoadTestResults, total_time: float) -> None:
    print("\n=== Resultado do load test ===")
    print(f"URL base: {BASE_URL}")
    print(f"Total de requisições: {TOTAL_REQUESTS}")
    print(f"Concorrência: {CONCURRENCY}")
    print(f"Sucesso: {results.succeeded}")
    print(f"Falha (HTTP não 2xx): {results.http_failures}")
    print(f"Falha (transporte/exceção): {results.transport_failures}")
    print(f"Falha total: {results.failed}")
    print(f"Tempo total: {total_time:.2f}s")
    if total_time > 0 and results.succeeded:
        print(
            f"Req/s (apenas sucesso): {results.succeeded / total_time:.2f} | "
            f"Req/s (total enviado): {TOTAL_REQUESTS / total_time:.2f}"
        )

    if not results.latencies:
        print_error_diagnostics(results)
        return

    print(f"Latência média (sucessos): {statistics.mean(results.latencies):.2f} ms")
    print(f"Mediana: {statistics.median(results.latencies):.2f} ms")
    print(
        f"Min: {min(results.latencies):.2f} ms | Max: {max(results.latencies):.2f} ms"
    )
    print(
        f"P95: {percentile(results.latencies, 95):.2f} ms | P99: {percentile(results.latencies, 99):.2f} ms"
    )
    print_error_diagnostics(results)


async def create_order(
    client: httpx.AsyncClient,
    order_number: int,
    limit: asyncio.Semaphore,
    results: LoadTestResults,
) -> None:
    payload: dict[str, Any] = {
        "customer_name": f"Cliente {order_number}",
        "items": [
            {
                "product_id": f"product-{order_number}",
                "quantity": 1,
                "unit_price": 150.0,
            }
        ],
    }

    async with limit:
        started_at = time.perf_counter()

        try:
            response = await client.post(
                ORDERS_URL, json=payload, timeout=TIMEOUT_SECONDS
            )
            elapsed_ms = (time.perf_counter() - started_at) * 1000

            if response.status_code in (200, 201):
                results.record_ok(order_number, elapsed_ms)
                return

            results.record_http_error(
                order_number, response.status_code, response.text, elapsed_ms
            )
        except (httpx.HTTPError, OSError) as exc:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            results.record_transport_error(order_number, exc, elapsed_ms)


async def main() -> None:
    limits = httpx.Limits(
        max_connections=max(CONCURRENCY * 2, 100),
        max_keepalive_connections=CONCURRENCY * 2,
    )
    timeout = httpx.Timeout(TIMEOUT_SECONDS)
    results = LoadTestResults()
    limit = asyncio.Semaphore(CONCURRENCY)

    print(
        f"Config: CONCURRENCY={CONCURRENCY}, TIMEOUT={TIMEOUT_SECONDS}s, "
        f"VERBOSE={VERBOSE}, MAX_ERROR_SAMPLES={MAX_ERROR_SAMPLES}\n"
    )

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        await check_health(client)

        started_at = time.perf_counter()
        tasks = [
            create_order(client, order_number, limit, results)
            for order_number in range(TOTAL_REQUESTS)
        ]
        await asyncio.gather(*tasks)
        total_time = time.perf_counter() - started_at

    print_report(results, total_time)


if __name__ == "__main__":
    asyncio.run(main())
