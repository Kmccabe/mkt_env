# Market Simulation API & Frontend

A complete full-stack application that simulates supply and demand markets with discrete buyers and sellers. Features a FastAPI backend for market calculations and a React + TypeScript frontend for interactive visualization.

## 🚀 Features

- **Enhanced Backend API**: Generate random buyers and sellers with advanced segmentation support
- **Market Logic**: Pure functions for sorting demand/supply curves and finding equilibrium
- **Interactive Frontend**: React + TypeScript interface with real-time chart visualization
- **Advanced Parameters**: Support for market segments with different price distributions
- **Performance Monitoring**: Built-in logging, rate limiting, and execution metrics
- **Production Ready**: Comprehensive error handling, validation, and configuration management

## 📊 New in Version 2.1

- **✨ Market Segments**: Define buyer/seller groups with custom price ranges and distributions
- **📈 Enhanced Analytics**: Total surplus calculations and market efficiency metrics
- **🛡️ Rate Limiting**: API protection against abuse (30 requests/minute)
- **📝 Comprehensive Logging**: Track API usage and performance
- **⚙️ Environment Configuration**: Easy setup with `.env` file support
- **🧪 Testing Suite**: Unit tests for reliable market logic
- **📋 Better Validation**: Detailed error messages and market feasibility checks

## 🏗️ Project Structure

```
mkt_env/
├── backend/              # FastAPI backend
│   ├── __init__.py      # Package initialization
│   ├── main.py          # FastAPI app and endpoints (enhanced)
│   ├── market.py        # Pure market logic functions (improved)
│   ├── models.py        # Pydantic data models (expanded)
│   └── config.py        # Configuration management (new)
├── frontend/            # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx              # Main app component
│   │   ├── api.ts               # API client and types
│   │   ├── index.css            # Styling
│   │   └── components/
│   │       ├── Controls.tsx     # Market parameter form
│   │       └── MarketChart.tsx  # Recharts visualization
│   ├── package.json             # Dependencies and scripts
│   ├── tsconfig.json            # TypeScript configuration
│   └── vite.config.ts           # Vite build configuration
├── requirements.txt             # Python production dependencies
├── requirements-dev.txt         # Development dependencies (new)
├── test_market.py              # Unit tests (new)
├── .env.example                # Environment variables template (new)
└── README.md                   # This file
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   
   # For development (includes testing tools):
   pip install -r requirements-dev.txt
   ```

2. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Run tests (optional but recommended):**
   ```bash
   python -m pytest tests/ -v
   ```

4. **Start the FastAPI server:**
   ```bash
   python -m uvicorn backend.main:app --reload --port 8001
   ```

   The backend will be available at:
   - **API Base**: http://127.0.0.1:8001
   - **Interactive Docs**: http://127.0.0.1:8001/docs
   - **OpenAPI Spec**: http://127.0.0.1:8001/openapi.json

### 2. Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at:
   - **Local**: http://localhost:5173/
   - **Network**: Use `--host` flag to expose to network

## 🔌 API Endpoints

### Health Check
```bash
GET /health
```
**Response:**
```json
{
  "status": "ok",
  "details": {
    "market_logic_test": "passed"
  }
}
```

### Market Simulation
```bash
POST /market
```

#### Simple Parameters (Legacy)
```json
{
  "num_buyers": 10,
  "num_sellers": 10,
  "min_wtp": 10,
  "max_wtp": 40,
  "min_cost": 5,
  "max_cost": 35,
  "seed": 42
}
```

#### Advanced Segmented Parameters (New!)
```json
{
  "seed": 123,
  "buyer_segments": [
    {
      "n": 6,
      "p_min": 30,
      "p_max": 40,
      "dist": "uniform"
    },
    {
      "n": 4,
      "p_min": 20,
      "p_max": 29,
      "dist": "normal",
      "mean": 25,
      "sd": 2
    }
  ],
  "seller_segments": [
    {
      "n": 5,
      "p_min": 10,
      "p_max": 15,
      "dist": "uniform"
    },
    {
      "n": 5,
      "p_min": 16,
      "p_max": 25,
      "dist": "normal"
    }
  ]
}
```

#### Enhanced Response
```json
{
  "demand": [{"q": 1, "p": 35}, {"q": 2, "p": 32}, ...],
  "supply": [{"q": 1, "p": 8}, {"q": 2, "p": 12}, ...],
  "equilibrium": {
    "quantity": 6,
    "price": 18.5
  },
  "surplus": {
    "total_max": 127.5
  },
  "metadata": {
    "execution_time_ms": 2.34,
    "total_buyers": 10,
    "total_sellers": 10,
    "trades_possible": true,
    "efficiency_ratio": 0.6
  }
}
```

## 📋 Example Usage

### Test Backend API
```bash
# Health check
curl http://127.0.0.1:8001/health

# Simple market simulation
curl -X POST http://127.0.0.1:8001/market \
  -H "Content-Type: application/json" \
  -d '{"num_buyers": 5, "num_sellers": 5, "seed": 42}'

# Advanced segmented market
curl -X POST http://127.0.0.1:8001/market \
  -H "Content-Type: application/json" \
  -d '{
    "seed": 123,
    "buyer_segments": [
      {"n": 6, "p_min": 30, "p_max": 40},
      {"n": 4, "p_min": 20, "p_max": 29}
    ],
    "seller_segments": [
      {"n": 5, "p_min": 10, "p_max": 15},
      {"n": 5, "p_min": 16, "p_max": 25}
    ]
  }'
```

### Test Frontend
1. Open http://localhost:5173/ in your browser
2. Choose between simple or segmented market parameters
3. Adjust parameters using the interactive form
4. Click "Generate Market" to create a new simulation
5. View the interactive chart with equilibrium analysis

## 🧮 Market Logic

The equilibrium algorithm:

1. **Build Participants**: Generate buyers and sellers from segments or simple parameters
2. **Sort Markets**: Buyers by WTP (high→low), sellers by cost (low→high)
3. **Find Matches**: Pair buyers with sellers where WTP ≥ cost
4. **Calculate Equilibrium**: 
   - **Quantity**: Number of successful matches
   - **Price**: Midpoint of marginal matched pair
5. **Compute Surplus**: Sum of (WTP - cost) for all traded units

### Market Segments
New segmented approach allows:
- **Multiple buyer/seller groups** with different price ranges
- **Distribution types**: Uniform or normal distribution within segments
- **Custom parameters**: Mean and standard deviation for normal distributions
- **Realistic modeling**: Better representation of heterogeneous markets

## 🎯 Frontend Features

- **Parameter Form**: Configure simple or segmented market parameters
- **Real-time Validation**: Input validation with helpful error messages
- **Interactive Charts**: Recharts-based visualization with step functions
- **Equilibrium Display**: Visual reference lines and equilibrium point
- **Performance Metrics**: Display execution time and market efficiency
- **Error Handling**: Clear error messages and loading states
- **Responsive Design**: Works on desktop and mobile devices

## 📦 Dependencies

### Backend
- `fastapi>=0.104.0` - Web framework
- `uvicorn[standard]>=0.24.0` - ASGI server  
- `pydantic>=2.0.0` - Data validation and settings
- `pydantic-settings>=2.0.0` - Configuration management
- `slowapi>=0.1.9` - Rate limiting

### Frontend
- `react>=18.2.0` - UI library
- `typescript>=5.2.2` - Type safety
- `recharts>=2.8.0` - Chart components
- `vite>=5.0.8` - Build tool and dev server

### Development
- `pytest>=7.4.0` - Testing framework
- `black>=23.0.0` - Code formatting
- `mypy>=1.5.0` - Type checking

## 🔧 Configuration

The API supports environment-based configuration. Create a `.env` file:

```bash
# Copy the example and customize
cp .env.example .env
```

Key configuration options:
- `ENVIRONMENT` - development/staging/production
- `DEFAULT_PORT` - API server port (default: 8001)
- `MAX_BUYERS/MAX_SELLERS` - Participant limits
- `RATE_LIMIT_REQUESTS` - API rate limit per minute
- `CORS_ORIGINS` - Allowed frontend origins
- `LOG_LEVEL` - Logging verbosity

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run with coverage report (install pytest-cov first)
pip install pytest-cov
python -m pytest tests/ --cov=backend --cov-report=html

# Run specific test class
python -m pytest tests/test_market.py::TestEquilibrium -v

# Run tests with specific markers
python -m pytest tests/ -m "unit" -v
```

Tests cover:
- Equilibrium finding algorithms
- Market construction from parameters
- Surplus calculations
- Input validation
- Edge cases and error handling

## 🏗️ Development

### Backend Development
- **Pure functions** in `backend/market.py` for easy testing
- **Type hints** throughout for better IDE support
- **Comprehensive logging** for debugging and monitoring
- **Modular architecture** for easy extension

### Frontend Development
- **TypeScript interfaces** match backend API exactly
- **Component-based architecture** for maintainability
- **Hot reload** during development with Vite
- **Modern React patterns** with hooks and functional components

## 🚨 Troubleshooting

### Port Conflicts
If port 8001 is in use:
```bash
python -m uvicorn backend.main:app --reload --port 8002
# Update frontend/src/api.ts with new port
```

### Frontend Won't Start
```bash
cd frontend
npm install
npm run dev
```

### API Connection Issues
Verify both servers are running:
- Backend health: http://127.0.0.1:8001/health
- Frontend: http://localhost:5173/

### Rate Limiting
If you hit the rate limit (30 requests/minute), either:
- Wait a minute for the limit to reset
- Increase `RATE_LIMIT_REQUESTS` in your `.env` file

### Environment Issues
- Check `.env` file syntax (no spaces around `=`)
- Verify Python version compatibility (3.8+)
- Clear browser cache if frontend behaves unexpectedly

## 🔮 Future Enhancements

Potential features for future versions:
- **Market History**: Store and retrieve simulation results
- **Advanced Auction Types**: Dutch auctions, sealed bids
- **Real-time Updates**: WebSocket support for live simulations  
- **Data Export**: CSV/JSON download capabilities
- **Advanced Analytics**: Market concentration metrics
- **Authentication**: User accounts and simulation history

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🎉 Getting Started Quick Guide

1. **Clone and setup:**
   ```bash
   git clone <your-repo>
   cd mkt_env
   pip install -r requirements.txt
   ```

2. **Start backend:**
   ```bash
   python -m uvicorn backend.main:app --reload --port 8001
   ```

3. **Start frontend:**
   ```bash
   cd frontend && npm install && npm run dev
   ```

4. **Test it out:**
   - Visit http://localhost:5173/
   - Try a simple market simulation
   - Explore the segmented market features!

Happy Building! 🚀