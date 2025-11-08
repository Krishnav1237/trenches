package main

import (
	"database/sql/driver"
	"encoding/json"
	"fmt"

	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"

	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
)

type JSONB map[string]any

func (j *JSONB) Scan(src interface{}) error {
	if src == nil {
		*j = nil
		return nil
	}
	switch data := src.(type) {

	case []byte:
		return json.Unmarshal(data, j)
	case string:
		return json.Unmarshal([]byte(data), j)

	default:
		return nil
	}
}

func (j JSONB) Value() (driver.Value, error) {
	if j == nil {
		return nil, nil
	}
	return json.Marshal(j)
}

type Tweet struct {
	ID       int    `db:"id" json:"id"`
	AgentID  string `db:"agent_id" json:"agent_id"`
	Content  string `db:"content" json:"content"`
	ThreadID *int   `db:"thread_id" json:"thread_id,omitempty"`
	Likes    int    `db:"likes" json:"likes"`
	Retweets int    `db:"retweets" json:"retweets"`
}

type Profile struct {
	ID       int    `db:"id" json:"id"`
	Username string `db:"username" json:"username"`
	Avatar   string `db:"avatar" json:"avatar"`
	Metadata JSONB  `db:"metadata" json:"metadata"`
}

type WalletSnapshot struct {
	ID            int       `db:"id" json:"id"`
	WalletAddress string    `db:"wallet_address" json:"wallet_address"`
	Balance       float64   `db:"balance" json:"balance"`
	BlockNumber   int64     `db:"block_number" json:"block_number"`
	Timestamp     time.Time `db:"timestamp" json:"timestamp"`
}

type NewsItem struct {
	Source string `json:"source"`
	Title  string `json:"title"`
	URL    string `json:"url"`
}

type MarketData struct {
	Prices     map[string]float64   `json:"prices"`
	Liquidity  []Pool               `json:"liquidity"`
	OrderBooks map[string]OrderBook `json:"order_books"`
}

type Pool struct {
	Symbol string  `json:"symbol"`
	TVL    float64 `json:"tvl_usd"`
	APY    float64 `json:"apy"`
	URL    string  `json:"url"`
}

type OrderBook struct {
	Bids [][]float64 `json:"bids"`
	Asks [][]float64 `json:"asks"`
}

var db *sqlx.DB
var wsHub *Hub

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow all origins for development
	},
}

func GetMarketData(c *gin.Context) {
	data := MarketData{
		Prices: map[string]float64{"BTC": 67000, "ETH": 3500},
		Liquidity: []Pool{
			{Symbol: "USDC-WETH", TVL: 92884538, APY: 18.79, URL: "https://dexscreener.com/"},
		},
		OrderBooks: map[string]OrderBook{},
	}
	c.JSON(http.StatusOK, data)
}

func logEvent(event any) {
	wrapped := map[string]any{
		"timestamp": time.Now().UTC().Format(time.RFC3339),
		"event":     event,
	}

	log.Println("Logging event:", wrapped)

	file, err := os.OpenFile("events.jsonl", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Println("Failed to open events log:", err)
		return
	}
	defer file.Close()

	bytes, _ := json.Marshal(wrapped)
	file.Write(bytes)
	file.Write([]byte("\n"))
}

func GetNews(c *gin.Context) {
	limit := 20
	if v := c.Query("limit"); v != "" {
		if n, err := strconv.Atoi(v); err == nil && n > 0 && n <= 200 {
			limit = n
		}
	}

	var news []NewsItem
	err := db.Select(&news, `
        SELECT id, source, title, url, timestamp
        FROM news
        ORDER BY timestamp DESC
        LIMIT $1
    `, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, news)
}

func PostNews(c *gin.Context) {
	var items []NewsItem
	if err := c.ShouldBindJSON(&items); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	tx, err := db.Beginx()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to start tx"})
		return
	}
	defer tx.Rollback()

	stmt, err := tx.Preparex(`INSERT INTO news (source, title, url) 
                              VALUES ($1, $2, $3) 
                              ON CONFLICT (url) DO NOTHING`)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to prepare stmt"})
		return
	}
	defer stmt.Close()

	inserted := 0
	for _, it := range items {
		if _, err := stmt.Exec(it.Source, it.Title, it.URL); err == nil {
			inserted++
		}
	}

	if err := tx.Commit(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to commit tx"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"status": "ok", "inserted": inserted, "received": len(items)})
}

func main() {
	var err error
	db, err = sqlx.Connect("postgres", "host=postgres port=5432 user=trenches password=secret dbname=trenches sslmode=disable")
	if err != nil {
		log.Fatalln("DB connection error:", err)
	}
	InitRedis()

	schema := `
	CREATE TABLE IF NOT EXISTS tweets (
		id SERIAL PRIMARY KEY,
		agent_id TEXT NOT NULL,
		content TEXT NOT NULL,
		thread_id INT,
		likes INT DEFAULT 0,
		retweets INT DEFAULT 0
	);

	CREATE TABLE IF NOT EXISTS profiles (
		id SERIAL PRIMARY KEY,
		username TEXT NOT NULL,
		avatar TEXT,
		metadata JSONB
	);

	CREATE TABLE IF NOT EXISTS wallet_snapshots (
		id SERIAL PRIMARY KEY,
		wallet_address TEXT NOT NULL,
		balance NUMERIC,
		block_number BIGINT,
		timestamp TIMESTAMP DEFAULT NOW()
	);

	CREATE TABLE IF NOT EXISTS follows (
		id SERIAL PRIMARY KEY,
		follower_id TEXT NOT NULL,
		following_id TEXT NOT NULL,
		created_at TIMESTAMP DEFAULT NOW(),
		UNIQUE(follower_id, following_id)
	);

	CREATE INDEX IF NOT EXISTS idx_follows_follower ON follows(follower_id);
	CREATE INDEX IF NOT EXISTS idx_follows_following ON follows(following_id);

	CREATE TABLE IF NOT EXISTS news (
		id SERIAL PRIMARY KEY,
		source TEXT NOT NULL,
		title TEXT NOT NULL,
		url TEXT NOT NULL UNIQUE,
		timestamp TIMESTAMP DEFAULT NOW()
	);

	CREATE INDEX IF NOT EXISTS idx_news_timestamp ON news(timestamp DESC);

	CREATE TABLE IF NOT EXISTS users (
		id SERIAL PRIMARY KEY,
		username TEXT NOT NULL UNIQUE,
		email TEXT NOT NULL UNIQUE,
		password_hash TEXT NOT NULL,
		display_name TEXT NOT NULL,
		avatar TEXT,
		created_at TIMESTAMP DEFAULT NOW()
	);

	CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
	CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

	CREATE TABLE IF NOT EXISTS sessions (
		id SERIAL PRIMARY KEY,
		user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		token TEXT NOT NULL UNIQUE,
		expires_at TIMESTAMP NOT NULL,
		created_at TIMESTAMP DEFAULT NOW()
	);

	CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
	CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);

	CREATE TABLE IF NOT EXISTS notifications (
		id SERIAL PRIMARY KEY,
		user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		actor_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		type TEXT NOT NULL,
		tweet_id INT REFERENCES tweets(id) ON DELETE CASCADE,
		read BOOLEAN DEFAULT FALSE,
		created_at TIMESTAMP DEFAULT NOW()
	);

	CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
	CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(user_id, read);
	CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);

	CREATE TABLE IF NOT EXISTS bookmarks (
		id SERIAL PRIMARY KEY,
		user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		tweet_id INT NOT NULL REFERENCES tweets(id) ON DELETE CASCADE,
		created_at TIMESTAMP DEFAULT NOW(),
		UNIQUE(user_id, tweet_id)
	);

	CREATE INDEX IF NOT EXISTS idx_bookmarks_user_id ON bookmarks(user_id);
	CREATE INDEX IF NOT EXISTS idx_bookmarks_tweet_id ON bookmarks(tweet_id);
	CREATE INDEX IF NOT EXISTS idx_bookmarks_created_at ON bookmarks(created_at DESC);

	CREATE TABLE IF NOT EXISTS conversations (
		id SERIAL PRIMARY KEY,
		user1_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		user2_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		last_message_at TIMESTAMP DEFAULT NOW(),
		created_at TIMESTAMP DEFAULT NOW(),
		UNIQUE(user1_id, user2_id),
		CHECK (user1_id < user2_id)
	);

	CREATE INDEX IF NOT EXISTS idx_conversations_user1 ON conversations(user1_id);
	CREATE INDEX IF NOT EXISTS idx_conversations_user2 ON conversations(user2_id);
	CREATE INDEX IF NOT EXISTS idx_conversations_last_message ON conversations(last_message_at DESC);

	CREATE TABLE IF NOT EXISTS messages (
		id SERIAL PRIMARY KEY,
		conversation_id INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
		sender_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		content TEXT NOT NULL,
		read BOOLEAN DEFAULT FALSE,
		created_at TIMESTAMP DEFAULT NOW()
	);

	CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
	CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
	CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);

	CREATE TABLE IF NOT EXISTS hashtags (
		id SERIAL PRIMARY KEY,
		tag TEXT NOT NULL UNIQUE,
		count INT DEFAULT 0,
		last_used TIMESTAMP DEFAULT NOW()
	);

	CREATE INDEX IF NOT EXISTS idx_hashtags_tag ON hashtags(tag);
	CREATE INDEX IF NOT EXISTS idx_hashtags_count ON hashtags(count DESC);

	CREATE TABLE IF NOT EXISTS tweet_hashtags (
		id SERIAL PRIMARY KEY,
		tweet_id INT NOT NULL REFERENCES tweets(id) ON DELETE CASCADE,
		hashtag_id INT NOT NULL REFERENCES hashtags(id) ON DELETE CASCADE,
		UNIQUE(tweet_id, hashtag_id)
	);

	CREATE INDEX IF NOT EXISTS idx_tweet_hashtags_tweet ON tweet_hashtags(tweet_id);
	CREATE INDEX IF NOT EXISTS idx_tweet_hashtags_hashtag ON tweet_hashtags(hashtag_id);

	CREATE TABLE IF NOT EXISTS polls (
		id SERIAL PRIMARY KEY,
		tweet_id INT NOT NULL UNIQUE REFERENCES tweets(id) ON DELETE CASCADE,
		duration_hours INT NOT NULL DEFAULT 24,
		ends_at TIMESTAMP NOT NULL,
		created_at TIMESTAMP DEFAULT NOW()
	);

	CREATE TABLE IF NOT EXISTS poll_options (
		id SERIAL PRIMARY KEY,
		poll_id INT NOT NULL REFERENCES polls(id) ON DELETE CASCADE,
		option_text TEXT NOT NULL,
		vote_count INT DEFAULT 0,
		option_index INT NOT NULL
	);

	CREATE INDEX IF NOT EXISTS idx_poll_options_poll ON poll_options(poll_id);

	CREATE TABLE IF NOT EXISTS poll_votes (
		id SERIAL PRIMARY KEY,
		poll_id INT NOT NULL REFERENCES polls(id) ON DELETE CASCADE,
		user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		option_id INT NOT NULL REFERENCES poll_options(id) ON DELETE CASCADE,
		created_at TIMESTAMP DEFAULT NOW(),
		UNIQUE(poll_id, user_id)
	);

	CREATE INDEX IF NOT EXISTS idx_poll_votes_poll ON poll_votes(poll_id);
	CREATE INDEX IF NOT EXISTS idx_poll_votes_user ON poll_votes(user_id);

	`

	// Add additional columns to tables if they don't exist
	db.Exec(`ALTER TABLE users ADD COLUMN IF NOT EXISTS pinned_tweet_id INT REFERENCES tweets(id) ON DELETE SET NULL`)
	db.Exec(`ALTER TABLE tweets ADD COLUMN IF NOT EXISTS quoted_tweet_id INT REFERENCES tweets(id) ON DELETE SET NULL`)

	db.MustExec(schema)

	r := gin.Default()

	// Initialize WebSocket hub
	wsHub = NewHub()
	go wsHub.Run()
	log.Println("✅ WebSocket hub started")

	// Enable CORS for frontend integration
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:3001", "http://localhost:3000", "http://localhost:5173"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
	}))

	// Ping
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "pong"})
	})

	// 🔐 Authentication Endpoints
	r.POST("/auth/signup", Signup)
	r.POST("/auth/login", Login)
	r.POST("/auth/logout", Logout)
	r.GET("/auth/me", AuthMiddleware(), GetMe)

	// 🔔 Notification Endpoints
	r.GET("/notifications", AuthMiddleware(), GetUserNotifications)
	r.GET("/notifications/unread-count", AuthMiddleware(), GetUnreadCount)
	r.POST("/notifications/:id/read", AuthMiddleware(), MarkNotificationAsRead)
	r.POST("/notifications/read-all", AuthMiddleware(), MarkAllAsRead)

	// 🔖 Bookmark Endpoints
	r.POST("/tweets/:id/bookmark", AuthMiddleware(), AddBookmark)
	r.DELETE("/tweets/:id/bookmark", AuthMiddleware(), RemoveBookmark)
	r.GET("/bookmarks", AuthMiddleware(), GetBookmarks)
	r.GET("/tweets/:id/bookmarked", AuthMiddleware(), CheckBookmark)

	// 📌 Pinned Tweet Endpoints
	r.POST("/tweets/:id/pin", AuthMiddleware(), PinTweet)
	r.POST("/tweets/unpin", AuthMiddleware(), UnpinTweet)
	r.GET("/users/:id/pinned-tweet", GetPinnedTweet)

	// 💬 Direct Messages Endpoints
	r.POST("/messages/send", AuthMiddleware(), SendMessage)
	r.GET("/messages/conversations", AuthMiddleware(), GetConversations)
	r.GET("/messages/conversation/:user_id", AuthMiddleware(), GetMessages)
	r.GET("/messages/unread-count", AuthMiddleware(), GetUnreadMessageCount)

	// #️⃣ Hashtag Endpoints
	r.GET("/hashtags/trending", GetTrendingHashtags)
	r.GET("/hashtags/:tag/tweets", GetTweetsByHashtag)

	// 📊 Poll Endpoints
	r.POST("/polls/create", AuthMiddleware(), CreatePoll)
	r.GET("/polls/tweet/:id", GetPoll)
	r.POST("/polls/:id/vote", AuthMiddleware(), VotePoll)

	// WebSocket endpoint for real-time updates
	r.GET("/ws", func(c *gin.Context) {
		conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
		if err != nil {
			log.Println("WebSocket upgrade error:", err)
			return
		}

		client := &Client{
			hub:  wsHub,
			conn: conn,
			send: make(chan []byte, 256),
		}

		wsHub.register <- client

		// Start client goroutines
		go client.writePump()
		go client.readPump()
	})

	// Create Tweet
	r.POST("/tweets", func(c *gin.Context) {
		var tweet Tweet
		if err := c.ShouldBindJSON(&tweet); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		err := db.QueryRowx(
			`INSERT INTO tweets (agent_id, content, thread_id)
			 VALUES ($1, $2, $3) RETURNING id`,
			tweet.AgentID, tweet.Content, tweet.ThreadID,
		).Scan(&tweet.ID)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// Process hashtags and mentions
		go func() {
			if err := ProcessHashtags(tweet.ID, tweet.Content); err != nil {
				log.Println("Failed to process hashtags:", err)
			}
			if err := ProcessMentions(tweet.ID, tweet.Content); err != nil {
				log.Println("Failed to process mentions:", err)
			}
		}()

		// cached Tweet
		tweetJSON, _ := json.Marshal(tweet)
		err = RedisClient.Set(ctx, fmt.Sprintf("tweet:%d", tweet.ID), tweetJSON, 5*time.Minute).Err()
		if err != nil {
			log.Println("Failed to cache tweet:", err)
		}
		logEvent(tweet)

		// Broadcast new tweet to all WebSocket clients
		wsHub.BroadcastTweet(tweet)

		c.JSON(http.StatusCreated, gin.H{"status": "tweet posted", "tweet": tweet})

		err = RedisClient.Set(ctx, fmt.Sprintf("tweet:%d", tweet.ID), tweetJSON, 5*time.Minute).Err()
		RedisClient.Del(ctx, "tweets:recent")

	})

	r.GET("/tweets", func(c *gin.Context) {
		cacheKey := "tweets:recent"

		// Check Redis first
		val, err := RedisClient.Get(ctx, cacheKey).Result()
		if err == nil {
			var tweets []Tweet
			if err := json.Unmarshal([]byte(val), &tweets); err == nil {
				log.Println("⚡ Serving tweets from Redis cache")
				c.JSON(http.StatusOK, tweets)
				return
			}
		}

		// If cache miss → hit DB
		var tweets []Tweet
		err = db.Select(&tweets, "SELECT * FROM tweets ORDER BY id DESC LIMIT 20")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// Save to Redis for next time
		bytes, _ := json.Marshal(tweets)
		RedisClient.Set(ctx, cacheKey, bytes, 1*time.Minute)

		// Also store single tweets individually (optional)
		for _, tweet := range tweets {
			CacheTweet(tweet)
		}

		c.JSON(http.StatusOK, tweets)
	})

	// Like
	r.POST("/tweets/:id/likes", func(c *gin.Context) {
		id := c.Param("id")
		_, err := db.Exec(`UPDATE tweets SET likes = COALESCE(likes, 0) + 1 WHERE id=$1`, id)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		logEvent(map[string]any{"action": "like", "tweet_id": id})
		c.JSON(http.StatusOK, gin.H{"status": "tweet liked"})
		RedisClient.Del(ctx, fmt.Sprintf("tweet:%s", id))
	})

	// 👍 Get likes count for a tweet
	r.GET("/tweets/:id/likes", func(c *gin.Context) {
		id := c.Param("id")
		var likes int
		err := db.Get(&likes, "SELECT likes FROM tweets WHERE id=$1", id)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Tweet not found"})
			return
		}
		c.JSON(http.StatusOK, gin.H{"likes": likes})
	})

	// Retweet
	r.POST("/tweets/:id/retweets", func(c *gin.Context) {
		id := c.Param("id")
		_, err := db.Exec(`UPDATE tweets SET retweets = COALESCE(retweets, 0) + 1 WHERE id=$1`, id)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		logEvent(map[string]any{"action": "retweet", "tweet_id": id})
		c.JSON(http.StatusOK, gin.H{"status": "tweet retweeted"})
		RedisClient.Del(ctx, fmt.Sprintf("tweet:%s", id))

	})

	// 🔁 Get retweets count for a tweet
	r.GET("/tweets/:id/retweets", func(c *gin.Context) {
		id := c.Param("id")
		var retweets int
		err := db.Get(&retweets, "SELECT retweets FROM tweets WHERE id=$1", id)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Tweet not found"})
			return
		}
		c.JSON(http.StatusOK, gin.H{"retweets": retweets})
	})

	// Reply
	r.POST("/tweets/:id/reply", func(c *gin.Context) {
		parentID := c.Param("id")
		var tweet Tweet
		if err := c.ShouldBindJSON(&tweet); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		err := db.QueryRowx(
			`INSERT INTO tweets (agent_id, content, thread_id)
			 VALUES ($1, $2, $3) RETURNING id`,
			tweet.AgentID, tweet.Content, parentID,
		).Scan(&tweet.ID)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		logEvent(tweet)

		// Broadcast reply to WebSocket clients
		wsHub.BroadcastTweet(tweet)

		c.JSON(http.StatusCreated, gin.H{"status": "reply posted", "tweet": tweet})
	})

	// 💬 Conversation & Threading Endpoints

	// Get full conversation thread
	r.GET("/tweets/:id/thread", func(c *gin.Context) {
		tweetID := c.Param("id")

		// Get the original tweet
		var originalTweet Tweet
		err := db.Get(&originalTweet, "SELECT id, agent_id, content, thread_id, likes, retweets FROM tweets WHERE id=$1", tweetID)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Tweet not found"})
			return
		}

		// Get all replies in the thread
		var replies []Tweet
		db.Select(&replies, `
			SELECT id, agent_id, content, thread_id, likes, retweets
			FROM tweets
			WHERE thread_id = $1
			ORDER BY id ASC
		`, tweetID)

		c.JSON(http.StatusOK, gin.H{
			"original_tweet": originalTweet,
			"replies":        replies,
			"reply_count":    len(replies),
		})
	})

	// Get all replies to a tweet
	r.GET("/tweets/:id/replies", func(c *gin.Context) {
		tweetID := c.Param("id")
		limitStr := c.DefaultQuery("limit", "50")
		limit, _ := strconv.Atoi(limitStr)

		var replies []Tweet
		err := db.Select(&replies, `
			SELECT id, agent_id, content, thread_id, likes, retweets
			FROM tweets
			WHERE thread_id = $1
			ORDER BY id DESC
			LIMIT $2
		`, tweetID, limit)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"tweet_id": tweetID,
			"replies":  replies,
			"count":    len(replies),
		})
	})

	// Get active conversations (threads with multiple replies)
	r.GET("/conversations", func(c *gin.Context) {
		limitStr := c.DefaultQuery("limit", "20")
		limit, _ := strconv.Atoi(limitStr)

		type Conversation struct {
			TweetID      int    `db:"tweet_id" json:"tweet_id"`
			AgentID      string `db:"agent_id" json:"agent_id"`
			Content      string `db:"content" json:"content"`
			ReplyCount   int    `db:"reply_count" json:"reply_count"`
			LastReplyAt  string `db:"last_reply_at" json:"last_reply_at"`
			TotalLikes   int    `db:"total_likes" json:"total_likes"`
		}

		var conversations []Conversation
		err := db.Select(&conversations, `
			SELECT
				t.id as tweet_id,
				t.agent_id,
				t.content,
				COUNT(r.id) as reply_count,
				MAX(r.id)::text as last_reply_at,
				COALESCE(SUM(r.likes), 0) as total_likes
			FROM tweets t
			LEFT JOIN tweets r ON r.thread_id = t.id
			WHERE t.thread_id IS NULL
			GROUP BY t.id, t.agent_id, t.content
			HAVING COUNT(r.id) > 0
			ORDER BY reply_count DESC, last_reply_at DESC
			LIMIT $1
		`, limit)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"conversations": conversations,
			"count":         len(conversations),
		})
	})

	// Get conversation participants
	r.GET("/tweets/:id/participants", func(c *gin.Context) {
		tweetID := c.Param("id")

		var participants []string
		err := db.Select(&participants, `
			SELECT DISTINCT agent_id
			FROM tweets
			WHERE id = $1 OR thread_id = $1
			ORDER BY agent_id
		`, tweetID)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"tweet_id":      tweetID,
			"participants":  participants,
			"count":         len(participants),
		})
	})

	// Get conversation stats
	r.GET("/tweets/:id/conversation-stats", func(c *gin.Context) {
		tweetID := c.Param("id")

		var stats struct {
			TotalReplies   int     `db:"total_replies"`
			UniqueAgents   int     `db:"unique_agents"`
			TotalLikes     int     `db:"total_likes"`
			TotalRetweets  int     `db:"total_retweets"`
			AvgEngagement  float64 `db:"avg_engagement"`
		}

		err := db.Get(&stats, `
			SELECT
				COUNT(*) as total_replies,
				COUNT(DISTINCT agent_id) as unique_agents,
				COALESCE(SUM(likes), 0) as total_likes,
				COALESCE(SUM(retweets), 0) as total_retweets,
				COALESCE(AVG(likes + retweets), 0) as avg_engagement
			FROM tweets
			WHERE thread_id = $1
		`, tweetID)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"tweet_id":        tweetID,
			"total_replies":   stats.TotalReplies,
			"unique_agents":   stats.UniqueAgents,
			"total_likes":     stats.TotalLikes,
			"total_retweets":  stats.TotalRetweets,
			"avg_engagement":  stats.AvgEngagement,
		})
	})

	// --- ✅ PROFILES CRUD ---

	// Create
	r.POST("/profiles", func(c *gin.Context) {
		var p Profile
		if err := c.ShouldBindJSON(&p); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		metadataBytes, _ := json.Marshal(p.Metadata)

		err := db.QueryRowx(
			`INSERT INTO profiles (username, avatar, metadata) VALUES ($1, $2, $3) RETURNING id`,
			p.Username, p.Avatar, metadataBytes,
		).Scan(&p.ID)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		logEvent(p)
		c.JSON(http.StatusCreated, gin.H{"status": "profile created", "profile": p})
	})

	// Get all
	r.GET("/profiles", func(c *gin.Context) {
		var profiles []Profile
		err := db.Select(&profiles, "SELECT * FROM profiles")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, profiles)
	})

	// Get one
	r.GET("/profiles/:id", func(c *gin.Context) {
		id := c.Param("id")
		var p Profile
		err := db.Get(&p, "SELECT * FROM profiles WHERE id=$1", id)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Profile not found"})
			return
		}
		c.JSON(http.StatusOK, p)
	})
	// GET /experiments/:id/export
	r.GET("/experiments/:id/export", func(c *gin.Context) {

		filePath := "events.jsonl"

		// Check if file exists
		if _, err := os.Stat(filePath); os.IsNotExist(err) {
			c.JSON(http.StatusNotFound, gin.H{"error": "No events log found"})
			return
		}

		// Set headers for download
		c.Header("Content-Disposition", "attachment; filename=events.jsonl")
		c.Header("Content-Type", "application/json")

		c.File(filePath)
	})

	// Update
	r.PUT("/profiles/:id", func(c *gin.Context) {
		id := c.Param("id")
		var p Profile
		if err := c.ShouldBindJSON(&p); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		metadataBytes, _ := json.Marshal(p.Metadata)

		_, err := db.Exec(
			`UPDATE profiles SET username=$1, avatar=$2, metadata=$3 WHERE id=$4`,
			p.Username, p.Avatar, metadataBytes, id,
		)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		logEvent(map[string]any{"action": "profile_updated", "profile_id": id})
		c.JSON(http.StatusOK, gin.H{"status": "profile updated"})
	})

	// Delete
	r.DELETE("/profiles/:id", func(c *gin.Context) {
		id := c.Param("id")
		_, err := db.Exec(`DELETE FROM profiles WHERE id=$1`, id)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		logEvent(map[string]any{"action": "profile_deleted", "profile_id": id})
		c.JSON(http.StatusOK, gin.H{"status": "profile deleted"})
	})

	// 🧾 Get stats for a specific tweet
	r.GET("/tweets/:id/stats", func(c *gin.Context) {
		id := c.Param("id")

		var stats struct {
			Likes    int `db:"likes" json:"likes"`
			Retweets int `db:"retweets" json:"retweets"`
			Replies  int `json:"replies"`
		}

		// Get likes and retweets
		err := db.Get(&stats, "SELECT likes, retweets FROM tweets WHERE id=$1", id)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Tweet not found"})
			return
		}

		// Count replies to this tweet
		err = db.Get(&stats.Replies, "SELECT COUNT(*) FROM tweets WHERE thread_id=$1", id)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, stats)
	})

	// 🏆 Get all tweets with stats, ordered by likes + retweets
	r.GET("/tweets/stats", func(c *gin.Context) {
		var tweets []Tweet
		err := db.Select(&tweets, "SELECT * FROM tweets ORDER BY (likes + retweets) DESC")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, tweets)
	})

	// 📁 Export all logged events (for analysis)
	r.GET("/events/export", func(c *gin.Context) {
		filePath := "events.jsonl"

		// Check if the file exists
		if _, err := os.Stat(filePath); os.IsNotExist(err) {
			c.JSON(http.StatusNotFound, gin.H{"error": "No events log found"})
			return
		}

		c.Header("Content-Disposition", "attachment; filename=events.jsonl")
		c.Header("Content-Type", "application/json")
		c.File(filePath)
	})

	// 📰 Get timeline (latest tweets, limited)
	r.GET("/timeline", func(c *gin.Context) {
		limit := 20 // default
		if l := c.Query("limit"); l != "" {
			if parsed, err := strconv.Atoi(l); err == nil {
				limit = parsed
			}
		}

		var tweets []Tweet
		err := db.Select(&tweets, "SELECT * FROM tweets ORDER BY id DESC LIMIT $1", limit)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, tweets)
	})

	// GET /stats — return total likes & retweets grouped by agent
	r.GET("/stats", func(c *gin.Context) {
		var stats []struct {
			AgentID       string `db:"agent_id" json:"agent_id"`
			TotalLikes    int    `db:"total_likes" json:"total_likes"`
			TotalRetweets int    `db:"total_retweets" json:"total_retweets"`
		}

		query := `
		SELECT 
			agent_id, 
			COALESCE(SUM(likes), 0) AS total_likes,
			COALESCE(SUM(retweets), 0) AS total_retweets
		FROM tweets
		GROUP BY agent_id
	`

		err := db.Select(&stats, query)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, stats)
	})

	// Metrics Endpoint
	r.GET("/metrics", func(c *gin.Context) {
		var totalTweets int
		var totalLikes int
		var totalRetweets int
		tweetsPerAgent := make(map[string]int)

		// Total tweets
		err := db.Get(&totalTweets, "SELECT COUNT(*) FROM tweets")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count tweets"})
			return
		}

		// Total likes
		err = db.Get(&totalLikes, "SELECT COALESCE(SUM(likes), 0) FROM tweets")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to sum likes"})
			return
		}

		// Total retweets
		err = db.Get(&totalRetweets, "SELECT COALESCE(SUM(retweets), 0) FROM tweets")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to sum retweets"})
			return
		}

		// Tweets per agent
		rows, err := db.Queryx(`SELECT agent_id, COUNT(*) as count FROM tweets GROUP BY agent_id`)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to group tweets"})
			return
		}
		defer rows.Close()

		for rows.Next() {
			var agentID string
			var count int
			if err := rows.Scan(&agentID, &count); err != nil {
				continue
			}
			tweetsPerAgent[agentID] = count
		}

		c.JSON(http.StatusOK, gin.H{
			"total_tweets":     totalTweets,
			"total_likes":      totalLikes,
			"total_retweets":   totalRetweets,
			"tweets_per_agent": tweetsPerAgent,
		})
	})

	// --- WALLET SNAPSHOTS ---
	r.POST("/wallet_snapshots", func(c *gin.Context) {
		var ws WalletSnapshot
		if err := c.ShouldBindJSON(&ws); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		_, err := db.Exec(`INSERT INTO wallet_snapshots (wallet_address, balance, block_number) VALUES ($1, $2, $3)`,
			ws.WalletAddress, ws.Balance, ws.BlockNumber,
		)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": "snapshot saved"})
	})

	r.GET("/wallet_snapshots/:wallet", func(c *gin.Context) {
		wallet := c.Param("wallet")
		var snapshots []WalletSnapshot
		err := db.Select(&snapshots, "SELECT * FROM wallet_snapshots WHERE wallet_address=$1 ORDER BY timestamp DESC", wallet)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		if snapshots == nil {
			snapshots = []WalletSnapshot{}
		}
		c.JSON(http.StatusOK, snapshots)
	})

	// Get all tracked wallets
	r.GET("/wallets", func(c *gin.Context) {
		var wallets []struct {
			WalletAddress  string  `db:"wallet_address" json:"wallet_address"`
			LatestBalance  float64 `db:"latest_balance" json:"latest_balance"`
			SnapshotCount  int     `db:"snapshot_count" json:"snapshot_count"`
			LastUpdate     string  `db:"last_update" json:"last_update"`
		}

		err := db.Select(&wallets, `
			SELECT
				wallet_address,
				MAX(balance) as latest_balance,
				COUNT(*) as snapshot_count,
				MAX(timestamp)::text as last_update
			FROM wallet_snapshots
			GROUP BY wallet_address
			ORDER BY latest_balance DESC
		`)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"wallets": wallets,
			"count":   len(wallets),
		})
	})

	// Get wallet analytics
	r.GET("/wallets/:address/analytics", func(c *gin.Context) {
		address := c.Param("address")

		// Get latest balance and first balance
		var analytics struct {
			LatestBalance float64 `db:"latest_balance"`
			FirstBalance  float64 `db:"first_balance"`
			HighestBalance float64 `db:"highest_balance"`
			LowestBalance  float64 `db:"lowest_balance"`
			SnapshotCount  int     `db:"snapshot_count"`
		}

		err := db.Get(&analytics, `
			SELECT
				MAX(balance) as latest_balance,
				MIN(balance) as first_balance,
				MAX(balance) as highest_balance,
				MIN(balance) as lowest_balance,
				COUNT(*) as snapshot_count
			FROM wallet_snapshots
			WHERE wallet_address = $1
		`, address)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		balanceChange := analytics.LatestBalance - analytics.FirstBalance
		percentChange := 0.0
		if analytics.FirstBalance > 0 {
			percentChange = (balanceChange / analytics.FirstBalance) * 100
		}

		// Get recent snapshots for chart
		var recentSnapshots []WalletSnapshot
		db.Select(&recentSnapshots, `
			SELECT * FROM wallet_snapshots
			WHERE wallet_address = $1
			ORDER BY timestamp DESC
			LIMIT 30
		`, address)

		c.JSON(http.StatusOK, gin.H{
			"wallet_address":   address,
			"latest_balance":   analytics.LatestBalance,
			"first_balance":    analytics.FirstBalance,
			"highest_balance":  analytics.HighestBalance,
			"lowest_balance":   analytics.LowestBalance,
			"balance_change":   balanceChange,
			"percent_change":   percentChange,
			"snapshot_count":   analytics.SnapshotCount,
			"recent_snapshots": recentSnapshots,
		})
	})

	// Wallet leaderboard
	r.GET("/wallets/leaderboard", func(c *gin.Context) {
		limitStr := c.DefaultQuery("limit", "10")
		limit, _ := strconv.Atoi(limitStr)

		type WalletRank struct {
			Rank          int     `json:"rank"`
			WalletAddress string  `db:"wallet_address" json:"wallet_address"`
			Balance       float64 `db:"balance" json:"balance"`
			SnapshotCount int     `db:"snapshot_count" json:"snapshot_count"`
		}

		var leaderboard []WalletRank
		err := db.Select(&leaderboard, `
			SELECT
				wallet_address,
				MAX(balance) as balance,
				COUNT(*) as snapshot_count
			FROM wallet_snapshots
			GROUP BY wallet_address
			ORDER BY balance DESC
			LIMIT $1
		`, limit)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// Add rank numbers
		for i := range leaderboard {
			leaderboard[i].Rank = i + 1
		}

		c.JSON(http.StatusOK, gin.H{
			"leaderboard": leaderboard,
			"count":       len(leaderboard),
		})
	})

	// 📰 Get all news
	r.GET("/news", func(c *gin.Context) {
		limit := 20
		if v := c.Query("limit"); v != "" {
			if n, err := strconv.Atoi(v); err == nil && n > 0 && n <= 200 {
				limit = n
			}
		}

		type NewsItemWithTimestamp struct {
			ID        int       `db:"id" json:"id"`
			Source    string    `db:"source" json:"source"`
			Title     string    `db:"title" json:"title"`
			URL       string    `db:"url" json:"url"`
			Timestamp time.Time `db:"timestamp" json:"timestamp"`
		}

		var news []NewsItemWithTimestamp
		err := db.Select(&news, `
        SELECT id, source, title, url, timestamp
        FROM news
        ORDER BY timestamp DESC
        LIMIT $1
    `, limit)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		if news == nil {
			news = []NewsItemWithTimestamp{}
		}

		c.JSON(http.StatusOK, gin.H{
			"news":  news,
			"count": len(news),
		})
	})

	// 📰 Insert news batch (Python → Go)
	r.POST("/news", func(c *gin.Context) {
		var items []NewsItem
		if err := c.ShouldBindJSON(&items); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		tx, err := db.Beginx()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to start transaction"})
			return
		}
		defer tx.Rollback()

		stmt, err := tx.Preparex(`INSERT INTO news (source, title, url)
                              VALUES ($1, $2, $3)
                              ON CONFLICT (url) DO NOTHING`)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to prepare statement"})
			return
		}
		defer stmt.Close()

		inserted := 0
		for _, it := range items {
			if _, err := stmt.Exec(it.Source, it.Title, it.URL); err == nil {
				inserted++
			}
		}

		if err := tx.Commit(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to commit transaction"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"status":   "ok",
			"inserted": inserted,
			"received": len(items),
		})
	})

	// 🔍 Advanced Tweet Search
	r.GET("/search/tweets", func(c *gin.Context) {
		agent := c.Query("agent")        // Filter by agent_id
		keyword := c.Query("keyword")    // Search in content
		token := c.Query("token")        // Filter by token mention
		minLikes := c.Query("min_likes") // Minimum likes
		limitStr := c.DefaultQuery("limit", "50")

		limit, _ := strconv.Atoi(limitStr)
		if limit > 100 {
			limit = 100
		}

		query := "SELECT id, agent_id, content, thread_id, likes, retweets FROM tweets WHERE 1=1"
		args := []interface{}{}
		argPos := 1

		// Add filters
		if agent != "" {
			query += fmt.Sprintf(" AND agent_id = $%d", argPos)
			args = append(args, agent)
			argPos++
		}

		if keyword != "" {
			query += fmt.Sprintf(" AND content ILIKE $%d", argPos)
			args = append(args, "%"+keyword+"%")
			argPos++
		}

		if token != "" {
			query += fmt.Sprintf(" AND (content ILIKE $%d OR content ILIKE $%d)", argPos, argPos+1)
			args = append(args, "%"+token+"%", "%$"+token+"%")
			argPos += 2
		}

		if minLikes != "" {
			minLikesInt, _ := strconv.Atoi(minLikes)
			query += fmt.Sprintf(" AND likes >= $%d", argPos)
			args = append(args, minLikesInt)
			argPos++
		}

		query += fmt.Sprintf(" ORDER BY id DESC LIMIT $%d", argPos)
		args = append(args, limit)

		var tweets []Tweet
		if err := db.Select(&tweets, query, args...); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"tweets": tweets,
			"count":  len(tweets),
		})
	})

	// 🔥 Trending Tokens Endpoint
	r.GET("/trending", func(c *gin.Context) {
		limitStr := c.DefaultQuery("limit", "10")
		limit, _ := strconv.Atoi(limitStr)

		// Get top mentioned tokens from recent tweets (last 1000 tweets)
		type TokenCount struct {
			Token   string `db:"token"`
			Count   int    `db:"count"`
			AvgLikes float64 `db:"avg_likes"`
		}

		// Common crypto tokens to search for
		tokens := []string{"BTC", "ETH", "SOL", "ADA", "DOT", "DOGE", "SHIB", "PEPE", "XRP", "BNB", "AVAX", "MATIC"}

		var trending []TokenCount
		for _, token := range tokens {
			var count TokenCount
			err := db.Get(&count, `
				SELECT
					$1 as token,
					COUNT(*) as count,
					COALESCE(AVG(likes), 0) as avg_likes
				FROM tweets
				WHERE content ILIKE $2 OR content ILIKE $3
				LIMIT 1
			`, token, "%"+token+"%", "%$"+token+"%")

			if err == nil && count.Count > 0 {
				trending = append(trending, count)
			}
		}

		// Sort by count desc
		for i := 0; i < len(trending); i++ {
			for j := i + 1; j < len(trending); j++ {
				if trending[j].Count > trending[i].Count {
					trending[i], trending[j] = trending[j], trending[i]
				}
			}
		}

		// Limit results
		if len(trending) > limit {
			trending = trending[:limit]
		}

		c.JSON(http.StatusOK, gin.H{
			"trending": trending,
			"count":    len(trending),
		})
	})

	// 📊 Agent Search
	r.GET("/search/agents", func(c *gin.Context) {
		query := c.Query("q")           // Search query
		limitStr := c.DefaultQuery("limit", "20")
		limit, _ := strconv.Atoi(limitStr)

		var profiles []Profile
		if query != "" {
			err := db.Select(&profiles, `
				SELECT id, username, avatar, metadata
				FROM profiles
				WHERE username ILIKE $1
				ORDER BY username
				LIMIT $2
			`, "%"+query+"%", limit)

			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
		} else {
			// Return all if no query
			err := db.Select(&profiles, "SELECT id, username, avatar, metadata FROM profiles ORDER BY username LIMIT $1", limit)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
		}

		c.JSON(http.StatusOK, gin.H{
			"agents": profiles,
			"count":  len(profiles),
		})
	})

	// 🎯 Top Agents (by engagement)
	r.GET("/agents/top", func(c *gin.Context) {
		limitStr := c.DefaultQuery("limit", "10")
		limit, _ := strconv.Atoi(limitStr)

		type AgentStats struct {
			AgentID      string  `db:"agent_id" json:"agent_id"`
			TotalTweets  int     `db:"total_tweets" json:"total_tweets"`
			TotalLikes   int     `db:"total_likes" json:"total_likes"`
			TotalRetweets int    `db:"total_retweets" json:"total_retweets"`
			AvgEngagement float64 `db:"avg_engagement" json:"avg_engagement"`
		}

		var topAgents []AgentStats
		err := db.Select(&topAgents, `
			SELECT
				agent_id,
				COUNT(*) as total_tweets,
				SUM(likes) as total_likes,
				SUM(retweets) as total_retweets,
				AVG(likes + retweets) as avg_engagement
			FROM tweets
			GROUP BY agent_id
			ORDER BY avg_engagement DESC
			LIMIT $1
		`, limit)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"top_agents": topAgents,
			"count":      len(topAgents),
		})
	})

	// 👥 Follow System Endpoints

	// Get detailed agent information
	r.GET("/agents/:id", func(c *gin.Context) {
		agentID := c.Param("id")

		// Get agent's tweet stats
		var stats struct {
			TotalTweets   int     `db:"total_tweets"`
			TotalLikes    int     `db:"total_likes"`
			TotalRetweets int     `db:"total_retweets"`
			AvgEngagement float64 `db:"avg_engagement"`
		}

		err := db.Get(&stats, `
			SELECT
				COUNT(*) as total_tweets,
				COALESCE(SUM(likes), 0) as total_likes,
				COALESCE(SUM(retweets), 0) as total_retweets,
				COALESCE(AVG(likes + retweets), 0) as avg_engagement
			FROM tweets
			WHERE agent_id = $1
		`, agentID)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// Get follower/following counts
		var followerCount int
		db.Get(&followerCount, "SELECT COUNT(*) FROM follows WHERE following_id = $1", agentID)

		var followingCount int
		db.Get(&followingCount, "SELECT COUNT(*) FROM follows WHERE follower_id = $1", agentID)

		// Get recent tweets
		var recentTweets []Tweet
		db.Select(&recentTweets, `
			SELECT id, agent_id, content, thread_id, likes, retweets
			FROM tweets
			WHERE agent_id = $1
			ORDER BY id DESC
			LIMIT 10
		`, agentID)

		c.JSON(http.StatusOK, gin.H{
			"agent_id":        agentID,
			"total_tweets":    stats.TotalTweets,
			"total_likes":     stats.TotalLikes,
			"total_retweets":  stats.TotalRetweets,
			"avg_engagement":  stats.AvgEngagement,
			"followers_count": followerCount,
			"following_count": followingCount,
			"recent_tweets":   recentTweets,
		})
	})

	// Follow an agent
	r.POST("/agents/:id/follow", func(c *gin.Context) {
		agentID := c.Param("id")
		var req struct {
			FollowerID string `json:"follower_id" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "follower_id is required"})
			return
		}

		// Prevent self-follow
		if req.FollowerID == agentID {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Cannot follow yourself"})
			return
		}

		_, err := db.Exec(`
			INSERT INTO follows (follower_id, following_id)
			VALUES ($1, $2)
			ON CONFLICT (follower_id, following_id) DO NOTHING
		`, req.FollowerID, agentID)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// Invalidate cache
		RedisClient.Del(ctx, fmt.Sprintf("followers:%s", agentID))
		RedisClient.Del(ctx, fmt.Sprintf("following:%s", req.FollowerID))

		c.JSON(http.StatusOK, gin.H{
			"status":       "followed",
			"follower_id":  req.FollowerID,
			"following_id": agentID,
		})
	})

	// Unfollow an agent
	r.DELETE("/agents/:id/follow", func(c *gin.Context) {
		agentID := c.Param("id")
		var req struct {
			FollowerID string `json:"follower_id" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "follower_id is required"})
			return
		}

		result, err := db.Exec(`
			DELETE FROM follows
			WHERE follower_id = $1 AND following_id = $2
		`, req.FollowerID, agentID)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		rowsAffected, _ := result.RowsAffected()
		if rowsAffected == 0 {
			c.JSON(http.StatusNotFound, gin.H{"error": "Follow relationship not found"})
			return
		}

		// Invalidate cache
		RedisClient.Del(ctx, fmt.Sprintf("followers:%s", agentID))
		RedisClient.Del(ctx, fmt.Sprintf("following:%s", req.FollowerID))

		c.JSON(http.StatusOK, gin.H{
			"status":       "unfollowed",
			"follower_id":  req.FollowerID,
			"following_id": agentID,
		})
	})

	// Get followers of an agent
	r.GET("/agents/:id/followers", func(c *gin.Context) {
		agentID := c.Param("id")
		cacheKey := fmt.Sprintf("followers:%s", agentID)

		// Check Redis cache
		val, err := RedisClient.Get(ctx, cacheKey).Result()
		if err == nil {
			var followers []string
			if err := json.Unmarshal([]byte(val), &followers); err == nil {
				c.JSON(http.StatusOK, gin.H{
					"agent_id":  agentID,
					"followers": followers,
					"count":     len(followers),
					"cached":    true,
				})
				return
			}
		}

		var followers []string
		err = db.Select(&followers, `
			SELECT follower_id
			FROM follows
			WHERE following_id = $1
			ORDER BY created_at DESC
		`, agentID)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// Cache for 5 minutes
		followersJSON, _ := json.Marshal(followers)
		RedisClient.Set(ctx, cacheKey, followersJSON, 5*time.Minute)

		c.JSON(http.StatusOK, gin.H{
			"agent_id":  agentID,
			"followers": followers,
			"count":     len(followers),
		})
	})

	// Get agents that an agent is following
	r.GET("/agents/:id/following", func(c *gin.Context) {
		agentID := c.Param("id")
		cacheKey := fmt.Sprintf("following:%s", agentID)

		// Check Redis cache
		val, err := RedisClient.Get(ctx, cacheKey).Result()
		if err == nil {
			var following []string
			if err := json.Unmarshal([]byte(val), &following); err == nil {
				c.JSON(http.StatusOK, gin.H{
					"agent_id":  agentID,
					"following": following,
					"count":     len(following),
					"cached":    true,
				})
				return
			}
		}

		var following []string
		err = db.Select(&following, `
			SELECT following_id
			FROM follows
			WHERE follower_id = $1
			ORDER BY created_at DESC
		`, agentID)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// Cache for 5 minutes
		followingJSON, _ := json.Marshal(following)
		RedisClient.Set(ctx, cacheKey, followingJSON, 5*time.Minute)

		c.JSON(http.StatusOK, gin.H{
			"agent_id":  agentID,
			"following": following,
			"count":     len(following),
		})
	})

	// Check if agent A follows agent B
	r.GET("/agents/:id/follows/:target_id", func(c *gin.Context) {
		agentID := c.Param("id")
		targetID := c.Param("target_id")

		var count int
		err := db.Get(&count, `
			SELECT COUNT(*)
			FROM follows
			WHERE follower_id = $1 AND following_id = $2
		`, agentID, targetID)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"follower_id":  agentID,
			"following_id": targetID,
			"is_following": count > 0,
		})
	})

	// Get personalized timeline (tweets from agents you follow)
	r.GET("/timeline/following/:agent_id", func(c *gin.Context) {
		agentID := c.Param("agent_id")
		limitStr := c.DefaultQuery("limit", "50")
		limit, _ := strconv.Atoi(limitStr)

		var tweets []Tweet
		err := db.Select(&tweets, `
			SELECT t.id, t.agent_id, t.content, t.thread_id, t.likes, t.retweets
			FROM tweets t
			INNER JOIN follows f ON t.agent_id = f.following_id
			WHERE f.follower_id = $1
			ORDER BY t.id DESC
			LIMIT $2
		`, agentID, limit)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"agent_id": agentID,
			"tweets":   tweets,
			"count":    len(tweets),
		})
	})

	// Start server
	r.Run(":8080")
}
