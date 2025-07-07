# Dynamic Pricing Agent

![Dynamic Pricing](https://img.shields.io/badge/AI-Dynamic%20Pricing-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![ML](https://img.shields.io/badge/ML-PyTorch%20%7C%20RL-orange)

An intelligent dynamic pricing system that combines **demand forecasting** and **reinforcement learning** to optimize pricing strategies in real-time. Built with modern AI/ML technologies for enterprise-grade performance.

## 🚀 Overview

This system automatically adjusts prices based on predicted demand patterns, achieving **25%+ revenue improvements** over static pricing through:

- **LSTM Neural Networks** for accurate demand forecasting
- **PPO Reinforcement Learning** for optimal pricing decisions
- **Real-time API** for instant pricing recommendations
- **Interactive Dashboard** for monitoring and insights

## ✨ Features

### 🧠 AI-Powered Forecasting
- **LSTM Neural Network** trained on historical sales data
- **Multi-feature Input**: price, seasonality, external factors
- **7-day sequence prediction** with proven accuracy
- **Automatic fallback** strategies for reliability

### 🎯 Reinforcement Learning Optimization
- **PPO (Proximal Policy Optimization)** agent
- **Custom reward shaping** for revenue maximization
- **Price stability controls** to prevent extreme changes
- **Continuous learning** from market feedback

### 🌐 Production-Ready API
- **FastAPI** backend with async performance
- **RESTful endpoints** for easy integration
- **Comprehensive error handling** and validation
- **Health monitoring** and logging
- **Production deployment** on Render.com

### 📊 Interactive Dashboard
- **Real-time pricing insights** and recommendations
- **Performance analytics** and revenue comparisons
- **Visual charts** showing pricing decisions over time
- **Agent metrics** for monitoring ML performance
- **Deployed on Vercel** with production optimizations

### 🔍 System Monitoring & Alerting
- **Real-time health monitoring** with comprehensive metrics
- **Performance tracking** (response times, error rates, uptime)
- **Model performance analytics** and accuracy monitoring
- **Automated alerting** for system degradation

### 🧪 A/B Testing Framework
- **Automated user group assignment** with consistent bucketing
- **Statistical significance testing** with confidence intervals
- **Real-time performance comparison** between strategies
- **Revenue impact tracking** and conversion analytics

### 🔄 Automated Retraining Pipeline
- **Daily model retraining** based on feedback data
- **Incremental learning** to adapt to market changes
- **Model validation** before deployment
- **Rollback capabilities** for failed updates

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   ML Models     │
│                 │    │                  │    │                 │
│ ├─ Dashboard    │◄──►│ ├─ FastAPI       │◄──►│ ├─ LSTM         │
│ ├─ Analytics    │    │ ├─ Pricing API   │    │ ├─ PPO Agent    │
│ └─ Monitoring   │    │ └─ Health Check  │    │ └─ Simulator    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚦 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/namm9an/Dynamic-Pricing-Agent.git
cd Dynamic-Pricing-Agent
```

### 2. Backend Setup
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Train models (optional - models auto-train on first run)
python backend/train_demand.py
python backend/train_agent.py

# Start API server
uvicorn backend.app:app --reload
```

### 3. Frontend Setup
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

### 4. Access Application
- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📡 API Reference

### Demand Forecasting
```http
POST /predict-demand
Content-Type: application/json

{
  "price": 49.99,
  "location": "New York",
  "product_id": "PROD_001"
}
```

**Response:**
```json
{
  "predicted_demand": 99.99,
  "price": 49.99,
  "location": "New York",
  "product_id": "PROD_001",
  "model_version": "1.0-lstm"
}
```

### Optimal Pricing
```http
POST /get-optimal-price
Content-Type: application/json

{
  "base_price": 25.0,
  "product_id": "PROD_001",
  "location": "US"
}
```

**Response:**
```json
{
  "optimal_price": 37.5,
  "expected_revenue": 3000.0,
  "demand_forecast": 80.0
}
```

## 🧪 Performance Results

### Revenue Optimization
- **25.1% Revenue Lift** over static pricing
- **1.0% Average Price Change** (excellent stability)
- **Sub-200ms Response Time** for real-time decisions

### Model Accuracy
- **LSTM Demand Model**: MAE 16.32
- **PPO Agent**: 25%+ improvement over baseline
- **Price Stability**: <15% variance maintained

## 🛠️ Tech Stack

### Backend
- **Python 3.10+** - Core language
- **FastAPI** - High-performance web framework
- **PyTorch** - Deep learning framework
- **Stable-Baselines3** - Reinforcement learning
- **Pandas/NumPy** - Data processing
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI framework
- **Vite** - Fast build tool
- **Recharts** - Data visualization
- **Axios** - HTTP client

### Machine Learning
- **LSTM Networks** - Time series forecasting
- **PPO Algorithm** - Reinforcement learning
- **Gymnasium** - RL environment framework
- **Custom Reward Shaping** - Performance optimization

## 📂 Project Structure

```
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── pricing_engine/
│   │   ├── demand_model.py    # LSTM forecasting model
│   │   ├── rl_agent.py        # PPO pricing agent
│   │   ├── rl_env.py          # Custom RL environment
│   │   └── simulator.py       # Performance simulation
│   ├── train_demand.py        # Demand model training
│   ├── train_agent.py         # RL agent training
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── PricingDashboard.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json           # Node dependencies
├── models/                    # Trained ML models
└── README.md
```

## 🔧 Development

### Training New Models
```bash
# Train demand forecasting model
python backend/train_demand.py

# Train reinforcement learning agent
python backend/train_agent.py --steps 20000

# Evaluate performance
python backend/evaluate_performance.py
```

### Testing
```bash
# Test all models
python backend/test_models.py

# Validate system
python backend/validate_system.py
```

### Model Performance
```bash
# Generate performance reports
python backend/evaluate_models.py --plot
```

## 🚀 Deployment

### Production Setup
1. **Environment Variables**: Configure `.env` file
2. **Model Training**: Ensure models are trained
3. **API Deployment**: Deploy FastAPI with Gunicorn/Uvicorn
4. **Frontend Build**: `npm run build` and serve static files
5. **Monitoring**: Set up logging and health checks

### Docker Support
```bash
# Build and run with Docker
docker-compose up --build
```

## 📈 Business Impact

### Key Metrics
- **Revenue Optimization**: 25%+ improvement over static pricing
- **Response Time**: <200ms for real-time pricing decisions
- **Price Stability**: Controlled changes with <15% variance
- **Scalability**: Handles 10+ requests/second

### Use Cases
- **E-commerce**: Dynamic product pricing
- **SaaS**: Subscription tier optimization
- **Retail**: Real-time price adjustments
- **Marketplace**: Competitive pricing strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions and support:
- Create an [issue](https://github.com/namm9an/Dynamic-Pricing-Agent/issues)
- Email: [your-email@example.com]

---

**Built with ❤️ for intelligent pricing optimization**
