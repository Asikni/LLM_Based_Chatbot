import streamlit as st

class Sidebar:

    MODEL_OPTIONS = ["gpt-3.5-turbo-16k", "gpt-3.5-turbo"]
    Split_options = ["Character Text Splitter",  "Recursive Character Text Splitter"]
    temp_min= 0.0
    temp_max = 1.0
    temp_default= 0.0
    temp_by_step= 0.1
    min_chunk_size = 500
    max_chunk_size = 2500
    default_chunk_size = 1500
    chunk_size_step = 500
    min_chunk_overlap = 0
    max_chunk_overlap = 500
    default_chunk_overlap = 150
    chunk_overlap_step = 50
 



    @staticmethod
    def about():
        about = st.expander("About this chatbot")   #change this
        
        sections = [
            "This is a large language model based medical chatbot.The general flow for this goes, the question comes in, we look up for the relevant documents, we then pass those splits along with a system prompt and the human question to the language model and get the answer. By default, we just pass all the chunks into the same context window, into the same call of the language model."
            
        ]
        for section in sections:
            about.write(section)

        
    def change_sidebar_color(self):
        """
            Change the color of the sidebar
        """
        st.markdown("""
        <style>
            [data-testid=stSidebar] {
                background-color: #C6FFAA;
            }
        </style>
        """, unsafe_allow_html=True)


    @staticmethod
    def reset_chat_button():  
        '''
        Reset the chat
        '''
        if st.button("Clear chat",key='Ctrl+.'):
            st.session_state["reset_chat"] = True
        st.session_state.setdefault("reset_chat", False)

    def model_selector(self):
        model = st.radio(
        "**Choose a Model:**",
        ("gpt-3.5-turbo",  "gpt-3.5-turbo-16k")
        )
        st.session_state["Model"] = model

    def Temperature(self):
        temperature = st.slider(
            label="**Temperature:**",
            min_value=self.temp_min,
            max_value=self.temp_max,
            value=self.temp_default,
            step=self.temp_by_step,
        )
        st.session_state["temperature"] = temperature

    def split_method(self):
        split = st.radio(
        "**Split Method:**",
        ("Character Text Splitter",  "Recursive Character Text Splitter")
        )
        st.session_state["split"] = split
        

    def chunk_size(self):
        chunk_size = st.slider(
                label="**Chunk Size:**",
                min_value= self.min_chunk_size,
                max_value= self.max_chunk_size,
                value=self.default_chunk_size,
                step=self.chunk_size_step,
            )
        st.session_state["chunk_size"] = chunk_size

    def chunk_overlap(self):
        chunk_overlap = st.slider(
                label="**Chunk Overlap:**",
                min_value= self.min_chunk_overlap,
                max_value= self.max_chunk_overlap,
                value=self.default_chunk_overlap,
                step=self.chunk_overlap_step,
            )
        st.session_state["chunk_overlap"] = chunk_overlap


        
    def show_options(self):
        with st.sidebar:
            st.write("**Reset Chat Environment:**")
            self.reset_chat_button()
            st.write("**Hyperparameters:**")
            self.model_selector()
            self.split_method()
            self.chunk_size()
            self.chunk_overlap()
            self.Temperature()
            self.change_sidebar_color()
            st.session_state.setdefault("model", self.MODEL_OPTIONS[0])
            st.session_state.setdefault("temperature", self.temp_default)
            st.session_state.setdefault("split", self.Split_options[1])
            st.session_state.setdefault("chunk_size", self.default_chunk_size)
            st.session_state.setdefault('chunk_overlap' ,self.default_chunk_overlap)

    