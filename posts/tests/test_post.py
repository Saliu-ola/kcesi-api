import pytest
from django.urls import reverse
from .factories import PostFactroy
from accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

POST_LIST_URL = "post:post-list"
POST_DETAIL_URL = "post:post-detail"
CURRENT_USER_POST_URL = "post:post-get-post-for-current-user"


class TestDevice:
    def test_list_all_posts(self, api_client, mocked_authentication):
        """Test list all posts"""
        user = UserFactory(is_verified=True)
        PostFactroy.create_batch(3, author=user)
        mocked_authentication(verified_user=user)
        url = reverse(POST_LIST_URL)
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.json()["total"] == 3

    def test_create_post(self, api_client, mocked_authentication):
        """Test create post"""
        user = UserFactory(is_verified=True, organization_id='KOR-123444')
        mocked_authentication(verified_user=user)
        url = reverse(POST_LIST_URL)
        payload = {"title": "some title", "content": "Loren ipsinmsn enjjenndd"}
        response = api_client.post(url, data=payload)
        assert response.status_code == 201
        assert response.data["title"] == payload["title"]
        assert response.data["content"] == payload["content"]
        assert response.data["author"] == user.id

    def test_get_post(self, api_client, mocked_authentication):
        """Test retrieve a posts"""
        user = UserFactory(is_verified=True)
        post = PostFactroy(author=user)
        mocked_authentication(verified_user=user)
        url = reverse(POST_DETAIL_URL, kwargs={"pk": post.id})
        response = api_client.get(url)
        print(response.data)
        assert response.status_code == 200
        assert response.data["title"] == post.title
        assert response.data["content"] == post.content
        assert response.data["author"] == user.id

    @pytest.mark.parametrize("method_name", ['patch', 'put'])
    def test_update_post(self, api_client, method_name, mocked_authentication):
        """Test updating a post"""
        user = UserFactory(is_verified=True)
        post = PostFactroy(author=user, title="Old title", content="Old content")
        mocked_authentication(verified_user=user)
        payload = {"title": "new title", "content": "new content"}
        url = reverse(POST_DETAIL_URL, kwargs={"pk": post.id})
        response = getattr(api_client, method_name)(url, data=payload)
        post.refresh_from_db()
        assert response.status_code == 200
        assert response.json()['title'] == payload['title']
        assert post.title == payload['title']
        assert post.content == payload['content']

    def test_delete_post(self, api_client, mocked_authentication):
        """Test deleting of a post"""
        user = UserFactory(is_verified=True)
        post = PostFactroy(author=user)
        mocked_authentication(verified_user=user)
        url = reverse(POST_DETAIL_URL, kwargs={"pk": post.id})
        response = api_client.delete(url)
        assert response.status_code == 204

    def test_get_current_user_posts(self, api_client, mocked_authentication):
        """Test get all posts for current user"""
        user_1 = UserFactory(
            is_verified=True,
        )
        PostFactroy.create_batch(5, author=user_1)
        user_2 = UserFactory(
            is_verified=True,
        )
        PostFactroy.create_batch(3, author=user_2)
        mocked_authentication(verified_user=user_1)
        url = reverse(CURRENT_USER_POST_URL)
        response = api_client.get(url)
        print(response.data)
        assert response.status_code == 200
        assert response.json()["total"] == 5
        assert response.json()["results"][0]["author"] == user_1.id
