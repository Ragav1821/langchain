from langchain_community.document_loaders import PyPDFLoader

file_path="D:\llm\Presentation - Usability Testing Suite.pdf"

loader=PyPDFLoader(file_path)

docs=loader.load()
print(docs)