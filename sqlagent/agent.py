from llama_index.core.query_pipeline import (
    QueryPipeline as QP,
    InputComponent,
)
from llama_index.llms.openai import OpenAI
from llama_index.core.prompts import PromptTemplate
import os
from sqlalchemy import (
    create_engine,
)
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
)
from llama_index.core import SQLDatabase
from llama_index.core.retrievers import SQLRetriever
from sqlagent.components.sql_parser_component import sql_parser_component
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core.query_pipeline import FnComponent
from llama_index.core.objects import (
    SQLTableSchema,
)


async def arun(
    query: str,
    db_url: str = os.getenv("DATABASE_URL", ""),
    api_key: str = os.getenv("OPENAI_API_KEY", ""),
    model: str = "gpt-3.5-turbo",
    embedding_model: str = "text-embedding-3-small",
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", ""),
    pinecone_host: str = os.getenv("PINECONE_HOST", ""),
    pinecone_namespace: str = os.getenv("PINECONE_NAMESPACE", "default"),
    object_index_dir: str = "./object_index",
):
    # INIT
    engine = create_engine(url=db_url, pool_recycle=3600, echo=True)

    sql_database = SQLDatabase(
        engine,
        ignore_tables=["admin", "admin_block", "api_key", "refresh_token"],
    )

    table_node_mapping = SQLTableNodeMapping(sql_database)

    def get_table_context_str(table_schema_objs: list[SQLTableSchema]):
        """Get table context string."""
        context_strs = []
        for table_schema_obj in table_schema_objs:
            table_info = sql_database.get_single_table_info(table_schema_obj.table_name)
            if table_schema_obj.context_str:
                table_opt_context = " The table description is: "
                table_opt_context += table_schema_obj.context_str
                table_info += table_opt_context

            context_strs.append(table_info)
        return "\n\n".join(context_strs)

    table_parser_component = FnComponent(fn=get_table_context_str)
    # OBJ RETRIEVER
    # try loading the object index
    obj_index = ObjectIndex.from_persist_dir(
        persist_dir=object_index_dir, object_node_mapping=table_node_mapping
    )
    obj_retriever = obj_index.as_retriever(similarity_top_k=3)

    # SQL RETRIEVER
    sql_retriever = SQLRetriever(sql_database)

    # TEXT TO SQL
    text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
        dialect=engine.dialect.name
    )

    # RESPONSE SYNTHESIS
    response_synthesis_prompt_str = (
        "Given an input question, synthesize a response from the query results.\n"
        "Query: {query_str}\n"
        "SQL: {sql_query}\n"
        "SQL Response: {context_str}\n"
        "Response: "
    )
    response_synthesis_prompt = PromptTemplate(
        response_synthesis_prompt_str,
    )

    # LLM
    llm = OpenAI(model="gpt-3.5-turbo", api_key=api_key)

    # PIPELINE
    qp = QP(
        modules={
            "input": InputComponent(),
            "table_retriever": obj_retriever,
            "table_output_parser": table_parser_component,
            "text2sql_prompt": text2sql_prompt,
            "text2sql_llm": llm,
            "sql_output_parser": sql_parser_component,
            "sql_retriever": sql_retriever,
            "response_synthesis_prompt": response_synthesis_prompt,
            "response_synthesis_llm": llm,
        },
        verbose=True,
    )
    qp.add_chain(["input", "table_retriever", "table_output_parser"])
    qp.add_link("input", "text2sql_prompt", dest_key="query_str")
    qp.add_link("table_output_parser", "text2sql_prompt", dest_key="schema")
    qp.add_chain(
        ["text2sql_prompt", "text2sql_llm", "sql_output_parser", "sql_retriever"]
    )
    qp.add_link("sql_output_parser", "response_synthesis_prompt", dest_key="sql_query")
    qp.add_link("sql_retriever", "response_synthesis_prompt", dest_key="context_str")
    qp.add_link("input", "response_synthesis_prompt", dest_key="query_str")
    qp.add_link("response_synthesis_prompt", "response_synthesis_llm")

    response = qp.run(query=query)

    return response
