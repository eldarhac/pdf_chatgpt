import streamlit as st
import os
import tempfile
from pdf_translator import translate_pdf

# File uploader allows the user to upload a PDF
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save the file to a temporary directory
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpfile:
        tmpfile.write(uploaded_file.getvalue())
        file_path = tmpfile.name

    # Translate the PDF (you'll implement the actual logic)
    translated_file_path = translate_pdf(file_path)

    # Provide a link to download the translated file
    with open(translated_file_path, "rb") as file:
        btn = st.download_button(
            label="Download Translated PDF",
            data=file,
            file_name="translated.pdf",
            mime="application/octet-stream"
        )

    Optional: Clean up if you want to delete the temporary files
    os.remove(file_path)
    os.remove(translated_file_path)
