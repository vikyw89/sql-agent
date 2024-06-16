import os

from pinecone import Pinecone



def test_load_and_persist_object_index():
    from sqlagent.agent import SQLAgent

    SQLAgent()

# def test_delete_all_namespace():
#     pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY",""), host=os.getenv("PINECONE_HOST",""))
#     pc_index = pc.Index(host=os.getenv("PINECONE_HOST",""))
#     namespaces = pc_index.describe_index_stats()["namespaces"]
#     for namespace in namespaces:
#         pc_index.delete(delete_all=True, namespace=namespace)


