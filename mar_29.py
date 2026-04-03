import os
from dotenv import load_dotenv
from pydantic import BaseModel

# LLM
from langchain_groq import ChatGroq

# Core
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

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
# 🧠 STATE
# -----------------------------
state = {
    "stage": "questioning",
    "questions_asked": 0,
    "answers": {}
}

# -----------------------------
# 📊 STRUCTURED OUTPUT
# -----------------------------
class HairLossReport(BaseModel):
    patient_summary: str
    key_observations: str
    possible_conditions: str
    recommended_actions: str
    lifestyle_plan: str
    follow_up: str
    explanation: str

parser = PydanticOutputParser(pydantic_object=HairLossReport)
format_instructions = parser.get_format_instructions()

# -----------------------------
# 🧾 PROMPTS
# -----------------------------

# QUESTION PROMPT
question_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a professional Trichologist AI.

Ask ONLY ONE question at a time.

RULES:
- Do NOT give diagnosis
- Do NOT give suggestions
- Ask relevant next question based on previous answers
- Avoid repeating questions

Focus areas:
- duration
- hair loss pattern
- stress
- diet
- scalp condition
- medical history
"""),
    ("human", "{input}")
])

question_chain = question_prompt | llm


# REPORT PROMPT
report_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""
You are a professional Trichologist AI.

Based on user answers, generate:

1. Clear explanation (human readable)
2. Structured JSON report

RULES:
- No medical claims
- No prescriptions
- Simple language for general users

STRICT FORMAT:
{format_instructions}
"""),
    ("human", "User answers: {answers}")
])

report_chain = report_prompt | llm


# -----------------------------
# 🔁 MAIN LOOP
# -----------------------------
print("🧑‍⚕️ Hair Loss Trichologist AI Started\n")

while True:
    user_input = input("\nEnter input (or exit): ")

    if user_input.lower() == "exit":
        break

    # Save user input
    history.add_user_message(user_input)

    # -----------------------------
    # 🧠 QUESTIONING STAGE
    # -----------------------------
    if state["stage"] == "questioning":

        # Store answer
        if state["questions_asked"] > 0:
            state["answers"][f"q{state['questions_asked']}"] = user_input

        # Ask next question
        response = question_chain.invoke({"input": user_input})
        output = response.content

        print("\n🤖 QUESTION:\n")
        print(output)

        history.add_ai_message(output)

        state["questions_asked"] += 1

        # Move to report after 4 questions
        if state["questions_asked"] >= 4:
            state["stage"] = "reporting"

    # -----------------------------
    # 📊 REPORTING STAGE
    # -----------------------------
    elif state["stage"] == "reporting":

        response = report_chain.invoke({
            "answers": str(state["answers"])
        })

        output = response.content

        print("\n=== FINAL REPORT ===\n")
        print(output)

        # Validate JSON
        try:
            structured = parser.parse(output)
            print("\n✅ STRUCTURED OUTPUT:\n")
            print(structured.model_dump())
        except Exception as e:
            print("\n❌ JSON PARSE FAILED:", e)

        # Reset state for next session
        state = {
            "stage": "questioning",
            "questions_asked": 0,
            "answers": {}
        }

        history.clear()