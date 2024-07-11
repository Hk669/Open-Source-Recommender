from openai import AzureOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = AzureOpenAI(
    api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version = "2024-02-01",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
)

def generate_embeddings(text, model="text-embedding-3-small"):
    """Generate embeddings for the given text using the specified model"""
    return client.embeddings.create(input = [text], model=model).data[0].embedding

