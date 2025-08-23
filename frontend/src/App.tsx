/*
 * Market Simulation Frontend
 * 
 * This React app provides a visual interface for the market simulation API.
 * Now supports segmented market inputs and surplus calculation.
 * 
 * Setup Instructions:
 * 1. Start the backend: python -m uvicorn backend.main:app --reload --port 8001
 * 2. Start the frontend: cd frontend && npm install && npm run dev
 * 3. Open http://127.0.0.1:5173 in your browser
 * 
 * Features:
 * - Segmented market parameters (up to 3 segments for buyers and sellers)
 * - Distribution options (uniform or normal) for each segment
 * - Interactive chart showing demand and supply curves as step functions
 * - Equilibrium point visualization with reference lines
 * - Maximum total surplus calculation and display
 * - Real-time validation and error handling
 */

import { useState } from 'react';
import { Controls } from './components/Controls';
import { MarketChart } from './components/MarketChart';
import { fetchMarket, MarketParams, MarketResponse } from './api';

// Default market parameters using segments
const DEFAULT_PARAMS: MarketParams = {
  buyer_segments: [
    { n: 10, p_min: 10, p_max: 40 }
  ],
  seller_segments: [
    { n: 10, p_min: 5, p_max: 35 }
  ],
  seed: 42
};

function App() {
  const [params, setParams] = useState<MarketParams>(DEFAULT_PARAMS);
  const [response, setResponse] = useState<MarketResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await fetchMarket(params);
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Market Simulation</h1>
      <p>Generate supply and demand curves with segmented markets and find market equilibrium</p>
      
      <Controls
        params={params}
        onParamsChange={setParams}
        onGenerate={handleGenerate}
        loading={loading}
      />

      {error && (
        <div className="error" style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#ffebee' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading && (
        <div className="loading">
          Generating market simulation...
        </div>
      )}

      {response && (
        <>
          <MarketChart
            demand={response.demand}
            supply={response.supply}
            equilibrium={response.equilibrium}
            surplus={response.surplus}
          />
          
          <div className="equilibrium-info">
            <h3>Market Equilibrium</h3>
            <p>
              <strong>Quantity (Q*):</strong> {response.equilibrium.quantity} units
            </p>
            <p>
              <strong>Price (P*):</strong> ${response.equilibrium.price?.toFixed(2) ?? '—'}
            </p>
            <p>
              <strong>Maximum Total Surplus:</strong> ${response.surplus.total_max.toFixed(2)}
            </p>
            {response.equilibrium.quantity === 0 && (
              <p style={{ color: '#666', fontStyle: 'italic' }}>
                No trade occurs at these parameters - buyers' willingness to pay is too low relative to sellers' costs.
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default App;
