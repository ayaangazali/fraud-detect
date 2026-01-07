-- Migration 001: Add Authentication and Case Management
-- Date: 2026-01-06
-- Description: Adds full authentication system, case management, enhanced workflow tables

-- ============================================================================
-- PHASE 1: AUTHENTICATION TABLES
-- ============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'screener',  -- screener, checker, finalizer
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- Refresh tokens table
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_revoked BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);

-- ============================================================================
-- PHASE 2: CASE MANAGEMENT TABLES
-- ============================================================================

-- Cases table
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    created_by_id INTEGER,
    assigned_to_id INTEGER,
    title VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,
    FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_cases_number ON cases(case_number);
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_cases_priority ON cases(priority);
CREATE INDEX idx_cases_created_by ON cases(created_by_id);
CREATE INDEX idx_cases_assigned_to ON cases(assigned_to_id);
CREATE INDEX idx_cases_created_at ON cases(created_at);

-- Case notes table
CREATE TABLE IF NOT EXISTS case_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    user_id INTEGER,
    note TEXT NOT NULL,
    note_type VARCHAR(50) NOT NULL DEFAULT 'comment',
    note_metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_case_notes_case ON case_notes(case_id);
CREATE INDEX idx_case_notes_user ON case_notes(user_id);
CREATE INDEX idx_case_notes_type ON case_notes(note_type);
CREATE INDEX idx_case_notes_created_at ON case_notes(created_at);

-- ============================================================================
-- PHASE 2: EMAIL NOTIFICATION TABLES
-- ============================================================================

-- Email notifications queue
CREATE TABLE IF NOT EXISTS email_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    to_email VARCHAR(255) NOT NULL,
    email_type VARCHAR(50) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    email_metadata TEXT,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    failed_at TIMESTAMP,
    next_retry_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_email_notifications_user ON email_notifications(user_id);
CREATE INDEX idx_email_notifications_email ON email_notifications(to_email);
CREATE INDEX idx_email_notifications_type ON email_notifications(email_type);
CREATE INDEX idx_email_notifications_status ON email_notifications(status);
CREATE INDEX idx_email_notifications_created_at ON email_notifications(created_at);

-- Email templates
CREATE TABLE IF NOT EXISTS email_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name VARCHAR(100) UNIQUE NOT NULL,
    email_type VARCHAR(50) NOT NULL,
    subject_template VARCHAR(500) NOT NULL,
    body_template TEXT NOT NULL,
    description TEXT,
    variables TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_email_templates_name ON email_templates(template_name);
CREATE INDEX idx_email_templates_type ON email_templates(email_type);

-- ============================================================================
-- PHASE 2: REPORT GENERATION TABLES
-- ============================================================================

-- Reports table
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type VARCHAR(50) NOT NULL,
    report_number VARCHAR(50) UNIQUE NOT NULL,
    generated_by_id INTEGER,
    date_from DATE,
    date_to DATE,
    filters TEXT,
    file_path VARCHAR(500),
    file_name VARCHAR(255),
    file_size INTEGER,
    file_format VARCHAR(10),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    report_metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (generated_by_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_number ON reports(report_number);
CREATE INDEX idx_reports_generated_by ON reports(generated_by_id);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_date_from ON reports(date_from);
CREATE INDEX idx_reports_date_to ON reports(date_to);
CREATE INDEX idx_reports_created_at ON reports(created_at);

-- Report schedules
CREATE TABLE IF NOT EXISTS report_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    schedule_name VARCHAR(255) NOT NULL,
    schedule_type VARCHAR(20) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    report_config TEXT NOT NULL,
    send_email BOOLEAN NOT NULL DEFAULT 1,
    email_recipients TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    last_run TIMESTAMP,
    last_status VARCHAR(50),
    last_error TEXT,
    next_run TIMESTAMP,
    run_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_report_schedules_user ON report_schedules(user_id);
CREATE INDEX idx_report_schedules_type ON report_schedules(schedule_type);
CREATE INDEX idx_report_schedules_active ON report_schedules(is_active);
CREATE INDEX idx_report_schedules_next_run ON report_schedules(next_run);

-- ============================================================================
-- ROLLBACK SCRIPT (Save this separately as rollback_001.sql)
-- ============================================================================

/*
-- To rollback this migration, run:

DROP TABLE IF EXISTS report_schedules;
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS email_templates;
DROP TABLE IF EXISTS email_notifications;
DROP TABLE IF EXISTS case_notes;
DROP TABLE IF EXISTS cases;
DROP TABLE IF EXISTS refresh_tokens;
DROP TABLE IF EXISTS users;

-- Note: Existing tables (kamco_*, in_review_queue, flagged_items, logbook) will remain
-- Run seed_database.py after rollback to restore test data
*/
