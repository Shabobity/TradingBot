"""Agent loops for Claude (Anthropic) and Groq LLMs."""

import json
from typing import List, Dict
import anthropic
from groq import Groq
from executor import execute_tool
from config import ANTHROPIC_API_KEY, GROQ_API_KEY, USE_GROQ
from tools import CLAUDE_TOOLS


SYSTEM_PROMPT = """You are an expert AI stock market analyst with deep knowledge of technical, 
fundamental, and sentiment analysis. You have access to real-time market data tools.

Your approach:
- Direct and confident — give clear recommendations
- Data-driven — always use tools before answering about specific stocks
- Explain your reasoning — don't just give a number
- Use market knowledge — connect the dots across all analyses

Rules:
- ALWAYS call analyze_stock before giving opinions on specific tickers
- ALWAYS call compare_stocks when comparing multiple stocks
- For portfolio questions, ALWAYS call build_portfolio
- Check market regime if unsure about conditions
- Be honest about conflicting signals
- Remind users: This is educational, NOT financial advice

When presenting results:
- Lead with the key finding (probability and direction)
- Explain the top 2-3 drivers
- Mention any risks or conflicts
- Describe trade setup if available"""


def run_agent(user_message: str, conversation_history: List[Dict]) -> str:
    """Run the agent with automatic Groq/Anthropic selection."""
    if USE_GROQ:
        return _run_agent_groq(user_message, conversation_history)
    else:
        return _run_agent_anthropic(user_message, conversation_history)


def _run_agent_groq(user_message: str, conversation_history: List[Dict]) -> str:
    """Groq agent loop using Llama 3.3 70B."""
    if not GROQ_API_KEY:
        return "ERROR: GROQ_API_KEY not set in .env"
    
    client = Groq(api_key=GROQ_API_KEY)
    
    # Convert to Groq/OpenAI format
    groq_tools = [{
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"],
        }
    } for t in CLAUDE_TOOLS]
    
    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + conversation_history
        + [{"role": "user", "content": user_message}]
    )
    
    # Agent loop
    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=groq_tools,
            tool_choice="auto",
            max_tokens=4096,
            temperature=0.3,
        )
        
        msg = response.choices[0].message
        
        # No tool calls — done
        if not msg.tool_calls:
            return msg.content or ""
        
        # Append assistant message
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                } for tc in msg.tool_calls
            ]
        })
        
        # Execute tools
        for tc in msg.tool_calls:
            tool_name = tc.function.name
            try:
                tool_input = json.loads(tc.function.arguments)
            except:
                tool_input = {}
            
            print(f"\n[agent] Calling: {tool_name}({json.dumps(tool_input)})")
            result = execute_tool(tool_name, tool_input)
            
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": tool_name,
                "content": result,
            })


def _run_agent_anthropic(user_message: str, conversation_history: List[Dict]) -> str:
    """Anthropic/Claude agent loop."""
    if not ANTHROPIC_API_KEY:
        return "ERROR: No API key set"
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    messages = conversation_history + [{"role": "user", "content": user_message}]
    
    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=CLAUDE_TOOLS,
            messages=messages,
        )
        
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n[agent] Calling: {block.name}({json.dumps(block.input)})")
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            
            messages.append({"role": "user", "content": tool_results})
        else:
            return "".join(b.text for b in response.content if hasattr(b, "text"))
