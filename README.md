# SQL2Text: Natural Language to SQL Query Generator

## Introduction

SQL2Text is a tool that translates natural language questions into SQL queries for Microsoft SQL Server databases. It allows users without SQL knowledge to extract insights directly from databases using plain English.

## Features

- **Natural Language to SQL Conversion**: Translate English questions into SQL Server queries
- **Dynamic Schema Retrieval**: Automatically analyze any SQL Server database backup file structure
- **Query Execution**: Run generated SQL and display formatted results
- **Query Refinement**: Automatically refine queries that encounter execution errors (up to 3 attempts)
- **Clean and Intuitive UI**: Simple Streamlit interface with database schema viewer
- **Containerized Deployment**: Docker-based setup for cross-platform execution
- **Simple Setup Script**: Interactive configuration of environment variables

## Architecture

The application implements a layered architecture where higher-level layers depend on lower-level layers:

```
┌─────────────────┐
│  Presentation   │ → User interface components (Streamlit)
└────────┬────────┘
         ↓
┌─────────────────┐
│    Services     │ → Business logic and core functionality
└────────┬────────┘
         ↓
┌─────────────────┐
│ Infrastructure  │ → Database, LLM, and configuration
└─────────────────┘
```

### 1. Presentation Layer (`src/presentation/`)

- **UI Module** (`ui.py`): Streamlit interface with components for:
  - Displaying database schema
  - Accepting natural language input
  - Showing SQL queries and execution results
  - Handling error displays and refinement information

### 2. Services Layer (`src/services/`)

- **LLM Text-to-SQL Service** (`llm_text_to_sql_service.py`): 
  - Converts natural language to SQL using OpenAI
  - Implements query refinement logic for handling errors
  - Manages prompts for initial generation and refinement

- **Database Schema Service** (`database_schema_service.py`):
  - Extracts schema information from SQL Server
  - Caches schema to improve performance
  - Formats schema as structured data for LLM context

### 3. Infrastructure Layer (`src/infrastructure/`)

- **Database** (`database.py`):
  - Handles SQL Server connections
  - Executes queries and processes results
  - Supports both local and containerized environments

- **OpenAI LLM** (`open_ai_llm.py`):
  - Manages OpenAI API interactions
  - Handles API key and model configuration

- **Config** (`config.py`):
  - Manages environment variables
  - Provides typed access to configuration

- **Exceptions** (`exceptions.py`):
  - Defines custom exceptions for error handling

### 4. Setup and Deployment

- **Setup Script** (`setup_helpers/setup_env.py`):
  - Interactive configuration tool
  - Generates environment variables with defaults

- **Docker Configuration**:
  - Application container (`Dockerfile.app`)
  - SQL Server container (`Dockerfile.sqlserver`)
  - Container orchestration (`docker-compose.yml`)

### Data Flow

1. **Schema Context**: Database schema is retrieved from SQL Server and cached
2. **User Input**: User enters a natural language question via the Streamlit UI
3. **LLM Processing**: Question and schema are sent to OpenAI API via a crafted prompt
4. **SQL Generation**: LLM generates an SQL query based on the natural language
5. **Query Execution**: Generated SQL is executed against the database
6. **Error Handling**: If execution fails, query is refined and retried (up to 3 times)
7. **Result Display**: Query and results are displayed to the user

## Assumptions

- Only OpenAI API is used for language model integration
- Only Microsoft SQL Server backup (.bak) files are supported
- No RAG (Retrieval Augmented Generation) pipeline was implemented
- No vector search or embeddings were used for schema understanding
- Database schema is relatively stable and can be cached
- Query refinement within 3 attempts is sufficient for most errors

## How to Run

Running SQL2Text is simple:

1. Clone the repository

2. Run the setup script:
   ```
   python setup_helpers/setup_env.py
   ```
   The script will ask for:
   - Your OpenAI API key (required)
   - Path to your SQL Server .bak file (required)
   - Other optional configuration (or use defaults)

3. Build and start the containers:
   ```
   docker-compose build
   docker-compose up
   ```

4. Wait for the database restoration and application startup to complete (this may take a few minutes depending on your database size)

5. Access the application at:
   ```
   http://localhost:8501
   ```

## Development Tools

This project was developed with assistance from Windsurf AI, which was used during the development process to:
- Research SQL Server database connectivity
- Debug ODBC driver configuration issues
- Build and refine prompt engineering strategies
- Fix containerization issues
- Research query refinement approaches
