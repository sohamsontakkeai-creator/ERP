from mailersend import emails
import os

def test_mailersend():
    mailer = emails.NewEmail(os.getenv("MAILERSEND_API_KEY"))

    mail_body = {
        "from": {
            "email": os.getenv("MAILERSEND_FROM_EMAIL"),
            "name": "Alankar ERP"
        },
        "to": [{"email": "sohamsontakke.spotify@gmail.com"}],
        "subject": "MailerSend Test Email",
        "text": "This is a test email from MailerSend API integration."
    }

    response = mailer.send(mail_body)
    print("✅ MailerSend response:", response)

if __name__ == "__main__":
    test_mailersend()
