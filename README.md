# Final output local filter

A deterministic, local-only Hermes output filter and reusable document checker. `filter_core.py` preserves Markdown and protected syntax, applies narrowly bounded rules, and fails open on ambiguity. It never calls a provider.

## Components

- `filter_core.py`: pure deterministic transform; `filter_text(text, mode="response")` preserves the historical response behavior; `mode="document"` checks prose segments with bounded, segment-local rollback and the visible document cap.
- `__init__.py`: Hermes `transform_llm_output` adapter returns only changed final output; otherwise returns `None` to preserve pass-through.
- `check_document.py`: local UTF-8 document check. Dry-run is the default; `--apply` atomically writes only the specified path when a safe candidate exists. Reports include text for local caller use; handle reports accordingly.
- `tests/test_filter_core.py`: deterministic synthetic regression tests; no provider/network calls.

No correction is made for ambiguous, protected, technical, conditional, operational, or otherwise excluded text. The checker does not make correctness or completeness judgments. This is a narrow language-cleanup aid, not a universal safety or quality gate.

## Try

```sh
python3 check_document.py sample.md
# Only after reviewing the dry-run result:
python3 check_document.py sample.md --apply
```

Install/enable through Hermes' plugin manager for host integration. Installing this source does not activate a running profile or gateway. The package declares no external Python dependencies and makes no provider calls.

## Verify

```sh
python3 -m pytest -q tests/test_filter_core.py
hermes plugins validate . --json
```
