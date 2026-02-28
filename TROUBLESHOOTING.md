# Troubleshooting Guide

## Vấn đề: Agent chỉ hiển thị SQL query mà không trả về kết quả

### Triệu chứng
Agent gọi tool `run_sql` nhưng chỉ hiển thị câu lệnh SQL, không hiển thị kết quả thực tế từ database.

```json
{
  "name": "run_sql",
  "arguments": {
    "sql": "SELECT COUNT(*) FROM users;"
  }
}
```

### Nguyên nhân có thể

1. **Model không hỗ trợ tool calling đúng cách**
2. **Agent không được config system prompt**
3. **FastAPI server không xử lý tool results**
4. **Model cần nhiều iterations để hoàn thành**

### Giải pháp

#### 1. Test Agent trực tiếp (không qua web UI)

```bash
# Test cơ bản
python test_agent.py

# Test với debug mode
python debug_agent.py
```

Điều này giúp kiểm tra xem vấn đề là ở agent hay ở web UI.

#### 2. Kiểm tra logs

Logs sẽ hiển thị chi tiết về:
- Tool được gọi
- Arguments được truyền
- Results được trả về
- Responses từ LLM

#### 3. Thử model khác

Một số models hoạt động tốt hơn với tools:

**Tốt nhất:**
```bash
ollama pull qwen2.5:7b
# Cập nhật .env: OLLAMA_MODEL=qwen2.5:7b
```

**Hoặc:**
```bash
ollama pull llama3.1:8b
# Cập nhật .env: OLLAMA_MODEL=llama3.1:8b
```

**Hoặc:**
```bash
ollama pull mistral
# Cập nhật .env: OLLAMA_MODEL=mistral
```

#### 4. Kiểm tra Agent configuration

Đảm bảo agent có system prompt (đã được thêm vào code):

```python
agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    user_resolver=user_resolver,
    agent_memory=agent_memory,
    system_prompt=system_prompt  # ← Quan trọng!
)
```

#### 5. Tăng max iterations

Thêm vào khi tạo agent:

```python
agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    user_resolver=user_resolver,
    agent_memory=agent_memory,
    system_prompt=system_prompt,
    max_iterations=5  # ← Cho phép nhiều iterations hơn
)
```

#### 6. Kiểm tra tool results trong web UI

Mở developer console trong browser (F12) và xem network requests:
- Xem request/response từ API
- Kiểm tra xem tool results có được trả về không

#### 7. Test với câu hỏi đơn giản

Thử các câu hỏi dễ trước:

```
"Show tables"
"SELECT * FROM users LIMIT 5"
"Count records in users table"
```

### Debug Commands

```bash
# 1. Chạy test script
python test_agent.py

# 2. Chạy debug mode
python debug_agent.py

# 3. Chạy với full logging
python sql_agent.py 2>&1 | tee agent.log

# 4. Kiểm tra Ollama
curl http://10.13.13.6:11434/api/version

# 5. Test Ollama tool calling
ollama run qwen2.5-coder:7b "Can you use tools?"
```

### Kiểm tra Database Connection

```bash
# Test MySQL connection
mysql -h layer-sea.db.vpn -P 6033 -u readonly_user -p dson

# Hoặc với Python
python -c "
from config import Config
from vanna.integrations.mysql import MySQLRunner

runner = MySQLRunner(
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME
)

result = runner.run_sql('SHOW TABLES')
print(result)
"
```

### Nếu vẫn không hoạt động

#### Option A: Sử dụng Vanna Cloud (có UI tốt hơn)

```python
# Thay vì Ollama, dùng OpenAI hoặc Anthropic
from vanna.integrations.openai import OpenAILlmService

llm = OpenAILlmService(
    api_key="your-api-key",
    model="gpt-4"
)
```

#### Option B: Quay lại CLI mode đơn giản hơn

Có thể tạo một version CLI đơn giản mà không dùng Agent API phức tạp.

#### Option C: Check Vanna version

```bash
pip show vanna
# Đảm bảo >= 0.8.0

# Upgrade nếu cần
pip install --upgrade vanna
```

### Useful Links

- [Vanna Agent Documentation](https://docs.vanna.ai/agents/)
- [Ollama Tool Support](https://ollama.ai/blog/tool-support)
- [Vanna GitHub Issues](https://github.com/vanna-ai/vanna/issues)

### Contact

Nếu vẫn gặp vấn đề, hãy:
1. Chạy `debug_agent.py` và lưu output
2. Kiểm tra logs
3. Share error messages cụ thể
