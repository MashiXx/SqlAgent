#!/usr/bin/env python3
"""
Example usage and customization for SqlAgent
"""

from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool,
    SaveTextMemoryTool
)
from vanna.servers.fastapi import VannaFastAPIServer
from vanna.integrations.ollama import OllamaLlmService
from vanna.integrations.mysql import MySQLRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory
from config import Config


# Example 1: Basic usage (same as sql_agent.py)
def basic_usage():
    """Basic usage - just run the default agent"""
    from sql_agent import create_agent, run_server

    agent = create_agent()
    run_server(agent)


# Example 2: Custom user authentication
class CustomUserResolver(UserResolver):
    """Custom user authentication with role-based access"""

    async def resolve_user(self, request_context: RequestContext) -> User:
        # Get user from header or cookie
        user_id = request_context.get_header('X-User-ID') or \
                  request_context.get_cookie('user_id') or \
                  'anonymous'

        # Custom role assignment logic
        if user_id == 'admin@company.com':
            groups = ['admin', 'power_user', 'user']
        elif user_id.endswith('@company.com'):
            groups = ['user']
        else:
            groups = ['guest']

        return User(
            id=user_id,
            email=user_id,
            group_memberships=groups
        )


def custom_auth_example():
    """Example with custom authentication"""
    Config.validate_config()

    llm = OllamaLlmService(
        model=Config.OLLAMA_MODEL,
        host=Config.OLLAMA_HOST
    )

    db_tool = RunSqlTool(
        sql_runner=MySQLRunner(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT
        )
    )

    agent_memory = DemoAgentMemory(max_items=1000)
    user_resolver = CustomUserResolver()  # Use custom resolver

    tools = ToolRegistry()
    tools.register_local_tool(db_tool, access_groups=['admin', 'power_user', 'user'])
    tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=['admin'])
    tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=['admin', 'power_user', 'user'])
    tools.register_local_tool(SaveTextMemoryTool(), access_groups=['admin', 'power_user', 'user'])
    tools.register_local_tool(VisualizeDataTool(), access_groups=['admin', 'power_user', 'user'])

    agent = Agent(
        llm_service=llm,
        tool_registry=tools,
        user_resolver=user_resolver,
        agent_memory=agent_memory
    )

    server = VannaFastAPIServer(agent)
    server.run(host="0.0.0.0", port=8000)


# Example 3: Different Ollama model
def use_different_model():
    """Example using a different Ollama model"""
    import os

    # Temporarily override the model
    original_model = Config.OLLAMA_MODEL
    Config.OLLAMA_MODEL = "codellama"  # or "mistral", "llama2:13b", etc.

    from sql_agent import create_agent, run_server

    try:
        agent = create_agent()
        run_server(agent)
    finally:
        Config.OLLAMA_MODEL = original_model


# Example 4: Limited tool access
def limited_tools_example():
    """Example with limited tools (read-only)"""
    Config.validate_config()

    llm = OllamaLlmService(
        model=Config.OLLAMA_MODEL,
        host=Config.OLLAMA_HOST
    )

    # Only database and visualization tools, no memory tools
    db_tool = RunSqlTool(
        sql_runner=MySQLRunner(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT
        )
    )

    agent_memory = DemoAgentMemory(max_items=100)

    from sql_agent import SimpleUserResolver
    user_resolver = SimpleUserResolver()

    tools = ToolRegistry()
    # Only register database and visualization tools
    tools.register_local_tool(db_tool, access_groups=['user'])
    tools.register_local_tool(VisualizeDataTool(), access_groups=['user'])

    agent = Agent(
        llm_service=llm,
        tool_registry=tools,
        user_resolver=user_resolver,
        agent_memory=agent_memory
    )

    server = VannaFastAPIServer(agent)
    server.run(host="0.0.0.0", port=8000)


# Example 5: Multiple database connections
def multi_database_example():
    """Example with multiple database connections"""
    Config.validate_config()

    llm = OllamaLlmService(
        model=Config.OLLAMA_MODEL,
        host=Config.OLLAMA_HOST
    )

    # Primary database
    db_tool_primary = RunSqlTool(
        sql_runner=MySQLRunner(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT
        ),
        name="primary_db"  # Give it a custom name
    )

    # Secondary database (analytics)
    db_tool_analytics = RunSqlTool(
        sql_runner=MySQLRunner(
            host=Config.DB_HOST,
            database="analytics_db",  # Different database
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT
        ),
        name="analytics_db"
    )

    agent_memory = DemoAgentMemory(max_items=1000)

    from sql_agent import SimpleUserResolver
    user_resolver = SimpleUserResolver()

    tools = ToolRegistry()
    # Register both database tools
    tools.register_local_tool(db_tool_primary, access_groups=['admin', 'user'])
    tools.register_local_tool(db_tool_analytics, access_groups=['admin'])  # Only admin can access analytics
    tools.register_local_tool(VisualizeDataTool(), access_groups=['admin', 'user'])

    agent = Agent(
        llm_service=llm,
        tool_registry=tools,
        user_resolver=user_resolver,
        agent_memory=agent_memory
    )

    server = VannaFastAPIServer(agent)
    server.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example = sys.argv[1]

        if example == "basic":
            basic_usage()
        elif example == "custom-auth":
            custom_auth_example()
        elif example == "different-model":
            use_different_model()
        elif example == "limited-tools":
            limited_tools_example()
        elif example == "multi-db":
            multi_database_example()
        else:
            print(f"Unknown example: {example}")
            print("Available examples: basic, custom-auth, different-model, limited-tools, multi-db")
    else:
        print("Usage: python example.py <example_name>")
        print("Available examples:")
        print("  basic          - Basic usage (default)")
        print("  custom-auth    - Custom authentication")
        print("  different-model- Use different Ollama model")
        print("  limited-tools  - Limited tools (read-only)")
        print("  multi-db       - Multiple database connections")
        print("\nExample: python example.py basic")
