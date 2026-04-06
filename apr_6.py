from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

# =========================
# LLM
# =========================
llm = ChatOpenAI(
    model="Qwen/Qwen2.5-72B-Instruct",
    temperature=0.3
)

# =========================
# TOOL
# =========================
tools = [TavilySearchResults(max_results=3)]

# =========================
# CUSTOM PROMPT
# =========================
prompt = PromptTemplate.from_template("""
You are an intelligent AI assistant.

STRICT RULES:
-You dont give Answers from internal knowledge
- You MUST use the search tool before answering.
- DO NOT answer directly.
- Always follow the format.

Format:

Question: {input}
Thought: think about what to do
Action: one of [{tool_names}]
Action Input: input for the tool
Observation: result of the tool
... (repeat if needed)
Thought: I now know the final answer
Final Answer: final answer to user

{agent_scratchpad}
""")

# =========================
# AGENT
# =========================
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"prompt": prompt},
    verbose=True
)

# =========================
# RUN
# =========================
query = "Latest AI trends in 2026"

response = agent.invoke({"input": query})

print("\nFinal Answer:\n", response["output"])