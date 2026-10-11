-- Singular test: fails if it returns any rows.
select *
from {{ ref('fact_orders') }}
where line_total < 0
