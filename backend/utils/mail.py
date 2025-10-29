import os
from mailersend import MailerSendClient, EmailBuilder

def send_mailersend_email(from_email, to_email, subject, html_content, text_content=None):
    try:
        client = MailerSendClient(api_key=os.environ.get('MAILERSEND_API_KEY'))

        email = EmailBuilder()
        email.set_from(from_email)
        email.set_to(to_email)
        email.set_subject(subject)
        email.set_html(html_content)
        email.set_text(text_content or html_content)

        response = client.send(email)
        print(f"✅ Email sent to {to_email}, response: {response}")
        return True
    except Exception as e:
        print(f"❌ Failed to send MailerSend email: {e}")
        return False
