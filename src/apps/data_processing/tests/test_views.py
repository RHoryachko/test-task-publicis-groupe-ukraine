import pytest

from django.urls import reverse


@pytest.mark.django_db
class TestFileUploadView:

    def test_upload_requires_login(self, client):
        url = reverse("data_processing:upload")
        response = client.post(url, {})
        assert response.status_code in (302, 403)
        if response.status_code == 302:
            assert "login" in response.url

    def test_upload_valid_file_redirects_success(self, client, user, csv_valid_content):
        from django.core.files.uploadedfile import SimpleUploadedFile

        client.force_login(user)
        url = reverse("data_processing:upload")
        f = SimpleUploadedFile("valid.csv", csv_valid_content, content_type="text/csv")
        response = client.post(url, {"file": f}, follow=True)
        assert response.status_code == 200
        from apps.data_processing.models import DataFile
        assert DataFile.objects.filter(user=user, filename="valid.csv").exists()


@pytest.mark.django_db
class TestAggregatedStatsView:

    def test_stats_requires_login(self, client):
        url = reverse("data_processing:stats")
        response = client.get(url)
        assert response.status_code in (302, 403)
        if response.status_code == 302:
            assert "login" in response.url

    def test_stats_returns_200_with_context(self, client, user):
        client.force_login(user)
        url = reverse("data_processing:stats")
        response = client.get(url)
        assert response.status_code == 200
        assert "year_stats" in response.context
        assert "numeric_columns" in response.context
        html = response.content.decode("utf-8", errors="ignore")
        assert "year_stats" in str(response.context) or "Impressions" in html or "numeric" in html.lower()
