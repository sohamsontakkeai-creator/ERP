"""
Fix trailing whitespace in designation column
"""
from config import config
from models import db
from models.hr import Employee
from flask import Flask

app = Flask(__name__)
app.config.from_object(config['default'])
db.init_app(app)

def fix_designations():
    """Trim whitespace from all designations"""
    with app.app_context():
        print('🔄 Fixing designation whitespace...')
        
        # Find all employees with designations
        employees = Employee.query.all()
        fixed_count = 0
        
        for emp in employees:
            if emp.designation:
                original = emp.designation
                trimmed = original.strip()
                
                if original != trimmed:
                    emp.designation = trimmed
                    fixed_count += 1
                    print(f"  ✓ {emp.first_name} {emp.last_name}: '{original}' → '{trimmed}'")
        
        if fixed_count > 0:
            db.session.commit()
            print(f'\n✅ Fixed {fixed_count} employee designation(s)')
        else:
            print('\n✅ No designations needed fixing')

if __name__ == '__main__':
    fix_designations()