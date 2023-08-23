class Context:
    name = 'Oracle'
    motive = "You are an instance of the oracle project. You have been provided search results related to a message about your source code. Reply to the message."

    def __init__(self):
        from langchain.vectorstores import Chroma
        from contexts.oracle.embedding import bge_base_en

        self.db = Chroma(embedding_function=bge_base_en, persist_directory='contexts/oracle/index')

    def find(self, text):
        instruction = 'Represent this sentence for searching relevant passages: '
        results = self.db.similarity_search(instruction+text, k=8)
        for doc in results:
            yield doc.page_content
