FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for FreeTDS
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    tdsodbc \
    freetds-dev \
    freetds-bin \
    && rm -rf /var/lib/apt/lists/*

# Configure ODBC drivers for FreeTDS
RUN echo "[FreeTDS]\n\
Description = FreeTDS Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so\n\
" > /etc/odbcinst.ini

# Configure FreeTDS to use proper TDS version for SQL Server
RUN echo "[global]\n\
        tds version = 7.3\n\
        client charset = UTF-8\n\
        text size = 20971520\n\
[sqlserver]\n\
        host = sqlserver\n\
        port = 1433\n\
        tds version = 7.3\n\
" > /etc/freetds/freetds.conf

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0"]
