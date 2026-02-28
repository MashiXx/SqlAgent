# SqlAgent

An AI-powered SQL assistant that lets you query MySQL databases using natural language. Built with [Vanna](https://vanna.ai/) Agent API, supporting [Ollama](https://ollama.ai/) for local LLM inference or [Google Gemini](https://ai.google.dev/) as a cloud LLM, with [ChromaDB](https://www.trychroma.com/) for persistent schema caching.

## Features

- **Natural language to SQL** - Ask questions in plain English, get SQL results back
- **Multiple LLM providers** - Use Ollama for local inference or Google Gemini as a cloud alternative
- **Auto schema training** - Automatically extracts and learns your database schema on startup
- **Schema caching with ChromaDB** - Extracted schema is persisted so subsequent startups are instant
- **Schema refresh API** - Force re-extraction when your database schema changes
- **Web UI** - Chat interface served via FastAPI
- **Data visualization** - Generate charts from query results with Plotly
- **Role-based access control** - Admin and user groups with per-tool permissions
- **Agent memory** - Saves successful queries to improve future responses

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────┐
│  Web UI     │────▶│  FastAPI      │────▶│  Vanna  │
│  (Browser)  │◀────│  Server       │◀────│  Agent  │
└─────────────┘     └──────────────┘     └────┬────┘
                                              │
                    ┌─────────────────────────┤
                    │              │           │
               ┌────▼────┐  ┌─────▼─────┐ ┌──▼───────┐
               │ Ollama / │  │  MySQL    │ │ ChromaDB │
               │ Gemini   │  │  (Data)   │ │ (Memory) │
               │  (LLM)   │  └───────────┘ └──────────┘
               └──────────┘
```

## Prerequisites

- **Python** 3.10+
- **MySQL** database accessible from the machine
- **One of the following LLM providers:**
  - **Ollama** running locally (or on a remote host) with a tool-calling model (e.g., `qwen2.5`, `llama3.1`, `mistral`)
  - **Google Gemini** API key from [Google AI Studio](https://aistudio.google.com/)

## Quick Start

### 1. Clone and setup

```bash
git clone https://github.com/your-username/SqlAgent.git
cd SqlAgent
bash setup.sh
```

Or manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# MySQL Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database

# LLM Provider: "ollama" or "gemini"
LLM_PROVIDER=ollama

# Ollama (when LLM_PROVIDER=ollama)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# Gemini (when LLM_PROVIDER=gemini)
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Schema Cache
CHROMA_PERSIST_DIR=./chroma_data
SCHEMA_CACHE_ENABLED=true
```

### 3. Start your LLM provider

**Option A: Ollama (local)**

```bash
ollama serve
ollama pull qwen2.5:7b   # or your preferred model
```

**Option B: Gemini (cloud)**

Set your API key in `.env`:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
```

### 4. Run the agent

```bash
source venv/bin/activate
python sql_agent.py
```

The web UI will be available at `http://localhost:8000`.

## How It Works

### Schema Auto-Training

On first startup, SqlAgent:

1. Connects to your MySQL database
2. Extracts `CREATE TABLE` DDL for every table
3. Generates a schema summary (tables, columns, relationships)
4. Stores everything in ChromaDB as vector embeddings

On subsequent startups, it detects the existing cache and skips extraction. This means the first launch may take a moment (depending on database size), but every launch after that is fast.

### Query Flow

1. User asks a question in the web UI
2. The agent searches ChromaDB for relevant schema context
3. The LLM (Ollama or Gemini) generates a SQL query based on the schema and question
4. The query runs against MySQL and results are returned
5. The agent formats and presents the results (with optional charts)

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Web chat UI |
| `/api/v0/chat` | POST | Send a chat message |
| `/api/refresh-schema` | POST | Force re-extract database schema |
| `/api/schema-status` | GET | Check schema cache status |
| `/docs` | GET | Swagger API documentation |

### Refresh Schema

When your database schema changes, trigger a refresh:

```bash
curl -X POST http://localhost:8000/api/refresh-schema
```

### Check Schema Status

```bash
curl http://localhost:8000/api/schema-status
```

## Project Structure

```
SqlAgent/
├── sql_agent.py        # Main application - agent setup and server
├── config.py           # Configuration from environment variables
├── schema_tools.py     # Schema extraction and DDL training
├── example.py          # Usage examples (custom auth, multi-db, etc.)
├── requirements.txt    # Python dependencies
├── setup.sh            # Setup script
├── .env.example        # Environment variable template
└── chroma_data/        # ChromaDB persistent storage (auto-created)
```

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | `localhost` | MySQL host |
| `DB_PORT` | `3306` | MySQL port |
| `DB_USER` | `root` | MySQL username |
| `DB_PASSWORD` | (empty) | MySQL password |
| `DB_NAME` | `test` | MySQL database name |
| `LLM_PROVIDER` | `ollama` | LLM provider: `ollama` or `gemini` |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama2` | Ollama model name |
| `GEMINI_API_KEY` | (empty) | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `CHROMA_PERSIST_DIR` | `./chroma_data` | ChromaDB storage path |
| `SCHEMA_CACHE_ENABLED` | `true` | Enable schema caching |
| `SCHEMA_AUTO_TRAIN` | `true` | Auto-train schema on startup |

## Examples

The `example.py` file demonstrates several customization patterns:

```bash
python example.py custom-auth      # Custom user authentication
python example.py different-model  # Use a different Ollama model
python example.py limited-tools    # Read-only mode (no memory tools)
python example.py multi-db         # Multiple database connections
```

## Recommended Models

Models with good tool-calling support:

| Model | Size | Notes |
|---|---|---|
| `qwen2.5:7b` | ~4.7 GB | Best overall for SQL tasks |
| `llama3.1:8b` | ~4.7 GB | Good general purpose |
| `mistral` | ~4.1 GB | Lightweight, fast |

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

**Common issues:**

- **Agent returns SQL but no results** - Try a model with better tool-calling support (e.g., `qwen2.5:7b`)
- **Schema extraction is slow** - This only happens on first run; subsequent starts use the ChromaDB cache
- **Connection refused to Ollama** - Make sure `ollama serve` is running and `OLLAMA_HOST` is correct

## License

MIT
