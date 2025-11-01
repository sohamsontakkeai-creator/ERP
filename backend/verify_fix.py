"""
Verify the designation whitespace fix
"""
from config import config
from models import db
from services.hr_service import HRService
from flask import Flask
import json

app = Flask(__name__)
app.config.from_object(config['default'])
db.init_app(app)

with app.app_context():
    email = 'wsdsdad@jsfsf'
    print(f'Testing HRService.get_employee_by_email for: {email}')
    
    employee = HRService.get_employee_by_email(email)
    if employee:
        print(json.dumps(employee, indent=2))
        
        # Verify the comparison works now
        if employee['designation'].lower() == 'manager':
            print('\n✅ Designation comparison works correctly!')
        else:
            print(f'\n❌ Designation mismatch. Got: "{employee["designation"]}"')
    else:
        print('No employee found')