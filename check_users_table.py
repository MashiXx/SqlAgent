#!/usr/bin/env python3
"""
Check the structure of the 'users' table
"""

import asyncio
from sql_agent import create_agent
from schema_tools import SchemaExtractor
from vanna.core.user import User
from vanna.core.tool import ToolContext
import uuid


async def check_users_table():
    """Check users table structure"""
    print("\n" + "="*70)
    print("CHECKING 'users' TABLE STRUCTURE")
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

    # Extract table info
    extractor = SchemaExtractor(sql_runner, context)

    # Get table structure
    table_info = await extractor.get_table_info('users')
    print(f"\n✓ Table: users")
    print(f"✓ Columns: {len(table_info['columns'])}\n")

    print("Column Details:")
    print("-" * 70)
    for col in table_info['columns']:
        print(f"  {col.get('Field', '?'):20} {col.get('Type', '?'):20} {col.get('Null', '?'):5} {col.get('Key', '?')}")

    # Get DDL
    ddl = await extractor.get_table_ddl('users')
    print(f"\n{'='*70}")
    print("CREATE TABLE Statement:")
    print("="*70)
    print(ddl)

    # Check primary key
    pk_cols = [col['Field'] for col in table_info['columns'] if col.get('Key') == 'PRI']
    if pk_cols:
        print(f"\n✓ Primary Key: {', '.join(pk_cols)}")

    print("\n" + "="*70)
    print("RECOMMENDED TEST QUESTIONS:")
    print("="*70)
    print("\nBased on this table structure, try these questions:")
    print("1. 'Show me all columns in the users table'")
    print("2. 'How many rows are in the users table?'")
    print(f"3. 'What is in the {table_info['columns'][0]['Field']} column?'")
    print("4. 'Describe the users table'")
    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(check_users_table())
