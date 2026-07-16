import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, AlertTriangle, Info, CheckCircle, Activity, 
  Menu, Bell, Loader2, Copy, X, ChevronRight, ChevronLeft
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

const App = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activePage, setActivePage] = useState('dashboard');
  const [alerts, setAlerts] = useState([]);
  const [systemInfo, setSystemInfo] = useState({});
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [lastScan, setLastScan] = useState(null);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);

  // API Functions
  const apiRequest = async (endpoint, options = {}) => {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [alertsData, sysData] = await Promise.all([
        apiRequest('/alerts').catch(() => []),
        apiRequest('/system').catch(() => ({ kernel: {}, network: {} })),
      ]);
      setAlerts(alertsData);
      setSystemInfo(sysData);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
    setLoading(false);
  };

  const runScan = async () => {
    setScanning(true);
    try {
      await apiRequest('/scan-and-alert', { method: 'POST' });
      setLastScan(new Date().toISOString());
      await loadData();
      setNotifications(prev => [{
        id: Date.now(),
        title: '✅ Scan Complete',
        message: 'System scan finished successfully',
        time: new Date().toISOString(),
        read: false
      }, ...prev]);
    } catch (error) {
      setNotifications(prev => [{
        id: Date.now(),
        title: '❌ Scan Failed',
        message: error.message,
        time: new Date().toISOString(),
        read: false
      }, ...prev]);
    }
    setScanning(false);
  };

  const analyzeIssue = async (alert) => {
    setSelectedAlert(alert);
    setAiAnalysis(null);
    try {
      const analysis = await apiRequest('/analyse', {
        method: 'POST',
        body: JSON.stringify({ issue: alert.title, tool: alert.tool }),
      });
      setAiAnalysis(analysis);
    } catch (error) {
      setAiAnalysis({ error: error.message });
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setNotifications(prev => [{
      id: Date.now(),
      title: '📋 Copied!',
      message: 'Commands copied to clipboard',
      time: new Date().toISOString(),
      read: false
    }, ...prev]);
  };

  const criticalCount = alerts.filter(a => a.severity === 'critical').length;
  const warningCount = alerts.filter(a => a.severity === 'warning').length;
  const infoCount = alerts.filter(a => a.severity === 'info').length;
  const healthScore = alerts.length === 0 ? 100 : Math.max(0, 100 - (criticalCount * 15 + warningCount * 5));
  const unreadCount = notifications.filter(n => !n.read).length;

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Never';
    const diff = Math.floor((new Date() - new Date(timestamp)) / 1000 / 60);
    if (diff < 1) return 'Just now';
    if (diff < 60) return `${diff} min ago`;
    if (diff < 1440) return `${Math.floor(diff / 60)} hours ago`;
    return `${Math.floor(diff / 1440)} days ago`;
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
    { id: 'history', label: 'History', icon: RefreshCw },
  ];

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0D1117' }}>
      {/* Sidebar */}
      <div style={{
        position: 'fixed',
        left: 0,
        top: 0,
        height: '100%',
        width: sidebarOpen ? '260px' : '70px',
        backgroundColor: '#161B22',
        borderRight: '1px solid #30363D',
        transition: 'width 0.3s',
        zIndex: 20
      }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #30363D', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {sidebarOpen ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '24px' }}>🔧</span>
              <span style={{ fontWeight: 'bold', fontSize: '18px', color: '#E6EDF3' }}>EnviroFix</span>
            </div>
          ) : (
            <span style={{ fontSize: '24px', margin: '0 auto' }}>🔧</span>
          )}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} style={{ background: 'none', border: 'none', color: '#8B949E', cursor: 'pointer' }}>
            {sidebarOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
          </button>
        </div>
        <nav style={{ marginTop: '24px' }}>
          {menuItems.map((item) => (
            <div
              key={item.id}
              onClick={() => setActivePage(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '12px 16px',
                cursor: 'pointer',
                backgroundColor: activePage === item.id ? 'rgba(47, 129, 247, 0.1)' : 'transparent',
                borderRight: activePage === item.id ? '2px solid #2F81F7' : 'none',
              }}
            >
              <item.icon size={20} style={{ color: activePage === item.id ? '#2F81F7' : '#8B949E' }} />
              {sidebarOpen && <span style={{ marginLeft: '12px', color: activePage === item.id ? '#2F81F7' : '#8B949E' }}>{item.label}</span>}
            </div>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div style={{ marginLeft: sidebarOpen ? '260px' : '70px', transition: 'margin-left 0.3s' }}>
        {/* Header */}
        <header style={{ backgroundColor: '#161B22', borderBottom: '1px solid #30363D', padding: '12px 24px', position: 'sticky', top: 0, zIndex: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ fontSize: '20px', fontWeight: '600', color: '#E6EDF3', margin: 0, textTransform: 'capitalize' }}>{activePage}</h1>
              <p style={{ fontSize: '12px', color: '#8B949E', margin: '4px 0 0 0' }}>
                {loading ? 'Loading...' : `${alerts.length} alerts | Last scan: ${formatTime(lastScan)}`}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              {/* Notification Bell */}
              <div style={{ position: 'relative' }}>
                <button onClick={() => setShowNotifications(!showNotifications)} style={{ background: 'none', border: 'none', padding: '8px', borderRadius: '8px', cursor: 'pointer', position: 'relative' }}>
                  <Bell size={20} style={{ color: '#8B949E' }} />
                  {unreadCount > 0 && (
                    <span style={{ position: 'absolute', top: 0, right: 0, width: '16px', height: '16px', backgroundColor: '#F85149', borderRadius: '50%', fontSize: '10px', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      {unreadCount}
                    </span>
                  )}
                </button>
                {showNotifications && (
                  <div style={{ position: 'absolute', right: 0, top: '40px', width: '280px', backgroundColor: '#161B22', border: '1px solid #30363D', borderRadius: '8px', zIndex: 30 }}>
                    <div style={{ padding: '12px', borderBottom: '1px solid #30363D' }}>
                      <h3 style={{ margin: 0, color: '#E6EDF3' }}>Notifications</h3>
                    </div>
                    <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                      {notifications.length === 0 ? (
                        <div style={{ padding: '16px', textAlign: 'center', color: '#8B949E' }}>No notifications</div>
                      ) : (
                        notifications.map(n => (
                          <div key={n.id} style={{ padding: '12px', borderBottom: '1px solid #30363D', cursor: 'pointer', backgroundColor: !n.read ? 'rgba(47, 129, 247, 0.1)' : 'transparent' }}>
                            <p style={{ margin: 0, fontSize: '14px', fontWeight: '500', color: '#E6EDF3' }}>{n.title}</p>
                            <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#8B949E' }}>{n.message}</p>
                            <p style={{ margin: '4px 0 0 0', fontSize: '10px', color: '#8B949E' }}>{formatTime(n.time)}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Scan Button */}
              <button
                onClick={runScan}
                disabled={scanning}
                style={{
                  backgroundColor: '#2F81F7',
                  color: 'white',
                  border: 'none',
                  padding: '8px 16px',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  cursor: scanning ? 'not-allowed' : 'pointer',
                  opacity: scanning ? 0.6 : 1
                }}
              >
                {scanning ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <RefreshCw size={16} />}
                <span>{scanning ? 'Scanning...' : 'Scan System'}</span>
              </button>

              {/* Refresh Button */}
              <button onClick={loadData} style={{ background: 'none', border: 'none', padding: '8px', borderRadius: '8px', cursor: 'pointer' }}>
                <RefreshCw size={18} style={{ color: '#8B949E' }} />
              </button>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main style={{ padding: '24px' }}>
          {activePage === 'dashboard' && (
            <div>
              {/* Stats Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                <div style={{ backgroundColor: '#161B22', border: '1px solid #30363D', borderRadius: '8px', padding: '20px' }}>
                  <p style={{ color: '#8B949E', fontSize: '14px', margin: 0 }}>Health Score</p>
                  <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#3FB950', margin: '8px 0 0 0' }}>{healthScore}%</p>
                  <p style={{ fontSize: '12px', color: '#8B949E', margin: '4px 0 0 0' }}>{healthScore >= 80 ? 'System Healthy' : 'Needs Attention'}</p>
                </div>
                <div style={{ backgroundColor: '#161B22', border: '1px solid #30363D', borderRadius: '8px', padding: '20px' }}>
                  <p style={{ color: '#8B949E', fontSize: '14px', margin: 0 }}>Critical</p>
                  <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#F85149', margin: '8px 0 0 0' }}>{criticalCount}</p>
                </div>
                <div style={{ backgroundColor: '#161B22', border: '1px solid #30363D', borderRadius: '8px', padding: '20px' }}>
                  <p style={{ color: '#8B949E', fontSize: '14px', margin: 0 }}>Warnings</p>
                  <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#D29922', margin: '8px 0 0 0' }}>{warningCount}</p>
                </div>
                <div style={{ backgroundColor: '#161B22', border: '1px solid #30363D', borderRadius: '8px', padding: '20px' }}>
                  <p style={{ color: '#8B949E', fontSize: '14px', margin: 0 }}>Info</p>
                  <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#58A6FF', margin: '8px 0 0 0' }}>{infoCount}</p>
                </div>
              </div>

              {/* Alerts Section */}
              <div style={{ backgroundColor: '#161B22', border: '1px solid #30363D', borderRadius: '8px', padding: '20px', marginBottom: '24px' }}>
                <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#E6EDF3', margin: '0 0 16px 0' }}>⚠️ Active Alerts</h2>
                {loading ? (
                  <div style={{ textAlign: 'center', padding: '32px', color: '#8B949E' }}>Loading...</div>
                ) : alerts.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '32px' }}>
                    <CheckCircle size={48} style={{ color: '#3FB950', margin: '0 auto 8px' }} />
                    <p style={{ color: '#8B949E' }}>No alerts! System is healthy.</p>
                  </div>
                ) : (
                  alerts.map(alert => (
                    <div key={alert.id} style={{ border: '1px solid #D29922', borderRadius: '8px', padding: '16px', marginBottom: '12px', cursor: 'pointer' }} onClick={() => analyzeIssue(alert)}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: '600', color: '#E6EDF3', marginBottom: '8px' }}>{alert.title}</div>
                          <div style={{ fontSize: '14px', color: '#8B949E', marginBottom: '8px' }}>{alert.detail}</div>
                          {alert.fix && (
                            <div style={{ fontSize: '12px', color: '#2F81F7', fontFamily: 'monospace' }}>💡 {alert.fix}</div>
                          )}
                        </div>
                        <button style={{ background: 'none', border: 'none', color: '#2F81F7', cursor: 'pointer', padding: '4px 8px' }}>Learn</button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* System Info */}
              <div style={{ backgroundColor: '#161B22', border: '1px solid #30363D', borderRadius: '8px', padding: '20px' }}>
                <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#E6EDF3', margin: '0 0 16px 0' }}>💻 System Snapshot</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                  <div><span style={{ color: '#8B949E' }}>Kernel:</span> <span style={{ fontFamily: 'monospace' }}>{systemInfo.kernel?.kernel_version || 'Unknown'}</span></div>
                  <div><span style={{ color: '#8B949E' }}>Headers:</span> <span style={{ color: systemInfo.kernel?.kernel_headers_installed ? '#3FB950' : '#F85149' }}>{systemInfo.kernel?.kernel_headers_installed ? '✅ Installed' : '❌ Missing'}</span></div>
                  <div><span style={{ color: '#8B949E' }}>DKMS:</span> <span style={{ color: systemInfo.kernel?.dkms_installed ? '#3FB950' : '#D29922' }}>{systemInfo.kernel?.dkms_installed ? '✅ Installed' : '⚠️ Not installed'}</span></div>
                  <div><span style={{ color: '#8B949E' }}>VPN:</span> <span style={{ color: systemInfo.network?.vpn_active ? '#3FB950' : '#D29922' }}>{systemInfo.network?.vpn_active ? 'Active' : 'Inactive'}</span></div>
                </div>
              </div>
            </div>
          )}

          {activePage === 'alerts' && (
            <div style={{ backgroundColor: '#161B22', border: '1px solid #30363D', borderRadius: '8px', padding: '20px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#E6EDF3', margin: '0 0 16px 0' }}>📋 All Alerts</h2>
              {alerts.map(alert => (
                <div key={alert.id} style={{ borderBottom: '1px solid #30363D', padding: '12px', cursor: 'pointer' }} onClick={() => analyzeIssue(alert)}>
                  <div style={{ fontWeight: '600', color: '#E6EDF3' }}>{alert.title}</div>
                  <div style={{ fontSize: '14px', color: '#8B949E' }}>{alert.detail}</div>
                </div>
              ))}
            </div>
          )}

          {activePage === 'history' && (
            <div style={{ backgroundColor: '#161B22', border: '1px solid #30363D', borderRadius: '8px', padding: '20px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#E6EDF3', margin: '0 0 16px 0' }}>📜 Scan History</h2>
              <p style={{ color: '#8B949E' }}>Coming soon</p>
            </div>
          )}
        </main>
      </div>

      {/* AI Analysis Modal */}
      {selectedAlert && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50, padding: '16px' }} onClick={() => setSelectedAlert(null)}>
          <div style={{ backgroundColor: '#161B22', border: '1px solid #2F81F7', borderRadius: '8px', maxWidth: '600px', width: '100%', maxHeight: '80vh', overflow: 'auto' }} onClick={e => e.stopPropagation()}>
            <div style={{ padding: '16px', borderBottom: '1px solid #30363D', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ margin: 0, color: '#2F81F7' }}>🤖 AI Analysis</h2>
              <button onClick={() => setSelectedAlert(null)} style={{ background: 'none', border: 'none', color: '#8B949E', cursor: 'pointer', fontSize: '24px' }}>✕</button>
            </div>
            <div style={{ padding: '20px' }}>
              {!aiAnalysis ? (
                <div style={{ textAlign: 'center', padding: '32px' }}>
                  <Loader2 size={48} style={{ animation: 'spin 1s linear infinite', margin: '0 auto 16px', color: '#2F81F7' }} />
                  <p style={{ color: '#8B949E' }}>AI is analyzing the issue...</p>
                </div>
              ) : aiAnalysis.error ? (
                <div style={{ textAlign: 'center', color: '#F85149' }}>Error: {aiAnalysis.error}</div>
              ) : (
                <div>
                  <div style={{ marginBottom: '16px' }}>
                    <h3 style={{ color: '#2F81F7', marginBottom: '8px' }}>📋 Root Cause</h3>
                    <p style={{ color: '#8B949E' }}>{aiAnalysis.root_cause}</p>
                  </div>
                  <div style={{ marginBottom: '16px' }}>
                    <h3 style={{ color: '#2F81F7', marginBottom: '8px' }}>🔧 Fix Commands</h3>
                    <div style={{ backgroundColor: '#0D1117', borderRadius: '8px', padding: '12px' }}>
                      {aiAnalysis.fix_steps?.map((step, i) => (
                        <code key={i} style={{ display: 'block', color: '#3FB950', fontFamily: 'monospace', fontSize: '12px', marginBottom: '4px' }}>$ {step}</code>
                      ))}
                    </div>
                    <button onClick={() => copyToClipboard(aiAnalysis.fix_steps?.join('\n') || '')} style={{ marginTop: '8px', background: 'none', border: 'none', color: '#2F81F7', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Copy size={14} /> Copy all commands
                    </button>
                  </div>
                  <div>
                    <h3 style={{ color: '#2F81F7', marginBottom: '8px' }}>⚠️ Risk Level</h3>
                    <span style={{ display: 'inline-block', padding: '4px 12px', borderRadius: '16px', fontSize: '12px', backgroundColor: 'rgba(210, 153, 34, 0.2)', color: '#D29922' }}>
                      {aiAnalysis.risk_level || 'Caution'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default App;
