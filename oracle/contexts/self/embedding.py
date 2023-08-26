from langchain.embeddings import HuggingFaceBgeEmbeddings

import oracle


bge_base_en = HuggingFaceBgeEmbeddings(
    model_name='BAAI/bge-base-en',
    model_kwargs={'device': oracle.get_device()},
    encode_kwargs={'normalize_embeddings': True}
)
