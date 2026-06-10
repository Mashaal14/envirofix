import React from 'react';
import { Cpu, Network, Package as PackageIcon, Wifi, WifiOff } from 'lucide-react';
import { useScan } from '../../context/ScanContext';

const SystemSnapshot = () => {
  const { systemInfo } = useScan();

  const InfoRow = ({ label, value, icon: Icon, status }) => (
    <div className="flex items-center justify-between py-2 border-b border-border last:border-0">
      <div className="flex items-center space-x-2">
        <Icon size={16} className="text-text-secondary" />
        <span className="text-sm text-text-secondary">{label}</span>
      </div>
      <div className="flex items-center space-x-2">
        {status && (
          <span className={`text-xs px-2 py-0.5 rounded ${status === 'ok' ? 'bg-success bg-opacity-20 text-success' : 'bg-critical bg-opacity-20 text-critical'}`}>
            {status === 'ok' ? 'OK' : 'Issue'}
          </span>
        )}
        <span className="text-sm font-mono text-text-primary">{value || 'N/A'}</span>
      </div>
    </div>
  );

  const kernel = systemInfo?.kernel || {};
  const network = systemInfo?.network || {};

  return (
    <div className="bg-card-bg border border-border rounded-lg p-5">
      <h2 className="text-lg font-semibold text-text-primary mb-4">🖥️ System Snapshot</h2>
      
      <div className="space-y-2">
        <InfoRow
          label="Kernel Version"
          value={kernel.kernel_version}
          icon={Cpu}
          status={kernel.kernel_version ? 'ok' : 'error'}
        />
        <InfoRow
          label="Kernel Headers"
          value={kernel.kernel_headers_installed ? 'Installed' : 'Missing'}
          icon={PackageIcon}
          status={kernel.kernel_headers_installed ? 'ok' : 'error'}
        />
        <InfoRow
          label="DKMS"
          value={kernel.dkms_installed ? 'Installed' : 'Not installed'}
          icon={PackageIcon}
          status={kernel.dkms_installed ? 'ok' : 'error'}
        />
      </div>
      
      <h3 className="text-sm font-semibold mt-4 mb-2 text-accent">🌐 Network Interfaces</h3>
      <div className="space-y-2">
        {Object.entries(network?.interfaces || {}).map(([name, info]) => (
          <div key={name} className="flex items-center justify-between py-1">
            <span className="text-sm text-text-secondary">{name}</span>
            <div className="flex items-center space-x-2">
              {info.status === 'UP' ? (
                <Wifi size={14} className="text-success" />
              ) : (
                <WifiOff size={14} className="text-text-secondary" />
              )}
              <span className="text-xs font-mono text-text-primary">{info.ip || 'No IP'}</span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-3 pt-2 border-t border-border">
        <div className="flex items-center justify-between">
          <span className="text-sm text-text-secondary">VPN Status</span>
          <span className={`text-xs px-2 py-0.5 rounded ${network.vpn_active ? 'bg-success bg-opacity-20 text-success' : 'bg-warning bg-opacity-20 text-warning'}`}>
            {network.vpn_active ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default SystemSnapshot;
