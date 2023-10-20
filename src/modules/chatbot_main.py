import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain.memory import ConversationBufferMemory
from modules.sidebar import Sidebar
import langchain
langchain.verbose = False

class Chatbot:

    def __init__(self, model_name, temperature, vectors):
        self.model_name = model_name
        self.temperature = temperature
        self.vectors = vectors
        

    def conversational_chatbot(self, query):
        """
        Start a conversational chat with a model via Langchain
        """
        llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)
        #chain_type = 'refine' or map_rank  #we can use this also
        #chain_type = 'stuff' which acts as default
        retriever = self.vectors.as_retriever()
        memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True    #returns chat history as a list of messages as opposed to a single string
)
        template = """Given an uploaded file, take the query and answer it based on the uploaded file then take up
        a follow up query, rephrase the follow up query to be a standalone question, in its original language. Also
        say "Thanks for asking this question" after every query. If you don't know the answer say "Sorry, I don't 
        know the answer to this question.", don't make up your own answer. Be polite and fluent in your answers
        Chat History:
        {chat_history}
        Follow Up Input: {query}
        Standalone question:"""
        CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(template)

        
        chain = ConversationalRetrievalChain.from_llm(llm=llm, memory=memory,condense_question_prompt=CONDENSE_QUESTION_PROMPT,
            retriever=retriever,verbose=True, return_source_documents=False)
      
        chain_input = {"question": query, "chat_history": st.session_state["history"]}
        result = chain(chain_input)

        st.session_state["history"].append((query, result["answer"]))
        return result["answer"]
    
    
