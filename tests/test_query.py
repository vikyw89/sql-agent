import asyncio


def test_query():
    from sqlagent.agent import SQLAgent
    agent = SQLAgent(max_db_row_index=1000)
    res = asyncio.run(agent.arun(query="give me toyota motor price"))
    print(res)
    assert isinstance(res, str)
