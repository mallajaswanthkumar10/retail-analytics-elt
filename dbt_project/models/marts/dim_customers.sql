select
    customer_id,
    customer_name,
    email,
    signup_date,
    country
from {{ ref('stg_customers') }}
