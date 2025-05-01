# Use the official Microsoft SQL Server image
FROM mcr.microsoft.com/mssql/server:2022-latest

# Set environment variables
ENV ACCEPT_EULA=Y \
    MSSQL_PID=Developer \
    SA_PASSWORD=${SQL_PASSWORD}

# Copy initialization scripts and backup file
COPY init.sh /usr/src/app/init.sh
COPY restore.sql /usr/src/app/restore.sql
COPY AdventureWorks2022.bak /var/opt/mssql/backup/AdventureWorks2022.bak

# Switch to root to change permissions
USER root

# Grant permissions for the init script to be executable
RUN chmod +x /usr/src/app/init.sh

# Switch back to the default user
USER mssql

# Run the init script
CMD ["/bin/bash", "-c", "/usr/src/app/init.sh & /opt/mssql/bin/sqlservr"]
