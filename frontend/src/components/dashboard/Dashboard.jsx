import React, { useEffect } from 'react';
import HealthCards from './HealthCards';
import SystemSnapshot from './SystemSnapshot';
import AlertsTable from './AlertsTable';
import AIInsights from './AIInsights';
import { useScan } from '../../context/ScanContext';

const Dashboard = () => {
  const { refreshAll } = useScan();

  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 30000);
    return () => clearInterval(interval);
  }, [refreshAll]);

  return (
    <div className="space-y-6">
      <HealthCards />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <AlertsTable />
        </div>
        <div>
          <SystemSnapshot />
        </div>
      </div>
      
      <AIInsights />
    </div>
  );
};

export default Dashboard;
