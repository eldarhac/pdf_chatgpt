import streamlit as st
import os
import tempfile
from pdf_translator import translate_pdf
from random import randint

# File uploader allows the user to upload a PDF
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

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

    #Optional: Clean up if you want to delete the temporary files
    os.remove(translated_file_path)
    uploaded_file.key = str(randint(1000, 100000000))
    st.rerun()
