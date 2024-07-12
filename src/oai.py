from openai import AzureOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key = os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
    api_version = "2023-09-15-preview",
)

def generate_embeddings(text, model="text-embedding-3-small"):
    """Generate embeddings for the given text using the specified model"""
    return client.embeddings.create(input = [text], model=model).data[0].embedding

if __name__ == "__main__":
    text = "I am a software engineer"
    embeddings = generate_embeddings(text)
    print(embeddings)
