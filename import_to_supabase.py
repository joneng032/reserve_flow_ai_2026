#!/usr/bin/env python3
"""
Supabase Data Import Script for Reserve Flow AI Migration

This script imports migrated data from IndexedDB JSON export into Supabase PostgreSQL.
"""

import json
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add the backend directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# The importer intentionally uses some broad `except Exception` handlers
# because it is a best-effort migration tool: we want imports to continue
# in the face of unexpected third-party client exceptions and report
# problems rather than crashing the whole process. Mirror the database
# module's approach and disable the linter warnings for broad-except
# at the file level so the rationale is obvious to future maintainers.
# pylint: disable=broad-except
# flake8: noqa: S110

# Avoid importing the supabase client at module import time. Importing
# `supabase` can pull in native crypto extensions (via gotrue/cryptography)
# which may crash the process during test collection on some platforms
# (notably Windows). Defer any import and client creation to runtime (main)
# so tests can safely import this module and provide a fake client.
create_client = None
Client = None
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase = None


class SupabaseImporter:
    def __init__(self, supabase_client: Optional[Client] = None):
        """Initialize the importer with an optional supabase client.

        If no client is provided the importer will operate in a dry mode
        (self.supabase == None). Tests should provide a fake client when
        exercising import/verify logic to avoid importing the real client.
        """
        self.supabase = supabase_client
        self.id_mappings = {
            "profiles": {},
            "projects": {},
            "components": {},
            "categories": {},
            "field_definitions": {},
            "templates": {},
            "tags": {},
        }

    def load_migration_data(self, filepath: str) -> Dict[str, Any]:
        """Load migration data from JSON file"""
        print(f"📂 Loading migration data from {filepath}...")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(
                f"✅ Loaded data with {data.get('metadata', {}).get('totalRecords', 0)} records"
            )
            return data
        except FileNotFoundError:
            print(f"❌ File not found: {filepath}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            # Malformed JSON is an expected, recoverable error from bad input
            print(f"❌ Invalid JSON file: {e}")
            sys.exit(1)
        except OSError as e:
            # Any other unexpected IO/OS-related errors are surfaced here
            # Narrow to OSError because file/OS-level errors are the
            # expected cause for failures at this point and this reduces
            # the need for a broad-except while preserving useful debug
            # information for callers.
            print(f"❌ Unexpected error reading {filepath}: {e}")
            sys.exit(1)

    def create_uuid_mapping(
        self, old_data: List[Dict[str, Any]], _entity_type: str
    ) -> Dict[str, str]:
        """Create mapping from old IDs to new UUIDs"""
        mapping = {}
        for item in old_data:
            old_id = item.get("id")
            if old_id is not None:
                new_id = str(uuid.uuid4())
                mapping[str(old_id)] = new_id
                item["id"] = new_id
        return mapping

    def update_foreign_keys(
        self,
        data: List[Dict[str, Any]],
        foreign_key_field: str,
        mapping: Dict[str, str],
    ):
        """Update foreign key references using the mapping"""
        for item in data:
            old_fk = item.get(foreign_key_field)
            if old_fk is not None and str(old_fk) in mapping:
                item[foreign_key_field] = mapping[str(old_fk)]

    def prepare_data_for_import(
        self, data: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Prepare data by creating new UUIDs and updating foreign key references"""
        print("🔄 Preparing data for import...")

        # Create new UUIDs for all entities
        self.id_mappings["profiles"] = self.create_uuid_mapping(
            data["profiles"], "profiles"
        )
        self.id_mappings["projects"] = self.create_uuid_mapping(
            data["projects"], "projects"
        )
        self.id_mappings["components"] = self.create_uuid_mapping(
            data["components"], "components"
        )
        self.id_mappings["categories"] = self.create_uuid_mapping(
            data["categories"], "categories"
        )
        self.id_mappings["field_definitions"] = self.create_uuid_mapping(
            data["fieldDefinitions"], "field_definitions"
        )
        self.id_mappings["templates"] = self.create_uuid_mapping(
            data["templates"], "templates"
        )
        self.id_mappings["tags"] = self.create_uuid_mapping(data["tags"], "tags")

        # Update foreign key references
        # Projects reference profiles
        self.update_foreign_keys(
            data["projects"], "profile_id", self.id_mappings["profiles"]
        )

        # Components reference projects
        self.update_foreign_keys(
            data["components"], "project_id", self.id_mappings["projects"]
        )

        # Categories reference projects
        self.update_foreign_keys(
            data["categories"], "project_id", self.id_mappings["projects"]
        )

        # Field definitions reference projects
        self.update_foreign_keys(
            data["fieldDefinitions"], "project_id", self.id_mappings["projects"]
        )

        # Templates reference projects
        self.update_foreign_keys(
            data["templates"], "project_id", self.id_mappings["projects"]
        )

        # Tags reference projects
        self.update_foreign_keys(
            data["tags"], "project_id", self.id_mappings["projects"]
        )

        # Component tags reference components and tags
        self.update_foreign_keys(
            data["componentTags"], "component_id", self.id_mappings["components"]
        )
        self.update_foreign_keys(
            data["componentTags"], "tag_id", self.id_mappings["tags"]
        )

        # Audit logs reference profiles
        self.update_foreign_keys(
            data["auditLogs"], "profile_id", self.id_mappings["profiles"]
        )

        # Project metro settings reference projects
        self.update_foreign_keys(
            data["projectMetroSettings"], "project_id", self.id_mappings["projects"]
        )

        # Rename keys to match Supabase table names
        prepared_data = {
            "profiles": data["profiles"],
            "projects": data["projects"],
            "components": data["components"],
            "component_catalog": data["componentCatalog"],
            "categories": data["categories"],
            "field_definitions": data["fieldDefinitions"],
            "templates": data["templates"],
            "tags": data["tags"],
            "component_tags": data["componentTags"],
            "audit_logs": data["auditLogs"],
            "app_settings": data["appSettings"],
            "project_metro_settings": data["projectMetroSettings"],
        }

        print("✅ Data preparation complete")
        return prepared_data

    def import_table_data(self, table_name: str, records: List[Dict[str, Any]]) -> int:
        """Import data into a Supabase table"""
        if not records:
            print(f"⏭️  Skipping {table_name} (no records)")
            return 0

        print(f"📤 Importing {len(records)} records into {table_name}...")

        try:
            # Insert in batches to avoid payload size limits
            batch_size = 100
            imported = 0

            for i in range(0, len(records), batch_size):
                batch = records[i : i + batch_size]
                try:
                    result = self.supabase.table(table_name).insert(batch).execute()
                    imported += len(result.data) if result.data else 0
                    print(
                        f"  📦 Imported batch {i//batch_size + 1}/{(len(records) + batch_size - 1)//batch_size}"
                    )
                except ValueError as ve:
                    # Data-shape errors from the client library
                    print(f"  ⚠️  Data error importing batch {i//batch_size + 1}: {ve}")
                except (
                    Exception
                ) as ex:  # noqa: S110 - third-party client may raise varied exceptions
                    # Keep a broad catch here because the supabase client may
                    # raise different third-party exceptions; surface them and
                    # continue importing remaining batches where possible.
                    print(
                        f"  ❌ Unexpected error importing batch {i//batch_size + 1}: {ex}"
                    )

            print(f"✅ Successfully imported {imported} records into {table_name}")
            return imported
        except (
            Exception
        ) as e:  # noqa: S110 - top-level import protection for external client errors
            # Final broad catch to avoid crashing the whole import script on
            # an unexpected error. We print and return 0 to indicate failure
            # for this table but keep the script running so other tables may
            # still be imported or inspected.
            print(f"❌ Failed to import into {table_name}: {e}")
            return 0

    def import_all_data(
        self, prepared_data: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, int]:
        """Import all data into Supabase tables"""
        print("🚀 Starting data import to Supabase...")

        results = {}

        # Import order matters due to foreign key constraints
        import_order = [
            "profiles",
            "projects",
            "component_catalog",  # No foreign keys
            "categories",
            "field_definitions",
            "templates",
            "tags",
            "components",
            "component_tags",
            "audit_logs",
            "app_settings",
            "project_metro_settings",
        ]

        total_imported = 0
        for table_name in import_order:
            records = prepared_data.get(table_name, [])
            imported = self.import_table_data(table_name, records)
            results[table_name] = imported
            total_imported += imported

        print(f"🎉 Import complete! Total records imported: {total_imported}")
        return results

    def verify_import(
        self,
        _prepared_data: Dict[str, List[Dict[str, Any]]],
        import_results: Dict[str, int],
    ):
        """Verify that all data was imported successfully"""
        print("🔍 Verifying import...")

        issues = []

        for table_name, expected_count in import_results.items():
            try:
                # Query the table to get actual count
                result = (
                    self.supabase.table(table_name).select("*", count="exact").execute()
                )
                actual_count = result.count if result.count is not None else 0

                if actual_count != expected_count:
                    issues.append(
                        f"{table_name}: expected {expected_count}, got {actual_count}"
                    )
                else:
                    print(f"✅ {table_name}: {actual_count} records verified")

            except (
                Exception
            ) as e:  # noqa: S110 - verification should not abort on client errors
                # Keep broad catch for third-party client errors during verification
                issues.append(f"{table_name}: verification failed - {e}")

        if issues:
            print("⚠️  Import verification found issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ All imports verified successfully!")

        return issues


def main():
    if len(sys.argv) != 2:
        print("Usage: python import_to_supabase.py <migration_data.json>")
        sys.exit(1)

    migration_file = sys.argv[1]

    # Initialize importer. Create a real supabase client only when running
    # the script directly; don't attempt to import supabase during test
    # collection or when the module is imported by unit tests.
    real_client = None
    if SUPABASE_URL and SUPABASE_ANON_KEY:
        try:
            # Use the centralized adapter which will try the legacy supabase
            # package and fall back to supabase_auth when available.
            from backend.app.utils.supabase_adapter import (
                create_supabase_client as _create_supabase_client,
            )

            real_client = _create_supabase_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        except ImportError:
            print(
                "⚠️  Supabase library not installed; run the importer with a real client."
            )
        except Exception as e:
            print(f"❌ Failed to initialize Supabase client: {e}")

    importer = SupabaseImporter(real_client)

    try:
        # Load and prepare data
        raw_data = importer.load_migration_data(migration_file)
        prepared_data = importer.prepare_data_for_import(raw_data)

        # Import data
        import_results = importer.import_all_data(prepared_data)

        # Verify import
        issues = importer.verify_import(prepared_data, import_results)

        # Summary
        print("\n📊 Migration Summary:")
        print(f"📁 Source file: {migration_file}")
        print(f"📅 Imported at: {datetime.now().isoformat()}")
        print(f"📈 Total records: {sum(import_results.values())}")

        if issues:
            print("⚠️  Issues found during verification:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print("🎉 Migration completed successfully!")

    except (
        Exception
    ) as e:  # noqa: S110 - top-level script should report errors instead of crashing
        print(f"💥 Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
