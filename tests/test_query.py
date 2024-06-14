

def test_query():
    from sqlagent.agent import arun

    import asyncio
    try:
        res = asyncio.run(arun(query="show tables"))
        print(res)
    except Exception as e:
        print(str(e))