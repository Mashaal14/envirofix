import React, { useState } from 'react';
import { Lightbulb, Copy, ChevronDown, ChevronUp } from 'lucide-react';
import { useScan } from '../../context/ScanContext';
import api from '../../services/api';

const AIInsights = () => {
  const { alerts } = useScan();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const getTopIssue = () => {
    const critical = alerts.find(a => a.severity === 'critical');
    if (critical) return critical;
    const warning = alerts.find(a => a.severity === 'warning');
    if (warning) return warning;
    return alerts[0];
  };

  const analyzeTopIssue = async () => {
    const issue = getTopIssue();
    if (!issue) return;
    
    setLoading(true);
    try {
      const result = await api.analyseIssue(issue.title, issue.tool);
      setAnalysis(result);
    } catch (error) {
      console.error('AI analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const topIssue = getTopIssue();

  return (
    <div className="bg-card-bg border border-border rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-text-primary">🤖 AI Insights</h2>
        {topIssue && (
          <button
            onClick={analyzeTopIssue}
            disabled={loading}
            className="text-accent hover:text-opacity-80 text-sm disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Analyze Top Issue'}
          </button>
        )}
      </div>
      
      {!topIssue ? (
        <div className="text-center py-8 text-text-secondary">
          <Lightbulb size={48} className="mx-auto mb-2 opacity-50" />
          <p>No issues detected. System is healthy!</p>
        </div>
      ) : analysis ? (
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-accent">Root Cause</h3>
            <p className="text-text-secondary mt-1">{analysis.root_cause}</p>
          </div>
          
          <div>
            <h3 className="font-semibold text-accent">Fix Command</h3>
            <div className="bg-black bg-opacity-50 rounded-lg p-3 mt-1 relative group">
              <code className="text-sm text-success block font-mono">
                {analysis.fix_steps?.join(' && ') || 'No fix steps available'}
              </code>
              <button
                onClick={() => navigator.clipboard.writeText(analysis.fix_steps?.join(' && ') || '')}
                className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition"
              >
                <Copy size={16} className="text-text-secondary" />
              </button>
            </div>
          </div>
          
          <div>
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center space-x-1 text-accent hover:text-opacity-80"
            >
              {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              <span className="text-sm">What you'll learn</span>
            </button>
            {expanded && (
              <p className="text-text-secondary mt-2 text-sm">{analysis.teaches}</p>
            )}
          </div>
          
          <div className="flex items-center justify-between pt-2 border-t border-border">
            <span className="text-xs text-text-secondary">
              Confidence: {analysis.confidence || 'high'}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded ${
              analysis.risk_level === 'Safe' ? 'bg-success bg-opacity-20 text-success' :
              analysis.risk_level === 'Caution' ? 'bg-warning bg-opacity-20 text-warning' :
              'bg-critical bg-opacity-20 text-critical'
            }`}>
              Risk: {analysis.risk_level || 'Caution'}
            </span>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-text-secondary">
          <Lightbulb size={48} className="mx-auto mb-2 opacity-50" />
          <p>Click "Analyze Top Issue" for AI-powered insights</p>
        </div>
      )}
    </div>
  );
};

export default AIInsights;
