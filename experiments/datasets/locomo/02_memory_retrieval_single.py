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


async def main():
    module = importlib.import_module("experiments.datasets.locomo.02_memory_retrieval")
    selected_conversations = _parse_selected_conversations()

    await module.main(
        selected_conversations=selected_conversations,
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
