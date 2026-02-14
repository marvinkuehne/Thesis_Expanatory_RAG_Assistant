
def update_category_for_file(search_client, user_id: str, source_blob: str, category: str | None):
    results = search_client.search(
        search_text="*",
        filter=f"user_id eq '{user_id}' and source eq '{source_blob}'",
        select=["id"],
        top=1000
    )
    docs = [{"id": r["id"], "category": category} for r in results]
    if docs:
        search_client.merge_or_upload_documents(documents=docs)


