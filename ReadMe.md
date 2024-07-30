# Azure Open AI Sample

## Required packages

````bash
pip install streamlit pypdf2 langchain faiss-cpu langchain-community openai tiktoken langchain-openai
````

## Run

````bash 
export OPENAI_API_KEY=
export AZURE_ENDPOINT="https://ad-openai-instance.openai.azure.com/"
export OPENAI_API_TYPE=azure
export OPENAI_API_VERSION=2023-05-15

streamlit run chatbot.py
````

