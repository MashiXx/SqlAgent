#!/usr/bin/env python3
"""
Find where the 'users' table actually is
"""

import asyncio
from sql_agent import create_agent
from vanna.core.user import User
from vanna.core.tool import ToolContext
from vanna.capabilities.sql_runner import RunSqlToolArgs
import uuid


async def find_users_table():
    """Find the actual users table"""
    print("\n" + "="*70)
    print("INVESTIGATING 'users' TABLE LOCATION")
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

    print(f"\nCurrent database: {sql_runner.database}")

    # Method 1: Check with database prefix
    print("\n" + "-"*70)
    print("Method 1: SHOW TABLES (what we see)")
    print("-"*70)

    args = RunSqlToolArgs(sql="SHOW TABLES")
    result = await sql_runner.run_sql(args, context)
    print(f"Tables found: {len(result)}")

    # Check if 'users' is in the list
    first_col = result.columns[0]
    tables_list = result[first_col].tolist()

    if 'users' in tables_list:
        print(f"✓ 'users' found in SHOW TABLES at position {tables_list.index('users') + 1}")

    # Method 2: Check FULL table name
    print("\n" + "-"*70)
    print("Method 2: SHOW TABLES with database prefix")
    print("-"*70)

    args2 = RunSqlToolArgs(sql="SHOW TABLES LIKE 'users'")
    result2 = await sql_runner.run_sql(args2, context)
    print(f"Result: {result2}")

    # Method 3: Query information_schema
    print("\n" + "-"*70)
    print("Method 3: Query information_schema.TABLES")
    print("-"*70)

    args3 = RunSqlToolArgs(sql="""
        SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
        FROM information_schema.TABLES
        WHERE TABLE_NAME = 'users'
        LIMIT 10
    """)
    result3 = await sql_runner.run_sql(args3, context)
    print(f"\nTables named 'users' in information_schema:")
    print(result3.to_string())

    # Method 4: Try to describe the table
    print("\n" + "-"*70)
    print("Method 4: Try DESCRIBE on different variations")
    print("-"*70)

    variations = [
        'users',
        '`users`',
        f'{sql_runner.database}.users',
        f'`{sql_runner.database}`.`users`'
    ]

    for var in variations:
        try:
            args4 = RunSqlToolArgs(sql=f"DESCRIBE {var}")
            result4 = await sql_runner.run_sql(args4, context)
            print(f"✓ SUCCESS with: DESCRIBE {var}")
            print(f"  Columns: {len(result4)}")
            break
        except Exception as e:
            print(f"✗ FAILED: DESCRIBE {var}")
            print(f"  Error: {str(e)[:80]}")

    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)

    if not result3.empty:
        print("\nThe 'users' table exists in these databases:")
        for _, row in result3.iterrows():
            schema = row['TABLE_SCHEMA']
            table_type = row['TABLE_TYPE']
            print(f"  - {schema}.users ({table_type})")

            if schema != sql_runner.database:
                print(f"\n⚠️  WARNING: 'users' table is in '{schema}', but you're connected to '{sql_runner.database}'!")
                print(f"\nTo fix, either:")
                print(f"1. Change DB_NAME in config.py to: {schema}")
                print(f"2. Or use full table name in queries: {schema}.users")
    else:
        print("\n✗ 'users' table not found in information_schema!")
        print("  This is strange - SHOW TABLES lists it but it doesn't exist?")

    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(find_users_table())
