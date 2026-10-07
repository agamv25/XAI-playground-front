'use client';

import { useState, useRef } from 'react';
import { uploadFiles, computeExplanations, pollResults, type ResultsResponse } from '@/lib/api';

export default function Home() {
  const [analysisId, setAnalysisId] = useState('');
  const [status, setStatus] = useState<'idle' | 'uploading' | 'ready' | 'computing' | 'polling' | 'done' | 'error'>('idle');
  const [results, setResults] = useState<Record<string, ResultsResponse> | null>(null);
  const [error, setError] = useState('');
  const csvFileRef = useRef<HTMLInputElement>(null);
  const modelFileRef = useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    const csvFile = csvFileRef.current?.files?.[0];
    const modelFile = modelFileRef.current?.files?.[0];

    if (!csvFile || !modelFile) {
      setError('Please select both files');
      return;
    }

    try {
      setError('');
      setStatus('uploading');
      console.log('Uploading files...', csvFile.name, modelFile.name);
      const response = await uploadFiles(csvFile, modelFile);
      console.log('Upload response:', response);
      setAnalysisId(response.analysis_id);
      setStatus('ready');
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.message || 'Upload failed');
      setStatus('error');
    }
  };

  const handleAnalyze = async () => {
    if (!analysisId) return;

    try {
      setError('');
      setStatus('computing');
      console.log('Starting computation...');
      await computeExplanations(analysisId, ['shap', 'lime', 'importance'], 0);
      
      setStatus('polling');
      console.log('Polling results...');
      const allResults = await pollResults(analysisId, ['shap', 'lime', 'importance']);
      console.log('Results received:', allResults);
      setResults(allResults);
      setStatus('done');
    } catch (err: any) {
      console.error('Analysis error:', err);
      setError(err.message || 'Analysis failed');
      setStatus('error');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: '#fff' }}>
      {/* Header */}
      <header style={{ borderBottom: '1px solid #e5e5e5', padding: '0 2rem', height: '56px', display: 'flex', alignItems: 'center' }}>
        <div style={{ fontWeight: 700, fontSize: '16px' }}>XAI Playground</div>
      </header>

      {/* Main content */}
      <main style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
        {status === 'idle' && (
          <div style={{ textAlign: 'center', maxWidth: '520px' }}>
            <h1 style={{ fontSize: '32px', fontWeight: 500, margin: '0 0 1rem 0' }}>No analysis yet</h1>
            <p style={{ fontSize: '16px', color: '#666', margin: '0 0 2rem 0' }}>Upload your data and model to explore explainability techniques.</p>
            
            <div style={{ marginBottom: '2rem', textAlign: 'left', border: '1px solid #e5e5e5', borderRadius: '8px', padding: '1.5rem' }}>
              <label style={{ display: 'block', marginBottom: '1rem', fontSize: '13px', color: '#666' }}>
                CSV File
                <input 
                  ref={csvFileRef} 
                  type="file" 
                  accept=".csv"
                  style={{ display: 'block', marginTop: '8px', width: '100%', padding: '8px' }}
                />
              </label>
              <label style={{ display: 'block', fontSize: '13px', color: '#666' }}>
                Model File (.pkl)
                <input 
                  ref={modelFileRef} 
                  type="file" 
                  accept=".pkl"
                  style={{ display: 'block', marginTop: '8px', width: '100%', padding: '8px' }}
                />
              </label>
            </div>

            {error && <p style={{ color: 'red', marginBottom: '1rem' }}>{error}</p>}
            
            <button 
              onClick={handleUpload}
              style={{ padding: '12px 32px', background: '#000', color: 'white', border: 'none', borderRadius: '4px', fontSize: '15px', fontWeight: 500, cursor: 'pointer' }}
            >
              Upload & Analyze
            </button>
          </div>
        )}
        {status === 'uploading' && <p>Uploading files...</p>}
        {status === 'ready' && (
          <div style={{ textAlign: 'center' }}>
            <p>Dataset loaded successfully</p>
            <button 
              onClick={handleAnalyze}
              style={{ padding: '12px 32px', background: '#000', color: 'white', border: 'none', borderRadius: '4px', fontSize: '15px', fontWeight: 500, cursor: 'pointer' }}
            >
              Analyze
            </button>
          </div>
        )}
        {status === 'computing' && <p>Computing explanations...</p>}
        {status === 'polling' && <p>Polling results...</p>}
        {status === 'done' && results && (
          <div style={{ width: '100%', maxWidth: '1000px' }}>
            <h2>Results</h2>
            <pre style={{ background: '#f5f5f5', padding: '1rem', borderRadius: '8px', overflow: 'auto', maxHeight: '600px' }}>
              {JSON.stringify(results, null, 2)}
            </pre>
          </div>
        )}
        {status === 'error' && error && <p style={{ color: 'red' }}>Error: {error}</p>}
      </main>
    </div>
  );
}