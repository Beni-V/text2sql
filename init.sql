-- Wait for SQL Server to be ready
DECLARE @i INT = 0
WHILE @i < 30
BEGIN
    BEGIN TRY
        EXEC sp_executesql N'SELECT 1'
        BREAK
    END TRY
    BEGIN CATCH
        WAITFOR DELAY '00:00:10'
        SET @i = @i + 1
    END CATCH
END

-- Check if database already exists
IF NOT EXISTS (SELECT name FROM master.dbo.sysdatabases WHERE name = 'AdventureWorks')
BEGIN
    -- Restore the database from backup
    RESTORE DATABASE AdventureWorks FROM DISK = '/var/opt/mssql/backup/AdventureWorks2022.bak'
    WITH 
        MOVE 'AdventureWorks2022' TO '/var/opt/mssql/data/AdventureWorks.mdf',
        MOVE 'AdventureWorks2022_log' TO '/var/opt/mssql/data/AdventureWorks.ldf',
        REPLACE,
        STATS = 10;
    
    -- Verify restore completed
    IF EXISTS (SELECT name FROM master.dbo.sysdatabases WHERE name = 'AdventureWorks')
        PRINT 'AdventureWorks database restored successfully'
    ELSE
        THROW 51000, 'Failed to restore AdventureWorks database', 1
END
ELSE
    PRINT 'AdventureWorks database already exists'

-- Set recovery model to simple
ALTER DATABASE AdventureWorks SET RECOVERY SIMPLE;

-- Enable contained database authentication
ALTER DATABASE AdventureWorks SET CONTAINMENT = PARTIAL;
