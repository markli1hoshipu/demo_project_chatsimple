CREATE DATABASE chatsimple_demo;

USE chatsimple_demo;

CREATE TABLE visitors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fingerprint VARCHAR(64) NOT NULL UNIQUE,    -- 设备指纹
    user_agent TEXT,                            -- 用户浏览器信息
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    count INT
);

CREATE TABLE responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    visitor_id VARCHAR(64) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    FOREIGN KEY (visitor_id) REFERENCES visitors(fingerprint)
);

/* 
FOREIGN KEY (visitor_id) REFERENCES visitors(fingerprint) ON DELETE CASCADE
*/




