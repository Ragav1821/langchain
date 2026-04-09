import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

# LLM
from langchain_groq import ChatGroq

# Core
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

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
# 🧠 STATE
# -----------------------------
state = {
    "stage": "questioning",
    "answers": {
        "duration": None,
        "pattern": None,
        "lifestyle": None,
        "diet": None,
        "scalp": None
    }
}

# -----------------------------
# 📊 EXTRACTION SCHEMA
# -----------------------------
class Extraction(BaseModel):
    duration: Optional[str] = None
    pattern: Optional[str] = None
    lifestyle: Optional[str] = None
    diet: Optional[str] = None
    scalp: Optional[str] = None

extract_parser = PydanticOutputParser(pydantic_object=Extraction)
extract_format = extract_parser.get_format_instructions()
extract_format = extract_format.replace("{", "{{").replace("}", "}}")

# -----------------------------
# 📊 FINAL REPORT SCHEMA
# -----------------------------
class HairLossReport(BaseModel):
    patient_summary: str
    key_observations: str
    possible_conditions: str
    recommended_actions: str
    lifestyle_plan: str
    follow_up: str
    explanation: str

report_parser = PydanticOutputParser(pydantic_object=HairLossReport)
report_format = report_parser.get_format_instructions()
report_format = report_format.replace("{", "{{").replace("}", "}}")

# -----------------------------
# 🤖 EXTRACTION PROMPT
# -----------------------------
extract_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""
You are a trichology data extraction AI.

Extract structured data from user input.

Fields:
- duration
- pattern
- lifestyle
- diet
- scalp

RULES:
- Extract only if clearly mentioned
- Do NOT guess
- Return null if not present

FORMAT:
{extract_format}
"""),
    ("human", "{input}")
])

extract_chain = extract_prompt | llm

# -----------------------------
# 🤖 QUESTION PROMPT
# -----------------------------
question_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a Trichologist AI.

Ask ONE intelligent question.

RULES:
- Ask ONLY ONE question
- Do NOT repeat known info
- Focus on missing fields only
- No advice or diagnosis
- Keep it simple

Fields:
duration, pattern, lifestyle, diet, scalp
"""),
    ("human", """
Known answers:
{answers}

Missing fields:
{missing}
""")
])

question_chain = question_prompt | llm

# -----------------------------
# 🤖 REPORT PROMPT
# -----------------------------
report_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""
You are a professional Trichologist AI.

Based on user data:

1. Explain cause of hair loss
2. Suggest safe actions

RULES:
- No medical claims
- No prescriptions
- Simple language

STRICT FORMAT:
{report_format}
"""),
    ("human", "User data: {answers}")
])

report_chain = report_prompt | llm

# -----------------------------
# 🧠 HELPERS
# -----------------------------
def extract_info_llm(user_input):
    try:
        response = extract_chain.invoke({"input": user_input})
        parsed = extract_parser.parse(response.content)
        data = parsed.model_dump()

        for key, value in data.items():
            if value and state["answers"][key] is None:
                state["answers"][key] = value

    except Exception as e:
        print("⚠️ Extraction error:", e)


def get_missing_fields():
    return [k for k, v in state["answers"].items() if v is None]


# -----------------------------
# 🚀 MAIN LOOP
# -----------------------------
print("🧑‍⚕️ Hair Loss Trichologist AI Started\n")

while True:
    user_input = input("\nEnter input (or exit): ")

    if user_input.lower() == "exit":
        break

    # -----------------------------
    # 🧠 EXTRACT INFO
    # -----------------------------
    extract_info_llm(user_input)

    # -----------------------------
    # 🔍 CHECK MISSING
    # -----------------------------
    missing = get_missing_fields()

    # -----------------------------
    # 🤖 QUESTIONING STAGE
    # -----------------------------
    if state["stage"] == "questioning":

        if missing:
            response = question_chain.invoke({
                "answers": state["answers"],
                "missing": missing
            })

            print("\n🤖 QUESTION:\n")
            print(response.content)

        else:
            state["stage"] = "reporting"

    # -----------------------------
    # 📊 REPORTING STAGE
    # -----------------------------
    if state["stage"] == "reporting":

        response = report_chain.invoke({
            "answers": str(state["answers"])
        })

        output = response.content

        print("\n=== FINAL REPORT ===\n")
        print(output)

        # -----------------------------
        # ✅ VALIDATE JSON
        # -----------------------------
        try:
            structured = report_parser.parse(output)
            print("\n✅ STRUCTURED OUTPUT:\n")
            print(structured.model_dump())

        except Exception as e:
            print("\n❌ JSON FAILED:", e)

        # RESET
        state = {
            "stage": "questioning",
            "answers": {
                "duration": None,
                "pattern": None,
                "lifestyle": None,
                "diet": None,
                "scalp": None
            }
        }

        print("\n🔄 Session reset\n")