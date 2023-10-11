import streamlit as st

class Layout:
    
    def Header(self, types_files):
        """
        Displays the header of our application
        """
 
        st.markdown(
            f"""
            <h1 style='text-align: center; color:#45035E; font-family: Verdana;'> Document Assistant </h1>
            """,
            unsafe_allow_html=True,
        )


    def prompt_form(self):
        """
        Displays the prompt form
        """
        with st.form(key="my_form", clear_on_submit=True): #clear_on_submit argument is set to True so that the text area is cleared when the user submits the form
            user_input = st.text_area(
                "Query:",
                placeholder="What do you want to know....",
                key="input",
                label_visibility="hidden",   #check this out
            )
            submit_button = st.form_submit_button(label="Submit", type = "primary")
            
            is_ready = submit_button and user_input
        return is_ready, user_input
    
