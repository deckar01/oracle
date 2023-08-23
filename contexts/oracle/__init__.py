from langchain.vectorstores import Chroma
from oracle.embeddings import bge_base_en


name = 'Oracle'
motive = "You are have been provided search results related to a question about your source code. Answer the question about your source code."

db = Chroma(embedding_function=bge_base_en, persist_directory='contexts/oracle/index')

def find(text):
    instruction = 'Represent this sentence for searching relevant passages: '
    results = db.similarity_search(instruction+text, k=8)
    for doc in results:
        yield doc.page_content