#!/usr/bin/env python3
"""
Migration script to create sales_target table for tracking monthly sales targets
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from config import config as app_config

# Load environment variables
load_dotenv()

# Pick config (same as app's create_app)
CONFIG_NAME = os.getenv('FLASK_CONFIG', 'default')
FlaskConfig = app_config[CONFIG_NAME]
SQLALCHEMY_DATABASE_URI = FlaskConfig.SQLALCHEMY_DATABASE_URI

# Create database connection
engine = create_engine(SQLALCHEMY_DATABASE_URI)

def create_sales_target_table():
    """Create sales_target table for tracking monthly targets"""
    
    create_sales_target_table_sql = """
    CREATE TABLE IF NOT EXISTS sales_target (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sales_person VARCHAR(100) NOT NULL,
        year INT NOT NULL,
        month INT NOT NULL COMMENT '1-12',
        target_amount FLOAT NOT NULL COMMENT 'Monthly target amount',
        assignment_type VARCHAR(50) DEFAULT 'manual' COMMENT 'manual, formula, historical',
        assigned_by VARCHAR(100),
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uq_sales_target (sales_person, year, month),
        INDEX idx_sales_person (sales_person),
        INDEX idx_year_month (year, month)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    
    try:
        with engine.connect() as connection:
            print("Creating sales_target table...")
            connection.execute(text(create_sales_target_table_sql))
            connection.commit()
            
            print("✅ Sales target table created successfully!")
            print("\nTable structure:")
            print("- id: Primary key (auto-increment)")
            print("- sales_person: Name of the salesperson")
            print("- year: Year for the target")
            print("- month: Month (1-12)")
            print("- target_amount: Target amount for the month")
            print("- assignment_type: How the target was assigned (manual, formula, historical)")
            print("- assigned_by: Admin or user who assigned the target")
            print("- notes: Additional notes about the target")
            print("- created_at: Timestamp of creation")
            print("- updated_at: Timestamp of last update")
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_sales_target_table()