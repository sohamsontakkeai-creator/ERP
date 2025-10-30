import os
from mailersend import emails

def send_mailersend_email(from_email, to_email, subject, html_content, text_content=None):
    try:
        # Initialize client
        mailer = emails.NewEmail(os.environ.get('MAILERSEND_API_KEY'))

        # Create message object
        mail_body = {}

        # Set required fields
        mailer.set_mail_from(mail_body, from_email)
        mailer.set_mail_to(mail_body, [to_email])
        mailer.set_subject(mail_body, subject)
        mailer.set_html_content(mail_body, html_content)
        mailer.set_plaintext_content(mail_body, text_content or html_content)

        # (Optional) Add reply-to or personalization
        # mailer.set_mail_reply_to(mail_body, "support@yourdomain.com")

        # Send the email
        response = mailer.send(mail_body)

        print(f"✅ Email sent to {to_email}, response: {response}")
        return True

    except Exception as e:
        print(f"❌ Failed to send MailerSend email: {e}")
        return False
