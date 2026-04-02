import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# LLM
from langchain_groq import ChatGroq

# Core
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

# Memory
from langchain_community.chat_message_histories import ChatMessageHistory


# -----------------------------
# 🔐 LOAD ENV
# -----------------------------
load_dotenv("D:/llm/.env")

# -----------------------------
# 🤖 LLM
# -----------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# -----------------------------
# 🧠 MEMORY
# -----------------------------
history = ChatMessageHistory()

# -----------------------------
# 🛠 TOOL
# -----------------------------
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """
    Search dermatology-related information.
    Use ONLY short, specific queries (max 10 words).
    """
    query = query[:100]  # hard limit safety

    return f"[WEB RESULT] Dermatology info about: {query}"

tools = [search_web]

# Bind tools to LLM (IMPORTANT)
llm_with_tools = llm.bind_tools(tools)

# -----------------------------
# 📊 STRUCTURED OUTPUT
# -----------------------------
class DermatologyReport(BaseModel):
    patient_summary: str
    key_observations: str
    possible_conditions: str
    recommended_actions: str
    lifestyle_plan: str
    follow_up: str
    explanation: str

parser = PydanticOutputParser(pydantic_object=DermatologyReport)

# -----------------------------
# 🧾 PROMPT
# -----------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a Dermatologist AI.

RULES:
- Do NOT overuse tools
- Use tools ONLY if absolutely necessary
- Tool query must be SHORT (max 5–10 words)
- DO NOT repeat phrases

If enough information is available → DO NOT call tools.

Final answer must be JSON only.
"""),
    ("human", "{input}")
])

chain = prompt | llm_with_tools


# -----------------------------
# 🚀 MAIN LOOP
# -----------------------------
print("🧑‍⚕️ Modern LangChain Agent Started\n")

while True:
    user_input = input("\nEnter input (or exit): ")

    if user_input.lower() == "exit":
        break

    history.add_user_message(user_input)

    # Build conversation
    messages = []
    for msg in history.messages:
        if msg.type == "human":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))

    # Invoke model
    response = chain.invoke({"input": user_input})

    # Handle tool calls
    response = chain.invoke({"input": user_input})

    if hasattr(response, "tool_calls") and response.tool_calls:
        for tool_call in response.tool_calls:
            query = tool_call["args"].get("query", "")

            # 🚨 Guard: prevent long queries
            if len(query.split()) > 10:
                print("\n⚠️ Tool blocked: query too long\n")
                continue

            result = search_web.invoke({"query": query})

            print("\n🔎 TOOL USED:\n", result)
            history.add_ai_message(result)
            continue

    output = response.content

    print("\n=== RESPONSE ===\n")
    print(output)

    history.add_ai_message(output)

    # -----------------------------
    # 🧪 STRUCTURED OUTPUT
    # -----------------------------
    try:
        structured = parser.parse(output)

        print("\n✅ STRUCTURED OUTPUT:\n")
        print(structured.model_dump())

    except Exception:
        print("\n⚠️ Not structured output yet")