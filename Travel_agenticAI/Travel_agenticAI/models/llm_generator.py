from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT")
version = os.getenv("AZURE_OPENAI_API_VERSION")

def build_llm() :
    llm = AzureChatOpenAI (
        api_key=key,
        azure_endpoint=endpoint,
        api_version=version,
        deployment_name="gpt-4o",
        temperature=1
    )
    
    return llm