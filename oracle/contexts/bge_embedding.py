import oracle


class BGEEmbedding:
    def __init__(self):
        super().__init__()
        from langchain.embeddings import HuggingFaceBgeEmbeddings
        self.embedding = HuggingFaceBgeEmbeddings(
            model_name='BAAI/bge-base-en',
            model_kwargs={'device': oracle.get_device()},
            encode_kwargs={'normalize_embeddings': True}
        )
