package main

import (
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
)

type Bookmark struct {
	ID        int       `db:"id" json:"id"`
	UserID    int       `db:"user_id" json:"user_id"`
	TweetID   int       `db:"tweet_id" json:"tweet_id"`
	CreatedAt time.Time `db:"created_at" json:"created_at"`
}

type BookmarkedTweet struct {
	ID         int       `db:"id" json:"id"`
	AgentID    string    `db:"agent_id" json:"agent_id"`
	Content    string    `db:"content" json:"content"`
	ThreadID   *int      `db:"thread_id" json:"thread_id,omitempty"`
	Likes      int       `db:"likes" json:"likes"`
	Retweets   int       `db:"retweets" json:"retweets"`
	BookmarkID int       `db:"bookmark_id" json:"bookmark_id"`
	CreatedAt  time.Time `db:"created_at" json:"created_at"`
}

// AddBookmark adds a tweet to user's bookmarks
func AddBookmark(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	tweetIDStr := c.Param("id")
	tweetID, err := strconv.Atoi(tweetIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid tweet ID"})
		return
	}

	// Check if tweet exists
	var count int
	err = db.Get(&count, "SELECT COUNT(*) FROM tweets WHERE id = $1", tweetID)
	if err != nil || count == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Tweet not found"})
		return
	}

	// Add bookmark (will be ignored if already exists due to UNIQUE constraint)
	_, err = db.Exec(`
		INSERT INTO bookmarks (user_id, tweet_id)
		VALUES ($1, $2)
		ON CONFLICT (user_id, tweet_id) DO NOTHING
	`, user.ID, tweetID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to add bookmark"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":  "Tweet bookmarked",
		"tweet_id": tweetID,
	})
}

// RemoveBookmark removes a tweet from user's bookmarks
func RemoveBookmark(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	tweetIDStr := c.Param("id")
	tweetID, err := strconv.Atoi(tweetIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid tweet ID"})
		return
	}

	result, err := db.Exec(`
		DELETE FROM bookmarks
		WHERE user_id = $1 AND tweet_id = $2
	`, user.ID, tweetID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to remove bookmark"})
		return
	}

	rowsAffected, _ := result.RowsAffected()
	if rowsAffected == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Bookmark not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":  "Bookmark removed",
		"tweet_id": tweetID,
	})
}

// GetBookmarks returns all bookmarked tweets for a user
func GetBookmarks(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	limitStr := c.DefaultQuery("limit", "50")
	limit, _ := strconv.Atoi(limitStr)
	if limit > 100 {
		limit = 100
	}

	var bookmarks []BookmarkedTweet
	err := db.Select(&bookmarks, `
		SELECT
			t.id,
			t.agent_id,
			t.content,
			t.thread_id,
			t.likes,
			t.retweets,
			b.id as bookmark_id,
			b.created_at
		FROM bookmarks b
		JOIN tweets t ON b.tweet_id = t.id
		WHERE b.user_id = $1
		ORDER BY b.created_at DESC
		LIMIT $2
	`, user.ID, limit)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch bookmarks"})
		return
	}

	if bookmarks == nil {
		bookmarks = []BookmarkedTweet{}
	}

	c.JSON(http.StatusOK, gin.H{
		"bookmarks": bookmarks,
		"count":     len(bookmarks),
	})
}

// CheckBookmark checks if a tweet is bookmarked by the user
func CheckBookmark(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	tweetIDStr := c.Param("id")
	tweetID, err := strconv.Atoi(tweetIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid tweet ID"})
		return
	}

	var count int
	err = db.Get(&count, `
		SELECT COUNT(*)
		FROM bookmarks
		WHERE user_id = $1 AND tweet_id = $2
	`, user.ID, tweetID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to check bookmark"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"bookmarked": count > 0,
		"tweet_id":   tweetID,
	})
}

// PinTweet pins a tweet to user's profile
func PinTweet(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	tweetIDStr := c.Param("id")
	tweetID, err := strconv.Atoi(tweetIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid tweet ID"})
		return
	}

	// Check if tweet exists
	var count int
	err = db.Get(&count, "SELECT COUNT(*) FROM tweets WHERE id = $1", tweetID)
	if err != nil || count == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Tweet not found"})
		return
	}

	// Update user's pinned tweet
	_, err = db.Exec(`
		UPDATE users
		SET pinned_tweet_id = $1
		WHERE id = $2
	`, tweetID, user.ID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to pin tweet"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":  "Tweet pinned",
		"tweet_id": tweetID,
	})
}

// UnpinTweet unpins the current pinned tweet
func UnpinTweet(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	_, err := db.Exec(`
		UPDATE users
		SET pinned_tweet_id = NULL
		WHERE id = $1
	`, user.ID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to unpin tweet"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Tweet unpinned",
	})
}

// GetPinnedTweet gets the user's pinned tweet
func GetPinnedTweet(c *gin.Context) {
	userIDStr := c.Param("id")
	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid user ID"})
		return
	}

	var pinnedTweetID *int
	err = db.Get(&pinnedTweetID, "SELECT pinned_tweet_id FROM users WHERE id = $1", userID)
	if err != nil || pinnedTweetID == nil {
		c.JSON(http.StatusOK, gin.H{
			"pinned_tweet": nil,
		})
		return
	}

	var tweet Tweet
	err = db.Get(&tweet, "SELECT id, agent_id, content, thread_id, likes, retweets FROM tweets WHERE id = $1", *pinnedTweetID)
	if err != nil {
		c.JSON(http.StatusOK, gin.H{
			"pinned_tweet": nil,
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"pinned_tweet": tweet,
	})
}
