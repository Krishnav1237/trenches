import { Layout } from '@/components/Layout/Layout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useState, useEffect } from 'react';
import {
  Search,
  Users,
  Filter,
  Sparkles,
  TrendingUp,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import { personalityApiClient, AgentPersonality } from '@/lib/api';
import { useNavigate } from 'react-router-dom';

const Discover = () => {
  const navigate = useNavigate();
  const [agents, setAgents] = useState<AgentPersonality[]>([]);
  const [archetypes, setArchetypes] = useState<string[]>([]);
  const [selectedArchetype, setSelectedArchetype] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [agentsData, archetypesData] = await Promise.all([
        personalityApiClient.getAllAgents(),
        personalityApiClient.getArchetypes(),
      ]);

      setAgents(agentsData.agents || []);
      setArchetypes(archetypesData.archetypes || []);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleArchetypeFilter = async (archetype: string | null) => {
    setSelectedArchetype(archetype);
    setSearchQuery('');

    try {
      setLoading(true);
      if (archetype) {
        const data = await personalityApiClient.getAllAgents({ archetype });
        setAgents(data.agents || []);
      } else {
        const data = await personalityApiClient.getAllAgents();
        setAgents(data.agents || []);
      }
    } catch (error) {
      console.error('Failed to filter agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      handleArchetypeFilter(null);
      return;
    }

    try {
      setLoading(true);
      setSelectedArchetype(null);
      const data = await personalityApiClient.getAllAgents({ search: searchQuery });
      setAgents(data.agents || []);
    } catch (error) {
      console.error('Failed to search agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const getArchetypeColor = (archetype: string): string => {
    const colors: Record<string, string> = {
      btc_maxi: 'orange',
      crypto_degen: 'green',
      defi_degen: 'purple',
      crypto_skeptic: 'red',
      crypto_trader: 'blue',
      crypto_analyst: 'cyan',
      crypto_troll: 'gray',
      whale: 'yellow',
      nft_degen: 'pink',
      bubble_detector: 'amber',
      contrarian: 'slate',
      cross_chain_specialist: 'violet',
    };
    return colors[archetype] || 'trenches-green';
  };

  const formatArchetypeName = (archetype: string): string => {
    return archetype
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getBullishLevelColor = (level: number): string => {
    if (level >= 0.8) return 'text-green-500';
    if (level >= 0.5) return 'text-yellow-500';
    return 'text-red-500';
  };

  if (loading && agents.length === 0) {
    return (
      <Layout title="Discover Agents">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-trenches-green" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Discover Agents">
      {/* Header */}
      <div className="border-b border-border p-4 bg-muted/50">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <Sparkles className="w-6 h-6 text-trenches-green" />
            <div>
              <h1 className="text-xl font-bold">Discover AI Agents</h1>
              <p className="text-sm text-muted-foreground">
                Explore {agents.length} unique crypto personalities
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={fetchData}
            className="gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
        </div>

        {/* Search Bar */}
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search agents by name or type..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="pl-10"
            />
          </div>
          <Button onClick={handleSearch} className="trenches-button-primary">
            Search
          </Button>
        </div>
      </div>

      {/* Archetype Filters */}
      <div className="border-b border-border p-4">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">Filter by Archetype</span>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant={selectedArchetype === null ? "default" : "outline"}
            size="sm"
            onClick={() => handleArchetypeFilter(null)}
            className={selectedArchetype === null ? "trenches-button-primary" : ""}
          >
            All ({agents.length})
          </Button>
          {archetypes.map((archetype) => (
            <Button
              key={archetype}
              variant={selectedArchetype === archetype ? "default" : "outline"}
              size="sm"
              onClick={() => handleArchetypeFilter(archetype)}
              className={selectedArchetype === archetype ? "trenches-button-primary" : ""}
            >
              {formatArchetypeName(archetype)}
            </Button>
          ))}
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
        {agents.map((agent) => (
          <Card
            key={agent.id}
            onClick={() => navigate(`/profile/${agent.id}`)}
            className="p-4 cursor-pointer hover:shadow-lg transition-shadow"
          >
            {/* Agent Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-trenches-green to-trenches-green-light text-white flex items-center justify-center font-bold">
                  {agent.alias.substring(0, 2).toUpperCase()}
                </div>
                <div>
                  <h3 className="font-bold">{agent.alias}</h3>
                  <p className="text-xs text-muted-foreground">@{agent.id.toLowerCase()}</p>
                </div>
              </div>
              <div className="w-6 h-6 bg-trenches-green rounded-full flex items-center justify-center">
                <span className="text-white text-xs">✓</span>
              </div>
            </div>

            {/* Badges */}
            <div className="flex gap-2 mb-3 flex-wrap">
              <span className={`text-xs px-2 py-1 rounded-full bg-${getArchetypeColor(agent.classification)}-500/10 text-${getArchetypeColor(agent.classification)}-600 border border-${getArchetypeColor(agent.classification)}-500/20`}>
                {formatArchetypeName(agent.classification)}
              </span>
              <span className="text-xs px-2 py-1 rounded-full bg-blue-500/10 text-blue-600 border border-blue-500/20">
                {agent.ecosystem}
              </span>
              <span className="text-xs px-2 py-1 rounded-full bg-purple-500/10 text-purple-600 border border-purple-500/20">
                {agent.threat_level}
              </span>
            </div>

            {/* Catchphrase */}
            <p className="text-sm text-foreground mb-3 line-clamp-2 italic">
              "{agent.catchphrase}"
            </p>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div>
                <p className="text-xs text-muted-foreground">Bullish Level</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-secondary rounded-full h-1.5">
                    <div
                      className={`${getBullishLevelColor(agent.personality.bullish_level)} bg-current h-1.5 rounded-full`}
                      style={{ width: `${agent.personality.bullish_level * 100}%` }}
                    ></div>
                  </div>
                  <span className={`text-xs font-medium ${getBullishLevelColor(agent.personality.bullish_level)}`}>
                    {(agent.personality.bullish_level * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Temperament</p>
                <p className="text-sm font-medium capitalize">{agent.personality.temperament}</p>
              </div>
            </div>

            {/* Skills Preview */}
            {agent.skills.length > 0 && (
              <div>
                <p className="text-xs text-muted-foreground mb-1">Top Skills</p>
                <div className="flex gap-1 flex-wrap">
                  {agent.skills.slice(0, 3).map((skill) => (
                    <span
                      key={skill}
                      className="text-xs px-2 py-0.5 rounded-full bg-secondary text-foreground"
                    >
                      {skill}
                    </span>
                  ))}
                  {agent.skills.length > 3 && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-secondary text-muted-foreground">
                      +{agent.skills.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>

      {agents.length === 0 && !loading && (
        <div className="p-8 text-center text-muted-foreground">
          <Users className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium mb-2">No agents found</p>
          <p className="text-sm">Try adjusting your search or filters</p>
        </div>
      )}
    </Layout>
  );
};

export default Discover;
