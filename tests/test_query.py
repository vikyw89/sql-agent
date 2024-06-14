import asyncio
import os


def test_query():
    from sqlagent.agent import SQLAgent

    agent = SQLAgent(
        db_url=os.getenv("DATABASE_URL", ""),
        api_key=os.getenv("OPENAI_API_KEY", ""),
        object_index_dir="./object_index",
        model="gpt-3.5-turbo",
    )
    res = asyncio.run(agent.arun(query="give me toyota motor price"))
    print(res)
    assert isinstance(res, str)
