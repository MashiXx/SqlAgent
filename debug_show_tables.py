#!/usr/bin/env python3
"""
Debug SHOW TABLES output
"""

import asyncio
from sql_agent import create_agent
from vanna.core.user import User
from vanna.core.tool import ToolContext
from vanna.capabilities.sql_runner import RunSqlToolArgs
import uuid


async def debug_show_tables():
    """Debug what SHOW TABLES actually returns"""
    print("\n" + "="*70)
    print("DEBUG: SHOW TABLES OUTPUT")
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

    # Run SHOW TABLES
    args = RunSqlToolArgs(sql="SHOW TABLES")
    result = await sql_runner.run_sql(args, context)

    print(f"\nDataFrame info:")
    print(f"  Shape: {result.shape}")
    print(f"  Columns: {result.columns.tolist()}")
    print(f"  Column types: {result.dtypes.tolist()}")

    print(f"\nFirst 20 rows:")
    print(result.head(20).to_string())

    # Convert to list and check
    first_col = result.columns[0]
    tables_list = result[first_col].tolist()

    print(f"\n" + "="*70)
    print(f"Tables as list (first 30):")
    print("="*70)
    for i, table in enumerate(tables_list[:30], 1):
        print(f"{i:3}. '{table}' (type: {type(table).__name__})")

    # Check for 'users'
    if 'users' in tables_list:
        idx = tables_list.index('users')
        print(f"\n✓ Found 'users' at index {idx}")
        print(f"  Value: '{tables_list[idx]}'")
        print(f"  Type: {type(tables_list[idx])}")

        # Try to describe THIS specific table
        print(f"\n" + "-"*70)
        print("Trying to DESCRIBE this 'users' table...")
        print("-"*70)

        try:
            # Maybe it has a different database prefix in the name?
            table_name = tables_list[idx]
            args2 = RunSqlToolArgs(sql=f"DESCRIBE `{table_name}`")
            result2 = await sql_runner.run_sql(args2, context)
            print(f"✓ SUCCESS!")
            print(result2.to_string())
        except Exception as e:
            print(f"✗ FAILED: {e}")

            # Check if the table name contains a dot
            if '.' in str(table_name):
                print(f"\n  Table name contains '.': {table_name}")
                db, tbl = table_name.split('.', 1)
                print(f"  Database: {db}")
                print(f"  Table: {tbl}")

    # List all tables that ACTUALLY exist in 'dson'
    print(f"\n" + "="*70)
    print(f"ACTUAL TABLES in database '{sql_runner.database}':")
    print("="*70)

    args3 = RunSqlToolArgs(sql=f"""
        SELECT TABLE_NAME, TABLE_ROWS, TABLE_TYPE
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = '{sql_runner.database}'
        ORDER BY TABLE_NAME
        LIMIT 50
    """)
    result3 = await sql_runner.run_sql(args3, context)

    if not result3.empty:
        print(f"\n✓ Found {len(result3)} actual tables in '{sql_runner.database}':\n")
        print(result3.to_string())

        # Check if any contain 'user'
        user_tables = result3[result3['TABLE_NAME'].str.contains('user', case=False, na=False)]
        if not user_tables.empty:
            print(f"\n✓ Tables containing 'user':")
            print(user_tables.to_string())
        else:
            print(f"\n✗ No tables containing 'user' in database '{sql_runner.database}'")
    else:
        print(f"\n✗ No tables found in '{sql_runner.database}'")

    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(debug_show_tables())
