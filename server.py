"""FastAPI server setup and API endpoint registration for SqlAgent"""

import asyncio

from vanna import Agent
from vanna.servers.fastapi import VannaFastAPIServer

from config import Config
from schema_training import auto_train_schema, refresh_schema, _check_schema_cache


def run_server(agent: Agent, sql_runner=None, agent_memory=None,
               host: str = "0.0.0.0", port: int = 8000, auto_train: bool = True):
    """
    Run the FastAPI server

    Args:
        agent: The Vanna agent
        sql_runner: SQL runner for schema extraction (optional)
        agent_memory: Agent memory for training (optional)
        host: Server host
        port: Server port
        auto_train: Whether to auto-train on startup (default: True)
    """
    # Auto-train on schema if enabled
    if auto_train and sql_runner and agent_memory:
        asyncio.run(auto_train_schema(sql_runner, agent_memory))

    server = VannaFastAPIServer(agent)
    app = server.create_app()

    # Add refresh-schema endpoint
    if sql_runner and agent_memory:
        @app.post("/api/refresh-schema")
        async def api_refresh_schema():
            """Force re-extract database schema and update ChromaDB cache"""
            success, count = await refresh_schema(sql_runner, agent_memory)
            if success:
                return {"status": "success", "message": f"Schema refreshed with {count} tables"}
            else:
                return {"status": "error", "message": "Schema refresh failed. Check server logs."}

        @app.get("/api/schema-status")
        async def api_schema_status():
            """Check current schema cache status"""
            has_cache, cache_count = _check_schema_cache(agent_memory)
            return {
                "cached": has_cache,
                "item_count": cache_count,
                "persist_directory": Config.CHROMA_PERSIST_DIR,
                "cache_enabled": Config.SCHEMA_CACHE_ENABLED,
            }

    print(f"Starting FastAPI server...")
    print(f"Access the application at: http://localhost:{port}")
    print(f"API documentation at: http://localhost:{port}/docs")

    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")
