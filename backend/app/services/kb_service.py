# services/kb_service.py
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Hapa unaweza kutumia Vector DB yako (k.m. ChromaDB, FAISS, au Orodha ya kawaida)
vector_store = []


def load_and_index_documents(docs_dir: str = "./data/docs") -> int:
    """Inasoma nyaraka zote kutoka kwenye folda na kuzihifadhi kwenye vector store."""
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir, exist_ok=True)
        print(f"📁 Folda la {docs_dir} limetengenezwa. Weka nyaraka zako hapa.")
        return 0

    # 1. Soma nyaraka zote za .txt au .pdf
    loader = DirectoryLoader(docs_dir, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()

    if not documents:
        print("⚠️ Hakuna nyaraka zilizopatikana kwenye folda.")
        return 0

    # 2. Kata nyaraka kuwa vipande vidogo (chunks)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)

    # 3. Hifadhi kwenye Vector Store
    global vector_store
    vector_store.clear()
    vector_store.extend(chunks)

    return len(chunks)


def get_vector_store():
    return vector_store