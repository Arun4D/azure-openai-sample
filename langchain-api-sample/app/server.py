# app/server.py
import re
from decouple import config
from fastapi import FastAPI
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langserve import add_routes
from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

class TestScenario(BaseModel):
    text: str

class GeneratedTestResult(BaseModel):
    feature: str
    stepConfig: str
    stepDefinitions: str
    rawData: str

class UserDetailsRawRequest(BaseModel):
    text: str

class UserDetailsRawResponse(BaseModel):
    text: str

class AddressDetail(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
class UserDetails(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[AddressDetail] = Field(default=None, description="Address details")

# Step 3: Extract code snippets
def extract_code_snippets(response_text):
    code_snippets = []
    in_code_block = False
    current_snippet = []

    lines = response_text.split('\n')

    for line in lines:
        line = line.strip()  # Clean up the line
        if line.startswith('```'):
            if in_code_block:
                # End of code block
                code_snippets.append('\n'.join(current_snippet))
                current_snippet = []
            in_code_block = not in_code_block
        elif in_code_block:
            current_snippet.append(line)

    # Handle the case where the response ends with a code block
    if in_code_block:
        code_snippets.append('\n'.join(current_snippet))

    return code_snippets

# Function to extract Java class names from code snippets
def extract_java_class_names(snippet):
    class_names = []
    
    # Regular expression to match Java class declarations
    class_pattern = re.compile(r'\bclass\s+(\w+)\b')
    
    for l_snippet in snippet:
        matches = class_pattern.findall(l_snippet)
        class_names.extend(matches)
    
    return class_names

# Function to extract Feature from code snippets
def extract_feature_names(snippet):
    feature_names = []
    
    # Regular expression to match the 'Feature' line
    feature_pattern = re.compile(r'^\s*Feature:\s*(.+)', re.MULTILINE)
    
    for l_snippet in snippet:
        matches = feature_pattern.findall(l_snippet)
        feature_names.extend(matches)
    
    return feature_names

app = FastAPI()

#model = ChatOpenAI(openai_api_key=config("OPENAI_API_KEY"))
model = AzureChatOpenAI(
        model="gpt-35-turbo-16k",
        deployment_name="gpt-35-turbo-16k",
        azure_endpoint=config("AZURE_ENDPOINT"),
        openai_api_key=config("OPENAI_API_KEY"),
        openai_api_type=config("OPENAI_API_TYPE"),
        openai_api_version=config("OPENAI_API_VERSION")
    )

prompt = ChatPromptTemplate.from_template("generate test scenarios like '{topic}' for behavior driven development (BDD)  with java code and all input values need to be in config class.  display only feature file and java step file  and java config file")
chain = prompt | model

#add_routes(app, chain, path="/openai")

@app.post("/testscenario/", status_code=201, response_model=GeneratedTestResult)
async def create_test_scenario(testScenario: TestScenario):

    response = chain.invoke(testScenario.text)
    response_text = response.content #response.text if hasattr(response, 'text') else str(response)
    responseData = {
        "feature": "",
        "stepConfig": "",
        "stepDefinitions": "",
        "rawData": response.content
    }

    # Get the code snippets
    code_snippets = extract_code_snippets(response_text)


    # Print the code snippets
    for i, snippet in enumerate(code_snippets, 1):
        if "class" in snippet:
            classNames = extract_java_class_names([snippet])
            if "Step" in classNames[0]:
                responseData['stepDefinitions'] = classNames[0]  +".class"+" >> "+ snippet
            elif "Config" in classNames[0]:
                responseData['stepConfig'] = classNames[0]  +".class"+" >> "+ snippet
            
        elif "Feature:" in snippet:
            featureNames = extract_feature_names([snippet])
            featureName = featureNames[0].replace(" ","") + ".feature"
            responseData['feature'] = featureName +" >> "+ snippet

    generatedTestResult = GeneratedTestResult(**responseData)

    return generatedTestResult


#parser = JsonOutputParser()
parser = PydanticOutputParser(pydantic_object=UserDetails)

prompt1 = PromptTemplate(
    template="Convert the user text to json.\n{format_instructions}\n Text '{query}' to json and fields are address  with line1, line2 , city, district , state and pin code. signature contain firstname, lastname, phonenumber,\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain1 = prompt1 | model | parser


@app.post("/userdetails/", status_code=201)
async def create_test_scenario(userDetailsRaw: UserDetailsRawRequest):
    response = chain1.invoke(userDetailsRaw.text)
    
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000) 