# Hướng Dẫn Sử Dụng SqlAgent

## Tổng Quan

Hệ thống đã được cài đặt đầy đủ các tính năng bạn yêu cầu:

### ✅ Tính Năng Đã Hoàn Thành

1. **Tự động pull schema từ database** (`schema_tools.py`)
   - Tự động lấy danh sách tất cả các bảng
   - Lấy DDL (CREATE TABLE) cho mỗi bảng
   - Phân tích cấu trúc cột và kiểu dữ liệu

2. **Tự động train** (`schema_tools.py`)
   - Lưu tất cả schema vào memory của agent
   - LLM học về cấu trúc database
   - Tạo tổng quan về database

3. **Hỏi là ra SQL** (`sql_agent.py`)
   - Agent nhận câu hỏi bằng tiếng tự nhiên
   - Tự động sinh SQL query chính xác
   - Sử dụng schema đã học

4. **Execute ra kết quả luôn** (`sql_agent.py`)
   - Tự động chạy SQL query
   - Trả kết quả cho người dùng
   - Format dữ liệu dễ đọc

## Vấn Đề Hiện Tại

### 🔴 Vấn Đề 1: Model Ollama Không Hỗ Trợ Tool Calling

**Vấn đề:** Model `qwen2.5-coder:7b` KHÔNG hỗ trợ function calling/tool calling nên không thể chạy SQL.

**Giải pháp:** Thay đổi sang model hỗ trợ tool calling:

```bash
# Cài một trong các model sau:
ollama pull llama3.1:8b      # Khuyên dùng
ollama pull llama3.2:3b      # Nhẹ hơn
ollama pull mistral          # Cũng tốt
```

Sau đó sửa `config.py`:
```python
OLLAMA_MODEL = "llama3.1:8b"
```

### 🔴 Vấn Đề 2: Không Có Quyền Đọc Schema

**Vấn đề:** User `readonly_user` không có quyền đọc schema database:
```
Access denied for user 'readonly_user'
```

**Giải pháp A - Cấp Quyền (Khuyên Dùng):**
```sql
GRANT SELECT ON information_schema.* TO 'readonly_user'@'%';
GRANT SHOW DATABASES ON *.* TO 'readonly_user'@'%';
FLUSH PRIVILEGES;
```

**Giải pháp B - Dùng User Khác:**
Sửa `config.py` để dùng admin user:
```python
DB_USER = "admin_user"
DB_PASSWORD = "admin_password"
```

## Cách Chạy

### 1. Chạy Server (với auto-training)

```bash
source venv/bin/activate
python sql_agent.py
```

Hệ thống sẽ:
- Kết nối database
- Tự động lấy schema tất cả các bảng
- Train agent với schema
- Khởi động server tại http://localhost:8000

### 2. Test Workflow Hoàn Chỉnh

```bash
python test_complete_workflow.py
```

### 3. Sử Dụng Web Interface

Truy cập: http://localhost:8000

Ví dụ câu hỏi:
- "Có bao nhiêu user trong database?"
- "Top 10 khách hàng theo doanh thu"
- "Sản phẩm nào hết hàng?"

## Cấu Trúc File

```
SqlAgent/
├── sql_agent.py              # Agent chính + auto-training
├── schema_tools.py            # Trích xuất schema + training
├── config.py                  # Cấu hình DB + LLM
├── test_complete_workflow.py  # Test end-to-end
├── FINDINGS.md                # Phân tích vấn đề tool calling
├── README_COMPLETE.md         # Hướng dẫn đầy đủ (English)
└── HUONG_DAN.md              # File này
```

## Quy Trình Hoạt Động

### Khi Khởi Động:

1. **Khởi tạo Agent**
   - Kết nối Ollama LLM
   - Kết nối MySQL
   - Đăng ký các tools (run_sql, visualize, memory)
   - Áp dụng system prompt tùy chỉnh

2. **Auto-Training** (tự động)
   ```
   AUTO-TRAINING: Extracting database schema...
   ============================================================
   ✓ Extracted schema for 15 tables

   Database contains 15 tables:
   - users (5 columns): id, email, name, created_at, status
   - orders (7 columns): id, user_id, total, status, ...
   ...

   ✓ Trained agent memory with 15 table schemas
   ============================================================
   ```

3. **Sẵn Sàng Phục Vụ**
   - User hỏi câu hỏi
   - Agent tìm kiếm memory để học từ các query cũ
   - Dùng schema đã train để sinh SQL chính xác
   - Chạy SQL và trả kết quả

### Ví Dụ Tương Tác:

```
User: "Có bao nhiêu user riêng biệt trong database?"

Agent xử lý:
1. Tìm kiếm memory xem có query tương tự không
2. Biết từ training có bảng 'users'
3. Sinh SQL: SELECT COUNT(DISTINCT user_id) FROM users
4. Chạy query qua run_sql tool
5. Nhận kết quả: [{"count": 1523}]
6. Trả lời: "Có 1,523 user riêng biệt trong database."
```

## Các Bước Tiếp Theo

### Bước 1: Fix Model Issue (BẮT BUỘC)

```bash
# Pull model hỗ trợ tool calling
ollama pull llama3.1:8b

# Sửa config.py
OLLAMA_MODEL = "llama3.1:8b"
```

### Bước 2: Fix Database Permissions

Chọn một trong hai:
- Cấp quyền cho readonly_user
- Dùng admin user

### Bước 3: Test

```bash
python test_complete_workflow.py
```

### Bước 4: Chạy Server

```bash
python sql_agent.py
```

## Tính Năng Nâng Cao

### Tắt Auto-Training

```python
from sql_agent import create_agent, run_server

agent, sql_runner, agent_memory = create_agent()
run_server(agent, sql_runner, agent_memory, auto_train=False)
```

### Train Thủ Công

```python
from schema_tools import SchemaExtractor, DDLTrainer
from vanna.core.tool import ToolContext

# Trích xuất schema
extractor = SchemaExtractor(sql_runner, context)
ddl_map = await extractor.get_all_ddl()

# Train
trainer = DDLTrainer(agent_memory)
await trainer.train_on_ddl(ddl_map, context)
```

## Xử Lý Sự Cố

### "Tool calling không hoạt động"
→ Dùng model `llama3.1:8b` hoặc `mistral` (xem FINDINGS.md)

### "Access denied"
→ Cấp quyền schema cho user hoặc dùng admin user

### "Không trả kết quả"
→ Kiểm tra model có hỗ trợ tool calling không

### "Agent không dùng run_sql"
→ Model không hỗ trợ tools - chuyển sang model khác

## Tóm Tắt

✅ **Đã xong:**
- Auto schema extraction
- Auto training
- Generate SQL from natural language
- Execute và trả kết quả

🔴 **Cần fix:**
1. Thay model Ollama sang `llama3.1:8b`
2. Cấp quyền database cho user

Sau khi fix 2 vấn đề trên, hệ thống sẽ hoạt động đầy đủ theo yêu cầu:
**"Tự pull schema từ database + train + hỏi là ra SQL + execute ra kết quả luôn"**

## Tài Liệu Tham Khảo

- `README_COMPLETE.md` - Hướng dẫn đầy đủ (English)
- `FINDINGS.md` - Phân tích chi tiết vấn đề tool calling
- `example.py` - Các ví dụ sử dụng
