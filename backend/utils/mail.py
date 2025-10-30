import os
from mailersend import emails

def send_mailersend_email(from_email, to_email, subject, html_content, text_content=None):
    try:
        mailer = emails.NewEmail(os.environ.get('MAILERSEND_API_KEY'))

        # ✅ Build message manually as a dict
        mail_body = {
            "from": {"email": from_email, "name": "ERP Support"},
            "to": [{"email": to_email}],
            "subject": subject,
            "html": html_content,
            "text": text_content or html_content
        }

        # ✅ Send the email directly
        response = mailer.send(mail_body)

        print(f"✅ Email sent successfully to {to_email}, response: {response}")
        return True

    except Exception as e:
        print(f"❌ Failed to send MailerSend email: {e}")
        return False
