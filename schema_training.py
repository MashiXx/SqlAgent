"""Schema extraction, training, and cache management for SqlAgent"""

import logging
import uuid

from vanna.core.user import User
from vanna.core.tool import ToolContext

from config import Config
from schema_tools import SchemaExtractor, DDLTrainer


def _check_schema_cache(agent_memory):
    """Check if ChromaDB already has cached schema data"""
    try:
        collection = agent_memory._get_collection()
        count = collection.count()
        return count > 0, count
    except Exception:
        return False, 0


async def _extract_and_train(sql_runner, agent_memory):
    """Extract schema from MySQL and train agent memory"""
    admin_user = User(
        id="system_admin",
        email="system@internal",
        group_memberships=["admin"]
    )

    context = ToolContext(
        user=admin_user,
        conversation_id=str(uuid.uuid4()),
        request_id=str(uuid.uuid4()),
        agent_memory=agent_memory
    )

    # Extract schema
    extractor = SchemaExtractor(sql_runner, context)
    ddl_map = await extractor.get_all_ddl()
    summary = await extractor.get_database_summary()

    print(f"\n✓ Extracted schema for {len(ddl_map)} tables")
    print(f"\n{summary}\n")

    # Train on DDL
    trainer = DDLTrainer(agent_memory)
    count = await trainer.train_on_ddl(ddl_map, context)
    await trainer.train_on_schema_summary(summary, context)

    print(f"✓ Trained agent memory with {count} table schemas")
    return count


async def auto_train_schema(sql_runner, agent_memory):
    """
    Smart schema training: skip extraction if ChromaDB cache already has data
    """
    if not Config.SCHEMA_AUTO_TRAIN:
        print("Schema auto-training is disabled (SCHEMA_AUTO_TRAIN=false)")
        return True

    print("\n" + "="*60)

    # Check if schema is already cached
    if Config.SCHEMA_CACHE_ENABLED:
        has_cache, cache_count = _check_schema_cache(agent_memory)
        if has_cache:
            print(f"Schema cache found ({cache_count} items in ChromaDB), skipping extraction")
            print("Use POST /api/refresh-schema to force re-extraction")
            print("="*60 + "\n")
            return True

    print("AUTO-TRAINING: Extracting database schema...")
    print("="*60)

    try:
        await _extract_and_train(sql_runner, agent_memory)
        print("="*60 + "\n")
        return True

    except Exception as e:
        print(f"✗ Auto-training failed: {e}")
        logging.error(f"Schema auto-training error: {e}", exc_info=True)
        return False


async def refresh_schema(sql_runner, agent_memory):
    """
    Force refresh: clear ChromaDB cache and re-extract schema from MySQL
    """
    print("\n" + "="*60)
    print("REFRESH: Clearing schema cache and re-extracting...")
    print("="*60)

    try:
        # Clear all existing memories
        admin_user = User(
            id="system_admin",
            email="system@internal",
            group_memberships=["admin"]
        )
        context = ToolContext(
            user=admin_user,
            conversation_id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            agent_memory=agent_memory
        )
        cleared = await agent_memory.clear_memories(context)
        print(f"✓ Cleared {cleared} cached items")

        # Re-extract and train
        count = await _extract_and_train(sql_runner, agent_memory)
        print("="*60 + "\n")
        return True, count

    except Exception as e:
        print(f"✗ Schema refresh failed: {e}")
        logging.error(f"Schema refresh error: {e}", exc_info=True)
        return False, 0
