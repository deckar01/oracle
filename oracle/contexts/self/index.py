import subprocess

from langchain.vectorstores import Chroma

from ..bge_embedding import BGEEmbedding


def get_authors(file=None):
    meta = subprocess.check_output(
        ['git', 'shortlog', '-s', '-n'] +
        (['--', file] if file else []),
        encoding='utf-8',
    ).strip()
    return ', '.join([
        author.strip().split('\t', 1)[1]
        for author in meta.split('\n')
    ])

print('loading repo...')
paths = subprocess.check_output([
    'git', 'ls-tree',
    '--full-tree', '-r',
    '--name-only',
    'HEAD'
], encoding='utf-8')
files = []
for file in paths.split('\n'):
    if not file.strip():
        continue
    try:
        files.append(
            f'# Filename: {file}\n' +
            f'# Authors: {get_authors(file)}\n' +
            open(file, encoding='utf-8').read()
        )
    except Exception:
        print(f'Ignoring {file}...')

files.append(f'# All project authors: {get_authors()}')
files.append('# Repository Link: https://github.com/deckar01/oracle')

print('building db...')
db = Chroma.from_texts(
    files,
    BGEEmbedding().embedding,
    persist_directory='oracle/contexts/self/index',
)
