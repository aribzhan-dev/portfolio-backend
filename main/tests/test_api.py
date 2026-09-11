import pytest
from django.urls import reverse

from main.models import ContactMessage

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestProfileEndpoint:
    def test_returns_profile_data(self, api_client, profile):
        # Act
        response = api_client.get(reverse('profile'))

        # Assert
        assert response.status_code == 200
        assert response.data['full_name'] == profile.full_name
        assert response.data['years_experience'] == 3

    def test_returns_404_when_profile_not_created(self, api_client):
        # Act
        response = api_client.get(reverse('profile'))

        # Assert
        assert response.status_code == 404


class TestSkillsEndpoint:
    def test_returns_categories_with_nested_skills(self, api_client, skill_category):
        # Act
        response = api_client.get(reverse('skills-list'))

        # Assert
        assert response.status_code == 200
        assert len(response.data) == 1

        category = response.data[0]
        assert category['name'] == 'Backend'
        assert [skill['name'] for skill in category['skills']] == ['Python', 'Django']

    def test_returns_empty_list_when_no_skills(self, api_client):
        # Act
        response = api_client.get(reverse('skills-list'))

        # Assert
        assert response.status_code == 200
        assert response.data == []


class TestProjectsEndpoint:
    def test_returns_all_projects(self, api_client, web_project, bot_project):
        # Act
        response = api_client.get(reverse('projects-list'))

        # Assert
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_tags_are_serialized_as_plain_names(self, api_client, web_project):
        # Act
        response = api_client.get(reverse('projects-list'))

        # Assert
        assert sorted(response.data[0]['tags']) == ['Django', 'Python']

    def test_filters_by_project_type(self, api_client, web_project, bot_project):
        # Act
        response = api_client.get(reverse('projects-list'), {'type': 'bot'})

        # Assert
        assert len(response.data) == 1
        assert response.data[0]['slug'] == bot_project.slug

    def test_filters_by_featured_flag(self, api_client, web_project, bot_project):
        # Act
        response = api_client.get(reverse('projects-list'), {'featured': 'true'})

        # Assert
        assert len(response.data) == 1
        assert response.data[0]['slug'] == web_project.slug

    def test_returns_single_project_by_slug(self, api_client, web_project):
        # Act
        response = api_client.get(reverse('projects-detail', args=[web_project.slug]))

        # Assert
        assert response.status_code == 200
        assert response.data['title'] == web_project.title

    def test_returns_404_for_unknown_slug(self, api_client):
        # Act
        response = api_client.get(reverse('projects-detail', args=['no-such-project']))

        # Assert
        assert response.status_code == 404


class TestExperienceEndpoint:
    def test_returns_experience_with_is_current_flag(self, api_client, current_job):
        # Act
        response = api_client.get(reverse('experience-list'))

        # Assert
        assert response.status_code == 200
        assert response.data[0]['is_current'] is True
        assert response.data[0]['kind'] == 'work'


class TestSocialsEndpoint:
    def test_returns_social_links(self, api_client, social_link):
        # Act
        response = api_client.get(reverse('socials-list'))

        # Assert
        assert response.status_code == 200
        assert response.data[0]['icon'] == 'github'


class TestContactEndpoint:
    VALID_PAYLOAD = {
        'name': 'Иван',
        'email': 'ivan@example.com',
        'message': 'Здравствуйте, хочу обсудить проект.',
    }

    def test_saves_message_and_returns_201(self, api_client):
        # Act
        response = api_client.post(reverse('contact'), self.VALID_PAYLOAD, format='json')

        # Assert
        assert response.status_code == 201
        assert ContactMessage.objects.count() == 1
        assert ContactMessage.objects.first().email == 'ivan@example.com'

    def test_rejects_too_short_message(self, api_client):
        # Arrange
        payload = {**self.VALID_PAYLOAD, 'message': 'Привет'}

        # Act
        response = api_client.post(reverse('contact'), payload, format='json')

        # Assert
        assert response.status_code == 400
        assert 'message' in response.data
        assert ContactMessage.objects.count() == 0

    def test_rejects_invalid_email(self, api_client):
        # Arrange
        payload = {**self.VALID_PAYLOAD, 'email': 'не-почта'}

        # Act
        response = api_client.post(reverse('contact'), payload, format='json')

        # Assert
        assert response.status_code == 400
        assert 'email' in response.data

    def test_rejects_blank_name(self, api_client):
        # Arrange
        payload = {**self.VALID_PAYLOAD, 'name': '   '}

        # Act
        response = api_client.post(reverse('contact'), payload, format='json')

        # Assert
        assert response.status_code == 400
        assert 'name' in response.data

    def test_blocks_spam_after_rate_limit_is_reached(self, api_client):
        # Arrange — limit 5/hour
        url = reverse('contact')
        for _ in range(5):
            api_client.post(url, self.VALID_PAYLOAD, format='json')

        # Act
        response = api_client.post(url, self.VALID_PAYLOAD, format='json')

        # Assert
        assert response.status_code == 429
        assert ContactMessage.objects.count() == 5
