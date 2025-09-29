import React, { useState } from 'react';
import { Wifi, Battery, Signal } from 'lucide-react';
import { BottomNav } from './BottomNav';
import { MobileHome } from './MobileHome';
import { MobilePFPs } from './MobilePFPs';
import { MobileSearch } from './MobileSearch';
import { MobileNotifications } from './MobileNotifications';

interface MobileLayoutProps {
  children?: React.ReactNode;
  className?: string;
}

export type ActiveScreen = 'home' | 'pfps' | 'search' | 'notifications';

export const MobileLayout: React.FC<MobileLayoutProps> = ({ children, className = '' }) => {
  const [activeScreen, setActiveScreen] = useState<ActiveScreen>('home');

  const renderScreen = () => {
    switch (activeScreen) {
      case 'home':
        return <MobileHome className="h-full" />;
      case 'pfps':
        return <MobilePFPs className="h-full" />;
      case 'search':
        return <MobileSearch className="h-full" />;
      case 'notifications':
        return <MobileNotifications className="h-full" />;
      default:
        return <MobileHome className="h-full" />;
    }
  };

  return (
    <div className={`min-h-screen bg-black text-white flex flex-col max-w-sm mx-auto ${className}`}>
      {/* Status Bar */}
      <div className="flex items-center justify-between px-4 py-2 text-sm bg-black">
        <span className="font-medium">9:41</span>
        <div className="flex items-center space-x-1">
          <Signal className="w-4 h-4" />
          <Wifi className="w-4 h-4" />
          <Battery className="w-4 h-4" />
        </div>
      </div>

      {/* Header - Only show for home screen */}
      {activeScreen === 'home' && (
        <div className="px-4 py-4 border-b border-gray-800">
          <h1 className="text-2xl font-bold text-[#00ff88]">TRENCHES</h1>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {children || renderScreen()}
      </div>

      {/* Bottom Navigation */}
      <BottomNav activeScreen={activeScreen} onScreenChange={setActiveScreen} />
    </div>
  );
};