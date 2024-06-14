import os
import asyncio

def test_load_and_persist_object_index():
    from sqlagent.agent import SQLAgent

    agent = SQLAgent(db_url=os.getenv("DATABASE_URL",""), api_key=os.getenv("OPENAI_API_KEY",""),object_index_dir="./object_index", model="gpt-3.5-turbo")
    asyncio.run(agent.ingest_db())