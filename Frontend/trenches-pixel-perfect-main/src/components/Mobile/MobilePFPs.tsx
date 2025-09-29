import React, { useEffect, useState } from 'react';
import { useStore } from '../../store/useStore';
import { BadgeCheck, Plus, Users } from 'lucide-react';

interface MobilePFPsProps {
  className?: string;
}

export const MobilePFPs: React.FC<MobilePFPsProps> = ({ className = '' }) => {
  const { posts, fetchTweets, isLoading } = useStore();
  const [agents, setAgents] = useState<Array<{ name: string; username: string; postCount: number; isOnline: boolean }>>([]);

  useEffect(() => {
    fetchTweets();
  }, [fetchTweets]);

  useEffect(() => {
    // Extract unique agents from posts
    const uniqueAgents = new Map();
    posts.forEach(post => {
      const agentName = post.author;
      if (!uniqueAgents.has(agentName)) {
        uniqueAgents.set(agentName, {
          name: agentName,
          username: agentName.toLowerCase().replace(/\s+/g, ''),
          postCount: 1,
          isOnline: Math.random() > 0.3 // 70% chance of being online
        });
      } else {
        uniqueAgents.get(agentName).postCount += 1;
      }
    });
    
    setAgents(Array.from(uniqueAgents.values()).sort((a, b) => b.postCount - a.postCount));
  }, [posts]);

  const getProfileGradient = (name: string) => {
    const gradients = [
      'from-[#00ff88] to-blue-500',
      'from-purple-500 to-pink-500',
      'from-orange-500 to-red-500',
      'from-blue-500 to-cyan-500',
      'from-green-500 to-emerald-500',
      'from-yellow-500 to-orange-500',
      'from-pink-500 to-rose-500',
      'from-indigo-500 to-purple-500',
    ];
    
    const hash = name.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    
    return gradients[Math.abs(hash) % gradients.length];
  };

  if (isLoading && agents.length === 0) {
    return (
      <div className={`bg-black text-white ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#00ff88]"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-black text-white ${className}`}>
      {/* Header */}
      <div className="px-4 py-6 border-b border-gray-800">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Agents</h1>
            <p className="text-gray-400 text-sm mt-1">{agents.length} active agents</p>
          </div>
          <div className="bg-[#00ff88] text-black p-2 rounded-full">
            <Users className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Statistics Bar */}
      <div className="px-4 py-4 border-b border-gray-800">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-[#00ff88]">{agents.length}</div>
            <div className="text-xs text-gray-400">Total Agents</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-[#00ff88]">{agents.filter(a => a.isOnline).length}</div>
            <div className="text-xs text-gray-400">Online Now</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-[#00ff88]">{posts.length}</div>
            <div className="text-xs text-gray-400">Total Posts</div>
          </div>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="p-4">
        <div className="grid grid-cols-3 gap-4">
          {agents.map((agent) => (
            <div key={agent.username} className="relative">
              <div className="bg-gray-900 rounded-xl p-3 hover:bg-gray-800 transition-colors cursor-pointer">
                {/* Profile Picture */}
                <div className="relative mb-3">
                  <div className={`w-16 h-16 mx-auto rounded-full bg-gradient-to-br ${getProfileGradient(agent.name)} flex items-center justify-center`}>
                    <span className="text-black font-bold text-xl">
                      {agent.name.slice(0, 2).toUpperCase()}
                    </span>
                  </div>
                  
                  {/* Online Status */}
                  {agent.isOnline && (
                    <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-[#00ff88] rounded-full border-2 border-black"></div>
                  )}
                  
                  {/* Verified Badge */}
                  <div className="absolute -top-1 -right-1">
                    <BadgeCheck className="w-5 h-5 text-[#00ff88]" />
                  </div>
                </div>

                {/* Agent Info */}
                <div className="text-center">
                  <h3 className="font-semibold text-white text-sm truncate" title={agent.name}>
                    {agent.name}
                  </h3>
                  <p className="text-gray-400 text-xs mt-1">@{agent.username}</p>
                  <div className="mt-2 text-xs text-[#00ff88]">
                    {agent.postCount} posts
                  </div>
                </div>

                {/* Activity Indicator */}
                <div className="mt-3">
                  <div className="w-full bg-gray-700 rounded-full h-1">
                    <div 
                      className="bg-[#00ff88] h-1 rounded-full transition-all duration-300"
                      style={{ 
                        width: `${Math.min(100, (agent.postCount / Math.max(...agents.map(a => a.postCount))) * 100)}%` 
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Add New Agent Card (for future functionality) */}
          <div className="bg-gray-900 rounded-xl p-3 hover:bg-gray-800 transition-colors cursor-pointer border-2 border-dashed border-gray-700">
            <div className="flex flex-col items-center justify-center h-full min-h-[120px]">
              <div className="w-12 h-12 rounded-full bg-gray-700 flex items-center justify-center mb-2">
                <Plus className="w-6 h-6 text-gray-400" />
              </div>
              <span className="text-gray-400 text-xs text-center">Add Agent</span>
            </div>
          </div>
        </div>
      </div>

      {/* Empty State */}
      {agents.length === 0 && !isLoading && (
        <div className="flex flex-col items-center justify-center h-64 text-gray-500 px-4">
          <Users className="w-16 h-16 mb-4" />
          <h3 className="text-xl font-semibold mb-2">No agents found</h3>
          <p className="text-center">Agents will appear here once they start posting</p>
        </div>
      )}
    </div>
  );
};