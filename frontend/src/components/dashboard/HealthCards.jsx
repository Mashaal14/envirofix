import React from 'react';
import { Activity, AlertTriangle, Info, CheckCircle } from 'lucide-react';
import { useScan } from '../../context/ScanContext';

const HealthCards = () => {
  const { alerts, loading } = useScan();
  
  const criticalCount = alerts?.filter(a => a.severity === 'critical').length || 0;
  const warningCount = alerts?.filter(a => a.severity === 'warning').length || 0;
  const infoCount = alerts?.filter(a => a.severity === 'info').length || 0;
  
  // Calculate health score
  const totalIssues = criticalCount + warningCount + infoCount;
  const healthScore = totalIssues === 0 ? 100 : Math.max(0, 100 - (criticalCount * 15 + warningCount * 5 + infoCount));
  
  const cards = [
    {
      title: 'Health Score',
      value: loading ? '...' : `${healthScore}%`,
      icon: Activity,
      color: healthScore >= 80 ? '#3FB950' : healthScore >= 50 ? '#D29922' : '#F85149',
      bgColor: healthScore >= 80 ? 'rgba(63, 185, 80, 0.1)' : healthScore >= 50 ? 'rgba(210, 153, 34, 0.1)' : 'rgba(248, 81, 73, 0.1)',
      subtitle: healthScore >= 80 ? 'Good' : healthScore >= 50 ? 'Fair' : 'Poor',
    },
    {
      title: 'Critical',
      value: loading ? '...' : criticalCount,
      icon: AlertTriangle,
      color: '#F85149',
      bgColor: 'rgba(248, 81, 73, 0.1)',
      subtitle: 'Need immediate attention',
    },
    {
      title: 'Warnings',
      value: loading ? '...' : warningCount,
      icon: Info,
      color: '#D29922',
      bgColor: 'rgba(210, 153, 34, 0.1)',
      subtitle: 'Should be reviewed',
    },
    {
      title: 'Info',
      value: loading ? '...' : infoCount,
      icon: CheckCircle,
      color: '#58A6FF',
      bgColor: 'rgba(88, 166, 255, 0.1)',
      subtitle: 'Informational only',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => (
        <div key={idx} className="bg-card-bg border border-border rounded-lg p-5 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-text-secondary text-sm">{card.title}</p>
              <p className="text-3xl font-bold mt-1" style={{ color: card.color }}>{card.value}</p>
              <p className="text-xs text-text-secondary mt-1">{card.subtitle}</p>
            </div>
            <div className="p-3 rounded-full" style={{ backgroundColor: card.bgColor }}>
              <card.icon size={28} style={{ color: card.color }} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default HealthCards;
