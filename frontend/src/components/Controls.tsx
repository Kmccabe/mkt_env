import { useState } from 'react';
import { MarketParams, Segment } from '../api';

interface ControlsProps {
  params: MarketParams;
  onParamsChange: (params: MarketParams) => void;
  onGenerate: () => void;
  loading: boolean;
}

// Default segments for buyers and sellers
const DEFAULT_BUYER_SEGMENTS: Segment[] = [
  { n: 10, p_min: 10, p_max: 40 }
];

const DEFAULT_SELLER_SEGMENTS: Segment[] = [
  { n: 10, p_min: 5, p_max: 35 }
];

export function Controls({ params, onParamsChange, onGenerate, loading }: ControlsProps) {
  // Initialize segments if not present
  const [buyerSegments, setBuyerSegments] = useState<Segment[]>(
    params.buyer_segments || DEFAULT_BUYER_SEGMENTS
  );
  const [sellerSegments, setSellerSegments] = useState<Segment[]>(
    params.seller_segments || DEFAULT_SELLER_SEGMENTS
  );
  const [seed, setSeed] = useState<number | null>(params.seed || 42);

  const updateParams = () => {
    // Validate segments before updating params
    const validBuyerSegments = buyerSegments.filter(seg => seg.p_min <= seg.p_max);
    const validSellerSegments = sellerSegments.filter(seg => seg.p_min <= seg.p_max);
    
    // Debug logging
    if (buyerSegments.length !== validBuyerSegments.length || sellerSegments.length !== validSellerSegments.length) {
      console.warn('Invalid segments filtered out:', {
        buyerSegments,
        validBuyerSegments,
        sellerSegments,
        validSellerSegments
      });
    }
    
    const newParams: MarketParams = {
      buyer_segments: validBuyerSegments,
      seller_segments: validSellerSegments,
      seed: seed
    };
    onParamsChange(newParams);
  };

  const addBuyerSegment = () => {
    if (buyerSegments.length < 3) {
      // Ensure the new segment has valid p_min < p_max
      const newSegment: Segment = { n: 5, p_min: 20, p_max: 30 };
      const newSegments = [...buyerSegments, newSegment];
      setBuyerSegments(newSegments);
      updateParams();
    }
  };

  const removeBuyerSegment = (index: number) => {
    if (buyerSegments.length > 1) {
      const newSegments = buyerSegments.filter((_, i) => i !== index);
      setBuyerSegments(newSegments);
      updateParams();
    }
  };

  const addSellerSegment = () => {
    if (sellerSegments.length < 3) {
      // Ensure the new segment has valid p_min < p_max
      const newSegment: Segment = { n: 5, p_min: 15, p_max: 25 };
      const newSegments = [...sellerSegments, newSegment];
      setSellerSegments(newSegments);
      updateParams();
    }
  };

  const removeSellerSegment = (index: number) => {
    if (sellerSegments.length > 1) {
      const newSegments = sellerSegments.filter((_, i) => i !== index);
      setSellerSegments(newSegments);
      updateParams();
    }
  };

  const updateBuyerSegment = (index: number, field: keyof Segment, value: string | number) => {
    const newSegments = [...buyerSegments];
    const segment = { ...newSegments[index] };
    
    if (field === 'n') {
      segment.n = parseInt(value as string) || 0;
    } else if (field === 'p_min' || field === 'p_max') {
      const numValue = parseInt(value as string) || 0;
      
      // Prevent p_min from being greater than p_max
      if (field === 'p_min' && numValue > segment.p_max) {
        // Don't update if it would make p_min > p_max
        return;
      }
      if (field === 'p_max' && numValue < segment.p_min) {
        // Don't update if it would make p_max < p_min
        return;
      }
      
      segment[field] = numValue;
    } else if (field === 'dist') {
      segment.dist = value as "uniform" | "normal";
    } else if (field === 'mean' || field === 'sd') {
      const numValue = parseFloat(value as string);
      segment[field] = isNaN(numValue) ? null : numValue;
    }
    
    newSegments[index] = segment;
    setBuyerSegments(newSegments);
    updateParams();
  };

  const updateSellerSegment = (index: number, field: keyof Segment, value: string | number) => {
    const newSegments = [...sellerSegments];
    const segment = { ...newSegments[index] };
    
    if (field === 'n') {
      segment.n = parseInt(value as string) || 0;
    } else if (field === 'p_min' || field === 'p_max') {
      const numValue = parseInt(value as string) || 0;
      
      // Prevent p_min from being greater than p_max
      if (field === 'p_min' && numValue > segment.p_max) {
        // Don't update if it would make p_min > p_max
        return;
      }
      if (field === 'p_max' && numValue < segment.p_min) {
        // Don't update if it would make p_max < p_min
        return;
      }
      
      segment[field] = numValue;
    } else if (field === 'dist') {
      segment.dist = value as "uniform" | "normal";
    } else if (field === 'mean' || field === 'sd') {
      const numValue = parseFloat(value as string);
      segment[field] = isNaN(numValue) ? null : numValue;
    }
    
    newSegments[index] = segment;
    setSellerSegments(newSegments);
    updateParams();
  };

  const handleSeedChange = (value: string) => {
    const numValue = parseInt(value);
    const newSeed = isNaN(numValue) ? null : numValue;
    setSeed(newSeed);
    updateParams();
  };

  // Validation
  const buyerWarnings = buyerSegments.map(seg => seg.p_min > seg.p_max);
  const sellerWarnings = sellerSegments.map(seg => seg.p_min > seg.p_max);
  const hasWarnings = buyerWarnings.some(w => w) || sellerWarnings.some(w => w);
  
  // Check if any segments are invalid
  const hasInvalidSegments = buyerSegments.some(seg => seg.p_min > seg.p_max) || 
                            sellerSegments.some(seg => seg.p_min > seg.p_max);

  const renderSegment = (
    segment: Segment,
    index: number,
    isBuyer: boolean,
    updateFn: (index: number, field: keyof Segment, value: string | number) => void,
    removeFn: (index: number) => void,
    warnings: boolean[]
  ) => (
    <div key={index} className="segment" style={{ 
      border: '1px solid #ccc', 
      padding: '1rem', 
      margin: '0.5rem 0', 
      borderRadius: '8px',
      backgroundColor: warnings[index] ? '#fff3cd' : '#f8f9fa'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <h4 style={{ margin: 0 }}>Segment {index + 1}</h4>
        {((isBuyer && buyerSegments.length > 1) || (!isBuyer && sellerSegments.length > 1)) && (
          <button 
            onClick={() => removeFn(index)}
            style={{ 
              backgroundColor: '#dc3545', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              padding: '0.25rem 0.5rem',
              cursor: 'pointer'
            }}
          >
            Remove
          </button>
        )}
      </div>
      
      <div className="form-group">
        <label>Number of participants:</label>
        <input
          type="number"
          min="0"
          value={segment.n}
          onChange={(e) => updateFn(index, 'n', e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>Min price:</label>
        <input
          type="number"
          step="1"
          min="0"
          value={segment.p_min}
          onChange={(e) => updateFn(index, 'p_min', e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>Max price:</label>
        <input
          type="number"
          step="1"
          min="0"
          value={segment.p_max}
          onChange={(e) => updateFn(index, 'p_max', e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>Distribution:</label>
        <select
          value={segment.dist || 'uniform'}
          onChange={(e) => updateFn(index, 'dist', e.target.value)}
        >
          <option value="uniform">Uniform</option>
          <option value="normal">Normal</option>
        </select>
      </div>

      {segment.dist === 'normal' && (
        <>
          <div className="form-group">
            <label>Mean (optional):</label>
            <input
              type="number"
              step="0.01"
              placeholder="Auto-calculated if empty"
              value={segment.mean || ''}
              onChange={(e) => updateFn(index, 'mean', e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Standard Deviation (optional):</label>
            <input
              type="number"
              step="0.01"
              placeholder="Auto-calculated if empty"
              value={segment.sd || ''}
              onChange={(e) => updateFn(index, 'sd', e.target.value)}
            />
          </div>
        </>
      )}

      {warnings[index] && (
        <div className="warning" style={{ 
          color: '#d63384', 
          fontWeight: 'bold', 
          marginTop: '0.5rem',
          padding: '0.5rem',
          backgroundColor: '#f8d7da',
          borderRadius: '4px',
          border: '1px solid #f5c6cb'
        }}>
          ⚠️ Invalid: Min price ({segment.p_min}) cannot be greater than Max price ({segment.p_max})
        </div>
      )}
    </div>
  );

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <h2>Market Parameters</h2>
      
      {/* Buyer Segments */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3>Buyer Segments</h3>
          <button 
            onClick={addBuyerSegment}
            disabled={buyerSegments.length >= 3}
            style={{ 
              backgroundColor: '#28a745', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              padding: '0.5rem 1rem',
              cursor: buyerSegments.length >= 3 ? 'not-allowed' : 'pointer'
            }}
          >
            Add Segment
          </button>
        </div>
        {buyerSegments.map((segment, index) => 
          renderSegment(segment, index, true, updateBuyerSegment, removeBuyerSegment, buyerWarnings)
        )}
      </div>

      {/* Seller Segments */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3>Seller Segments</h3>
          <button 
            onClick={addSellerSegment}
            disabled={sellerSegments.length >= 3}
            style={{ 
              backgroundColor: '#28a745', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              padding: '0.5rem 1rem',
              cursor: sellerSegments.length >= 3 ? 'not-allowed' : 'pointer'
            }}
          >
            Add Segment
          </button>
        </div>
        {sellerSegments.map((segment, index) => 
          renderSegment(segment, index, false, updateSellerSegment, removeSellerSegment, sellerWarnings)
        )}
      </div>

      {/* Seed Input */}
      <div className="form-group">
        <label htmlFor="seed">Random Seed (optional):</label>
        <input
          id="seed"
          type="number"
          placeholder="Leave empty for random"
          value={seed || ''}
          onChange={(e) => handleSeedChange(e.target.value)}
        />
      </div>

      <button 
        onClick={onGenerate} 
        disabled={loading || hasWarnings || hasInvalidSegments}
        style={{ width: '100%', marginTop: '1rem' }}
      >
        {loading ? 'Generating...' : 'Generate Market'}
      </button>
    </div>
  );
}

