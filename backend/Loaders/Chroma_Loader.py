import os
from langchain_chroma import Chroma
from services.Create_Embedder import make_azure_langchain_embedder




def get_embedding_azure(chunks):
    texts = [c.page_content for c in chunks]
    embedder = make_azure_langchain_embedder()
    vectors = embedder.embed_documents(texts)  # list[list[float]]
    return vectors

# Embeddings Chroma + add to chroma
BASE_DIR = os.path.dirname(__file__)
PERSIST_DIR = os.path.join(BASE_DIR, "db", "chroma")
COLLECTION = "rag-chroma"

def _open_chroma():
    return Chroma(
        embedding_function=make_azure_langchain_embedder(),
        persist_directory=PERSIST_DIR,
        collection_name=COLLECTION,
    )

def add_to_chroma(chunks):
    #create/open chroma DB
    vectorstore = _open_chroma()


    # check duplicates
    existing_ids_list = vectorstore.get(include=[])  # extract ids via include[]
    existing_ids_hashset = set(
        existing_ids_list["ids"])  # convert existing_ids_list into hashset for quicker search wihtin DB

    new_chunks = []
    new_chunk_ids = []

    for chunk in chunks:
        chunk_id = chunk.metadata["id"]  # retrieve id field in metadata

        if chunk_id not in existing_ids_hashset:
            new_chunks.append(chunk)  # store unique chunk in new_chunks list
            new_chunk_ids.append(chunk_id)

    if new_chunks:
        print(f"👉 Adding new documents: {len(new_chunks)}")

        # Create slot "chunks" and "ids" in vectorstore and add only chunks with new ids
        vectorstore.add_documents(documents=new_chunks, ids=new_chunk_ids)
    else:
        print("No new chunks to add.")

    print("chroma count:", vectorstore._collection.count())
    # print("IDS: ", vectorstore._collection.get())

    return vectorstore


# Delete
def delete_from_chroma_for_file(source_blob: str):
    vs = _open_chroma()
    # du setzt bei load_docs: p.metadata["source"] = blob_name
    vs._collection.delete(where={"source": {"$eq": source_blob}})