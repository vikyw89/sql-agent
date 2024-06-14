

import os


def test_query():
    from sqlagent.agent import arun

    import asyncio
    try:
        res = asyncio.run(arun(query="show tables", api_key=os.getenv("OPENAI_API_KEY",""), model="gpt-3.5-turbo",db_url=os.getenv("DATABASE_URL","")))
        print(res)
    except Exception as e:
        print(str(e))