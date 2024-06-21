import factory
from accounts.models import User
from faker import Faker

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: "person{}@example.com".format(n))
    phone = factory.Sequence(lambda n: "+234801234567{}".format(n))
    password = factory.PostGenerationMethodCall("set_password", "passer@@@111")
    username = fake.name()
    first_name = fake.name()
    last_name = fake.name()
    
