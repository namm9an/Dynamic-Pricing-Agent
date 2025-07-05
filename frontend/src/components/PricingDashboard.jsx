import { useState, useEffect } from 'react';
import { healthCheck } from '../utils/api.js';
import { api } from '../utils/api.js';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  BarChart, Bar, ResponsiveContainer
} from 'recharts';

export default function PricingDashboard() {
  const [priceInput, setPriceInput] = useState('');
  const [optimal, setOptimal] = useState(null);
  const [history, setHistory] = useState([]);
  const [simulationData, setSimulationData] = useState(null);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!priceInput) return;
    const basePrice = parseFloat(priceInput);
    try {
      const { data } = await api.post('/get-optimal-price', {
        base_price: basePrice,
        product_id: 'PROD_001',
        location: 'US',
      });
      setOptimal(data);
      setHistory((prev) => [...prev, { index: prev.length + 1, ...data }]);
    } catch (err) {
      console.error(err);
      alert('API error');
    }
  };

  // Simulate revenue comparison data
  useEffect(() => {
    if (history.length > 3) {
      // Calculate simulated revenue comparison
      const staticRevenue = history.reduce((sum, h) => sum + (parseFloat(priceInput) || 10) * h.demand_forecast, 0);
      const dynamicRevenue = history.reduce((sum, h) => sum + h.expected_revenue, 0);
      const lift = ((dynamicRevenue - staticRevenue) / staticRevenue * 100).toFixed(1);
      
      setSimulationData({
        static: staticRevenue.toFixed(2),
        dynamic: dynamicRevenue.toFixed(2),
        lift: lift
      });
      
      // Calculate performance metrics
      const prices = history.map(h => h.optimal_price);
      const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
      const priceVariance = Math.sqrt(prices.reduce((sum, p) => sum + Math.pow(p - avgPrice, 2), 0) / prices.length);
      const maxPriceChange = Math.max(...prices.slice(1).map((p, i) => Math.abs(p - prices[i]) / prices[i] * 100));
      
      setPerformanceMetrics({
        avgPrice: avgPrice.toFixed(2),
        priceStability: (100 - priceVariance).toFixed(1),
        maxPriceChange: maxPriceChange.toFixed(1)
      });
    }
  }, [history, priceInput]);

  return (
    <div style={{ padding: '1rem' }}>
      <h2>RL Pricing Insights</h2>
      
      {/* Input Form */}
      <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
        <label>
          Base price ($):
          <input
            type="number"
            step="0.01"
            value={priceInput}
            onChange={(e) => setPriceInput(e.target.value)}
            style={{ marginLeft: '0.5rem' }}
          />
        </label>
        <button type="submit" style={{ marginLeft: '1rem' }}>Get Optimal Price</button>
      </form>

      {/* Current Recommendation */}
      {optimal && (
        <div style={{ 
          backgroundColor: '#f0f8ff', 
          padding: '1rem', 
          borderRadius: '8px',
          marginBottom: '2rem'
        }}>
          <h3>Current Recommendation</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            <div>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#666' }}>Optimal Price</p>
              <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold', color: '#1f77b4' }}>
                ${optimal.optimal_price}
              </p>
            </div>
            <div>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#666' }}>Expected Revenue</p>
              <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold', color: '#2ca02c' }}>
                ${optimal.expected_revenue}
              </p>
            </div>
            <div>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#666' }}>Demand Forecast</p>
              <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold' }}>
                {optimal.demand_forecast}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      {performanceMetrics && (
        <div style={{ 
          backgroundColor: '#f5f5f5', 
          padding: '1rem', 
          borderRadius: '8px',
          marginBottom: '2rem'
        }}>
          <h3>Agent Performance Metrics</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            <div>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#666' }}>Average Price</p>
              <p style={{ margin: 0, fontSize: '1.3rem', fontWeight: 'bold' }}>
                ${performanceMetrics.avgPrice}
              </p>
            </div>
            <div>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#666' }}>Price Stability</p>
              <p style={{ margin: 0, fontSize: '1.3rem', fontWeight: 'bold', 
                color: performanceMetrics.priceStability > 85 ? '#2ca02c' : '#ff7f0e' }}>
                {performanceMetrics.priceStability}%
              </p>
            </div>
            <div>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#666' }}>Max Price Change</p>
              <p style={{ margin: 0, fontSize: '1.3rem', fontWeight: 'bold',
                color: performanceMetrics.maxPriceChange < 15 ? '#2ca02c' : '#d62728' }}>
                {performanceMetrics.maxPriceChange}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Revenue Simulation */}
      {simulationData && (
        <div style={{ marginBottom: '2rem' }}>
          <h3>Revenue Simulation: Dynamic vs Static Pricing</h3>
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <div style={{ flex: 1 }}>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={[
                  { name: 'Static', revenue: parseFloat(simulationData.static) },
                  { name: 'Dynamic (RL)', revenue: parseFloat(simulationData.dynamic) }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                  <Bar dataKey="revenue" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ 
              backgroundColor: simulationData.lift > 5 ? '#d4edda' : '#f8d7da',
              padding: '1rem',
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#666' }}>Revenue Lift</p>
              <p style={{ 
                margin: 0, 
                fontSize: '2rem', 
                fontWeight: 'bold',
                color: simulationData.lift > 5 ? '#155724' : '#721c24'
              }}>
                {simulationData.lift > 0 ? '+' : ''}{simulationData.lift}%
              </p>
              <p style={{ margin: 0, fontSize: '0.8rem', marginTop: '0.5rem' }}>
                {simulationData.lift > 5 ? '✅ Target Met' : '⚠️ Below Target'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Decision History */}
      {history.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Price Decisions Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="index" label={{ value: 'Decision #', position: 'insideBottom', offset: -5 }} />
              <YAxis yAxisId="left" label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }} />
              <YAxis yAxisId="right" orientation="right" label={{ value: 'Revenue ($)', angle: 90, position: 'insideRight' }} />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="optimal_price" stroke="#8884d8" name="Optimal Price" strokeWidth={2} />
              <Line yAxisId="right" type="monotone" dataKey="expected_revenue" stroke="#82ca9d" name="Expected Revenue" strokeWidth={2} />
              <Line yAxisId="left" type="monotone" dataKey="demand_forecast" stroke="#ff7f0e" name="Demand Forecast" strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
