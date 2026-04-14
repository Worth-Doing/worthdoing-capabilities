# Claude.md

## Project Identity

This is **worthdoing-capabilities** — the official capability package by **WorthDoing AI**.

- **Owner**: WorthDoing AI (https://worthdoing.ai)
- **GitHub Org**: Worth-Doing
- **Package name**: `worthdoing-capabilities`
- **CLI command**: `wdcap`
- **Python import**: `from worthdoing_capabilities import ...`
- **License**: MIT
- **Status**: Active development

---

## What This Is

A production-grade, structured Python package for defining, registering, validating, and executing **agent capabilities**.

This is NOT:
- A utility library
- An API wrapper
- A LangChain/CrewAI/AutoGen plugin
- A toy or prototype

This IS:
- A standalone capability system with contracts, executors, a registry, a runtime, caching, auth, validation, and memory
- Designed to be used by any agent framework — or no framework at all
- Built from scratch by WorthDoing AI

---

## Architecture

```
src/worthdoing_capabilities/
├── __init__.py              # Public API: CapabilityRuntime, models
├── cli/main.py              # Typer CLI app (wdcap command)
├── contracts/               # YAML contract models + loader
│   ├── models.py            # Pydantic v2 models for capability contracts
│   └── loader.py            # Load + parse YAML contracts
├── registry/                # Capability discovery and indexing
├── runtime/                 # Execution engine
├── executors/               # HTTP, Python, Shell, Workflow executors
├── validation/              # Input/output schema validation
├── auth/                    # Centralized auth resolver
├── cache/                   # Deterministic caching per capability
├── memory/                  # Execution records
└── capabilities/            # Built-in capabilities (each with YAML contract)
    ├── web_search/
    ├── url_fetch/
    ├── market_data/
    ├── shell/
    ├── file_read/
    ├── embeddings/
    └── workflow/
```

---

## Core Concepts

### Capability Contract (YAML)
Every capability has a `capability.yaml` that declares:
- **name** and **version**
- **input/output schemas** (JSON Schema format)
- **executor type** (http, python, shell, workflow)
- **auth requirements** (method, env var, header)
- **cache config** (TTL, key fields)
- **planner hints** (when to use, cost, latency, determinism)

### Registry
Discovers capabilities from the filesystem, indexes them by name, provides lookup.

### Runtime Engine
The orchestrator. Takes a capability name + inputs, resolves auth, checks cache, validates input, dispatches to the correct executor, validates output, records execution, returns result.

### Executors
- **HTTP**: REST API calls via httpx (async)
- **Python**: Direct function calls
- **Shell**: Sanitized local commands
- **Workflow**: Chains capabilities sequentially

### Auth Resolver
Resolves credentials from environment variables. Injects into executor context.

### Cache Store
Deterministic caching keyed on capability name + specified input fields. Respects TTL.

### Validation
Pydantic v2 schema validation on both inputs and outputs.

### Memory / Records
Every execution produces an `ExecutionRecord` with capability name, inputs, outputs, duration, status, cached flag, timestamp.

---

## Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package metadata, dependencies, CLI entry point, tool config |
| `src/worthdoing_capabilities/__init__.py` | Public exports |
| `src/worthdoing_capabilities/contracts/models.py` | Pydantic models for the contract format |
| `src/worthdoing_capabilities/contracts/loader.py` | YAML parsing and contract instantiation |
| `src/worthdoing_capabilities/registry/__init__.py` | Capability discovery and lookup |
| `src/worthdoing_capabilities/runtime/__init__.py` | Main execution engine |
| `src/worthdoing_capabilities/executors/__init__.py` | All executor implementations |
| `src/worthdoing_capabilities/validation/validator.py` | Schema validation logic |
| `src/worthdoing_capabilities/auth/resolver.py` | Auth credential resolution |
| `src/worthdoing_capabilities/cache/store.py` | Cache implementation |
| `src/worthdoing_capabilities/memory/record.py` | ExecutionRecord model |
| `src/worthdoing_capabilities/cli/main.py` | Typer CLI commands |

---

## Built-in Capabilities

| Name | Executor | Auth | Cache |
|------|----------|------|-------|
| `web_search` | http | API key | 5 min |
| `url_fetch` | http | None | 10 min |
| `market_data.quote` | http | API key | 1 min |
| `shell.run` | shell | None | None |
| `file.read` | python | None | None |
| `embeddings.generate` | http | API key | 30 min |
| `workflow.simple_chain` | workflow | Inherited | None |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Models | Pydantic v2 |
| HTTP | httpx (async) |
| CLI | Typer + Rich |
| Config | YAML (PyYAML) |
| Testing | pytest + pytest-asyncio |
| Linting | Ruff |
| Types | mypy (strict) |
| Build | Hatchling |

---

## Code Standards

- **Type hints everywhere** — strict mypy compliance
- **Pydantic v2 models** — no raw dicts for structured data
- **Async-first executors** — sync wrappers provided for convenience
- **Ruff for linting** — line length 100, isort, bugbear, simplify
- **Tests next to code** — each capability has co-located tests
- **No print statements** — use Rich console or logging
- **No wildcard imports** — explicit imports only
- **Docstrings on public APIs** — Google style

---

## CLI Commands

```bash
wdcap list                           # List all capabilities
wdcap inspect <name>                 # Show full contract details
wdcap run <name> --input '{...}'     # Execute a capability
wdcap validate <path>                # Validate a contract YAML
wdcap history                        # Show execution history
```

---

## Testing

```bash
pytest                               # Run all tests
pytest tests/unit/                   # Unit tests
pytest tests/integration/            # Integration tests
pytest --cov=worthdoing_capabilities # With coverage
```

---

## How to Add a New Capability

1. Create a directory under `src/worthdoing_capabilities/capabilities/<name>/`
2. Write `capability.yaml` — the contract
3. Write `executor.py` — the implementation
4. Create `tests/` directory with test files
5. The registry auto-discovers it on next runtime init

---

## What "Production-Grade" Means Here

- Every input is validated before execution
- Every output is validated after execution
- Every execution is recorded with timing and status
- Auth is resolved centrally, not scattered
- Caching is deterministic and configurable
- Errors produce structured results, not raw exceptions
- The contract is always the source of truth
- The system is testable at every layer

Build it with that level of seriousness.
