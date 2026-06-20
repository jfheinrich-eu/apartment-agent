# GitHub Copilot Instructions – wohnung_agent

## Project overview

Python 3.11+ apartment search agent. Adapter-based architecture:
- `wohnung_agent/adapters/` – data source adapters (all implement `search(profile) -> list[Apartment]`)
- `wohnung_agent/models.py` – Pydantic data models
- `wohnung_agent/filter_engine.py` – scoring and filtering
- `wohnung_agent/database.py` – SQLite persistence
- `wohnung_agent/runner.py` – search orchestration
- `wohnung_agent/main.py` – CLI entry point
- `tests/` – pytest test suite

Dependencies: `requests`, `beautifulsoup4`, `pydantic`, `PyYAML`, `APScheduler`.  
All code is in **English** (variable names, function names, comments, docstrings).

---

## Custom commands

### /check-security

Perform a full security review of the entire project.

1. **Dependencies** – check all entries in `pyproject.toml` for known CVEs and supply-chain risks. Report outdated packages with known vulnerabilities.
2. **Secrets & credentials** – scan all files for hardcoded tokens, passwords, API keys, or private URLs. Flag any `.env` references that are committed.
3. **OWASP Top 10 patterns** – look for injection risks (SQL, command, path traversal), insecure deserialization, improper error handling that leaks internals, and missing input validation at system boundaries.
4. **HTTP requests** – verify that all outgoing `requests` calls validate TLS (`verify=True` by default), use timeouts, and do not follow untrusted redirects blindly.
5. **File & database access** – check that file paths are not user-controlled without sanitization, and that SQLite queries use parameterized statements.
6. **Output** – produce a prioritized list: **Critical / High / Medium / Low / Info**. For each finding state file, line, description, and recommended fix.

---

### /check-quality

Perform a full code-quality review of the entire project.

1. **Language** – all identifiers (variables, functions, classes, modules), comments, and docstrings must be in **English**. Flag any German or mixed-language names.
2. **Naming** – names must be descriptive and self-documenting. Flag:
   - Single-character variables outside loop counters (`i`, `j`, `k`, `n`) and short-lived accumulators
   - Abbreviations that are not universally understood (`tmp`, `val`, `mgr`, `lst`, etc.)
   - Boolean variables not prefixed with `is_`, `has_`, `can_`, or `should_`
3. **Clean Code**
   - Functions do one thing; flag functions longer than ~30 lines or with more than 3 levels of nesting
   - No magic numbers or magic strings – constants should be named
   - Dead code, unreachable branches, or commented-out code blocks
4. **Best practices**
   - Type hints on all public functions and methods
   - Pydantic models used for external data; no raw `dict` passed across module boundaries
   - Exceptions caught at the narrowest useful scope; bare `except Exception` only with explicit logging
   - No mutable default arguments
5. **Robustness & error handling**
   - All I/O operations (file, network, DB) wrapped with specific exception handling
   - Logged errors include enough context (URL, file path, relevant values) to diagnose without a debugger
6. **Maintainability**
   - Public functions and classes have docstrings explaining *why*, not just *what*
   - No copy-paste duplication – flag code blocks that appear more than once
   - Test coverage: each adapter, filter rule, and model field should have at least one test
7. **Configuration consistency** – compare `config/search_profile.example.yml` and `config/search_profile.yml` against the actual config keys consumed in `config_loader.py`, `main.py`, and all adapter `__init__` methods. Flag:
   - Keys present in the example but missing from the live config
   - Keys present in the live config but missing from the example (undocumented options)
   - Keys referenced in code but absent from both config files (unset defaults with no documentation)
   - Adapter config sections (`demo`, `immowelt`, …) whose available options are not fully reflected in the example
8. **Output** – produce a categorized list grouped by file. For each finding state line, category, description, and recommended improvement.
