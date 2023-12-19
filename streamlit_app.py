import streamlit as st
import os
import tempfile
from pdf_translator import translate_pdf
from random import randint

if 'key' not in st.session_state:
    st.session_state['key'] = 'value'

# File uploader allows the user to upload a PDF
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key=2)

if uploaded_file is not None:
    # Save the file to a temporary directory
    # Translate the PDF (you'll implement the actual logic)
    translated_file_path = translate_pdf(uploaded_file)

    # Provide a link to download the translated file
    with open(translated_file_path, "rb") as file:
        btn = st.download_button(
            label="Download Translated PDF",
            data=file,
            file_name=f"{uploaded_file.name[:-4]}_translated.pdf",
            mime="application/octet-stream"
        )
        
    #Optional: Clean up if you want to clear the uploaded file
    st.session_state.pop('key')
    st.rerun()

