# Langchain API Sample

## Steps

1. Add environment
````bash
vi .env 

cat > .env  << EOF
export OPENAI_API_KEY=
export AZURE_ENDPOINT="https://ad-openai-instance.openai.azure.com/"
export OPENAI_API_TYPE=azure
export OPENAI_API_VERSION=2023-05-15
EOF
````

2. Activate the virtual environment

````bash
python -m venv venv
source venv/bin/activate
````
3. Required packages

````bash
pip install -U pip langchain-cli poetry
````

4. Initialize a LangChain project

````bash
langchain app new .
poetry add "langserve[all]" langchain-openai python-decouple
````

## Run

````bash 
export OPENAI_API_KEY=
export AZURE_ENDPOINT="https://ad-openai-instance.openai.azure.com/"
export OPENAI_API_TYPE=azure
export OPENAI_API_VERSION=2023-05-15

streamlit run chatbot.py
````

## Reference

[Koyeb Deployment](https://www.koyeb.com/tutorials/using-langserve-to-build-rest-apis-for-langchain-applications)

