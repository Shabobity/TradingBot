"""Interactive conversational chat interface."""

from typing import List, Dict
import textwrap
from agent_loop import run_agent
from config import USE_GROQ


def chat():
    """Run the interactive chat interface."""
    model_label = "Groq Llama 3.3 70B (free)" if USE_GROQ else "Anthropic Claude"
    
    print()
    print("=" * 60)
    print("AI Stock Analysis Agent")
    print(f"Model: {model_label}")
    print("=" * 60)
    print("Ask me anything about stocks, portfolios, or market conditions.")
    print("Type 'exit' to quit | Type 'scan' for a quick watchlist scan")
    print("=" * 60)
    print()
    
    history: List[Dict] = []
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ("exit", "quit", "q"):
            print("Goodbye.")
            break
        
        if user_input.lower() == "scan":
            from main import quick_scan
            quick_scan()
            continue
        
        print("\nAgent: ", end="", flush=True)
        
        response = run_agent(user_input, history)
        
        # Print with wrapping
        for line in response.split("\n"):
            wrapped = textwrap.wrap(line, width=72) if line.strip() else [""]
            for wl in wrapped:
                print(f"{wl}")
        
        print()
        
        # Update history
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})
        
        # Bound history to avoid token overflow
        if len(history) > 40:
            history = history[-40:]
