-- Singular test: fails if it returns any rows.
select *
from {{ ref('fact_orders') }}
where quantity <= 0
