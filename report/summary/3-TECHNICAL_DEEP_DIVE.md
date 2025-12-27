# 🎓 ĐIỂM NỔI BẬT VÀ CÔNG NGHỆ CHI TIẾT

## 📌 I. ĐIỂM NỔI BẬT CỦA CHATBOT MULTI-AGENT

### 1.1 Tại Sao Cần Multi-Agent Architecture?

**Vấn đề với LLM-only approach:**
- ❌ Chậm: LLM inference mất 1-3 giây
- ❌ Tốn kém: $0.01+ per API call
- ❌ Không reliable: Hallucination, sai tool call
- ❌ Không scalable: Rate limiting từ LLM provider

**Giải pháp: Multi-Agent Architecture**
- ✅ Nhanh: 50-100ms cho hầu hết requests
- ✅ Rẻ: $0 cho 90% requests (NLP-only)
- ✅ Reliable: Rule-based + explicit tool calls
- ✅ Scalable: Horizontal scaling không bị rate limit

---

### 1.2 5 Agents Giải Quyết Những Vấn Đề Gì?

```
PROBLEM: "Tôi muốn tìm balo màu đỏ"

WITHOUT Multi-Agent:
└─> Single LLM
    ├─ Parse user intent (expensive)
    ├─ Extract entities (expensive)
    ├─ Choose tool (error-prone)
    ├─ Call tool (expensive)
    ├─ Generate response (expensive)
    └─ Response time: 2-3 seconds, Cost: $0.01

WITH Multi-Agent:
└─> Agent 1: Clean text (50ms, $0)
    └─> Agent 2: Classify intent = PRODUCT.SEARCH (20ms, $0)
        └─> Agent 3: Validate permissions (10ms, $0)
            └─> Agent 4: Execute search_products("balo màu đỏ") (150ms, $0)
                └─> Agent 5: Generate response from template (30ms, $0)
                    └─ Response time: 260ms, Cost: $0
```

---

### 1.3 Decision Tree vs LLM

**Decision Tree Approach (Agent 2):**

```
User: "tìm balo"
│
├─ Contains "tìm" OR "search"? → YES
│
├─ Contains "order" OR "cart"? → NO
│
├─ Contains "sản phẩm" OR "product"? → YES
│
├─ Contains "so sánh" OR "compare"? → NO
│
└─> INTENT = PRODUCT.SEARCH ✅
    Extract query: "balo"
```

**LLM Approach:**

```
User: "tìm balo"
│
└─> Call LLM: "What is the user's intent?"
    └─> LLM processes entire context
        └─> Returns: {"intent": "search_product", "query": "balo"}
            └─> 1000-3000ms, $0.001+, possible hallucination
```

**Comparison:**
| Aspect | Decision Tree | LLM |
|--------|--------------|-----|
| Speed | 10-20ms | 1000-3000ms |
| Cost | $0 | $0.001+ |
| Accuracy | 95%+ | 85-90% |
| Edge cases | Limited | Flexible |
| Interpretable | ✅ Yes | ❌ Black box |

---

### 1.4 Tool Execution Pattern

**Pattern 1: Single Tool Call**

```
Intent: PRODUCT.SEARCH
Query: "balo đỏ"
│
└─> Executor calls:
    └─> search_products(query="balo đỏ", limit=5)
        └─> Returns: [prod_1, prod_2, prod_3]
            └─> Response Generator creates template:
                "Tìm thấy 3 sản phẩm cho 'balo đỏ'"
```

**Pattern 2: Multi-Step Conversation**

```
Step 1 - User: "Theo dõi đơn hàng"
         Intent: ORDER.TRACK (requires order_id)
         Response: "Vui lòng cung cấp số đơn hàng"

Step 2 - User: "123456"
         Context: order_id = "123456"
         Executor calls:
         └─> get_order(order_id="123456")
             └─> Returns: {status: "shipped", tracking: "..."}
                 └─> Response: "Đơn hàng #123456 đang vận chuyển..."
```

**Pattern 3: Permission-Based Routing**

```
User: "guest" (chưa đăng nhập)
Intent: ORDER.TRACK
│
├─ Permission check: customer-only intent?
│
└─> NO PERMISSION
    Response: "Vui lòng đăng nhập để xem đơn hàng"
    Action: show_login_modal
```

---

### 1.5 Human Escalation Flow

```
SCENARIO: Customer says "Tôi muốn nói chuyện với nhân viên"

Step 1 - Detect escalation
└─> Intent = SUPPORT.ESCALATE

Step 2 - Orchestrator validates
└─> Can escalate? Yes
    └─> session.status = 'escalated'

Step 3 - Notify admin dashboard
└─> WebSocket message:
    {
      "type": "escalation_request",
      "session_id": "sess_12345",
      "customer": "john@email.com",
      "last_message": "Sản phẩm bị hỏng, tôi muốn đổi",
      "conversation_history": [...]
    }

Step 4 - Admin UI
└─> 🔔 Notification appears
    ├─ Show customer info
    ├─ Show conversation history
    └─ [Take Over] button

Step 5 - Staff takes over
└─> Click "Take Over"
    └─> session.staff_id = 'staff_123'
    └─> AI pauses, chat continues with human

Step 6 - Customer receives human support
└─> Customer & staff chat in real-time
    └─> AI monitors (can suggest quick replies)
        └─> Staff resolves issue
            └─> Close conversation
```

---

### 1.6 Error Handling & Resilience

**Example: Product Search Fails**

```
User: "tìm balo đỏ"
│
└─> Executor calls: search_products(query="balo đỏ")
    └─> API timeout / error
        │
        ├─ Retry logic:
        │  └─ Retry 1: Wait 1s, try again
        │     Fail again
        │  └─ Retry 2: Wait 2s, try again
        │     Fail again
        │  └─ Max retries reached
        │
        └─ Fallback:
           ├─ Check cache for recent search results
           ├─ Return cached results if available
           ├─ Or return empty but helpful response:
           │  "Hiện tại không thể tìm kiếm, vui lòng thử lại"
           └─ Log error for monitoring
```

---

## 📊 II. ĐIỂM NỔI BẬT CỦA RECOMMENDATION ENGINE

### 2.1 Hybrid Algorithm vs Pure Approaches

**Problem:** Chọn phương pháp nào cho ML recommendation?

**Approaches:**

```
1. CONTENT-BASED ONLY
   ├─ Pro: Simple, interpretable, no cold start
   ├─ Con: Lack of discovery (only similar to viewed)
   └─ Result: Limited diversity, boring recommendations

2. COLLABORATIVE FILTERING ONLY
   ├─ Pro: Discover new products, proven in Netflix/Amazon
   ├─ Con: Cold start problem (new users/products)
   └─ Result: Good for active users, bad for new users

3. HYBRID (OUR CHOICE) ⭐
   ├─ Pro: Combines strength of both
   │  ├─ Content: Handles new users/products
   │  ├─ Collaborative: Discovers new items
   │  └─ Both: Better accuracy
   │
   └─ Formula: Score = 0.4×Content + 0.6×Collaborative
```

**Formula Explanation:**

```
HYBRID_SCORE(user, product) = 
    0.4 × CONTENT_SCORE(user, product) +
    0.6 × COLLABORATIVE_SCORE(user, product)

WHERE:
  CONTENT_SCORE = 
    Σ(user_category_preference[cat] × product_category_match[cat])
    └─ How much user likes this product's category?
       Example: If user viewed 5 backpacks, score=0.8
                If user never viewed shoes, score=0.2

  COLLABORATIVE_SCORE = 
    Σ(similarity(user, user_i) × rating(user_i, product))
    └─ Would similar users buy this product?
       Example: 10 similar users bought this product → score=0.7
```

---

### 2.2 5 Recommendation Strategies

**Strategy 1: Hybrid (Default) - 70% of requests**

```
Use case: Regular users with some history
Score = 0.4×Content + 0.6×Collaborative
Time: 200-500ms (computed) / <50ms (cached)
```

**Strategy 2: Content-Based - 10% of requests**

```
Use case: New users (cold start problem)
How: "Show products similar to what you viewed"
Products: Same category as viewed items
Time: <100ms
```

**Strategy 3: Collaborative Filtering - 10% of requests**

```
Use case: Mature users with lots of interactions
How: "Show products bought by similar users"
Products: What users like you also purchased
Time: 300-500ms
```

**Strategy 4: Trending - 5% of requests**

```
Use case: Discover what's popular
Metric: Most viewed in last 7 days
Time: <50ms (cached)
```

**Strategy 5: Frequently Bought Together - 5% of requests**

```
Use case: Cross-sell / upsell
How: "Often bought together"
Products: Products frequently co-purchased
Time: <50ms (pre-computed)
```

---

### 2.3 Cold Start Problem Solution

**Problem:** New user arrives → No interaction history → Can't recommend

**Solution:**

```
New User Flow:

1. First page view: Product A
   └─ Track as interaction (content_based score)
   └─ Recommendation strategy = Content-Based
       └─ Find products in same category
       └─ Recommend top 5

2. Second page view: Product B
   └─ Now has 2 interactions
   └─ Still use Content-Based (not enough data)

3. After ~10 interactions
   └─ User has enough history
   └─ Switch to Hybrid algorithm
   └─ Better recommendations

4. Algorithm selection:
   if interaction_count < 5:
     use ContentBased()
   elif interaction_count < 20:
     use Hybrid(w_content=0.6, w_collab=0.4)
   else:
     use Hybrid(w_content=0.4, w_collab=0.6)
```

---

### 2.4 Caching Strategy

**Why Cache?**

```
Without cache:
- User loads homepage
- Need recommendations for 3 products
- Each needs computation: 200-500ms
- Total: 600-1500ms ❌ Too slow!

With cache:
- First time: Compute + store in Redis → 500ms
- Next 50 users (within 1 hour TTL): <50ms ✅ Fast!
```

**Cache Strategy:**

```python
def get_recommendations(user_id, limit=10):
    # Step 1: Check Redis cache
    cache_key = f"rec:recommendations:{user_id}"
    cached = redis.get(cache_key)
    
    if cached and not expired(cached):
        return cached  # <50ms ✅
    
    # Step 2: Compute recommendations
    recommendations = compute_hybrid_score(user_id, limit)
    
    # Step 3: Store in cache (1 hour TTL)
    redis.setex(
        cache_key,
        3600,  # 1 hour
        json.dumps(recommendations)
    )
    
    return recommendations  # First time 200-500ms
```

**Cache Hit Rate Analysis:**

```
Assumption: 1000 users/day

Scenario 1 - Low engagement:
└─ Users visit 1-2 times/day
└─ Cache TTL: 1 hour
└─ Cache hit rate: ~80%
└─ Avg response: 0.8×50ms + 0.2×300ms = 100ms

Scenario 2 - High engagement:
└─ Users visit 5-10 times/day
└─ Same TTL
└─ Cache hit rate: ~95%
└─ Avg response: 0.95×50ms + 0.05×300ms = 65ms

Target: >80% cache hit rate
```

---

### 2.5 Similarity Computation

**Product Similarity (Pre-computed Nightly)**

```python
def compute_product_similarities():
    """
    For each product pair, calculate similarity score.
    Run once/day at 2 AM (off-peak).
    Result: Stored in rec_product_similarities table
    """
    
    # Algorithm:
    products = get_all_products()  # 100+ products
    
    for i in range(len(products)):
        for j in range(i+1, len(products)):
            prod_i = products[i]
            prod_j = products[j]
            
            # Calculate similarity
            similarity = 0
            
            # 1. Category match (60% weight)
            if prod_i.category == prod_j.category:
                similarity += 0.6
            
            # 2. Tag overlap (20% weight)
            tag_overlap = len(set(prod_i.tags) & set(prod_j.tags))
            similarity += 0.2 * (tag_overlap / max_tags)
            
            # 3. Co-occurrence (20% weight)
            # How often bought together?
            co_buys = count_co_purchases(prod_i.id, prod_j.id)
            similarity += 0.2 * min(co_buys / 10, 1.0)
            
            # Store result
            store_similarity(prod_i.id, prod_j.id, similarity)
    
    # Cost: O(n²) for n products
    # Optimization: Only update if products changed
```

**User Similarity (For Collaborative Filtering)**

```python
def compute_user_similarities():
    """
    Find similar users based on interaction patterns.
    Used during recommendation generation.
    """
    
    # Algorithm: Cosine similarity on preference vectors
    
    users = get_all_users()
    
    for user in users:
        # Get user's preference vector
        prefs = get_user_preferences(user.id)
        # prefs = {backpack: 0.9, shoes: 0.3, jacket: 0.2}
        
        # Find k nearest neighbors (top 10 similar users)
        similar_users = []
        
        for other_user in users:
            if other_user.id == user.id:
                continue
            
            other_prefs = get_user_preferences(other_user.id)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(prefs, other_prefs)
            
            similar_users.append((other_user.id, similarity))
        
        # Sort and keep top 10
        similar_users = sorted(similar_users, 
                              key=lambda x: x[1], 
                              reverse=True)[:10]
        
        # Store for later use in recommendations
        store_similar_users(user.id, similar_users)
```

---

## 🔄 III. INTEGRATION POINTS

### 3.1 Frontend → Recommendation Service

```
USER ACTION: Views product page
│
├─ Frontend logs: trackProductView(productId)
│  └─ POST /api/recommendations/track
│     {
│       "user_id": "guest_uuid_or_customer_id",
│       "session_id": "session_abc123",
│       "product_id": "prod_jansport_superbreak",
│       "interaction_type": "view",
│       "metadata": {
│         "category": "backpack",
│         "price": 1299000,
│         "title": "JanSport Superbreak"
│       }
│     }
│
├─ Next.js API route proxies to Recommendation Service
│  └─ HTTP POST http://recommendation:8001/track
│
├─ Recommendation Service processes
│  └─ INSERT into rec_user_interactions
│  └─ UPDATE rec_user_preferences (learn preferences)
│
└─ Response: {"success": true, "interaction_id": "..."}

---

USER ACTION: Views homepage
│
├─ Frontend loads: <PersonalizedRecommendations />
│  └─ GET /api/recommendations?userId=XXX&limit=10
│
├─ Next.js API route proxies
│  └─ HTTP GET http://recommendation:8001/recommendations?userId=XXX&limit=10
│
├─ Recommendation Service executes
│  ├─ Check Redis cache (hit = <50ms)
│  ├─ Or compute hybrid score
│  │  ├─ Read rec_user_interactions (last 30 days)
│  │  ├─ Read rec_user_preferences
│  │  ├─ Query rec_product_similarities
│  │  ├─ Calculate: Score = 0.4×content + 0.6×collab
│  │  ├─ Sort products by score
│  │  └─ Cache result in Redis (1 hour TTL)
│  │
│  └─ Return: [{product_id, score, reason}, ...]
│
└─ Frontend displays products with score-based ordering
```

---

### 3.2 Frontend → Chatbot Service

```
USER ACTION: Types message in chat widget
│
├─ Frontend sends: ChatMessage (WebSocket)
│  └─ WS POST ws://localhost:8000/ws/chat
│     {
│       "message": "tìm balo màu đỏ",
│       "user_id": "user_123",
│       "session_id": "session_456"
│     }
│
├─ WebSocket connection to Chatbot Service
│
├─ Chatbot Pipeline processes (5 agents)
│  ├─ Agent 1: Clean text → "tìm balo màu đỏ"
│  ├─ Agent 2: Classify intent → PRODUCT.SEARCH
│  ├─ Agent 3: Validate → OK
│  ├─ Agent 4: Execute tool → search_products("balo đỏ")
│  │  └─ Query Medusa API: GET /store/products?q=balo
│  ├─ Agent 5: Generate response → Template + Product list
│  │
│  └─ Response:
│     {
│       "response": "Tìm thấy 3 sản phẩm cho 'balo đỏ'",
│       "products": [
│         {
│           "id": "prod_123",
│           "title": "JanSport Superbreak Red",
│           "price": 1299000,
│           "image": "url"
│         }
│       ],
│       "quick_replies": ["Xem chi tiết", "Thêm vào giỏ"],
│       "actions": ["show_products"]
│     }
│
└─ Frontend displays message + product cards in widget
```

---

### 3.3 Chatbot Service → Medusa Backend

```
TOOL CALL: search_products("balo")
│
├─ Chatbot Executor calls Medusa API
│  └─ GET http://medusa:9000/store/products?q=balo
│
├─ Medusa processes search
│  ├─ Query: SELECT * FROM product WHERE title LIKE '%balo%'
│  ├─ Apply filters, sorting
│  └─ Return: [{id, title, price, ...}, ...]
│
└─ Response: [prod_1, prod_2, prod_3]
   └─ Chatbot extracts key info → Response
      └─ Frontend displays with prices, images
```

---

## 🛡️ IV. ERROR HANDLING & RESILIENCE

### 4.1 Chatbot Error Handling

```
Failure Scenario 1: Medusa API Down
├─ Tool call: search_products() fails
├─ Retry logic: 3 retries with exponential backoff
├─ Backoff: 1s, 2s, 4s
├─ Still fails?
├─ Response fallback: "Hiện tại không thể tìm kiếm, vui lòng thử lại"
└─ Log error for debugging

Failure Scenario 2: Database timeout
├─ Query hangs (network issue)
├─ Timeout after 5s
├─ Retry with shorter timeout
├─ Still slow? Return cached results if available
└─ User sees old data but no broken experience

Failure Scenario 3: LLM API down (Qwen3)
├─ Fallback LLM needed
├─ Response fallback: Use default template
├─ No personalized response, but works
└─ Escalate to human if needed

Failure Scenario 4: Invalid user input
├─ Input validation at Agent 1
├─ Sanitize text: Remove special chars
├─ Max length: 500 chars
├─ If invalid: "Không hiểu yêu cầu, vui lòng thử lại"
└─ Don't pass to later agents
```

---

### 4.2 Recommendation Error Handling

```
Failure Scenario 1: Redis cache fails
├─ Fall back to direct database computation
├─ Slower (200-500ms vs <50ms) but works
└─ Monitor cache health

Failure Scenario 2: Product similarity not computed
├─ Use fallback algorithm (pure content-based)
├─ Similarity computation job might have failed
├─ Monitor batch job logs
└─ Trigger manual recompute

Failure Scenario 3: No user history (new user)
├─ Use trending products (most viewed)
├─ Or featured collection
├─ Switch to content-based as user interacts
└─ Handle cold start gracefully

Failure Scenario 4: Concurrent recommendation requests
├─ Rate limiting: 10 requests/second per user
├─ Queue excess requests
├─ Serve from cache if available
└─ Return previous recommendations if timeout
```

---

## 📈 V. PERFORMANCE OPTIMIZATION

### 5.1 Database Query Optimization

```sql
-- ❌ SLOW: Full table scan
SELECT * FROM rec_user_interactions 
WHERE user_id = 'user_123';
-- Cost: O(n) where n = total rows

-- ✅ FAST: Indexed query
CREATE INDEX idx_user_id ON rec_user_interactions(user_id);
CREATE INDEX idx_product_id ON rec_user_interactions(product_id);

SELECT * FROM rec_user_interactions 
WHERE user_id = 'user_123'
ORDER BY created_at DESC 
LIMIT 10;
-- Cost: O(log n) or O(1) with index

-- ✅ FASTER: Partition by date (for large tables)
CREATE TABLE rec_user_interactions_2025_12 
PARTITION OF rec_user_interactions 
FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');
-- Cost: O(1) for recent data
```

---

### 5.2 Algorithm Optimization

```python
# ❌ SLOW: Compute similarity for all product pairs
def compute_similarities_slow():
    products = get_all_products()  # 100+
    for i in range(len(products)):
        for j in range(i+1, len(products)):
            similarity = calculate(products[i], products[j])
            # Time: O(n²) ≈ 5000 computations!

# ✅ FAST: Only compute for candidate products
def compute_similarities_fast():
    products = get_all_products()
    for product in products:
        # Only find similar products (same category)
        candidates = get_products(category=product.category)
        # Time: O(n * m) where m << n

# ✅ FASTER: Pre-compute & cache
def compute_similarities_cached():
    # Step 1: Pre-compute nightly (off-peak)
    # Step 2: Cache in rec_product_similarities
    # Step 3: During day, just lookup
    # Time: O(1) for each recommendation
```

---

### 5.3 Frontend Performance

```
OPTIMIZATION: Lazy load recommendations

❌ Load all recommendations on page load
├─ Blocks page render
└─ User waits 1-2 seconds

✅ Use React Suspense + Server Components
├─ Initial load: Show skeleton
├─ Stream recommendations as ready
├─ User sees content immediately
└─ Recommendations fill in as data ready

✅ Intersection Observer (client-side)
├─ Only load recommendations when visible
├─ If below fold, load when scrolled to
└─ Reduces initial load time
```

---

## 🎯 VI. TESTING & MONITORING

### 6.1 Unit Testing Strategy

```
Chatbot:
├─ test_input_processor.py
│  ├─ Test text normalization
│  ├─ Test language detection
│  └─ Test spell check
├─ test_intent_classifier.py
│  ├─ Test keyword matching
│  ├─ Test decision tree
│  └─ Test entity extraction
├─ test_executor.py
│  ├─ Mock Medusa API
│  ├─ Test tool calls
│  └─ Test error handling
└─ test_response_generator.py
   ├─ Test template rendering
   ├─ Test LLM fallback
   └─ Test response structure

Recommendation:
├─ test_hybrid_algorithm.py
│  ├─ Test scoring formula
│  ├─ Test weight calculation
│  └─ Test ranking
├─ test_similarity.py
│  ├─ Test cosine similarity
│  ├─ Test category matching
│  └─ Test co-occurrence
└─ test_cache.py
   ├─ Test Redis operations
   ├─ Test TTL expiry
   └─ Test cache invalidation
```

### 6.2 Integration Testing

```bash
# Chatbot service
python -m pytest chatbot-service/tests/test_chat_pipeline.py

# Recommendation service
python -m pytest recommendation-service/tests/test_quick.py

# E2E tests
pytest tests/e2e/test_homepage_personalization.py
pytest tests/e2e/test_chatbot_workflow.py
```

### 6.3 Monitoring Metrics

```
Chatbot Metrics (track in database):
├─ Intent classification accuracy
├─ Tool execution success rate
├─ Response time distribution (p50, p95, p99)
├─ LLM fallback frequency
├─ Escalation rate
└─ User satisfaction (if survey)

Recommendation Metrics:
├─ Click-through rate (CTR)
├─ Conversion rate
├─ Cache hit rate
├─ Average recommendation latency
├─ Recommendation diversity
└─ Cold start handling effectiveness

System Metrics:
├─ API latency
├─ Error rates
├─ Database query times
├─ Cache efficiency
└─ Resource utilization (CPU, memory, disk)
```

---

## 🎓 VII. LEARNING & FUTURE IMPROVEMENTS

### 7.1 What This Project Demonstrates

✅ **Software Architecture:**
- Microservices design
- API design & integration
- Database normalization
- Caching strategies
- Error handling & resilience

✅ **AI/ML:**
- Multi-agent systems
- Intent classification
- Hybrid recommendation algorithms
- Collaborative filtering
- Cold start problem handling

✅ **DevOps:**
- Docker & containerization
- Docker Compose orchestration
- Service discovery
- Environment management
- Scaling considerations

✅ **Full-Stack Development:**
- Frontend (Next.js, React)
- Backend (Node.js, Python)
- Database (PostgreSQL)
- Caching (Redis)
- Real-time (WebSocket)

---

### 7.2 Key Learnings

1. **Don't use LLM for everything**
   - Rule-based NLP can handle 90% of cases
   - LLM should be fallback, not default
   - Save money by being smart about when to use LLM

2. **Hybrid approaches beat single methods**
   - Hybrid recommendation > pure content or collaborative
   - Multi-agent > monolithic system
   - Combine rule-based + ML for robustness

3. **Caching is critical**
   - Cache hit rate 80%+ makes huge difference
   - Redis is simple and effective
   - Know your cache invalidation strategy

4. **User experience matters**
   - 200ms response time feels fast
   - 1000ms+ feels slow
   - Optimize for p95 latency, not just average

5. **Monitoring is essential**
   - Track metrics from day 1
   - Know your bottlenecks
   - Data-driven optimization

---

## 📚 VIII. REFERENCES & RESOURCES

### 8.1 Architecture References

- [System Design Interview Book](https://www.educative.io/courses/grokking-the-system-design-interview)
- [Recommendation System Design](https://developers.google.com/machine-learning/recommendation)
- [Building Microservices](https://microservices.io/)

### 8.2 Technology Documentation

- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Next.js](https://nextjs.org/docs) - React framework
- [Medusa](https://docs.medusajs.com/) - E-commerce platform
- [PostgreSQL](https://www.postgresql.org/docs/) - Database
- [Redis](https://redis.io/documentation) - Cache
- [scikit-learn](https://scikit-learn.org/stable/) - ML library

### 8.3 Papers & Articles

- [Collaborative Filtering](https://en.wikipedia.org/wiki/Collaborative_filtering)
- [Content-Based Filtering](https://en.wikipedia.org/wiki/Content-based_filtering)
- [Hybrid Recommender Systems](https://en.wikipedia.org/wiki/Recommender_system#Hybrid_recommender_systems)

---

**Document Version:** v1.0  
**Last Updated:** December 15, 2025  
**Status:** Production-Ready ✅
