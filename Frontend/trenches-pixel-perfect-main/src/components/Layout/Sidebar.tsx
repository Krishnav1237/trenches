import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Search,
  Bell,
  Mail,
  User,
  Hash,
  Newspaper,
  Bookmark,
  Settings,
  Moon,
  Sun
} from 'lucide-react';
import { useStore } from '@/store/useStore';
import { Button } from '@/components/ui/button';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<any>;
}

const navItems: NavItem[] = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Search', href: '/search', icon: Search },
  { name: 'Notifications', href: '/notifications', icon: Bell },
  { name: 'Messages', href: '/messages', icon: Mail },
  { name: 'Profile', href: '/profile', icon: User },
  { name: 'Trending', href: '/trending', icon: Hash },
  { name: 'News', href: '/news', icon: Newspaper },
  { name: 'Bookmarks', href: '/bookmarks', icon: Bookmark },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export const Sidebar = () => {
  const location = useLocation();
  const { darkMode, toggleDarkMode, currentUser } = useStore();

  return (
    <div className="h-screen w-64 fixed left-0 top-0 bg-background border-r border-border p-4 flex flex-col">
      {/* Logo */}
      <div className="mb-8">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-trenches-green rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">T</span>
          </div>
          <span className="text-2xl font-bold text-trenches-green">Trenches</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.href;
          
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`trenches-sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Icon size={24} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Theme Toggle */}
      <div className="mb-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleDarkMode}
          className="trenches-button-ghost w-full justify-start"
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          <span className="ml-3">{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
        </Button>
      </div>

      {/* User Profile */}
      {currentUser && (
        <div className="p-3 rounded-xl hover:bg-secondary transition-colors cursor-pointer">
          <div className="flex items-center gap-3">
            <img
              src={currentUser.avatar}
              alt={currentUser.displayName}
              className="trenches-avatar w-10 h-10"
            />
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm truncate">{currentUser.displayName}</p>
              <p className="text-muted-foreground text-xs truncate">@{currentUser.username}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};