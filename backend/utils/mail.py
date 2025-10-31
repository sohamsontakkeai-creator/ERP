import os
from mailersend import emails

def send_mailersend_email(from_email, to_email, subject, html_content, text_content=None):
    """
    Send an email using MailerSend API.
    Works both for user emails and fixed admin-only delivery.
    """
    try:
        api_key = os.environ.get('MAILERSEND_API_KEY')
        if not api_key:
            raise ValueError("MAILERSEND_API_KEY not set in environment variables.")

        mailer = emails.NewEmail(api_key)

        # ✅ Ensure the 'to_email' is always a list of recipients
        if isinstance(to_email, str):
            to_email = [to_email]

        # ✅ Build mail body correctly
        mail_body = {
            "from": {"email": from_email, "name": "ERP Support"},
            "to": [{"email": addr} for addr in to_email],
            "subject": subject,
            "html": html_content,
            "text": text_content or html_content,
        }

        # ✅ Send email
        response = mailer.send(mail_body)
        print(f"✅ Email sent successfully to {to_email}, response: {response}")
        return True

    except Exception as e:
        print(f"❌ Failed to send MailerSend email: {e}")
        return False
