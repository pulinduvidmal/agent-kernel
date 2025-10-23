import os
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

class RAGService:
    def __init__(self, data_directory="local_data/"):
        print("Initializing RAG Service...")
        self.db = self._load_and_index(data_directory)
        self.retriever = self.db.as_retriever()
        print("RAG Service Ready.")

    def _load_and_index(self, directory):
        # 1. Load Documents
        # Use TextLoader for .txt files
        loader = DirectoryLoader(directory, glob="**/*.txt", loader_cls=TextLoader)
        documents = loader.load()
        print(f"Loaded {len(documents)} documents.")

        # 2. Split Documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        print(f"Split into {len(splits)} chunks.")

        # 3. Create Embeddings (Local Model)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # 4. Store in FAISS Vector DB
        db = FAISS.from_documents(splits, embeddings)
        print("Created FAISS vector index.")
        return db

    def query(self, question):
        """
        Takes a user question, finds relevant docs, and returns them.
        """
        print(f"RAG received query: {question}")
        relevant_docs = self.retriever.get_relevant_documents(question)
        return relevant_docs

if __name__ == "__main__":
    rag = RAGService()
    results = rag.query("What is the latest news from the local area?")
    for doc in results:
        print("--- RELEVANT CHUNK ---")
        print(doc.page_content)