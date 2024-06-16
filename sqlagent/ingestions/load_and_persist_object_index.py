import asyncio
import os

from pydantic import BaseModel, Field
from sqlalchemy import (
    create_engine,
)
from llama_index.core import SQLDatabase
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llmtext.llms.openai import OpenAILLM, AsyncOpenAI


class TableInfo(BaseModel):
    """Information regarding a structured table."""

    table_name: str = Field(
        description="table name (must be underscores and NO spaces)"
    )
    table_summary: str = Field(
        description="short, concise summary/caption of the table in business perspective"
    )


async def aextract_table_info(
    sql_database: SQLDatabase,
    api_key: str = os.getenv("OPENAI_API_KEY", ""),
    model: str = "gpt-3.5-turbo",
) -> list[TableInfo]:
    tables = sql_database.get_usable_table_names()

    llm = OpenAILLM(client=AsyncOpenAI(api_key=api_key),model=model)

    gather = []
    for table in tables:
        # retrieve table schema
        schema = sql_database.get_single_table_info(table_name=table)
        dialect = sql_database.dialect
        data = sql_database.run_sql(
            f"""SELECT *
FROM {table}
LIMIT 3;"""
        )
        prompt = f"""Let's think step by step.
Create a summary of the table 
{table}

Database is in dialect 
{dialect}

Here's the schema
{schema}

Here's the sample data
{data}
"""

        gather.append(llm.astructured_extraction(text=prompt, output_class=TableInfo))
    table_infos = await asyncio.gather(*gather)
    return table_infos


async def arun(
    db_url: str,
    api_key: str,
    model: str = "gpt-3.5-turbo",
    object_index_dir: str = "./object_index",
) -> ObjectIndex:
    engine = create_engine(url=db_url, pool_recycle=3600, echo=True)

    sql_database = SQLDatabase(
        engine,
        ignore_tables=["admin", "admin_block", "api_key", "refresh_token"],
    )

    print("creating table node mapping")
    table_node_mapping = SQLTableNodeMapping(sql_database)
    # create index if it doesn't exist yet
    try:
        # load object index
        print("loading object index")
        obj_index = ObjectIndex.from_persist_dir(persist_dir=object_index_dir, object_node_mapping=table_node_mapping)

        return obj_index
    except Exception:
        print("object index not found, creating new one")
        pass

    print("creating new object index")


    print("extracting table info")
    table_infos = await aextract_table_info(
        sql_database=sql_database, api_key=api_key, model=model
    )

    print("creating table schema objects")
    table_schema_objs = [
        SQLTableSchema(table_name=t.table_name, context_str=t.table_summary)
        for t in table_infos
    ]

    print("persisting object index")
    # create object index only if it doesn't exist yet
    obj_index = ObjectIndex.from_objects(table_schema_objs, table_node_mapping)
    obj_index.persist(persist_dir=object_index_dir, obj_node_mapping_fname=object_index_dir)

    return obj_index
