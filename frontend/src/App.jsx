import { useState, useEffect } from 'react';
import PricingDashboard from './components/PricingDashboard.jsx';
import SystemMonitoring from './components/SystemMonitoring.jsx';
import ABTesting from './components/ABTesting.jsx';
import { trackEngagement } from './utils/tracking.js';

export default function App() {
  const [activeTab, setActiveTab] = useState('pricing');
  const [systemHealth, setSystemHealth] = useState('loading');

  useEffect(() => {
    trackEngagement('app_loaded', { timestamp: new Date().toISOString() });
  }, []);

  const tabs = [
    { id: 'pricing', name: '💰 Pricing Agent', component: <PricingDashboard /> },
    { id: 'monitoring', name: '🔍 System Monitoring', component: <SystemMonitoring /> },
    { id: 'abtesting', name: '🧪 A/B Testing', component: <ABTesting /> }
  ];

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    trackEngagement('tab_change', { tab: tabId });
  };

  return (
    <div style={{ 
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    }}>
      {/* Header */}
      <header style={{
        backgroundColor: 'white',
        padding: '1rem 2rem',
        borderBottom: '1px solid #e0e0e0',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between'
        }}>
          <div>
            <h1 style={{ 
              margin: 0, 
              fontSize: '1.8rem', 
              color: '#1976d2',
              fontWeight: 'bold'
            }}>
              🤖 Dynamic Pricing Agent
            </h1>
            <p style={{ 
              margin: '0.25rem 0 0 0', 
              color: '#666', 
              fontSize: '0.9rem'
            }}>
              Phase 3: Production Deployment & Live Operations
            </p>
          </div>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '1rem'
          }}>
            <div style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#e8f5e8',
              borderRadius: '20px',
              border: '1px solid #4caf50',
              color: '#2e7d32',
              fontSize: '0.85rem',
              fontWeight: 'bold'
            }}>
              ✅ Production Ready
            </div>
            
            <div style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#e3f2fd',
              borderRadius: '20px',
              border: '1px solid #2196f3',
              color: '#1976d2',
              fontSize: '0.85rem',
              fontWeight: 'bold'
            }}>
              v3.0.0
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e0e0e0'
      }}>
        <div style={{
          display: 'flex',
          padding: '0 2rem'
        }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              style={{
                padding: '1rem 1.5rem',
                border: 'none',
                backgroundColor: 'transparent',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '500',
                color: activeTab === tab.id ? '#1976d2' : '#666',
                borderBottom: activeTab === tab.id ? '3px solid #1976d2' : '3px solid transparent',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                if (activeTab !== tab.id) {
                  e.target.style.color = '#1976d2';
                  e.target.style.backgroundColor = '#f5f5f5';
                }
              }}
              onMouseLeave={(e) => {
                if (activeTab !== tab.id) {
                  e.target.style.color = '#666';
                  e.target.style.backgroundColor = 'transparent';
                }
              }}
            >
              {tab.name}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main style={{
        padding: '2rem',
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        {tabs.find(tab => tab.id === activeTab)?.component}
      </main>

      {/* Footer */}
      <footer style={{
        backgroundColor: 'white',
        borderTop: '1px solid #e0e0e0',
        padding: '1rem 2rem',
        marginTop: '2rem',
        color: '#666',
        fontSize: '0.85rem',
        textAlign: 'center'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            © 2025 Dynamic Pricing Agent | Built with React + FastAPI + PyTorch
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <span>🚀 Deployed on Render + Vercel</span>
            <span>🔄 Auto-retraining enabled</span>
            <span>📊 A/B testing active</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
