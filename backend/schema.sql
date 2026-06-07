CREATE DATABASE IF NOT EXISTS ai_chat_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ai_chat_agent;

-- Users table (populated on first Google login)
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    google_id   VARCHAR(128) NOT NULL UNIQUE,
    email       VARCHAR(255) NOT NULL UNIQUE,
    name        VARCHAR(255),
    picture     TEXT,
    is_premium  BOOLEAN DEFAULT FALSE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Daily message usage per user
CREATE TABLE IF NOT EXISTS daily_usage (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    usage_date  DATE NOT NULL,
    msg_count   INT DEFAULT 0,
    UNIQUE KEY uniq_user_date (user_id, usage_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Full conversation history
CREATE TABLE IF NOT EXISTS conversations (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    role        ENUM('user','assistant') NOT NULL,
    content     TEXT NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Integration settings per user
CREATE TABLE IF NOT EXISTS integrations (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    -- WhatsApp
    wa_number       VARCHAR(32),
    wa_api_key      TEXT,
    wa_enabled      BOOLEAN DEFAULT FALSE,
    -- E-commerce
    ec_store_type   ENUM('shopify','woocommerce','custom') DEFAULT 'custom',
    ec_store_url    VARCHAR(512),
    ec_api_key      TEXT,
    ec_enabled      BOOLEAN DEFAULT FALSE,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);