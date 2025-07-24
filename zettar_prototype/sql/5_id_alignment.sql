-- Step 1: Rename the column
ALTER TABLE substations
RENAME COLUMN substationid TO substation_nged_id;

-- Step 2: Add new internal ID column (typically a serial primary key)
ALTER TABLE substations
ADD COLUMN id SERIAL PRIMARY KEY;
