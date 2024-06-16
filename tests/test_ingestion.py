import os
import asyncio

from llama_index.core import SQLDatabase
from pinecone import Pinecone
from sqlalchemy.engine import create_engine



def test_load_and_persist_object_index():
    from sqlagent.agent import SQLAgent

    agent = SQLAgent()

def test_delete_all_namespace():
    from sqlagent.ingestions import load_and_persist_tables_row
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY",""), host=os.getenv("PINECONE_HOST",""))
    pc_index = pc.Index(host=os.getenv("PINECONE_HOST",""))
    namespaces = pc_index.describe_index_stats()["namespaces"]
    for namespace in namespaces:
        pc_index.delete(delete_all=True, namespace=namespace)

    
    # engine = create_engine(url=os.getenv("DATABASE_URL",""), pool_recycle=3600, echo=True)
    # sql_database = SQLDatabase(
    #     engine=engine,
    #     ignore_tables=["admin", "admin_block", "api_key", "refresh_token"],
    # )
    # vector_store_dict = asyncio.run(load_and_persist_tables_row.arun(sql_database=sql_database))


