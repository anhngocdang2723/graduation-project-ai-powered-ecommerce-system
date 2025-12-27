import asyncio
import sys
import os
from typing import Dict, List, Optional

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.agents.intent_classifier import VI_KEYWORDS, _match_score, IntentClassifier
from app.models.agent_types import ProcessedInput, IntentResult, SessionContext

class ScopedIntentClassifier(IntentClassifier):
    async def run(self, processed: ProcessedInput, scope: Optional[str] = None) -> IntentResult:
        text = processed.cleaned_text
        
        # 1. Define Scope Mappings (Scope -> Allowed Intent Prefixes)
        scope_map = {
            "product": ["PRODUCT", "CART"],
            "order": ["ORDER"],
            "staff": ["STAFF"],
            "manager": ["MANAGER"]
        }
        
        allowed_prefixes = scope_map.get(scope, []) if scope else []
        
        # 2. Compute scores with Scope Bias
        scores: Dict[str, int] = {}
        for key, phrases in VI_KEYWORDS.items():
            base_score = _match_score(text, phrases)
            
            # Apply Scope Logic
            if scope:
                # If key matches scope, boost score significantly
                if any(key.startswith(prefix) for prefix in allowed_prefixes):
                    # Boost score to ensure it wins if there's any match
                    # Or even if match is weak, we prioritize it.
                    # Here we just multiply score if it matches, or penalize others.
                    if base_score > 0:
                        scores[key] = base_score * 10 
                    else:
                        # Even if no keyword match, if we are in a strict scope, 
                        # we might want to default to a generic intent within that scope?
                        # For now, let's just rely on keyword matching but boosted.
                        scores[key] = 0
                else:
                    # Penalize out-of-scope intents
                    scores[key] = 0
            else:
                scores[key] = base_score

        # 3. Decide top intent
        if not scores:
            top_key = "UNKNOWN"
            top_score = 0
        else:
            top_key = max(scores.items(), key=lambda kv: kv[1])[0]
            top_score = scores.get(top_key, 0)

        print(f"   [Scope: {scope or 'None'}] Input: '{text}' -> Top Key: {top_key} (Score: {top_score})")
        
        # Map to system intents (simplified for test)
        intent_map = {
            "GREETING": "general",
            "PRODUCT.SEARCH": "product_inquiry",
            "ORDER.TRACK": "order_tracking",
            "CART.VIEW": "cart_view",
            "CART.ADD": "cart_add",
            "STAFF.CHECK_STOCK": "staff_check_stock",
            "STAFF.CUSTOMER_LOOKUP": "staff_customer_lookup",
            "MANAGER.REPORT_SALES": "manager_report_sales",
        }
        
        return IntentResult(
            intent=intent_map.get(top_key, "general"),
            confidence=1.0 if top_score > 0 else 0.0,
            entities={}
        )

async def run_test():
    classifier = ScopedIntentClassifier()
    
    # Test Case: Ambiguous input "kiểm tra"
    # "kiểm tra" is in ORDER.TRACK ("kiểm tra") and STAFF.CHECK_STOCK ("kiểm kho" - close, but maybe not exact match in current keywords)
    # Let's use "tìm" which is in PRODUCT.SEARCH ("tìm") and STAFF.CUSTOMER_LOOKUP ("tìm khách")
    
    input_text = "tìm kiếm"
    
    print(f"\n--- Testing Input: '{input_text}' ---")
    
    # 1. No Scope
    ctx = SessionContext()
    p1 = ProcessedInput(text=input_text, cleaned_text=input_text, session_id="1", customer_id="1", language="vi", user_type="customer", session_ctx=ctx)
    await classifier.run(p1, scope=None)
    
    # 2. Scope: Product
    await classifier.run(p1, scope="product")
    
    # 3. Scope: Staff
    # Note: "tìm kiếm" matches PRODUCT.SEARCH. 
    # STAFF.CUSTOMER_LOOKUP has "tìm khách". "tìm kiếm" might not match "tìm khách" directly with simple substring check if not exact.
    # Let's check _match_score logic: " {p} " in " {text} ".
    # "tìm kiếm" contains "tìm" (PRODUCT.SEARCH).
    # "tìm khách" is not in "tìm kiếm".
    # So for Staff scope, if we input "tìm khách", it works.
    
    input_text_2 = "kiểm tra"
    print(f"\n--- Testing Input: '{input_text_2}' ---")
    # ORDER.TRACK has "kiểm tra".
    # STAFF.CHECK_STOCK has "kiểm kho".
    
    p2 = ProcessedInput(text=input_text_2, cleaned_text=input_text_2, session_id="1", customer_id="1", language="vi", user_type="customer", session_ctx=ctx)
    await classifier.run(p2, scope=None) # Should be ORDER.TRACK
    await classifier.run(p2, scope="order") # Should be ORDER.TRACK
    await classifier.run(p2, scope="staff") # Should be UNKNOWN or STAFF if we add "kiểm tra" to staff keywords?
    
    # Let's try to add a collision to demonstrate the value.
    # Suppose we add "kiểm tra" to STAFF.CHECK_STOCK in the test class for demonstration.
    VI_KEYWORDS["STAFF.CHECK_STOCK"].append("kiểm tra")
    
    print(f"\n--- Testing Input: '{input_text_2}' (After adding 'kiểm tra' to Staff keywords) ---")
    await classifier.run(p2, scope=None) # Ambiguous, might pick first or max score
    await classifier.run(p2, scope="order") # Should pick ORDER
    await classifier.run(p2, scope="staff") # Should pick STAFF

if __name__ == "__main__":
    asyncio.run(run_test())
