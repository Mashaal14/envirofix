import React, { useState } from 'react';
import { AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react';
import { useScan } from '../../context/ScanContext';
import api from '../../services/api';

const AlertsTable = () => {
  const { alerts, resolveAlert } = useScan();
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <AlertTriangle size={18} className="text-critical" />;
      case 'warning': return <AlertTriangle size={18} className="text-warning" />;
      case 'info': return <Info size={18} className="text-info" />;
      default: return <CheckCircle size={18} className="text-success" />;
    }
  };

  const getSeverityClass = (severity) => {
    switch (severity) {
      case 'critical': return 'border-critical bg-critical bg-opacity-5';
      case 'warning': return 'border-warning bg-warning bg-opacity-5';
      case 'info': return 'border-info bg-info bg-opacity-5';
      default: return 'border-success bg-success bg-opacity-5';
    }
  };

  const handleAnalyze = async (alert) => {
    setSelectedAlert(alert);
    setLoading(true);
    try {
      const analysis = await api.analyseIssue(alert.title, alert.tool);
      setAiAnalysis(analysis);
    } catch (error) {
      console.error('AI analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Unknown';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000 / 60);
    if (diff < 1) return 'Just now';
    if (diff < 60) return `${diff} min ago`;
    if (diff < 1440) return `${Math.floor(diff / 60)} hours ago`;
    return `${Math.floor(diff / 1440)} days ago`;
  };

  return (
    <div className="bg-card-bg border border-border rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-text-primary">⚠️ Active Alerts</h2>
        <span className="text-sm text-text-secondary">{alerts.length} total</span>
      </div>
      
      <div className="space-y-3">
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-text-secondary">
            <CheckCircle size={48} className="mx-auto mb-2 text-success" />
            <p>No active alerts! System is healthy.</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div key={alert.id} className={`border rounded-lg p-4 ${getSeverityClass(alert.severity)}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  {getSeverityIcon(alert.severity)}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-semibold text-text-primary">{alert.title}</h3>
                      <span className="text-xs text-text-secondary">{formatTime(alert.created_at)}</span>
                    </div>
                    <p className="text-sm mt-1 text-text-secondary">{alert.detail}</p>
                    {alert.fix && (
                      <div className="mt-2">
                        <code className="text-xs bg-black bg-opacity-30 px-2 py-1 rounded block text-text-primary">
                          {alert.fix}
                        </code>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleAnalyze(alert)}
                    className="px-3 py-1 text-sm bg-accent bg-opacity-20 text-accent rounded hover:bg-opacity-30 transition"
                  >
                    Learn
                  </button>
                  <button
                    onClick={() => resolveAlert(alert.id)}
                    className="px-3 py-1 text-sm bg-gray-700 text-text-primary rounded hover:bg-gray-600 transition"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* AI Analysis Modal */}
      {selectedAlert && aiAnalysis && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-card-bg border border-border rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-text-primary">🤖 AI Analysis</h2>
                <button
                  onClick={() => {
                    setSelectedAlert(null);
                    setAiAnalysis(null);
                  }}
                  className="text-text-secondary hover:text-text-primary"
                >
                  <XCircle size={24} />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-accent">Root Cause</h3>
                  <p className="text-text-secondary mt-1">{aiAnalysis.root_cause}</p>
                </div>
                
                <div>
                  <h3 className="font-semibold text-accent">Fix Steps</h3>
                  <div className="bg-black bg-opacity-50 rounded-lg p-3 mt-1">
                    {aiAnalysis.fix_steps?.map((step, idx) => (
                      <code key={idx} className="block text-sm text-success font-mono">
                        $ {step}
                      </code>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold text-accent">Risk Level</h3>
                  <span className={`inline-block px-3 py-1 rounded text-sm mt-1 ${getSeverityClass(aiAnalysis.risk_level?.toLowerCase() || 'info')}`}>
                    {aiAnalysis.risk_level || 'Caution'}
                  </span>
                </div>
                
                <div className="pt-4 border-t border-border">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-secondary">
                      Confidence: {aiAnalysis.confidence || 'high'}
                    </span>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(aiAnalysis.fix_steps?.join('\n') || '');
                      }}
                      className="text-accent hover:text-opacity-80 text-sm"
                    >
                      📋 Copy Commands
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertsTable;
