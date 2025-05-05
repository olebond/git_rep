#1_time_on_ground

select
tail_number,
wheels_on,
lead(wheels_off) over (PARTITION BY tail_number order by wheels_on) as next_wheels_off,
lead(wheels_off) over (PARTITION BY tail_number order by wheels_on) - wheels_on as time_on_ground
from flights
order by tail_number, wheels_on;

#2_count_departure

SELECT
  airline,
  COUNT(*) FILTER (WHERE day_of_week = 1 AND departure_time IS NOT NULL) AS "Sun",
  COUNT(*) FILTER (WHERE day_of_week = 2 AND departure_time IS NOT NULL) AS "Mon",
  COUNT(*) FILTER (WHERE day_of_week = 3 AND departure_time IS NOT NULL) AS "Tue",
  COUNT(*) FILTER (WHERE day_of_week = 4 AND departure_time IS NOT NULL) AS "Wed",
  COUNT(*) FILTER (WHERE day_of_week = 5 AND departure_time IS NOT NULL) AS "Thu",
  COUNT(*) FILTER (WHERE day_of_week = 6 AND departure_time IS NOT NULL) AS "Fri",
  COUNT(*) FILTER (WHERE day_of_week = 7 AND departure_time IS NOT NULL) AS "Sat"
FROM flights
where departure_time::date between '2015-07-01' and '2015-07-07'
GROUP BY airline
ORDER BY 2 desc, 3 DESC, 4 DESC, 5 DESC, 6 DESC, 7 DESC, 8 DESC;



#3_count_of_flight, total_distance, time_in_air per tail_number
SELECT
  TAIL_NUMBER,
  COUNT(*) AS count_of_flights,
  sum(distance) as total_distance,
  sum(air_time) as time_in_air
FROM flights
WHERE departure_time IS NOT NULL
group by TAIL_NUMBER
ORDER BY count_of_flights desc;



