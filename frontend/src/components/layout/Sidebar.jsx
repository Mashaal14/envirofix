import React from 'react';
import { 
  LayoutDashboard, 
  AlertTriangle, 
  Package, 
  GraduationCap, 
  History,
  Settings,
  Cpu
} from 'lucide-react';

const Sidebar = ({ isOpen, setIsOpen }) => {
  const [activeItem, setActiveItem] = React.useState('Dashboard');
  
  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard' },
    { icon: AlertTriangle, label: 'Alerts' },
    { icon: Package, label: 'Tools' },
    { icon: GraduationCap, label: 'Learning' },
    { icon: History, label: 'History' },
    { icon: Cpu, label: 'System' },
    { icon: Settings, label: 'Settings' },
  ];

  return (
    <div className={`fixed left-0 top-0 h-full bg-card-bg border-r border-border transition-all duration-300 z-20 ${isOpen ? 'w-64' : 'w-20'}`}>
      <div className="p-4 border-b border-border">
        {isOpen ? (
          <div className="flex items-center space-x-2">
            <span className="text-2xl">🔧</span>
            <span className="font-bold text-lg text-text-primary">EnviroFix</span>
          </div>
        ) : (
          <div className="flex justify-center">
            <span className="text-2xl">🔧</span>
          </div>
        )}
      </div>
      
      <nav className="mt-6">
        {menuItems.map((item) => (
          <div
            key={item.label}
            onClick={() => setActiveItem(item.label)}
            className={`flex items-center px-4 py-3 cursor-pointer transition-colors ${
              activeItem === item.label 
                ? 'bg-accent bg-opacity-10 border-r-2 border-accent' 
                : 'hover:bg-gray-800'
            }`}
          >
            <item.icon size={20} className={activeItem === item.label ? 'text-accent' : 'text-text-secondary'} />
            {isOpen && (
              <span className={`ml-3 ${activeItem === item.label ? 'text-accent' : 'text-text-secondary'}`}>
                {item.label}
              </span>
            )}
          </div>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;
