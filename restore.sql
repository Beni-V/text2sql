CREATE DATABASE AdventureWorks2022;
GO
RESTORE DATABASE AdventureWorks2022
FROM DISK = '/var/opt/mssql/backup/AdventureWorks2022.bak'
WITH MOVE 'AdventureWorks2022' TO '/var/opt/mssql/data/AdventureWorks2022.mdf',
MOVE 'AdventureWorks2022_log' TO '/var/opt/mssql/data/AdventureWorks2022.ldf';
GO