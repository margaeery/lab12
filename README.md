# Лабораторная работа №12: AI-ассистированная разработка

**Студент:** Ражина Маргарита Александровна  
**Группа:** 220032-11  
**Вариант:** 18 — Система управления гостиницей (Задания средней сложности)

## Описание проекта

REST API для управления номерами и бронированиями гостиницы, построенное на **FastAPI** с использованием **SQLAlchemy** и **PostgreSQL**. Реализованы CRUD-операции для номеров и броней, валидация данных, автоматический расчёт стоимости проживания, проверка доступности номеров на выбранные даты и миграции через Alembic.

Кроме API, проект включает модуль `room_cost_calculator` — калькулятор итоговой стоимости номера с учётом сезонных коэффициентов, количества гостей, дополнительных услуг и скидок за длительность.

---

## Стек технологий

| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.12+ | Язык программирования |
| FastAPI | 0.115.0 | Веб-фреймворк |
| Uvicorn | 0.32.0 | ASGI-сервер |
| SQLAlchemy | 2.0.36 | ORM |
| PostgreSQL | 18 | База данных |
| Pydantic | 2.9.2 | Валидация данных |
| Alembic | 1.14.0 | Миграции БД |
| Pytest | 8.3.3 | Тестирование |
| Docker | — | Контейнеризация |

---

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `DB_HOST` | Хост базы данных | `localhost` |
| `DB_PORT` | Порт PostgreSQL | `5432` |
| `DB_USER` | Имя пользователя БД | `hotel_user` |
| `DB_PASSWORD` | Пароль пользователя БД | `hotel_pass` |
| `DB_NAME` | Название базы данных | `hotel_db` |

---

## Установка и запуск

### Быстрый старт через Docker (рекомендуется)

```bash
# 1. Скопировать шаблон переменных окружения
cp .env.example .env

# 2. Запустить контейнеры
docker-compose up --build

# 3. API доступно по адресу: http://localhost:8000
#    Swagger UI: http://localhost:8000/docs
#    PostgreSQL: localhost:5432
```

Миграции Alembic применяются автоматически перед стартом приложения через `entrypoint.sh`.

**Остановка:**
```bash
docker-compose down
```

**Остановка с удалением данных:**
```bash
docker-compose down -v
```

---

### Локальный запуск (без Docker)

#### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### 2. Настройка PostgreSQL

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

#### 3. Настройка переменных окружения

```bash
cp .env.example .env
```

Отредактируйте `.env` при необходимости.

#### 4. Запуск приложения

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

---

### Запуск тестов

Тесты используют SQLite для изоляции.

```bash
pytest --cov=app --cov=room_cost_calculator --cov-report=term-missing
```

---

## API Endpoints

### Общая информация

- Базовый URL: `http://localhost:8000`
- Формат данных: JSON
- Документация: `/docs` (Swagger UI)

---

### Модель данных Room

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | `integer` | Уникальный идентификатор | автоинкремент |
| `room_number` | `string` | Номер комнаты | уникальный, обязательный |
| `room_type` | `enum` | Тип номера | `standard`, `suite`, `family` |
| `price_per_night` | `float` | Цена за ночь | `> 0` |
| `floor` | `integer` | Этаж | обязательный |
| `capacity` | `integer` | Вместимость | `> 0` |

---

### 1. Получить все номера

```http
GET /rooms
```

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/rooms" \
  -H "accept: application/json"
```

**Пример ответа (200 OK):**
```json
[
  {
    "id": 1,
    "room_number": "101",
    "room_type": "standard",
    "price_per_night": 2500.0,
    "floor": 1,
    "capacity": 2
  },
  {
    "id": 2,
    "room_number": "202",
    "room_type": "suite",
    "price_per_night": 5000.0,
    "floor": 2,
    "capacity": 4
  }
]
```

---

### 2. Создать новый номер

```http
POST /rooms
```

**Тело запроса (RoomCreate):**

| Поле | Тип | Обязательное | Ограничения |
|------|-----|-------------|-------------|
| `room_number` | `string` | да | `min_length=1`, уникальный |
| `room_type` | `enum` | да | `standard`, `suite`, `family` |
| `price_per_night` | `float` | да | `> 0` |
| `floor` | `integer` | да | — |
| `capacity` | `integer` | да | `> 0` |

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/rooms" \
  -H "Content-Type: application/json" \
  -H "accept: application/json" \
  -d '{
    "room_number": "101",
    "room_type": "standard",
    "price_per_night": 2500.0,
    "floor": 1,
    "capacity": 2
  }'
```

**Пример ответа (201 Created):**
```json
{
  "id": 1,
  "room_number": "101",
  "room_type": "standard",
  "price_per_night": 2500.0,
  "floor": 1,
  "capacity": 2
}
```

**Ошибка (409 Conflict) — номер уже существует:**
```json
{
  "detail": "Room with this room_number already exists"
}
```

**Ошибка (422 Unprocessable Entity) — невалидные данные:**
```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "price_per_night"],
      "msg": "Input should be greater than 0",
      "input": -100
    }
  ]
}
```

---

### 3. Получить номер по ID

```http
GET /rooms/{room_id}
```

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `room_id` | `integer` | ID номера |

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/rooms/1" \
  -H "accept: application/json"
```

**Пример ответа (200 OK):**
```json
{
  "id": 1,
  "room_number": "101",
  "room_type": "standard",
  "price_per_night": 2500.0,
  "floor": 1,
  "capacity": 2
}
```

**Ошибка (404 Not Found):**
```json
{
  "detail": "Room not found"
}
```

---

### 4. Обновить номер

```http
PUT /rooms/{room_id}
```

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `room_id` | `integer` | ID номера |

**Тело запроса (RoomUpdate) — все поля опциональные:**

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `room_number` | `string` | `min_length=1` |
| `room_type` | `enum` | `standard`, `suite`, `family` |
| `price_per_night` | `float` | `> 0` |
| `floor` | `integer` | — |
| `capacity` | `integer` | `> 0` |

**Пример запроса:**
```bash
curl -X PUT "http://localhost:8000/rooms/1" \
  -H "Content-Type: application/json" \
  -H "accept: application/json" \
  -d '{
    "price_per_night": 3000.0,
    "capacity": 3
  }'
```

**Пример ответа (200 OK):**
```json
{
  "id": 1,
  "room_number": "101",
  "room_type": "standard",
  "price_per_night": 3000.0,
  "floor": 1,
  "capacity": 3
}
```

**Ошибка (409 Conflict) — номер уже существует:**
```json
{
  "detail": "Room with this room_number already exists"
}
```

**Ошибка (404 Not Found):**
```json
{
  "detail": "Room not found"
}
```

---

### 5. Удалить номер

```http
DELETE /rooms/{room_id}
```

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `room_id` | `integer` | ID номера |

**Пример запроса:**
```bash
curl -X DELETE "http://localhost:8000/rooms/1"
```

**Ответ:**
- `204 No Content` — успешное удаление (тело пустое)

**Ошибка (404 Not Found):**
```json
{
  "detail": "Room not found"
}
```

---

### Модель данных Booking

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | `integer` | Уникальный идентификатор брони | автоинкремент |
| `room_id` | `integer` | ID номера | `> 0`, обязательный |
| `guest_name` | `string` | Имя гостя | `min_length=1`, обязательный |
| `guest_email` | `string` | Email гостя | `min_length=1`, обязательный |
| `guests_count` | `integer` | Количество гостей | `> 0` |
| `check_in` | `date` | Дата заезда (ISO 8601) | обязательный |
| `check_out` | `date` | Дата выезда (ISO 8601) | обязательный, должен быть после заезда |
| `season` | `enum` | Сезон | `peak`, `shoulder`, `off_season`, `normal` |
| `extra_service` | `enum \| null` | Доп. услуга | `breakfast`, `parking`, `spa` |
| `total_price` | `float` | Итоговая стоимость | рассчитывается автоматически |
| `status` | `enum` | Статус брони | `pending`, `confirmed`, `cancelled` |
| `created_at` | `datetime` | Дата создания брони | UTC |
| `room` | `RoomResponse \| null` | Данные о номере | возвращается при детальном запросе |

---

### 6. Получить все бронирования

```http
GET /bookings
```

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/bookings" \
  -H "accept: application/json"
```

**Пример ответа (200 OK):**
```json
[
  {
    "id": 1,
    "room_id": 1,
    "guest_name": "Иван Иванов",
    "guest_email": "ivan@example.com",
    "guests_count": 2,
    "check_in": "2025-07-01",
    "check_out": "2025-07-05",
    "season": "peak",
    "extra_service": "breakfast",
    "total_price": 15750.0,
    "status": "pending",
    "created_at": "2025-06-15T10:30:00",
    "room": {
      "id": 1,
      "room_number": "101",
      "room_type": "standard",
      "price_per_night": 2500.0,
      "floor": 1,
      "capacity": 2
    }
  }
]
```

---

### 7. Создать бронирование

```http
POST /bookings
```

**Тело запроса (BookingCreate):**

| Поле | Тип | Обязательное | Ограничения |
|------|-----|-------------|-------------|
| `room_id` | `integer` | да | `> 0` |
| `guest_name` | `string` | да | `min_length=1` |
| `guest_email` | `string` | да | `min_length=1` |
| `guests_count` | `integer` | да | `> 0` |
| `check_in` | `string (date)` | да | ISO 8601 |
| `check_out` | `string (date)` | да | ISO 8601, после `check_in` |
| `season` | `enum` | да | `peak`, `shoulder`, `off_season`, `normal` |
| `extra_service` | `enum \| null` | нет | `breakfast`, `parking`, `spa` |

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/bookings" \
  -H "Content-Type: application/json" \
  -H "accept: application/json" \
  -d '{
    "room_id": 1,
    "guest_name": "Иван Иванов",
    "guest_email": "ivan@example.com",
    "guests_count": 2,
    "check_in": "2025-07-01",
    "check_out": "2025-07-05",
    "season": "peak",
    "extra_service": "breakfast"
  }'
```

**Пример ответа (201 Created):**
```json
{
  "id": 1,
  "room_id": 1,
  "guest_name": "Иван Иванов",
  "guest_email": "ivan@example.com",
  "guests_count": 2,
  "check_in": "2025-07-01",
  "check_out": "2025-07-05",
  "season": "peak",
  "extra_service": "breakfast",
  "total_price": 15750.0,
  "status": "pending",
  "created_at": "2025-06-15T10:30:00",
  "room": null
}
```

**Ошибка (404 Not Found) — номер не найден:**
```json
{
  "detail": "Room not found"
}
```

**Ошибка (409 Conflict) — номер занят на выбранные даты:**
```json
{
  "detail": "Room is not available for the selected dates"
}
```

**Ошибка (422 Unprocessable Entity) — невалидные даты:**
```json
{
  "detail": "check_out must be after check_in"
}
```

**Ошибка (422 Unprocessable Entity) — превышение вместимости:**
```json
{
  "detail": "Guests count (5) exceeds room capacity (2)"
}
```

**Ошибка (422 Unprocessable Entity) — дата заезда в прошлом:**
```json
{
  "detail": "check_in must not be in the past"
}
```

---

### 8. Получить бронирование по ID

```http
GET /bookings/{booking_id}
```

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `booking_id` | `integer` | ID брони |

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/bookings/1" \
  -H "accept: application/json"
```

**Пример ответа (200 OK):**
```json
{
  "id": 1,
  "room_id": 1,
  "guest_name": "Иван Иванов",
  "guest_email": "ivan@example.com",
  "guests_count": 2,
  "check_in": "2025-07-01",
  "check_out": "2025-07-05",
  "season": "peak",
  "extra_service": "breakfast",
  "total_price": 15750.0,
  "status": "pending",
  "created_at": "2025-06-15T10:30:00",
  "room": {
    "id": 1,
    "room_number": "101",
    "room_type": "standard",
    "price_per_night": 2500.0,
    "floor": 1,
    "capacity": 2
  }
}
```

**Ошибка (404 Not Found):**
```json
{
  "detail": "Booking not found"
}
```

---

### 9. Обновить бронирование

```http
PUT /bookings/{booking_id}
```

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `booking_id` | `integer` | ID брони |

**Тело запроса (BookingUpdate) — все поля опциональные:**

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `guest_name` | `string` | `min_length=1`, `max_length=100` |
| `guest_email` | `string` | валидный email (`EmailStr`) |
| `guests_count` | `integer` | `> 0` |
| `check_in` | `string (date)` | ISO 8601 |
| `check_out` | `string (date)` | ISO 8601, после `check_in` |
| `season` | `enum` | `peak`, `shoulder`, `off_season`, `normal` |
| `status` | `enum` | `pending`, `confirmed`, `cancelled` |
| `extra_service` | `enum \| null` | `breakfast`, `parking`, `spa` |

При изменении дат, количества гостей, сезона, доп. услуг или номера стоимость пересчитывается автоматически, а доступность номера проверяется заново (с учётом текущей брони).

**Пример запроса:**
```bash
curl -X PUT "http://localhost:8000/bookings/1" \
  -H "Content-Type: application/json" \
  -H "accept: application/json" \
  -d '{
    "guest_name": "Иван Петров",
    "guests_count": 2,
    "status": "confirmed"
  }'
```

**Пример ответа (200 OK):**
```json
{
  "id": 1,
  "room_id": 1,
  "guest_name": "Иван Петров",
  "guest_email": "ivan@example.com",
  "guests_count": 2,
    "check_in": "2025-07-01",
  "check_out": "2025-07-05",
  "season": "peak",
  "extra_service": "breakfast",
  "total_price": 16500.0,
  "status": "confirmed",
  "created_at": "2025-06-15T10:30:00",
  "room": null
}
```

**Ошибка (404 Not Found):**
```json
{
  "detail": "Booking not found"
}
```

**Ошибка (409 Conflict) — номер занят на новые даты:**
```json
{
  "detail": "Room is not available for the selected dates"
}
```

**Ошибка (422 Unprocessable Entity):**
```json
{
  "detail": "check_out must be after check_in"
}
```

---

### 10. Удалить бронирование

```http
DELETE /bookings/{booking_id}
```

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `booking_id` | `integer` | ID брони |

**Пример запроса:**
```bash
curl -X DELETE "http://localhost:8000/bookings/1"
```

**Ответ:**
- `204 No Content` — успешное удаление (тело пустое)

**Ошибка (404 Not Found):**
```json
{
  "detail": "Booking not found"
}
```

---

### Сводная таблица эндпоинтов

| Метод | Эндпоинт | Описание | Коды ответа |
|-------|----------|----------|-------------|
| `GET` | `/rooms` | Получить все номера | 200 |
| `POST` | `/rooms` | Создать новый номер | 201, 409, 422 |
| `GET` | `/rooms/{id}` | Получить номер по ID | 200, 404 |
| `PUT` | `/rooms/{id}` | Обновить номер | 200, 404, 409, 422 |
| `DELETE` | `/rooms/{id}` | Удалить номер | 204, 404 |
| `GET` | `/bookings` | Получить все бронирования | 200 |
| `POST` | `/bookings` | Создать бронирование | 201, 404, 409, 422 |
| `GET` | `/bookings/{id}` | Получить бронирование по ID | 200, 404 |
| `PUT` | `/bookings/{id}` | Обновить бронирование | 200, 404, 409, 422 |
| `DELETE` | `/bookings/{id}` | Удалить бронирование | 204, 404 |

---

## Калькулятор стоимости проживания

Модуль `room_cost_calculator` рассчитывает итоговую стоимость номера с учётом множества факторов.

### Использование

```python
from room_cost_calculator.calculator import calculate_total_cost, Season, ExtraService

total = calculate_total_cost(
    price_per_night=2500.0,
    nights=10,
    guests=4,
    season=Season.PEAK,
    extra_service=ExtraService.BREAKFAST,
)
```

### Параметры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `price_per_night` | `float` | Цена за одну ночь |
| `nights` | `int` | Количество ночей |
| `guests` | `int` | Количество гостей |
| `season` | `Season` | Сезон: `PEAK`, `SHOULDER`, `OFF_SEASON`, `NORMAL` |
| `extra_service` | `ExtraService \| None` | Доп. услуга: `BREAKFAST`, `PARKING`, `SPA` |

### Сезонные коэффициенты

| Сезон | Множитель | Налог |
|-------|-----------|-------|
| `PEAK` | 1.5 | 10% |
| `SHOULDER` | 1.2 | 5% |
| `OFF_SEASON` | 0.8 | 0% |
| `NORMAL` | 1.0 | 0% |

---

## Рефакторинг калькулятора

### Исходная версия — `bad_calculator.py`

Функция `f(p, n, g, s, e)` содержала:
- неинформативные имена переменных (`p`, `n`, `g`, `s`, `e`)
- магические числа без пояснений (`1.5`, `500`, `0.95`)
- дублирование проверок (`g > 2`, `e == 1`) в нескольких местах
- отсутствие валидации входных данных
- побочный эффект `print()` внутри функции

### Отрефакторенная версия — `calculator.py`

- Понятные имена: `calculate_total_cost(price_per_night, nights, guests, ...)`
- Перечисления: `Season` и `ExtraService`
- Константы в словарях: `SEASON_MULTIPLIERS`, `EXTRA_BASE_FEES` и др.
- Вспомогательные функции: `_guest_tiered_surcharge`, `_duration_discount` и др.
- Валидация: проверка на положительность параметров
- Удалён `print`, функция возвращает `round(total, 2)`
- Type hints для всех параметров

---

## Меры безопасности (Security Audit)

В ходе аудита внесены следующие улучшения:

| Улучшение | Описание |
|-----------|----------|
| Валидация email | `guest_email` — `EmailStr`, строгая проверка формата |
| Ограничение длины | `room_number` ≤ 20, `guest_name` ≤ 100 символов |
| Положительные числа | `floor` > 0, `price_per_night` > 0, `capacity` > 0 |
| Проверка вместимости | `guests_count` не может превышать `room.capacity` |
| Запрет прошедших дат | `check_in` должен быть ≥ сегодняшней даты |
| CORS | Разрешены только `localhost:3000` и `127.0.0.1:3000` |
| Убран `print()` | Из `bad_calculator.py` удалён побочный эффект вывода в stdout |

---

## Валидатор номера договора бронирования

Модуль `contract_validator.py` проверяет формат номера договора.

**Формат:** `XX-123456.YYYY`
- 2 заглавные латинские буквы (серия)
- дефис
- ровно 6 цифр (номер)
- точка
- год от 2024 до 2035

**Примеры:**

| Значение | Результат |
|----------|-----------|
| `HB-123456.2025` | ✅ Валидно |
| `hb-123456.2025` | ❌ Невалидно (строчные буквы) |
| `HB-12345.2025` | ❌ Невалидно (5 цифр вместо 6) |
| `HB-123456.2036` | ❌ Невалидно (год вне диапазона) |

**Использование:**

```python
from contract_validator import is_valid_contract

is_valid_contract('HB-123456.2025')  # True
is_valid_contract('hb-123456.2025')  # False
```

---

## Аналитический SQL-запрос

Файл `SQLquery.md` содержит запрос для отчёта **«Топ-5 номеров по выручке за последние 30 дней»** среди подтверждённых бронирований.

**Выходные поля:**
- `room_number` — номер комнаты
- `room_type` — тип номера
- `total_revenue` — общая выручка
- `booking_count` — количество бронирований

```sql
SELECT
    r.room_number,
    r.room_type,
    SUM(b.total_price) AS total_revenue,
    COUNT(*) AS booking_count
FROM rooms r
INNER JOIN bookings b ON r.id = b.room_id
WHERE b.status = 'confirmed'
  AND b.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY r.id, r.room_number, r.room_type
ORDER BY total_revenue DESC
LIMIT 5;
```

---

## Структура проекта

```
lab12/
├── app/
│   ├── __init__.py
│   ├── database.py          # Подключение к БД
│   ├── enums.py             # Перечисления (RoomType, BookingStatus)
│   ├── main.py              # FastAPI приложение и эндпоинты
│   ├── models.py            # SQLAlchemy модели (Room, Booking)
│   └── schemas.py           # Pydantic схемы
├── room_cost_calculator/
│   ├── __init__.py
│   ├── bad_calculator.py    # Исходная "плохая" версия
│   └── calculator.py        # Отрефакторенная версия
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Фикстуры pytest
│   ├── test_booking.py      # Тесты API бронирований
│   ├── test_calculator.py   # Тесты калькулятора
│   ├── test_contract_validator.py  # Тесты валидатора договора
│   └── test_main.py         # Тесты API номеров
├── alembic/                 # Миграции БД
├── .env.example             # Шаблон переменных окружения
├── contract_validator.py    # Валидатор номера договора
├── docker-compose.yml       # Docker Compose
├── Dockerfile               # Образ приложения
├── entrypoint.sh            # Скрипт запуска
├── explanation.md           # Объяснение бизнес-логики
├── PROMPT_LOG.md            # Лог промптов
├── requirements.txt         # Зависимости Python
├── SQLquery.md              # Аналитический SQL-запрос
├── vulnerabilities.md       # Отчёт security audit
└── README.md                # Документация
```