from llama_index.core.llms import ChatResponse
from llama_index.core.query_pipeline import FnComponent


def parse_response_to_sql(res: ChatResponse) -> str:
    """Parse response to SQL."""
    if res.message is None:
        return ""
    if res.message.content is None:
        return ""
    response = str(res.message.content)
    sql_query_start = response.find("SQLQuery:")
    if sql_query_start != -1:
        response = response[sql_query_start:]
        # TODO: move to removeprefix after Python 3.9+
        if response.startswith("SQLQuery:"):
            response = response[len("SQLQuery:") :]
    sql_result_start = response.find("SQLResult:")
    if sql_result_start != -1:
        response = response[:sql_result_start]
    return response.strip().strip("```").strip("sql").strip("\n").strip()


sql_parser_component = FnComponent(fn=parse_response_to_sql)
