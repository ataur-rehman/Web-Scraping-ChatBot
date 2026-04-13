# app/api/routes.py
from typing import Optional

from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chatbot import AgenticService

router = APIRouter()

# Lazily initialize service to avoid app startup failures when env vars are missing.
_agent_service: Optional[AgenticService] = None


def get_agent_service() -> AgenticService:
    global _agent_service
    if _agent_service is None:
        _agent_service = AgenticService()
    return _agent_service

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        agent_service = get_agent_service()

        reply = await agent_service.get_response(
            user_input=request.message,
            history=request.history,
            context_url=request.url,
        )
        
        # Debugging: See what is actually being sent to Pydantic
        print(f"✅ [SUCCESS] Sending reply to frontend: {type(reply)}")
        
        return ChatResponse(answer=reply)
    except Exception as e:
        # Detailed logging to catch the "missing context" or "hallucination"
        print(f"❌ [ROUTE ERROR] Type: {type(e).__name__} | Details: {str(e)}")
        raise HTTPException(status_code=500, detail="Agent processing failed.")