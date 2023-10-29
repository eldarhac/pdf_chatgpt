# coding part
import shutil

import streamlit as st
from deep_translator import GoogleTranslator
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.vectorstores.chroma import Chroma
from streamlit_chat import message
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.callbacks import get_openai_callback

import pickle
import os
from subprocess import STDOUT, check_call
check_call(['apt-get', 'install', 'poppler-utils'],
     stdout=open(os.devnull,'wb'), stderr=STDOUT) 


# load api key lib
from dotenv import load_dotenv

# from config import config
from pdf_translator import translate_pdf

# add_bg_from_local('images.jpeg')

# sidebar contents

with st.sidebar:
    st.title("""🦜️ Multilingual ChatGPT for your scanned documents 🤗""")
    st.markdown('''
    ## About APP:

    The app's primary resource is utilised to create::

    - [streamlit](https://streamlit.io/)
    - [Langchain](https://docs.langchain.com/docs/)
    - [OpenAI](https://openai.com/)

    ## About me:

    - [Linkedin](https://www.linkedin.com/in/eldar-refael-hacohen-58b4b018a/)

    ''')

load_dotenv()


def init():
    # test that the API key exists
    # os.environ['OPENAI_API_KEY'] = config.get('OPENAI_API_KEY')
    if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
        print("OPENAI_API_KEY is not set")
        exit(1)
    else:
        print("OPENAI_API_KEY is set")

    # # setup streamlit page
    # st.set_page_config(
    #     page_title="Your own ChatGPT",
    #     page_icon="🤖"
    # )


def main():
    init()

    doc_lang = st.selectbox(
        'Which language is your document in?',
        ('Hebrew', 'English'))

    st.write('You selected:', doc_lang)

    tr = lambda msg: GoogleTranslator(source='auto', target='en').translate(msg)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo")

    # upload a your pdf file
    pdf = st.file_uploader("Upload your PDF", type='pdf')

    if pdf is not None:
        store_name = pdf.name[:-4]
        DIR_NAME = f"{store_name}_dir"

        # initialize message history
        if "messages" not in st.session_state:
            st.session_state.messages = [
                SystemMessage(content="You are a helpful assistant."
                                      "Please provide page numbers and part of the document"
                                      "of where the answer is taken from.")
            ]
            os.makedirs(DIR_NAME, exist_ok=True)
            with open(os.path.join(DIR_NAME, f"{store_name}_history.pkl"), "wb") as f:
                pickle.dump([], f)

        st.header("📄Chat with your pdf file🤗")

        if os.path.exists(os.path.join(DIR_NAME, f"{store_name}.pkl")):
            with open(os.path.join(DIR_NAME, f"{store_name}.pkl"), "rb") as f:
                documents = pickle.load(f)
            st.write("Already, Embeddings loaded from the your folder (disks)")
        else:
            if not os.path.exists(os.path.join(DIR_NAME, f"{store_name}.pkl")):
                pdf_path = translate_pdf(pdf.name, DIR_NAME, translate=(doc_lang == "Hebrew"))
                loader = PyPDFLoader(pdf_path)
                documents = loader.load()
                text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                documents = text_splitter.split_documents(documents)

                with open(os.path.join(DIR_NAME, f"{store_name}.pkl"), "wb") as f:
                    pickle.dump(documents, f)

        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(documents, embeddings)
        text = st.text_input("Your message: ", key="user_input")
        if len(text):
            user_input = GoogleTranslator(source='auto', target='en').translate(text)
            qa = ConversationalRetrievalChain.from_llm(llm, vectorstore.as_retriever())

            if os.path.exists(os.path.join(DIR_NAME, f"{store_name}_history.pkl")):
                with open(os.path.join(DIR_NAME, f"{store_name}_history.pkl"), "rb") as f:
                    chat_history = pickle.load(f)
                    print(chat_history)
                st.write("Already, Embeddings loaded from the your folder (disks)")
            else:
                chat_history = []

            # handle user input
            if user_input:
                st.session_state.messages.append(HumanMessage(content=text))
                # docs = vectorstore.similarity_search(query=user_input, k=3)
                with st.spinner("Thinking..."):
                    with get_openai_callback() as cb:
                        resp = qa({'question': user_input, "chat_history": chat_history})['answer']
                        response = GoogleTranslator(source='auto', target='iw').translate(resp)
                        print(cb)
                st.session_state.messages.append(
                    AIMessage(content=response))
                chat_history.append((tr(text), resp))

                with open(os.path.join(DIR_NAME, f"{store_name}_history.pkl"), "wb") as f:
                    pickle.dump(chat_history, f)

        # display message history
        messages = st.session_state.get('messages', [])
        for i, msg in enumerate(messages[1:]):
            if i % 2 == 0:
                message(msg.content, is_user=True, key=str(i) + '_user')
            else:
                message(msg.content, is_user=False, key=str(i) + '_ai')


if __name__ == "__main__":
    main()
