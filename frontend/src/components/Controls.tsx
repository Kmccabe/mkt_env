import { useEffect, useState } from 'react';
import { MarketParams, Segment } from '../api';

interface ControlsProps {
  params: MarketParams;
  onParamsChange: (params: MarketParams) => void;
  onGenerate: () => void;
  loading: boolean;
}

// ----- store strings while typing -----
type SegmentForm = {
  n: string;
  p_min: string;
  p_max: string;
  dist: 'uniform' | 'normal';
  mean: string; // '' = unset
  sd: string;   // '' = unset
};

// defaults (numeric)
const DEFAULT_BUYER_SEGMENTS: Segment[] = [{ n: 10, p_min: 10, p_max: 40, dist: 'uniform' }];
const DEFAULT_SELLER_SEGMENTS: Segment[] = [{ n: 10, p_min: 5, p_max: 35, dist: 'uniform' }];

// conversion helpers
const toFormSegment = (s: Segment): SegmentForm => ({
  n: String(s.n ?? 0),
  p_min: String(s.p_min ?? 0),
  p_max: String(s.p_max ?? 0),
  dist: (s.dist ?? 'uniform') as 'uniform' | 'normal',
  mean: s.mean == null ? '' : String(s.mean),
  sd: s.sd == null ? '' : String(s.sd),
});
const toInt = (v: string, fallback = 0) => {
  const n = parseInt(v, 10);
  return Number.isFinite(n) ? n : fallback;
};
const toNumOrNull = (v: string) => (v === '' ? null : Number(v));
const toPayloadSegment = (f: SegmentForm): Segment => ({
  n: toInt(f.n),
  p_min: toInt(f.p_min),
  p_max: toInt(f.p_max === '' ? f.p_min : f.p_max),
  dist: f.dist,
  mean: toNumOrNull(f.mean) ?? undefined,
  sd: toNumOrNull(f.sd) ?? undefined,
});

export function Controls({ params, onParamsChange, onGenerate, loading }: ControlsProps) {
  // local form state as strings
  const [buyerSegs, setBuyerSegs] = useState<SegmentForm[]>(
    (params.buyer_segments ?? DEFAULT_BUYER_SEGMENTS).map(toFormSegment)
  );
  const [sellerSegs, setSellerSegs] = useState<SegmentForm[]>(
    (params.seller_segments ?? DEFAULT_SELLER_SEGMENTS).map(toFormSegment)
  );
  const [seedStr, setSeedStr] = useState<string>(params.seed == null ? '' : String(params.seed));

  // initialize from parent ONCE (don’t overwrite while typing)
  useEffect(() => {
    if (params.buyer_segments) setBuyerSegs(params.buyer_segments.map(toFormSegment));
    if (params.seller_segments) setSellerSegs(params.seller_segments.map(toFormSegment));
    setSeedStr(params.seed == null ? '' : String(params.seed));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // mount-only

  // add/remove (do NOT push up while typing)
  const addBuyerSegment = () => {
    if (buyerSegs.length >= 3) return;
    const next = [...buyerSegs, toFormSegment({ n: 5, p_min: 20, p_max: 30, dist: 'uniform' })];
    setBuyerSegs(next);
  };
  const removeBuyerSegment = (index: number) => {
    if (buyerSegs.length <= 1) return;
    const next = buyerSegs.filter((_, i) => i !== index);
    setBuyerSegs(next);
  };
  const addSellerSegment = () => {
    if (sellerSegs.length >= 3) return;
    const next = [...sellerSegs, toFormSegment({ n: 5, p_min: 15, p_max: 25, dist: 'uniform' })];
    setSellerSegs(next);
  };
  const removeSellerSegment = (index: number) => {
    if (sellerSegs.length <= 1) return;
    const next = sellerSegs.filter((_, i) => i !== index);
    setSellerSegs(next);
  };

  // update fields (keep raw strings; do NOT push up here)
  const updateBuyerSegment = (index: number, field: keyof SegmentForm, value: string) => {
    setBuyerSegs(prev => {
      const next = prev.slice();
      next[index] = { ...next[index], [field]: value };
      return next;
    });
  };
  const updateSellerSegment = (index: number, field: keyof SegmentForm, value: string) => {
    setSellerSegs(prev => {
      const next = prev.slice();
      next[index] = { ...next[index], [field]: value };
      return next;
    });
  };
  const handleSeedChange = (value: string) => {
    setSeedStr(value); // don’t push up yet
  };

  // warnings for UI (don’t remove segments—just warn)
  const buyerWarnings = buyerSegs.map(seg =>
    seg.p_min !== '' && seg.p_max !== '' && toInt(seg.p_min) > toInt(seg.p_max)
  );
  const sellerWarnings = sellerSegs.map(seg =>
    seg.p_min !== '' && seg.p_max !== '' && toInt(seg.p_min) > toInt(seg.p_max)
  );
  const hasWarnings = buyerWarnings.some(Boolean) || sellerWarnings.some(Boolean);

  // clamp helper (onBlur)
  const clampInt = (v: string, lo?: number, hi?: number) => {
    if (v === '') return v;
    let x = parseInt(v, 10);
    if (Number.isNaN(x)) return '';
    if (lo != null && x < lo) x = lo;
    if (hi != null && x > hi) x = hi;
    return String(x);
  };

  // Build & send payload ONLY when clicking Generate
  const handleGenerateClick = () => {
    const payload: MarketParams = {
      buyer_segments: buyerSegs.map(toPayloadSegment),
      seller_segments: sellerSegs.map(toPayloadSegment),
      seed: seedStr === '' ? null : Number(seedStr),
    };
    // filter invalid segments NOW (not during typing)
    payload.buyer_segments = payload.buyer_segments.filter(s => s.p_min <= s.p_max);
    payload.seller_segments = payload.seller_segments.filter(s => s.p_min <= s.p_max);

    onParamsChange(payload);
    onGenerate();
  };

  const renderSegment = (
    segment: SegmentForm,
    index: number,
    isBuyer: boolean,
    updateFn: (index: number, field: keyof SegmentForm, value: string) => void,
    removeFn: (index: number) => void,
    warnings: boolean[]
  ) => (
    <div
      key={index}
      className="segment"
      style={{
        border: '1px solid #ccc',
        padding: '1rem',
        margin: '0.5rem 0',
        borderRadius: '8px',
        backgroundColor: warnings[index] ? '#fff3cd' : '#f8f9fa',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <h4 style={{ margin: 0 }}>Segment {index + 1}</h4>
        {((isBuyer && buyerSegs.length > 1) || (!isBuyer && sellerSegs.length > 1)) && (
          <button
            onClick={() => removeFn(index)}
            style={{
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '0.25rem 0.5rem',
              cursor: 'pointer',
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
          step={1}
          min={0}
          value={segment.n}
          onChange={(e) => updateFn(index, 'n', e.target.value)}
          onBlur={() => updateFn(index, 'n', clampInt(segment.n, 0))}
        />
      </div>

      <div className="form-group">
        <label>Min price:</label>
        <input
          type="number"
          step={1}
          min={0}
          value={segment.p_min}
          onChange={(e) => updateFn(index, 'p_min', e.target.value)}
          onBlur={() => updateFn(index, 'p_min', clampInt(segment.p_min, 0))}
        />
      </div>

      <div className="form-group">
        <label>Max price:</label>
        <input
          type="number"
          step={1}
          min={0}
          value={segment.p_max}
          onChange={(e) => updateFn(index, 'p_max', e.target.value)}
          onBlur={() => updateFn(index, 'p_max', clampInt(segment.p_max, 0))}
        />
      </div>

      <div className="form-group">
        <label>Distribution:</label>
        <select
          value={segment.dist}
          onChange={(e) => updateFn(index, 'dist', e.target.value as 'uniform' | 'normal')}
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
              step="any"
              placeholder="Auto-calculated if empty"
              value={segment.mean}
              onChange={(e) => updateFn(index, 'mean', e.target.value)}
              onBlur={() => updateFn(index, 'mean', segment.mean === '' ? '' : String(Number(segment.mean)))}
            />
          </div>
          <div className="form-group">
            <label>Standard Deviation (optional):</label>
            <input
              type="number"
              step="any"
              placeholder="Auto-calculated if empty"
              value={segment.sd}
              onChange={(e) => updateFn(index, 'sd', e.target.value)}
              onBlur={() => updateFn(index, 'sd', segment.sd === '' ? '' : String(Number(segment.sd)))}
            />
          </div>
        </>
      )}

      {warnings[index] && (
        <div
          className="warning"
          style={{
            color: '#d63384',
            fontWeight: 'bold',
            marginTop: '0.5rem',
            padding: '0.5rem',
            backgroundColor: '#f8d7da',
            borderRadius: '4px',
            border: '1px solid #f5c6cb',
          }}
        >
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
            disabled={buyerSegs.length >= 3}
            style={{
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '0.5rem 1rem',
              cursor: buyerSegs.length >= 3 ? 'not-allowed' : 'pointer',
            }}
          >
            Add Segment
          </button>
        </div>
        {buyerSegs.map((segment, index) =>
          renderSegment(segment, index, true, updateBuyerSegment, removeBuyerSegment, buyerWarnings)
        )}
      </div>

      {/* Seller Segments */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3>Seller Segments</h3>
          <button
            onClick={addSellerSegment}
            disabled={sellerSegs.length >= 3}
            style={{
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '0.5rem 1rem',
              cursor: sellerSegs.length >= 3 ? 'not-allowed' : 'pointer',
            }}
          >
            Add Segment
          </button>
        </div>
        {sellerSegs.map((segment, index) =>
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
          value={seedStr}
          onChange={(e) => handleSeedChange(e.target.value)}
          onBlur={() => handleSeedChange(seedStr === '' ? '' : String(parseInt(seedStr, 10)))}
        />
      </div>

      <button
        onClick={handleGenerateClick}
        disabled={loading || hasWarnings}
        style={{ width: '100%', marginTop: '1rem' }}
      >
        {loading ? 'Generating...' : 'Generate Market'}
      </button>
    </div>
  );
}
