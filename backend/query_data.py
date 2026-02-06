import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import OpenAI


def query_rag(query: str, categories: list[str] | None = None):
    # --- Azure Search client ---
    search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_INDEX"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_ADMIN_KEY")),
    )

    # --- Azure OpenAI v1 client (Foundry) ---
    # IMPORTANT: base_url must end with /openai/v1/
    base_url = os.getenv("AZURE_OPENAI_ENDPOINT").rstrip("/") + "/openai/v1/"

    client = OpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        base_url=base_url,
    )

    embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
    chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

    # --- 1) embed query ---
    q_emb = client.embeddings.create(
        model=embedding_deployment,   # deployment name!
        input=[query],
    ).data[0].embedding

    # --- 2) optional category filter ---
    cats = [c.strip() for c in (categories or []) if c and c.strip()]
    odata_filter = None
    if cats:
        cat_filter = " or ".join([f"category eq '{c}'" for c in cats])
        odata_filter = f"({cat_filter})"

    # --- 3) retrieve from Azure AI Search ---
    vector_query = VectorizedQuery(
        vector=q_emb,
        k_nearest_neighbors=6,
        fields="embedding"
    )

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        filter=odata_filter,
        top=6,
        select=["chunk", "source", "page", "id", "category"],
    )

    # --- 4) build context ---
    context_parts = []
    sources = []
    for i, doc in enumerate(results, start=1):
        src = (doc.get("source") or "unknown")
        page = doc.get("page") or 0
        chunk = (doc.get("chunk") or "").strip()
        if not chunk:
            continue
        context_parts.append(f"[{i}] From {src} (page {page}):\n{chunk}")
        sources.append(f"{src}:p{page}")

    context = "\n\n---\n\n".join(context_parts)[:12000]

    # --- 5) generate answer (Responses API) ---
    system = (
        "You are a helpful assistant. Use only the provided excerpts to answer. "
        "If the excerpts don't contain the answer, say so briefly."
    )

    user_msg = f"EXCERPTS:\n{context}\n\nQUESTION:\n{query}"

    resp = client.responses.create(
        model=chat_deployment,  # deployment name!
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
        max_output_tokens=600,
    )

    # responses API text extraction:
    answer = resp.output_text
    return answer, sources