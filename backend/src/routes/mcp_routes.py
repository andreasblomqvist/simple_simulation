from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp", tags=["mcp"])

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    success: bool

@router.post("/chat", response_model=ChatResponse)
async def chat_with_mcp(request: ChatRequest):
    """
    Handle chat requests with the MCP server
    """
    try:
        # TODO: Integrate with your MCP server
        # For now, return a mock response
        
        user_message = request.message.lower()
        context = request.context or {}
        
        # Basic response logic based on message content
        if any(keyword in user_message for keyword in ["kpi", "performance", "metrics"]):
            if context.get("hasSimulationData"):
                response = f"I can see you have simulation data for {context.get('totalOffices', 0)} offices over {context.get('periods', 0)} periods. What specific KPIs would you like me to analyze?"
            else:
                response = "I can help you understand KPIs and performance metrics. Try running a simulation first to get detailed insights."
        
        elif any(keyword in user_message for keyword in ["journey", "career", "level"]):
            response = "I can help analyze career journey distributions and progression patterns. The Journey classification represents career stages: Journey 1 (junior), Journey 2-3 (mid-senior), and Journey 4 (leadership)."
        
        elif any(keyword in user_message for keyword in ["growth", "headcount", "recruitment"]):
            response = "I can analyze growth patterns, headcount changes, and recruitment metrics. Would you like me to explain the growth trends in your simulation results?"
        
        elif any(keyword in user_message for keyword in ["financial", "revenue", "cost", "ebitda"]):
            response = "I can help analyze financial metrics including net sales, EBITDA, margins, and cost structures. What specific financial aspects would you like to explore?"
        
        elif any(keyword in user_message for keyword in ["help", "what can you do"]):
            response = """I'm your SimpleSim assistant! I can help you with:

🎯 **KPI Analysis** - Explain performance metrics and trends
📊 **Journey Distribution** - Analyze career progression patterns  
📈 **Growth Insights** - Understand headcount and recruitment trends
💰 **Financial Metrics** - Break down revenue, costs, and margins
🏢 **Office Comparisons** - Compare performance across locations
⚡ **Simulation Tips** - Optimize your simulation parameters

Just ask me about any aspect of your simulation results!"""
        
        else:
            response = "I'm here to help you understand your SimpleSim results! Ask me about KPIs, growth patterns, financial metrics, or career journeys. What would you like to explore?"
        
        return ChatResponse(response=response, success=True)
        
    except Exception as e:
        logger.error(f"Error in MCP chat: {str(e)}")
        return ChatResponse(
            response="I apologize, but I encountered an error processing your request. Please try again.",
            success=False
        )

@router.get("/health")
async def mcp_health():
    """Health check for MCP integration"""
    return {"status": "ok", "mcp_connected": False}  # TODO: Check actual MCP connection 