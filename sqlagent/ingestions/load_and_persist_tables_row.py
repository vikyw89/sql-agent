from llama_index.core import SQLDatabase, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
from sqlalchemy import text
from llama_index.core.schema import TextNode
from llama_index.core.storage import StorageContext
import os
from typing import Dict


async def arun(
    max_row_index: int | None,
    sql_database: SQLDatabase,
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", ""),
    embedding_model=OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL,
    pinecone_host: str = os.getenv("PINECONE_HOST", ""),
    openai_api_key: str = os.getenv("OPENAI_API_KEY", ""),
) -> Dict[str, VectorStoreIndex]:
    """Index all tables."""
    embedding_model = OpenAIEmbedding(api_key=openai_api_key, model=embedding_model)
    pc = Pinecone(api_key=pinecone_api_key, host=pinecone_host)
    pc_index = pc.Index(host=pinecone_host)
    stats = pc_index.describe_index_stats()
    indexed_tables = stats["namespaces"].keys()

    vector_index_dict = {}
    engine = sql_database.engine
    for table_name in sql_database.get_usable_table_names():
        # create pinecone vector store, using namespace as table name
        pinecone_vector_store = PineconeVectorStore(
            pinecone_index=pc_index, namespace=table_name
        )
        # use pinecone store to save and load
        storage_context = StorageContext.from_defaults(
            vector_store=pinecone_vector_store,
        )
        print(f"Indexing rows in table: {table_name}")
        # if table index exist in namespace, skip
        if table_name in indexed_tables:
            print(f"Table {table_name} already indexed. Skipping.")
            vector_index_dict[table_name] = VectorStoreIndex.from_vector_store(
                vector_store=pinecone_vector_store, embed_model=embedding_model
            )
            continue

        # start indexing and generate embeddings
        with engine.connect() as conn:
            limit = f"LIMIT {max_row_index}" if max_row_index else ""
            cursor = conn.execute(text(f"""SELECT * FROM {table_name} {limit}"""))
            result = cursor.fetchall()
            row_tups = []
            for row in result:
                row_tups.append(tuple(row))

        # index each row, put into vector store index
        nodes = [
            TextNode(text=str(t), id_=f"{table_name}{str(t[0])}") for t in row_tups
        ]

        # put into vector store index (use OpenAIEmbeddings by default)
        index = VectorStoreIndex(
            nodes=nodes,
            storage_context=storage_context,
            show_progress=True,
            embed_model=embedding_model,
        )

        # construct a dict of table name and index
        vector_index_dict[table_name] = index

    return vector_index_dict
