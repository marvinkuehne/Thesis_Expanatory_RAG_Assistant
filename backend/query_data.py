import os
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from langchain_chroma import Chroma

load_dotenv()


from langchain_openai import AzureOpenAIEmbeddings



def make_azure_langchain_embedder():
    global _EMBEDDER

    _EMBEDDER = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
    return _EMBEDDER

#Switcher
def query_rag(
    query: str,
    categories: Optional[List[str]] = None,
    backend: str = "azure",   # "azure" oder "chroma"
) -> Tuple[str, List[str]]:
    backend = (backend or "azure").lower().strip()

    if backend == "azure":
        return query_rag_azure(query, categories)

    if backend == "chroma":
        return query_rag_chroma(query, categories)

    raise ValueError(f"Unknown backend: {backend}")


# -------------------------
# AZURE SEARCH RAG
# -------------------------
def query_rag_azure(
    query: str,
    categories: Optional[List[str]] = None,
) -> Tuple[str, List[str]]:

    # 1) embed query
    embedder = make_azure_langchain_embedder()
    q_emb = embedder.embed_query(query)

    # 2) search client
    search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_INDEX"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_ADMIN_KEY")),
    )

    # 3) optional category filter
    cats = [c.strip() for c in (categories or []) if c and c.strip()]
    odata_filter = None
    if cats:
        # category eq 'A' or category eq 'B'
        odata_filter = "(" + " or ".join([f"category eq '{c}'" for c in cats]) + ")"

    # 4) retrieve
    vector_query = VectorizedQuery(vector=q_emb, k_nearest_neighbors=6, fields="embedding")

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        filter=odata_filter,
        top=6,
        select=["chunk", "source", "page", "category"],
    )

    # 5) build context + sources
    context_parts = []
    sources = []
    for i, doc in enumerate(results, start=1):
        chunk = (doc.get("chunk") or "").strip()
        if not chunk:
            continue
        src = doc.get("source") or "unknown"
        page = doc.get("page") or 0

        context_parts.append(f"[{i}] {src} (page {page}):\n{chunk}")
        sources.append(f"{src}:p{page}")

    context = "\n\n---\n\n".join(context_parts)[:12000]

    # 6) answer with Azure OpenAI
    client = OpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        base_url=os.getenv("AZURE_OPENAI_BASEURL"),  # must end with /openai/v1/
    )

    chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

    resp = client.chat.completions.create(
        model=chat_deployment,
        messages=[
            {"role": "system", "content": "Use only the excerpts to answer. If missing, say you don't know."},
            {"role": "user", "content": f"EXCERPTS:\n{context}\n\nQUESTION:\n{query}"},
        ],
    )
    answer = resp.choices[0].message.content or ""
    return answer, sources


# -------------------------
# CHROMA RAG
# -------------------------
def query_rag_chroma(
    query: str,
    categories: Optional[List[str]] = None,
) -> Tuple[str, List[str]]:

    # 1) open chroma
    base_dir = os.path.dirname(__file__)
    persist_dir = os.path.join(base_dir, "db", "chroma")

    vs = Chroma(
        persist_directory=persist_dir,
        collection_name="rag-chroma",
        embedding_function=make_azure_langchain_embedder(),
    )

    # 2) retrieve
    cats = [c.strip() for c in (categories or []) if c and c.strip()]
    where = {"category": {"$in": cats}} if cats else None

    try:
        results = vs.similarity_search_with_score(query, k=6, filter=where)
    except Exception:
        # falls filter nicht supported ist in deiner version:
        results = vs.similarity_search_with_score(query, k=6)

    # 3) build context + sources
    context_parts = []
    sources = []
    for i, (doc, score) in enumerate(results, start=1):
        chunk = (doc.page_content or "").strip()
        if not chunk:
            continue
        src = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", 0)

        context_parts.append(f"[{i}] {src} (page {page}):\n{chunk}")
        sources.append(f"{src}:p{page}")

    context = "\n\n---\n\n".join(context_parts)[:12000]

    # 4) answer with Azure OpenAI (gleich wie Azure-Backend)
    client = OpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        base_url=os.getenv("AZURE_OPENAI_BASEURL"),
    )
    chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

    resp = client.chat.completions.create(
        model=chat_deployment,
        messages=[
            {"role": "system", "content": "Use only the excerpts to answer. If missing, say you don't know."},
            {"role": "user", "content": f"EXCERPTS:\n{context}\n\nQUESTION:\n{query}"},
        ],
    )
    answer = resp.choices[0].message.content or ""
    return answer, sources