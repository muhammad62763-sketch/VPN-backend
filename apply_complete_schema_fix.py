#!/usr/bin/env python3
"""
Apply complete schema fix migration
Adds all missing tables and columns referenced in the codebase
"""
import asyncio
import asyncpg
from app.config import settings

async def apply_migration():
    print("🔧 Applying Complete Schema Fix Migration...")
    print("=" * 80)
    
    # Connect to database
    url = settings.NEON_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(dsn=url, ssl="require")
    
    try:
        # Read migration file with UTF-8 encoding
        with open("database/migrations/003_complete_schema_fix.sql", "r", encoding="utf-8") as f:
            migration_sql = f.read()
        
        print("📄 Executing migration SQL...")
        await conn.execute(migration_sql)
        
        print("✅ Migration completed successfully!")
        print("=" * 80)
        
        # Verify tables
        print("\n📊 Verifying database schema...")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        print(f"\n✅ Total tables: {len(tables)}")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        # Verify users table columns
        print("\n📋 Users table columns:")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"   - {col['column_name']}: {col['data_type']} {nullable}")
        
        print("\n" + "=" * 80)
        print("✅ Schema verification complete!")
        print("🚀 Your database is now ready for production!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(apply_migration())
