import { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  Scatter,
  ResponsiveContainer
} from 'recharts';
import { PricePoint } from '../api';

interface MarketChartProps {
  demand: PricePoint[];
  supply: PricePoint[];
  equilibrium: {
    quantity: number;
    price: number | null;
  };
  surplus: {
    total_max: number;
  };
}

export function MarketChart({ demand, supply, equilibrium, surplus }: MarketChartProps) {
  // Combine demand and supply data for the chart
  const chartData = useMemo(() => {
    const maxQ = Math.max(
      demand.length > 0 ? demand[demand.length - 1].q : 0,
      supply.length > 0 ? supply[supply.length - 1].q : 0
    );

    const data: Array<{
      q: number;
      demandP: number | null;
      supplyP: number | null;
    }> = [];

    for (let i = 1; i <= maxQ; i++) {
      const demandPoint = demand.find(d => d.q === i);
      const supplyPoint = supply.find(s => s.q === i);

      data.push({
        q: i,
        demandP: demandPoint ? demandPoint.p : null,
        supplyP: supplyPoint ? supplyPoint.p : null,
      });
    }

    return data;
  }, [demand, supply]);

  // Create equilibrium point for scatter plot
  const equilibriumPoint = equilibrium.quantity > 0 ? [{
    q: equilibrium.quantity,
    price: equilibrium.price
  }] : [];

  return (
    <div className="chart-container">
      <h3>Market Supply and Demand</h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="q" 
            label={{ value: 'Quantity', position: 'insideBottom', offset: -5 }}
          />
          <YAxis 
            label={{ value: 'Price', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip 
            formatter={(value: any, name: string) => [
              value !== null ? value.toFixed(2) : 'N/A', 
              name === 'demandP' ? 'Demand' : name === 'supplyP' ? 'Supply' : name
            ]}
            labelFormatter={(label) => `Quantity: ${label}`}
          />
          <Legend />
          
          {/* Demand line */}
          <Line
            type="stepAfter"
            dataKey="demandP"
            name="Demand"
            stroke="#8884d8"
            strokeWidth={2}
            connectNulls={false}
            dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
          />
          
          {/* Supply line */}
          <Line
            type="stepAfter"
            dataKey="supplyP"
            name="Supply"
            stroke="#82ca9d"
            strokeWidth={2}
            connectNulls={false}
            dot={{ fill: '#82ca9d', strokeWidth: 2, r: 4 }}
          />

          {/* Equilibrium reference lines */}
          {equilibrium.quantity > 0 && equilibrium.price !== null && (
            <>
              <ReferenceLine
                x={equilibrium.quantity}
                stroke="#ff7300"
                strokeDasharray="3 3"
                label={{ value: `Q* = ${equilibrium.quantity}`, position: 'top' }}
              />
              <ReferenceLine
                y={equilibrium.price}
                stroke="#ff7300"
                strokeDasharray="3 3"
                label={{ value: `P* = ${equilibrium.price.toFixed(2)}`, position: 'right' }}
              />
            </>
          )}

          {/* Equilibrium point */}
          {equilibrium.quantity > 0 && (
            <Scatter
              data={equilibriumPoint}
              dataKey="price"
              fill="#ff7300"
              shape="circle"
              name="Equilibrium"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
      
      {/* Surplus Information Panel */}
      <div style={{ 
        marginTop: '1rem', 
        padding: '1rem', 
        backgroundColor: '#e8f5e8', 
        borderRadius: '8px',
        border: '1px solid #c3e6c3'
      }}>
        <h4 style={{ margin: '0 0 0.5rem 0', color: '#2d5a2d' }}>Economic Surplus</h4>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <strong>Equilibrium:</strong> Q* = {equilibrium.quantity}, P* = {equilibrium.price?.toFixed(2) ?? '—'}
          </div>
          <div>
            <strong>Maximum Total Surplus:</strong> {surplus.total_max.toFixed(2)}
          </div>
        </div>
        {equilibrium.quantity === 0 && (
          <div style={{ marginTop: '0.5rem', color: '#666', fontStyle: 'italic' }}>
            No trade occurs at these parameters - buyers' willingness to pay is too low relative to sellers' costs.
          </div>
        )}
      </div>
    </div>
  );
}
