# SqlAgent - Automatic Schema-Aware SQL Assistant

## Overview

This is a complete SQL assistant that automatically:
1. **Pulls schema from database** (auto-extracts DDL for all tables)
2. **Trains on the schema** (saves table structures to memory)
3. **Answers questions in natural language** (generates SQL)
4. **Executes and returns results** (runs SQL and presents data)

## Features Implemented

### ✅ Auto Schema Extraction (`schema_tools.py`)
- `SchemaExtractor`: Automatically discovers all tables and extracts DDL
- Supports MySQL databases
- Gets table structures, column types, and relationships

### ✅ Auto Training (`schema_tools.py`)
- `DDLTrainer`: Saves all table schemas to agent memory
- LLM learns about your database structure
- Includes database summary for context

### ✅ Enhanced SQL Agent (`sql_agent.py`)
- Custom system prompt with schema awareness
- Memory tools for learning patterns
- Auto-training on startup
- FastAPI server included

### ✅ Complete Workflow Scripts
- `test_complete_workflow.py`: End-to-end testing
- `test_agent.py`: Basic agent testing
- `test_tools.py`: Tool availability testing

## Current Issues & Solutions

### Issue 1: LLM Model Doesn't Support Tool Calling ⚠️

**Problem:** The `qwen2.5-coder:7b` model doesn't support native tool/function calling.

**Solution:** Use a compatible Ollama model:
```bash
# Best options:
ollama pull llama3.1:8b
# or
ollama pull llama3.2:3b
# or
ollama pull mistral
```

Then update `config.py`:
```python
OLLAMA_MODEL = "llama3.1:8b"
```

### Issue 2: Database Permission Error ⚠️

**Problem:** The `readonly_user` doesn't have permission to read schema:
```
Access denied for user 'readonly_user'
```

**Solutions:**

**Option A: Grant Schema Read Permissions (Recommended)**
```sql
-- Grant permissions to read schema information
GRANT SELECT ON information_schema.* TO 'readonly_user'@'%';
GRANT SELECT ON mysql.* TO 'readonly_user'@'%';
GRANT SHOW DATABASES ON *.* TO 'readonly_user'@'%';
FLUSH PRIVILEGES;
```

**Option B: Use Admin User for Schema Extraction**

Update `config.py` to use an admin user temporarily for schema extraction:
```python
# For schema extraction (needs SHOW TABLES permission)
SCHEMA_DB_USER = "admin_user"
SCHEMA_DB_PASSWORD = "admin_password"

# For regular queries (can be readonly)
DB_USER = "readonly_user"
DB_PASSWORD = "readonly_password"
```

**Option C: Disable Auto-Training**

If you can't get schema permissions, disable auto-training and manually document your schema in the system prompt.

## File Structure

```
SqlAgent/
├── sql_agent.py              # Main agent with auto-training
├── schema_tools.py            # Schema extraction and DDL training
├── config.py                  # Database and LLM configuration
├── test_complete_workflow.py  # End-to-end testing
├── test_agent.py              # Basic agent testing
├── test_tools.py              # Tool testing
├── example.py                 # Usage examples
├── setup.sh                   # Installation script
├── FINDINGS.md                # Tool calling issue analysis
└── README_COMPLETE.md         # This file
```

## Usage

### 1. Start the Server (with auto-training)

```bash
python sql_agent.py
```

This will:
- Connect to database
- Extract all table schemas
- Train the agent memory
- Start FastAPI server on port 8000

### 2. Test the Complete Workflow

```bash
python test_complete_workflow.py
```

### 3. Web Interface

Access the web UI at: `http://localhost:8000`

### 4. API Documentation

Swagger docs at: `http://localhost:8000/docs`

## Configuration

Edit `config.py`:

```python
class Config:
    # Database connection
    DB_HOST = "your-db-host"
    DB_PORT = 3306
    DB_NAME = "your_database"
    DB_USER = "your_user"
    DB_PASSWORD = "your_password"

    # Ollama LLM
    OLLAMA_MODEL = "llama3.1:8b"  # Use tool-compatible model!
    OLLAMA_HOST = "http://localhost:11434"
```

## How It Works

### Startup Sequence

1. **Agent Initialization**
   - Creates Ollama LLM service
   - Sets up MySQL connection
   - Registers tools (run_sql, visualize_data, memory tools)
   - Applies custom system prompt with schema awareness

2. **Auto-Training** (if enabled)
   - Connects to database
   - Runs `SHOW TABLES` to get all tables
   - Runs `SHOW CREATE TABLE` for each table
   - Saves all DDL to agent memory
   - Creates database summary

3. **Ready for Queries**
   - User asks question in natural language
   - Agent searches memory for similar patterns
   - Agent knows database schema from training
   - Generates accurate SQL
   - Executes query
   - Returns formatted results

### Example Interaction

```
User: "How many distinct users are in the database?"

Agent thinks:
1. Searches memory for similar queries
2. Knows from training that there's a 'users' table
3. Generates SQL: SELECT COUNT(DISTINCT user_id) FROM users
4. Executes query via run_sql tool
5. Gets result: [{"count": 1523}]
6. Responds: "There are 1,523 distinct users in the database."
```

## Next Steps

1. **Fix LLM Model Issue**
   ```bash
   ollama pull llama3.1:8b
   ```
   Update `config.py` with new model

2. **Fix Database Permissions**
   - Grant schema read permissions to user
   - Or use separate admin user for schema extraction

3. **Test Complete Workflow**
   ```bash
   python test_complete_workflow.py
   ```

4. **Start Server**
   ```bash
   python sql_agent.py
   ```

## Advanced Features

### Disable Auto-Training

```python
from sql_agent import create_agent, run_server

agent, sql_runner, agent_memory = create_agent()
run_server(agent, sql_runner, agent_memory, auto_train=False)
```

### Manual Schema Training

```python
from schema_tools import SchemaExtractor, DDLTrainer
from vanna.core.tool import ToolContext

# Extract schema manually
extractor = SchemaExtractor(sql_runner, context)
ddl_map = await extractor.get_all_ddl()

# Train manually
trainer = DDLTrainer(agent_memory)
await trainer.train_on_ddl(ddl_map, context)
```

### Custom User Authentication

See `example.py` for custom `UserResolver` implementations.

## Troubleshooting

### "Tool calling not working"
→ Use `llama3.1:8b` or `mistral` model (see FINDINGS.md)

### "Access denied"
→ Grant schema permissions or use admin user (see Issue 2)

### "No results returned"
→ Check that LLM model supports tool calling

### "Agent doesn't use run_sql"
→ Model doesn't support tools - switch to compatible model

## References

- [Vanna AI Documentation](https://docs.vanna.com/)
- [Ollama Models](https://ollama.com/library)
- [FINDINGS.md](./FINDINGS.md) - Detailed tool calling analysis
