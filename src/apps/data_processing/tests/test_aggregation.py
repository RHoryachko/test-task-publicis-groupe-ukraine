import pytest

from apps.data_processing.models import DataFile, DataRecord
from apps.data_processing.services.aggregation import AGGREGATED_NUMERIC_FIELDS, get_aggregated_stats


@pytest.mark.django_db
class TestGetAggregatedStats:
    """Test get_aggregated_stats: sums by years by numeric columns."""

    def test_empty_returns_empty_lists(self):
        result = get_aggregated_stats()
        assert "numeric_columns" in result
        assert "year_stats" in result
        assert result["numeric_columns"] == AGGREGATED_NUMERIC_FIELDS
        assert result["year_stats"] == []

    def test_aggregates_by_year(self, user):
        data_file = DataFile.objects.create(
            user=user,
            filename="test.xlsx",
            status="success",
            rows_processed=3,
        )
        DataRecord.objects.bulk_create([
            DataRecord(file=data_file, year=2021, impressions=100),
            DataRecord(file=data_file, year=2021, impressions=200),
            DataRecord(file=data_file, year=2022, impressions=500),
        ])
        result = get_aggregated_stats()
        assert len(result["year_stats"]) == 2
        years = {r["year"]: r["totals"] for r in result["year_stats"]}
        assert 2021 in years
        assert 2022 in years
        assert years[2021][0] == 300
        assert years[2022][0] == 500

    def test_numeric_columns_match_aggregated_fields(self):
        result = get_aggregated_stats()
        assert len(result["numeric_columns"]) == len(AGGREGATED_NUMERIC_FIELDS)
        assert result["numeric_columns"][0][0] == "impressions"
