USE master;
GO
RESTORE DATABASE __SQL_DATABASE__
FROM DISK = '/var/opt/mssql/backup/database.bak'
WITH REPLACE,
MOVE '__DATA_FILE_NAME__' TO '/var/opt/mssql/data/__SQL_DATABASE__.mdf',
MOVE '__LOG_FILE_NAME__' TO '/var/opt/mssql/data/__SQL_DATABASE__.ldf';
GO