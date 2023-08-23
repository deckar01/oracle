from langchain.vectorstores import Chroma
from oracle.embeddings import bge_base_en


name = 'Oracle'
motive = "You are in instance of the oracle project. You are have been provided search results related to a message about your source code. Reply to the message."

db = Chroma(embedding_function=bge_base_en, persist_directory='contexts/oracle/index')

def find(text):
    instruction = 'Represent this sentence for searching relevant passages: '
    results = db.similarity_search(instruction+text, k=8)
    for doc in results:
        yield doc.page_content
