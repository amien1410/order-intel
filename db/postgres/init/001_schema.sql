CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE customers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  customer_id UUID NOT NULL REFERENCES customers(id),
  status TEXT NOT NULL CHECK (status IN ('pending','paid','shipped','cancelled','refunded')),
  total_amount NUMERIC(12,2) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ON orders (customer_id, created_at DESC);
CREATE INDEX ON orders (status);
-- Example partial index for "active" orders
CREATE INDEX orders_active_idx ON orders (created_at DESC) WHERE status IN ('pending','paid','shipped');

CREATE TABLE order_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  sku TEXT NOT NULL,
  qty INT NOT NULL CHECK (qty > 0),
  unit_price NUMERIC(12,2) NOT NULL
);

CREATE INDEX ON order_items (order_id);

CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID NOT NULL REFERENCES orders(id),
  method TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('initiated','authorized','captured','failed','refunded')),
  amount NUMERIC(12,2) NOT NULL,
  paid_at TIMESTAMPTZ
);

CREATE INDEX ON payments (order_id, status);
