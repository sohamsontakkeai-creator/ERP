from models.hr import Employee
from utils.database import db
from app import app

with app.app_context():
    # Find employees with 'logan' in the name
    employees = Employee.query.filter(Employee.first_name.ilike('%logan%')).all()
    if not employees:
        employees = Employee.query.filter(Employee.last_name.ilike('%logan%')).all()
    
    if not employees:
        print("No employees found with 'logan' in name")
    else:
        for emp in employees:
            print(f'Name: {emp.first_name} {emp.last_name}')
            print(f'Email: {emp.email}')
            print(f'Department: {emp.department}')
            print(f'Designation: {emp.designation}')
            print('---')