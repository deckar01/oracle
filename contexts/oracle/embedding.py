from langchain.embeddings import HuggingFaceBgeEmbeddings
import torch


if torch.cuda.is_available() and torch.cuda.device_count():
    DEVICE = 'cuda'
else:
    DEVICE = 'cpu'

bge_base_en = HuggingFaceBgeEmbeddings(
    model_name='BAAI/bge-base-en',
    model_kwargs={'device': DEVICE},
    encode_kwargs={'normalize_embeddings': True}
)
