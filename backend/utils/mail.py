import os
from mailersend import emails

def send_mailersend_email(from_email, to_email, subject, html_content, text_content=None):
    """
    Sends an email via MailerSend
    """
    try:
        client = emails.Client(api_key=os.environ.get('MAILERSEND_API_KEY'))
        response = client.send(
            sender=from_email,
            recipients=[to_email],
            subject=subject,
            html=html_content,
            text=text_content or html_content
        )
        print(f"✅ Email sent to {to_email}, response: {response}")
        return True
    except Exception as e:
        print(f"❌ Failed to send MailerSend email: {e}")
        return False
