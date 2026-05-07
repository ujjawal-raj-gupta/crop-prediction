-- Phase 1: PostgreSQL schema for market intelligence (prices)

CREATE TABLE IF NOT EXISTS price_history (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  crop VARCHAR(50) NOT NULL,
  mandi VARCHAR(100) NOT NULL,
  state VARCHAR(50) NOT NULL,
  district VARCHAR(100),
  price_per_quintal NUMERIC(10,2),
  min_price NUMERIC(10,2),
  max_price NUMERIC(10,2),
  raw JSONB,
  UNIQUE(date, crop, mandi, state)
);

