import os
from mailersend import emails

def send_mailersend_email(from_email, to_email, subject, html_content, text_content=None):
    """
    Send an email using MailerSend v2.
    """
    try:
        client = emails.Client(api_key=os.environ.get('MAILERSEND_API_KEY'))

        # Construct email payload
        email_data = {
            "from": {
                "email": from_email,
                "name": "ERP Support"
            },
            "to": [
                {"email": to_email}
            ],
            "subject": subject,
            "html": html_content,
            "text": text_content or html_content
        }

        response = client.send(email_data)
        print(f"✅ Email sent to {to_email}, response: {response}")
        return True

    except Exception as e:
        print(f"❌ Failed to send MailerSend email: {e}")
        return False
