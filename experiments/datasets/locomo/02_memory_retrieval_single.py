#!/usr/bin/env python3
"""
TiMem Memory Retrieval Workflow - Single Conversation Entry Point

This is a thin wrapper around `02_memory_retrieval.py` that defaults to
running only one conversation, while still allowing `TIMEM_TEST_CONV_IDS`
to override the target conversation set.
"""

import asyncio
import importlib
import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)


def _parse_selected_conversations():
    raw = os.getenv("TIMEM_TEST_CONV_IDS", "").strip()
    if not raw:
        return None
    return [item.strip() for item in raw.split(",") if item.strip()]


def _parse_int_list(env_name: str):
    raw = os.getenv(env_name, "").strip()
    if not raw:
        return None
    values = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            values.append(int(item))
        except ValueError:
            raise ValueError(f"{env_name} must be a comma-separated list of integers, got: {raw}")
    return values or None


def _parse_int(env_name: str):
    raw = os.getenv(env_name, "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{env_name} must be an integer, got: {raw}") from exc


def _parse_bool(env_name: str, default: bool = False) -> bool:
    raw = os.getenv(env_name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


async def main():
    module = importlib.import_module("experiments.datasets.locomo.02_memory_retrieval")
    selected_conversations = _parse_selected_conversations()
    test_categories = _parse_int_list("TIMEM_TEST_CATEGORIES")
    test_limit = _parse_int("TIMEM_TEST_LIMIT")
    debug_timing = _parse_bool("TIMEM_TEST_DEBUG_TIMING", default=False)

    await module.main(
        selected_conversations=selected_conversations,
        test_categories=test_categories,
        test_limit=test_limit,
        debug_timing=debug_timing,
        single_conversation_mode=True,
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[REALISTIC_SIM] ⚠️ Test interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[REALISTIC_SIM] ❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
