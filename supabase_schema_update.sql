-- ============================================================================
-- SUPABASE SCHEMA UPDATE
-- ============================================================================
-- Run this script in your Supabase SQL Editor to add new columns
-- ============================================================================

-- 1. Add thumbs_rating column to comments table
ALTER TABLE comments 
ADD COLUMN IF NOT EXISTS thumbs_rating TEXT CHECK (thumbs_rating IS NULL OR thumbs_rating IN ('up', 'down'));

-- Create index for faster queries on thumbs_rating
CREATE INDEX IF NOT EXISTS idx_comments_thumbs_rating ON comments(thumbs_rating) WHERE thumbs_rating IS NOT NULL;

-- 2. Add criteria_ratings column to feedback table (JSONB for storing criteria evaluations)
ALTER TABLE feedback 
ADD COLUMN IF NOT EXISTS criteria_ratings JSONB;

-- Create index for faster queries on criteria_ratings
CREATE INDEX IF NOT EXISTS idx_feedback_criteria_ratings ON feedback USING GIN (criteria_ratings) WHERE criteria_ratings IS NOT NULL;

-- Optional: Remove text_position column if it's causing issues (uncomment if needed)
-- ALTER TABLE comments DROP COLUMN IF EXISTS text_position;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify the columns were added:
-- 
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'comments' AND column_name = 'thumbs_rating';
--
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'feedback' AND column_name = 'criteria_ratings';
-- ============================================================================

