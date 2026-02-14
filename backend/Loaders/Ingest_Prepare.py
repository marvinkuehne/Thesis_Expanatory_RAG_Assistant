import os
from dotenv import load_dotenv
from langchain_community.document_loaders import (PyMuPDFLoader, TextLoader, UnstructuredWordDocumentLoader, UnstructuredPowerPointLoader, UnstructuredExcelLoader,)
from azure.storage.blob import BlobServiceClient
from langchain_experimental.text_splitter import SemanticChunker
import tempfile
from services.Create_Embedder import make_azure_langchain_embedder



load_dotenv()

# 1) call container
blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_CONNECTION_STRING'))  # create connection to Storage
upload_container = "docs"
upload_container_client = blob_service_client.get_container_client(upload_container)  # enter upload container


# 2) Load blobs
def load_docs(blob_names: list[str] | None = None):
    # FALLBACK: wenn nichts übergeben wurde, alle Blobs nehmen
    if blob_names is None:
        blob_names = [b.name for b in upload_container_client.list_blobs()]

    docs = []

    #1) extract filename from each blob object
    for blob_name in blob_names:
        filename = os.path.basename(blob_name)
        ext = os.path.splitext(filename)[1].lower()
        print(filename)

        # 2) check filetypes

        if ext not in [".pdf", ".txt", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx"]:
            print(f"Skipping unsupported file: {filename}")
            continue

        # 2) Download bytes from blob storage (use blob_name)
        blob_client = upload_container_client.get_blob_client(blob_name)
        data = blob_client.download_blob().readall()

        # 3) Store bytes as temporary files on disk (necessary as PyMuPdf etc. exppect file and not bytes)
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(data)
            tmp_path = tmp.name

        try:
            # 4) select right loader
            if ext == ".pdf":
                loader = PyMuPDFLoader(tmp_path)
            elif ext == ".txt":
                loader = TextLoader(tmp_path, encoding="utf-8")
            elif ext in [".doc", ".docx"]:
                loader = UnstructuredWordDocumentLoader(tmp_path)
            elif ext in [".ppt", ".pptx"]:
                loader = UnstructuredPowerPointLoader(tmp_path)
            elif ext in [".xls", ".xlsx"]:
                loader = UnstructuredExcelLoader(tmp_path)
            else:
                continue

            pages = loader.load()
            for p in pages:
                p.metadata["source"] = blob_name
            docs.extend(pages)
            print(f"Loaded: {filename} -> {len(pages)} docs/pages")

        finally:
            os.remove(tmp_path)

    return docs



# 3) Chunking
def split_documents_semantic(docs):
    embedder = make_azure_langchain_embedder()

    splitter = SemanticChunker(
        embedder,
        breakpoint_threshold_type="percentile"
    )

    chunks = splitter.split_documents(docs)

    return chunks



# 4) append chunks with ids
def create_ids(chunks):
    prev_source = None
    id_counter = 0

    for chunk in chunks:
        source_blob = chunk.metadata.get("source", "unknown")
        filename = os.path.basename(source_blob)
        page = chunk.metadata.get("page", 0)

        if source_blob != prev_source:
            prev_source = source_blob
            id_counter = 0

        safe_filename = filename.replace(".", "_") # azure accepts no "."
        chunk_id = f"{safe_filename}-{page}-{id_counter}"
        chunk.metadata["id"] = chunk_id
        id_counter += 1

    return chunks

