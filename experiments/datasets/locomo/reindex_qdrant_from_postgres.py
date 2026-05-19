"""
Rebuild Qdrant vectors from PostgreSQL memory records.

This script does not call the chat model. It only:
1. Reads memory records from PostgreSQL.
2. Reconstructs payload fields needed by retrieval.
3. Generates embeddings with the local embedding service.
4. Recreates and repopulates the Qdrant collection.

Usage:
    export PYTHONPATH=.
    .venv/bin/python experiments/datasets/locomo/reindex_qdrant_from_postgres.py
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from sqlalchemy import text

from storage.postgres_store import get_postgres_store
from storage.vector_adapter import get_vector_adapter
from timem.models.memory import create_memory_by_level


SELECT_ALL_MEMORIES_SQL = text(
    """
    SELECT
        cm.id,
        cm.user_id,
        cm.expert_id,
        cm.level,
        cm.title,
        cm.content,
        cm.created_at,
        cm.updated_at,
        cm.time_window_start,
        cm.time_window_end,
        l1.session_id AS l1_session_id,
        l1.dialogue_turns_json,
        l2.session_id AS l2_session_id,
        l3.date_value,
        l4.year AS l4_year,
        l4.week_number,
        l5.year AS l5_year,
        l5.month
    FROM core_memories cm
    LEFT JOIN l1_fragment_memories l1
        ON cm.id = l1.memory_id AND cm.level = 'L1'
    LEFT JOIN l2_session_memories l2
        ON cm.id = l2.memory_id AND cm.level = 'L2'
    LEFT JOIN l3_daily_memories l3
        ON cm.id = l3.memory_id AND cm.level = 'L3'
    LEFT JOIN l4_weekly_memories l4
        ON cm.id = l4.memory_id AND cm.level = 'L4'
    LEFT JOIN l5_monthly_memories l5
        ON cm.id = l5.memory_id AND cm.level = 'L5'
    ORDER BY cm.created_at ASC, cm.id ASC
    """
)


def row_to_memory_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    level = row["level"]
    payload: Dict[str, Any] = {
        "id": row["id"],
        "user_id": row["user_id"],
        "expert_id": row["expert_id"],
        "level": level,
        "title": row["title"],
        "content": row["content"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "time_window_start": row["time_window_start"],
        "time_window_end": row["time_window_end"],
    }

    if level == "L1":
        payload["session_id"] = row["l1_session_id"]
        payload["dialogue_turns"] = row["dialogue_turns_json"] or []
    elif level == "L2":
        payload["session_id"] = row["l2_session_id"]
    elif level == "L3":
        payload["date_value"] = row["date_value"]
    elif level == "L4":
        payload["year"] = row["l4_year"]
        payload["week_number"] = row["week_number"]
    elif level == "L5":
        payload["year"] = row["l5_year"]
        payload["month"] = row["month"]

    return payload


async def load_memories() -> List[Any]:
    store = await get_postgres_store()
    async with store.get_session() as session:
        result = await session.execute(SELECT_ALL_MEMORIES_SQL)
        rows = [dict(row._mapping) for row in result.fetchall()]

    memories = [create_memory_by_level(**row_to_memory_payload(row)) for row in rows]
    return memories


async def main() -> None:
    print("[REINDEX] Loading PostgreSQL memories...")
    memories = await load_memories()
    print(f"[REINDEX] Loaded {len(memories)} memories from PostgreSQL.")

    vector_adapter = get_vector_adapter()
    print("[REINDEX] Connecting to Qdrant...")
    connected = await vector_adapter.connect()
    if not connected:
        raise RuntimeError("Qdrant connection failed.")

    print("[REINDEX] Recreating Qdrant collection...")
    recreate_result = await vector_adapter.clear_all_data()
    if not recreate_result.get("success"):
        raise RuntimeError(f"Failed to recreate Qdrant collection: {recreate_result}")

    print("[REINDEX] Writing vectors to Qdrant...")
    memory_ids = await vector_adapter.batch_store_memories(memories, wait_for_vector_indexing=True)
    print(f"[REINDEX] Finished. Stored {len(memory_ids)} vectors.")

    stats = await vector_adapter.get_stats()
    print(f"[REINDEX] Qdrant stats: {stats}")

    await vector_adapter.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
