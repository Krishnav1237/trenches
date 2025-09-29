import React from 'react';
import { Home, Bell, Search, Users } from 'lucide-react';
import { ActiveScreen } from './MobileLayout';

interface BottomNavProps {
  activeScreen: ActiveScreen;
  onScreenChange: (screen: ActiveScreen) => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({ activeScreen, onScreenChange }) => {
  const navItems = [
    { key: 'home' as ActiveScreen, icon: Home, label: 'Home' },
    { key: 'pfps' as ActiveScreen, icon: Users, label: 'PFPs' },
    { key: 'search' as ActiveScreen, icon: Search, label: 'Search' },
    { key: 'notifications' as ActiveScreen, icon: Bell, label: 'Notifications' },
  ];

  return (
    <div className="flex items-center justify-around py-3 px-4 border-t border-gray-800 bg-black">
      {navItems.map(({ key, icon: Icon, label }) => (
        <button
          key={key}
          onClick={() => onScreenChange(key)}
          className={`flex flex-col items-center space-y-1 transition-colors ${
            activeScreen === key 
              ? 'text-[#00ff88]' 
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Icon className="w-6 h-6" />
          <span className="text-xs">{label}</span>
        </button>
      ))}
    </div>
  );
};