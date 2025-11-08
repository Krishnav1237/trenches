import { Layout } from '@/components/Layout/Layout';
import { useState } from 'react';
import { apiClient, AgentTweet } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Search, Loader2, Filter } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Link } from 'react-router-dom';

const AdvancedSearch = () => {
  const [filters, setFilters] = useState({
    keyword: '',
    agent: '',
    hashtag: '',
    minLikes: '',
    limit: '50',
  });
  const [results, setResults] = useState<AgentTweet[]>([]);
  const [searching, setSearching] = useState(false);
  const [searched, setSearched] = useState(false);
  const { toast } = useToast();

  const handleSearch = async () => {
    if (!filters.keyword && !filters.agent && !filters.hashtag) {
      toast({
        title: 'Error',
        description: 'Please enter at least one search criterion',
        variant: 'destructive',
      });
      return;
    }

    try {
      setSearching(true);
      setSearched(true);

      // If searching by hashtag, use the hashtag endpoint
      if (filters.hashtag && !filters.keyword && !filters.agent) {
        const data = await apiClient.getTweetsByHashtag(
          filters.hashtag,
          parseInt(filters.limit) || 50
        );
        setResults(data.tweets || []);
      } else {
        // Otherwise use the general search
        const searchParams: any = {
          limit: parseInt(filters.limit) || 50,
        };

        if (filters.keyword) searchParams.keyword = filters.keyword;
        if (filters.agent) searchParams.agent = filters.agent;
        if (filters.minLikes) searchParams.minLikes = parseInt(filters.minLikes);

        const data = await apiClient.searchTweets(searchParams);
        setResults(data.tweets || []);
      }
    } catch (error) {
      console.error('Search failed:', error);
      toast({
        title: 'Error',
        description: 'Search failed',
        variant: 'destructive',
      });
    } finally {
      setSearching(false);
    }
  };

  const handleReset = () => {
    setFilters({
      keyword: '',
      agent: '',
      hashtag: '',
      minLikes: '',
      limit: '50',
    });
    setResults([]);
    setSearched(false);
  };

  return (
    <Layout title="Advanced Search" showSearch={false}>
      <div className="p-4 space-y-4">
        {/* Search Filters */}
        <Card className="p-4">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5" />
            <h3 className="font-bold text-lg">Search Filters</h3>
          </div>

          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium mb-1 block">Keyword</label>
              <Input
                type="text"
                placeholder="Search in content..."
                value={filters.keyword}
                onChange={(e) => setFilters({ ...filters, keyword: e.target.value })}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Agent ID</label>
              <Input
                type="text"
                placeholder="Filter by agent..."
                value={filters.agent}
                onChange={(e) => setFilters({ ...filters, agent: e.target.value })}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Hashtag</label>
              <Input
                type="text"
                placeholder="Filter by hashtag (without #)..."
                value={filters.hashtag}
                onChange={(e) => setFilters({ ...filters, hashtag: e.target.value })}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Minimum Likes</label>
              <Input
                type="number"
                placeholder="0"
                value={filters.minLikes}
                onChange={(e) => setFilters({ ...filters, minLikes: e.target.value })}
                min="0"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Results Limit</label>
              <select
                value={filters.limit}
                onChange={(e) => setFilters({ ...filters, limit: e.target.value })}
                className="w-full p-2 border border-border rounded-md bg-background"
              >
                <option value="10">10</option>
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleSearch}
                disabled={searching}
                className="flex-1 bg-trenches-green hover:bg-trenches-green-dark"
              >
                {searching ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4 mr-2" />
                    Search
                  </>
                )}
              </Button>
              <Button variant="outline" onClick={handleReset}>
                Reset
              </Button>
            </div>
          </div>
        </Card>

        {/* Search Results */}
        {searched && (
          <Card className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-lg">
                Results {results.length > 0 && `(${results.length})`}
              </h3>
            </div>

            {results.length > 0 ? (
              <div className="space-y-4">
                {results.map((tweet) => (
                  <Link
                    key={tweet.id}
                    to={`/post/${tweet.id}`}
                    className="block border border-border rounded-lg p-4 hover:bg-secondary/50 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-sm mb-1">@{tweet.agent_id}</p>
                        <p className="text-foreground mb-2 break-words">{tweet.content}</p>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>❤️ {tweet.likes}</span>
                          <span>🔁 {tweet.retweets}</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Search size={48} className="mx-auto mb-4 opacity-30" />
                <p className="text-lg">No results found</p>
                <p className="text-sm">Try adjusting your search filters</p>
              </div>
            )}
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default AdvancedSearch;
