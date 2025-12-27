# Logging System Documentation

## Overview

Hệ thống logging đã được tích hợp vào cả **Multi-Agent Chatbot System** và **Recommendation Service** để theo dõi luồng dữ liệu một cách chi tiết, phục vụ cho báo cáo và quá trình bảo vệ đồ án.

## Chatbot Multi-Agent System Logging

### Cấu trúc Log

Log được ghi vào file `chatbot-service/logs/chatbot_YYYYMMDD.log` với format:

```
[TIMESTAMP] | LEVEL | COMPONENT | MESSAGE
```

### Các Agent và Log Tracking

#### 1. **Input Processor** (Agent 1)
- **Đầu vào**: Raw user message từ API
- **Xử lý**: 
  - Text normalization
  - Language detection
  - Context loading (previous messages, product IDs)
- **Đầu ra**: ProcessedInput object
- **Log format**: 
  ```
  [AGENT-1:InputProcessor] session={session_id} language={vi/en} user_type={guest/customer} cleaned_text='...'
  ```

#### 2. **Intent Classifier** (Agent 2)
- **Đầu vào**: ProcessedInput
- **Xử lý**: 
  - Keyword matching với VI_KEYWORDS/EN_KEYWORDS
  - Score calculation
  - Intent mapping
  - Entity extraction
- **Đầu ra**: IntentResult (intent, confidence, entities)
- **Log format**:
  ```
  [AGENT-2:IntentClassifier] intent={product_inquiry} confidence={0.85} entities={'product_query': 'balo'}
  ```

#### 3. **Orchestrator** (Agent 3)
- **Đầu vào**: ProcessedInput, IntentResult
- **Xử lý**:
  - Tag-based routing (action:*, scope:*)
  - Intent-based agent selection
  - Action plan generation
- **Đầu ra**: ActionPlan (tools to execute)
- **Log format**:
  ```
  [AGENT-3:Orchestrator] action_plan={'tools': ['product.search'], 'next_step': 'show_products'}
  ```

#### 4. **Executor** (Agent 4)
- **Đầu vào**: ProcessedInput, IntentResult, ActionPlan
- **Xử lý**:
  - Tool execution (product.search, cart.add, order.track, etc.)
  - Context-aware parameter resolution
  - Error handling
- **Đầu ra**: ToolResults (data, errors, timings)
- **Log format**:
  ```
  [AGENT-4:Executor] Tool execution SUCCESS - type=list, count=5
  ```

#### 5. **Response Generator** (Agent 5)
- **Đầu vào**: ProcessedInput, IntentResult, ActionPlan, ToolResults
- **Xử lý**:
  - Template-based response (FAQ, greetings)
  - LLM-based response (complex queries)
  - Product formatting
  - Quick reply generation
- **Đầu ra**: ChatResponse (text, products, quick_replies)
- **Log format**:
  ```
  [AGENT-5:ResponseGenerator] Generated response - products_count=5 response_length=127
  ```

#### 6. **Pipeline Summary**
```
[PIPELINE] Complete - session={session_id} total_time=245ms intent={product_inquiry}
```

### Log Levels

- **INFO**: Main flow tracking (mỗi agent execution)
- **DEBUG**: Chi tiết nội bộ (context loading, entity extraction)
- **WARNING**: Non-critical issues (unknown tools, fallback routing)
- **ERROR**: Errors with stack traces

### Ví dụ Luồng Log Hoàn Chỉnh

```
2025-12-21 15:30:45 | INFO     | agent.InputProcessor      | Processing input - session=sess_123 message_length=15
2025-12-21 15:30:45 | DEBUG    | agent.InputProcessor      | Context - last_intent=product_inquiry history_count=3
2025-12-21 15:30:45 | INFO     | agent.InputProcessor      | Input processed - language=vi user_type=customer tag=None
2025-12-21 15:30:45 | INFO     | agent.IntentClassifier    | Classifying intent - text='tìm balo đi học...'
2025-12-21 15:30:45 | DEBUG    | agent.IntentClassifier    | Intent scores - top=PRODUCT.SEARCH(5) secondary=None
2025-12-21 15:30:45 | INFO     | agent.IntentClassifier    | Intent classified - intent=product_inquiry confidence=0.85 entities={'product_query': 'balo đi học', 'quantity': 1}
2025-12-21 15:30:45 | INFO     | agent.Orchestrator        | Routing request - tag=None intent=product_inquiry
2025-12-21 15:30:45 | INFO     | agent.Orchestrator        | Implicit routing - intent=product_inquiry agent=SalesAgent
2025-12-21 15:30:45 | INFO     | agent.Executor            | Executing tools - count=1 tools=['product.search']
2025-12-21 15:30:45 | INFO     | agent.Executor            | Executing tool - name=product.search
2025-12-21 15:30:46 | INFO     | agent.Executor            | Tool execution complete - success=True errors=0
2025-12-21 15:30:46 | INFO     | agent.ResponseGenerator   | Generating response - intent=product_inquiry has_tool_result=True
2025-12-21 15:30:46 | INFO     | agent.ResponseGenerator   | Using product_found template - count=5
2025-12-21 15:30:46 | INFO     | agent.ResponseGenerator   | Response generated - text_length=127 products=5 quick_replies=4
2025-12-21 15:30:46 | INFO     | agent.main                | [PIPELINE] Complete - session=sess_123 total_time=245ms intent=product_inquiry
```

---

## Recommendation Service Logging

### Cấu trúc Log

Log được ghi vào file `recommendation-service/logs/recommendation_YYYYMMDD.log`

### Các Thành Phần Logging

#### 1. **Interaction Tracking**
- **Chức năng**: Track user interactions (view, add_to_cart, purchase, wishlist)
- **Log format**:
  ```
  TRACK | User={user_id} Type={view} Product={prod_123} Meta={...}
  ```

#### 2. **Recommendation Request**
- **Chức năng**: Log incoming recommendation requests
- **Log format**:
  ```
  REQUEST | User={user_id} Context={homepage} Limit={12} Filters={...}
  ```

#### 3. **Algorithm Selection**
- **Chức năng**: Log which algorithm is selected based on user stats
- **Strategies**:
  - `interaction_based`: User has interactions → hybrid approach
  - `trending_fallback`: New user → trending/random products
- **Log format**:
  ```
  ALGO_SELECT | User={user_id} Selected={interaction_based} Reason={User has 15 interactions} Stats={...}
  ```

#### 4. **Recommendation Result**
- **Chức năng**: Log final recommendations generated
- **Log format**:
  ```
  RESULT | User={user_id} Algo={hybrid} Count={12} Time={45.23ms} Details={...}
  ```

### Ví dụ Luồng Log Recommendation

```
2025-12-21 15:32:10 | INFO     | rec.main                  | Getting personalized recommendations - user=cus_abc limit=12
2025-12-21 15:32:10 | DEBUG    | rec.engine                | User interaction stats - user=cus_abc stats={'total_interactions': 15, 'views': 12, 'cart_adds': 2, 'purchases': 1}
2025-12-21 15:32:10 | INFO     | rec.engine                | ALGO_SELECT | User=cus_abc Selected=interaction_based Reason=User has 15 interactions Stats={...}
2025-12-21 15:32:10 | INFO     | rec.engine                | Added similar to cart/wishlist - count=4
2025-12-21 15:32:10 | INFO     | rec.engine                | Added category-based recommendations - count=4
2025-12-21 15:32:10 | INFO     | rec.engine                | Added collaborative recommendations - count=4
2025-12-21 15:32:10 | INFO     | rec.engine                | Added similar to recent products - count=3
2025-12-21 15:32:10 | INFO     | rec.main                  | RESULT | User=cus_abc Algo=hybrid Count=12 Time=45.23ms Details={'context': 'homepage'}
```

---

## Cách Sử Dụng Cho Báo Cáo

### 1. Extract Logs cho Demo

```bash
# Chatbot logs
grep "PIPELINE\|AGENT-" chatbot-service/logs/chatbot_20251221.log > demo_chatbot_flow.log

# Recommendation logs
grep "REQUEST\|RESULT\|ALGO_SELECT" recommendation-service/logs/recommendation_20251221.log > demo_rec_flow.log
```

### 2. Phân Tích Performance

```bash
# Average response time
grep "PIPELINE" chatbot-service/logs/*.log | grep -oP "total_time=\K\d+" | awk '{sum+=$1; count++} END {print "Avg:", sum/count, "ms"}'

# Success rate
grep "Tool execution" chatbot-service/logs/*.log | grep -c "SUCCESS"
```

### 3. Theo Dõi Intent Distribution

```bash
grep "Intent classified" chatbot-service/logs/*.log | grep -oP "intent=\K\w+" | sort | uniq -c
```

---

## Cấu Hình Logging

### Chatbot Service

File: `chatbot-service/app/logging_config.py`

```python
# Thay đổi log level
setup_logging(log_level="DEBUG")  # DEBUG, INFO, WARNING, ERROR

# Tắt file logging (chỉ console)
setup_logging(enable_file_logging=False)

# Tắt màu sắc
console_handler.setFormatter(AgentFormatter(use_color=False))
```

### Recommendation Service

File: `recommendation-service/app/logging_config.py` (tương tự)

---

## Log Rotation

Logs được tạo theo ngày (`chatbot_YYYYMMDD.log`). Để quản lý:

```bash
# Xóa logs cũ hơn 7 ngày
find chatbot-service/logs/ -name "chatbot_*.log" -mtime +7 -delete
find recommendation-service/logs/ -name "recommendation_*.log" -mtime +7 -delete
```

---

## Troubleshooting

### Không thấy logs

1. Kiểm tra thư mục logs có tồn tại:
   ```bash
   ls -la chatbot-service/logs/
   ```

2. Kiểm tra permissions:
   ```bash
   chmod 755 chatbot-service/logs/
   ```

3. Kiểm tra logging có được setup:
   ```python
   # Trong main.py/worker.py phải có:
   from app.logging_config import setup_logging
   setup_logging()
   ```

### Log bị duplicate

- Đảm bảo `setup_logging()` chỉ được gọi 1 lần trong mỗi process
- Kiểm tra không có multiple handlers

---

## Best Practices

1. **Sensitive Data**: Không log passwords, tokens, full credit card numbers
2. **PII**: Cẩn thận với user emails, phones - có thể hash hoặc mask
3. **Performance**: Sử dụng `DEBUG` level cho chi tiết, `INFO` cho production
4. **Structure**: Log messages nên có format consistent để dễ parse

---

## Contact

Nếu có vấn đề với logging system, liên hệ team development.
