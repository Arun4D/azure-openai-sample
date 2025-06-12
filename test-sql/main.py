from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.agents import initialize_agent
from langchain_community.llms import Ollama

# Connect to your database
db = SQLDatabase.from_uri(
    "mssql+pyodbc://SA:YourStrong%40Passw0rd@localhost:1433/AdventureWorks?driver=ODBC+Driver+17+for+SQL+Server"
)

# LLM from Ollama
# llm = Ollama(model="codellama:7b-instruct")
llm = Ollama(model="phi3")
# Create SQL Agent
agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Run your query
query = "Get me the average monthly salary paid for the last 2 years by department based on the shift"

result = agent_executor.run(query)

print(result)
