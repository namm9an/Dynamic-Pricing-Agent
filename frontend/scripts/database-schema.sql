-- Create pricing_decisions table
CREATE TABLE IF NOT EXISTS pricing_decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id VARCHAR(50) NOT NULL,
  predicted_demand INTEGER,
  actual_demand INTEGER,
  prediction_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE pricing_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE demand_predictions ENABLE ROW LEVEL SECURITY;

-- Create policies for dashboard access
CREATE POLICY "Allow dashboard access to pricing_decisions" ON pricing_decisions
  FOR SELECT USING (true);

CREATE POLICY "Allow dashboard access to demand_predictions" ON demand_predictions
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
  ('enterprise-plan', 105.00, 102.50, 'Price sensitivity detected', 0.89);

-- Insert sample data for demand_predictions
INSERT INTO demand_predictions (product_id, predicted_demand, actual_demand, prediction_date) VALUES
  ('premium-plan', 150, 142, CURRENT_DATE - INTERVAL '1 day'),
  ('enterprise-plan', 45, 48, CURRENT_DATE - INTERVAL '1 day'),
  ('starter-plan', 320, 315, CURRENT_DATE - INTERVAL '1 day'),
  ('premium-plan', 165, 158, CURRENT_DATE - INTERVAL '2 days'),
  ('enterprise-plan', 52, 49, CURRENT_DATE - INTERVAL '2 days'),
  ('starter-plan', 298, 305, CURRENT_DATE - INTERVAL '2 days');
