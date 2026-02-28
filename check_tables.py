#!/usr/bin/env python3
"""
Check what tables actually exist in the database
"""

import asyncio
from sql_agent import create_agent
from schema_tools import SchemaExtractor
from vanna.core.user import User
from vanna.core.tool import ToolContext
import uuid


async def check_tables():
    """Check actual tables in database"""
    print("\n" + "="*70)
    print("CHECKING ACTUAL TABLES IN DATABASE")
    print("="*70)

    # Create agent
    agent, sql_runner, agent_memory = create_agent()

    # Create context
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

    # Extract tables
    extractor = SchemaExtractor(sql_runner, context)
    tables = await extractor.get_all_tables()

    print(f"\n✓ Found {len(tables)} tables in database '{sql_runner.database}'\n")

    # Check if 'users' table exists
    has_users = 'users' in tables or 'user' in tables

    if has_users:
        print("✓ Found 'users' table!")
    else:
        print("✗ NO 'users' table found!")
        print("\nSearching for user-related tables...")
        user_tables = [t for t in tables if 'user' in t.lower()]
        if user_tables:
            print(f"  Found {len(user_tables)} user-related tables:")
            for t in user_tables:
                print(f"    - {t}")
        else:
            print("  No user-related tables found")

    print(f"\n{'='*70}")
    print("ALL TABLES (first 50):")
    print("="*70)

    for i, table in enumerate(tables[:50], 1):
        print(f"{i:3}. {table}")

    if len(tables) > 50:
        print(f"\n... and {len(tables) - 50} more tables")

    print("\n" + "="*70)
    print(f"TOTAL: {len(tables)} tables")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(check_tables())
