-- Database Migration: Add Phase 3 Fields to FlaggedItem
-- Run this to add the 7 new columns needed for Phase 3 workflow tracking

-- Add timestamp columns for workflow tracking
ALTER TABLE flagged_items ADD COLUMN checker_assigned_at TIMESTAMP;
ALTER TABLE flagged_items ADD COLUMN checker_reviewed_at TIMESTAMP;
ALTER TABLE flagged_items ADD COLUMN finalizer_reviewed_at TIMESTAMP;
ALTER TABLE flagged_items ADD COLUMN resolution_date TIMESTAMP;

-- Add notes columns for reviewer comments
ALTER TABLE flagged_items ADD COLUMN checker_notes TEXT;
ALTER TABLE flagged_items ADD COLUMN finalizer_notes TEXT;

-- Add escalation tracking
ALTER TABLE flagged_items ADD COLUMN escalation_level VARCHAR(50);

-- Verify columns were added
SELECT sql FROM sqlite_master WHERE type='table' AND name='flagged_items';
