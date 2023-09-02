import oracle.device


class BGEEmbedding:
    def __init__(self):
        super().__init__()
        from langchain.embeddings import HuggingFaceBgeEmbeddings
        self.embedding = HuggingFaceBgeEmbeddings(
            model_name='BAAI/bge-base-en',
            model_kwargs={'device': oracle.device.get()},
            encode_kwargs={'normalize_embeddings': True}
        )
