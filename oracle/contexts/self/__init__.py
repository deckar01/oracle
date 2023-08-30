from ..bge_embedding import BGEEmbedding
from ..chroma_index import ChromaIndex

class Context(ChromaIndex, BGEEmbedding):
    index = 'oracle/contexts/self/index'
    name = 'Oracle\'s source code'
    motive = "I am an instance of the Oracle project. "\
        "I can search my source code for context. "\
        "I provide useful responses to messages."
