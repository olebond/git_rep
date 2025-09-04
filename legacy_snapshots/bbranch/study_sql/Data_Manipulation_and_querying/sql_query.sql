--Manipulate date and time data using:

--1Functions that return system date and time values (SYSDATETIME, SYSDATETIMEOFFSET).
select current_date;
select current_timestamp;
select now;

--2Functions that return date and time parts (DATENAME, DATEPART, DAY, MONTH, YEAR).
SELECT tail_number, TO_CHAR(wheels_on, 'Day') AS weekday_name
FROM flights
WHERE wheels_on IS NOT NULL;

SELECT tail_number, EXTRACT(DOW FROM wheels_on) AS weekday_number
FROM flights;

SELECT
  tail_number,
  EXTRACT(DAY FROM departure_time)   AS day,
  EXTRACT(MONTH FROM departure_time) AS month,
  EXTRACT(YEAR FROM departure_time)  AS year
FROM flights;

--3Functions that return date and time values from their parts (DATEFROMPARTS, DATETIME2FROMPARTS, DATETIMEFROMPARTS, DATETIMEOFFSETFROMPARTS, SMALLDATETIMEFROMPARTS, TIMEFROMPARTS).
SELECT MAKE_DATE(year::int, month::int, day::int) AS full_date
FROM flights2;

SELECT MAKE_TIME(14, 45, 0) AS example_time;

SELECT
  tail_number,
  MAKE_TIMESTAMP(year::int, month::int, day::int, 14, 30, 0) AS scheduled_ts
FROM flights
LIMIT 5;

--4Function that returns date and time difference values (DATEDIFF).
SELECT
  tail_number,
  wheels_on,
  wheels_on - wheels_off AS time_in_air
FROM flights
WHERE wheels_on IS NOT NULL AND wheels_off IS NOT NULL;

--повернути потім в годинах, хвилинах цілу число
SELECT
  tail_number,
  EXTRACT(EPOCH FROM wheels_on - wheels_off) / 60 AS minutes_in_air   -- back in sec
FROM flights
WHERE wheels_on IS NOT NULL AND wheels_off IS NOT NULL;

--без фільтрів
SELECT
  tail_number,
  DATE_PART('day', wheels_on - wheels_off) AS days_in_air
FROM flights
WHERE wheels_on IS NOT NULL AND wheels_off IS NOT NULL;

--5Functions that modify date and time values (DATEADD, EOMONTH, SWITCHOFFSET).

SELECT DATE(departure_time) + INTERVAL '1 day' AS next_day
FROM flights;

SELECT
  tail_number,
  DATE_TRUNC('month', wheels_on) + INTERVAL '1 month - 1 day' AS end_of_month
FROM flights;

--6Function that validates date and time values (ISDATE).  no isdate in postgress.
SELECT
  tail_number,
  arrival_time::timestamp IS NOT NULL AS is_valid
FROM flights;

--Manipulate string values

--1Return a starting position of the specified expression in a character string (CHARINDEX).

select tail_number, POSITION('A' in tail_number) as pos_A
from flights
limit 5;
--2Return the left part of a character string with the specified number of characters (LEFT).

select airport_country_name
from airport_dim
where left(airport_country_name, 3)='Ukr';
--3Return the integer value of the string length (LEN).

select airport_country_name, length(airport_country_name) as len_value
from airport_dim
where left(airport_country_name, 3)='Ukr'

--4Remove leading blanks (LTRIM).
--5Remove trailing blanks (RTRIM).
select LTRIM('    AA123') as no_spaces_left,
select RTRIM('AA123    ') as no_spaces_rights;

--6Return the integer value of the starting position of text found in the string (PATINDEX).

--7Replace occurrences of text found in the string with a new value (REPLACE).
select tail_number, REPLACE(tail_number, 'N', 'T') as replaced
from flights
limit 3;

--8Repeat a character expression for a specified number of times (REPLICATE).
select airline, Repeat(airline, 3) as replicated
from flights
limit 10;

--9Return the reverse of a character expression (REVERSE).
select distinct airport_country_name, distinct reverse(airport_country_name) as reversed
from airport_dim
limit 5;

--10Return portion of the string (SUBSTRING).
select tail_number, substring(tail_number from 3 for 2) as sub_tail
from flights
limit 5;

--11Return a character expression with lowercase character data converted to uppercase (UPPER).
SELECT airline, UPPER(airline) AS upper_case
FROM flights
LIMIT 5;

--Implement manual (explicit) conversion of data types in the SQL queries using:
--1Functions that convert an expression of one data type to another (CAST, CONVERT).
SELECT
  MAKE_DATE(CAST(year AS INT), CAST(month AS INT), CAST(day AS INT)) AS flight_date
FROM flights2
LIMIT 5;

--2Functions that return the result of an expression translated to the requested data type (PARSE, TRY_PARSE).

SELECT
  CAST('2025-05-20' AS DATE) AS parsed_date;
--3Functions that return a value cast to the specified data type (TRY_CAST, TRY_CONVERT).

--Rank the data in database queries
--Rank values for each row in a table using ranking functions and break up the data into partitions using OVER and PARTITION BY statements.
--The SQL Server provides the following Rank Functions that allow assigning different ranks:

--Function that assigns the rank number to each record present in a partition (RANK).
--Function that assigns the number to each record within a partition without skipping the rank numbers (DENSE_RANK).
--Function that assigns the number to the group or bucket of rows within a partition (NTILE).
--Function that assigns the sequential number to each unique record present in a partition (ROW_NUMBER).
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
JOIN airport_dim
  ON flights.origin_airport = airport_dim.airport
GROUP BY airport_dim.airport_state_name, flights.airline
ORDER BY state, flights_count DESC;

--by window function. window
--Combine the results of two or more SELECT statements so that:

--Resulted data set includes the rows returned by both statements (UNION ALL).
SELECT origin_airport FROM flights
UNION ALL
SELECT airport FROM airport_dim;

--порядок і назва,
--Resulted data set includes the rows returned by both statements without duplicates (UNION).
SELECT origin_airport FROM flights
UNION
SELECT airport FROM airport_dim;

--

--Resulted data set includes all the rows common to both queries (INTERSECT).
SELECT origin_airport FROM flights
INTERSECT
SELECT airport FROM airport_dim;

--Resulted data set includes the difference between the two queries (EXCEPT).
SELECT origin_airport FROM flights
EXCEPT
SELECT airport FROM airport_dim;

--Use the following logical join operators to join tables in queries:

--Inner Join
SELECT *
FROM flights
INNER JOIN airport_dim
  ON flights.origin_airport = airport_dim.airport;
--Left Outer Join
SELECT *
FROM flights
LEFT JOIN airport_dim
  ON flights.origin_airport = airport_dim.airport;
--Right Outer Join

-- add alias, flights like f, add coalesce. вибірка пару колонок. більш складніший скрипт
SELECT *
FROM flights
RIGHT JOIN airport_dim
  ON flights.origin_airport = airport_dim.airport;
--Full Outer Join
SELECT *
FROM flights
FULL OUTER JOIN airport_dim
  ON flights.origin_airport = airport_dim.airport;
--Cross Join
SELECT
  flights.flight_number,
  flights.origin_airport,
  airport_dim.airport_state_name
FROM flights
CROSS JOIN airport_dim
LIMIT 100;

--inner join + where = cross join

SELECT
  f.flight_number,
  f.origin_airport,
  a.airport,
  a.airport_state_name
FROM flights f
CROSS JOIN airport_dim a
WHERE f.origin_airport = a.airport
  AND a.airport_state_name = 'California'
LIMIT 20;