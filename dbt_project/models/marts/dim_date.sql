-- A date spine covering 3 years back through today, built with DuckDB's
-- native generate_series rather than a dbt_utils macro - keeps this
-- project dependency-free (no `dbt deps` / packages.yml network install).
with spine as (
    select cast(d as date) as date_day
    from generate_series(
        current_date - interval '3 years',
        current_date,
        interval '1 day'
    ) as t(d)
)
select
    date_day,
    extract(year from date_day) as year,
    extract(month from date_day) as month,
    extract(day from date_day) as day,
    extract(dow from date_day) as day_of_week,
    strftime(date_day, '%Y-%m') as year_month
from spine
