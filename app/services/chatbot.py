import os
import httpx
from bs4 import BeautifulSoup
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv

# ✅ Switched from Google to Groq
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.core.prompts import CHATBOT_ROLE
from app.schemas.chat import ChatMessage

load_dotenv()

# --- TOOL DEFINITION ---
@tool
def fetch_website_content(url: str) -> str:
    """
    Mandatory tool for searching any provided URL. 
    Use this to get real-time data from a website to answer user questions.
    """
    print(f"🔍 [AGENT LOG] Scraping: {url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        with httpx.Client(follow_redirects=True, headers=headers, timeout=15.0) as client:
            response = client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove non-content elements
            for s in soup(["script", "style", "nav", "footer", "aside", "header"]): 
                s.decompose()
            
            # ✅ Preserve form metadata for action-oriented parsing
            for form in soup.find_all("form"):
                if form.get("action"):
                    form.insert(0, f"[FORM_META: action='{form['action']}', method='{form.get('method', 'post').upper()}'] ")
                for input_field in form.find_all(["input", "textarea", "select"]):
                    if input_field.get("name"):
                        required = "required" if input_field.get("required") else "optional"
                        field_type = input_field.get("type", "text")
                        form.append(f" [FIELD: {input_field['name']}|type:{field_type}|{required}] ")
            
            text = " ".join(soup.get_text().split())
            if not text:
                return f"Error: Content at {url} appears empty or blocked by a bot-shield."
            
            return text[:10000]  # Slightly larger context for form-heavy pages
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code} while accessing {url}."
    except Exception as e:
        return f"Error: Could not access {url}. {str(e)}"

# --- STATE MANAGEMENT ---
class AgentState(TypedDict):
    # LangGraph handles the merging of messages automatically
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]

class AgenticService:
    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise RuntimeError(
                "Missing GROQ_API_KEY environment variable. Set it in Railway/Vercel project settings."
            )

        # ✅ Updated to Groq API (OpenAI-compatible routing)
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile", # Fast & reliable Groq model
            groq_api_key=groq_api_key,
            temperature=0.0,
        ).bind_tools([fetch_website_content])

        # Graph Construction
        builder = StateGraph(AgentState)
        builder.add_node("agent", self.call_model)
        builder.add_node("tools", ToolNode([fetch_website_content]))
        
        builder.set_entry_point("agent")
        builder.add_conditional_edges(
            "agent", 
            self.should_continue, 
            {"continue": "tools", "end": END}
        )
        builder.add_edge("tools", "agent")
        
        self.graph = builder.compile()

    def should_continue(self, state: AgentState):
        last_message = state["messages"][-1]
        # ✅ Safer check for tool calls across LangChain versions
        tool_calls = getattr(last_message, "tool_calls", None)
        return "continue" if tool_calls else "end"

    async def call_model(self, state: AgentState):
        # Prepend SystemMessage to the current state messages
        # Groq/OpenAI-compatible models handle SystemMessage natively (removed Gemini flag)
        full_history = [SystemMessage(content=CHATBOT_ROLE)] + state["messages"]
        response = await self.llm.ainvoke(full_history)
        return {"messages": [response]}

    async def get_response(self, user_input: str, history: List[ChatMessage]) -> str:
        # Convert API history to LangChain format
        lc_history = []
        for m in history:
            if m.role == "user":
                lc_history.append(HumanMessage(content=m.content))
            else:
                lc_history.append(AIMessage(content=m.content))
        
        # Build initial input
        inputs = {"messages": lc_history + [HumanMessage(content=user_input)]}
        
        try:
            print("🤖 [AGENT LOG] Initiating reasoning loop...")
            result = await self.graph.ainvoke(inputs)
            
            # --- ROBUST STRING EXTRACTION ---
            final_msg = result["messages"][-1]
            content = final_msg.content
            
            if isinstance(content, list):
                extracted_text = ""
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        extracted_text += part.get("text", "")
                    elif isinstance(part, str):
                        extracted_text += part
                return extracted_text.strip()
            
            return str(content).strip()

        except Exception as e:
            print(f"❌ [AGENT CRITICAL ERROR] {str(e)}")
            return f"I ran into a technical hurdle while processing that. Error: {str(e)}"