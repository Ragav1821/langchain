import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

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
# 🛠 TOOL (WEB SEARCH SIMULATION)
# -----------------------------
def search_web(query: str):
    return f"[WEB RESULT] Dermatology info about: {query}"

# -----------------------------
# 📊 STRUCTURED OUTPUT (PYDANTIC)
# -----------------------------
class DermatologyReport(BaseModel):
    patient_summary: str = Field(description="Summary")
    key_observations: str
    possible_conditions: str
    recommended_actions: str
    lifestyle_plan: str
    follow_up: str
    explanation: str

parser = PydanticOutputParser(pydantic_object=DermatologyReport)
format_instructions = parser.get_format_instructions()

# -----------------------------
# 🧾 PROMPT (AGENT-LIKE LOGIC)
# -----------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", f"""
You are a Dermatologist AI.

WORKFLOW:
1. Ask questions if info is insufficient
2. If needed, request web search using:
   SEARCH: <query>
3. If enough info → generate final report

IMPORTANT:
Return JSON ONLY for final report.

{format_instructions}
"""),
    ("human", "{input}")
])

chain = prompt | llm

# -----------------------------
# 🚀 MAIN LOOP
# -----------------------------
print("🧑‍⚕️ LangChain Dermatology System Started\n")

while True:
    user_input = input("\nEnter input (or exit): ")

    if user_input.lower() == "exit":
        break

    # Add user message to history
    history.add_user_message(user_input)

    # Combine history manually
    conversation = "\n".join([
        f"{msg.type}: {msg.content}" for msg in history.messages
    ])

    # Run model
    response = chain.invoke({"input": conversation})
    output = response.content

    # -----------------------------
    # 🔍 TOOL HANDLING (SIMULATED AGENT)
    # -----------------------------
    if "SEARCH:" in output:
        query = output.split("SEARCH:")[-1].strip()

        tool_result = search_web(query)

        print("\n🔎 TOOL USED:\n", tool_result)

        history.add_ai_message(f"[TOOL RESULT]: {tool_result}")
        continue

    print("\n=== RESPONSE ===\n")
    print(output)

    history.add_ai_message(output)

    # -----------------------------
    # 🧪 PARSE STRUCTURED OUTPUT
    # -----------------------------
    try:
        structured = parser.parse(output)

        print("\n✅ STRUCTURED OUTPUT:\n")
        print(structured.model_dump())

    except Exception:
        print("\n⚠️ Not structured output yet (still Q&A phase)")