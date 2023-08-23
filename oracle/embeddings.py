from langchain.embeddings import HuggingFaceBgeEmbeddings

bge_base_en = HuggingFaceBgeEmbeddings(
    model_name='BAAI/bge-base-en',
    model_kwargs={'device': 'cuda'},
    encode_kwargs={'normalize_embeddings': True}
)
