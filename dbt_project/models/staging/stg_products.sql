select
    product_id,
    name as product_name,
    category,
    unit_price
from {{ source('raw', 'products') }}
