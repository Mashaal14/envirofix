import React, { useState } from 'react';
import { Menu, RefreshCw, Bell, User, Loader2 } from 'lucide-react';
import { useScan } from '../../context/ScanContext';

const Header = ({ toggleSidebar }) => {
  const { lastScanTime, loading, runScan, refreshAll } = useScan();
  const [scanning, setScanning] = useState(false);

  const formatLastScan = () => {
    if (!lastScanTime) return 'No scan yet';
    const date = new Date(lastScanTime);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000 / 60);
    if (diff < 1) return 'Just now';
    if (diff < 60) return `${diff} min ago`;
    if (diff < 1440) return `${Math.floor(diff / 60)} hours ago`;
    return `${Math.floor(diff / 1440)} days ago`;
  };

  const handleScan = async () => {
    setScanning(true);
    try {
      await runScan();
    } catch (error) {
      console.error('Scan failed:', error);
    } finally {
      setScanning(false);
    }
  };

  const handleRefresh = async () => {
    await refreshAll();
  };

  return (
    <header className="bg-card-bg border-b border-border px-6 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button 
            onClick={toggleSidebar} 
            className="text-text-secondary hover:text-text-primary transition-colors"
          >
            <Menu size={24} />
          </button>
          <div>
            <h1 className="text-xl font-semibold text-text-primary">Dashboard</h1>
            <p className="text-sm text-text-secondary">Last scan: {formatLastScan()}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={handleScan}
            disabled={scanning || loading}
            className="bg-accent hover:bg-opacity-80 text-white px-4 py-2 rounded-md transition-all flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {(scanning || loading) ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <RefreshCw size={16} />
            )}
            <span>{scanning || loading ? 'Scanning...' : 'Scan Now'}</span>
          </button>
          
          <button 
            onClick={handleRefresh}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            title="Refresh all data"
          >
            <RefreshCw size={18} className="text-text-secondary" />
          </button>
          
          <button className="p-2 hover:bg-gray-800 rounded-lg relative transition-colors">
            <Bell size={18} className="text-text-secondary" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-critical rounded-full"></span>
          </button>
          
          <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
            <User size={18} className="text-text-secondary" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
