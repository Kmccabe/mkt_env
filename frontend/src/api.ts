// API types for market simulation with segmented inputs and surplus calculation
export interface Segment {
  n: number;
  p_min: number;  // Integer price
  p_max: number;  // Integer price
  dist?: "uniform" | "normal";
  mean?: number | null;
  sd?: number | null;
}

export interface PricePoint {
  q: number;
  p: number;  // Integer price
}

export interface MarketParams {
  // Legacy simple params (keep for fallback UI if needed)
  num_buyers?: number;
  num_sellers?: number;
  min_wtp?: number;
  max_wtp?: number;
  min_cost?: number;
  max_cost?: number;

  seed?: number | null;

  // New segmented inputs (if provided, backend uses these)
  buyer_segments?: Segment[];
  seller_segments?: Segment[];
}

export interface MarketResponse {
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

// API configuration with environment detection
const getBaseUrl = (): string => {
  // Type assertion for import.meta.env
  const env = (import.meta as any).env;
  
  // Check if VITE_API_URL is explicitly set (for production overrides)
  if (env?.VITE_API_URL) {
    return env.VITE_API_URL;
  }
  
  // Auto-detect based on environment
  if (env?.DEV) {
    // Development mode - use your local backend
    return "http://127.0.0.1:8001";
  } else {
    // Production mode - this will be replaced by students with their Railway URL
    // Students should set VITE_API_URL environment variable in Vercel
    return "https://your-railway-app.railway.app";
  }
};

export const BASE_URL = getBaseUrl();

/**
 * Fetch market simulation data from the backend
 * @param params Market parameters (may include segments or simple params)
 * @returns Market response with demand, supply, equilibrium, and surplus
 * @throws Error if the request fails
 */
export async function fetchMarket(params: MarketParams): Promise<MarketResponse> {
  try {
    const response = await fetch(`${BASE_URL}/market`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Market simulation failed: ${response.status} ${response.statusText}. ${errorText}`);
    }

    return response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error(`Network error: Unable to connect to backend at ${BASE_URL}`);
  }
}

/**
 * Check if the backend is healthy
 * @returns Promise that resolves to true if healthy
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

// Debug helper - log the current API URL (useful for troubleshooting)
if ((import.meta as any).env?.DEV) {  // ✅ Fixed with type assertion
  console.log(`🔗 API Base URL: ${BASE_URL}`);
}
