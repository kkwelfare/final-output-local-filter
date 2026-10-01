"""Hermes adapter for the shared deterministic local filter."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import importlib.util
import sys

try:  # PluginManager loads this module as a package.
    from .filter_core import filter_text
except ImportError:  # Direct execution/test collection has no package context.
    _spec = importlib.util.spec_from_file_location(
        "_final_output_local_filter_core", Path(__file__).with_name("filter_core.py")
    )
    if _spec is None or _spec.loader is None:
        raise
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _module
    _spec.loader.exec_module(_module)
    filter_text = _module.filter_text

PLUGIN_ID = "final-output-local-filter"


def transform_llm_output(**kwargs: Any) -> str | None:
    """Return only a changed final response; None preserves Hermes pass-through."""
    text = kwargs.get("response_text")
    if not isinstance(text, str):
        return None
    result = filter_text(text)
    return result.text if result.text != text else None


def register(ctx: Any) -> None:
    ctx.register_hook("transform_llm_output", transform_llm_output)
