import streamlit as st
import os
import streamlit as st
from langchain.vectorstores import Chroma
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
from langchain.chains.summarize import load_summarize_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import WebBaseLoader
from langchain.memory import ConversationBufferMemory
import os
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

#st.set_page_config(layout="wide",page_title="Home")

# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()

st.markdown(
    f"""
    <h1 style='text-align: center; color:#45035E; font-family: Verdana;'> Chat with any website</h1>
    """,
    unsafe_allow_html=True,
)

user_api_key = utils.load_api_key()

if not user_api_key:
    layout.show_api_key_missing()

else:
    os.environ["OPENAI_API_KEY"] = user_api_key

    def get_website_url(url):
        loader = WebBaseLoader(url)
        docs = loader.load()
        return docs             #getting the website data

    website_url = st.text_input("Website URL")
    if website_url :
            text = get_website_url(website_url)   #get the
            text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1500,   #size of a single chunk
            chunk_overlap = 150  #how much overlapping between two chunks
        )

            splits = text_splitter.split_documents(text)
            #print(splits[0:50])
            embedding = OpenAIEmbeddings()

            vectordb = Chroma.from_documents(
            documents=splits,
            embedding=embedding
        )
            # Define prompt
            template = """Given the website data answer the query with respect to the website data, 
            then take the follow up query and rephrase the follow up query to be a standalone question, in its original language 
            & answer it based on the content of the website.Also say "Thanks for asking this question" after every query. 
            If you don't know the answer say "Sorry, I don't know the answer to this question.", don't make up
            your own answer. Be polite and fluent in your answers.
            Chat History:
            {chat_history}
            Follow Up Input: {query}
            Standalone question:"""
            CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(template)

            st.session_state["history"] = []

            memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True    #returns chat history as a list of messages as opposed to a single string
        )
            llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
            chain = ConversationalRetrievalChain.from_llm(
                    llm,
                    retriever= vectordb.as_retriever() ,
                    memory=memory,
                    condense_question_prompt=CONDENSE_QUESTION_PROMPT,
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




