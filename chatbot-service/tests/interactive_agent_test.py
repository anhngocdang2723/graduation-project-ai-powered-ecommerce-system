import asyncio
import os
import sys
import uuid
import json
from typing import Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.agent_types import ProcessedInput, SessionContext
from app.agents.input_processor import InputProcessor
from app.agents.intent_classifier import IntentClassifier
from app.agents.orchestrator import Orchestrator
from app.agents.executor import Executor
from app.agents.response_generator import ResponseGenerator

from app.models.api_models import ChatRequest

def print_step(name: str, data: Any):
    print(f"\n🔹 [{name}]")
    if hasattr(data, "model_dump_json"):
        print(data.model_dump_json(indent=2))
    elif hasattr(data, "dict"):
        print(json.dumps(data.dict(), indent=2, default=str))
    else:
        print(data)

async def run_interactive_test():
    print("🤖 Chatbot Agent Interactive Test Mode")
    print("Type 'exit' or 'quit' to stop.\n")

    session_id = str(uuid.uuid4())
    customer_id = "test_customer"
    # We keep a local session context to persist cart_id across turns
    local_cart_id = None

    print(f"Session ID: {session_id}")
    print(f"Customer ID: {customer_id}")

    while True:
        try:
            user_input = input("\n👤 You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            if not user_input.strip():
                continue

            print("\n--- 🔄 Processing Pipeline ---")

            # 1. Input Processor
            req = ChatRequest(
                message=user_input,
                session_id=session_id,
                customer_id=customer_id,
                language="vi"
            )
            
            processor = InputProcessor()
            # Pass pool=None to skip DB fetch
            processed = await processor.run(req, pool=None)
            
            # Inject local cart_id
            if local_cart_id:
                processed.session_ctx.cart_id = local_cart_id
                
            print_step("1. Input Processor", processed)

            # 2. Intent Classifier
            classifier = IntentClassifier()
            intent_res = await classifier.run(processed)
            print_step("2. Intent Classifier", intent_res)

            # 3. Orchestrator
            orchestrator = Orchestrator()
            plan, _ = await orchestrator.run(processed, intent_res)
            print_step("3. Orchestrator (Plan)", plan)

            # 4. Executor
            executor = Executor()
            tool_res = await executor.run(processed, intent_res, plan)
            if tool_res:
                print_step("4. Executor (Tool Result)", tool_res)
                
                # Update session context if cart was created/found
                if tool_res.ok and tool_res.data and isinstance(tool_res.data, dict):
                    # Check if it's a cart object (has 'items', 'region_id', etc.)
                    # Medusa cart object usually has 'id', 'items', etc.
                    if "id" in tool_res.data and "items" in tool_res.data:
                         new_cart_id = tool_res.data.get("id")
                         if new_cart_id and local_cart_id != new_cart_id:
                             print(f"   👉 Updating Session Cart ID: {new_cart_id}")
                             local_cart_id = new_cart_id
                             processed.session_ctx.cart_id = local_cart_id
            else:
                print("\n🔹 [4. Executor] No tools executed.")

            # 5. Response Generator
            generator = ResponseGenerator()
            agent_response = await generator.run(
                processed, intent_res, plan, tool_res
            )
            print_step("5. Response Generator", agent_response)

            print(f"\n🤖 Bot: {agent_response.response}")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Set env vars for testing if needed
    # os.environ["MEDUSA_BACKEND_URL"] = "http://localhost:9000" 
    asyncio.run(run_interactive_test())
