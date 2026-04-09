import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM (Hugging Face)
from langchain_community.llms import HuggingFaceHub

# Tool (Web Search)
from langchain_community.tools import DuckDuckGoSearchRun

# Stable Agent API
from langchain.agents import initialize_agent, AgentType

# -------------------------------
# LLM SETUP
# -------------------------------
llm = HuggingFaceHub(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    model_kwargs={
        "temperature": 0.3,
        "max_new_tokens": 256
    }
)

# -------------------------------
# TOOL SETUP
# -------------------------------
search = DuckDuckGoSearchRun()
tools = [search]

# -------------------------------
# AGENT SETUP
# -------------------------------
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# -------------------------------
# CLI LOOP
# -------------------------------
while True:
    query = input("\nAsk something (or 'exit'): ")

    if query.lower() == "exit":
        break

    try:
        response = agent_executor.run(query)
        print("\nAnswer:\n", response)

    except Exception as e:
        print("\nError:", str(e))