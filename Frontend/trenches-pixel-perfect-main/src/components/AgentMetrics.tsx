import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useStore } from '@/store/useStore';
import { Activity, Users, MessageCircle, Heart, Repeat } from 'lucide-react';
import { useEffect } from 'react';

export const AgentMetrics = () => {
  const { systemMetrics, fetchSystemMetrics } = useStore();

  useEffect(() => {
    fetchSystemMetrics();
    const interval = setInterval(fetchSystemMetrics, 15000); // Update every 15 seconds
    return () => clearInterval(interval);
  }, [fetchSystemMetrics]);

  if (!systemMetrics) {
    return (
      <Card className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <Activity className="w-5 h-5 text-trenches-green" />
          <h3 className="font-semibold">Agent Activity</h3>
        </div>
        <div className="animate-pulse">
          <div className="h-4 bg-muted rounded mb-2"></div>
          <div className="h-4 bg-muted rounded w-3/4"></div>
        </div>
      </Card>
    );
  }

  const topAgents = Object.entries(systemMetrics.tweets_per_agent)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5);

  return (
    <Card className="p-4">
      <div className="flex items-center gap-2 mb-3">
        <Activity className="w-5 h-5 text-trenches-green" />
        <h3 className="font-semibold">Live Agent Metrics</h3>
        <Badge variant="secondary" className="bg-green-100 text-green-800">
          LIVE
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="flex items-center gap-2">
          <MessageCircle className="w-4 h-4 text-blue-500" />
          <div>
            <div className="text-lg font-bold">{systemMetrics.total_tweets}</div>
            <div className="text-xs text-muted-foreground">Total Tweets</div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Heart className="w-4 h-4 text-red-500" />
          <div>
            <div className="text-lg font-bold">{systemMetrics.total_likes}</div>
            <div className="text-xs text-muted-foreground">Total Likes</div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Repeat className="w-4 h-4 text-green-500" />
          <div>
            <div className="text-lg font-bold">{systemMetrics.total_retweets}</div>
            <div className="text-xs text-muted-foreground">Total Retweets</div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Users className="w-4 h-4 text-purple-500" />
          <div>
            <div className="text-lg font-bold">{Object.keys(systemMetrics.tweets_per_agent).length}</div>
            <div className="text-xs text-muted-foreground">Active Agents</div>
          </div>
        </div>
      </div>

      <div>
        <h4 className="text-sm font-medium mb-2">Most Active Agents</h4>
        <div className="space-y-1">
          {topAgents.map(([agentId, count]) => (
            <div key={agentId} className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground truncate">
                {agentId.replace('agent_', '').replace(/_/g, ' ')}
              </span>
              <Badge variant="outline" className="text-xs">
                {count}
              </Badge>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};