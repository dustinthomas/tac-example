-- 002_create_equipment.sql
-- Create equipment table for fab tool tracking

CREATE TABLE IF NOT EXISTS equipment (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    area VARCHAR(50) NOT NULL CHECK (area IN ('Lithography', 'Etching', 'Deposition', 'Metrology')),
    bay VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'DOWN' CHECK (status IN ('UP', 'UP WITH ISSUES', 'MAINTENANCE', 'DOWN')),
    criticality VARCHAR(20) NOT NULL DEFAULT 'Medium' CHECK (criticality IN ('Critical', 'High', 'Medium', 'Low')),
    updated_by VARCHAR(50),
    last_comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
