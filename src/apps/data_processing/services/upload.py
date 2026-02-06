from .parsing import validate_and_parse


def process_file_upload(user, uploaded_file):
    """
    Validate file, create DataFile and DataRecord, return result for view.
    Returns: (success: bool, message: str, is_error: bool).
    """
    from ..models import DataFile, DataRecord

    filename = uploaded_file.name
    content = uploaded_file.read()
    file_size = len(content)

    ok, data_or_message, error_type, skipped_rows = validate_and_parse(content, filename)

    data_file = DataFile.objects.create(
        user=user,
        filename=filename,
        status="error" if not ok else "processing",
        file_size=file_size,
        error_type=error_type if not ok else None,
        error_message=data_or_message if not ok else None,
    )

    if not ok:
        data_file.status = "error"
        data_file.save(update_fields=["status"])
        return False, data_or_message, True

    records = [
        DataRecord(
            file=data_file,
            year=r["year"],
            advertiser=r["advertiser"] or "",
            brand=r["brand"] or "",
            start_date=r["start_date"],
            end_date=r["end_date"],
            format_type=r["format_type"] or "",
            platform=r["platform"] or "",
            impressions=r["impressions"],
        )
        for r in data_or_message
    ]
    DataRecord.objects.bulk_create(records)

    skipped_log = (
        "\n".join(f"Рядок {s['row_num']}: {s['detail']}" for s in skipped_rows)
        if skipped_rows
        else ""
    )
    data_file.status = "success"
    data_file.rows_processed = len(records)
    data_file.skipped_rows_log = skipped_log
    data_file.save(update_fields=["status", "rows_processed", "skipped_rows_log"])

    msg = f"Оброблено рядків: {len(records)}."
    if skipped_rows:
        msg += f" Пропущено рядків: {len(skipped_rows)} (див. лог в адмінці)."
    return True, msg, False
