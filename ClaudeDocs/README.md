# SqlAgent

A Natural Language to SQL application powered by Vanna.ai Agent API, Ollama, and MySQL. This application provides a web-based interface for querying databases using natural language.

## Features

- **Natural Language Queries**: Ask questions in plain English and get SQL + results
- **Web UI**: Modern FastAPI-powered web interface
- **Local LLM**: Uses Ollama for privacy-friendly local inference
- **MySQL Support**: Connect to any MySQL database
- **Agent Memory**: Remembers successful queries to improve over time
- **Visualization**: Automatic data visualization with Plotly
- **Role-Based Access**: Configurable user authentication and access control
- **Tool Registry**: Extensible architecture with pluggable tools

## Tech Stack

- **Vanna.ai Agent API**: Advanced text-to-SQL framework
- **Ollama**: Local LLM runtime (privacy-friendly)
- **FastAPI**: Modern web framework
- **MySQL**: Database backend
- **Python 3.8+**: Programming language

## Architecture

```
┌─────────────────┐
│   Web Browser   │
└────────┬────────┘
         │ HTTP
         v
┌─────────────────┐
│  FastAPI Server │
│  (Port 8000)    │
└────────┬────────┘
         │
         v
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  Vanna Agent    │────>│   Ollama     │     │   MySQL     │
│  + Tool Registry│     │   LLM        │     │  Database   │
│  + Memory       │     │  (Port 11434)│     │ (Port 3306) │
└─────────────────┘     └──────────────┘     └─────────────┘
```

## Prerequisites

### 1. Python 3.8 or higher

```bash
python3 --version
```

### 2. Ollama installed and running

```bash
# Install Ollama from https://ollama.ai

# Pull a model (choose one):
ollama pull llama2        # Faster, smaller
ollama pull codellama     # Better for SQL
ollama pull mistral       # Good balance

# Verify Ollama is running:
ollama list
```

### 3. MySQL database

- Running MySQL server
- Database with some tables/data
- User credentials with appropriate permissions

## Installation

### Quick Setup

```bash
# 1. Clone or download this repository
cd SqlAgent

# 2. Run the setup script
chmod +x setup.sh
./setup.sh

# 3. Edit .env file with your credentials
nano .env
```

### Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
nano .env  # Edit with your settings
```

## Configuration

Edit `.env` file with your settings:

```env
# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

## Usage

### Starting the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run the agent
python sql_agent.py
```

The application will be available at:
- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Using the Web Interface

1. Open http://localhost:8000 in your browser
2. Type your question in natural language
3. The agent will:
   - Generate SQL query
   - Execute it against your database
   - Display results
   - Create visualizations (if applicable)

### Example Questions

- "How many records are in the users table?"
- "Show me the top 10 customers by revenue"
- "What is the average order value?"
- "List all products that are out of stock"
- "Show me sales by month for the last year"
- "Who are the most active users this week?"

## Advanced Usage

### Custom Authentication

Create custom user authentication by extending `UserResolver`:

```python
from vanna.core.user import UserResolver, User, RequestContext

class CustomUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        user_email = request_context.get_header('X-User-Email')
        # Your custom logic here
        return User(
            id=user_email,
            email=user_email,
            group_memberships=['admin']
        )
```

### Multiple Databases

See `example.py` for connecting to multiple databases simultaneously.

### Custom Tools

Add custom tools to the agent:

```python
from vanna.tools import Tool

class CustomTool(Tool):
    def execute(self, **kwargs):
        # Your custom logic
        pass

tools.register_local_tool(CustomTool(), access_groups=['admin'])
```

### Using Different Models

```bash
# Pull a more capable model
ollama pull codellama

# Update .env
OLLAMA_MODEL=codellama

# Or use model variants
OLLAMA_MODEL=llama2:13b
OLLAMA_MODEL=mistral:latest
```

## Examples

The `example.py` file includes several usage patterns:

```bash
# Basic usage
python example.py basic

# Custom authentication
python example.py custom-auth

# Different Ollama model
python example.py different-model

# Limited tools (read-only)
python example.py limited-tools

# Multiple database connections
python example.py multi-db
```

## API Endpoints

### Main Endpoints

- `GET /`: Web UI
- `POST /api/v1/query`: Submit natural language query
- `GET /api/v1/history`: Get query history
- `POST /api/v1/feedback`: Provide feedback on queries

### Authentication

By default, users are identified by the `vanna_email` cookie. Customize authentication by implementing your own `UserResolver`.

## Project Structure

```
SqlAgent/
├── sql_agent.py          # Main agent and server
├── config.py             # Configuration management
├── example.py            # Usage examples
├── requirements.txt      # Python dependencies
├── setup.sh              # Setup script
├── .env.example         # Example environment variables
├── .env                 # Your configuration (not in git)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## How It Works

### Query Flow

1. **User Input**: User types question in web UI
2. **Agent Processing**: Vanna Agent receives the question
3. **Memory Search**: Agent searches for similar past queries
4. **Context Building**: Retrieves relevant database schema
5. **LLM Generation**: Ollama generates SQL query
6. **Execution**: SQL runs against MySQL database
7. **Visualization**: Optionally creates charts
8. **Memory Update**: Saves successful queries for future use

### Agent Components

- **LLM Service**: OllamaLlmService for local inference
- **Tool Registry**: Manages available tools and access control
- **SQL Runner**: Executes queries against MySQL
- **Agent Memory**: Stores successful queries and learnings
- **User Resolver**: Handles authentication and authorization
- **Visualization**: Automatic chart generation

## Troubleshooting

### Ollama Connection Error

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama
ollama serve

# Verify model is available
ollama list
```

### Database Connection Error

```bash
# Test MySQL connection
mysql -h localhost -u username -p database_name

# Check credentials in .env
cat .env | grep DB_
```

### Poor SQL Generation

- Use a more capable model (codellama, llama2:13b)
- Add example queries to agent memory
- Ensure database schema is accessible
- Provide more context in your questions

### Port Already in Use

```bash
# Change port in sql_agent.py or .env
SERVER_PORT=8001

# Or find and kill process using port 8000
lsof -i :8000
kill -9 <PID>
```

## Security Considerations

- **Never commit `.env`**: Contains sensitive credentials
- **Use read-only DB users**: Limit database permissions
- **Implement proper auth**: Replace SimpleUserResolver in production
- **Review generated SQL**: Before executing in production
- **Network security**: Use firewall rules to restrict access
- **Keep updated**: Regularly update dependencies

## Performance Optimization

### Model Selection

- **llama2**: Fast, good for simple queries
- **codellama**: Better SQL understanding
- **llama2:13b**: More accurate but slower
- **mistral**: Good balance of speed and quality

### Memory Management

- Adjust `max_items` in `DemoAgentMemory`
- Regularly clean up old memories
- Use production memory backend for scale

### Database Optimization

- Index frequently queried columns
- Use database query caching
- Limit result set sizes
- Implement query timeouts

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Tools

1. Create tool class extending `Tool`
2. Register in `ToolRegistry`
3. Assign access groups

### Debugging

```bash
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "sql_agent.py"]
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn sql_agent:app --workers 4 --bind 0.0.0.0:8000
```

### Environment Variables

Set production environment variables:

```bash
export DB_HOST=prod-db.example.com
export OLLAMA_MODEL=codellama
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Resources

- [Vanna.ai Documentation](https://vanna.ai/docs/)
- [Vanna Agent API](https://docs.vanna.ai/agents/)
- [Ollama Documentation](https://ollama.ai)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

## License

This project is open source and available for educational and commercial use.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the documentation
- Review example.py for usage patterns

## Changelog

### v2.0.0 (Current)
- Migrated to Vanna Agent API
- Added FastAPI web server
- Implemented tool registry system
- Added user authentication
- Integrated agent memory
- Added visualization support

### v1.0.0
- Initial CLI-based implementation
- Basic Vanna integration
- MySQL support
- Ollama integration
