import { useState, useEffect } from 'react';
import { api } from '../utils/api.js';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function SystemMonitoring() {
  const [metrics, setMetrics] = useState(null);
  const [healthHistory, setHealthHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [realTimeMode, setRealTimeMode] = useState(false);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, realTimeMode ? 5000 : 30000); // 5s in real-time mode, 30s otherwise
    return () => clearInterval(interval);
  }, [realTimeMode]);

  const fetchMetrics = async () => {
    try {
      const response = await api.get('/metrics');
      const newMetrics = response.data;
      
      setMetrics(newMetrics);
      
      // Add to health history for trending
      setHealthHistory(prev => {
        const newHistory = [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          error_rate: newMetrics.system_health.error_rate,
          avg_response_time: newMetrics.system_health.avg_response_time,
          total_requests: newMetrics.system_health.total_requests
        }];
        
        // Keep only last 20 data points
        return newHistory.slice(-20);
      });
      
      setLoading(false);
      setError(null);
    } catch (err) {
      setError('Failed to fetch system metrics');
      setLoading(false);
      console.error('Error fetching metrics:', err);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{ fontSize: '1.2rem', color: '#666' }}>Loading system metrics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        padding: '2rem', 
        backgroundColor: '#ffebee', 
        borderRadius: '8px',
        border: '1px solid #f44336'
      }}>
        <h3 style={{ color: '#d32f2f', margin: '0 0 1rem 0' }}>⚠️ Monitoring Error</h3>
        <p style={{ margin: 0, color: '#666' }}>{error}</p>
        <button 
          onClick={fetchMetrics}
          style={{
            marginTop: '1rem',
            padding: '0.5rem 1rem',
            backgroundColor: '#f44336',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  const systemHealth = metrics.system_health;
  const modelPerf = metrics.model_performance;
  const feedbackLoop = metrics.feedback_loop;

  // Calculate health score
  const healthScore = Math.round(
    (systemHealth.error_rate < 5 ? 40 : 0) +
    (systemHealth.avg_response_time < 500 ? 30 : 0) +
    (modelPerf.model_status === 'loaded' ? 20 : 0) +
    (feedbackLoop.total_feedback_records > 0 ? 10 : 0)
  );

  const healthData = [
    { name: 'Healthy', value: healthScore },
    { name: 'Issues', value: 100 - healthScore }
  ];

  return (
    <div style={{ padding: '1rem' }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '2rem'
      }}>
        <h2 style={{ margin: 0 }}>🔍 System Monitoring</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <input
              type="checkbox"
              checked={realTimeMode}
              onChange={(e) => setRealTimeMode(e.target.checked)}
            />
            Real-time monitoring
          </label>
          <div style={{
            padding: '0.5rem 1rem',
            borderRadius: '20px',
            backgroundColor: systemHealth.status === 'healthy' ? '#e8f5e8' : '#fff3cd',
            color: systemHealth.status === 'healthy' ? '#2e7d32' : '#856404',
            fontWeight: 'bold',
            fontSize: '0.9rem'
          }}>
            {systemHealth.status === 'healthy' ? '✅ Healthy' : '⚠️ Degraded'}
          </div>
        </div>
      </div>

      {/* System Health Overview */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '1.5rem',
        marginBottom: '2rem'
      }}>
        {/* Health Score */}
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          textAlign: 'center'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>Overall Health</h3>
          <ResponsiveContainer width="100%" height={150}>
            <PieChart>
              <Pie
                data={healthData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={60}
                dataKey="value"
                startAngle={90}
                endAngle={450}
              >
                {healthData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={index === 0 ? '#4caf50' : '#ff9800'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ 
            fontSize: '2rem', 
            fontWeight: 'bold',
            color: healthScore >= 80 ? '#4caf50' : healthScore >= 60 ? '#ff9800' : '#f44336'
          }}>
            {healthScore}%
          </div>
        </div>

        {/* Key Metrics */}
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>Key Metrics</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Error Rate</div>
              <div style={{ 
                fontSize: '1.5rem', 
                fontWeight: 'bold',
                color: systemHealth.error_rate < 5 ? '#4caf50' : '#f44336'
              }}>
                {systemHealth.error_rate.toFixed(2)}%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Avg Response</div>
              <div style={{ 
                fontSize: '1.5rem', 
                fontWeight: 'bold',
                color: systemHealth.avg_response_time < 500 ? '#4caf50' : '#ff9800'
              }}>
                {systemHealth.avg_response_time.toFixed(0)}ms
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Total Requests</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#2196f3' }}>
                {systemHealth.total_requests.toLocaleString()}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Uptime</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#4caf50' }}>
                {systemHealth.uptime_hours.toFixed(1)}h
              </div>
            </div>
          </div>
        </div>

        {/* Model Performance */}
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>Model Performance</h3>
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              marginBottom: '0.5rem'
            }}>
              <span style={{ fontSize: '0.9rem', color: '#666' }}>Model Status</span>
              <span style={{
                padding: '0.25rem 0.75rem',
                borderRadius: '12px',
                fontSize: '0.8rem',
                fontWeight: 'bold',
                backgroundColor: modelPerf.model_status === 'loaded' ? '#e8f5e8' : '#fff3cd',
                color: modelPerf.model_status === 'loaded' ? '#2e7d32' : '#856404'
              }}>
                {modelPerf.model_status === 'loaded' ? '🤖 Loaded' : '⚠️ Fallback'}
              </span>
            </div>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              marginBottom: '0.5rem'
            }}>
              <span style={{ fontSize: '0.9rem', color: '#666' }}>PyTorch Available</span>
              <span style={{ 
                color: modelPerf.torch_available ? '#4caf50' : '#f44336',
                fontWeight: 'bold'
              }}>
                {modelPerf.torch_available ? '✅' : '❌'}
              </span>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Predictions</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#9c27b0' }}>
                {modelPerf.total_predictions}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Avg Revenue</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#4caf50' }}>
                ${modelPerf.avg_revenue_per_decision.toFixed(0)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Trends */}
      {healthHistory.length > 5 && (
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          marginBottom: '2rem'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>Performance Trends</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={healthHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="error_rate"
                stackId="1"
                stroke="#f44336"
                fill="#f44336"
                fillOpacity={0.6}
                name="Error Rate (%)"
              />
              <Area
                yAxisId="right"
                type="monotone"
                dataKey="avg_response_time"
                stackId="2"
                stroke="#2196f3"
                fill="#2196f3"
                fillOpacity={0.6}
                name="Response Time (ms)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Feedback Loop Status */}
      <div style={{
        backgroundColor: 'white',
        padding: '1.5rem',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>🔄 Feedback Loop</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <div style={{ fontSize: '0.9rem', color: '#666' }}>Total Feedback Records</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#ff5722' }}>
              {feedbackLoop.total_feedback_records.toLocaleString()}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '0.9rem', color: '#666' }}>Recent Feedback</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#3f51b5' }}>
              {feedbackLoop.recent_feedback_count}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '0.9rem', color: '#666' }}>Last Feedback</div>
            <div style={{ fontSize: '1rem', fontWeight: 'bold', color: '#607d8b' }}>
              {feedbackLoop.last_feedback_time ? 
                new Date(feedbackLoop.last_feedback_time).toLocaleTimeString() : 
                'No data'
              }
            </div>
          </div>
        </div>
        
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          backgroundColor: feedbackLoop.total_feedback_records >= 100 ? '#e8f5e8' : '#fff3cd',
          borderRadius: '8px',
          border: `1px solid ${feedbackLoop.total_feedback_records >= 100 ? '#4caf50' : '#ff9800'}`
        }}>
          <div style={{ 
            fontWeight: 'bold',
            color: feedbackLoop.total_feedback_records >= 100 ? '#2e7d32' : '#856404'
          }}>
            {feedbackLoop.total_feedback_records >= 100 ? 
              '✅ Sufficient feedback data for retraining' : 
              '⚠️ Collecting feedback data for next retraining cycle'
            }
          </div>
          <div style={{ fontSize: '0.9rem', marginTop: '0.5rem', color: '#666' }}>
            {100 - feedbackLoop.total_feedback_records % 100} more records needed for next retraining trigger
          </div>
        </div>
      </div>
    </div>
  );
}
