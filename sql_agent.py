#!/usr/bin/env python3
"""
SqlAgent using Vanna Agent API with Ollama and MySQL
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from agent_factory import create_agent
from server import run_server

if __name__ == "__main__":
    # Create the agent
    agent, sql_runner, agent_memory = create_agent()

    # Run the server with auto-training (Access at http://localhost:8000)
    run_server(agent, sql_runner, agent_memory, auto_train=True)
