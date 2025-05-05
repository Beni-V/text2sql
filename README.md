# SQL2Text: Natural Language to SQL Query Generator

## Introduction

Text2SQL is a tool that translates natural language queries into SQL queries for Microsoft SQL Server databases. It allows users without SQL knowledge to extract insights directly from databases using plain English.

## Features

- **Natural Language to SQL Conversion**: Translate English natural language queries into SQL Server queries
- **Dynamic Schema Retrieval**: Automatically analyze any SQL Server database backup file structure
- **Query Execution**: Run generated SQL and display formatted results
- **Query Refinement**: Automatically refine queries that encounter execution errors (up to 3 attempts)
- **Clean and Intuitive UI**: Simple Streamlit interface with database schema viewer
- **Containerized Deployment**: Docker-based setup for cross-platform execution
- **Simple Setup Script**: Interactive configuration of environment variables
- **RAG Support**: Retrieval Augmented Generation for more efficient and accurate SQL query generation

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
  - Selecting between RAG and regular generation modes

### 2. Services Layer (`src/services/`)

- **LLM Text-to-SQL Service** (`llm_text_to_sql_service.py`): 
  - Converts natural language to SQL using OpenAI
  - Implements query refinement logic for handling errors
  - Manages prompts for initial generation and refinement
  - Supports both RAG and regular (full schema) generation modes

- **Database Schema Service** (`database_schema_service.py`):
  - Extracts schema information from SQL Server
  - Caches schema to improve performance
  - Formats schema as structured data for LLM context

- **Schema Embedding Service** (`schema_embedding_service.py`):
  - Vectorizes database schema into FAISS.
  - Create embeddings for schema tables
  - Persists vector store to disk for reuse

- **Schema Excerption Service** (`schema_excerption_service.py`):
  - Retrieve relevant schema information based on user queries
  - Use similarity search to find most relevant schema parts
  - Dynamically adjusts search scope during query refinement

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
2. **Schema Ingestion**: Schema is processed into documents and stored in a vector database
3. **User Input**: User enters a natural language queries via the Streamlit UI
4. **RAG Processing**: If RAG mode is enabled, only relevant schema parts are retrieved based on the query
5. **LLM Processing**: Natural language queries and schema are sent to OpenAI API via a crafted prompt
6. **SQL Generation**: LLM generates an SQL query based on the natural language
7. **Query Execution**: Generated SQL is executed against the database
8. **Error Handling**: If execution fails, query is refined with more schema context and retried (up to 3 times)
9. **Result Display**: Query and results are displayed to the user

## Tradeoffs

- Only OpenAI API is used for language model integration
- Only Microsoft SQL Server backup (.bak) files are supported
- RAG implementation uses FAISS for vector storage and retrieval
- OpenAI's text-embedding-3-small model is used for embeddings
- Database schema is supposed to be relatively stable and can be cached
- Query refinement within 3 attempts is sufficient for most errors
- RAG mode dynamically increases schema context during refinement attempts

## How to Run

Running SQL2Text is simple:

### For macOS/Linux:
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

4. Wait for the database restoration and application startup to complete

5. Access the application at:
   ```
   http://localhost:8501
   ```

### For Windows (11):
1. Install WSL (Windows Subsystem for Linux):
   ```
   wsl --install
   ```
   This will install WSL

2. Install ubuntu over WSL:
   ```
   wsl --install -d Ubuntu
   ```
   (For other Windows versions, follow Microsoft's WSL installation guide)

3. Restart your computer when prompted

4. Launch Ubuntu shell:
   ```
   wsl -d Ubuntu
   ```

5. Configure Docker WSL integration:
   - Open Docker Desktop
   - Go to Settings → Resources → WSL Integration
   - Enable integration with your Ubuntu distro

6. In the Ubuntu shell, navigate to the cloned repository

7. Run the setup script:
   ```
   sudo python3 setup_helpers/setup_env.py
   ```
   Enter values as prompted. For the .bak file path, use WSL format:
   ```
   /mnt/c/Users/{your_username}/{path_to_file}
   ```

8. Build and start containers:
   ```
   sudo docker-compose build
   sudo docker-compose up
   ```

9. Access the application at:
   ```
   http://localhost:8501
   ```

## Troubleshooting

### Backup File Access Denied Error
If you encounter the error:
```
BackupDiskFile::OpenMedia: Backup device '/var/opt/mssql/backup/database.bak' failed to open. Operating system error 5(Access is denied.).
```
Try these solutions:
1. Move the .bak file into the project directory
2. Use a relative path instead of absolute path
3. Ensure the file has proper permissions in WSL
4. For Windows, verify the file path uses the correct WSL format (/mnt/c/...)

## Using RAG vs Regular Mode

The application supports two modes of operation:

- **RAG Mode (default)**: Uses Retrieval Augmented Generation to only include relevant parts of the schema in the prompt. This improves performance by:
  - Reducing token usage by focusing only on relevant tables
  - Improving accuracy by reducing noise from irrelevant schema parts
  - Dynamically expanding context during refinement attempts

- **Regular Mode**: Includes the entire database schema in each prompt. This can be useful for:
  - Complex queries that might need context from many tables
  - Debugging when RAG might be missing important schema information

You can switch between modes using the radio buttons in the UI.

## Development Tools

This project was developed with assistance from Windsurf AI, which was used during the development process to:
- Research SQL Server database connectivity
- Debug ODBC driver configuration issues
- Build and refine prompt engineering strategies
- Fix containerization issues
- Research query refinement approaches
- Writing the skeleton of the Streamlit UI
- Implementing RAG support for improved query generation
