import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq

load_dotenv(dotenv_path="D:/llm/.env")

model = ChatGroq(
    model="llama-3.3-8b-instant",  
    temperature=0
)

def search_web(query: str) -> str:
    """Search the web for relevant information."""
    return f"[WEB RESULT] Searching for: {query}"

def send_mail(content: str) -> str:
    """Send an email with the given content."""
    return f"[EMAIL SENT] Content: {content}"

tools = [search_web, send_mail]

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="""
You are a smart coding assistant.

Behaviors:
- If user gives code → do code review
- If user asks question → answer clearly
- If task unclear → ask clarification
"""
)

def parse_input(user_text: str) -> dict:
    """
    Convert raw user input into structured JSON
    """

    # simple detection logic
    if "def " in user_text or "import " in user_text:
        return {
            "task": "code_review",
            "language": "python",
            "code": user_text
        }

    return {
        "task": "general",
        "content": user_text
    }

def build_prompt(data: dict) -> str:
    """
    Convert structured JSON into final prompt
    """

    if data["task"] == "code_review":
        return f"""
You are a senior Python code reviewer.

Analyze the following code:

{data['code']}

Provide:
1. Issues
2. Improvements
3. Optimized version
"""

    return data["content"]

while True:
    user_input = input("\nEnter your input (or type 'exit'): \n")
    if user_input.lower() == "exit":
        break
    structured_data = parse_input(user_input)
    prompt = build_prompt(structured_data)
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })
    print("\n=== FINAL OUTPUT ===\n")
    print(result["messages"][-1].content)