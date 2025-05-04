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

# Fix permissions on backup file for Windows compatibility
chmod 644 /var/opt/mssql/backup/database.bak

# Extract logical file names from the backup file
echo "Extracting logical file names from backup..."
FILELISTONLY_OUTPUT=$(/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -Q "RESTORE FILELISTONLY FROM DISK = '/var/opt/mssql/backup/database.bak'" -C)
DATA_FILE_NAME=$(echo "$FILELISTONLY_OUTPUT" | grep -E 'Row|mdf|MDF' | grep -v "model\|tempdb\|master\|msdb" | head -1 | awk '{print $1}')
LOG_FILE_NAME=$(echo "$FILELISTONLY_OUTPUT" | grep -E 'Row|ldf|LDF' | grep -v "model\|tempdb\|master\|msdb" | head -1 | awk '{print $1}')

echo "Found logical files: DATA='$DATA_FILE_NAME', LOG='$LOG_FILE_NAME'"

# Create a temporary restore script with the environment variables
cp /usr/src/app/restore.sql /tmp/restore_temp.sql
sed -i "s/__SQL_DATABASE__/$SQL_DATABAASE/g" /tmp/restore_temp.sql
sed -i "s/__DATA_FILE_NAME__/$DATA_FILE_NAME/g" /tmp/restore_temp.sql
sed -i "s/__LOG_FILE_NAME__/$LOG_FILE_NAME/g" /tmp/restore_temp.sql

# Run the restore script
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -i /tmp/restore_temp.sql -C