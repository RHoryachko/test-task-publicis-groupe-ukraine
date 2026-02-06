from django.db.models import Sum

from ..models import DataRecord


AGGREGATED_NUMERIC_FIELDS = [
    ("impressions", "Impressions (Impr)"),
]


def get_aggregated_stats():
    """Returns context for aggregated statistics page: numeric_columns, year_stats."""
    annotate_kw = {f"total_{name}": Sum(name) for name, _ in AGGREGATED_NUMERIC_FIELDS}
    qs = (
        DataRecord.objects.filter(year__isnull=False)
        .values("year")
        .annotate(**annotate_kw)
        .order_by("year")
    )
    year_stats = []
    for r in qs:
        row = {"year": r["year"], "totals": []}
        for name, _ in AGGREGATED_NUMERIC_FIELDS:
            val = r.get(f"total_{name}")
            row["totals"].append(val if val is not None else 0)
        year_stats.append(row)
    return {
        "numeric_columns": AGGREGATED_NUMERIC_FIELDS,
        "year_stats": year_stats,
    }
