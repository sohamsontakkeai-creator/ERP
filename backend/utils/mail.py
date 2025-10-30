import os
from mailersend import emails

def send_mailersend_email(from_email, to_email, subject, html_content, text_content=None):
    try:
        # Initialize client
        mailer = emails.NewEmail(os.environ.get('MAILERSEND_API_KEY'))

        # Set up the "from" field
        mailer.set_mail_from(from_email)

        # Set up the "to" field
        mailer.set_mail_to([to_email])

        # Set the subject
        mailer.set_subject(subject)

        # Set the message content
        mailer.set_html_content(html_content)
        mailer.set_plaintext_content(text_content or html_content)

        # Optional: add reply-to if needed
        # mailer.set_mail_reply_to('reply@yourdomain.com')

        # Send the email
        response = mailer.send()

        print(f"✅ Email sent to {to_email}, response: {response}")
        return True

    except Exception as e:
        print(f"❌ Failed to send MailerSend email: {e}")
        return False
