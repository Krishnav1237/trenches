package main

import (
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
)

type Poll struct {
	ID            int       `db:"id" json:"id"`
	TweetID       int       `db:"tweet_id" json:"tweet_id"`
	DurationHours int       `db:"duration_hours" json:"duration_hours"`
	EndsAt        time.Time `db:"ends_at" json:"ends_at"`
	CreatedAt     time.Time `db:"created_at" json:"created_at"`
}

type PollOption struct {
	ID          int    `db:"id" json:"id"`
	PollID      int    `db:"poll_id" json:"poll_id"`
	OptionText  string `db:"option_text" json:"option_text"`
	VoteCount   int    `db:"vote_count" json:"vote_count"`
	OptionIndex int    `db:"option_index" json:"option_index"`
}

type PollWithOptions struct {
	ID            int          `json:"id"`
	TweetID       int          `json:"tweet_id"`
	DurationHours int          `json:"duration_hours"`
	EndsAt        time.Time    `json:"ends_at"`
	IsEnded       bool         `json:"is_ended"`
	TotalVotes    int          `json:"total_votes"`
	Options       []PollOption `json:"options"`
	UserVote      *int         `json:"user_vote,omitempty"`
}

// CreatePoll creates a poll for a tweet
func CreatePoll(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	var req struct {
		Content       string   `json:"content" binding:"required"`
		Options       []string `json:"options" binding:"required,min=2,max=4"`
		DurationHours int      `json:"duration_hours" binding:"required,min=1,max=168"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// TODO: In a real implementation, we'd need agent_id from user mapping
	// For now, use username as agent_id
	agentID := user.Username

	// Create tweet
	var tweetID int
	err := db.QueryRowx(`
		INSERT INTO tweets (agent_id, content)
		VALUES ($1, $2)
		RETURNING id
	`, agentID, req.Content).Scan(&tweetID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create tweet"})
		return
	}

	// Create poll
	endsAt := time.Now().Add(time.Duration(req.DurationHours) * time.Hour)
	var pollID int
	err = db.QueryRowx(`
		INSERT INTO polls (tweet_id, duration_hours, ends_at)
		VALUES ($1, $2, $3)
		RETURNING id
	`, tweetID, req.DurationHours, endsAt).Scan(&pollID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create poll"})
		return
	}

	// Create poll options
	var options []PollOption
	for i, optionText := range req.Options {
		var option PollOption
		err = db.QueryRowx(`
			INSERT INTO poll_options (poll_id, option_text, option_index)
			VALUES ($1, $2, $3)
			RETURNING id, poll_id, option_text, vote_count, option_index
		`, pollID, optionText, i).StructScan(&option)

		if err != nil {
			continue
		}
		options = append(options, option)
	}

	c.JSON(http.StatusOK, gin.H{
		"poll_id":  pollID,
		"tweet_id": tweetID,
		"options":  options,
		"ends_at":  endsAt,
	})
}

// GetPoll gets a poll with its options
func GetPoll(c *gin.Context) {
	tweetIDStr := c.Param("id")
	tweetID, err := strconv.Atoi(tweetIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid tweet ID"})
		return
	}

	var poll Poll
	err = db.Get(&poll, `
		SELECT id, tweet_id, duration_hours, ends_at, created_at
		FROM polls
		WHERE tweet_id = $1
	`, tweetID)

	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Poll not found"})
		return
	}

	var options []PollOption
	err = db.Select(&options, `
		SELECT id, poll_id, option_text, vote_count, option_index
		FROM poll_options
		WHERE poll_id = $1
		ORDER BY option_index
	`, poll.ID)

	if err != nil {
		options = []PollOption{}
	}

	totalVotes := 0
	for _, opt := range options {
		totalVotes += opt.VoteCount
	}

	isEnded := time.Now().After(poll.EndsAt)

	pollWithOptions := PollWithOptions{
		ID:            poll.ID,
		TweetID:       poll.TweetID,
		DurationHours: poll.DurationHours,
		EndsAt:        poll.EndsAt,
		IsEnded:       isEnded,
		TotalVotes:    totalVotes,
		Options:       options,
	}

	// Check if user voted
	user, exists := GetCurrentUser(c)
	if exists {
		var votedOptionID int
		err = db.Get(&votedOptionID, `
			SELECT option_id FROM poll_votes
			WHERE poll_id = $1 AND user_id = $2
		`, poll.ID, user.ID)
		if err == nil {
			pollWithOptions.UserVote = &votedOptionID
		}
	}

	c.JSON(http.StatusOK, pollWithOptions)
}

// VotePoll votes on a poll
func VotePoll(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	pollIDStr := c.Param("id")
	pollID, err := strconv.Atoi(pollIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid poll ID"})
		return
	}

	var req struct {
		OptionID int `json:"option_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Check if poll exists and is not ended
	var poll Poll
	err = db.Get(&poll, `
		SELECT id, tweet_id, duration_hours, ends_at, created_at
		FROM polls
		WHERE id = $1
	`, pollID)

	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Poll not found"})
		return
	}

	if time.Now().After(poll.EndsAt) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Poll has ended"})
		return
	}

	// Check if option exists for this poll
	var optionExists int
	err = db.Get(&optionExists, `
		SELECT COUNT(*) FROM poll_options
		WHERE id = $1 AND poll_id = $2
	`, req.OptionID, pollID)

	if err != nil || optionExists == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid option"})
		return
	}

	// Insert or update vote
	_, err = db.Exec(`
		INSERT INTO poll_votes (poll_id, user_id, option_id)
		VALUES ($1, $2, $3)
		ON CONFLICT (poll_id, user_id) DO UPDATE
		SET option_id = $3
	`, pollID, user.ID, req.OptionID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to record vote"})
		return
	}

	// Update vote counts
	_, err = db.Exec(`
		UPDATE poll_options
		SET vote_count = (
			SELECT COUNT(*) FROM poll_votes WHERE option_id = poll_options.id
		)
		WHERE poll_id = $1
	`, pollID)
	if err != nil {
		log.Println("Warning: Failed to update vote counts:", err)
	}

	c.JSON(http.StatusOK, gin.H{
		"message":   "Vote recorded",
		"option_id": req.OptionID,
	})
}
