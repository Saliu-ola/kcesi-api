import pytest
from django.urls import reverse
from .factories import PostFactroy
from accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

POST_LIST_URL = "post:post-list"
POST_DETAIL_URL = "post:post-detail"
CURRENT_USER_POST_URL = "post:post-get-post-for-current-user"


class TestPost:
    def test_list_all_posts(self, api_client, mocked_admin_authentication):
        """Test list all posts for all organizations by admin"""

        user_1 = UserFactory.create(
            is_verified=True,
            organization_name="ORGPO",
            role_id=3,
            group_id=1,
        )

        user_2 = UserFactory.create(
            is_verified=True,
            role_id=3,
            organization_name="BORP",
            group_id=1,
        )

        PostFactroy.create_batch(3, organization_id=user_1.organization_id)
        PostFactroy.create_batch(4, organization_id=user_2.organization_id)
        mocked_admin_authentication()
        url = reverse(POST_LIST_URL)
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.json()["total"] == 7

    def test_create_post(self, verified_admin_user, api_client, mocked_user_authentication):
        """Test create post"""

        user = UserFactory.create(
            is_verified=True,
            organization_name=verified_admin_user.organization_name,
            organization_id=verified_admin_user.organization_id,
            role_id=3,
            group_id=1,
        )
        mocked_user_authentication()
        url = reverse(POST_LIST_URL)
        payload = {
            "title": "some title",
            "content": "Loren ipsinmsn enjjenndd",
            "organization_id": user.organization_id,
        }
        response = api_client.post(url, data=payload)
        assert response.status_code == 201
        assert response.data["title"] == payload["title"]
        assert response.data["content"] == payload["content"]
        assert response.data["organization_id"] == user.organization_id

    def test_get_post(self, verified_admin_user, api_client, mocked_user_authentication):
        """Test retrieve a posts"""
        user = UserFactory.create(
            is_verified=True,
            organization_name=verified_admin_user.organization_name,
            organization_id=verified_admin_user.organization_id,
            role_id=3,
            group_id=1,
        )
        post = PostFactroy(organization_id=user.organization_id)
        mocked_user_authentication()
        url = reverse(POST_DETAIL_URL, kwargs={"pk": post.id})
        response = api_client.get(url)
        print(response.data)
        assert response.status_code == 200
        assert response.data["title"] == post.title
        assert response.data["content"] == post.content
        assert response.data["organization_id"] == user.organization_id

    @pytest.mark.parametrize("method_name", ['patch', 'put'])
    def test_update_post(
        self, api_client, verified_admin_user, method_name, mocked_user_authentication
    ):
        """Test updating a post"""
        user = UserFactory.create(
            is_verified=True,
            organization_id=verified_admin_user.organization_id,
            organization_name=verified_admin_user.organization_name,
            role_id=3,
            group_id=1,
        )
        post = PostFactroy(
            organization_id=user.organization_id, title="Old title", content="Old content"
        )
        mocked_user_authentication()
        payload = {"title": "new title", "content": "new content"}
        url = reverse(POST_DETAIL_URL, kwargs={"pk": post.id})
        response = getattr(api_client, method_name)(url, data=payload)
        post.refresh_from_db()
        assert response.status_code == 200
        assert response.json()['title'] == payload['title']
        assert post.title == payload['title']
        assert post.content == payload['content']

    def test_delete_post(self, api_client, verified_admin_user, mocked_user_authentication):
        """Test deleting of a post"""
        user = UserFactory.create(
            is_verified=True,
            organization_id=verified_admin_user.organization_id,
            organization_name=verified_admin_user.organization_name,
            role_id=3,
            group_id=1,
        )
        post = PostFactroy(organization_id=user.organization_id)
        mocked_user_authentication()
        url = reverse(POST_DETAIL_URL, kwargs={"pk": post.id})
        response = api_client.delete(url)
        assert response.status_code == 204

    def test_get_current_organization_posts(self, api_client):
        """Test get all posts for current user"""
        user_1 = UserFactory.create(
            is_verified=True,
            organization_name="LMONJI",
            organization_id="LMO-34785909463",
            role_id=3,
            group_id=1,
        )
        PostFactroy.create_batch(5, organization_id=user_1.organization_id)
        user_2 = UserFactory.create(
            is_verified=True,
            organization_name="FIKJK",
            organization_id="FIK-64787374627",
            role_id=3,
            group_id=3,
        )
        PostFactroy.create_batch(3, organization_id=user_2.organization_id)
        user_3 = UserFactory.create(
            is_verified=True,
            organization_name="REUSJ",
            organization_id="REU-99078643678",
            role_id=3,
            group_id=3,
        )
        PostFactroy.create_batch(2, organization_id=user_3.organization_id)
        url = reverse(POST_LIST_URL) + f'?organization_id={user_2.organization_id}'
        response = api_client.get(url)
        print(response.data)
        assert response.status_code == 200
        assert response.json()["total"] == 3
        assert response.json()["results"][0]["organization_id"] == user_2.organization_id
