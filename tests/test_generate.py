from data_generator.generate import generate_customers, generate_orders_and_items, generate_products


def test_generate_customers_count_and_unique_ids():
    customers = generate_customers(50, seed=1)
    assert len(customers) == 50
    assert len({c["customer_id"] for c in customers}) == 50


def test_generate_customers_unique_emails():
    customers = generate_customers(200, seed=1)
    assert len({c["email"] for c in customers}) == 200


def test_generate_customers_is_deterministic_given_same_seed():
    first = generate_customers(20, seed=7)
    second = generate_customers(20, seed=7)
    assert first == second


def test_generate_products_count_and_price_range():
    products = generate_products(30, seed=1)
    assert len(products) == 30
    assert all(5.0 <= p["unit_price"] <= 500.0 for p in products)


def test_generate_orders_reference_valid_customers_and_products():
    customers = generate_customers(10, seed=1)
    products = generate_products(10, seed=1)
    orders, order_items = generate_orders_and_items(customers, products, n_orders=25, seed=1)

    customer_ids = {c["customer_id"] for c in customers}
    product_ids = {p["product_id"] for p in products}

    assert len(orders) == 25
    assert all(o["customer_id"] in customer_ids for o in orders)
    assert all(oi["product_id"] in product_ids for oi in order_items)


def test_every_order_has_at_least_one_item():
    customers = generate_customers(5, seed=1)
    products = generate_products(5, seed=1)
    orders, order_items = generate_orders_and_items(customers, products, n_orders=10, seed=1)

    order_ids_with_items = {oi["order_id"] for oi in order_items}
    assert order_ids_with_items == {o["order_id"] for o in orders}


def test_order_item_ids_are_unique():
    customers = generate_customers(5, seed=1)
    products = generate_products(5, seed=1)
    _, order_items = generate_orders_and_items(customers, products, n_orders=20, seed=1)

    ids = [oi["order_item_id"] for oi in order_items]
    assert len(ids) == len(set(ids))
