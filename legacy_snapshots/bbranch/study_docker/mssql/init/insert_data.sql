USE flights_db;
GO

-- Вставка даних в таблицю flights2 з 201507_flights.csv
BULK INSERT flights2
FROM '/tmp/201507_flights.csv'
WITH
(
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    MAXERRORS = 2
);
GO

-- Вставка даних в таблицю flights з flights_update.csv
BULK INSERT flights
FROM '/tmp/flights_update.csv'
WITH
(
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    MAXERRORS = 2
);
GO 