import factory
from group.models import Group


class GroupFactroy(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
