import os
from langchain_openai import AzureOpenAIEmbeddings

def make_azure_langchain_embedder():
    global _EMBEDDER

    _EMBEDDER = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
    return _EMBEDDER