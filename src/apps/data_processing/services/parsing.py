import logging

from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from io import BytesIO

import pandas as pd

logger = logging.getLogger(__name__)

COLUMN_ALIASES = {
    "advertis": "advertiser",
    "brand": "brand",
    "start": "start",
    "end": "end",
    "format": "format",
    "platforr": "platform",
    "platform": "platform",
    "impr": "impressions",
}
REQUIRED_COLUMNS = {"start", "end"}

DATE_FORMATS = [
    "%d.%m.%y",
    "%d.%m.%Y",
    "%Y-%m-%d",
    "%d/%m/%y",
    "%d/%m/%Y",
    "%d-%m-%y",
    "%d-%m-%Y",
    "%Y.%m.%d",
    "%d %b %Y",
    "%d %B %Y",
    "%b %d, %Y",
    "%B %d, %Y",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%m.%d.%Y",
    "%m-%d-%Y",
]


def _normalize_columns(df):
    """Map dataframe columns to standard names."""
    mapping = {}
    for col in df.columns:
        key = str(col).strip().lower().replace(" ", "")
        if key in COLUMN_ALIASES:
            mapping[col] = COLUMN_ALIASES[key]
    return df.rename(columns=mapping)


def _excel_serial_to_date(n):
    """Convert Excel serial number to date."""
    try:
        days = int(round(float(n)))
        if 0 < days <= 500000:
            ts = pd.Timestamp("1899-12-30") + pd.Timedelta(days=days)
            return ts.date()
    except (ValueError, TypeError):
        pass
    return None


_EXCEL_ERROR_STRINGS = frozenset(
    s.strip().upper()
    for s in ("#N/A", "#VALUE!", "#REF!", "#DIV/0!", "#NAME?", "#NULL!", "#NUM!", "#GETTING_DATA", "-", "—")
)


def _parse_date(val):
    """Parse date from string, number (Excel serial), or datetime."""
    if pd.isna(val) or val == "" or (isinstance(val, str) and not val.strip()):
        return None
    if isinstance(val, str) and val.strip().upper() in _EXCEL_ERROR_STRINGS:
        return None
    if isinstance(val, (datetime, date)):
        return val.date() if isinstance(val, datetime) else val
    if isinstance(val, (int, float)):
        d = _excel_serial_to_date(val)
        if d is not None:
            return d
        try:
            return pd.Timestamp(val).date()
        except (ValueError, TypeError, AttributeError):
            pass
        return None

    try:
        ts = pd.Timestamp(val)
        return ts.date()
    except (ValueError, TypeError, AttributeError):
        pass
    s = str(val).strip().strip("\ufeff")
    if s.upper() in _EXCEL_ERROR_STRINGS:
        return None

    if s.isdigit() and len(s) >= 4:
        d = _excel_serial_to_date(s)
        if d is not None:
            return d
    try:
        n = float(s.replace(",", "."))
        d = _excel_serial_to_date(n)
        if d is not None:
            return d
    except (ValueError, TypeError):
        pass
    if " " in s:
        s = s.split(" ")[0].strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except (ValueError, TypeError):
            continue

    for dayfirst in (True, False):
        try:
            ts = pd.to_datetime(s, dayfirst=dayfirst, errors="coerce")
            if pd.notna(ts):
                return ts.date()
        except (ValueError, TypeError):
            continue

    try:
        ts = pd.to_datetime(val, errors="coerce")
        if pd.notna(ts):
            return ts.date()
    except (ValueError, TypeError):
        pass
    return None


def _parse_number(val):
    """Parse number with space/comma."""
    if pd.isna(val) or val == "":
        return None
    s = str(val).strip().replace(" ", "").replace(",", ".")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def validate_and_parse(file_content, filename):
    """
    Validate file and return (success, data_or_error_message, error_type, skipped_rows).
    """
    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(BytesIO(file_content), sep=None, engine="python", encoding="utf-8")
        else:
            df = pd.read_excel(BytesIO(file_content), engine="openpyxl")
    except Exception as e:
        return False, str(e), "format", []

    if df.empty or len(df) == 0:
        return False, "Файл не містить даних.", "structure", []

    df = _normalize_columns(df)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        return False, f"Відсутні обов'язкові колонки: {', '.join(missing)}.", "required_columns", []

    start_col = "start"
    end_col = "end"
    for idx, row in df.iterrows():
        if pd.isna(row.get(start_col)) or str(row.get(start_col, "")).strip() == "":
            return False, "Колонки Start та End не можуть бути порожніми. Таблиця невалідна.", "empty_dates", []
        if pd.isna(row.get(end_col)) or str(row.get(end_col, "")).strip() == "":
            return False, "Колонки Start та End не можуть бути порожніми. Таблиця невалідна.", "empty_dates", []

    rows = []
    skipped_rows = []
    for idx, row in df.iterrows():
        raw_start = row.get(start_col)
        raw_end = row.get(end_col)
        start_date = _parse_date(raw_start)
        end_date = _parse_date(raw_end)
        row_num = int(idx) + 2

        if start_date is None:
            skipped_rows.append({
                "row_num": row_num,
                "reason": "invalid_start",
                "detail": f"невалідний формат Start (значення: {raw_start!r})",
            })
            logger.warning("Пропущено рядок %s: невалідний формат Start. Файл: %s. Значення: %s", row_num, filename, raw_start)
            continue
        if end_date is None:
            skipped_rows.append({
                "row_num": row_num,
                "reason": "invalid_end",
                "detail": f"невалідний формат End (значення: {raw_end!r})",
            })
            logger.warning("Пропущено рядок %s: невалідний формат End. Файл: %s. Значення: %s", row_num, filename, raw_end)
            continue
        if start_date > end_date:
            skipped_rows.append({
                "row_num": row_num,
                "reason": "start_gt_end",
                "detail": f"Start ({start_date}) > End ({end_date})",
            })
            logger.warning(
                "Пропущено рядок %s: Start (%s) пізніше за End (%s). Файл: %s.",
                row_num, start_date, end_date, filename,
            )
            continue

        year = start_date.year
        impr = _parse_number(row.get("impressions")) if "impressions" in df.columns else None
        rows.append({
            "year": year,
            "advertiser": str(row.get("advertiser", "")).strip() if pd.notna(row.get("advertiser")) else "",
            "brand": str(row.get("brand", "")).strip() if pd.notna(row.get("brand")) else "",
            "start_date": start_date,
            "end_date": end_date,
            "format_type": str(row.get("format", "")).strip() if pd.notna(row.get("format")) else "",
            "platform": str(row.get("platform", "")).strip() if pd.notna(row.get("platform")) else "",
            "impressions": impr,
        })
    return True, rows, None, skipped_rows
