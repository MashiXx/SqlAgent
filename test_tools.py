#!/usr/bin/env python3
"""
Test to check if tools are being registered and available
"""

import asyncio
from sql_agent import create_agent
from vanna.core.user import User, RequestContext


async def test_tools():
    """Test tool availability"""
    print("Creating agent...")
    agent = create_agent()

    # Create a test request context
    request_context = RequestContext(
        cookies={"vanna_email": "test@example.com"}
    )

    # Resolve the user
    user = await agent.user_resolver.resolve_user(request_context)
    print(f"\nUser: {user.email}")
    print(f"Groups: {user.group_memberships}")

    # Get available tools for this user
    tools = await agent.tool_registry.get_schemas(user)

    print(f"\n{'='*60}")
    print(f"Available tools for user ({len(tools)} total):")
    print(f"{'='*60}\n")

    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"  Description: {tool.description}")
        print(f"  Parameters: {list(tool.parameters.get('properties', {}).keys())}")
        print()


if __name__ == "__main__":
    asyncio.run(test_tools())
