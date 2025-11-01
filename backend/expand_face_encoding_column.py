#!/usr/bin/env python3
"""
Migration script to expand face_encoding column from TEXT to LONGTEXT
This allows storage of 7 face encodings (~292KB) per user
"""

from app import create_app
from models import db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def expand_face_encoding_column():
    """Expand face_encoding column to handle large face encoding data"""
    try:
        app = create_app()
        with app.app_context():
            # Get database engine
            engine = db.engine
            
            logger.info("🔄 Starting face_encoding column expansion...")
            logger.info("=" * 80)
            
            # Check current column type
            logger.info("📋 Checking current column type...")
            with engine.connect() as connection:
                result = connection.execute(text("""
                    SELECT COLUMN_TYPE 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'gate_users' 
                    AND COLUMN_NAME = 'face_encoding'
                """))
                current_type = result.scalar()
                logger.info(f"Current column type: {current_type}")
            
            # Alter the column
            logger.info("\n🔧 Expanding face_encoding column to LONGTEXT...")
            with engine.begin() as connection:
                connection.execute(text("""
                    ALTER TABLE gate_users 
                    MODIFY COLUMN face_encoding LONGTEXT
                """))
                logger.info("✅ Column expanded successfully!")
            
            # Verify the change
            logger.info("\n✓ Verifying column change...")
            with engine.connect() as connection:
                result = connection.execute(text("""
                    SELECT COLUMN_TYPE 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'gate_users' 
                    AND COLUMN_NAME = 'face_encoding'
                """))
                new_type = result.scalar()
                logger.info(f"New column type: {new_type}")
            
            logger.info("\n" + "=" * 80)
            logger.info("✅ Migration completed successfully!")
            logger.info("\nDatabase column capacity:")
            logger.info("  - Old capacity (TEXT):     ~65KB")
            logger.info("  - New capacity (LONGTEXT): ~4GB")
            logger.info("  - Per user storage needed: ~292KB (7 encodings)")
            logger.info("=" * 80)
            
            return True
            
    except Exception as e:
        logger.error(f"\n❌ Error during migration: {e}")
        logger.error("Troubleshooting tips:")
        logger.error("  1. Ensure MySQL/MariaDB is running")
        logger.error("  2. Check database connection credentials in .env")
        logger.error("  3. Verify gate_users table exists")
        logger.error("  4. Check that your database user has ALTER permissions")
        return False

if __name__ == '__main__':
    success = expand_face_encoding_column()
    exit(0 if success else 1)