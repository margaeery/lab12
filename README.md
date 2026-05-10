# Лабораторная работа №12: AI-ассистированная разработка

**Студент:** Ражина Маргарита Александровна
**Группа:** 220032-11
**Вариант:** 18 Система управления гостиницей (Задания средней сложности)

## Выполненные задания

### Задания средней сложности:

## Инструкция по запуску Hotel Room API

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка PostgreSQL

Создайте базу данных и пользователя:

```bash
psql -U postgres
```

```sql
CREATE DATABASE hotel_db;
CREATE USER hotel_user WITH PASSWORD 'hotel_pass';
GRANT ALL PRIVILEGES ON DATABASE hotel_db TO hotel_user;
ALTER DATABASE hotel_db OWNER TO hotel_user;
\c hotel_db
GRANT ALL ON SCHEMA public TO hotel_user;
```

### 3. Настройка подключения

Скопируйте `.env.example` в `.env` и укажите актуальные параметры:

```bash
cp .env.example .env
```

Отредактируйте файл `.env`:

```
DATABASE_URL=postgresql://hotel_user:hotel_pass@localhost:5432/hotel_db
```

### 4. Запуск тестов
Тесты используют SQLite для изоляции.

```bash
pytest --cov=app --cov-report=term-missing
```

### 5. Запуск приложения

```bash
uvicorn app.main:app --reload
```

API будет доступно по адресу: `http://127.0.0.1:8000`

Интерактивная документация (Swagger UI): `http://127.0.0.1:8000/docs`

## API Endpoints

| Метод | Эндпоинт | Описание | Коды ответа |
|-------|----------|----------|-------------|
| GET | `/rooms` | Получить все номера | 200 |
| POST | `/rooms` | Создать новый номер | 201, 409 |
| GET | `/rooms/{id}` | Получить номер по ID | 200, 404 |
| PUT | `/rooms/{id}` | Обновить номер | 200, 404, 409 |
| DELETE | `/rooms/{id}` | Удалить номер | 204, 404 |

## Модель данных

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | int | Уникальный идентификатор | автоинкремент |
| room_number | str | Номер комнаты | уникальный, обязательный |
| room_type | enum | Тип номера | standard/suite/family |
| price_per_night | float | Цена за ночь | > 0 |
| floor | int | Этаж | обязательный |
| capacity | int | Вместимость | > 0 |

### 5. Примеры запросов

**Создание номера:**

```bash
curl -X POST "http://127.0.0.1:8000/rooms" \
  -H "Content-Type: application/json" \
  -d '{
    "room_number": "101",
    "room_type": "standard",
    "price_per_night": 2500.0,
    "floor": 1,
    "capacity": 2
  }'
```

**Получение списка номеров:**

```bash
curl -X GET "http://127.0.0.1:8000/rooms"
```

**Получение номера по id:**

```bash
curl -X GET "http://127.0.0.1:8000/rooms/1"
```

**Обновление номера:**

```bash
curl -X PUT "http://127.0.0.1:8000/rooms/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price_per_night": 3000.0,
    "capacity": 3
  }'
```

**Удаление номера:**

```bash
curl -X DELETE "http://127.0.0.1:8000/rooms/1"
```

### 6. Просмотр данных в базе

```bash
psql -U hotel_user -d hotel_db -h localhost
```

```sql
SELECT * FROM rooms;
```

Чтобы посмотреть структуру таблицы:

```sql
\d rooms
```

# Калькулятор стоимости проживания

Модуль для расчёта итоговой стоимости проживания в гостинице с учётом сезонного коэффициента, количества гостей, дополнительных услуг и скидок за длительность.

## Файлы

| Файл | Назначение |
|------|------------|
| `bad_calculator.py` | Исходная «плохая» версия функции `f(p, n, g, s, e)` |
| `calculator.py` | Отрефакторенная версия `calculate_total_cost(...)` |

## Использование

```python
from room_cost_calculator.calculator import calculate_total_cost, Season, ExtraService

total = calculate_total_cost(
    price_per_night=1000.0,
    nights=3,
    guests=4,
    season=Season.PEAK,
    extra_service=ExtraService.BREAKFAST,
)
```

## Параметры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `price_per_night` | `float` | Цена за одну ночь |
| `nights` | `int` | Количество ночей |
| `guests` | `int` | Количество гостей |
| `season` | `Season` | Сезон: PEAK, SHOULDER, OFF_SEASON, NORMAL |
| `extra_service` | `ExtraService \| None` | Дополнительная услуга: BREAKFAST, PARKING, SPA |

## Рефакторинг

### Исходная версия — `bad_calculator.py`

Функция `f(p, n, g, s, e)` содержала:
- неинформативные имена переменных (`p`, `n`, `g`, `s`, `e`, `r`, `c`)
- магические числа без пояснений (`1.5`, `500`, `0.95`, `100`, `0.1`, `200`)
- дублирование одних и тех же проверок (`g > 2`, `e == 1`, `s == 1`) в 3-4 местах
- мёртвый код (недостижимые `elif` из-за неверного порядка условий)
- отсутствие валидации входных данных
- побочный эффект `print()` внутри функции

### Отрефактореная версия — `calculator.py`

1. **Понятные имена**: `calculate_total_cost(price_per_night, nights, guests, season, extra_service)`
2. **Перечисления**: `Season` и `ExtraService` вместо магических чисел `1`, `2`, `3`
3. **Константы в словарях**: `SEASON_MULTIPLIERS`, `EXTRA_BASE_FEES`, `GUEST_TIERED_RATES` и др.
4. **Вспомогательные функции**: повторяющиеся блоки вынесены (`_guest_tiered_surcharge`, `_duration_discount` и др.)
5. **Исправлен порядок условий**: скидки за длительность теперь применяются корректно (>30 → >14 → >7)
6. **Валидация**: проверка на положительность параметров с `raise ValueError`
7. **Удалён print**: функция возвращает `round(total, 2)`
8. **Type hints**: все параметры и возвращаемые значения типизированы



---
 
4. **Задание :** Генерация Docker-конфигурации


5. **Задание :** Объяснение сложного кода 


6. **Задание :** Генерация документации 


7. **Задание :** Генерация миграций БД 


8. **Задание :** Поиск уязвимостей в коде


9. **Задание :** Генерация SQL-запросов


10. **Задание :** Генерация регулярного выражения


---

