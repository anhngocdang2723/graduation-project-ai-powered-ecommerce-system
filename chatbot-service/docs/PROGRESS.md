# 📊 PROGRESS TRACKING

## Tổng quan tiến độ

| Phase | Mô tả | Trạng thái | Hoàn thành |
|-------|-------|------------|------------|
| Phase 0 | Setup & Planning | ✅ Done | 100% |
| Phase 1 | Core Agents | ✅ Done | 100% |
| Phase 2 | Tools & Medusa API | 🔲 In Progress | 30% |
| Phase 3 | Response & Templates | 🔲 In Progress | 20% |
| Phase 4 | FE Widget & Admin UI | 🔲 Not Started | 0% |
| Phase 5 | Testing & Polish | 🔲 Not Started | 0% |

---

## Phase 0: Setup & Planning ✅

### Completed Tasks

- [x] Docker Compose setup (postgres, redis, medusa, chatbot, pgadmin)
- [x] Chatbot service skeleton (FastAPI)
- [x] Database schema design (`chatbot.sessions`, `chatbot.messages`, `chatbot.settings`)
- [x] Medusa schema analysis (export to `medusa-schema.json`)
- [x] Architecture design (Multi-Agent)
- [x] Decision Tree design
- [x] Documentation structure

### Files Created
- `docker-compose.yml` - Orchestration
- `chatbot-service/app/main.py` - FastAPI entry (basic)
- `chatbot-service/database/init.sql` - DB schema
- `chatbot-service/database/medusa-schema.json` - Medusa reference
- `chatbot-service/docs/README.md` - Project overview
- `chatbot-service/docs/ARCHITECTURE.md` - System design
- `chatbot-service/docs/DECISION_TREE.md` - Intent flow
- `chatbot-service/docs/PROGRESS.md` - This file

---

## Phase 1: Core Agents ✅

### Tasks

| Task | File | Status | Notes |
|------|------|--------|-------|
| Base Agent class | `app/agents/base.py` | ✅ | Agent protocol + AgentError |
| Config & Settings | `app/config.py` | ✅ | Env vars, feature flags |
| Pydantic Models | `app/models/*.py` | ✅ | Request/Response + agent types |
| Agent 1: Input Processor | `app/agents/input_processor.py` | ✅ | Text clean, lang detect |
| Agent 2: Intent Classifier | `app/agents/intent_classifier.py` | ✅ | Keyword matching |
| Agent 3: Orchestrator | `app/agents/orchestrator.py` | ✅ | Plan builder |
| Agent 4: Executor | `app/agents/executor.py` | ✅ | Tool runner |
| Agent 5: Response Generator | `app/agents/response_generator.py` | ✅ | Templates + quick replies |
| Intent Tree | `app/intents/tree.py` | 🔲 | Decision tree data |
| NLP: Text Cleaner | `app/nlp/text_cleaner.py` | 🔲 | Regex, normalize |
| NLP: Lang Detector | `app/nlp/lang_detector.py` | 🔲 | langdetect lib |

### Acceptance Criteria
- [ ] `/chat` endpoint processes through all 5 agents
- [ ] Intent classification works for basic keywords
- [ ] Session context is maintained
- [ ] Guest vs Customer detection works

---

## Phase 2: Tools & Medusa API 🔲

### Tasks

| Task | File | Status | Notes |
|------|------|--------|-------|
| Base Tool class | `app/tools/base.py` | 🔲 | |
| Product: search | `app/tools/product_tools.py` | ✅ | GET /store/products (+ publishable key) |
| Product: detail | `app/tools/product_tools.py` | 🔲 | GET /store/products/{id} |
| Order: get | `app/tools/order_tools.py` | 🔲 | GET /store/orders |
| Order: list | `app/tools/order_tools.py` | 🔲 | |
| Cart: get | `app/tools/cart_tools.py` | 🔲 | GET /store/carts/{id} |
| Cart: add item | `app/tools/cart_tools.py` | 🔲 | POST /store/carts/{id}/line-items |
| Cart: update | `app/tools/cart_tools.py` | 🔲 | |
| Cart: remove | `app/tools/cart_tools.py` | 🔲 | |
| Customer: get | `app/tools/customer_tools.py` | 🔲 | |

### Acceptance Criteria
- [ ] All tools can call Medusa API successfully
- [ ] Error handling for API failures
- [ ] Response data formatted for chatbot use

---

## Phase 3: Response & Templates 🔲

### Tasks

| Task | File | Status | Notes |
|------|------|--------|-------|
| Vietnamese templates | `app/templates/vi.py` | 🔲 | |
| English templates | `app/templates/en.py` | 🔲 | |
| LLM client (Qwen) | `app/llm/qwen.py` | 🔲 | Existing code |
| Quick Replies config | `app/templates/quick_replies.py` | 🔲 | |
| Product card format | `app/templates/formatters.py` | 🔲 | |

### Acceptance Criteria
- [ ] 90% of responses use templates (no LLM)
- [ ] LLM fallback works for unknown intents
- [ ] Quick replies render correctly

---

## Phase 4: FE Widget & Admin UI 🔲

### Tasks

| Task | File | Status | Notes |
|------|------|--------|-------|
| Chat Widget component | `vercel-commerce/components/chat/` | 🔲 | Existing basic |
| Quick Reply buttons | | 🔲 | |
| Product card in chat | | 🔲 | |
| Login prompt in chat | | 🔲 | |
| Admin: Chat history | `medusa/admin/routes/chatbot/` | 🔲 | Existing basic |
| Admin: Live chat view | | 🔲 | |
| Admin: Escalation alerts | | 🔲 | WebSocket |
| Admin: Take over chat | | 🔲 | |

### Acceptance Criteria
- [ ] Widget works on all pages
- [ ] Guest can chat without login
- [ ] Staff can take over escalated chats
- [ ] Chat history persists after page reload

---

## Phase 5: Testing & Polish 🔲

### Tasks

| Task | Status | Notes |
|------|--------|-------|
| Unit tests for agents | 🔲 | |
| Unit tests for tools | 🔲 | |
| Integration tests | ✅ | `tests/test_chat_pipeline.py` covers PRODUCT.SEARCH flow |
| Performance testing | 🔲 | Response time < 500ms |
| Error handling review | 🔲 | |
| Security review | 🔲 | |
| Documentation update | 🔲 | |

---

## 🐛 Known Issues

| Issue | Priority | Status | Notes |
|-------|----------|--------|-------|
| - | - | - | - |

---

## 📝 Decision Log

| Date | Decision | Reason |
|------|----------|--------|
| 2025-11-30 | Use Multi-Agent architecture | Modular, easier to debug |
| 2025-11-30 | NLP-first, LLM as fallback | Reduce cost & latency |
| 2025-11-30 | Separate chatbot schema | Avoid conflicts with Medusa |
| 2025-11-30 | Support Guest chat | Better UX, handle session migration |
| 2025-11-30 | Human escalation feature | Required for complex issues |
| 2025-11-30 | VN primary, EN secondary | Target market is Vietnam |

---

## 🔜 Next Steps

1. **Immediate (Today):**
   - [ ] Set `MEDUSA_PUBLISHABLE_KEY` and verify product search tool live
   - [ ] Align legacy flow to reuse tool headers (optional)

2. **This Week:**
   - [ ] Implement Guardrails v1 (input/output checks)
   - [ ] Implement Evaluator/Critic v1 (post-response heuristics)
   - [ ] Expand templates for additional intents

3. **Next Week:**
   - [ ] Memory v1 (conversation summary + profile)
   - [ ] Observability v1 (trace_id, timings)
   - [ ] Extend Medusa tools (orders, customers)

---

*Last updated: 2025-12-03*
