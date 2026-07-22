from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    SparseVectorParams,
    SparseIndexParams,
)
from config.settings import QDRANT_HOST, QDRANT_PORT, QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION

if QDRANT_URL:
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
else:
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

_collection_created = False


def ensure_collection():
    global _collection_created
    if _collection_created:
        return
    collections = [c.name for c in client.get_collections().collections]
    if QDRANT_COLLECTION in collections:
        try:
            client.get_collection(QDRANT_COLLECTION)
            _collection_created = True
            return
        except Exception:
            client.delete_collection(QDRANT_COLLECTION)

    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config={
            "text-dense-vector": VectorParams(size=3072, distance=Distance.COSINE),
        },
        sparse_vectors_config={
            "text-sparse-vector": SparseVectorParams(
                index=SparseIndexParams(on_disk=False),
            ),
        },
    )
    _collection_created = True


def upsert_vectors(vectors: list[PointStruct]):
    ensure_collection()
    client.upsert(collection_name=QDRANT_COLLECTION, points=vectors)


def search(query_vector: list[float], limit: int = 5):
    ensure_collection()
    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        using="text-dense-vector",
        limit=limit,
        with_payload=True,
    )
    return results.points


def search_hybrid(query_vector: list[float], sparse_vector: list[int], limit: int = 5):
    ensure_collection()
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    
    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=[
            (
                "text-dense-vector",
                query_vector,
            ),
            (
                "text-sparse-vector",
                sparse_vector,
            ),
        ],
        limit=limit,
        with_payload=True,
    )
    return results.points


def search_by_category(query_vector: list[float], category: str, limit: int = 5):
    ensure_collection()
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    
    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        using="text-dense-vector",
        limit=limit,
        with_payload=True,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="category",
                    match=MatchValue(value=category)
                )
            ]
        ),
    )
    return results.points
