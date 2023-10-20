import os
import pickle
import streamlit as st
import tempfile
from modules.sidebar import Sidebar
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
class Embedder:

    def __init__(self):
        self.PATH = "embeddings"
        self.createEmbeddingsDir()
        self.chunk_size = st.session_state["chunk_size"]
        self.overlap = st.session_state["chunk_size"]
        self.split = st.session_state["split"]
         
    def createEmbeddingsDir(self):
        """
        Creates a directory to store the embeddings vectors
        """
        if not os.path.exists(self.PATH):
            os.mkdir(self.PATH)

    def Store_document_embeddings(self, file, original_filename):
        """
        Stores document embeddings using Langchain and  FAISS
        """
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp_file:
            tmp_file.write(file)
            tmp_file_path = tmp_file.name
            
        def get_file_extension(uploaded_file):
            file_extension =  os.path.splitext(uploaded_file)[1].lower()
            
            return file_extension
        
        def split_texts(chunk_size, overlap,length_function ,split_method) :
            splitter = None

            if split_method == "Recursive Character Text Splitter":
                splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,length_function = length_function ,
                                                            chunk_overlap=overlap)
            elif split_method == "Character Text Splitter":
                splitter = CharacterTextSplitter(
                                                    chunk_size=chunk_size,length_function =length_function ,
                                                    chunk_overlap=overlap)
            print(splitter)
            return splitter
        
        text_splitter = split_texts(chunk_size= self.chunk_size , overlap =  self.overlap, length_function  = len, split_method =  self.split)
        file_extension = get_file_extension(original_filename)

        if file_extension == ".csv":
            loader = CSVLoader(file_path=tmp_file_path, encoding = 'utf8')
            data = loader.load_and_split(text_splitter)
            data = loader.load()

        elif file_extension == ".pdf":
            loader = PyPDFLoader(file_path=tmp_file_path)  
            data = loader.load_and_split(text_splitter)
        
        elif file_extension == ".txt":
            loader = TextLoader(file_path=tmp_file_path)
            data = loader.load_and_split(text_splitter)

        elif file_extension == ".html":
            loader = UnstructuredHTMLLoader(file_path=tmp_file_path)
            data = loader.load_and_split(text_splitter)

        embeddings = OpenAIEmbeddings()

   
        vectors = FAISS.from_documents(data, embeddings)
        os.remove(tmp_file_path)

        # Save the vectors to a pickle file
        with open(f"{self.PATH}/{original_filename}.pkl", "wb") as f:
            pickle.dump(vectors, f)

    def Get_document_embeddings(self, file, original_filename):
        """
        Retrieves document embeddings
        """
        if not os.path.isfile(f"{self.PATH}/{original_filename}.pkl"):
            self.Store_document_embeddings(file, original_filename)

        # Load the vectors from the pickle file
        with open(f"{self.PATH}/{original_filename}.pkl", "rb") as f:
            vectors = pickle.load(f)
        
        return vectors
