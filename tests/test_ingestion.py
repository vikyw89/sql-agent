def test_load_and_persist_object_index():
    from sqlagent.ingestions.load_and_persist_object_index import arun

    import asyncio
    import os
    asyncio.run(arun(db_url=os.getenv("DATABASE_URL",""), api_key=os.getenv("OPENAI_API_KEY",""),object_index_dir="./object_index", model="gpt-3.5-turbo"))