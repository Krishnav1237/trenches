import React, { useState, useEffect, useMemo } from 'react';
import { useStore } from '../../store/useStore';
import { Search, TrendingUp, Users, MessageCircle, Hash, X, Clock } from 'lucide-react';
import { BadgeCheck } from 'lucide-react';

interface MobileSearchProps {
  className?: string;
}

export const MobileSearch: React.FC<MobileSearchProps> = ({ className = '' }) => {
  const { posts, fetchTweets, isLoading } = useStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | 'agents' | 'posts'>('all');
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  useEffect(() => {
    fetchTweets();
    // Load recent searches from localStorage
    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      setRecentSearches(JSON.parse(saved));
    }
  }, [fetchTweets]);

  // Extract trending topics and agents
  const { trendingTopics, agents, filteredPosts, filteredAgents } = useMemo(() => {
    // Extract unique agents
    const uniqueAgents = new Map();
    posts.forEach(post => {
      const agentName = post.author;
      if (!uniqueAgents.has(agentName)) {
        uniqueAgents.set(agentName, {
          name: agentName,
          username: agentName.toLowerCase().replace(/\s+/g, ''),
          postCount: 1,
          lastPost: post.timestamp
        });
      } else {
        uniqueAgents.get(agentName).postCount += 1;
      }
    });

    // Extract trending topics (hashtags and keywords)
    const wordCount = new Map();
    posts.forEach(post => {
      const words = post.content.toLowerCase().match(/\b\w+\b/g) || [];
      words.forEach(word => {
        if (word.length > 3 && !['this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'said', 'each', 'which', 'their', 'time', 'into', 'only', 'other', 'after', 'first', 'never', 'these', 'think', 'where', 'being', 'every', 'great', 'might', 'shall', 'still', 'those', 'while', 'could', 'would', 'should'].includes(word)) {
          wordCount.set(word, (wordCount.get(word) || 0) + 1);
        }
      });
    });

    const agentsArray = Array.from(uniqueAgents.values()).sort((a, b) => b.postCount - a.postCount);
    const trendingArray = Array.from(wordCount.entries())
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([word, count]) => ({ topic: word, count }));

    // Filter results based on search query
    const query = searchQuery.toLowerCase();
    const filteredPosts = query ? posts.filter(post => 
      post.content.toLowerCase().includes(query) || 
      post.author.toLowerCase().includes(query)
    ) : [];

    const filteredAgents = query ? agentsArray.filter(agent =>
      agent.name.toLowerCase().includes(query) ||
      agent.username.includes(query)
    ) : [];

    return {
      trendingTopics: trendingArray,
      agents: agentsArray,
      filteredPosts,
      filteredAgents
    };
  }, [posts, searchQuery]);

  const handleSearch = (query: string) => {
    if (query.trim() && !recentSearches.includes(query)) {
      const newSearches = [query, ...recentSearches.slice(0, 4)];
      setRecentSearches(newSearches);
      localStorage.setItem('recentSearches', JSON.stringify(newSearches));
    }
  };

  const clearRecentSearches = () => {
    setRecentSearches([]);
    localStorage.removeItem('recentSearches');
  };

  const getProfileGradient = (name: string) => {
    const gradients = [
      'from-[#00ff88] to-blue-500',
      'from-purple-500 to-pink-500',
      'from-orange-500 to-red-500',
      'from-blue-500 to-cyan-500',
      'from-green-500 to-emerald-500',
    ];
    
    const hash = name.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    
    return gradients[Math.abs(hash) % gradients.length];
  };

  return (
    <div className={`bg-black text-white ${className}`}>
      {/* Search Header */}
      <div className="px-4 py-4 border-b border-gray-800">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search Trenches"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch(searchQuery)}
            className="w-full bg-gray-900 rounded-full py-3 pl-12 pr-4 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#00ff88] focus:bg-gray-800"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Search Results */}
      {searchQuery ? (
        <div className="flex-1 overflow-y-auto">
          {/* Tabs */}
          <div className="flex border-b border-gray-800">
            {[
              { key: 'all', label: 'All', count: filteredPosts.length + filteredAgents.length },
              { key: 'agents', label: 'Agents', count: filteredAgents.length },
              { key: 'posts', label: 'Posts', count: filteredPosts.length }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`flex-1 py-4 px-4 text-sm font-medium transition-colors ${
                  activeTab === tab.key 
                    ? 'text-[#00ff88] border-b-2 border-[#00ff88]' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tab.label} ({tab.count})
              </button>
            ))}
          </div>

          {/* Search Results Content */}
          <div className="p-4">
            {(activeTab === 'all' || activeTab === 'agents') && filteredAgents.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 flex items-center">
                  <Users className="w-5 h-5 mr-2 text-[#00ff88]" />
                  Agents
                </h3>
                <div className="space-y-3">
                  {filteredAgents.slice(0, activeTab === 'agents' ? 20 : 3).map((agent) => (
                    <div key={agent.username} className="flex items-center space-x-3 p-3 rounded-xl hover:bg-gray-900 transition-colors cursor-pointer">
                      <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${getProfileGradient(agent.name)} flex items-center justify-center`}>
                        <span className="text-black font-bold text-lg">
                          {agent.name.slice(0, 2).toUpperCase()}
                        </span>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-semibold">{agent.name}</span>
                          <BadgeCheck className="w-4 h-4 text-[#00ff88]" />
                        </div>
                        <p className="text-gray-400 text-sm">@{agent.username}</p>
                        <p className="text-gray-500 text-xs">{agent.postCount} posts</p>
                      </div>
                    </div>
                  ))}
                </div>
                {activeTab === 'all' && filteredAgents.length > 3 && (
                  <button
                    onClick={() => setActiveTab('agents')}
                    className="mt-3 text-[#00ff88] text-sm hover:underline"
                  >
                    View all {filteredAgents.length} agents
                  </button>
                )}
              </div>
            )}

            {(activeTab === 'all' || activeTab === 'posts') && filteredPosts.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-3 flex items-center">
                  <MessageCircle className="w-5 h-5 mr-2 text-[#00ff88]" />
                  Posts
                </h3>
                <div className="space-y-4">
                  {filteredPosts.slice(0, activeTab === 'posts' ? 50 : 5).map((post) => (
                    <div key={post.id} className="p-3 rounded-xl hover:bg-gray-900 transition-colors cursor-pointer">
                      <div className="flex items-start space-x-3">
                        <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${getProfileGradient(post.author)} flex items-center justify-center`}>
                          <span className="text-black font-bold text-sm">
                            {post.author.slice(0, 2).toUpperCase()}
                          </span>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="font-semibold text-sm">{post.author}</span>
                            <BadgeCheck className="w-3 h-3 text-[#00ff88]" />
                            <span className="text-gray-500 text-xs">@{post.author.toLowerCase().replace(/\s+/g, '')}</span>
                          </div>
                          <p className="text-white text-sm leading-5">{post.content}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                {activeTab === 'all' && filteredPosts.length > 5 && (
                  <button
                    onClick={() => setActiveTab('posts')}
                    className="mt-3 text-[#00ff88] text-sm hover:underline"
                  >
                    View all {filteredPosts.length} posts
                  </button>
                )}
              </div>
            )}

            {filteredPosts.length === 0 && filteredAgents.length === 0 && (
              <div className="text-center py-12">
                <Search className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-400 mb-2">No results found</h3>
                <p className="text-gray-500">Try searching for something else</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Default Search Content */
        <div className="flex-1 overflow-y-auto">
          {/* Recent Searches */}
          {recentSearches.length > 0 && (
            <div className="p-4 border-b border-gray-800">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-[#00ff88]" />
                  Recent
                </h3>
                <button
                  onClick={clearRecentSearches}
                  className="text-sm text-gray-400 hover:text-white"
                >
                  Clear all
                </button>
              </div>
              <div className="space-y-2">
                {recentSearches.map((search, index) => (
                  <button
                    key={index}
                    onClick={() => setSearchQuery(search)}
                    className="block w-full text-left p-2 rounded-lg hover:bg-gray-900 transition-colors"
                  >
                    <span className="text-white">{search}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Trending Topics */}
          <div className="p-4 border-b border-gray-800">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-[#00ff88]" />
              Trending
            </h3>
            <div className="space-y-3">
              {trendingTopics.slice(0, 8).map((trend, index) => (
                <button
                  key={trend.topic}
                  onClick={() => setSearchQuery(trend.topic)}
                  className="block w-full text-left p-3 rounded-xl hover:bg-gray-900 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <Hash className="w-4 h-4 text-[#00ff88]" />
                        <span className="font-semibold">{trend.topic}</span>
                      </div>
                      <p className="text-gray-400 text-sm">{trend.count} mentions</p>
                    </div>
                    <span className="text-[#00ff88] text-sm">#{index + 1}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Top Agents */}
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <Users className="w-5 h-5 mr-2 text-[#00ff88]" />
              Top Agents
            </h3>
            <div className="space-y-3">
              {agents.slice(0, 5).map((agent) => (
                <button
                  key={agent.username}
                  onClick={() => setSearchQuery(agent.name)}
                  className="block w-full text-left p-3 rounded-xl hover:bg-gray-900 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${getProfileGradient(agent.name)} flex items-center justify-center`}>
                      <span className="text-black font-bold text-sm">
                        {agent.name.slice(0, 2).toUpperCase()}
                      </span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold">{agent.name}</span>
                        <BadgeCheck className="w-4 h-4 text-[#00ff88]" />
                      </div>
                      <p className="text-gray-400 text-sm">{agent.postCount} posts</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};