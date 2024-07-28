import json, os
from datetime import datetime
from django.core.exceptions import ValidationError
from pathlib import Path
from celery import shared_task
from .models import BadWord
from django.conf import settings

#!!!!! NOTE TO SELF, take care of duplicates b4 adding new_terms to related_terms

def add_related_terms():
    try:
        with open(os.path.join(settings.BASE_DIR, 'hate_speech/new_terms.json'), 'r') as file:
            if file:
                data = json.load(file)
                new_terms = data.get('new_terms', [])
            else:
                print("cant find file")
                raise FileNotFoundError("No json file found.")

            if not isinstance(new_terms, list):
                raise ValueError('new_terms must be a list')
            
        badword_instance = BadWord.objects.first()
            
        if not badword_instance:
            badword_instance = BadWord.objects.create(related_terms=[])
            # print("No BadWord instance to work with!")
            # raise ValidationError("No BadWord instance found.")

        existing_terms = badword_instance.related_terms or []

        terms_to_add = [term for term in new_terms if term not in existing_terms]


        if terms_to_add:
            if existing_terms:
                existing_terms.extend(terms_to_add)
            else:
                existing_terms = terms_to_add
            
            badword_instance.related_terms = existing_terms
            badword_instance.save()
            send_success_email(terms_to_add)

    except Exception as e:
        send_error_email(str(e))


def send_error_email(error_message):
    from django.core.mail import send_mail
    sender = settings.EMAIL_HOST_USER
    send_mail(
        'Hate Speech Library Weekly Update',
        f'The following error occurred: {error_message}',
        sender,
        ['brasheed240@gmail.com'],
        fail_silently=True,
    )

def send_success_email(terms_to_add):
    from django.core.mail import send_mail
    sender = settings.EMAIL_HOST_USER
    send_mail(
        'Hate Speech Library Weekly Update',
        f'The following words were added succesfully added to the library: {terms_to_add}',
        sender,
        ['brasheed240@gmail.com'],
        fail_silently=True,
    )