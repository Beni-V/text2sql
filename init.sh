#!/bin/bash
# Wait for SQL Server to be ready
for i in {1..50}; do
    if /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -Q "SELECT 1" -C > /dev/null; then
        echo "SQL Server ready"
        break
    else
        echo "Waiting for SQL Server..."
        sleep 2
    fi
done

# Run the restore script
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -i /usr/src/app/restore.sql -C