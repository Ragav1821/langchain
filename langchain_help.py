from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# 🔹 LLM setup (initialize once)
llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    model="meta-llama/llama-3-8b-instruct",
    temperature=0.7
)

# 🔹 Prompt template (reuse)
prompt = PromptTemplate(
    input_variables=["human_type", "letter", "length"],
    template="""
Generate 5 cute South Indian baby names.

Contraints:
- Start with {letter}
- strictly give 5 name
- name must be given length {length}

Return only names as a numbered list.
No explanation.
"""
)

# 🔹 Chain
chain = prompt | llm


# 🔹 Function called by main.py
def generate_raw_names(human_type, letter, length):
    response = chain.invoke({
        "human_type": human_type,
        "letter": letter,
        "length": length
    })

    return response.content