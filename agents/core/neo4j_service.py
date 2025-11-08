"""
Neo4j Social Graph Service
Tracks agent interactions, relationships, and social dynamics in a graph database.
"""

import logging
import os
from typing import Dict, List, Optional, Any
from neo4j import GraphDatabase, Driver
from datetime import datetime


class Neo4jSocialGraph:
    """Service for tracking social graph in Neo4j"""

    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Initialize Neo4j connection

        Args:
            uri: Neo4j connection URI (default: bolt://localhost:7687)
            user: Neo4j username (default: neo4j)
            password: Neo4j password (from env or default)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "verysecret123")

        self.driver: Optional[Driver] = None
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Verify connectivity
            self.driver.verify_connectivity()
            self.logger.info(f"✅ Connected to Neo4j at {self.uri}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Neo4j: {e}")
            return False

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            self.logger.info("Neo4j connection closed")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def initialize_schema(self):
        """Create indexes and constraints for optimal performance"""
        with self.driver.session() as session:
            # Constraints (ensure uniqueness)
            constraints = [
                "CREATE CONSTRAINT agent_id_unique IF NOT EXISTS FOR (a:Agent) REQUIRE a.id IS UNIQUE",
                "CREATE CONSTRAINT tweet_id_unique IF NOT EXISTS FOR (t:Tweet) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT token_symbol_unique IF NOT EXISTS FOR (tk:Token) REQUIRE tk.symbol IS UNIQUE",
                "CREATE CONSTRAINT topic_name_unique IF NOT EXISTS FOR (tp:Topic) REQUIRE tp.name IS UNIQUE",
            ]

            # Indexes (improve query performance)
            indexes = [
                "CREATE INDEX agent_archetype_idx IF NOT EXISTS FOR (a:Agent) ON (a.archetype)",
                "CREATE INDEX agent_ecosystem_idx IF NOT EXISTS FOR (a:Agent) ON (a.ecosystem)",
                "CREATE INDEX tweet_timestamp_idx IF NOT EXISTS FOR (t:Tweet) ON (t.timestamp)",
                "CREATE INDEX tweet_sentiment_idx IF NOT EXISTS FOR (t:Tweet) ON (t.sentiment)",
                "CREATE INDEX token_price_idx IF NOT EXISTS FOR (tk:Token) ON (tk.price)",
            ]

            for constraint in constraints:
                try:
                    session.run(constraint)
                    self.logger.info(f"Created constraint: {constraint.split('FOR')[0]}")
                except Exception as e:
                    self.logger.warning(f"Constraint creation skipped: {e}")

            for index in indexes:
                try:
                    session.run(index)
                    self.logger.info(f"Created index: {index.split('FOR')[0]}")
                except Exception as e:
                    self.logger.warning(f"Index creation skipped: {e}")

    # ===== AGENT OPERATIONS =====

    def create_or_update_agent(self, agent_data: Dict[str, Any]):
        """Create or update an agent node in the graph"""
        query = """
        MERGE (a:Agent {id: $id})
        SET a.username = $username,
            a.alias = $alias,
            a.archetype = $archetype,
            a.ecosystem = $ecosystem,
            a.temperament = $temperament,
            a.tone = $tone,
            a.threat_level = $threat_level,
            a.last_updated = datetime()
        RETURN a
        """

        params = {
            "id": agent_data.get("id"),
            "username": agent_data.get("id"),
            "alias": agent_data.get("alias", agent_data.get("id")),
            "archetype": agent_data.get("classification", "unknown"),
            "ecosystem": agent_data.get("ecosystem", "crypto"),
            "temperament": agent_data.get("personality", {}).get("temperament", "neutral"),
            "tone": agent_data.get("personality", {}).get("tone", "neutral"),
            "threat_level": agent_data.get("threat_level", "gamma")
        }

        with self.driver.session() as session:
            result = session.run(query, params)
            self.logger.debug(f"Created/updated agent: {params['id']}")
            return result.single()

    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive stats for an agent from the graph"""
        query = """
        MATCH (a:Agent {id: $agent_id})
        OPTIONAL MATCH (a)-[:TWEETED]->(t:Tweet)
        OPTIONAL MATCH (a)-[:FOLLOWS]->(other:Agent)
        OPTIONAL MATCH (follower:Agent)-[:FOLLOWS]->(a)
        OPTIONAL MATCH (a)-[:INFLUENCED_BY]->(influencer:Agent)
        RETURN a.id as agent_id,
               count(DISTINCT t) as total_tweets,
               count(DISTINCT other) as following_count,
               count(DISTINCT follower) as follower_count,
               count(DISTINCT influencer) as influenced_by_count
        """

        with self.driver.session() as session:
            result = session.run(query, {"agent_id": agent_id})
            record = result.single()
            if record:
                return dict(record)
            return {}

    # ===== TWEET OPERATIONS =====

    def create_tweet_node(self, tweet_data: Dict[str, Any]):
        """Create a tweet node and link it to the agent"""
        query = """
        MATCH (a:Agent {id: $agent_id})
        CREATE (t:Tweet {
            id: $tweet_id,
            content: $content,
            timestamp: datetime($timestamp),
            sentiment: $sentiment,
            likes: 0,
            retweets: 0
        })
        CREATE (a)-[:TWEETED]->(t)
        RETURN t
        """

        params = {
            "agent_id": tweet_data.get("agent_id"),
            "tweet_id": tweet_data.get("id", f"tweet_{datetime.now().timestamp()}"),
            "content": tweet_data.get("content", ""),
            "timestamp": tweet_data.get("timestamp", datetime.now().isoformat()),
            "sentiment": tweet_data.get("sentiment", "neutral")
        }

        with self.driver.session() as session:
            result = session.run(query, params)
            self.logger.debug(f"Created tweet node: {params['tweet_id']}")
            return result.single()

    def track_like(self, agent_id: str, tweet_id: int, target_agent_id: str):
        """Track a like action in the graph"""
        query = """
        MATCH (liker:Agent {id: $agent_id})
        MATCH (tweet:Tweet {id: $tweet_id})
        MATCH (author:Agent {id: $target_agent_id})
        MERGE (liker)-[r:LIKED {timestamp: datetime()}]->(tweet)
        WITH liker, author, count(r) as like_count
        WHERE like_count > 3
        MERGE (liker)-[inf:INFLUENCED_BY]->(author)
        ON CREATE SET inf.strength = 1, inf.created = datetime()
        ON MATCH SET inf.strength = inf.strength + 0.1
        """

        with self.driver.session() as session:
            session.run(query, {
                "agent_id": agent_id,
                "tweet_id": tweet_id,
                "target_agent_id": target_agent_id
            })
            self.logger.debug(f"{agent_id} liked tweet {tweet_id} from {target_agent_id}")

    def track_retweet(self, agent_id: str, tweet_id: int, target_agent_id: str):
        """Track a retweet action in the graph"""
        query = """
        MATCH (retweeter:Agent {id: $agent_id})
        MATCH (tweet:Tweet {id: $tweet_id})
        MATCH (author:Agent {id: $target_agent_id})
        MERGE (retweeter)-[r:RETWEETED {timestamp: datetime()}]->(tweet)
        WITH retweeter, author
        MERGE (retweeter)-[inf:INFLUENCED_BY]->(author)
        ON CREATE SET inf.strength = 2, inf.created = datetime()
        ON MATCH SET inf.strength = inf.strength + 0.2
        """

        with self.driver.session() as session:
            session.run(query, {
                "agent_id": agent_id,
                "tweet_id": tweet_id,
                "target_agent_id": target_agent_id
            })
            self.logger.debug(f"{agent_id} retweeted tweet {tweet_id} from {target_agent_id}")

    def track_reply(self, agent_id: str, original_tweet_id: int, reply_tweet_id: int, target_agent_id: str):
        """Track a reply action in the graph"""
        query = """
        MATCH (replier:Agent {id: $agent_id})
        MATCH (original:Tweet {id: $original_tweet_id})
        MATCH (reply:Tweet {id: $reply_tweet_id})
        MATCH (author:Agent {id: $target_agent_id})
        CREATE (reply)-[:REPLIED_TO {timestamp: datetime()}]->(original)
        WITH replier, author
        MERGE (replier)-[inf:INFLUENCED_BY]->(author)
        ON CREATE SET inf.strength = 1.5, inf.created = datetime()
        ON MATCH SET inf.strength = inf.strength + 0.15
        """

        with self.driver.session() as session:
            session.run(query, {
                "agent_id": agent_id,
                "original_tweet_id": original_tweet_id,
                "reply_tweet_id": reply_tweet_id,
                "target_agent_id": target_agent_id
            })
            self.logger.debug(f"{agent_id} replied to tweet {original_tweet_id} from {target_agent_id}")

    # ===== FOLLOW/RELATIONSHIP OPERATIONS =====

    def create_follow_relationship(self, follower_id: str, followee_id: str):
        """Create a follow relationship between agents"""
        query = """
        MATCH (follower:Agent {id: $follower_id})
        MATCH (followee:Agent {id: $followee_id})
        MERGE (follower)-[r:FOLLOWS {since: datetime()}]->(followee)
        RETURN r
        """

        with self.driver.session() as session:
            result = session.run(query, {
                "follower_id": follower_id,
                "followee_id": followee_id
            })
            self.logger.info(f"{follower_id} now follows {followee_id}")
            return result.single()

    def remove_follow_relationship(self, follower_id: str, followee_id: str):
        """Remove a follow relationship"""
        query = """
        MATCH (follower:Agent {id: $follower_id})-[r:FOLLOWS]->(followee:Agent {id: $followee_id})
        DELETE r
        """

        with self.driver.session() as session:
            session.run(query, {
                "follower_id": follower_id,
                "followee_id": followee_id
            })
            self.logger.info(f"{follower_id} unfollowed {followee_id}")

    # ===== TOKEN/TOPIC OPERATIONS =====

    def link_tweet_to_token(self, tweet_id: int, token_symbol: str, sentiment: str = "neutral"):
        """Link a tweet to a token it mentions"""
        query = """
        MATCH (t:Tweet {id: $tweet_id})
        MERGE (tk:Token {symbol: $symbol})
        MERGE (t)-[m:MENTIONS {sentiment: $sentiment, timestamp: datetime()}]->(tk)
        RETURN m
        """

        with self.driver.session() as session:
            result = session.run(query, {
                "tweet_id": tweet_id,
                "symbol": token_symbol.upper(),
                "sentiment": sentiment
            })
            return result.single()

    def track_agent_sentiment_on_token(self, agent_id: str, token_symbol: str, sentiment: str):
        """Track an agent's sentiment towards a token"""
        if sentiment == "positive":
            rel_type = "BULLISH_ON"
        elif sentiment == "negative":
            rel_type = "BEARISH_ON"
        else:
            return  # Don't track neutral sentiment

        query = f"""
        MATCH (a:Agent {{id: $agent_id}})
        MERGE (tk:Token {{symbol: $symbol}})
        MERGE (a)-[r:{rel_type}]->(tk)
        ON CREATE SET r.strength = 1, r.first_expressed = datetime(), r.last_updated = datetime()
        ON MATCH SET r.strength = r.strength + 1, r.last_updated = datetime()
        RETURN r
        """

        with self.driver.session() as session:
            result = session.run(query, {
                "agent_id": agent_id,
                "symbol": token_symbol.upper()
            })
            return result.single()

    # ===== ANALYSIS QUERIES =====

    def find_echo_chambers(self, min_size: int = 3) -> List[Dict[str, Any]]:
        """Find echo chambers (highly connected agent groups)"""
        query = """
        MATCH (a:Agent)-[:FOLLOWS]->(b:Agent)
        WITH a, collect(b) as following
        WHERE size(following) >= $min_size
        RETURN a.id as agent_id,
               a.archetype as archetype,
               [f in following | f.id] as follows,
               size(following) as network_size
        ORDER BY network_size DESC
        LIMIT 20
        """

        with self.driver.session() as session:
            result = session.run(query, {"min_size": min_size})
            return [dict(record) for record in result]

    def get_influence_leaders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find most influential agents based on INFLUENCED_BY relationships"""
        query = """
        MATCH (influencer:Agent)<-[r:INFLUENCED_BY]-(influenced:Agent)
        WITH influencer, sum(r.strength) as total_influence, count(influenced) as influenced_count
        RETURN influencer.id as agent_id,
               influencer.alias as alias,
               influencer.archetype as archetype,
               total_influence,
               influenced_count
        ORDER BY total_influence DESC
        LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(query, {"limit": limit})
            return [dict(record) for record in result]

    def get_sentiment_propagation_path(self, token_symbol: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Track how sentiment about a token spreads through the network"""
        query = """
        MATCH path = (start:Agent)-[:INFLUENCED_BY*1..$max_depth]->(end:Agent)
        WHERE (start)-[:BULLISH_ON|BEARISH_ON]->(:Token {symbol: $symbol})
        AND (end)-[:BULLISH_ON|BEARISH_ON]->(:Token {symbol: $symbol})
        RETURN [node in nodes(path) | node.id] as propagation_path,
               length(path) as path_length
        ORDER BY path_length
        LIMIT 20
        """

        with self.driver.session() as session:
            result = session.run(query, {
                "symbol": token_symbol.upper(),
                "max_depth": max_depth
            })
            return [dict(record) for record in result]

    def get_agent_recommendations(self, agent_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recommend agents to follow based on network analysis"""
        query = """
        MATCH (a:Agent {id: $agent_id})-[:FOLLOWS]->(friend:Agent)-[:FOLLOWS]->(recommendation:Agent)
        WHERE NOT (a)-[:FOLLOWS]->(recommendation)
        AND a <> recommendation
        WITH recommendation, count(DISTINCT friend) as common_connections
        MATCH (recommendation)<-[:INFLUENCED_BY]-(influenced:Agent)
        WITH recommendation, common_connections, count(influenced) as influence_score
        RETURN recommendation.id as agent_id,
               recommendation.alias as alias,
               recommendation.archetype as archetype,
               common_connections,
               influence_score,
               (common_connections * 2 + influence_score) as recommendation_score
        ORDER BY recommendation_score DESC
        LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(query, {
                "agent_id": agent_id,
                "limit": limit
            })
            return [dict(record) for record in result]

    def detect_coordinated_behavior(self, time_window_minutes: int = 60) -> List[Dict[str, Any]]:
        """Detect potential coordinated behavior (agents acting in sync)"""
        query = """
        MATCH (a1:Agent)-[r1:LIKED|RETWEETED]->(t:Tweet)
        WHERE r1.timestamp > datetime() - duration({minutes: $time_window})
        WITH t, collect(DISTINCT a1) as actors
        WHERE size(actors) >= 3
        MATCH (author:Agent)-[:TWEETED]->(t)
        RETURN t.id as tweet_id,
               t.content as content,
               author.id as author,
               [actor in actors | actor.id] as coordinated_actors,
               size(actors) as actor_count
        ORDER BY actor_count DESC
        LIMIT 10
        """

        with self.driver.session() as session:
            result = session.run(query, {"time_window": time_window_minutes})
            return [dict(record) for record in result]

    def get_network_statistics(self) -> Dict[str, Any]:
        """Get overall network statistics"""
        query = """
        MATCH (a:Agent)
        OPTIONAL MATCH (a)-[:FOLLOWS]->(other)
        OPTIONAL MATCH (a)-[:TWEETED]->(t:Tweet)
        RETURN count(DISTINCT a) as total_agents,
               count(DISTINCT t) as total_tweets,
               count(DISTINCT other) as total_follow_relationships,
               avg(size((a)-[:FOLLOWS]->())) as avg_following
        """

        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                return dict(record)
            return {}


# Convenience function for testing
def test_neo4j_connection():
    """Test Neo4j connection and print stats"""
    graph = Neo4jSocialGraph()
    if graph.connect():
        graph.initialize_schema()
        stats = graph.get_network_statistics()
        print(f"✅ Neo4j connection successful!")
        print(f"Network stats: {stats}")
        graph.close()
        return True
    else:
        print(f"❌ Neo4j connection failed")
        return False


if __name__ == "__main__":
    test_neo4j_connection()
