--Manipulate date and time data using:

--1Functions that return system date and time values (SYSDATETIME, SYSDATETIMEOFFSET).
SELECT GETDATE() AS current_date;
SELECT SYSDATETIME() AS current_timestamp;
SELECT CURRENT_TIMESTAMP AS now;

--2Functions that return date and time parts (DATENAME, DATEPART, DAY, MONTH, YEAR).
SELECT tail_number, DATENAME(WEEKDAY, wheels_on) AS weekday_name
FROM flights
WHERE wheels_on IS NOT NULL;

SELECT tail_number, DATEPART(WEEKDAY, wheels_on) AS weekday_number
FROM flights;

SELECT
  tail_number,
  DAY(departure_time) AS day,
  MONTH(departure_time) AS month,
  YEAR(departure_time) AS year
FROM flights;

--3Functions that return date and time values from their parts
SELECT DATEFROMPARTS(year, month, day) AS full_date
FROM flights2;

SELECT TIMEFROMPARTS(14, 45, 0, 0, 0) AS example_time;

SELECT
  tail_number,
  DATETIMEFROMPARTS(year, month, day, 14, 30, 0, 0) AS scheduled_ts
FROM flights
LIMIT 5;

--DATETIME2FROMPARTS
SELECT DATETIME2FROMPARTS(2024, 3, 15, 14, 30, 0, 0, 7) AS datetime2_example;

--DATETIMEOFFSETFROMPARTS
SELECT DATETIMEOFFSETFROMPARTS(2024, 3, 15, 14, 30, 0, 0, 2, 0, 7) AS datetimeoffset_example;

--SMALLDATETIMEFROMPARTS
SELECT SMALLDATETIMEFROMPARTS(2024, 3, 15, 14, 30) AS smalldatetime_example;


--4Function that returns date and time difference values (DATEDIFF).
SELECT
  tail_number,
  wheels_on,
  DATEDIFF(MINUTE, wheels_off, wheels_on) AS time_in_air
FROM flights
WHERE wheels_on IS NOT NULL AND wheels_off IS NOT NULL;

--повернути потім в годинах, хвилинах цілу число
SELECT
  tail_number,
  DATEDIFF(MINUTE, wheels_off, wheels_on) AS minutes_in_air
FROM flights
WHERE wheels_on IS NOT NULL AND wheels_off IS NOT NULL;

--без фільтрів
SELECT
  tail_number,
  DATEDIFF(DAY, wheels_off, wheels_on) AS days_in_air
FROM flights
WHERE wheels_on IS NOT NULL AND wheels_off IS NOT NULL;

--5Functions that modify date and time values (DATEADD, EOMONTH, SWITCHOFFSET).
SELECT DATEADD(DAY, 1, departure_time) AS next_day
FROM flights;

SELECT
  tail_number,
  EOMONTH(wheels_on) AS end_of_month
FROM flights;

--SWITCHOFFSET
SELECT SWITCHOFFSET(SYSDATETIMEOFFSET(), '-05:00') AS switched_timezone; 

--6Function that validates date and time values (ISDATE).
SELECT
  tail_number,
  ISDATE(arrival_time) AS is_valid
FROM flights;

--02. Manipulate string values

--1Return a starting position of the specified expression in a character string (CHARINDEX).
SELECT tail_number, CHARINDEX('A', tail_number) as pos_A
FROM flights
LIMIT 5;

--2Return the left part of a character string with the specified number of characters (LEFT).
SELECT airport_country_name
FROM airport_dim
WHERE LEFT(airport_country_name, 3) = 'Ukr';

--3Return the integer value of the string length (LEN).
SELECT airport_country_name, LEN(airport_country_name) as len_value
FROM airport_dim
WHERE LEFT(airport_country_name, 3) = 'Ukr';

--4Remove leading blanks (LTRIM).
--5Remove trailing blanks (RTRIM).
SELECT LTRIM('    AA123') as no_spaces_left,
       RTRIM('AA123    ') as no_spaces_rights;

--6Return the integer value of the starting position of text found in the string (PATINDEX).
SELECT tail_number, PATINDEX('%[0-9]%', tail_number) as first_digit_position
FROM flights
LIMIT 5;

--7Replace occurrences of text found in the string with a new value (REPLACE).
SELECT tail_number, REPLACE(tail_number, 'N', 'T') as replaced
FROM flights
LIMIT 3;

--8Repeat a character expression for a specified number of times (REPLICATE).
SELECT airline, REPLICATE(airline, 3) as replicated
FROM flights
LIMIT 10;

--9Return the reverse of a character expression (REVERSE).
SELECT DISTINCT airport_country_name, REVERSE(airport_country_name) as reversed
FROM airport_dim

--10Return portion of the string (SUBSTRING).
SELECT tail_number, SUBSTRING(tail_number, 3, 2) as sub_tail
FROM flights

--11Return a character expression with lowercase character data converted to uppercase (UPPER).
SELECT airline, UPPER(airline) AS upper_case
FROM flights

--03. Implement manual (explicit) conversion of data types in the SQL queries using:
--1Functions that convert an expression of one data type to another (CAST, CONVERT).
SELECT
  tail_number,
  departure_time,
  CAST(departure_time AS DATE) AS departure_date,
  CAST(distance AS DECIMAL(10,2)) AS distance_decimal
FROM flights;

--CONVERT
SELECT 
  tail_number,
  departure_time,
  CONVERT(VARCHAR(10), departure_time, 103) AS formatted_date,
  CONVERT(DECIMAL(10,2), distance) AS distance_decimal,
  CONVERT(VARCHAR(5), departure_time, 108) AS time_only
FROM flights;

--2Functions that return the result of an expression translated to the requested data type (PARSE, TRY_PARSE).
SELECT 
  tail_number,
  departure_time,
  PARSE(CONVERT(VARCHAR(10), departure_time, 103) AS DATE) AS parsed_date
FROM flights;

--TRY_PARSE
SELECT 
  tail_number,
  departure_time,
  TRY_PARSE(CONVERT(VARCHAR(10), departure_time, 103) AS DATE) AS valid_date,
  TRY_PARSE('invalid-date' AS DATE) AS invalid_date
FROM flights;

--3Functions that return a value cast to the specified data type (TRY_CAST, TRY_CONVERT).
--TRY_CAST
SELECT 
  tail_number,
  distance,
  TRY_CAST(distance AS INT) AS distance_int,
  TRY_CAST(tail_number AS INT) AS invalid_number
FROM flights;

--TRY_CONVERT
SELECT 
  tail_number,
  departure_time,
  TRY_CONVERT(DECIMAL(10,2), distance) AS valid_decimal,
  TRY_CONVERT(DATE, departure_time) AS valid_date,
  TRY_CONVERT(INT, tail_number) AS invalid_conversion
FROM flights;

--04. Rank the data in database queries
SELECT
  airport_dim.airport_state_name AS state,
  flights.airline,
  COUNT(*) AS flights_count,
  RANK() OVER (
    PARTITION BY airport_dim.airport_state_name
    ORDER BY COUNT(*) DESC
  ) AS rank_pos,
  DENSE_RANK() OVER (
    PARTITION BY airport_dim.airport_state_name
    ORDER BY COUNT(*) DESC
  ) AS dense_rank_pos,
  ROW_NUMBER() OVER (
    PARTITION BY airport_dim.airport_state_name
    ORDER BY COUNT(*) DESC
  ) AS row_num,
  NTILE(5) OVER (
    PARTITION BY airport_dim.airport_state_name
    ORDER BY COUNT(*) DESC
  ) AS bucket
FROM flights
JOIN airport_dim ON flights.origin_airport = airport_dim.airport
GROUP BY airport_dim.airport_state_name, flights.airline
ORDER BY state, flights_count DESC;

SELECT
  tail_number,
  airline,
  COUNT(*) AS flights_count,
  RANK() OVER (ORDER BY COUNT(*) DESC) AS overall_rank,
  DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS dense_rank,
  ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS row_num,
  NTILE(4) OVER (ORDER BY COUNT(*) DESC) AS quartile
FROM flights
GROUP BY tail_number, airline;

--05. Combine the results of two or more SELECT statements
SELECT 
    tail_number,
    airline,
    'Origin' AS flight_type
FROM flights
UNION ALL
SELECT 
    tail_number,
    airline,
    'Destination' AS flight_type
FROM flights;

--6.
SELECT 
    origin_airport,
    COUNT(*) AS flight_count
FROM flights
GROUP BY origin_airport
INTERSECT
SELECT 
    destination_airport,
    COUNT(*) AS flight_count
FROM flights
GROUP BY destination_airport;

--7.
SELECT 
    origin_airport,
    COUNT(*) AS departure_count
FROM flights
GROUP BY origin_airport
EXCEPT
SELECT 
    destination_airport,
    COUNT(*) AS arrival_count
FROM flights
GROUP BY destination_airport;

--8.
SELECT 
    'Origin' AS airport_type,
    origin_airport AS airport,
    COUNT(*) AS flight_count
FROM flights
GROUP BY origin_airport
UNION
SELECT 
    'Destination' AS airport_type,
    destination_airport AS airport,
    COUNT(*) AS flight_count
FROM flights
GROUP BY destination_airport
ORDER BY airport_type, flight_count DESC;

--06. Use the following logical join operators to join tables in queries:

--1. Inner Join
SELECT 
    f.flight_number,
    f.origin_airport,
    a.airport_state_name,
    a.airport_city_name
FROM flights f
INNER JOIN airport_dim a ON f.origin_airport = a.airport;

--2. Left Outer Join
SELECT 
    f.flight_number,
    f.origin_airport,
    a.airport_state_name,
    a.airport_city_name
FROM flights f
LEFT JOIN airport_dim a ON f.origin_airport = a.airport
WHERE a.airport IS NULL;

--3. Right Outer Join
SELECT 
    a.airport,
    a.airport_state_name,
    COUNT(f.flight_number) AS flight_count
FROM flights f
RIGHT JOIN airport_dim a ON f.origin_airport = a.airport
GROUP BY a.airport, a.airport_state_name
ORDER BY flight_count DESC;

--4. Full Outer Join
SELECT 
    COALESCE(f.origin_airport, a.airport) AS airport,
    f.flight_number,
    a.airport_state_name
FROM flights f
FULL OUTER JOIN airport_dim a ON f.origin_airport = a.airport
WHERE f.origin_airport IS NULL OR a.airport IS NULL;

--5. Cross Join
SELECT 
    f.flight_number,
    f.origin_airport,
    a.airport_state_name
FROM flights f
CROSS JOIN airport_dim a
WHERE f.origin_airport = a.airport
  AND a.airport_state_name = 'California'
LIMIT 20;

--6. Self Join
SELECT 
    f1.flight_number AS flight1,
    f2.flight_number AS flight2,
    f1.origin_airport,
    f1.destination_airport
FROM flights f1
INNER JOIN flights f2 
    ON f1.origin_airport = f2.destination_airport 
    AND f1.destination_airport = f2.origin_airport
WHERE f1.flight_number < f2.flight_number;

--7. Multiple Joins - приклад з кількома об'єднаннями
SELECT 
    f.flight_number,
    f.airline,
    origin.airport_state_name AS origin_state,
    dest.airport_state_name AS destination_state
FROM flights f
INNER JOIN airport_dim origin ON f.origin_airport = origin.airport
INNER JOIN airport_dim dest ON f.destination_airport = dest.airport
WHERE origin.airport_state_name = dest.airport_state_name; -- внутрішні рейси

