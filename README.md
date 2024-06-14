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
pip install sql-agent-library
```

## Usage

Here's a quick example to get you started:

### Step 1: Import the Library

```python
from sql_agent_library import SQLAgent
```

### Step 2: Initialize the Agent

```python
# Create an instance of the SQLAgent
agent = SQLAgent(db_connection_string="your_database_connection_string")
```

### Step 3: Query the Database

```python
# Input: Describe your query in natural language
human_language_query = "Get the names and email addresses of all users who registered last month."

# Output: Get the query result
result = agent.query(human_language_query)

# Print the result
print(result)
```

## Configuration

You can configure the SQL Agent Library to connect to your specific database by providing the appropriate connection string during initialization.

```python
agent = SQLAgent(db_connection_string="mysql://username:password@host:port/database")
```

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