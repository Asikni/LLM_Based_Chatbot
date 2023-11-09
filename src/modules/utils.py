import os
import pandas as pd
import streamlit as st
import pdfplumber

from modules.chatbot_main import Chatbot
from modules.doc_embeddings import Embedder

class Utilities:

    @staticmethod
    def load_api_key():
        """
        Loads the OpenAI API key from the .env file or 
        from the user's input and returns it
        """
        if not hasattr(st.session_state, "api_key"):
            st.session_state.api_key = None
        
        if st.session_state.api_key is not None:
                user_api_key = st.session_state.api_key
        else:
                user_api_key = st.sidebar.text_input(
                    label="Enter OpenAI API key", 
                    placeholder="API Key", 
                    type="password",   #API key entered would remain hidden
                    max_chars = 51
                )
                if user_api_key:
                    st.session_state.api_key = user_api_key

        return user_api_key

    
    @staticmethod
    def handle_upload(file_types):
        """
        Handles and display uploaded_file
        :param file_types: List of accepted file types, e.g., ["csv", "pdf", "txt","html]
        """
        uploaded_file = st.file_uploader("Choose a file", 
                                                 type=file_types,
                                                 label_visibility="collapsed")
        
        if uploaded_file is not None:

            def show_csv_file(uploaded_file):
                file_container = st.expander("Uploaded CSV File")  
                uploaded_file.seek(0)
                shows = pd.read_csv(uploaded_file)  #read csv file
                file_container.write(shows)

            def show_pdf_file(uploaded_file):
                file_container = st.expander("Uploaded PDF File")
                with pdfplumber.open(uploaded_file) as pdf:  #using pdfplumber to open file
                    pdf_text = ""
                    for page in pdf.pages:
                        pdf_text += page.extract_text() + "\n\n"
                file_container.write(pdf_text)
            
            def show_txt_file(uploaded_file):
                file_container = st.expander("Uploaded TXT File")
                uploaded_file.seek(0)
                content = uploaded_file.read().decode("utf-8")  #read text file
                file_container.write(content)
            
            def get_file_extension(uploaded_file):
                return os.path.splitext(uploaded_file)[1].lower()  #get the file extension of the uploaded file and return it in lowercase.
                
            
            #file_extension = get_file_extension(uploaded_file.name)

            # Show the contents of the file based on its extension
            #if file_extension == ".csv" :
                #show_csv_file(uploaded_file)
            #if file_extension == ".pdf" : 
                #show_pdf_file(uploaded_file)
            #elif file_extension == ".txt" : 
                #show_txt_file(uploaded_file)

        else:
            st.session_state["reset_chat"] = True

        #print(uploaded_file)
        return uploaded_file

    @staticmethod
    def setup_chatbot(uploaded_file, model, temperature):
        """
        Sets up the chatbot with the uploaded file, model, and temperature
        """
        embedding = Embedder()

        with st.spinner("Processing..."):
            
            uploaded_file.seek(0)
            file = uploaded_file.read()
            # Get the document embeddings for the uploaded file
            vectors = embedding.Get_document_embeddings(file, uploaded_file.name)

            # Create a Chatbot instance with the specified model and temperature
            chatbot = Chatbot(model, temperature,vectors)
        st.session_state["ready"] = True

        return chatbot


    
