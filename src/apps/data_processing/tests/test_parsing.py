from apps.data_processing.services.parsing import validate_and_parse


class TestValidateAndParse:
    """Test validate_and_parse for different input data"""

    def test_valid_csv_returns_rows(self, csv_valid_content):
        ok, data, error_type, skipped = validate_and_parse(csv_valid_content, "data.csv")
        assert ok is True
        assert error_type is None
        assert len(data) == 2
        assert data[0]["year"] == 2021
        assert data[0]["advertiser"] == "Company A"
        assert data[0]["impressions"] == 1000
        assert data[1]["impressions"] == 2000
        assert skipped == []

    def test_empty_dates_invalid_table(self, csv_empty_dates):
        ok, msg, error_type, skipped = validate_and_parse(csv_empty_dates, "bad.csv")
        assert ok is False
        assert "Start та End не можуть бути порожніми" in msg
        assert error_type == "empty_dates"
        assert skipped == []

    def test_start_gt_end_row_skipped(self, csv_start_gt_end):
        ok, data, error_type, skipped = validate_and_parse(csv_start_gt_end, "data.csv")
        assert ok is True
        assert len(data) == 1
        assert data[0]["advertiser"] == "C"
        assert len(skipped) == 1
        assert skipped[0]["reason"] == "start_gt_end"
        assert skipped[0]["row_num"] == 2

    def test_missing_required_columns(self):
        content = b"Advertis,Brand,Format,Impr\nA,B,banner,100"
        ok, msg, error_type, skipped = validate_and_parse(content, "no_dates.csv")
        assert ok is False
        assert "обов'язкові колонки" in msg or "start" in msg.lower() or "end" in msg.lower()
        assert error_type == "required_columns"

    def test_empty_file_structure_error(self):
        content = b""
        ok, msg, error_type, skipped = validate_and_parse(content, "empty.csv")
        assert ok is False
        assert error_type in ("structure", "format")  # empty CSV can yield delimiter error

    def test_column_order_flexible(self):
        """Column order can be arbitrary (mapping by name). Day > 12 to avoid MM.DD."""
        content = b"Impr,End,Start,Brand,Advertis,Format,Platforr\n500,20.01.21,15.01.21,Y,B,ban,DV"
        ok, data, error_type, skipped = validate_and_parse(content, "reordered.csv")
        assert ok is True
        assert len(data) == 1
        assert data[0]["impressions"] == 500
        assert data[0]["year"] == 2021
        assert data[0]["advertiser"] == "B"

    def test_invalid_end_format_skipped(self):
        """Row with invalid End format is skipped, file is processed further."""
        content = b"Advertis,Brand,Start,End,Format,Platforr,Impr\nA,B,04.01.21,10.01.21,banner,DV,1\nC,D,11.01.21,not-a-date,ban,DV,2\nE,F,18.01.21,24.01.21,b,DV,3"
        ok, data, error_type, skipped = validate_and_parse(content, "mixed.csv")
        assert ok is True
        assert len(data) == 2
        assert len(skipped) == 1
        assert skipped[0]["reason"] == "invalid_end"

    def test_csv_extension_parsed(self, csv_valid_content):
        ok, data, _, _ = validate_and_parse(csv_valid_content, "file.csv")
        assert ok is True
        assert len(data) >= 1
