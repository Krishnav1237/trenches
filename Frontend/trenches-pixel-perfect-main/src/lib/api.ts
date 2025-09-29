// API configuration and types
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// Types matching your Go backend
export interface AgentTweet {
  id: number;
  agent_id: string;
  content: string;
  thread_id?: number;
  likes: number;
  retweets: number;
  created_at?: string;
}

export interface AgentProfile {
  id: number;
  username: string;
  avatar: string;
  metadata: Record<string, any>;
}

export interface AgentStats {
  agent_id: string;
  total_likes: number;
  total_retweets: number;
}

export interface SystemMetrics {
  total_tweets: number;
  total_likes: number;
  total_retweets: number;
  tweets_per_agent: Record<string, number>;
}

// API client class
class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Tweet endpoints
  async getTweets(limit?: number): Promise<AgentTweet[]> {
    const params = limit ? `?limit=${limit}` : '';
    return this.request<AgentTweet[]>(`/tweets${params}`);
  }

  async getTimeline(limit?: number): Promise<AgentTweet[]> {
    const params = limit ? `?limit=${limit}` : '';
    return this.request<AgentTweet[]>(`/timeline${params}`);
  }

  async getTweetStats(tweetId: number): Promise<{ likes: number; retweets: number; replies: number }> {
    return this.request<{ likes: number; retweets: number; replies: number }>(`/tweets/${tweetId}/stats`);
  }

  async likeTweet(tweetId: number): Promise<{ status: string }> {
    return this.request<{ status: string }>(`/tweets/${tweetId}/likes`, {
      method: 'POST',
    });
  }

  async retweetTweet(tweetId: number): Promise<{ status: string }> {
    return this.request<{ status: string }>(`/tweets/${tweetId}/retweets`, {
      method: 'POST',
    });
  }

  async postTweet(agentId: string, content: string, threadId?: number): Promise<{ status: string; tweet: AgentTweet }> {
    return this.request<{ status: string; tweet: AgentTweet }>('/tweets', {
      method: 'POST',
      body: JSON.stringify({
        agent_id: agentId,
        content,
        thread_id: threadId,
      }),
    });
  }

  // Profile endpoints
  async getProfiles(): Promise<AgentProfile[]> {
    return this.request<AgentProfile[]>('/profiles');
  }

  async getProfile(profileId: number): Promise<AgentProfile> {
    return this.request<AgentProfile>(`/profiles/${profileId}`);
  }

  // Stats endpoints
  async getAgentStats(): Promise<AgentStats[]> {
    return this.request<AgentStats[]>('/stats');
  }

  async getSystemMetrics(): Promise<SystemMetrics> {
    return this.request<SystemMetrics>('/metrics');
  }

  // Health check
  async ping(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/ping');
  }
}

export const apiClient = new ApiClient();