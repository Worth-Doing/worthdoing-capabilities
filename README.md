<p align="center">
  <img src="https://raw.githubusercontent.com/Worth-Doing/brand-assets/main/png/variants/04-horizontal.png" alt="WorthDoing.ai" width="600" />
</p>

<h1 align="center">WorthDoing Capabilities</h1>

<p align="center">
  <strong>A production-grade capability package for portable, composable, reusable agent actions.</strong>
  <br />
  <em>Built from scratch by WorthDoing AI — not a wrapper, not a toy, not another agent toolkit clone.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Built%20by-WorthDoing.ai-blue?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiPjxwb2x5Z29uIHBvaW50cz0iMTIgMiAxNS4wOSA4LjI2IDIyIDkuMjcgMTcgMTQuMTQgMTguMTggMjEuMDIgMTIgMTcuNzcgNS44MiAyMS4wMiA3IDE0LjE0IDIgOS4yNyA4LjkxIDguMjYgMTIgMiIvPjwvc3ZnPg==" alt="Built by WorthDoing.ai" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic v2" />
  <img src="https://img.shields.io/badge/Typer-CLI-009688?style=for-the-badge" alt="Typer CLI" />
  <img src="https://img.shields.io/badge/httpx-Async-FF6B35?style=for-the-badge" alt="httpx" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT License" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Capabilities-7+-green?style=flat-square" alt="7+ Capabilities" />
  <img src="https://img.shields.io/badge/Executors-4-orange?style=flat-square" alt="4 Executors" />
  <img src="https://img.shields.io/badge/Validation-First--Class-blue?style=flat-square" alt="Validation First-Class" />
  <img src="https://img.shields.io/badge/Cache-Built--in-purple?style=flat-square" alt="Cache Built-in" />
  <img src="https://img.shields.io/badge/Auth-Centralized-red?style=flat-square" alt="Auth Centralized" />
  <img src="https://img.shields.io/badge/CLI-Ready-brightgreen?style=flat-square" alt="CLI Ready" />
  <img src="https://img.shields.io/badge/Status-Active%20Development-brightgreen?style=flat-square" alt="Active Development" />
  <img src="https://img.shields.io/badge/PyPI-coming%20soon-lightgrey?style=flat-square&logo=pypi" alt="PyPI coming soon" />
</p>

---

## Overview

**WorthDoing Capabilities** is a structured, production-grade Python package for building portable, composable, and reusable agent capabilities. It is not a utility library. It is not an API wrapper. It is not another agent toolkit that stitches together a dozen third-party SDKs behind a thin facade.

Every capability in this package is defined by a **declarative YAML contract** that specifies its inputs, outputs, authentication requirements, caching behavior, and planner hints. A **runtime engine** discovers, validates, and executes capabilities through a unified interface. A **registry** indexes them. **Executors** handle the actual work — whether that means calling a REST API, running a Python function, executing a shell command, or chaining multiple capabilities into a workflow.

The result is a system where capabilities are first-class citizens: inspectable, testable, cacheable, and auditable — individually and as part of larger agent pipelines.

### Why WorthDoing Capabilities?

| Problem | Solution |
|---------|----------|
| Agent toolkits are collections of loose wrappers with no unifying architecture | **Structured capability architecture** with contracts, registry, and runtime engine |
| No standard for describing what a capability does, what it needs, and what it returns | **Declarative YAML contracts** with input/output schemas, auth requirements, cache policies, and planner hints |
| Auth scattered across implementations — every tool handles credentials differently | **Centralized auth resolver** that resolves credentials once and injects them uniformly |
| No caching strategy — every call hits the network regardless of determinism | **Built-in deterministic caching** per capability with configurable TTL and key strategies |
| Hard to test individual capabilities in isolation | **Per-capability test structure** with dedicated fixtures and mock support |
| No execution audit trail — impossible to debug what happened after the fact | **Standardized execution records** for every run with inputs, outputs, timing, and status |

---

## Architecture

The system is organized into five distinct layers, each with a clear responsibility boundary:

```
+-------------------------------------------------------------------+
|                        CLI Interface (Typer)                       |
|  wdcap list | inspect | run | validate | history                  |
+-------------------------------------------------------------------+
|                     Python API (CapabilityRuntime)                 |
|  list_capabilities | inspect | run | validate | get_history       |
+-------------------------------------------------------------------+
|                       Runtime Engine Layer                         |
|  Discovery | Contract Loading | Validation | Execution Dispatch   |
+-------------------------------------------------------------------+
|                        Executor Layer                              |
|  HTTP Executor | Python Executor | Shell Executor | Workflow Exec |
+-------------------------------------------------------------------+
|                      Foundation Services                          |
|  Validation | Auth Resolver | Cache Store | Memory / Records      |
+-------------------------------------------------------------------+
```

### Layer Responsibilities

| Layer | Role |
|-------|------|
| **CLI Interface** | Human-facing commands powered by Typer and Rich. Thin wrapper over the Python API. |
| **Python API** | The primary programmatic interface. Instantiate `CapabilityRuntime`, call methods. |
| **Runtime Engine** | Discovers capabilities from the filesystem, loads and validates contracts, dispatches execution to the correct executor. |
| **Executor Layer** | Four specialized executors that know how to perform the actual work for each capability type. |
| **Foundation Services** | Cross-cutting concerns: input/output validation (Pydantic v2), credential resolution, deterministic caching, and execution record keeping. |

---

## Built-in Capabilities

WorthDoing Capabilities ships with 7 production-ready capabilities across 5 categories:

| Capability | Category | Executor | Description | Auth | Cache |
|------------|----------|----------|-------------|------|-------|
| `web_search` | Search | HTTP | Search the web via a configurable search API and return structured results | API Key | 5 min TTL |
| `url_fetch` | Data Retrieval | HTTP | Fetch and extract content from a URL — raw HTML, text, or parsed metadata | None | 10 min TTL |
| `market_data.quote` | Finance | HTTP | Retrieve real-time stock/crypto quotes with price, volume, and change data | API Key | 1 min TTL |
| `shell.run` | System | Shell | Execute a local shell command with sanitization, timeout, and output capture | None | No cache |
| `file.read` | System | Python | Read local file contents with encoding detection and size limits | None | No cache |
| `embeddings.generate` | AI / ML | HTTP | Generate vector embeddings for text via a configurable embeddings API | API Key | 30 min TTL |
| `workflow.simple_chain` | Orchestration | Workflow | Chain multiple capabilities sequentially, piping outputs into inputs | Inherited | No cache |

Each capability lives in its own directory under `src/worthdoing_capabilities/capabilities/` with a YAML contract, executor implementation, and dedicated test directory.

---

## Capability Contract Format

Every capability is defined by a declarative YAML contract. The contract is the single source of truth for what a capability does, what it needs, what it returns, how it authenticates, how it caches, and how a planner should reason about it.

### Full Example: `market_data.quote`

```yaml
capability:
  name: market_data.quote
  version: "1.0.0"
  description: "Retrieve real-time stock or crypto quote data"
  category: finance
  executor: http

input:
  schema:
    type: object
    properties:
      symbol:
        type: string
        description: "Ticker symbol (e.g., AAPL, BTC-USD)"
      interval:
        type: string
        enum: ["1d", "5d", "1mo"]
        default: "1d"
    required:
      - symbol

output:
  schema:
    type: object
    properties:
      symbol:
        type: string
      price:
        type: number
      change:
        type: number
      change_percent:
        type: number
      volume:
        type: integer
      timestamp:
        type: string
        format: datetime

auth:
  method: api_key
  env_var: MARKET_DATA_API_KEY
  header: X-API-Key

cache:
  enabled: true
  ttl_seconds: 60
  key_fields:
    - symbol
    - interval

planner:
  use_when: "User asks for stock price, crypto price, market quote, or ticker data"
  cost: low
  latency: low
  deterministic: false
```

### Contract Field Groups

| Group | Purpose |
|-------|---------|
| **capability** | Identity — name, version, description, category, and which executor to use |
| **input** | JSON Schema defining the expected input, including required fields and defaults |
| **output** | JSON Schema defining the guaranteed output structure |
| **auth** | Authentication method, environment variable name, and how to inject credentials |
| **cache** | Whether caching is enabled, TTL, and which input fields form the cache key |
| **planner** | Hints for AI planners — when to use this capability, expected cost, latency, and determinism |

---

## Executor System

Executors are the runtime components that know how to actually perform the work described by a capability contract. The runtime engine dispatches to the correct executor based on the `executor` field in the contract.

| Executor | Type | Description | Use Cases |
|----------|------|-------------|-----------|
| **HTTP** | `http` | Makes REST API calls using httpx. Supports GET/POST, headers, query params, JSON bodies, and async execution. Auth credentials are injected automatically. | `web_search`, `url_fetch`, `market_data.quote`, `embeddings.generate` |
| **Python** | `python` | Calls internal Python functions directly. The function path is specified in the contract. Runs in-process with full access to the Python environment. | `file.read`, custom internal logic |
| **Shell** | `shell` | Executes local shell commands with input sanitization, configurable timeouts, and stdout/stderr capture. Commands are validated against an allowlist. | `shell.run`, local tooling |
| **Workflow** | `workflow` | Chains multiple capabilities sequentially. Each step's output can be mapped into the next step's input. Execution records are created for the workflow and each sub-step. | `workflow.simple_chain`, multi-step pipelines |

### Executor Contract

All executors implement a common interface:

```python
class BaseExecutor:
    async def execute(
        self,
        contract: CapabilityContract,
        inputs: dict,
        auth: AuthContext | None,
        cache: CacheStore,
    ) -> ExecutionResult:
        ...
```

---

## Python API

The primary interface for using WorthDoing Capabilities programmatically:

```python
from worthdoing_capabilities import CapabilityRuntime

# Initialize the runtime — discovers and loads all capability contracts
runtime = CapabilityRuntime()

# List all registered capabilities
capabilities = runtime.list_capabilities()
for cap in capabilities:
    print(f"{cap.name} ({cap.category}) — {cap.description}")

# Inspect a specific capability's full contract
contract = runtime.inspect("market_data.quote")
print(contract.input.schema)
print(contract.auth.method)
print(contract.cache.ttl_seconds)

# Run a capability
result = runtime.run("market_data.quote", {"symbol": "AAPL"})
print(result.output)       # {"symbol": "AAPL", "price": 198.50, ...}
print(result.cached)       # False (first call)
print(result.duration_ms)  # 230

# Run again — hits cache
result2 = runtime.run("market_data.quote", {"symbol": "AAPL"})
print(result2.cached)      # True

# Validate a contract file
issues = runtime.validate("capabilities/market_data/capability.yaml")
print(issues)              # [] (no issues)

# Get execution history
history = runtime.get_history()
for record in history:
    print(f"{record.capability} — {record.status} — {record.duration_ms}ms")
```

### Async Support

All executors support async execution via httpx:

```python
import asyncio
from worthdoing_capabilities import CapabilityRuntime

async def main():
    runtime = CapabilityRuntime()
    result = await runtime.run_async("web_search", {"query": "WorthDoing AI"})
    print(result.output)

asyncio.run(main())
```

---

## CLI

WorthDoing Capabilities includes a full command-line interface powered by Typer and Rich:

### List All Capabilities

```bash
wdcap list
```

```
 Capability              Category        Executor   Cache    Auth
 ───────────────────────────────────────────────────────────────────
 web_search               search          http       5m TTL   api_key
 url_fetch                data            http       10m TTL  none
 market_data.quote        finance         http       1m TTL   api_key
 shell.run                system          shell      none     none
 file.read                system          python     none     none
 embeddings.generate      ai              http       30m TTL  api_key
 workflow.simple_chain    orchestration   workflow   none     inherited
```

### Inspect a Capability

```bash
wdcap inspect market_data.quote
```

```
 market_data.quote v1.0.0
 ──────────────────────────
 Description:  Retrieve real-time stock or crypto quote data
 Category:     finance
 Executor:     http
 Auth:         api_key (MARKET_DATA_API_KEY)
 Cache:        60s TTL on [symbol, interval]

 Input Schema:
   symbol     string   required   Ticker symbol (e.g., AAPL, BTC-USD)
   interval   string   optional   1d | 5d | 1mo (default: 1d)

 Output Schema:
   symbol          string
   price           number
   change          number
   change_percent  number
   volume          integer
   timestamp       datetime
```

### Run a Capability

```bash
wdcap run market_data.quote --input '{"symbol": "AAPL"}'
```

```json
{
  "symbol": "AAPL",
  "price": 198.50,
  "change": 2.35,
  "change_percent": 1.20,
  "volume": 54200000,
  "timestamp": "2026-04-13T16:00:00Z"
}
```

### Validate a Contract

```bash
wdcap validate capabilities/market_data/capability.yaml
```

```
 Validating capabilities/market_data/capability.yaml...
 [PASS] Contract structure valid
 [PASS] Input schema valid
 [PASS] Output schema valid
 [PASS] Auth configuration valid
 [PASS] Cache configuration valid
 [PASS] Planner hints present
 All checks passed.
```

### View Execution History

```bash
wdcap history
```

```
 Timestamp              Capability           Status   Duration   Cached
 ──────────────────────────────────────────────────────────────────────
 2026-04-13 14:32:01    market_data.quote    success  230ms      no
 2026-04-13 14:32:05    market_data.quote    success  2ms        yes
 2026-04-13 14:33:12    web_search           success  890ms      no
 2026-04-13 14:35:44    shell.run            success  45ms       no
```

---

## Project Structure

```
worthdoing-capabilities/
├── pyproject.toml                                    # Package config, deps, CLI entry point
├── README.md                                         # This file
├── LICENSE                                           # MIT License
├── .gitignore                                        # Python ignores
├── docs/                                             # Documentation
├── examples/                                         # Usage examples
├── scripts/                                          # Dev & build scripts
├── src/
│   └── worthdoing_capabilities/
│       ├── __init__.py                               # Public API exports
│       ├── cli/
│       │   └── main.py                               # Typer CLI application
│       ├── contracts/
│       │   ├── __init__.py
│       │   ├── models.py                             # Pydantic models for contracts
│       │   └── loader.py                             # YAML contract loader
│       ├── registry/
│       │   └── __init__.py                           # Capability discovery & indexing
│       ├── runtime/
│       │   └── __init__.py                           # Runtime engine (orchestrator)
│       ├── executors/
│       │   └── __init__.py                           # HTTP, Python, Shell, Workflow executors
│       ├── validation/
│       │   ├── __init__.py
│       │   └── validator.py                          # Input/output validation (Pydantic v2)
│       ├── auth/
│       │   ├── __init__.py
│       │   └── resolver.py                           # Centralized auth credential resolver
│       ├── cache/
│       │   ├── __init__.py
│       │   └── store.py                              # Deterministic cache store
│       ├── memory/
│       │   ├── __init__.py
│       │   └── record.py                             # Execution record model
│       └── capabilities/                             # Built-in capabilities
│           ├── web_search/
│           │   ├── capability.yaml                   # Contract
│           │   ├── executor.py                       # Implementation
│           │   └── tests/                            # Capability-specific tests
│           ├── url_fetch/
│           │   ├── capability.yaml
│           │   ├── executor.py
│           │   └── tests/
│           ├── market_data/
│           │   ├── capability.yaml
│           │   ├── executor.py
│           │   └── tests/
│           ├── shell/
│           │   ├── capability.yaml
│           │   ├── executor.py
│           │   └── tests/
│           ├── file_read/
│           │   ├── capability.yaml
│           │   ├── executor.py
│           │   └── tests/
│           ├── embeddings/
│           │   ├── capability.yaml
│           │   ├── executor.py
│           │   └── tests/
│           └── workflow/
│               ├── capability.yaml
│               ├── executor.py
│               └── tests/
└── tests/
    ├── fixtures/                                     # Shared test fixtures
    ├── unit/                                         # Unit tests
    └── integration/                                  # Integration tests
```

---

## Installation

### From Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/Worth-Doing/worthdoing-capabilities.git
cd worthdoing-capabilities

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
wdcap list
```

### Requirements

- **Python 3.11+** (3.12 and 3.13 also supported)
- **pip** 23+

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pydantic | >=2.0 | Contract models, input/output validation |
| httpx | >=0.27 | Async HTTP client for API-based capabilities |
| typer | >=0.12 | CLI framework |
| pyyaml | >=6.0 | YAML contract parsing |
| rich | >=13.0 | Terminal formatting and tables |

---

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=worthdoing_capabilities --cov-report=term-missing
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Tests for a specific capability
pytest src/worthdoing_capabilities/capabilities/market_data/tests/

# Run with verbose output
pytest -v
```

### Test Structure

| Directory | Purpose |
|-----------|---------|
| `tests/unit/` | Unit tests for contracts, registry, runtime, executors, validation, auth, cache, memory |
| `tests/integration/` | End-to-end tests that exercise the full runtime pipeline |
| `tests/fixtures/` | Shared test data — sample contracts, mock responses, fixture configs |
| `capabilities/*/tests/` | Per-capability tests co-located with their implementations |

---

## Design Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Capability-First** | Capabilities are the primary abstraction. Everything else exists to serve them. The system is not organized around tools, functions, or endpoints — it is organized around capabilities with contracts. |
| 2 | **Runtime Separation** | The contract (what a capability does) is strictly separated from the runtime (how it gets executed). You can inspect, validate, and reason about capabilities without executing them. |
| 3 | **Declarative Contracts** | YAML contracts are the single source of truth. No magic decorators, no implicit registration, no convention-over-configuration guessing. If it is not in the contract, it does not exist. |
| 4 | **Small Focused Modules** | Every module has one job. The auth resolver resolves auth. The cache store caches. The validator validates. No god objects, no kitchen-sink utilities. |
| 5 | **Future Extensibility** | The executor interface, contract format, and registry are all designed to be extended without modifying existing code. New executors, new capabilities, new auth methods — all additive. |
| 6 | **Strong Validation** | Inputs and outputs are validated against their schemas on every execution. Bad data fails fast with clear error messages, not silently deep in a third-party API call. |
| 7 | **Reusability** | Capabilities are portable. A capability built here can be used by any agent, any pipeline, any orchestrator that speaks the contract format. No vendor lock-in, no framework coupling. |

---

## Roadmap

### Q2 2026 ![Q2 2026](https://img.shields.io/badge/Q2-2026-blue?style=flat-square)

- [ ] PyPI publication — `pip install worthdoing-capabilities`
- [ ] Additional capabilities: `llm.complete`, `code.execute`, `pdf.extract`, `calendar.events`
- [ ] Enhanced CLI with `wdcap init` scaffolding for new capabilities
- [ ] OpenAPI-to-contract generator — auto-generate contracts from OpenAPI specs
- [ ] Comprehensive documentation site

### Q3 2026 ![Q3 2026](https://img.shields.io/badge/Q3-2026-purple?style=flat-square)

- [ ] External capability packages — install third-party capabilities via pip
- [ ] Remote registries — discover and pull capabilities from hosted registries
- [ ] Capability versioning and migration support
- [ ] Webhook executor — trigger and wait for external webhooks
- [ ] Rate limiting and circuit breaker per capability

### Q4 2026 ![Q4 2026](https://img.shields.io/badge/Q4-2026-orange?style=flat-square)

- [ ] Capability marketplace — publish, discover, and install community capabilities
- [ ] Signed contracts — cryptographic verification of capability provenance
- [ ] Planner integration — native integration with WorthDoing AI agent planner
- [ ] Distributed execution — run capabilities across multiple nodes
- [ ] Real-time capability monitoring dashboard

---

## Contributing

<p align="center">
  <a href="https://github.com/Worth-Doing/worthdoing-capabilities/pulls">
    <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge" alt="PRs Welcome" />
  </a>
  <a href="https://github.com/Worth-Doing/worthdoing-capabilities/issues">
    <img src="https://img.shields.io/badge/Issues-Welcome-blue?style=for-the-badge" alt="Issues Welcome" />
  </a>
</p>

Contributions are welcome. This is a serious infrastructure project and there is a lot to build.

### Priority Areas

- New capability implementations (especially data retrieval, AI/ML, and productivity categories)
- Executor improvements (retry logic, connection pooling, streaming support)
- Contract format enhancements
- Test coverage expansion
- Documentation and usage examples

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-capability`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Ensure code quality (`ruff check . && mypy src/`)
6. Commit your changes (`git commit -m 'Add new capability'`)
7. Push to the branch (`git push origin feature/new-capability`)
8. Open a Pull Request

---

## License

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License" />
</p>

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <img src="https://raw.githubusercontent.com/Worth-Doing/brand-assets/main/png/variants/03-icon-only.png" alt="WorthDoing.ai" width="80" />
  <br /><br />
  <strong>Built with purpose by <a href="https://worthdoing.ai">WorthDoing AI</a></strong>
  <br />
  <em>AI That Decides What Matters</em>
  <br /><br />
  <a href="https://worthdoing.ai">
    <img src="https://img.shields.io/badge/Web-worthdoing.ai-blue?style=flat-square" alt="Website" />
  </a>
  <a href="https://github.com/Worth-Doing">
    <img src="https://img.shields.io/badge/GitHub-Worth--Doing-181717?style=flat-square&logo=github" alt="GitHub" />
  </a>
  <a href="mailto:admin@worthdoing.ai">
    <img src="https://img.shields.io/badge/Email-admin%40worthdoing.ai-red?style=flat-square&logo=gmail&logoColor=white" alt="Email" />
  </a>
</p>
