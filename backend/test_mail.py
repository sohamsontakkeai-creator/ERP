from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# Initialize Flask-Mail
mail = Mail(app)

def test_email():
    try:
        print("Mail settings:")
        print(f"Server: {app.config['MAIL_SERVER']}")
        print(f"Port: {app.config['MAIL_PORT']}")
        print(f"Username: {app.config['MAIL_USERNAME']}")
        print(f"TLS: {app.config['MAIL_USE_TLS']}")
        print(f"SSL: {app.config['MAIL_USE_SSL']}")
        
        msg = Message(
            'Test Email',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[app.config['MAIL_USERNAME']]  # Sending to self for testing
        )
        msg.body = 'This is a test email to verify SMTP configuration'
        mail.send(msg)
        print("Test email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == '__main__':
    with app.app_context():
        test_email()