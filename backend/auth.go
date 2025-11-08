package main

import (
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"golang.org/x/crypto/bcrypt"
)

type User struct {
	ID           int       `db:"id" json:"id"`
	Username     string    `db:"username" json:"username"`
	Email        string    `db:"email" json:"email"`
	PasswordHash string    `db:"password_hash" json:"-"`
	DisplayName  string    `db:"display_name" json:"display_name"`
	Avatar       string    `db:"avatar" json:"avatar"`
	CreatedAt    time.Time `db:"created_at" json:"created_at"`
}

type Session struct {
	ID        int       `db:"id" json:"id"`
	UserID    int       `db:"user_id" json:"user_id"`
	Token     string    `db:"token" json:"token"`
	ExpiresAt time.Time `db:"expires_at" json:"expires_at"`
	CreatedAt time.Time `db:"created_at" json:"created_at"`
}

// SignupRequest represents the signup payload
type SignupRequest struct {
	Username    string `json:"username" binding:"required,min=3,max=30"`
	Email       string `json:"email" binding:"required,email"`
	Password    string `json:"password" binding:"required,min=6"`
	DisplayName string `json:"display_name" binding:"required,min=1"`
}

// LoginRequest represents the login payload
type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

// AuthResponse is returned after successful authentication
type AuthResponse struct {
	User  User   `json:"user"`
	Token string `json:"token"`
}

// HashPassword hashes a password using bcrypt
func HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)
	return string(bytes), err
}

// CheckPasswordHash compares a password with a hash
func CheckPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}

// GenerateToken creates a secure random token
func GenerateToken() (string, error) {
	b := make([]byte, 32)
	_, err := rand.Read(b)
	if err != nil {
		return "", err
	}
	return base64.URLEncoding.EncodeToString(b), nil
}

// CreateSession creates a new session for a user
func CreateSession(userID int) (*Session, error) {
	token, err := GenerateToken()
	if err != nil {
		return nil, err
	}

	expiresAt := time.Now().Add(30 * 24 * time.Hour) // 30 days

	var sessionID int
	err = db.QueryRowx(`
		INSERT INTO sessions (user_id, token, expires_at)
		VALUES ($1, $2, $3)
		RETURNING id
	`, userID, token, expiresAt).Scan(&sessionID)

	if err != nil {
		return nil, err
	}

	return &Session{
		ID:        sessionID,
		UserID:    userID,
		Token:     token,
		ExpiresAt: expiresAt,
		CreatedAt: time.Now(),
	}, nil
}

// ValidateSession checks if a token is valid and returns the user
func ValidateSession(token string) (*User, error) {
	var session Session
	err := db.Get(&session, `
		SELECT id, user_id, token, expires_at, created_at
		FROM sessions
		WHERE token = $1 AND expires_at > NOW()
	`, token)

	if err != nil {
		return nil, fmt.Errorf("invalid or expired token")
	}

	var user User
	err = db.Get(&user, `
		SELECT id, username, email, display_name, avatar, created_at
		FROM users
		WHERE id = $1
	`, session.UserID)

	if err != nil {
		return nil, fmt.Errorf("user not found")
	}

	return &user, nil
}

// AuthMiddleware is middleware that requires authentication
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
			c.Abort()
			return
		}

		// Expecting "Bearer <token>"
		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid authorization format"})
			c.Abort()
			return
		}

		token := parts[1]
		user, err := ValidateSession(token)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid or expired token"})
			c.Abort()
			return
		}

		// Store user in context
		c.Set("user", user)
		c.Next()
	}
}

// OptionalAuthMiddleware is middleware that optionally validates auth
func OptionalAuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader != "" {
			parts := strings.Split(authHeader, " ")
			if len(parts) == 2 && parts[0] == "Bearer" {
				token := parts[1]
				user, err := ValidateSession(token)
				if err == nil {
					c.Set("user", user)
				}
			}
		}
		c.Next()
	}
}

// GetCurrentUser returns the authenticated user from context
func GetCurrentUser(c *gin.Context) (*User, bool) {
	user, exists := c.Get("user")
	if !exists {
		return nil, false
	}
	return user.(*User), true
}

// Signup handles user registration
func Signup(c *gin.Context) {
	var req SignupRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Check if username already exists
	var count int
	err := db.Get(&count, "SELECT COUNT(*) FROM users WHERE username = $1", req.Username)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}
	if count > 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Username already taken"})
		return
	}

	// Check if email already exists
	err = db.Get(&count, "SELECT COUNT(*) FROM users WHERE email = $1", req.Email)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}
	if count > 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Email already registered"})
		return
	}

	// Hash password
	passwordHash, err := HashPassword(req.Password)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
		return
	}

	// Generate avatar URL (using DiceBear API)
	avatar := fmt.Sprintf("https://api.dicebear.com/7.x/avataaars/svg?seed=%s", req.Username)

	// Create user
	var userID int
	err = db.QueryRowx(`
		INSERT INTO users (username, email, password_hash, display_name, avatar)
		VALUES ($1, $2, $3, $4, $5)
		RETURNING id
	`, req.Username, req.Email, passwordHash, req.DisplayName, avatar).Scan(&userID)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
		return
	}

	// Get the created user
	var user User
	err = db.Get(&user, "SELECT id, username, email, display_name, avatar, created_at FROM users WHERE id = $1", userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch user"})
		return
	}

	// Create session
	session, err := CreateSession(userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create session"})
		return
	}

	c.JSON(http.StatusCreated, AuthResponse{
		User:  user,
		Token: session.Token,
	})
}

// Login handles user authentication
func Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get user by username
	var user User
	err := db.Get(&user, `
		SELECT id, username, email, password_hash, display_name, avatar, created_at
		FROM users
		WHERE username = $1
	`, req.Username)

	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid username or password"})
		return
	}

	// Check password
	if !CheckPasswordHash(req.Password, user.PasswordHash) {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid username or password"})
		return
	}

	// Create session
	session, err := CreateSession(user.ID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create session"})
		return
	}

	// Remove password hash before sending
	user.PasswordHash = ""

	c.JSON(http.StatusOK, AuthResponse{
		User:  user,
		Token: session.Token,
	})
}

// Logout invalidates a session
func Logout(c *gin.Context) {
	authHeader := c.GetHeader("Authorization")
	if authHeader == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No token provided"})
		return
	}

	parts := strings.Split(authHeader, " ")
	if len(parts) != 2 || parts[0] != "Bearer" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid authorization format"})
		return
	}

	token := parts[1]

	// Delete session
	_, err := db.Exec("DELETE FROM sessions WHERE token = $1", token)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to logout"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Logged out successfully"})
}

// GetMe returns the currently authenticated user
func GetMe(c *gin.Context) {
	user, exists := GetCurrentUser(c)
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	c.JSON(http.StatusOK, user)
}
