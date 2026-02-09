import pytest

from apps.data_processing.models import DataFile, DataRecord
from apps.data_processing.services.upload import process_file_upload


@pytest.mark.django_db
class TestProcessFileUpload:

    def test_success_creates_datafile_and_records(self, user, csv_valid_content):
        from django.core.files.uploadedfile import SimpleUploadedFile

        f = SimpleUploadedFile("test.csv", csv_valid_content, content_type="text/csv")
        success, msg, is_error = process_file_upload(user, f)
        assert success is True
        assert is_error is False
        assert "Оброблено рядків: 2" in msg

        assert DataFile.objects.filter(user=user, filename="test.csv").count() == 1
        data_file = DataFile.objects.get(user=user, filename="test.csv")
        assert data_file.status == "success"
        assert data_file.rows_processed == 2
        assert DataRecord.objects.filter(file=data_file).count() == 2

    def test_error_saves_datafile_with_error_status(self, user, csv_empty_dates):
        from django.core.files.uploadedfile import SimpleUploadedFile

        f = SimpleUploadedFile("bad.csv", csv_empty_dates, content_type="text/csv")
        success, msg, is_error = process_file_upload(user, f)
        assert success is False
        assert is_error is True
        assert "порожніми" in msg or "Start" in msg or "End" in msg

        data_file = DataFile.objects.get(user=user, filename="bad.csv")
        assert data_file.status == "error"
        assert data_file.error_type == "empty_dates"
        assert DataRecord.objects.filter(file=data_file).count() == 0

    def test_skipped_rows_logged_in_datafile(self, user, csv_start_gt_end):
        from django.core.files.uploadedfile import SimpleUploadedFile

        f = SimpleUploadedFile("skip.csv", csv_start_gt_end, content_type="text/csv")
        success, msg, is_error = process_file_upload(user, f)
        assert success is True
        assert "Пропущено" in msg and "1" in msg

        data_file = DataFile.objects.get(user=user, filename="skip.csv")
        assert data_file.skipped_rows_log
        assert "Start" in data_file.skipped_rows_log and "End" in data_file.skipped_rows_log
        assert DataRecord.objects.filter(file=data_file).count() == 1
