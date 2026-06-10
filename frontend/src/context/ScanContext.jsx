import React, { createContext, useContext, useState, useCallback } from 'react';
import api from '../services/api';

const ScanContext = createContext();

export const useScan = () => {
  const context = useContext(ScanContext);
  if (!context) {
    throw new Error('useScan must be used within ScanProvider');
  }
  return context;
};

export const ScanProvider = ({ children }) => {
  const [scanData, setScanData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [history, setHistory] = useState([]);
  const [systemInfo, setSystemInfo] = useState(null);
  const [ragStatus, setRagStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastScanTime, setLastScanTime] = useState(null);

  const fetchAlerts = useCallback(async () => {
    try {
      const data = await api.getAlerts();
      setAlerts(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
      setError('Failed to load alerts');
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    try {
      const data = await api.getHistory();
      setHistory(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  }, []);

  const fetchSystemInfo = useCallback(async () => {
    try {
      const data = await api.getSystemInfo();
      setSystemInfo(data || {});
    } catch (error) {
      console.error('Failed to fetch system info:', error);
    }
  }, []);

  const fetchRagStatus = useCallback(async () => {
    try {
      const data = await api.getRAGStatus();
      setRagStatus(data || {});
    } catch (error) {
      console.error('Failed to fetch RAG status:', error);
    }
  }, []);

  const runScan = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Running scan...');
      const result = await api.triggerScanAndAlert();
      console.log('Scan result:', result);
      setScanData(result);
      setLastScanTime(new Date().toISOString());
      await Promise.all([fetchAlerts(), fetchHistory(), fetchSystemInfo()]);
      return result;
    } catch (error) {
      console.error('Scan failed:', error);
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [fetchAlerts, fetchHistory, fetchSystemInfo]);

  const resolveAlert = useCallback(async (alertId) => {
    try {
      await api.resolveAlert(alertId);
      await fetchAlerts();
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    }
  }, [fetchAlerts]);

  const refreshAll = useCallback(async () => {
    console.log('Refreshing all data...');
    await Promise.all([
      fetchAlerts(),
      fetchHistory(),
      fetchSystemInfo(),
      fetchRagStatus(),
    ]);
  }, [fetchAlerts, fetchHistory, fetchSystemInfo, fetchRagStatus]);

  // Initial load
  React.useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  return (
    <ScanContext.Provider value={{
      scanData,
      alerts,
      history,
      systemInfo,
      ragStatus,
      loading,
      error,
      lastScanTime,
      runScan,
      resolveAlert,
      refreshAll,
      fetchAlerts,
      fetchHistory,
      fetchSystemInfo,
      fetchRagStatus,
    }}>
      {children}
    </ScanContext.Provider>
  );
};
