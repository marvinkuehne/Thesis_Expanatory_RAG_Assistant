import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
load_dotenv()


# Build search docs
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_ADMIN_KEY"))
)

def build_search_docs(chunks, vectors):
    search_docs = []

    # upload dicts have to equal Azure AI search index
    for c, v in zip(chunks, vectors):
        search_docs.append({
            "id": c.metadata["id"],  # aus create_ids()
            "chunk": c.page_content,
            "source": c.metadata.get("source"),
            "page": c.metadata.get("page", 0),
            "embedding": v,
        })
    return search_docs


# Upload dicts
def upsert_docs(search_docs):
    result = search_client.upload_documents(documents=search_docs)
    print("uploaded:", len(result))
    return result


# Delete
def delete_chunks_for_file(search_client, source_blob: str):
    results = search_client.search(
        search_text="*",
        filter=f"source eq '{source_blob}'",
        select=["id"],
        top=1000,
    )
    ids = [{"id": r["id"]} for r in results]
    if ids:
        search_client.delete_documents(documents=ids)











