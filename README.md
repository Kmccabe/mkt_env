# Market Simulation API & Frontend

A complete full-stack application that simulates supply and demand markets with discrete buyers and sellers. Features a FastAPI backend for market calculations and a React + TypeScript frontend for interactive visualization.

## Features

- **Backend API**: Generate random buyers and sellers, calculate demand/supply schedules, find market equilibrium
- **Frontend Interface**: Interactive form for market parameters, real-time chart visualization using Recharts
- **Market Logic**: Pure functions for sorting demand/supply curves and finding equilibrium quantity/price
- **Visualization**: Step-function charts showing demand and supply curves with equilibrium point and reference lines

## Project Structure

```
new_cursor/
├── backend/           # FastAPI backend
│   ├── __init__.py   # Package initialization
│   ├── main.py       # FastAPI app and endpoints
│   ├── market.py     # Pure market logic functions
│   └── models.py     # Pydantic data models
├── frontend/         # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx           # Main app component
│   │   ├── api.ts            # API client and types
│   │   ├── index.css         # Styling
│   │   └── components/
│   │       ├── Controls.tsx  # Market parameter form
│   │       └── MarketChart.tsx # Recharts visualization
│   ├── package.json          # Dependencies and scripts
│   ├── tsconfig.json         # TypeScript configuration
│   └── vite.config.ts        # Vite build configuration
├── requirements.txt          # Python backend dependencies
└── README.md                # This file
```

## Setup Instructions

### 1. Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the FastAPI server:**
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

## API Endpoints

### Health Check
```bash
GET /health
```
Returns: `{"status": "ok"}`

### Market Simulation
```bash
POST /market
```

**Request body** (all fields optional with sensible defaults):
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

**Response:**
```json
{
  "demand": [
    {"q": 1, "p": 35},
    {"q": 2, "p": 32},
    ...
  ],
  "supply": [
    {"q": 1, "p": 8},
    {"q": 2, "p": 12},
    ...
  ],
  "equilibrium": {
    "quantity": 6,
    "price": 18.5
  }
}
```

## Example Usage

### Test Backend API
```bash
# Health check
curl http://127.0.0.1:8001/health

# Market simulation
curl -X POST http://127.0.0.1:8001/market \
  -H "Content-Type: application/json" \
  -d '{"num_buyers": 5, "num_sellers": 5, "seed": 42}'
```

### Test Frontend
1. Open http://localhost:5173/ in your browser
2. Adjust market parameters using the form
3. Click "Generate Market" to create a new simulation
4. View the interactive chart and equilibrium results

## Market Logic

The equilibrium is found by:
1. **Sorting buyers** by WTP (high to low) → demand curve
2. **Sorting sellers** by cost (low to high) → supply curve
3. **Matching buyers and sellers** where WTP ≥ cost
4. **Equilibrium quantity** = number of successful matches
5. **Equilibrium price** = midpoint of the marginal matched pair

## Frontend Features

- **Parameter Form**: Configure all market simulation parameters with validation
- **Real-time Validation**: Warnings for invalid min/max ranges
- **Interactive Charts**: Recharts-based visualization with step functions
- **Equilibrium Display**: Visual reference lines and equilibrium point
- **Error Handling**: Clear error messages and loading states
- **Responsive Design**: Works on desktop and mobile devices

## Dependencies

### Backend
- `fastapi>=0.104.0` - Web framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `pydantic>=2.0.0` - Data validation

### Frontend
- `react>=18.2.0` - UI library
- `typescript>=5.2.2` - Type safety
- `recharts>=2.8.0` - Chart components
- `vite>=5.0.8` - Build tool and dev server

## Development

### Backend Development
- All market logic is pure functions in `backend/market.py`
- Easy to test and extend with new market models
- Automatic API documentation with FastAPI

### Frontend Development
- TypeScript interfaces match backend API exactly
- Component-based architecture for easy maintenance
- Hot reload during development with Vite

## Troubleshooting

### Port Conflicts
If port 8001 is in use, use a different port:
```bash
python -m uvicorn backend.main:app --reload --port 8002
```
Then update `frontend/src/api.ts` with the new port.

### Frontend Won't Start
Ensure you're in the `frontend` directory:
```bash
cd frontend
npm install
npm run dev
```

### API Connection Issues
Check that both servers are running:
- Backend: http://127.0.0.1:8001/health
- Frontend: http://localhost:5173/

## License

This project is licensed under the [MIT License](LICENSE).