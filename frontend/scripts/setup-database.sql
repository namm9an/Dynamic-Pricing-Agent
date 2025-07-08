-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create pricing_decisions table
CREATE TABLE IF NOT EXISTS pricing_decisions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  product_id VARCHAR(50) NOT NULL,
  old_price DECIMAL(10,2),
  new_price DECIMAL(10,2),
  reason TEXT,
  confidence_score DECIMAL(3,2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create demand_predictions table
CREATE TABLE IF NOT EXISTS demand_predictions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  product_id VARCHAR(50) NOT NULL,
  predicted_demand INTEGER,
  actual_demand INTEGER,
  prediction_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE pricing_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE demand_predictions ENABLE ROW LEVEL SECURITY;

-- Create policies for dashboard access (allowing read access for authenticated users)
CREATE POLICY "Allow read access to pricing_decisions" ON pricing_decisions
  FOR SELECT USING (true);

CREATE POLICY "Allow read access to demand_predictions" ON demand_predictions
  FOR SELECT USING (true);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_pricing_decisions_timestamp ON pricing_decisions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_pricing_decisions_product_id ON pricing_decisions(product_id);
CREATE INDEX IF NOT EXISTS idx_demand_predictions_date ON demand_predictions(prediction_date DESC);
CREATE INDEX IF NOT EXISTS idx_demand_predictions_product_id ON demand_predictions(product_id);

-- Insert sample data for pricing_decisions
INSERT INTO pricing_decisions (product_id, old_price, new_price, reason, confidence_score) VALUES
  ('premium-plan', 29.99, 32.50, 'High demand detected', 0.87),
  ('enterprise-plan', 99.99, 105.00, 'Market conditions favorable', 0.92),
  ('starter-plan', 9.99, 11.50, 'Competitor analysis', 0.78),
  ('premium-plan', 32.50, 31.25, 'Demand stabilizing', 0.85),
  ('enterprise-plan', 105.00, 102.50, 'Price sensitivity detected', 0.89),
  ('starter-plan', 11.50, 12.99, 'Premium positioning', 0.82),
  ('premium-plan', 31.25, 33.75, 'Supply constraints', 0.90),
  ('enterprise-plan', 102.50, 108.00, 'Value optimization', 0.88),
  ('starter-plan', 12.99, 11.99, 'Market penetration', 0.75),
  ('premium-plan', 33.75, 35.00, 'Peak demand period', 0.93)
ON CONFLICT DO NOTHING;

-- Insert sample data for demand_predictions
INSERT INTO demand_predictions (product_id, predicted_demand, actual_demand, prediction_date) VALUES
  ('premium-plan', 150, 142, CURRENT_DATE - INTERVAL '1 day'),
  ('enterprise-plan', 45, 48, CURRENT_DATE - INTERVAL '1 day'),
  ('starter-plan', 320, 315, CURRENT_DATE - INTERVAL '1 day'),
  ('premium-plan', 165, 158, CURRENT_DATE - INTERVAL '2 days'),
  ('enterprise-plan', 52, 49, CURRENT_DATE - INTERVAL '2 days'),
  ('starter-plan', 298, 305, CURRENT_DATE - INTERVAL '2 days'),
  ('premium-plan', 140, 135, CURRENT_DATE - INTERVAL '3 days'),
  ('enterprise-plan', 38, 42, CURRENT_DATE - INTERVAL '3 days'),
  ('starter-plan', 285, 290, CURRENT_DATE - INTERVAL '3 days'),
  ('premium-plan', 175, 168, CURRENT_DATE - INTERVAL '4 days'),
  ('enterprise-plan', 55, 53, CURRENT_DATE - INTERVAL '4 days'),
  ('starter-plan', 310, 318, CURRENT_DATE - INTERVAL '4 days')
ON CONFLICT DO NOTHING;

-- Create a function to simulate real-time pricing decisions
CREATE OR REPLACE FUNCTION simulate_pricing_decision()
RETURNS void AS $$
DECLARE
  products TEXT[] := ARRAY['premium-plan', 'enterprise-plan', 'starter-plan'];
  product_name TEXT;
  old_price_val DECIMAL(10,2);
  new_price_val DECIMAL(10,2);
  reasons TEXT[] := ARRAY[
    'High demand detected',
    'Market conditions favorable', 
    'Competitor analysis',
    'Demand stabilizing',
    'Price sensitivity detected',
    'Supply constraints',
    'Value optimization',
    'Market penetration',
    'Peak demand period',
    'Cost optimization'
  ];
BEGIN
  -- Select random product
  product_name := products[1 + floor(random() * array_length(products, 1))];
  
  -- Generate realistic price changes
  CASE product_name
    WHEN 'premium-plan' THEN
      old_price_val := 29.99 + (random() * 10);
      new_price_val := old_price_val + (random() - 0.5) * 5;
    WHEN 'enterprise-plan' THEN
      old_price_val := 99.99 + (random() * 20);
      new_price_val := old_price_val + (random() - 0.5) * 15;
    WHEN 'starter-plan' THEN
      old_price_val := 9.99 + (random() * 5);
      new_price_val := old_price_val + (random() - 0.5) * 3;
  END CASE;
  
  -- Insert new pricing decision
  INSERT INTO pricing_decisions (
    product_id, 
    old_price, 
    new_price, 
    reason, 
    confidence_score
  ) VALUES (
    product_name,
    old_price_val,
    new_price_val,
    reasons[1 + floor(random() * array_length(reasons, 1))],
    0.7 + (random() * 0.3) -- Random confidence between 0.7 and 1.0
  );
END;
$$ LANGUAGE plpgsql;

-- Create a function to simulate demand predictions
CREATE OR REPLACE FUNCTION simulate_demand_prediction()
RETURNS void AS $$
DECLARE
  products TEXT[] := ARRAY['premium-plan', 'enterprise-plan', 'starter-plan'];
  product_name TEXT;
  predicted_val INTEGER;
  actual_val INTEGER;
BEGIN
  -- Select random product
  product_name := products[1 + floor(random() * array_length(products, 1))];
  
  -- Generate realistic demand predictions
  CASE product_name
    WHEN 'premium-plan' THEN
      predicted_val := 120 + floor(random() * 80); -- 120-200
      actual_val := predicted_val + floor((random() - 0.5) * 30); -- ±15 variance
    WHEN 'enterprise-plan' THEN
      predicted_val := 30 + floor(random() * 40); -- 30-70
      actual_val := predicted_val + floor((random() - 0.5) * 15); -- ±7 variance
    WHEN 'starter-plan' THEN
      predicted_val := 250 + floor(random() * 100); -- 250-350
      actual_val := predicted_val + floor((random() - 0.5) * 50); -- ±25 variance
  END CASE;
  
  -- Insert new demand prediction
  INSERT INTO demand_predictions (
    product_id,
    predicted_demand,
    actual_demand,
    prediction_date
  ) VALUES (
    product_name,
    predicted_val,
    actual_val,
    CURRENT_DATE
  );
END;
$$ LANGUAGE plpgsql;
