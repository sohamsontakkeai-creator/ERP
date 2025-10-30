import os
from mailersend import emails

def send_mailersend_email(from_email, to_email, subject, html_content, text_content=None):
    try:
        # Initialize the MailerSend client
        mailer = emails.NewEmail(os.environ.get('MAILERSEND_API_KEY'))

        # ✅ Create a dictionary object — this is the message container
        mail_body = {}

        # ✅ Use MailerSend's setter functions (they modify the dict)
        mailer.set_mail_from(mail_body, {"email": from_email, "name": "ERP Support"})
        mailer.set_mail_to(mail_body, [{"email": to_email}])
        mailer.set_subject(mail_body, subject)
        mailer.set_html_content(mail_body, html_content)
        mailer.set_plaintext_content(mail_body, text_content or html_content)

        # ✅ Send the email
        response = mailer.send(mail_body)
        print(f"✅ Email sent to {to_email}, response: {response}")
        return True

    except Exception as e:
        print(f"❌ Failed to send MailerSend email: {e}")
        return False
