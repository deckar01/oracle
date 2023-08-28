class ChromaIndex:
    index: str

    def __init__(self):
        super().__init__()
        from langchain.vectorstores import Chroma
        self.db = Chroma(embedding_function=self.embedding, persist_directory=self.index)

    def find(self, text):
        instruction = 'Represent this sentence for searching relevant passages: '
        results = self.db.similarity_search_with_relevance_scores(
            instruction + text,
            k=8,
        )
        for doc, score in results:
            yield f'# Relevance: {score:.0%}\n{doc.page_content}'