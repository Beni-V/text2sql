#!/bin/bash

# Wait for SQL Server to be ready
for i in {1..50}; do
    /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -Q "SELECT 1" &> /dev/null
    if [ $? -eq 0 ]; then
        echo "SQL Server is ready"
        break
    else
        echo "SQL Server not ready yet..."
        sleep 1
    fi
done

# Restore database
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -Q "
RESTORE DATABASE AdventureWorks2022 
FROM DISK = '/usr/src/AdventureWorks2022.bak'
WITH MOVE 'AdventureWorks2022' TO '/var/opt/mssql/data/AdventureWorks2022.mdf',
MOVE 'AdventureWorks2022_log' TO '/var/opt/mssql/data/AdventureWorks2022_log.ldf',
REPLACE, STATS=5"
