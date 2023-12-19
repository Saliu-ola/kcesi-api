import pytest
from django.urls import reverse
from .factories import GroupFactroy
from accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

Group_LIST_URL = "group:group-list"
Group_DETAIL_URL = "group:group-detail"
CURRENT_USER_Group_URL = "group:group-get-group-for-current-user"


class TestGroup:
    def test_list_all_groups(self, api_client, mocked_admin_authentication):
        """Test list all group for all organizations by admin"""

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

        GroupFactroy.create_batch(3, organization_id=user_1.organization_id)
        GroupFactroy.create_batch(4, organization_id=user_2.organization_id)
        mocked_admin_authentication()
        url = reverse(Group_LIST_URL)
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.json()["total"] == 7

    def test_create_group(self, verified_admin_user, api_client, mocked_admin_authentication):
        """Test create group"""

        user = UserFactory.create(
            is_verified=True,
            organization_name=verified_admin_user.organization_name,
            organization_id=verified_admin_user.organization_id,
            role_id=3,
            group_id=1,
        )
        mocked_admin_authentication()
        url = reverse(Group_LIST_URL)
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

    def test_get_group(self, verified_admin_user, api_client, mocked_admin_authentication):
        """Test retrieve a Groups"""
        user = UserFactory.create(
            is_verified=True,
            organization_name=verified_admin_user.organization_name,
            organization_id=verified_admin_user.organization_id,
            role_id=3,
            group_id=1,
        )
        group = GroupFactroy(organization_id=user.organization_id)
        mocked_admin_authentication()
        url = reverse(Group_DETAIL_URL, kwargs={"pk": group.id})
        response = api_client.get(url)
        print(response.data)
        assert response.status_code == 200
        assert response.data["title"] == group.title
        assert response.data["content"] == group.content
        assert response.data["organization_id"] == user.organization_id

    @pytest.mark.parametrize("method_name", ['patch', 'put'])
    def test_update_group(
        self, api_client, verified_admin_user, method_name, mocked_admin_authentication
    ):
        """Test updating a Group"""
        user = UserFactory.create(
            is_verified=True,
            organization_id=verified_admin_user.organization_id,
            organization_name=verified_admin_user.organization_name,
            role_id=3,
            group_id=1,
        )
        group = GroupFactroy(
            organization_id=user.organization_id, title="Old title", content="Old content"
        )
        mocked_admin_authentication()
        payload = {"title": "new title", "content": "new content"}
        url = reverse(Group_DETAIL_URL, kwargs={"pk": group.id})
        response = getattr(api_client, method_name)(url, data=payload)
        group.refresh_from_db()
        assert response.status_code == 200
        assert response.json()['title'] == payload['title']
        assert group.title == payload['title']
        assert group.content == payload['content']

    def test_delete_group(self, api_client, verified_admin_user, mocked_admin_authentication):
        """Test deleting of a group"""
        user = UserFactory.create(
            is_verified=True,
            organization_id=verified_admin_user.organization_id,
            organization_name=verified_admin_user.organization_name,
            role_id=3,
            group_id=1,
        )
        group = GroupFactroy(organization_id=user.organization_id)
        mocked_admin_authentication()
        url = reverse(Group_DETAIL_URL, kwargs={"pk": group.id})
        response = api_client.delete(url)
        assert response.status_code == 204

    def test_get_current_organization_group(self, api_client, mocked_admin_authentication):
        """Test get all Groups for current user"""
        user_1 = UserFactory.create(
            is_verified=True,
            organization_name="LMONJI",
            organization_id="LMO-34785909463",
            role_id=3,
            group_id=1,
        )
        GroupFactroy.create_batch(5, organization_id=user_1.organization_id)
        user_2 = UserFactory.create(
            is_verified=True,
            organization_name="FIKJK",
            organization_id="FIK-64787374627",
            role_id=3,
            group_id=3,
        )
        GroupFactroy.create_batch(3, organization_id=user_2.organization_id)
        user_3 = UserFactory.create(
            is_verified=True,
            organization_name="REUSJ",
            organization_id="REU-99078643678",
            role_id=3,
            group_id=3,
        )
        GroupFactroy.create_batch(2, organization_id=user_3.organization_id)
        mocked_admin_authentication()
        url = reverse(Group_LIST_URL) + f'?organization_id={user_2.organization_id}'
        response = api_client.get(url)
        print(response.data)
        assert response.status_code == 200
        assert response.json()["total"] == 3
        assert response.json()["results"][0]["organization_id"] == user_2.organization_id
