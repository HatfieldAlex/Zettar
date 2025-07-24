-- Add a new PostGIS geometry column to store lat/lon as a geographic point
ALTER TABLE substations 
ADD COLUMN geolocation geometry(Point, 4326);

-- Populate the new geolocation column using existing longitude and latitude
UPDATE substations 
SET geolocation = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
WHERE longitude IS NOT NULL AND latitude IS NOT NULL;

-- Remove the now-redundant longitude and latitude columns
ALTER TABLE substations
DROP COLUMN longitude,
DROP COLUMN latitude;

-- Create a spatial index on the new geolocation column to speed up spatial queries
CREATE INDEX idx_substations_geolocation
ON substations
USING GIST (geolocation);
