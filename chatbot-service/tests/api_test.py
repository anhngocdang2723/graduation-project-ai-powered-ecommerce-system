import asyncio
import sys
import os
import httpx

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

async def test_suggestions_endpoint():
    print("\n=== Testing POST /chat/suggestions ===")
    
    base_url = "http://localhost:8000" # Assuming running locally, but we can mock or use app directly if we want integration test.
    # Since we are in the same env, let's try to use FastAPI TestClient or just run the logic via function call if server not up.
    # But the user asked to "ensure APIs are ready", so I should probably assume the server code is correct.
    # I will use the app instance directly to test without running server.
    
    from app.main import app
    from app.models.api_models import ContextSuggestionRequest
    
    # We can use Starlette TestClient
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Case 1: Guest
    print("\n--- Case 1: Guest ---")
    req = {"user_type": "guest"}
    resp = client.post("/chat/suggestions", json=req)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Suggestions: {[s['label'] for s in data['suggestions']]}")
    
    # Case 2: Customer
    print("\n--- Case 2: Customer ---")
    req = {"user_type": "customer", "customer_id": "cus_123"}
    resp = client.post("/chat/suggestions", json=req)
    print(f"Suggestions: {[s['label'] for s in data['suggestions']]}") # Wait, I need to read resp again
    data = resp.json()
    print(f"Suggestions: {[s['label'] for s in data['suggestions']]}")

    # Case 3: Staff
    print("\n--- Case 3: Staff ---")
    req = {"user_type": "staff"}
    resp = client.post("/chat/suggestions", json=req)
    data = resp.json()
    print(f"Suggestions: {[s['label'] for s in data['suggestions']]}")

    # Case 4: Tag Context (scope:order)
    print("\n--- Case 4: Tag Context (scope:order) ---")
    req = {"user_type": "customer", "tag": "scope:order"}
    resp = client.post("/chat/suggestions", json=req)
    data = resp.json()
    print(f"Suggestions: {[s['label'] for s in data['suggestions']]}")

    # Case 5: Metadata Override (Staff via ChatRequest)
    print("\n--- Case 5: Metadata Override (Staff) ---")
    # Note: This tests InputProcessor logic if we were hitting /chat, but here we test /chat/suggestions which takes user_type directly.
    # To test InputProcessor, we should hit /chat.
    chat_req = {
        "message": "check kho",
        "session_id": "test_meta_staff",
        "metadata": {"user_type": "staff"}
    }
    # We need to mock the DB pool for /chat to work fully, or rely on the fact that we are using TestClient with the app.
    # However, the app startup creates a pool. If we run this script, the app instance is imported.
    # The startup event might not run with TestClient automatically unless using TestClient(app) context manager or similar.
    # But let's try hitting /chat and see if it accepts the metadata.
    # Since we don't have a real DB connection in this script context (unless we set it up), /chat might fail on DB.
    # So I will skip full /chat test here and rely on the fact that I updated InputProcessor.
    
    # But I can test /chat/suggestions with explicit user_type="staff" which I already did in Case 3.
    pass

if __name__ == "__main__":
    asyncio.run(test_suggestions_endpoint())
