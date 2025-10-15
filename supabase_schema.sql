-- Supabase Database Schema for Reserve Flow AI Migration
-- This schema replaces the IndexedDB Dexie.js schema with PostgreSQL tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Profiles table (replaces IndexedDB profiles)
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    hashed_pin TEXT,
    pin_salt TEXT,
    kdf JSONB, -- Store KDF metadata as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projects table (replaces IndexedDB projects)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    client_name TEXT,
    address TEXT,
    current_reserve_balance DECIMAL(12,2) DEFAULT 0,
    custom_fields JSONB DEFAULT '{}', -- Store custom field values as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes for performance
    UNIQUE(name, profile_id) -- Same project name can exist across different profiles
);

-- Categories table (replaces IndexedDB categories)
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    parent_id UUID REFERENCES categories(id) ON DELETE CASCADE, -- For nested categories
    meta JSONB DEFAULT '{}', -- Store additional category metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    UNIQUE(project_id, name) -- Category names unique per project
);

-- Field definitions table (replaces IndexedDB fieldDefinitions)
CREATE TABLE field_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL, -- Internal field key
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('component', 'project')),
    field_type TEXT NOT NULL CHECK (field_type IN ('text', 'number', 'currency', 'date', 'select', 'boolean')),
    label TEXT NOT NULL, -- User-visible label
    required BOOLEAN DEFAULT FALSE,
    default_value JSONB, -- Store default value as JSON
    options JSONB, -- For select fields, store options as JSON array
    validation JSONB, -- Store validation rules as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    UNIQUE(project_id, name, entity_type) -- Field names unique per project and entity type
);

-- Templates table (replaces IndexedDB templates)
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('component', 'project')),
    field_definitions UUID[] DEFAULT '{}', -- Array of field definition IDs
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    UNIQUE(project_id, name, entity_type)
);

-- Tags table (replaces IndexedDB tags)
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    UNIQUE(project_id, name)
);

-- Components table (replaces IndexedDB components)
CREATE TABLE components (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    category TEXT, -- Denormalized for performance, can also link to categories table
    base_cost DECIMAL(12,2),
    useful_life INTEGER,
    custom_fields JSONB DEFAULT '{}', -- Store custom field values as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    UNIQUE(project_id, name) -- Component names unique per project
);

-- Component tags junction table (replaces IndexedDB componentTags)
CREATE TABLE component_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_id UUID NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,

    -- Ensure no duplicate tag assignments
    UNIQUE(component_id, tag_id)
);

-- Component catalog table (replaces IndexedDB componentCatalog)
-- This stores global component templates that can be used across projects
CREATE TABLE component_catalog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    category TEXT,
    base_cost DECIMAL(12,2),
    useful_life INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit logs table (replaces IndexedDB auditLogs)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    entity_type TEXT NOT NULL, -- 'component', 'project', 'category', etc.
    entity_id UUID NOT NULL, -- ID of the affected entity
    action TEXT NOT NULL, -- 'create', 'update', 'delete', 'schema-change'
    old_values JSONB, -- Previous values (for updates/deletes)
    new_values JSONB, -- New values (for creates/updates)
    metadata JSONB DEFAULT '{}', -- Additional context
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes for efficient querying
    INDEX idx_audit_logs_profile_id (profile_id),
    INDEX idx_audit_logs_entity (entity_type, entity_id),
    INDEX idx_audit_logs_created_at (created_at)
);

-- App settings table (replaces IndexedDB appSettings)
CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Metro multipliers for cost adjustments (from source app data/metro.ts)
CREATE TABLE metro_multipliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metro_area TEXT NOT NULL UNIQUE,
    multiplier DECIMAL(4,3) NOT NULL, -- e.g., 1.050 for 5% adjustment
    region TEXT, -- e.g., 'Northeast', 'Southwest'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Project metro settings (linking projects to metro areas)
CREATE TABLE project_metro_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    metro_area TEXT NOT NULL,
    custom_multiplier DECIMAL(4,3), -- Optional custom multiplier override
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(project_id) -- One metro setting per project
);

-- Create indexes for better performance
CREATE INDEX idx_projects_profile_id ON projects(profile_id);
CREATE INDEX idx_components_project_id ON components(project_id);
CREATE INDEX idx_categories_project_id ON categories(project_id);
CREATE INDEX idx_field_definitions_project_id ON field_definitions(project_id);
CREATE INDEX idx_templates_project_id ON templates(project_id);
CREATE INDEX idx_tags_project_id ON tags(project_id);
CREATE INDEX idx_component_tags_component_id ON component_tags(component_id);
CREATE INDEX idx_component_tags_tag_id ON component_tags(tag_id);
CREATE INDEX idx_project_metro_settings_project_id ON project_metro_settings(project_id);

-- Row Level Security (RLS) policies for multi-tenant security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE components ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE component_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_metro_settings ENABLE ROW LEVEL SECURITY;

-- RLS Policies (users can only access their own data)
-- Note: These would be implemented with Supabase auth integration

-- Updated at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers to relevant tables
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_components_updated_at BEFORE UPDATE ON components FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_field_definitions_updated_at BEFORE UPDATE ON field_definitions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tags_updated_at BEFORE UPDATE ON tags FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_app_settings_updated_at BEFORE UPDATE ON app_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
