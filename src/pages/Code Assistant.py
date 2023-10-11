import streamlit as st
import os
from langchain.vectorstores import FAISS
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
from langchain.chains.summarize import load_summarize_chain
from langchain.embeddings.openai import OpenAIEmbeddings
import shutil
from langchain.memory import ConversationBufferMemory
import os
import stat
from git import Repo
from langchain.text_splitter import Language
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

st.markdown(
    f"""
    <h1 style='text-align: center; color:#45035E; font-family: Verdana;'> Know about any code </h1>
    """,
    unsafe_allow_html=True,
)


# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()


user_api_key = utils.load_api_key()

if not user_api_key:
    layout.show_api_key_missing()

else:
    os.environ["OPENAI_API_KEY"] = user_api_key
    def redo_with_write(redo_func, path, err):
        os.chmod(path, stat.S_IWRITE)
        redo_func(path)

    repo_path = "D:/llm-based-assistant/code"   
     # Check if the directory exists
    if os.path.exists(repo_path):
        # Delete the directory
        shutil.rmtree(repo_path ,onerror = redo_with_write)
    def get_website_url(url, path):

        repo = Repo.clone_from(url, to_path=path)

        loader = GenericLoader.from_filesystem(
            path,
            glob="**/*",
            suffixes=[".py", 'pdf'],
            parser=LanguageParser(language=Language.PYTHON, parser_threshold=500)
        )
        documents = loader.load()
        
        return documents
    website_url = st.text_input("Website URL")

    if website_url :
            text = get_website_url(website_url, repo_path)   #get the
            
            python_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON, 
                                                                        chunk_size=500, 
                                                                        chunk_overlap=50)
            texts = python_splitter.split_documents(text)
            embedding = OpenAIEmbeddings()

            vectordb = FAISS.from_documents(
            documents=texts,
            embedding=embedding
        )
            # Define prompt
            template = """Given the website url answer the query with respect to the website data, 
            then take the follow up query and rephrase the follow up query to be a standalone question, in its original language 
            & answer it based on the content of the website.Also say "Thanks for asking this question" after every query. 
            If you don't know the answer say "Sorry, I don't know the answer to this question.", don't make up
            your own answer. Be polite and fluent in your answers.
            Chat History:
            {chat_history}
            Standalone question:"""
            CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(template)

            st.session_state["history"] = []
            llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
            memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True    #returns chat history as a list of messages as opposed to a single string
            )
            
            chain = ConversationalRetrievalChain.from_llm(
                    llm,
                    retriever= vectordb.as_retriever(search_type = 'mmr') ,
                    memory=memory,
                    #condense_question_prompt=CONDENSE_QUESTION_PROMPT,
                )
            summary_chain = load_summarize_chain(llm,
                                            chain_type="refine",verbose=True)
            #answer = summary_chain.run(text)
            #st.markdown(answer)

            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if query := st.chat_input("What do you want to know...."):

                st.chat_message("user").markdown(query)
                st.session_state.messages.append({"role": "user", "content": query})
                if query == None:
                    query = "How can I assist you?"

                print("The type of the query is :",type(query))

                chain_input = {"question": query, "chat_history": st.session_state.messages}
                result = chain(chain_input)
                st.session_state["history"] += [(query, result["answer"])]

                answer = result["answer"]
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    
                st.session_state.messages.append({"role": "assistant", "content": answer})


def reset_conversation():
  st.session_state.conversation = None
  st.session_state.chat_history = None
  st.session_state.messages = []

st.sidebar.button('Reset Chat', on_click=reset_conversation)
