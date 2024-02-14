from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template

# Todo , add task delay using redis or any other message broker


def send_email_with_content(subject, content, reciever):
    sender = settings.EMAIL_HOST_USER
    send_mail(
        subject=subject,
        message='',
        from_email=sender,
        recipient_list=[reciever],
        fail_silently=False,
        html_message=content,
    )


def send_account_verification_mail(email_data):
    html_template = get_template('emails/account_verification.html')
    html_alternative = html_template.render(email_data)
    subject = "Account Verification"
    reciever = email_data['email']

    send_email_with_content(subject, html_alternative, reciever)




def send_password_reset_mail(email_data):
    html_template = get_template('emails/password_reset.html')
    html_alternative = html_template.render(email_data)
    subject = "Pasword Reset"
    reciever = email_data['email']

    send_email_with_content(subject, html_alternative, reciever)
