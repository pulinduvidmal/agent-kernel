import os
from typing import List
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class RAGService:
    def __init__(self, data_directory="local_data"):
        data_directory = os.path.abspath(data_directory)
        print(f"[RAG] Initializing… data dir = {data_directory}")
        self.db = self._load_and_index(data_directory)
        self.retriever = self.db.as_retriever(search_kwargs={"k": 5})
        print("[RAG] Ready.")

    def _load_and_index(self, directory):
        loader = DirectoryLoader(
            directory,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8", "autodetect_encoding": True},
            show_progress=True,
        )
        documents = loader.load()
        print(f"[RAG] Loaded {len(documents)} docs")

        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        chunks = splitter.split_documents(documents)
        print(f"[RAG] Split into {len(chunks)} chunks")

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db = FAISS.from_documents(chunks, embeddings)
        print("[RAG] FAISS index built")
        return db

    def query(self, question: str):
        print(f"[RAG] Query: {question}")
        docs = self.retriever.get_relevant_documents(question)
        return [
            {
                "snippet": d.page_content[:300].replace("\n", " "),
                "source": (d.metadata.get("source") or "unknown"),
            }
            for d in docs
        ]