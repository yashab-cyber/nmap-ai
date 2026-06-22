# NMAP-AI Roadmap

## Decision log

- **2026-06-07** — Phase 0 fork: chose **heuristic-honest** path. Rationale: the current `AIEngine` and `AIScriptGenerator` are entirely rule-based; no ML models exist on disk despite `requirements.txt` carrying ~3GB of TensorFlow/PyTorch/transformers. Cleanup is cheaper than implementing real ML, and the project is more useful as an honest heuristic scanner than a misleading "AI" one. Real ML can be revisited as a Phase 3 extension once the heuristic baseline is solid.

---

Findings that shaped this roadmap: tests exist (`tests/conftest.py`, `tests/unit/test_vulnerability_detector.py`, `tests/integration/test_api_endpoints.py`) — there's a scaffold to build on. The generated NSE scripts are syntactically valid Lua templates but the vulnerability checks themselves are stubs (`-- Add actual test logic here`). The `AIEngine` is rule-based, not ML, despite `.pkl` paths in config and heavy ML deps in `requirements.txt`.

## Phase 0: Truth in advertising (1–2 days, blocks everything else)

The single biggest problem: the README and feature list promise things the code doesn't do. Pick a direction before building more.

| Item | Verify by |
|---|---|
| ~~Decide: real ML or heuristic engine?~~ **DONE 2026-06-07** — chose heuristic (see Decision log) | ✅ |
| ~~Remove `tensorflow`, `torch`, `transformers` (and other unused deps) from `requirements.txt`; rewrite README "AI Capabilities" section as "Heuristic-based scan intelligence"~~ **DONE 2026-06-07** (commit 8e900eb) — also aligned `pyproject.toml`/`setup.py` deps & extras, fixed broken console-script entry points | ✅ |
| ~~Strip non-existent `.pkl` model paths from `AIConfig` in `config.py`~~ **DONE 2026-06-07** (commit 8e900eb) | ✅ |

## Phase 1: Make the existing surface honest (~1 week)

Finish or remove the half-built pieces.

| Item | Verify by |
|---|---|
| ~~Implement or delete `_export_xml` / `_export_csv` in `scanner.py` (currently `pass`)~~ **DONE 2026-06-07** (commit 0c46a31) — both implemented + unit-tested | ✅ |
| ~~Generated NSE scripts: replace `-- Add actual test logic here` stubs with working HTTP requests (xss, sql_injection)~~ **DONE 2026-06-07** (commit a73da0d) — real http.get logic; also fixed a Lua 5.3 `math.random(float)` crash; all 6 variants parse as valid Lua. *Note: not yet run against live `scanme.nmap.org` (no nmap/Lua runtime in dev env); validated via `luaparser`.* | ✅ (parse-validated) |
| ~~Web API: implement or strip the 501 stubs~~ **DONE 2026-06-07** (commit 15b45f4) — stripped the two HTTP 501 stub endpoints; extracted `create_app()` + module-level `app` for testability | ✅ |
| ~~GUI: build a working scan form or make `--gui` honest~~ **DONE 2026-06-07** (commit c456923) — chose honest stub: `--gui` exits non-zero with a pointer to the CLI (no fake window) | ✅ |

## Phase 2: Test foundation (~1 week, parallel with Phase 1)

You can't refactor what you can't verify.

| Item | Verify by |
|---|---|
| ~~Repair the broken test scaffold so the suite collects at all~~ **DONE 2026-06-07** (commit 15b45f4) — fixed `Config` imports, invalid pytest hook, ML import gate; rewrote API integration test to the real contract | ✅ |
| ~~Add `tests/unit/test_scanner.py` covering `NmapAIScanner` with a mocked `nmap.PortScanner`~~ **DONE 2026-06-07** (commit 0c46a31) — happy path, invalid target/ports, exporters, save dispatch | ✅ (async path still TODO) |
| ~~Add `tests/unit/test_ai_engine.py` covering `optimize_scan_arguments`, `_analyze_target_result`, `create_scan_plan`~~ **DONE 2026-06-07** — `core/ai_engine.py` coverage ~96% | ✅ |
| ~~Add `tests/unit/test_config.py` covering YAML round-trip + the `field(default_factory=...)` fix in commit c61d49f (regression guard)~~ **DONE 2026-06-07** — YAML+JSON round-trip equal; instance-independence guard | ✅ |
| ~~Wire up CI: GitHub Actions running `pytest`, `black --check`, `flake8`, `mypy` on PRs~~ **DONE 2026-06-07** — `.github/workflows/ci.yml`: pytest **gating** (py3.9–3.12), flake8 **gating**, black/mypy advisory | ✅ |

**Lint/type debt (follow-up):** flake8 is now **clean and gating** on `nmap_ai` + `tests` (commit pending). black (~reformat) and mypy (strict) remain **advisory** — flip each to a gating job in `ci.yml` as it reaches green. `.flake8` is black-compatible (max-line-length 100; ignores E203/W503/E501) and excludes `examples/`.

**Dead code:** ~~`nmap_ai/cli/commands/`~~ **DELETED 2026-06-07** — was a parallel CLI importing the non-existent `Config`, wired into nothing (real CLI is `nmap_ai/cli/main.py`). Note: several `examples/*.py` still import `Config`; they're excluded from flake8 and not part of the import surface — repair or delete in a later pass.

## Phase 3: Real intelligence layer (~2–4 weeks, only if Phase 0 picked "real ML")

This is the work that justifies the "AI" name.

| Item | Verify by |
|---|---|
| **Port prediction**: train a sklearn classifier (RandomForest / LightGBM) on a public port-scan dataset (e.g. CICIDS2017) to predict likely-open ports given host fingerprint hints | Model file in `models/`, integration test shows `optimize_scan_arguments` produces different port lists for "web-like" vs "db-like" targets |
| **Vulnerability classification**: replace the if/elif tree in `_analyze_target_result` with a model trained on CVE/service mappings | Detection precision/recall measured on a labeled test set, documented in `docs/ai-models.md` |
| **Script generation**: this is the hardest — a real solution needs either a fine-tuned code model or a structured grammar. If LLM-based, integrate through a provider SDK rather than bundling transformers | One generated script for each of 3 target types passes `nmap --script-help` without errors |

## Phase 4: Operational polish (~1 week)

Lower priority but unblock real use.

| Item | Verify by |
|---|---|
| ~~Persist scan history beyond process lifetime~~ **DONE 2026-06-07** — `core/history.py` `ScanHistoryStore` (stdlib sqlite3, no ORM) wired to `DatabaseConfig.url`; default now `~/.nmap-ai/history.db` (cwd-independent). A fresh scanner over the same DB sees prior scans (tested). | ✅ |
| ~~Hardcoded `secret_key` in `WebConfig` — load from env, fail fast on default~~ **DONE 2026-06-07** — `NMAP_AI_SECRET_KEY` env > config; `web_main` exits non-zero in non-debug mode while the default key is in effect. | ✅ |
| ~~Plugin discovery has no default directory~~ **DONE 2026-06-07** — `default_plugin_dirs()` (`~/.nmap-ai/plugins`, `./plugins`) used by `PluginManager()`; working `examples/plugins/markdown_report_plugin.py` + README; loaded end-to-end in tests. | ✅ |

> **Note (SQLAlchemy):** the original plan said "SQLAlchemy is already in requirements.txt." It was removed in Phase 0 (unused, heavy). History uses stdlib `sqlite3` instead — same approach as `vulnerability_detector.py`, no new dependency.

## Sequencing

```
Phase 0 ─┐
         ├─► Phase 1 ──┐
Phase 2 ─┘             ├─► Phase 3 (only if Phase 0 chose ML)
                       └─► Phase 4
```

Phase 0 is non-negotiable — the credibility gap will sink contributor goodwill if left alone. Phase 2 should run in parallel because the existing code has zero regression protection. Phase 3 is the most exciting but also where ambitious projects die; ship one small real model before promising a suite.
