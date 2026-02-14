# Load switcher: Decides where Data (blobs) send to

from enum import Enum
from Loaders.Chroma_Loader import add_to_chroma, get_embedding_azure
from Loaders.Azure_Loader import build_search_docs, upsert_docs
from Loaders.Ingest_Prepare import  load_docs, split_documents_semantic, create_ids

# Defines allowed values for Target (prevent typos)


class Target(str, Enum):
    AZURE = "azure"
    CHROMA = "chroma"


def ingest(blob_names: list[str], target: Target = Target.CHROMA):
    if target == Target.AZURE:
        return ingest_to_azure_search(blob_names) # A) Azure Writer
    if target == Target.CHROMA:
        return ingest_to_chroma(blob_names) # B) Chroma Writer
    raise ValueError(f"Unknown target: {target}")


# A) Azure Loader
def ingest_to_azure_search(blob_names: list[str] | None = None):
    chunks = ingest_prepare(blob_names)
    vectors = get_embedding_azure(chunks)
    search_docs = build_search_docs(chunks, vectors)
    upsert_docs(search_docs)
    return {"chunks": len(chunks), "uploaded": len(search_docs)}


# B) Chroma Loader
def ingest_to_chroma(blob_names: list[str] | None = None):
    chunks = ingest_prepare(blob_names)
    vs = add_to_chroma(chunks)
    return {"chunks": len(chunks), "chroma_count": vs._collection.count()}


# Helper function - shared part
def ingest_prepare(blob_names: list[str] | None = None):
    docs = load_docs(blob_names)
    chunks = split_documents_semantic(docs)
    ids = create_ids(chunks)

    return ids