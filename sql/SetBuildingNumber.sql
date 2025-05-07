-- Add a new column to the ClassMeetings table
ALTER TABLE ClassMeetings
ADD COLUMN Building_Room TEXT;

-- Update the new Building_Room column by combining Building and Room
UPDATE ClassMeetings
SET Building_Room = UPPER(SUBSTR(Building, 1, 3)) || '_' || Room;
