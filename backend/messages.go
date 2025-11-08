package main

import (
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
)

type Conversation struct {
	ID            int       `db:"id" json:"id"`
	User1ID       int       `db:"user1_id" json:"user1_id"`
	User2ID       int       `db:"user2_id" json:"user2_id"`
	LastMessageAt time.Time `db:"last_message_at" json:"last_message_at"`
	CreatedAt     time.Time `db:"created_at" json:"created_at"`
}

type Message struct {
	ID             int       `db:"id" json:"id"`
	ConversationID int       `db:"conversation_id" json:"conversation_id"`
	SenderID       int       `db:"sender_id" json:"sender_id"`
	Content        string    `db:"content" json:"content"`
	Read           bool      `db:"read" json:"read"`
	CreatedAt      time.Time `db:"created_at" json:"created_at"`
}

type ConversationWithUser struct {
	ID            int       `json:"id"`
	OtherUserID   int       `json:"other_user_id"`
	OtherUsername string    `json:"other_username"`
	OtherAvatar   string    `json:"other_avatar"`
	LastMessage   string    `json:"last_message"`
	LastMessageAt time.Time `json:"last_message_at"`
	UnreadCount   int       `json:"unread_count"`
}

type MessageWithSender struct {
	ID             int       `db:"id" json:"id"`
	ConversationID int       `db:"conversation_id" json:"conversation_id"`
	SenderID       int       `db:"sender_id" json:"sender_id"`
	SenderUsername string    `db:"sender_username" json:"sender_username"`
	SenderAvatar   string    `db:"sender_avatar" json:"sender_avatar"`
	Content        string    `db:"content" json:"content"`
	Read           bool      `db:"read" json:"read"`
	CreatedAt      time.Time `db:"created_at" json:"created_at"`
}

// GetOrCreateConversation gets or creates a conversation between two users
func GetOrCreateConversation(user1ID, user2ID int) (*Conversation, error) {
	// Ensure user1_id < user2_id for uniqueness
	if user1ID > user2ID {
		user1ID, user2ID = user2ID, user1ID
	}

	var conv Conversation
	err := db.Get(&conv, `
		SELECT * FROM conversations
		WHERE user1_id = $1 AND user2_id = $2
	`, user1ID, user2ID)

	if err != nil {
		// Create new conversation
		err = db.QueryRowx(`
			INSERT INTO conversations (user1_id, user2_id)
			VALUES ($1, $2)
			RETURNING id, user1_id, user2_id, last_message_at, created_at
		`, user1ID, user2ID).StructScan(&conv)
		if err != nil {
			return nil, err
		}
	}

	return &conv, nil
}

// SendMessage sends a message in a conversation
func SendMessage(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	var req struct {
		RecipientID int    `json:"recipient_id" binding:"required"`
		Content     string `json:"content" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Prevent sending message to self
	if user.ID == req.RecipientID {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Cannot send message to yourself"})
		return
	}

	// Get or create conversation
	conv, err := GetOrCreateConversation(user.ID, req.RecipientID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create conversation"})
		return
	}

	// Create message
	var message Message
	err = db.QueryRowx(`
		INSERT INTO messages (conversation_id, sender_id, content)
		VALUES ($1, $2, $3)
		RETURNING id, conversation_id, sender_id, content, read, created_at
	`, conv.ID, user.ID, req.Content).StructScan(&message)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send message"})
		return
	}

	// Update conversation last_message_at
	db.Exec(`
		UPDATE conversations
		SET last_message_at = NOW()
		WHERE id = $1
	`, conv.ID)

	c.JSON(http.StatusOK, gin.H{
		"message":         message,
		"conversation_id": conv.ID,
	})
}

// GetConversations gets all conversations for the current user
func GetConversations(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	var conversations []ConversationWithUser
	rows, err := db.Queryx(`
		SELECT
			c.id,
			CASE
				WHEN c.user1_id = $1 THEN c.user2_id
				ELSE c.user1_id
			END as other_user_id,
			CASE
				WHEN c.user1_id = $1 THEN u2.username
				ELSE u1.username
			END as other_username,
			CASE
				WHEN c.user1_id = $1 THEN u2.avatar
				ELSE u1.avatar
			END as other_avatar,
			COALESCE(m.content, '') as last_message,
			c.last_message_at,
			COALESCE((
				SELECT COUNT(*)
				FROM messages
				WHERE conversation_id = c.id
				AND sender_id != $1
				AND read = false
			), 0) as unread_count
		FROM conversations c
		JOIN users u1 ON c.user1_id = u1.id
		JOIN users u2 ON c.user2_id = u2.id
		LEFT JOIN LATERAL (
			SELECT content
			FROM messages
			WHERE conversation_id = c.id
			ORDER BY created_at DESC
			LIMIT 1
		) m ON true
		WHERE c.user1_id = $1 OR c.user2_id = $1
		ORDER BY c.last_message_at DESC
	`, user.ID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch conversations"})
		return
	}
	defer rows.Close()

	for rows.Next() {
		var conv ConversationWithUser
		err := rows.StructScan(&conv)
		if err != nil {
			continue
		}
		conversations = append(conversations, conv)
	}

	if conversations == nil {
		conversations = []ConversationWithUser{}
	}

	c.JSON(http.StatusOK, gin.H{
		"conversations": conversations,
		"count":         len(conversations),
	})
}

// GetMessages gets all messages in a conversation
func GetMessages(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	conversationIDStr := c.Param("id")
	conversationID, err := strconv.Atoi(conversationIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid conversation ID"})
		return
	}

	// Verify user is part of conversation
	var count int
	err = db.Get(&count, `
		SELECT COUNT(*)
		FROM conversations
		WHERE id = $1 AND (user1_id = $2 OR user2_id = $2)
	`, conversationID, user.ID)

	if err != nil || count == 0 {
		c.JSON(http.StatusForbidden, gin.H{"error": "Not authorized to view this conversation"})
		return
	}

	limitStr := c.DefaultQuery("limit", "50")
	limit, _ := strconv.Atoi(limitStr)
	if limit > 100 {
		limit = 100
	}

	var messages []MessageWithSender
	err = db.Select(&messages, `
		SELECT
			m.id,
			m.conversation_id,
			m.sender_id,
			u.username as sender_username,
			u.avatar as sender_avatar,
			m.content,
			m.read,
			m.created_at
		FROM messages m
		JOIN users u ON m.sender_id = u.id
		WHERE m.conversation_id = $1
		ORDER BY m.created_at DESC
		LIMIT $2
	`, conversationID, limit)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch messages"})
		return
	}

	if messages == nil {
		messages = []MessageWithSender{}
	}

	// Mark messages as read
	db.Exec(`
		UPDATE messages
		SET read = true
		WHERE conversation_id = $1 AND sender_id != $2 AND read = false
	`, conversationID, user.ID)

	c.JSON(http.StatusOK, gin.H{
		"messages": messages,
		"count":    len(messages),
	})
}

// GetUnreadMessageCount gets the total unread message count
func GetUnreadMessageCount(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	var count int
	err := db.Get(&count, `
		SELECT COUNT(*)
		FROM messages m
		JOIN conversations c ON m.conversation_id = c.id
		WHERE (c.user1_id = $1 OR c.user2_id = $1)
		AND m.sender_id != $1
		AND m.read = false
	`, user.ID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count messages"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"count": count,
	})
}
