import React, { useState } from 'react';
import api from '../services/api';

const TestAPI = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const testHealth = async () => {
    setLoading(true);
    try {
      const data = await api.getHealth();
      setResult(data);
    } catch (error) {
      setResult({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const testScan = async () => {
    setLoading(true);
    try {
      const data = await api.triggerScanAndAlert();
      setResult(data);
    } catch (error) {
      setResult({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card p-6">
      <h2 className="text-xl font-semibold mb-4">API Test</h2>
      <div className="space-x-4 mb-4">
        <button onClick={testHealth} className="btn-primary">Test Health</button>
        <button onClick={testScan} className="btn-primary">Test Scan</button>
      </div>
      {loading && <p>Loading...</p>}
      {result && (
        <pre className="bg-black bg-opacity-50 p-4 rounded-lg overflow-auto max-h-96 text-xs">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
};

export default TestAPI;
