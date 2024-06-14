# SQL Agent Library

## Overview

The SQL Agent Library allows users to interact with SQL databases using natural human language. With this library, users can simply describe what data they want to retrieve or manipulate, and the library will convert these descriptions into precise SQL queries and execute them. This simplifies database interactions for those who may not be familiar with SQL syntax but need to access and manage data.

## Features

- **Natural Language Processing**: Convert human language queries into SQL statements.
- **Database Agnostic**: Works with various SQL databases (MySQL, PostgreSQL, SQLite, etc.).
- **Ease of Use**: Simple input-output mechanism to facilitate quick querying.
- **Flexibility**: Handles a variety of query types including SELECT, INSERT, UPDATE, and DELETE.

## Installation

To install the SQL Agent Library, use pip:

```bash
pip install sqlagent
```

## Usage

Here's a quick example to get you started:

### Step 1: Do ingestion of db

```python
from sqlagent.ingestions import load_and_persist_object_index

await load_and_persist_object_index.arun(db_url=os.getenv("DATABASE_URL",""), api_key=os.getenv("OPENAI_API_KEY",""),object_index_dir="./object_index", model="gpt-3.5-turbo")
```

### Step 2: Initialize the Agent

```python
# Create an instance of the SQLAgent
agent = SQLAgent(db_connection_string="your_database_connection_string")
```

### Step 3: Query the Database

```python
from sqlagent import agent
await agent.arun(query="show tables", api_key=os.getenv("OPENAI_API_KEY",""), model="gpt-3.5-turbo",db_url=os.getenv("DATABASE_URL",""))
```

## Configuration

You can configure the SQL Agent Library to connect to your specific database by providing the appropriate connection string during initialization.
it's utilizing sqlachemy under the hood

## Supported Databases

- MySQL
- PostgreSQL
- SQLite

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

We'd like to thank all contributors and supporters of this project. Your efforts help make database interactions simpler for everyone.

## Contact

For any questions or issues, please open an issue on GitHub or contact us at vikyw89@gmail.com.
