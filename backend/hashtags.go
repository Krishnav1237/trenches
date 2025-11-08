package main

import (
	"net/http"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

type Hashtag struct {
	ID       int       `db:"id" json:"id"`
	Tag      string    `db:"tag" json:"tag"`
	Count    int       `db:"count" json:"count"`
	LastUsed time.Time `db:"last_used" json:"last_used"`
}

var hashtagRegex = regexp.MustCompile(`#(\w+)`)

// ExtractHashtags extracts hashtags from text
func ExtractHashtags(content string) []string {
	matches := hashtagRegex.FindAllStringSubmatch(content, -1)
	var hashtags []string
	seen := make(map[string]bool)

	for _, match := range matches {
		if len(match) > 1 {
			tag := strings.ToLower(match[1])
			if !seen[tag] {
				hashtags = append(hashtags, tag)
				seen[tag] = true
			}
		}
	}

	return hashtags
}

// ProcessHashtags processes hashtags for a tweet
func ProcessHashtags(tweetID int, content string) error {
	hashtags := ExtractHashtags(content)
	if len(hashtags) == 0 {
		return nil
	}

	for _, tag := range hashtags {
		// Insert or update hashtag
		var hashtagID int
		err := db.QueryRowx(`
			INSERT INTO hashtags (tag, count, last_used)
			VALUES ($1, 1, NOW())
			ON CONFLICT (tag) DO UPDATE
			SET count = hashtags.count + 1, last_used = NOW()
			RETURNING id
		`, tag).Scan(&hashtagID)

		if err != nil {
			continue
		}

		// Link tweet to hashtag
		_, err = db.Exec(`
			INSERT INTO tweet_hashtags (tweet_id, hashtag_id)
			VALUES ($1, $2)
			ON CONFLICT DO NOTHING
		`, tweetID, hashtagID)
		if err != nil {
			log.Println("Warning: Failed to link tweet to hashtag:", err)
		}
	}

	return nil
}

// ExtractMentions extracts user mentions from text
func ExtractMentions(content string) []string {
	mentionRegex := regexp.MustCompile(`@(\w+)`)
	matches := mentionRegex.FindAllStringSubmatch(content, -1)
	var mentions []string
	seen := make(map[string]bool)

	for _, match := range matches {
		if len(match) > 1 {
			username := strings.ToLower(match[1])
			if !seen[username] {
				mentions = append(mentions, username)
				seen[username] = true
			}
		}
	}

	return mentions
}

// ProcessMentions processes user mentions and creates notifications
func ProcessMentions(tweetID int, authorID int, content string) error {
	mentions := ExtractMentions(content)
	if len(mentions) == 0 {
		return nil
	}

	for _, username := range mentions {
		var userID int
		err := db.Get(&userID, "SELECT id FROM users WHERE username = $1", username)
		if err != nil {
			continue
		}

		// Create mention notification
		CreateNotification(userID, authorID, NotificationTypeMention, &tweetID)
	}

	return nil
}

// GetTrendingHashtags gets trending hashtags
func GetTrendingHashtags(c *gin.Context) {
	limitStr := c.DefaultQuery("limit", "20")
	limit, _ := strconv.Atoi(limitStr)
	if limit > 50 {
		limit = 50
	}

	var hashtags []Hashtag
	err := db.Select(&hashtags, `
		SELECT id, tag, count, last_used
		FROM hashtags
		WHERE last_used > NOW() - INTERVAL '7 days'
		ORDER BY count DESC, last_used DESC
		LIMIT $1
	`, limit)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch trending hashtags"})
		return
	}

	if hashtags == nil {
		hashtags = []Hashtag{}
	}

	c.JSON(http.StatusOK, gin.H{
		"hashtags": hashtags,
		"count":    len(hashtags),
	})
}

// GetTweetsByHashtag gets tweets containing a specific hashtag
func GetTweetsByHashtag(c *gin.Context) {
	tag := c.Param("tag")
	tag = strings.ToLower(strings.TrimPrefix(tag, "#"))

	limitStr := c.DefaultQuery("limit", "50")
	limit, _ := strconv.Atoi(limitStr)
	if limit > 100 {
		limit = 100
	}

	var tweets []Tweet
	err := db.Select(&tweets, `
		SELECT DISTINCT t.id, t.agent_id, t.content, t.thread_id, t.likes, t.retweets
		FROM tweets t
		JOIN tweet_hashtags th ON t.id = th.tweet_id
		JOIN hashtags h ON th.hashtag_id = h.id
		WHERE h.tag = $1
		ORDER BY t.id DESC
		LIMIT $2
	`, tag, limit)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch tweets"})
		return
	}

	if tweets == nil {
		tweets = []Tweet{}
	}

	c.JSON(http.StatusOK, gin.H{
		"tag":    tag,
		"tweets": tweets,
		"count":  len(tweets),
	})
}
