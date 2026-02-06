"""
Сервіси обробки даних: парсинг/валідація файлів, завантаження в БД, агрегація.
"""
from .parsing import validate_and_parse
from .upload import process_file_upload
from .aggregation import get_aggregated_stats

__all__ = ["validate_and_parse", "process_file_upload", "get_aggregated_stats"]
