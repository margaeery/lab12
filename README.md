# Лабораторная работа №12: AI-ассистированная разработка

**Студент:** Ражина Маргарита Александровна
**Группа:** 220032-11
**Вариант:** 18

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

### 4. Запуск приложения

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


2. **Задание :**  Генерация тестов


3. **Задание :** Рефакторинг «плохого» кода

 
4. **Задание :** Генерация Docker-конфигурации


5. **Задание :** Объяснение сложного кода 


6. **Задание :** Генерация документации 


7. **Задание :** Генерация миграций БД 


8. **Задание :** Поиск уязвимостей в коде


9. **Задание :** Генерация SQL-запросов


10. **Задание :** Генерация регулярного выражения


---

