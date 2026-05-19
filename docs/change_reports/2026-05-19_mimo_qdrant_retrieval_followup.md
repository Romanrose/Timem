# 2026-05-19 Mimo / Qdrant / Retrieval Follow-up

## Previous record location

The previous round of changes was not stored in a standalone markdown report.
The durable records were:

- Git commit: `875fa8e` (`Add Mimo provider and fix Locomo retrieval config`)
- Retrieval test outputs under `/logs/tests/`

This file is the formal follow-up report for changes made after that commit.

## Previous submission (`875fa8e`)

Commit:

- `875fa8e` - `Add Mimo provider and fix Locomo retrieval config`

Files changed in that submission:

- `/config/settings.yaml`
- `/llm/llm_manager.py`
- `/llm/mimo_adapter.py`
- `/config/datasets/locomo/qa_prompts.yaml`
- `/config/datasets/locomo/eval_prompt.yaml`
- `/config/datasets/locomo/retrieval_config.yaml`

What that submission changed:

- Added `llm.providers.mimo` to the main settings
- Switched `llm.default_provider` from `openai` to `mimo`
- Added `MimoAdapter` as a first-class adapter under `/llm/mimo_adapter.py`
- Added a `mimo` branch to `/llm/llm_manager.py`
- Switched Locomo QA generation config from `openai / gpt-4o-mini` to
  `mimo / mimo-v2-omni`
- Switched Locomo evaluation config from `openai / gpt-4o-mini` to
  `mimo / mimo-v2-omni`
- Switched Locomo retrieval config to use `mimo-v2-omni`
- Changed vector dimension in settings from `2048` to `1024`

Why that submission mattered:

- It established Xiaomi Mimo as a supported runtime provider in the project
- It aligned the Locomo experiment configs with the intended debug model
- It fixed the provider/model mismatch that had blocked retrieval and evaluation
- It corrected the configured vector size so Qdrant could match the actual
  embedding output dimension

## Scope

This follow-up focused on making the Locomo debug path reliable enough to run a
single-conversation retrieval test end-to-end with:

- Xiaomi Mimo as the active LLM provider
- PostgreSQL as the source of truth for memories
- Qdrant as the working vector index
- A reproducible single-conversation retrieval entry point

## Changes since `875fa8e`

### 1. Memory refiner prompt/template fixes

Files:

- `/timem/workflows/retrieval_nodes/memory_refiner.py`
- `/config/datasets/default/retrieval_config.yaml`
- `/config/datasets/locomo/retrieval_config.yaml`

What changed:

- Replaced the invalid default prompt name `memory_refiner` with
  `memory_refiner_simple`
- Corrected prompt template mappings from the nonexistent
  `relevance_analysis_*` keys to:
  - `memory_refiner_simple`
  - `memory_refiner_hybrid`
  - `memory_refiner_complex`
- Added stricter output instructions so the refiner returns JSON only
- Added tolerant parsing for:
  - embedded JSON
  - `relevant_ids: [...]` style fragments
  - plain numeric lists
- Added a `mimo` branch in the refiner LLM initialization path so it no longer
  falls back to a default provider

Why:

- The workflow was retrying and degrading because the configured prompt names
  did not exist
- The refiner could emit non-JSON wrappers, which caused parse noise
- `mimo` was configured globally but not fully recognized inside the refiner

### 2. Retrieval debug entry points

Files:

- `/experiments/datasets/locomo/01_memory_generation_single.py`
- `/experiments/datasets/locomo/02_memory_retrieval.py`
- `/experiments/datasets/locomo/02_memory_retrieval_single.py`
- `/experiments/datasets/locomo/__init__.py`

What changed:

- Added `01_memory_generation_single.py` for constrained single-conversation
  generation debugging
- Added a single-conversation mode to `02_memory_retrieval.py`
- Added `02_memory_retrieval_single.py` as a thin entry point for minimal
  debugging runs
- Updated the Locomo package docs to mention the single-conversation entry point

Why:

- Full retrieval runs were too expensive for iterative debugging
- We needed a stable way to validate one conversation and one question quickly

### 3. Provider alignment for answer generation

Files:

- `/config/datasets/default/qa_prompts.yaml`
- `/timem/workflows/retrieval_nodes/answer_generator.py`

What changed:

- Switched QA generation config from `openai / gpt-4o-mini` to
  `mimo / mimo-v2-omni`
- Ensured the answer generator requests the provider from dataset config instead
  of silently using the default path

Why:

- Debug runs were intended to use Xiaomi Mimo end-to-end
- Provider selection needed to be explicit in QA generation as well

### 4. OpenAI-compatible gateway hardening

Files:

- `/llm/openai_adapter.py`

What changed:

- Added support for custom model names on non-official OpenAI-compatible
  gateways
- Kept strict validation for the official OpenAI endpoint
- Normalized content extraction for gateways that return content in nonstandard
  list/delta forms
- Replaced hardcoded `"openai"` internal tags with `provider_name`

Why:

- Mimo is exposed through an OpenAI-compatible endpoint but uses non-OpenAI
  model names
- Some gateway responses differ slightly from the official OpenAI schema

### 5. PostgreSQL and Qdrant robustness fixes

Files:

- `/storage/postgres_adapter.py`
- `/storage/postgres_store.py`
- `/storage/vector_store.py`
- `/experiments/datasets/locomo/reindex_qdrant_from_postgres.py`

What changed:

- Normalized loose timestamp values before writing them into PostgreSQL
- Ensured core memory rows always have a valid time window
- Fixed level-table field filtering in PostgreSQL persistence
- Added compatibility for newer `qdrant-client` versions that use
  `query_points` instead of `search`
- Added a dedicated script to rebuild Qdrant from PostgreSQL memory records

Why:

- PostgreSQL writes were failing on timestamp shape mismatches
- Qdrant had ended up empty while PostgreSQL already contained valid memories
- Reindexing from SQL was the fastest way to restore vector retrieval without
  rerunning the whole generation pipeline

## Validation

### Qdrant recovery

- Rebuilt the vector collection from PostgreSQL
- Confirmed the collection dimension is `1024`
- Confirmed semantic retrieval returned records again

### Retrieval verification

Minimal end-to-end validation completed successfully with a single question:

- Question: `What did Caroline research?`
- Result: success
- Successful cases: `1`
- Failed cases: `0`
- Success rate: `100%`
- Total execution time: about `83.36s`

Artifacts:

- `/logs/tests/memory_retrieval_test_report_20260519_170235.json`
- `/logs/tests/memory_retrieval_eval_data_20260519_170235.json`
- `/logs/tests/performance_metrics_detailed_20260519_170235.csv`
- `/logs/tests/performance_statistics_20260519_170235.json`

## Errors that were removed

The follow-up fix eliminated these previously observed failures in the minimal
retrieval run:

- `Prompt not found: 'memory_refiner'`
- `Unknown LLM provider: mimo`
- `invalid_ids`
- `JSON parsing failed`
- `falling back to no refining`

## Notes

- The active dataset profile during the debug runs was `default`
- That means retrieval actually consumed `/config/datasets/default/...`
  at runtime, not only the Locomo-specific overrides
- `.history/` and local `data/` artifacts were intentionally excluded from the
  commit
