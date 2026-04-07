from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import json
from langchain.globals import set_verbose
from langchain.globals import set_debug




load_dotenv()
set_verbose(True)
set_debug(True)
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
# OUTPUT PARSER
# =========================
response_schemas = [
    ResponseSchema(name="tool_used", description="Name of the tool used"),
    ResponseSchema(name="final_answer", description="Final answer to the user")
]

parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = parser.get_format_instructions()

# =========================
# CUSTOM PROMPT
# =========================
prompt = PromptTemplate.from_template("""
You are an intelligent AI assistant.

STRICT RULES:
- You MUST use the search tool before answering
- DO NOT answer from internal knowledge
- If tool is not used → response is INVALID

{format_instructions}

Follow this process:

Question: {input}
Thought: think about what to do
Action: one of [{tool_names}]
Action Input: input for the tool
Observation: result of the tool
... (repeat if needed)
Thought: I now know the final answer

{agent_scratchpad}
""")

# =========================
# AGENT
# =========================
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={
        "prompt": prompt.partial(format_instructions=format_instructions)
    },
)

# =========================
# INTERACTIVE LOOP
# =========================
while True:
    query = input("\nEnter your query (or type 'exit'): ").strip()

    if query.lower() == "exit":
        print("Exiting...")
        break

    if not query:
        print("⚠️ Empty input. Please enter a valid query.")
        continue

    try:   
        response = agent.invoke({"input": query})
        raw_output = response["output"]

        print("\nRaw Output:\n", raw_output)

        # =========================

        # =========================
        try:
            parsed_output = parser.parse(raw_output)

        except Exception:
            print("⚠️ Parser failed. Attempting fallback...")

            # Fallback extraction
            parsed_output = {
                "tool_used": "unknown",
                "final_answer": raw_output
            }

        print("\nParsed Output:")
        print(parsed_output)

    except Exception as e:
        print("❌ Error:", str(e))