import os
from mailersend import MailerSendClient, EmailBuilder

def send_mailersend_email(from_email, to_email, subject, html_content, text_content=None):
    try:
        client = MailerSendClient(api_key=os.environ.get('MAILERSEND_API_KEY'))

        email = (EmailBuilder()
                 .from_email(from_email, "ERP Support")  # Sender name optional
                 .to_many([{"email": to_email}])
                 .subject(subject)
                 .html(html_content)
                 .text(text_content or html_content)
                 .build())

        response = client.emails.send(email)
        print(f"✅ Email sent to {to_email}, response: {response.status_code} {response.body}")
        return True
    except Exception as e:
        print(f"❌ Failed to send MailerSend email: {e}")
        return False
