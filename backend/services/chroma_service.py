import os

def update_category(vectorstore, filename: str, new_category: str | None):
    fname = os.path.basename(filename)

    res = vectorstore.get(where={"source": {"$eq": fname}}, include=[])
    ids = res.get("ids", []) or []
    if not ids:
        return {"status": "error", "message": f"No chunks found for {filename}"}

    # 2) Update metadata (keep "source", set/clear "category")
    meta_val = {"category": (new_category or ""), "source": fname}
    vectorstore._collection.update(ids=ids, metadatas=[meta_val] * len(ids))
    try:
        vectorstore._client.persist()
    except Exception as e:
        print("persist warning:", e)

    return {"status": "success", "updated": len(ids), "filename": fname, "new_category": new_category}


