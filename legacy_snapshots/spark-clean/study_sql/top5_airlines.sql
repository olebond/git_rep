SELECT state, airline, flights_count

FROM (
    SELECT airport_dim.airport_state_name AS state,
           flights.airline,
           COUNT(*) AS flights_count,
           ROW_NUMBER() OVER (PARTITION BY airport_dim.airport_state_name ORDER BY COUNT(*) DESC) AS rn
    FROM flights
    JOIN airport_dim
      ON flights.origin_airport = airport_dim.airport
    WHERE airport_dim.airport_country_name = 'United States'
      AND airport_dim.airport_is_latest = 1
    GROUP BY airport_dim.airport_state_name, flights.airline
) sub
WHERE rn <= 5
ORDER BY state, flights_count DESC;


--BQ(BigQuery)
SELECT
  airport_state_name AS state,
  flights.airline,
  COUNT(*) AS flights_count,
  ROW_NUMBER() OVER (
    PARTITION BY airport_state_name
    ORDER BY COUNT(*) DESC
  ) AS rn
FROM flights
JOIN airport_dim
  ON flights.origin_airport = airport_dim.airport
WHERE airport_dim.airport_country_name = 'United States'
  AND airport_dim.airport_is_latest = 1
GROUP BY airport_state_name, flights.airline
QUALIFY rn <= 5
ORDER BY state, flights_count DESC;

--1nf, 2nf, 3nf, database normalization
--вивести аеропорти де відбулось більше 100 вильотів

SELECT airline, COUNT(*) AS flights
FROM flights
GROUP BY airline
HAVING COUNT(*) > 10000;