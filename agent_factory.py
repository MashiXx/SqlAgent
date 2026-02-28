"""Agent creation and configuration for SqlAgent"""

from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.core.system_prompt.default import DefaultSystemPromptBuilder
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool,
    SaveTextMemoryTool
)
from vanna.integrations.mysql import MySQLRunner
from vanna.integrations.chromadb import ChromaAgentMemory

from config import Config
from prompts import CUSTOM_SYSTEM_PROMPT
from auth import SimpleUserResolver
from llm_factory import create_llm


def create_agent():
    """Create and configure the SqlAgent.

    Returns:
        Tuple of (agent, sql_runner, agent_memory)
    """
    # Validate configuration
    Config.validate_config()

    # Configure LLM
    llm = create_llm()

    # Create custom system prompt builder with our base prompt
    system_prompt_builder = DefaultSystemPromptBuilder(base_prompt=CUSTOM_SYSTEM_PROMPT)

    # Configure your database
    db_tool = RunSqlTool(
        sql_runner=MySQLRunner(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT
        )
    )

    # Configure your agent memory (persistent via ChromaDB)
    agent_memory = ChromaAgentMemory(persist_directory=Config.CHROMA_PERSIST_DIR)

    # Configure user authentication
    user_resolver = SimpleUserResolver()

    # Create tool registry and register tools
    tools = ToolRegistry()

    # Register database tool (accessible by admin and user groups)
    tools.register_local_tool(db_tool, access_groups=['admin', 'user'])

    # Register memory tools (important for schema knowledge)
    tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=['admin'])
    tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=['admin', 'user'])
    tools.register_local_tool(SaveTextMemoryTool(), access_groups=['admin', 'user'])

    # Register visualization tool
    tools.register_local_tool(VisualizeDataTool(), access_groups=['admin', 'user'])

    # Create the agent with custom system prompt
    agent = Agent(
        llm_service=llm,
        tool_registry=tools,
        user_resolver=user_resolver,
        agent_memory=agent_memory,
        system_prompt_builder=system_prompt_builder
    )

    print(f"SqlAgent initialized successfully!")
    print(f"Database: {Config.DB_NAME}")
    print(f"LLM Provider: {Config.LLM_PROVIDER}")
    if Config.LLM_PROVIDER == 'gemini':
        print(f"Gemini Model: {Config.GEMINI_MODEL}")
    else:
        print(f"Ollama Model: {Config.OLLAMA_MODEL}")
        print(f"Ollama Host: {Config.OLLAMA_HOST}")

    return agent, db_tool.sql_runner, agent_memory
