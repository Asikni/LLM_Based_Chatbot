import os
import streamlit as st
from io import StringIO
import re
import sys
from modules.Chat_history import ChatHistory
from modules.Page_layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar

#To be able to update the changes made to modules in localhost (press r)
def reload_module(module_name):
    import importlib
    import sys
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    return sys.modules[module_name]

#The reload_module() function takes a module name as its argument and imports the module again. This effectively 
# resets the module to its original state, including any changes that we have made to it.
history_module = reload_module('modules.Chat_history')
layout_module = reload_module('modules.Page_layout')
utils_module = reload_module('modules.utils')
sidebar_module = reload_module('modules.sidebar')

ChatHistory = history_module.ChatHistory   #creating variables 
Layout = layout_module.Layout
Utilities = utils_module.Utilities
Sidebar = sidebar_module.Sidebar


st.set_page_config(layout="wide", page_title="Medical Chatbot")
# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()

layout.Header("PDF, TXT, CSV, JSON, HTML")

user_api_key = utils.load_api_key()   #get api key


os.environ["OPENAI_API_KEY"] = user_api_key

uploaded_file = utils.handle_upload(["pdf", "txt", "csv","html"])   #types of files to be handled

if uploaded_file:

        # Configure the sidebar
        sidebar.show_options()
        sidebar.about()

        # Initialize chat history
        history = ChatHistory()
        try:
            chatbot = utils.setup_chatbot(
                uploaded_file, st.session_state["model"], st.session_state["temperature"]
            )   #model is the key in the session_state dict
            st.session_state["chatbot"] = chatbot

            if st.session_state["ready"]:
                # Create containers for chat responses and user prompts
                response_container, prompt_container = st.container(), st.container()

                with prompt_container:
                    # Display the prompt form
                    is_ready, user_input = layout.prompt_form()

                    # Initialize the chat history
                    history.initialize(uploaded_file)

                    # Reset the chat history if button clicked
                    if st.session_state["reset_chat"]:
                        history.reset(uploaded_file)

                    if is_ready:
                        # Update the chat history and display the chat messages
                        history.append("user", user_input)

                        old_stdout = sys.stdout
                        sys.stdout = captured_output = StringIO()

                        output = st.session_state["chatbot"].conversational_chatbot(user_input)

                        sys.stdout = old_stdout

                        history.append("assistant", output)

                        # Clean up the agent's thoughts to remove unwanted characters
                        thoughts = captured_output.getvalue()
                        cleaned_thoughts = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', thoughts)
                        cleaned_thoughts = re.sub(r'\[1m>', '', cleaned_thoughts)
                history.generate_messages(response_container)
        except Exception as e:
            st.error(f"Error: {str(e)}")


