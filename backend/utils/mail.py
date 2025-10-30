from mailersend import emails
import os

def send_mailersend_email(from_email, to_email, subject, html_content, text_content=None):
    try:
        mailer = emails.NewEmail(os.environ.get('MAILERSEND_API_KEY'))

        mail_from = {
            "email": from_email,
            "name": "ERP Support"
        }

        recipients = [{"email": to_email}]

        response = mailer.send(
            mail_from=mail_from,
            to=recipients,
            subject=subject,
            html_body=html_content,
            text_body=text_content or html_content
        )

        print(f"✅ Email sent to {to_email}, response: {response}")
        return True

    except Exception as e:
        print(f"❌ Failed to send MailerSend email: {e}")
        return False
