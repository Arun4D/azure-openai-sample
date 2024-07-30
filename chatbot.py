import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import AzureChatOpenAI

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
AZURE_ENDPOINT = os.environ['AZURE_ENDPOINT']
OPENAI_API_TYPE = os.environ['OPENAI_API_TYPE']
OPENAI_API_VERSION = os.environ['OPENAI_API_VERSION']
# upload a file
st.header("Ad Chatbot")

with st.sidebar:
    st.title("Upload Documents")
    file = st.file_uploader("Upload a pdf file and ask question", type="pdf")

if file is not None:
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
        # st.write(text)
# chunks
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n"],
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )
    chunk = text_splitter.split_text(text)
    # st.write(chunk)

    # generating embeddings
    # embeddings = AzureOpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    embeddings = AzureOpenAIEmbeddings(
        model="text-embedding-ada-002",
        deployment="ad-openai-text-emb-deployment",
        azure_endpoint=AZURE_ENDPOINT,
        openai_api_key=OPENAI_API_KEY,
        openai_api_type=OPENAI_API_TYPE,
        openai_api_version=OPENAI_API_VERSION,
        chunk_size=1000
    )

    # Create vector store - FAISS
    vector_store = FAISS.from_texts(chunk, embeddings)

    # user question
    user_question = st.text_input("Your question here")

    # do search
    if user_question:
        match = vector_store.similarity_search(user_question)
        # st.write(match)

        # Define the llm
        llm = AzureChatOpenAI(
            model="gpt-35-turbo",
            deployment_name="ad-openai-deployment",
            azure_endpoint=AZURE_ENDPOINT,
            openai_api_key=OPENAI_API_KEY,
            openai_api_type=OPENAI_API_TYPE,
            openai_api_version=OPENAI_API_VERSION
        )

        # output
        chain = load_qa_chain(llm, chain_type="stuff")
        response = chain.run(input_documents=match, question=user_question)
        st.write(response)
