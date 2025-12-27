import time
from typing import Any, Dict, Optional

from app.tools.base import BaseTool
from app.models.agent_types import ToolResults

class CustomerLookupTool(BaseTool):
    async def run(self, query: str) -> ToolResults:
        start_time = time.time()
        try:
            # Mock implementation - would query Medusa Admin API /admin/customers
            data = [
                {"id": "cust_1", "email": "test@example.com", "first_name": "Nguyen", "last_name": "Van A", "phone": "0901234567"},
                {"id": "cust_2", "email": "customer2@example.com", "first_name": "Le", "last_name": "Thi B", "phone": "0909876543"}
            ]
            # Simple filter
            q = query.lower()
            results = [
                c for c in data 
                if q in c['email'].lower() 
                or q in c['phone']
                or q in c['first_name'].lower()
                or q in c['last_name'].lower()
            ]
            
            duration = int((time.time() - start_time) * 1000)
            return ToolResults(
                ok=True, 
                data=results, 
                errors=[], 
                timings_ms={"lookup_customer": duration}
            )
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            return ToolResults(
                ok=False, 
                data=None, 
                errors=[str(e)], 
                timings_ms={"lookup_customer": duration}
            )

async def lookup_customer(query: str) -> ToolResults:
    tool = CustomerLookupTool()
    return await tool.run(query=query)
