#!/usr/bin/env python3
"""
Test script to debug agent behavior
"""

import asyncio
from sql_agent import create_agent
from vanna.core.user import User, RequestContext


async def test_agent():
    """Test the agent directly"""
    print("Creating agent...")
    agent = create_agent()

    # Create a test request context with a user email cookie
    request_context = RequestContext(
        cookies={"vanna_email": "test@example.com"}
    )

    # Test question - USE CORRECT TABLE NAME
    # Database has 'user' (no 's'), not 'users'
    question = "How many rows are in the user table?"

    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}\n")

    # Call the agent
    print("Sending to agent...\n")

    try:
        async for response in agent.send_message(
            request_context=request_context,
            message=question
        ):
            print(f"\n{'~'*60}")
            print(f"Agent response chunk:")
            print(f"Type: {type(response).__name__}")

            # Print response content
            if hasattr(response, '__dict__'):
                for key, value in response.__dict__.items():
                    if not key.startswith('_'):
                        print(f"  {key}: {value}")
            else:
                print(f"  Raw: {response}")

            print(f"{'~'*60}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_agent())
