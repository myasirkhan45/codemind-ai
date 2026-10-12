from app.vectorstore.chroma_store import get_embeddings

emb = get_embeddings()
vec = emb.embed_query("hello world")
print("Vector size:", len(vec))