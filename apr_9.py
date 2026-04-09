from langchain_community.document_loaders.csv_loader import CSVLoader

loader=CSVLoader(
    file_path="data.csv"
)

document=loader.load()

for i in loader.lazy_load():
    print(document)