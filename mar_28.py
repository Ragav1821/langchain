import os
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface import ChatHuggingFace

# Load env
load_dotenv()

# Step 1: Create LLM
llm = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",  # ✅ supported
    task="text-generation",
    temperature=0.7,
    max_new_tokens=512,
)

# Step 2: Wrap into chat model
model = ChatHuggingFace(llm=llm)

# Step 3: Invoke
response = model.invoke("Why do parrots talk?")
print(response.content)