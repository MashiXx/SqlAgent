#!/usr/bin/env python3
"""
Schema extraction and DDL training tools for SqlAgent
"""

import logging
from typing import List, Dict, Any
from vanna.integrations.mysql import MySQLRunner
from vanna.capabilities.sql_runner import RunSqlToolArgs

logger = logging.getLogger(__name__)


class SchemaExtractor:
    """Extract database schema information"""

    def __init__(self, sql_runner: MySQLRunner, context):
        self.sql_runner = sql_runner
        self.context = context

    async def get_all_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        # Use information_schema instead of SHOW TABLES
        # because SHOW TABLES may return tables from other databases (via ProxySQL)
        query = f"""
            SELECT TABLE_NAME
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = '{self.sql_runner.database}'
            AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """
        args = RunSqlToolArgs(sql=query)
        result = await self.sql_runner.run_sql(args, self.context)

        if result is None or result.empty:
            return []

        # Result is a DataFrame with TABLE_NAME column
        tables = result['TABLE_NAME'].tolist()

        return tables

    async def get_table_ddl(self, table_name: str) -> str:
        """Get CREATE TABLE statement for a table"""
        query = f"SHOW CREATE TABLE `{table_name}`"
        args = RunSqlToolArgs(sql=query)
        result = await self.sql_runner.run_sql(args, self.context)

        if result is None or result.empty:
            return ""

        # Result is a DataFrame with columns 'Table' and 'Create Table'
        # Get the 'Create Table' column from the first row
        if 'Create Table' in result.columns:
            return result.iloc[0]['Create Table']
        else:
            # Fallback: get the second column
            return result.iloc[0, 1]

    async def get_all_ddl(self) -> Dict[str, str]:
        """Get DDL for all tables in database"""
        tables = await self.get_all_tables()
        ddl_map = {}

        logger.info(f"Extracting DDL for {len(tables)} tables...")

        for table in tables:
            try:
                ddl = await self.get_table_ddl(table)
                if ddl:
                    ddl_map[table] = ddl
                    logger.debug(f"Extracted DDL for table: {table}")
            except Exception as e:
                logger.error(f"Failed to extract DDL for table {table}: {e}")

        logger.info(f"Successfully extracted DDL for {len(ddl_map)} tables")
        return ddl_map

    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table"""
        query = f"DESCRIBE `{table_name}`"
        args = RunSqlToolArgs(sql=query)
        result = await self.sql_runner.run_sql(args, self.context)

        # Convert DataFrame to list of dicts for easier handling
        columns = result.to_dict('records') if result is not None and not result.empty else []

        return {
            'table_name': table_name,
            'columns': columns
        }

    async def get_database_summary(self) -> str:
        """Get a text summary of the database schema"""
        tables = await self.get_all_tables()
        summary_parts = [
            f"Database contains {len(tables)} tables:",
            ""
        ]

        for table in tables:
            info = await self.get_table_info(table)
            columns = info['columns']
            column_names = [col.get('Field', '') for col in columns]
            summary_parts.append(f"- {table} ({len(columns)} columns): {', '.join(column_names)}")

        return "\n".join(summary_parts)


class DDLTrainer:
    """Train the agent with DDL information"""

    def __init__(self, agent_memory):
        self.agent_memory = agent_memory

    async def train_on_ddl(self, ddl_map: Dict[str, str], context) -> int:
        """
        Train the agent memory with DDL statements

        Args:
            ddl_map: Dictionary mapping table names to DDL statements
            context: ToolContext for memory operations

        Returns:
            Number of DDL statements saved
        """
        count = 0

        for table_name, ddl in ddl_map.items():
            try:
                # Save DDL as text memory with informative content
                content = f"Table '{table_name}' schema:\n{ddl}"

                await self.agent_memory.save_text_memory(
                    context=context,
                    content=content
                )

                count += 1
                logger.debug(f"Trained on DDL for table: {table_name}")

            except Exception as e:
                logger.error(f"Failed to save DDL for table {table_name}: {e}")

        logger.info(f"Successfully trained on {count} DDL statements")
        return count

    async def train_on_schema_summary(self, summary: str, context) -> bool:
        """
        Save database schema summary to memory

        Args:
            summary: Text summary of database schema
            context: ToolContext for memory operations

        Returns:
            True if successful
        """
        try:
            content = f"Database Schema Overview:\n{summary}"

            await self.agent_memory.save_text_memory(
                context=context,
                content=content
            )

            logger.info("Successfully saved schema summary to memory")
            return True

        except Exception as e:
            logger.error(f"Failed to save schema summary: {e}")
            return False
