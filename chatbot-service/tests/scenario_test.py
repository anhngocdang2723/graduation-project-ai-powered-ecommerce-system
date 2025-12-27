import asyncio
import sys
import os

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.agents.input_processor import InputProcessor
from app.agents.intent_classifier import IntentClassifier
from app.agents.orchestrator import Orchestrator
from app.agents.executor import Executor
from app.agents.response_generator import ResponseGenerator
from app.models.api_models import ChatRequest
from app.models.agent_types import ProcessedInput, IntentResult, ActionPlan

async def test_context_suggestions():
    print("\n=== Testing Context Suggestions ===")
    response_generator = ResponseGenerator()
    
    # Case 1: Guest
    print("\n--- Case 1: Guest ---")
    processed = ProcessedInput(
        session_id="guest_sess",
        text="hi",
        cleaned_text="hi",
        user_type="guest"
    )
    intent = IntentResult(intent="greeting")
    plan = ActionPlan()
    
    resp = await response_generator.run(processed, intent, plan)
    print(f"Guest Suggestions: {[qr.label for qr in resp.quick_replies]}")
    
    # Case 2: Customer
    print("\n--- Case 2: Customer ---")
    processed.user_type = "customer"
    processed.customer_id = "cus_123"
    resp = await response_generator.run(processed, intent, plan)
    print(f"Customer Suggestions: {[qr.label for qr in resp.quick_replies]}")
    
    # Case 3: Staff
    print("\n--- Case 3: Staff ---")
    processed.user_type = "staff"
    resp = await response_generator.run(processed, intent, plan)
    print(f"Staff Suggestions: {[qr.label for qr in resp.quick_replies]}")

    # Case 4: Tag Context (e.g. scope:order)
    print("\n--- Case 4: Tag Context (scope:order) ---")
    processed.user_type = "customer"
    processed.tag = "scope:order"
    resp = await response_generator.run(processed, intent, plan)
    print(f"Order Context Suggestions: {[qr.label for qr in resp.quick_replies]}")

    # Case 5: Intent Mapping (Guest Create Order -> Auth)
    print("\n--- Case 5: Intent Mapping (Guest Create Order) ---")
    processed.user_type = "guest"
    processed.tag = None
    intent.intent = "create_order"
    resp = await response_generator.run(processed, intent, plan)
    print(f"Guest Create Order Suggestions: {[qr.label for qr in resp.quick_replies]}")

async def run_scenario(name, inputs, tags=None, user_type="customer"):
    print(f"\n=== Running Scenario: {name} ===")
    
    # Initialize pipeline
    input_processor = InputProcessor()
    intent_classifier = IntentClassifier()
    orchestrator = Orchestrator()
    executor = Executor()
    response_generator = ResponseGenerator()

    session_id = "test_session"
    customer_id = "test_customer"

    for i, text in enumerate(inputs):
        tag = tags[i] if tags else None
        print(f"\n👤 User ({user_type}): {text} [Tag: {tag}]")
        
        # 1. Input Processing
        req = ChatRequest(
            session_id=session_id,
            customer_id=customer_id,
            message=text,
            tag=tag
        )
        processed = await input_processor.run(req, None)
        # Override user_type for testing
        processed.user_type = user_type
        
        # 2. Intent Classification
        intent = await intent_classifier.run(processed)
        print(f"   Intent (Global): {intent.intent} (Conf: {intent.confidence})")

        # 3. Orchestration
        plan, _ = await orchestrator.run(processed, intent)
        print(f"   Plan: {plan.tools} | Next Step: {plan.next_step}")

        # 4. Execution
        tool_res = await executor.run(processed, intent, plan)
        if tool_res:
            print(f"   Tool Result: OK={tool_res.ok}, Data={str(tool_res.data)[:100]}...")
        else:
            print("   Tool Result: None")

        # 5. Response Generation
        response = await response_generator.run(processed, intent, plan, tool_res)
        print(f"🤖 Bot: {response.response}")

async def main():
    await test_context_suggestions()

    # 1. Implicit Routing (No Tag)
    await run_scenario("Implicit Routing (Global NLU)", ["tìm áo thun"])
    
    # 2. Scoped Routing (Tag: scope:staff)
    await run_scenario("Scoped Routing (Staff Scope)", ["tìm khách Nguyen"], tags=["scope:staff"], user_type="staff")
    
    # 3. Executable Tag (Direct Action)
    await run_scenario("Executable Tag (Direct Action)", ["blabla"], tags=["action:view_cart"])

    # 4. Permission Denial (Customer tries Staff command)
    await run_scenario("Permission Denial", ["check kho Shorts"], tags=["scope:staff"], user_type="customer")

    # 5. Noise Handling
    await run_scenario("Noise Handling", ["Xin chào, hôm nay trời đẹp quá, tôi muốn tìm mua áo thun màu đỏ cho bạn gái"])

    # 6. Missing Entity
    await run_scenario("Missing Entity", ["check kho"], tags=["scope:staff"], user_type="staff")

    # 7. Invalid Tag
    await run_scenario("Invalid Tag", ["tìm áo thun"], tags=["scope:unknown"])

if __name__ == "__main__":
    asyncio.run(main())
