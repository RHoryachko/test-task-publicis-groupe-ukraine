# Data Processing — прийом даних та агрегована статистика

Django-додаток для прийому xls/csv файлів за шаблоном, валідації, збереження в БД та виведення агрегованих результатів по роках.

## Можливості

- **Завантаження файлів** — прийом xls/csv з колонками: Advertis, Brand, Start, End, Format, Platform, Impr. Підтримується довільний порядок колонок (маппінг по назвах).
- **Валідація** — перевірка обов’язкових колонок Start/End, форматів дат (різні формати та Excel-серійні числа), порожні значення. Рядки з невалідними датами або де Start > End пропускаються та пишуться в лог (в адмінці).
- **Агреговані результати** — сторінка з таблицею сумарних значень по роках по числовим колонкам (Impressions).
- **Два рівні доступу** — звичайний користувач (завантаження + статистика) та адмін (доступ до Django Admin).

## Стек

- Python 3.12, Django 5, Django REST Framework, JWT (drf-spectacular)
- Pandas, openpyxl — парсинг xls/csv
- Bootstrap 5, SQLite (або інша БД за налаштуванням)

## Швидкий старт (Docker)

```bash
# Клонувати репо
git clone <repo-url>
cd test-task-publicis-groupe-ukraine

# Запустити
docker compose up --build
```

Додаток буде доступний на **http://localhost:8000**.

- Логін: створіть суперюзера в контейнері:
  ```bash
  docker compose run --rm web python manage.py createsuperuser
  ```
- Або використайте production-сідер (див. нижче).

## Локальний запуск (без Docker)

```bash
cd src
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

Опційно скопіюйте `.env.example` у `.env` та задайте `SECRET_KEY`, `DEBUG` тощо.

## Тести

```bash
cd src
export DJANGO_SETTINGS_MODULE=core.settings
pip install -r ../requirements.txt
python -m pytest apps/data_processing/tests/ -v
```

Або через Docker:

```bash
docker compose run --rm -e DJANGO_SETTINGS_MODULE=core.settings web sh -c "pip install -q pytest pytest-django && python -m pytest apps/data_processing/tests/ -v"
```


## Структура проєкту

- `src/core/` — налаштування Django, urls
- `src/apps/users/` — логін, dashboard, seed-команда
- `src/apps/data_processing/` — завантаження файлів, валідація (services: parsing, upload, aggregation), views, адмінка
- `src/templates/` — базовий шаблон, сторінки логіну, дашборду та агрегованої статистики

## Ліцензія

Проєкт створено як тестове завдання.
