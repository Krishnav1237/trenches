import { Layout } from '@/components/Layout/Layout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useState, useEffect } from 'react';
import {
  Wallet as WalletIcon,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  DollarSign,
  BarChart3,
  Loader2,
  Trophy,
  RefreshCw,
} from 'lucide-react';
import { apiClient } from '@/lib/api';

interface WalletInfo {
  wallet_address: string;
  latest_balance: number;
  snapshot_count: number;
  last_update: string;
}

interface WalletAnalytics {
  wallet_address: string;
  latest_balance: number;
  first_balance: number;
  highest_balance: number;
  lowest_balance: number;
  balance_change: number;
  percent_change: number;
  snapshot_count: number;
  recent_snapshots: Array<{
    id: number;
    wallet_address: string;
    balance: number;
    block_number: number;
    timestamp: string;
  }>;
}

interface LeaderboardEntry {
  rank: number;
  wallet_address: string;
  balance: number;
  snapshot_count: number;
}

const Wallet = () => {
  const [wallets, setWallets] = useState<WalletInfo[]>([]);
  const [selectedWallet, setSelectedWallet] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<WalletAnalytics | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchWalletData();
  }, []);

  useEffect(() => {
    if (selectedWallet) {
      fetchAnalytics(selectedWallet);
    }
  }, [selectedWallet]);

  const fetchWalletData = async () => {
    try {
      setLoading(true);
      const [walletsData, leaderboardData] = await Promise.all([
        apiClient.getWallets(),
        apiClient.getWalletLeaderboard(10),
      ]);

      setWallets(walletsData.wallets || []);
      setLeaderboard(leaderboardData.leaderboard || []);

      // Auto-select first wallet if available
      if (walletsData.wallets && walletsData.wallets.length > 0) {
        setSelectedWallet(walletsData.wallets[0].wallet_address);
      }
    } catch (error) {
      console.error('Failed to fetch wallet data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async (address: string) => {
    try {
      const data = await apiClient.getWalletAnalytics(address);
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const formatAddress = (address: string) => {
    if (address.length <= 13) return address;
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const formatBalance = (balance: number) => {
    if (balance >= 1000000) {
      return `$${(balance / 1000000).toFixed(2)}M`;
    } else if (balance >= 1000) {
      return `$${(balance / 1000).toFixed(2)}K`;
    }
    return `$${balance.toFixed(2)}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <Layout title="Wallet Dashboard">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-trenches-green" />
        </div>
      </Layout>
    );
  }

  const totalPortfolioValue = wallets.reduce((sum, w) => sum + w.latest_balance, 0);

  return (
    <Layout title="Wallet Dashboard">
      {/* Header */}
      <div className="border-b border-border p-4 bg-muted/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <WalletIcon className="w-6 h-6 text-trenches-green" />
            <div>
              <h1 className="text-xl font-bold">Wallet Portfolio</h1>
              <p className="text-sm text-muted-foreground">
                Tracking {wallets.length} wallet{wallets.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={fetchWalletData}
            className="gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Portfolio Summary */}
      <div className="p-4 border-b border-border bg-gradient-to-r from-trenches-green/10 to-transparent">
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">Total Portfolio Value</p>
          <p className="text-4xl font-bold">{formatBalance(totalPortfolioValue)}</p>
          {analytics && (
            <div className="flex items-center gap-2">
              {analytics.percent_change >= 0 ? (
                <>
                  <ArrowUpRight className="w-4 h-4 text-green-500" />
                  <span className="text-green-500 font-medium">
                    +{analytics.percent_change.toFixed(2)}%
                  </span>
                </>
              ) : (
                <>
                  <ArrowDownRight className="w-4 h-4 text-red-500" />
                  <span className="text-red-500 font-medium">
                    {analytics.percent_change.toFixed(2)}%
                  </span>
                </>
              )}
              <span className="text-sm text-muted-foreground">
                ({analytics.balance_change >= 0 ? '+' : ''}
                {formatBalance(analytics.balance_change)})
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="w-full bg-transparent border-b border-border rounded-none h-auto p-0">
          <TabsTrigger
            value="overview"
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            Overview
          </TabsTrigger>
          <TabsTrigger
            value="analytics"
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            Analytics
          </TabsTrigger>
          <TabsTrigger
            value="leaderboard"
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            Leaderboard
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-0">
          <div className="divide-y divide-border">
            {wallets.length > 0 ? (
              wallets.map((wallet) => (
                <div
                  key={wallet.wallet_address}
                  onClick={() => {
                    setSelectedWallet(wallet.wallet_address);
                    setActiveTab('analytics');
                  }}
                  className="p-4 hover:bg-secondary cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <WalletIcon className="w-4 h-4 text-trenches-green" />
                        <span className="font-mono text-sm">
                          {formatAddress(wallet.wallet_address)}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {wallet.snapshot_count} snapshots •
                        Last update: {formatDate(wallet.last_update)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold">
                        {formatBalance(wallet.latest_balance)}
                      </p>
                      <ArrowUpRight className="w-4 h-4 text-trenches-green ml-auto" />
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                <WalletIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No wallets tracked yet</p>
              </div>
            )}
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="mt-0">
          {analytics ? (
            <div className="space-y-4 p-4">
              {/* Selected Wallet Header */}
              <Card className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Selected Wallet</p>
                    <p className="font-mono text-sm font-medium">
                      {formatAddress(analytics.wallet_address)}
                    </p>
                  </div>
                  <Button variant="outline" size="sm">
                    View on Explorer
                  </Button>
                </div>
              </Card>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-4">
                <Card className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <DollarSign className="w-4 h-4 text-trenches-green" />
                    <p className="text-xs text-muted-foreground">Current Balance</p>
                  </div>
                  <p className="text-2xl font-bold">
                    {formatBalance(analytics.latest_balance)}
                  </p>
                </Card>

                <Card className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    {analytics.balance_change >= 0 ? (
                      <TrendingUp className="w-4 h-4 text-green-500" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-500" />
                    )}
                    <p className="text-xs text-muted-foreground">Change</p>
                  </div>
                  <p className="text-2xl font-bold">
                    {analytics.percent_change >= 0 ? '+' : ''}
                    {analytics.percent_change.toFixed(2)}%
                  </p>
                </Card>

                <Card className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-blue-500" />
                    <p className="text-xs text-muted-foreground">Highest Balance</p>
                  </div>
                  <p className="text-xl font-bold">
                    {formatBalance(analytics.highest_balance)}
                  </p>
                </Card>

                <Card className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingDown className="w-4 h-4 text-orange-500" />
                    <p className="text-xs text-muted-foreground">Lowest Balance</p>
                  </div>
                  <p className="text-xl font-bold">
                    {formatBalance(analytics.lowest_balance)}
                  </p>
                </Card>
              </div>

              {/* Recent Activity */}
              <Card className="p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Activity className="w-4 h-4 text-trenches-green" />
                  <h3 className="font-bold">Recent Snapshots</h3>
                </div>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {analytics.recent_snapshots.map((snapshot, index) => (
                    <div
                      key={snapshot.id}
                      className="flex items-center justify-between p-2 rounded hover:bg-secondary"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-trenches-green/10 flex items-center justify-center text-xs font-bold text-trenches-green">
                          {index + 1}
                        </div>
                        <div>
                          <p className="text-sm font-medium">
                            {formatBalance(snapshot.balance)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Block {snapshot.block_number.toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(snapshot.timestamp)}
                      </p>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          ) : (
            <div className="p-8 text-center text-muted-foreground">
              <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Select a wallet to view analytics</p>
            </div>
          )}
        </TabsContent>

        {/* Leaderboard Tab */}
        <TabsContent value="leaderboard" className="mt-0">
          <div className="divide-y divide-border">
            {leaderboard.map((entry) => (
              <div
                key={entry.wallet_address}
                className="p-4 hover:bg-secondary cursor-pointer transition-colors"
                onClick={() => {
                  setSelectedWallet(entry.wallet_address);
                  setActiveTab('analytics');
                }}
              >
                <div className="flex items-center gap-4">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      entry.rank === 1
                        ? 'bg-yellow-500 text-white'
                        : entry.rank === 2
                        ? 'bg-gray-400 text-white'
                        : entry.rank === 3
                        ? 'bg-orange-600 text-white'
                        : 'bg-muted text-foreground'
                    }`}
                  >
                    {entry.rank <= 3 ? (
                      <Trophy className="w-5 h-5" />
                    ) : (
                      entry.rank
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="font-mono text-sm font-medium">
                      {formatAddress(entry.wallet_address)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {entry.snapshot_count} snapshots
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold">
                      {formatBalance(entry.balance)}
                    </p>
                    <p className="text-xs text-trenches-green">Rank #{entry.rank}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </Layout>
  );
};

export default Wallet;
