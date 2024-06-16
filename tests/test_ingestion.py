import os
import asyncio

from llama_index.core import SQLDatabase
from pinecone import Pinecone
from sqlalchemy.engine import create_engine



def test_load_and_persist_object_index():
    from sqlagent.agent import SQLAgent

    agent = SQLAgent(db_url=os.getenv("DATABASE_URL",""), api_key=os.getenv("OPENAI_API_KEY",""),object_index_dir="./object_index", model="gpt-3.5-turbo")


def test_load_and_persist_table_index():
    from sqlagent.ingestions import load_and_persist_tables_row
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY",""), host=os.getenv("PINECONE_HOST",""))
    pc_index = pc.Index(host=os.getenv("PINECONE_HOST",""))
    pc_index.delete(delete_all=True, namespace="ca_change_name")
    pc_index.delete(delete_all=True, namespace="ca_delisting")
    pc_index.delete(delete_all=True, namespace="table_index_dir")
    
    engine = create_engine(url=os.getenv("DATABASE_URL",""), pool_recycle=3600, echo=True)
    sql_database = SQLDatabase(
        engine=engine,
        ignore_tables=["admin", "admin_block", "api_key", "refresh_token"],
    )
    vector_store_dict = asyncio.run(load_and_persist_tables_row.arun(sql_database=sql_database))

    print(vector_store_dict)

