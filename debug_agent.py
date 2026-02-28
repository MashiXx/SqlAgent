#!/usr/bin/env python3
"""
Debug version with verbose logging
"""

import logging
import asyncio

# Enable DEBUG level logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from sql_agent import create_agent
from vanna.core.user import User


async def debug_agent():
    """Debug the agent with a simple query"""
    print("\n" + "="*80)
    print("DEBUG MODE - SqlAgent Testing")
    print("="*80 + "\n")

    # Create agent
    agent = create_agent()

    # Create test user
    user = User(
        id="debug@example.com",
        email="debug@example.com",
        group_memberships=["admin", "user"]
    )

    # Test questions
    questions = [
        "Show me all tables in the database",
        "How many records are in the user table?",
        "What are the column names in the user table?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {question}")
        print(f"{'='*80}\n")

        try:
            response_count = 0
            full_response = ""

            async for response in agent.send_message(user=user, message=question):
                response_count += 1
                print(f"\n--- Response #{response_count} ---")
                print(f"Type: {type(response).__name__}")

                # Print all attributes
                if hasattr(response, '__dict__'):
                    for key, value in response.__dict__.items():
                        if not key.startswith('_'):
                            print(f"  {key}: {value}")

                            # Collect text content
                            if key in ['content', 'text', 'message']:
                                full_response += str(value)
                else:
                    print(f"  Raw: {response}")
                    full_response += str(response)

            print(f"\n{'='*80}")
            print(f"FULL RESPONSE:")
            print(full_response)
            print(f"{'='*80}")
            print(f"\nTotal response chunks: {response_count}")

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "-"*80)
        input("\nPress Enter to continue to next test...")


if __name__ == "__main__":
    asyncio.run(debug_agent())
