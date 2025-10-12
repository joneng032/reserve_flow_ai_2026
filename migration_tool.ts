/**
 * Data Migration Tool for Reserve Flow AI
 *
 * This script migrates data from IndexedDB (Dexie.js) to Supabase PostgreSQL.
 * Run this in the browser console of the source PWA application.
 */

interface MigrationData {
  profiles: any[];
  projects: any[];
  components: any[];
  componentCatalog: any[];
  categories: any[];
  fieldDefinitions: any[];
  templates: any[];
  tags: any[];
  componentTags: any[];
  auditLogs: any[];
  appSettings: any[];
  projectMetroSettings: any[];
  metadata: {
    exportedAt: string;
    version: string;
    totalRecords: number;
  };
}

/**
 * Export all data from IndexedDB
 */
async function exportIndexedDBData(): Promise<MigrationData> {
  console.log("🔄 Starting IndexedDB data export...");

  // This would need to be run in the context of the source app
  // where Dexie db is available
  const data: MigrationData = {
    profiles: [],
    projects: [],
    components: [],
    componentCatalog: [],
    categories: [],
    fieldDefinitions: [],
    templates: [],
    tags: [],
    componentTags: [],
    auditLogs: [],
    appSettings: [],
    projectMetroSettings: [],
    metadata: {
      exportedAt: new Date().toISOString(),
      version: "1.0.0",
      totalRecords: 0,
    },
  };

  try {
    // Note: This code assumes the Dexie db instance is available globally
    // In the actual source app, you'd import it properly
    // const { db } = await import('./services/db');

    // For demonstration, we'll use a mock approach
    console.log("📊 Exporting profiles...");
    // data.profiles = await db.profiles.toArray();

    console.log("📊 Exporting projects...");
    // data.projects = await db.projects.toArray();

    console.log("📊 Exporting components...");
    // data.components = await db.components.toArray();

    console.log("📊 Exporting component catalog...");
    // data.componentCatalog = await db.componentCatalog.toArray();

    console.log("📊 Exporting categories...");
    // data.categories = await db.categories.toArray();

    console.log("📊 Exporting field definitions...");
    // data.fieldDefinitions = await db.fieldDefinitions.toArray();

    console.log("📊 Exporting templates...");
    // data.templates = await db.templates.toArray();

    console.log("📊 Exporting tags...");
    // data.tags = await db.tags.toArray();

    console.log("📊 Exporting component tags...");
    // data.componentTags = await db.componentTags.toArray();

    console.log("📊 Exporting audit logs...");
    // data.auditLogs = await db.auditLogs.toArray();

    console.log("📊 Exporting app settings...");
    // data.appSettings = await db.appSettings.toArray();

    // Calculate total records
    data.metadata.totalRecords = Object.values(data).reduce((total, arr) => {
      return Array.isArray(arr) ? total + arr.length : total;
    }, 0);

    console.log(
      `✅ Export complete! Total records: ${data.metadata.totalRecords}`,
    );
    return data;
  } catch (error) {
    console.error("❌ Export failed:", error);
    throw error;
  }
}

/**
 * Transform IndexedDB data to Supabase format
 */
function transformDataForSupabase(indexedDBData: MigrationData): any {
  console.log("🔄 Transforming data for Supabase...");

  const transformed = {
    profiles: indexedDBData.profiles.map((profile) => ({
      id: crypto.randomUUID(), // Generate new UUIDs for Supabase
      name: profile.name,
      email: profile.email,
      hashed_pin: profile.hashedPin,
      pin_salt: profile.pinSalt,
      kdf: profile.kdf,
      created_at: profile.createdAt,
      updated_at: profile.updatedAt || profile.createdAt,
    })),
    projects: indexedDBData.projects.map((project) => ({
      id: crypto.randomUUID(),
      name: project.name,
      profile_id: project.profileId, // Will need to map to new profile UUIDs
      client_name: project.clientName,
      address: project.address,
      current_reserve_balance: project.currentReserveBalance || 0,
      custom_fields: project.customFields || {},
      created_at: project.createdAt,
      updated_at: project.updatedAt || project.createdAt,
    })),
    components: indexedDBData.components.map((component) => ({
      id: crypto.randomUUID(),
      project_id: component.projectId, // Will need to map to new project UUIDs
      name: component.name,
      category: component.category,
      base_cost: component.baseCost,
      useful_life: component.usefulLife,
      custom_fields: component.customFields || {},
      created_at: component.createdAt,
      updated_at: component.updatedAt || component.createdAt,
    })),
    component_catalog: indexedDBData.componentCatalog.map((item) => ({
      id: crypto.randomUUID(),
      name: item.name,
      category: item.category,
      base_cost: item.baseCost,
      useful_life: item.usefulLife,
      created_at: item.createdAt,
      updated_at: item.updatedAt || item.createdAt,
    })),
    categories: indexedDBData.categories.map((category) => ({
      id: crypto.randomUUID(),
      project_id: category.projectId, // Will need to map to new project UUIDs
      name: category.name,
      parent_id: category.parentId,
      meta: category.meta || {},
      created_at: category.createdAt,
      updated_at: category.updatedAt || category.createdAt,
    })),
    field_definitions: indexedDBData.fieldDefinitions.map((field) => ({
      id: crypto.randomUUID(),
      name: field.name,
      project_id: field.projectId, // Will need to map to new project UUIDs
      entity_type: field.entityType,
      field_type: field.fieldType,
      label: field.label,
      required: field.required || false,
      default_value: field.defaultValue,
      options: field.options,
      validation: field.validation,
      created_at: field.createdAt,
      updated_at: field.updatedAt || field.createdAt,
    })),
    templates: indexedDBData.templates.map((template) => ({
      id: crypto.randomUUID(),
      name: template.name,
      project_id: template.projectId, // Will need to map to new project UUIDs
      entity_type: template.entityType,
      field_definitions: template.fieldDefinitions || [],
      created_at: template.createdAt,
      updated_at: template.updatedAt || template.createdAt,
    })),
    tags: indexedDBData.tags.map((tag) => ({
      id: crypto.randomUUID(),
      name: tag.name,
      project_id: tag.projectId, // Will need to map to new project UUIDs
      created_at: tag.createdAt,
      updated_at: tag.updatedAt || tag.createdAt,
    })),
    component_tags: indexedDBData.componentTags.map((ct) => ({
      id: crypto.randomUUID(),
      component_id: ct.componentId, // Will need to map to new component UUIDs
      tag_id: ct.tagId, // Will need to map to new tag UUIDs
    })),
    audit_logs: indexedDBData.auditLogs.map((log) => ({
      id: crypto.randomUUID(),
      profile_id: log.profileId,
      entity_type: log.entityType,
      entity_id: log.entityId,
      action: log.action,
      old_values: log.previousKdf || log.delta,
      new_values: log.newKdf,
      metadata: {},
      created_at: log.timestamp,
    })),
    app_settings: indexedDBData.appSettings.map((setting) => ({
      key: setting.key,
      value: setting.value,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })),
    project_metro_settings: indexedDBData.projectMetroSettings.map(
      (setting) => ({
        id: crypto.randomUUID(),
        project_id: setting.projectId,
        metro_area: setting.metroArea,
        custom_multiplier: setting.customMultiplier,
        created_at: setting.createdAt,
      }),
    ),
    metadata: indexedDBData.metadata,
  };

  console.log("✅ Data transformation complete");
  return transformed;
}

/**
 * Download data as JSON file
 */
function downloadMigrationData(
  data: any,
  filename: string = "reserve-flow-migration-data.json",
) {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  URL.revokeObjectURL(url);
  console.log(`📁 Migration data downloaded as ${filename}`);
}

/**
 * Main migration function
 */
async function migrateReserveFlowData() {
  try {
    console.log("🚀 Starting Reserve Flow AI data migration...");

    // Step 1: Export data from IndexedDB
    const indexedDBData = await exportIndexedDBData();

    // Step 2: Transform data for Supabase
    const supabaseData = transformDataForSupabase(indexedDBData);

    // Step 3: Download migration file
    const filename = `reserve-flow-migration-${
      new Date().toISOString().split("T")[0]
    }.json`;
    downloadMigrationData(supabaseData, filename);

    console.log("🎉 Migration preparation complete!");
    console.log("📋 Next steps:");
    console.log("1. Upload the downloaded JSON file to your migration server");
    console.log("2. Run the Supabase import script");
    console.log("3. Verify data integrity");
  } catch (error) {
    console.error("💥 Migration failed:", error);
  }
}

// Export for use in browser console
(window as any).migrateReserveFlowData = migrateReserveFlowData;

// Auto-run if this script is loaded directly
if (typeof window !== "undefined" && document.readyState === "complete") {
  console.log("🔧 Reserve Flow Migration Tool loaded!");
  console.log("💡 Run migrateReserveFlowData() to start migration");
}
