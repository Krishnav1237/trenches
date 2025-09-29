import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useStore } from '@/store/useStore';

interface TopBarProps {
  title?: string;
  showSearch?: boolean;
}

export const TopBar = ({ title = 'Home', showSearch = true }: TopBarProps) => {
  const { searchQuery, setSearchQuery } = useStore();

  return (
    <div className="sticky top-0 z-10 bg-background/80 backdrop-blur border-b border-border p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{title}</h1>
        
        {showSearch && (
          <div className="relative w-80">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" size={20} />
            <Input
              placeholder="Search Trenches"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12 bg-secondary border-none rounded-full"
            />
          </div>
        )}
      </div>
    </div>
  );
};