import os
from mailersend import emails

def send_mailersend_email(from_email, to_email, subject, html_content, text_content=None):
    try:
        # Initialize the MailerSend client
        mailer = emails.NewEmail(os.environ.get('MAILERSEND_API_KEY'))

        # ✅ Create the message as a dictionary
        mail_body = {
            "from": {"email": from_email, "name": "ERP Support"},
            "to": [{"email": to_email}],
            "subject": subject,
            "html": html_content,
            "text": text_content or html_content
        }

        # ✅ Use setter methods to populate data properly
        mailer.set_mail_from(mail_body, mail_body["from"])
        mailer.set_mail_to(mail_body, mail_body["to"])
        mailer.set_subject(mail_body, mail_body["subject"])
        mailer.set_html_content(mail_body, mail_body["html"])
        mailer.set_plaintext_content(mail_body, mail_body["text"])

        # ✅ Send the email
        response = mailer.send(mail_body)

        print(f"✅ Email sent successfully to {to_email}, response: {response}")
        return True

    except Exception as e:
        print(f"❌ Failed to send MailerSend email: {e}")
        return False
