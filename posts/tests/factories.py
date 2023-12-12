import factory
from posts.models import Post


class PostFactroy(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
