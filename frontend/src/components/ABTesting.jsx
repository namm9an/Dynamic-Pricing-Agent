import { useState, useEffect } from 'react';
import { api } from '../utils/api.js';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function ABTesting() {
  const [userGroup, setUserGroup] = useState(null);
  const [testResults, setTestResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState('');
  const [simulatedData, setSimulatedData] = useState(null);
  const [feedbackHistory, setFeedbackHistory] = useState([]);

  // Generate user ID on component mount
  useEffect(() => {
    const storedUserId = localStorage.getItem('ab_test_user_id');
    if (storedUserId) {
      setUserId(storedUserId);
      assignUserGroup(storedUserId);
    } else {
      const newUserId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setUserId(newUserId);
      localStorage.setItem('ab_test_user_id', newUserId);
      assignUserGroup(newUserId);
    }
  }, []);

  // Generate simulated A/B test results
  useEffect(() => {
    generateSimulatedResults();
    const interval = setInterval(generateSimulatedResults, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const assignUserGroup = async (id) => {
    try {
      setLoading(true);
      const response = await api.get(`/ab-test/${id}`);
      setUserGroup(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error assigning A/B test group:', error);
      setLoading(false);
      // Fallback: assign group locally
      const group = Math.random() < 0.5 ? 'test' : 'control';
      setUserGroup({
        user_id: id,
        ab_test_group: group,
        strategy: group === 'test' ? 'dynamic_pricing' : 'static_pricing',
        timestamp: new Date().toISOString()
      });
    }
  };

  const generateSimulatedResults = () => {
    // Simulate A/B test results with dynamic pricing showing better performance
    const controlMetrics = {
      conversion_rate: 2.3 + Math.random() * 0.5,
      revenue_per_session: 15.50 + Math.random() * 3,
      avg_order_value: 45.20 + Math.random() * 8,
      total_sessions: 1250 + Math.floor(Math.random() * 200),
      total_revenue: 19375 + Math.random() * 2000
    };

    const testMetrics = {
      conversion_rate: 2.8 + Math.random() * 0.6, // 20% better
      revenue_per_session: 19.20 + Math.random() * 4, // 25% better
      avg_order_value: 52.40 + Math.random() * 10, // 15% better
      total_sessions: 1200 + Math.floor(Math.random() * 200),
      total_revenue: 23040 + Math.random() * 2500 // Better overall revenue
    };

    const results = [
      {
        group: 'Control (Static)',
        ...controlMetrics,
        group_type: 'control'
      },
      {
        group: 'Test (Dynamic)',
        ...testMetrics,
        group_type: 'test'
      }
    ];

    setTestResults(results);

    // Calculate improvements
    const improvements = {
      conversion_rate: ((testMetrics.conversion_rate - controlMetrics.conversion_rate) / controlMetrics.conversion_rate * 100),
      revenue_per_session: ((testMetrics.revenue_per_session - controlMetrics.revenue_per_session) / controlMetrics.revenue_per_session * 100),
      avg_order_value: ((testMetrics.avg_order_value - controlMetrics.avg_order_value) / controlMetrics.avg_order_value * 100),
      total_revenue: ((testMetrics.total_revenue - controlMetrics.total_revenue) / controlMetrics.total_revenue * 100)
    };

    setSimulatedData({
      improvements,
      significance: 95.2, // Statistical significance
      runtime_days: 14,
      sample_size: controlMetrics.total_sessions + testMetrics.total_sessions
    });

    // Generate feedback history
    const now = new Date();
    const historyData = [];
    for (let i = 13; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      
      historyData.push({
        date: date.toLocaleDateString(),
        control_revenue: controlMetrics.total_revenue * (0.8 + Math.random() * 0.4) / 14,
        test_revenue: testMetrics.total_revenue * (0.8 + Math.random() * 0.4) / 14,
        control_conversions: controlMetrics.conversion_rate * (0.8 + Math.random() * 0.4),
        test_conversions: testMetrics.conversion_rate * (0.8 + Math.random() * 0.4)
      });
    }
    setFeedbackHistory(historyData);
  };

  const recordFeedback = async (outcome) => {
    try {
      const feedback = {
        price_set: outcome.price,
        actual_demand: outcome.demand,
        revenue_generated: outcome.revenue,
        product_id: 'PROD_001',
        location: 'US',
        ab_test_group: userGroup?.ab_test_group
      };

      await api.post('/record-outcome', feedback);
      console.log('Feedback recorded successfully');
    } catch (error) {
      console.error('Error recording feedback:', error);
    }
  };

  const simulateOutcome = () => {
    // Simulate a pricing outcome based on user's group
    const basePrice = 25 + Math.random() * 50;
    const isTestGroup = userGroup?.ab_test_group === 'test';
    
    // Test group (dynamic pricing) performs better
    const demand = isTestGroup ? 
      80 + Math.random() * 40 : 
      70 + Math.random() * 30;
    
    const finalPrice = isTestGroup ?
      basePrice * (0.9 + Math.random() * 0.2) : // Dynamic adjustment
      basePrice; // Static price
    
    const revenue = finalPrice * demand;

    recordFeedback({
      price: finalPrice,
      demand: demand,
      revenue: revenue
    });

    return { price: finalPrice, demand, revenue };
  };

  if (loading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{ fontSize: '1.2rem', color: '#666' }}>Setting up A/B test...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '1rem' }}>
      <h2 style={{ margin: '0 0 2rem 0' }}>🧪 A/B Testing Dashboard</h2>

      {/* User Group Assignment */}
      {userGroup && (
        <div style={{
          backgroundColor: userGroup.ab_test_group === 'test' ? '#e3f2fd' : '#f3e5f5',
          padding: '1.5rem',
          borderRadius: '12px',
          marginBottom: '2rem',
          border: `2px solid ${userGroup.ab_test_group === 'test' ? '#2196f3' : '#9c27b0'}`
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>Your Test Assignment</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>User ID</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 'bold', fontFamily: 'monospace' }}>
                {userGroup.user_id}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Test Group</div>
              <div style={{ 
                fontSize: '1.2rem', 
                fontWeight: 'bold',
                color: userGroup.ab_test_group === 'test' ? '#1976d2' : '#7b1fa2'
              }}>
                {userGroup.ab_test_group === 'test' ? '🧪 Test Group' : '🔒 Control Group'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Pricing Strategy</div>
              <div style={{ 
                fontSize: '1.2rem', 
                fontWeight: 'bold',
                color: userGroup.strategy === 'dynamic_pricing' ? '#2e7d32' : '#d84315'
              }}>
                {userGroup.strategy === 'dynamic_pricing' ? '🤖 Dynamic Pricing' : '📊 Static Pricing'}
              </div>
            </div>
          </div>
          
          <button
            onClick={simulateOutcome}
            style={{
              marginTop: '1rem',
              padding: '0.75rem 1.5rem',
              backgroundColor: userGroup.ab_test_group === 'test' ? '#2196f3' : '#9c27b0',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: 'bold'
            }}
          >
            🎯 Simulate Purchase Outcome
          </button>
        </div>
      )}

      {/* Test Results Overview */}
      {simulatedData && (
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          marginBottom: '2rem'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>📊 Test Results Summary</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Revenue Lift</div>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: 'bold',
                color: simulatedData.improvements.total_revenue > 0 ? '#4caf50' : '#f44336'
              }}>
                +{simulatedData.improvements.total_revenue.toFixed(1)}%
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Conversion Lift</div>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: 'bold',
                color: simulatedData.improvements.conversion_rate > 0 ? '#4caf50' : '#f44336'
              }}>
                +{simulatedData.improvements.conversion_rate.toFixed(1)}%
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Statistical Significance</div>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: 'bold',
                color: simulatedData.significance >= 95 ? '#4caf50' : '#ff9800'
              }}>
                {simulatedData.significance.toFixed(1)}%
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Test Duration</div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2196f3' }}>
                {simulatedData.runtime_days} days
              </div>
            </div>
          </div>

          <div style={{
            padding: '1rem',
            backgroundColor: simulatedData.improvements.total_revenue >= 5 ? '#e8f5e8' : '#fff3cd',
            borderRadius: '8px',
            border: `1px solid ${simulatedData.improvements.total_revenue >= 5 ? '#4caf50' : '#ff9800'}`
          }}>
            <div style={{ 
              fontWeight: 'bold',
              color: simulatedData.improvements.total_revenue >= 5 ? '#2e7d32' : '#856404'
            }}>
              {simulatedData.improvements.total_revenue >= 5 ? 
                '✅ Test is successful! Dynamic pricing shows significant improvement.' : 
                '⚠️ Test is ongoing. Results approaching significance threshold.'
              }
            </div>
            <div style={{ fontSize: '0.9rem', marginTop: '0.5rem', color: '#666' }}>
              Sample size: {simulatedData.sample_size.toLocaleString()} sessions
            </div>
          </div>
        </div>
      )}

      {/* Detailed Metrics Comparison */}
      {testResults.length > 0 && (
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          marginBottom: '2rem'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>📈 Detailed Metrics Comparison</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            {/* Conversion Rate Comparison */}
            <div>
              <h4 style={{ margin: '0 0 1rem 0', color: '#666', fontSize: '1rem' }}>Conversion Rate (%)</h4>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={testResults}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="group" />
                  <YAxis />
                  <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
                  <Bar dataKey="conversion_rate" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Revenue per Session */}
            <div>
              <h4 style={{ margin: '0 0 1rem 0', color: '#666', fontSize: '1rem' }}>Revenue per Session ($)</h4>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={testResults}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="group" />
                  <YAxis />
                  <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                  <Bar dataKey="revenue_per_session" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Metrics Table */}
          <div style={{ marginTop: '2rem' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ backgroundColor: '#f5f5f5' }}>
                  <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #ddd' }}>Metric</th>
                  <th style={{ padding: '0.75rem', textAlign: 'center', borderBottom: '2px solid #ddd' }}>Control</th>
                  <th style={{ padding: '0.75rem', textAlign: 'center', borderBottom: '2px solid #ddd' }}>Test</th>
                  <th style={{ padding: '0.75rem', textAlign: 'center', borderBottom: '2px solid #ddd' }}>Improvement</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { metric: 'Conversion Rate', key: 'conversion_rate', format: (v) => `${v.toFixed(2)}%` },
                  { metric: 'Revenue per Session', key: 'revenue_per_session', format: (v) => `$${v.toFixed(2)}` },
                  { metric: 'Average Order Value', key: 'avg_order_value', format: (v) => `$${v.toFixed(2)}` },
                  { metric: 'Total Revenue', key: 'total_revenue', format: (v) => `$${v.toLocaleString()}` }
                ].map((row, index) => {
                  const controlValue = testResults[0][row.key];
                  const testValue = testResults[1][row.key];
                  const improvement = ((testValue - controlValue) / controlValue * 100);
                  
                  return (
                    <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                      <td style={{ padding: '0.75rem', fontWeight: 'bold' }}>{row.metric}</td>
                      <td style={{ padding: '0.75rem', textAlign: 'center' }}>{row.format(controlValue)}</td>
                      <td style={{ padding: '0.75rem', textAlign: 'center' }}>{row.format(testValue)}</td>
                      <td style={{ 
                        padding: '0.75rem', 
                        textAlign: 'center',
                        color: improvement > 0 ? '#4caf50' : '#f44336',
                        fontWeight: 'bold'
                      }}>
                        {improvement > 0 ? '+' : ''}{improvement.toFixed(1)}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Performance Trends */}
      {feedbackHistory.length > 0 && (
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>📅 Performance Trends (Last 14 Days)</h3>
          
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={feedbackHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="control_revenue"
                stroke="#ff7300"
                strokeWidth={2}
                name="Control Revenue"
                strokeDasharray="5 5"
              />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="test_revenue"
                stroke="#387908"
                strokeWidth={2}
                name="Test Revenue"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="control_conversions"
                stroke="#8884d8"
                strokeWidth={2}
                name="Control Conversions"
                strokeDasharray="3 3"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="test_conversions"
                stroke="#82ca9d"
                strokeWidth={2}
                name="Test Conversions"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
