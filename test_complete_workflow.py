#!/usr/bin/env python3
"""
Test complete workflow:
1. Auto-extract schema
2. Auto-train on DDL
3. Ask question
4. Get SQL + Execute + Return results
"""

import asyncio
from sql_agent import create_agent, auto_train_schema
from vanna.core.user import RequestContext


async def test_complete_workflow():
    """Test the complete end-to-end workflow"""
    print("\n" + "="*70)
    print("TESTING COMPLETE WORKFLOW")
    print("="*70)

    # Step 1: Create agent
    print("\n[1/4] Creating agent...")
    agent, sql_runner, agent_memory = create_agent()
    print("✓ Agent created")

    # Step 2: Auto-train on schema
    print("\n[2/4] Auto-training on database schema...")
    success = await auto_train_schema(sql_runner, agent_memory)
    if success:
        print("✓ Schema training completed")
    else:
        print("✗ Schema training failed")
        return

    # Step 3: Ask a question
    print("\n[3/4] Asking question to agent...")
    request_context = RequestContext(
        cookies={"vanna_email": "test@example.com"}
    )

    # Use correct table name: 'user' (no 's'), not 'users'
    question = "How many rows are in the user table?"
    print(f"\nQuestion: {question}\n")
    print("-" * 70)

    # Step 4: Get response
    print("\n[4/4] Getting agent response...\n")
    print("Agent responses:")
    print("-" * 70)

    response_count = 0
    try:
        async for response in agent.send_message(
            request_context=request_context,
            message=question
        ):
            response_count += 1

            # Extract text content from response
            if hasattr(response, 'simple_component') and response.simple_component:
                if hasattr(response.simple_component, 'text'):
                    text = response.simple_component.text
                    if text and len(text.strip()) > 0:
                        print(f"\n📝 Response #{response_count}:")
                        print(text)
                        print("-" * 70)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    print(f"\n✓ Received {response_count} response chunks")

    print("\n" + "="*70)
    print("WORKFLOW TEST COMPLETED")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
