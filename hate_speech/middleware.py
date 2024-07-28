from django.utils import timezone
from datetime import timedelta
from .utils import add_related_terms



class UpdateRelatedTermsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_run = timezone.now() - timedelta(days=8)  #timedelta(minutes=3) # Initialize to more than 7 days ago

    def __call__(self, request):
        # print("middleware called: ", timezone.now())
        # Run the update function if 7 days have passed since the last run
        if timezone.now() - self.last_run >=  timedelta(days=7): #timedelta(minutes=2): 
            # print("time to add: ", timezone.now())
            add_related_terms()
            self.last_run = timezone.now()

        response = self.get_response(request)
        return response
