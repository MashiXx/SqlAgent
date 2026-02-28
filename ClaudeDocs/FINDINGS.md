# Vanna Agent Tool Calling Issue - Findings

## Problem
Vanna agent is not executing SQL queries and returning results to users. The agent generates SQL queries but doesn't actually execute them.

## Root Cause
The **qwen2.5-coder:7b** model does NOT support native tool calling/function calling.

### Evidence:
When the agent is asked "How many distinct users are in the database?", it:
1. Receives the tool schemas correctly ✅
2. Generates text like "Let me run this SQL query for you..." ❌
3. Does NOT actually invoke the `run_sql` tool ❌
4. Sometimes outputs tool calls as JSON text instead of actual invocations ❌

Example bad output:
```json
{
  "name": "run_sql",
  "arguments": {
    "sql": "SELECT COUNT(DISTINCT user_id) AS distinct_user_count FROM users;"
  }
}
```

This is TEXT output, not an actual tool invocation.

## Solutions

### Solution 1: Use a Tool-Calling Compatible Model (RECOMMENDED)
Switch to an Ollama model that supports native tool calling:

**Best options:**
- `llama3.2` (3B or 1B) - Fast, lightweight, supports tools
- `llama3.1` (8B or larger) - Better quality, supports tools
- `mistral` - Good tool calling support
- `qwen2.5:14b` or larger - Larger Qwen models support tools better

**To change:** Edit `config.py` and set:
```python
OLLAMA_MODEL = "llama3.1:8b"  # or another tool-compatible model
```

Then pull the model:
```bash
ollama pull llama3.1:8b
```

### Solution 2: Implement Manual Tool Call Parsing
Create a custom LLM service that:
1. Detects tool call patterns in the text output
2. Parses the JSON manually
3. Converts it to proper ToolCall objects
4. Re-injects into the agent loop

This is more complex and fragile.

### Solution 3: Use a Different LLM Provider
Instead of Ollama, use:
- **OpenAI** (GPT-4, GPT-3.5-turbo) - Best tool calling
- **Anthropic Claude** - Excellent tool calling
- **Azure OpenAI** - Enterprise option

Requires API keys and costs money.

## Recommended Action
**Switch to `llama3.1:8b` or `llama3.2:3b`** - these are free, local, and support tool calling natively.

Test with:
```bash
# Pull the model
ollama pull llama3.1:8b

# Update config.py to use the new model
# Then run the test
python test_agent.py
```

## Additional Notes
- The Vanna framework is correctly configured
- Tools are properly registered
- The issue is purely with the LLM model's capability
- System prompts won't fix this - the model fundamentally doesn't support tool calling
