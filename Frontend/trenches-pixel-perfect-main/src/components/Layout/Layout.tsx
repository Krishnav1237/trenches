import { useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { useStore } from '@/store/useStore';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  showSearch?: boolean;
}

export const Layout = ({ children, title, showSearch }: LayoutProps) => {
  const { darkMode } = useStore();

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      
      <div className="ml-64">
        <div className="max-w-2xl mx-auto">
          <TopBar title={title} showSearch={showSearch} />
          <main className="min-h-screen">
            {children}
          </main>
        </div>
        
        {/* Right Sidebar - Trending/Suggestions */}
        <div className="fixed right-4 top-20 w-80 hidden xl:block">
          <div className="trenches-card">
            <h3 className="font-bold text-lg mb-4">Trending</h3>
            <div className="space-y-3">
              <div className="hover:bg-secondary p-2 rounded cursor-pointer transition-colors">
                <p className="text-sm text-muted-foreground">Trending in Technology</p>
                <p className="font-semibold">React 18</p>
                <p className="text-sm text-muted-foreground">12.5K posts</p>
              </div>
              <div className="hover:bg-secondary p-2 rounded cursor-pointer transition-colors">
                <p className="text-sm text-muted-foreground">Trending</p>
                <p className="font-semibold">#WebDev</p>
                <p className="text-sm text-muted-foreground">8.2K posts</p>
              </div>
              <div className="hover:bg-secondary p-2 rounded cursor-pointer transition-colors">
                <p className="text-sm text-muted-foreground">Trending in Design</p>
                <p className="font-semibold">UI/UX</p>
                <p className="text-sm text-muted-foreground">5.7K posts</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};