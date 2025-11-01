"""
Migration script to add manager approval workflow to the Leave table
This script adds the necessary columns to support the new two-stage approval process:
- Manager approval (first stage)
- HR approval (final stage)
"""
import os
import sys
from sqlalchemy import text, inspect

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db

def migrate_leave_table():
    """Add manager approval columns to leaves table"""
    
    try:
        app = create_app()
        with app.app_context():
            with db.engine.begin() as connection:
                inspector = inspect(db.engine)
                columns = {col['name'] for col in inspector.get_columns('leaves')}
                
                print("Current columns in leaves table:", columns)
                
                # Check and add manager_id column
                if 'manager_id' not in columns:
                    print("Adding manager_id column...")
                    connection.execute(text(
                        'ALTER TABLE leaves ADD COLUMN manager_id INTEGER REFERENCES employees(id)'
                    ))
                    print("✓ manager_id column added")
                else:
                    print("✓ manager_id column already exists")
                
                # Check and add manager_status column
                if 'manager_status' not in columns:
                    print("Adding manager_status column...")
                    connection.execute(text(
                        "ALTER TABLE leaves ADD COLUMN manager_status VARCHAR(20) DEFAULT 'PENDING'"
                    ))
                    print("✓ manager_status column added")
                else:
                    print("✓ manager_status column already exists")
                
                # Check and add manager_approved_at column
                if 'manager_approved_at' not in columns:
                    print("Adding manager_approved_at column...")
                    connection.execute(text(
                        'ALTER TABLE leaves ADD COLUMN manager_approved_at TIMESTAMP'
                    ))
                    print("✓ manager_approved_at column added")
                else:
                    print("✓ manager_approved_at column already exists")
                
                # Check and add manager_rejection_reason column
                if 'manager_rejection_reason' not in columns:
                    print("Adding manager_rejection_reason column...")
                    connection.execute(text(
                        'ALTER TABLE leaves ADD COLUMN manager_rejection_reason TEXT'
                    ))
                    print("✓ manager_rejection_reason column added")
                else:
                    print("✓ manager_rejection_reason column already exists")
                
                # Check and add hr_rejection_reason column
                if 'hr_rejection_reason' not in columns:
                    print("Adding hr_rejection_reason column...")
                    connection.execute(text(
                        'ALTER TABLE leaves ADD COLUMN hr_rejection_reason TEXT'
                    ))
                    print("✓ hr_rejection_reason column added")
                else:
                    print("✓ hr_rejection_reason column already exists")
                
                # Check and add approval_stage column
                if 'approval_stage' not in columns:
                    print("Adding approval_stage column...")
                    connection.execute(text(
                        "ALTER TABLE leaves ADD COLUMN approval_stage VARCHAR(50) DEFAULT 'manager_review'"
                    ))
                    print("✓ approval_stage column added")
                else:
                    print("✓ approval_stage column already exists")
                
                print("\n✓ Migration completed successfully!")
                print("\nNew Leave Approval Workflow:")
                print("1. Employee creates leave request (status: PENDING, stage: manager_review)")
                print("2. Manager approves (stage: hr_review) or rejects (stage: rejected)")
                print("3. HR approves (stage: approved) or rejects (stage: rejected)")
                
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Leave Manager Approval Workflow Migration")
    print("=" * 60)
    success = migrate_leave_table()
    sys.exit(0 if success else 1)