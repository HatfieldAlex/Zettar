CREATE TABLE substations (
    -- Adjust so it's ngedSubstationID - bc its unique to that DB, not our primary key data
    substationID INTEGER, 
    "type" TEXT,
    area TEXT,
    "name" TEXT,
    substationNumber INTEGER,
    "description" TEXT,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    "primary" TEXT,
    BSP TEXT,
    GSP TEXT,
    demandConnectedHeadroomMW DOUBLE PRECISION,
    demandContractedHeadroomMW DOUBLE PRECISION,
    demandConnectedRAG TEXT,
    demandContractedRAG TEXT,
    generationTotalCapacity DOUBLE PRECISION,
    generationConnectedHeadroomMW DOUBLE PRECISION,
    generationContractedHeadroomMW DOUBLE PRECISION,
    generationQuotedCapacity DOUBLE PRECISION,
    generationConnectedRAG TEXT,
    generationContractedRAG TEXT
);
