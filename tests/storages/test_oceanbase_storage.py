from camel.embeddings import SentenceTransformerEncoder
from camel.storages.vectordb_storages import (
    OceanBaseStorage,
    VectorDBQuery,
    VectorRecord,
)
from camel.retrievers import VectorRetriever

embed_model = SentenceTransformerEncoder(model_name="")
ob_storage = OceanBaseStorage(
    vector_dim=embed_model.get_output_dim(),
    table_name="",
    uri="",
    user=",
    password="",
    db_name="",
    distance="",
)

status = ob_storage.status()
print(f"Vector dimension: {status.vector_dim}")
print(f"Initial vector count: {status.vector_count}")


vr = VectorRetriever(
    embedding_model=embed_model,
    storage=ob_storage,
)

q_vec = embed_model.embed("cafe")
results = ob_storage.query(VectorDBQuery(query_vector=q_vec, top_k=10))

print([res.record.payload['metadata']['business_id'] for res in results])
print([res.record.payload['metadata']['business_name'] for res in results])
print([res.record.payload['metadata']['business_name'] for res in results if res.record.payload['metadata']['business_id'] != 0])
# print([res.similarity for res in results])
# print(results[0])

print("===================================================")

results = vr.query(query="cafe", similarity_threshold=0.2, top_k=10)
print([res['metadata']['business_id'] for res in results])
print([res['metadata']['business_name'] for res in results])
print([res['metadata']['business_name'] for res in results if res['metadata']['business_id'] != 0])

"""
result_dict = {
    'similarity score': str(result.similarity),
    'content path': result.record.payload.get(
        'content path', ''
    ),
    'metadata': result.record.payload.get('metadata', {}),
    'extra_info': result.record.payload.get('extra_info', {}),
    'text': result.record.payload.get('text', ''),
}

如果通过 VectorRetriever 进行查询操作，需要预先在 VectorRecord 中设置好 metadata 字段的内容。

"""
