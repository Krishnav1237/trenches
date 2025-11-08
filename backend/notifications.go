package main

import (
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
)

// Notification types
const (
	NotificationTypeLike    = "like"
	NotificationTypeRetweet = "retweet"
	NotificationTypeReply   = "reply"
	NotificationTypeFollow  = "follow"
	NotificationTypeMention = "mention"
)

type Notification struct {
	ID        int       `db:"id" json:"id"`
	UserID    int       `db:"user_id" json:"user_id"`
	ActorID   int       `db:"actor_id" json:"actor_id"`
	Type      string    `db:"type" json:"type"`
	TweetID   *int      `db:"tweet_id" json:"tweet_id,omitempty"`
	Read      bool      `db:"read" json:"read"`
	CreatedAt time.Time `db:"created_at" json:"created_at"`
}

type NotificationWithDetails struct {
	ID               int       `json:"id"`
	Type             string    `json:"type"`
	Read             bool      `json:"read"`
	CreatedAt        time.Time `json:"created_at"`
	ActorUsername    string    `json:"actor_username"`
	ActorDisplayName string    `json:"actor_display_name"`
	ActorAvatar      string    `json:"actor_avatar"`
	TweetID          *int      `json:"tweet_id,omitempty"`
	TweetContent     *string   `json:"tweet_content,omitempty"`
}

// CreateNotification creates a new notification
func CreateNotification(userID, actorID int, notifType string, tweetID *int) error {
	// Don't create notification if user is the actor
	if userID == actorID {
		return nil
	}

	_, err := db.Exec(`
		INSERT INTO notifications (user_id, actor_id, type, tweet_id)
		VALUES ($1, $2, $3, $4)
	`, userID, actorID, notifType, tweetID)

	if err != nil {
		return err
	}

	// TODO: Broadcast notification via WebSocket
	// wsHub.BroadcastNotification(userID, notification)

	return nil
}

// GetUserNotifications returns notifications for a user
func GetUserNotifications(c *gin.Context) {
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

	unreadOnly := c.Query("unread") == "true"

	query := `
		SELECT
			n.id,
			n.type,
			n.read,
			n.created_at,
			u.username as actor_username,
			u.display_name as actor_display_name,
			u.avatar as actor_avatar,
			n.tweet_id,
			t.content as tweet_content
		FROM notifications n
		JOIN users u ON n.actor_id = u.id
		LEFT JOIN tweets t ON n.tweet_id = t.id
		WHERE n.user_id = $1
	`

	args := []interface{}{user.ID}
	argPos := 2

	if unreadOnly {
		query += fmt.Sprintf(" AND n.read = false")
	}

	query += fmt.Sprintf(" ORDER BY n.created_at DESC LIMIT $%d", argPos)
	args = append(args, limit)

	rows, err := db.Queryx(query, args...)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch notifications"})
		return
	}
	defer rows.Close()

	var notifications []NotificationWithDetails
	for rows.Next() {
		var n NotificationWithDetails
		err := rows.Scan(
			&n.ID,
			&n.Type,
			&n.Read,
			&n.CreatedAt,
			&n.ActorUsername,
			&n.ActorDisplayName,
			&n.ActorAvatar,
			&n.TweetID,
			&n.TweetContent,
		)
		if err != nil {
			continue
		}
		notifications = append(notifications, n)
	}

	if notifications == nil {
		notifications = []NotificationWithDetails{}
	}

	c.JSON(http.StatusOK, gin.H{
		"notifications": notifications,
		"count":         len(notifications),
	})
}

// GetUnreadCount returns the count of unread notifications
func GetUnreadCount(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	var count int
	err := db.Get(&count, `
		SELECT COUNT(*)
		FROM notifications
		WHERE user_id = $1 AND read = false
	`, user.ID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count notifications"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"count": count,
	})
}

// MarkNotificationAsRead marks a specific notification as read
func MarkNotificationAsRead(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	notifID := c.Param("id")

	result, err := db.Exec(`
		UPDATE notifications
		SET read = true
		WHERE id = $1 AND user_id = $2
	`, notifID, user.ID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to mark notification as read"})
		return
	}

	rowsAffected, _ := result.RowsAffected()
	if rowsAffected == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Notification not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Notification marked as read"})
}

// MarkAllAsRead marks all notifications as read for the user
func MarkAllAsRead(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	_, err := db.Exec(`
		UPDATE notifications
		SET read = true
		WHERE user_id = $1 AND read = false
	`, user.ID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to mark notifications as read"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "All notifications marked as read"})
}

// GetTweetAuthorID helper function to get the author of a tweet
func GetTweetAuthorID(tweetID int) (*int, error) {
	var agentID string
	err := db.Get(&agentID, "SELECT agent_id FROM tweets WHERE id = $1", tweetID)
	if err != nil {
		return nil, err
	}

	// For now, agent_id is a string. In the future, we'll need to map agents to users
	// For now, we'll skip creating notifications for agent tweets
	// This will be implemented when we have proper user-agent mapping
	return nil, nil
}
