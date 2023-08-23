import os

from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from langchain.vectorstores import Chroma
from langchain.document_loaders.text import TextLoader

from oracle.embeddings import bge_base_en


print('archiving repo...')
os.system('git archive HEAD -o contexts/oracle/source.tar.gz')
os.system('tar -xf contexts/oracle/source.tar.gz -C contexts/oracle/source')

print('loading repo...')
scraper = DirectoryLoader(
    'contexts/oracle/source',
    loader_cls=TextLoader,
    silent_errors=True,
    recursive=True,
    load_hidden=True,
    show_progress=True,
)
repo = scraper.load()

LANG = {
    'py': Language.PYTHON,
    'md': Language.MARKDOWN,
}

options = {
    'chunk_size': 256,
}

def get_splitter(doc):
    Splitter = RecursiveCharacterTextSplitter
    ext = doc.metadata['source'].split('.')[-1]
    if ext in LANG:
        return Splitter.from_language(LANG[ext], **options)
    else:
        return Splitter(**options)

print('Chunking files...')
chunks = [
    chunk
    for doc in repo
    for chunk in get_splitter(doc).split_documents([doc])
    if doc.page_content.strip()
]

print('building db...')
db = Chroma.from_documents(
    chunks,
    bge_base_en,
    persist_directory='contexts/oracle/index',
)
