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
from llama_index.core.llms import ChatResponse


class SQLAgent:
    def __init__(
        self,
        db_url: str = os.getenv("DATABASE_URL", ""),
        api_key: str = os.getenv("OPENAI_API_KEY", ""),
        model: str = "gpt-3.5-turbo",
        fallback_model: str = "gpt-4o",
        embedding_model: str = "text-embedding-ada-002",
        pinecone_api_key: str = os.getenv("PINECONE_API_KEY", ""),
        pinecone_host: str = os.getenv("PINECONE_HOST", ""),
        pinecone_namespace: str = os.getenv("PINECONE_NAMESPACE", "default"),
        object_index_dir: str = "./object_index",
    ):
        self.db_url = db_url
        self.api_key = api_key
        self.model = model
        self.embedding_model = embedding_model
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_host = pinecone_host
        self.pinecone_namespace = pinecone_namespace
        self.object_index_dir = object_index_dir
        self.fallback_model = fallback_model
        self.llm = OpenAI(model=self.model, api_key=self.api_key)
        self.engine = create_engine(url=self.db_url, pool_recycle=3600, echo=True)
        self.sql_database = SQLDatabase(
            engine=self.engine,
            ignore_tables=["admin", "admin_block", "api_key", "refresh_token"],
        )
        self.table_node_mapping = SQLTableNodeMapping(self.sql_database)
        self.sql_retriever = SQLRetriever(self.sql_database)
        self.table_parser_component = FnComponent(fn=self._get_table_context_str)

    async def ingest_db(self) -> ObjectIndex:
        from sqlagent.ingestions.load_and_persist_object_index import arun

        return await arun(
            db_url=self.db_url,
            api_key=self.api_key,
            object_index_dir=self.object_index_dir,
            model=self.model,
        )

    def _get_table_context_str(self, table_schema_objs: list[SQLTableSchema]):
        """Get table context string."""
        context_strs = []
        for table_schema_obj in table_schema_objs:
            table_info = self.sql_database.get_single_table_info(
                table_schema_obj.table_name
            )
            if table_schema_obj.context_str:
                table_opt_context = " The table description is: "
                table_opt_context += table_schema_obj.context_str
                table_info += table_opt_context

            context_strs.append(table_info)
        return "\n\n".join(context_strs)

    async def arun(self, query: str):
        obj_index = None
        try:
            obj_index = ObjectIndex.from_persist_dir(
                persist_dir=self.object_index_dir,
                object_node_mapping=self.table_node_mapping,
            )
        except Exception as e:
            print(e)
            obj_index = await self.ingest_db()
            
        obj_retriever = obj_index.as_retriever(similarity_top_k=3)

        # TEXT TO SQL
        text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
            dialect=self.engine.dialect.name
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

        # PIPELINE
        qp = QP(
            modules={
                "input": InputComponent(),
                "table_retriever": obj_retriever,
                "table_output_parser": self.table_parser_component,
                "text2sql_prompt": text2sql_prompt,
                "text2sql_llm": self.llm,
                "sql_output_parser": sql_parser_component,
                "sql_retriever": self.sql_retriever,
                "response_synthesis_prompt": response_synthesis_prompt,
                "response_synthesis_llm": self.llm,
            },
            verbose=True,
        )
        qp.add_chain(["input", "table_retriever", "table_output_parser"])
        qp.add_link("input", "text2sql_prompt", dest_key="query_str")
        qp.add_link("table_output_parser", "text2sql_prompt", dest_key="schema")
        qp.add_chain(
            ["text2sql_prompt", "text2sql_llm", "sql_output_parser", "sql_retriever"]
        )
        qp.add_link(
            "sql_output_parser", "response_synthesis_prompt", dest_key="sql_query"
        )
        qp.add_link(
            "sql_retriever", "response_synthesis_prompt", dest_key="context_str"
        )
        qp.add_link("input", "response_synthesis_prompt", dest_key="query_str")
        qp.add_link("response_synthesis_prompt", "response_synthesis_llm")

        try:
            response: ChatResponse = qp.run(query=query)
            return str(response.message.content) if response.message is not None else ""
        except Exception:
            # try again once with gpt 4o
            self.llm = OpenAI(model="gpt-4o", api_key=self.api_key)
            response: ChatResponse = qp.run(query=query)
            return str(response.message.content) if response.message is not None else ""
