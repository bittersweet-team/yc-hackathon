-- Create demos table
CREATE TABLE IF NOT EXISTS demos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    product_url TEXT NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    long_video_url TEXT,
    short_video_urls TEXT[] DEFAULT '{}',
    klap_folder_id TEXT,
    klap_project_id TEXT,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for user_id
CREATE INDEX IF NOT EXISTS idx_demos_user_id ON demos(user_id);

-- Create index for status
CREATE INDEX IF NOT EXISTS idx_demos_status ON demos(status);

-- Create RLS policies
ALTER TABLE demos ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own demos
CREATE POLICY "Users can view own demos" ON demos
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can create their own demos
CREATE POLICY "Users can create own demos" ON demos
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own demos
CREATE POLICY "Users can update own demos" ON demos
    FOR UPDATE USING (auth.uid() = user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_demos_updated_at BEFORE UPDATE ON demos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create storage bucket for videos
INSERT INTO storage.buckets (id, name, public)
VALUES ('demo-videos', 'demo-videos', true)
ON CONFLICT (id) DO NOTHING;

-- Create storage policies
CREATE POLICY "Users can upload videos" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'demo-videos' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can view videos" ON storage.objects
    FOR SELECT USING (bucket_id = 'demo-videos');

CREATE POLICY "Users can update their videos" ON storage.objects
    FOR UPDATE USING (bucket_id = 'demo-videos' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can delete their videos" ON storage.objects
    FOR DELETE USING (bucket_id = 'demo-videos' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Create task queue table
CREATE TABLE IF NOT EXISTS task_queue (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    attempts INT DEFAULT 0,
    max_attempts INT DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create index for task queue
CREATE INDEX IF NOT EXISTS idx_task_queue_status ON task_queue(status);
CREATE INDEX IF NOT EXISTS idx_task_queue_created ON task_queue(created_at);

-- Function to claim next task
CREATE OR REPLACE FUNCTION claim_next_task()
RETURNS task_queue AS $$
DECLARE
    next_task task_queue;
BEGIN
    SELECT * INTO next_task
    FROM task_queue
    WHERE status = 'pending'
    AND attempts < max_attempts
    ORDER BY created_at ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED;
    
    IF next_task.id IS NOT NULL THEN
        UPDATE task_queue
        SET status = 'processing',
            started_at = NOW(),
            attempts = attempts + 1
        WHERE id = next_task.id;
    END IF;
    
    RETURN next_task;
END;
$$ LANGUAGE plpgsql;