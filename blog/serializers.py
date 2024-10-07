from rest_framework import serializers
from topics.models import BlogTopic
from django.db import transaction
from .models import Blog, Comment, BlogCommentReplies, BlogRead


class BlogListSerializer(serializers.ModelSerializer):
    # author_name = serializers.StringRelatedField(
    #     source='author.full_name',
    # )
    author_name =serializers.SerializerMethodField()
    group_name = serializers.StringRelatedField(
        source='group.title',
    )
    organization_name = serializers.StringRelatedField(
        source='organization.name',
    )
    category_name = serializers.StringRelatedField(
        source='category.name',
    )
    resources_url = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='media_url', source='resources'
    )

    class Meta:
        model = Blog
        fields = "__all__"
    
    def get_author_name(self,obj):
        return f"{obj.author.first_name} "

class BlogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            "id",
            "topic",
            "category",
            "content",
            "organization",
            "group",
            "resources",
            "score"
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        with transaction.atomic():
            resources_data = validated_data.pop('resources', [])

            topic_title = validated_data['topic']
            blog_topic, created = BlogTopic.objects.get_or_create(
                title=topic_title,
                defaults={
                    'blog': None,  # We'll update this after creating the Blog
                    'group': validated_data.get('group'),
                    'organization': validated_data.get('organization'),
                    'author': self.context['request'].user,
                }
            )

            blog = Blog.objects.create(**validated_data)

            # Update the BlogTopic with the new Blog
            if created:
                blog_topic.blog = blog
                blog_topic.save()
            else:
                pass
                

            blog.resources.set(resources_data)

            return {
                'blog': blog,
                'blog_topic': blog_topic,
                'blog_topic_created': created
            }


class CommentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = Comment
        fields = "__all__"


class BlogCommentReplySerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = BlogCommentReplies
        fields = "__all__"


class BlogReadListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogRead
        fields = ['id', 'user', 'blog', 'group', 'organization', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BlogReadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogRead
        fields = ['id', 'blog', 'group', 'organization']
        read_only_fields = ['id']