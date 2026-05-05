# TeamFinder

**TeamFinder** – это платформа, на которой разработчики, дизайнеры и другие специалисты смогут находить единомышленников для совместной работы над Pet-проектами. Зарегистрированные пользователи смогут публиковать идеи проектов, находить команду на проект и откликаться на опубликованные предложения.

В проекте реализован **вариант 2**: Навыки, фильтрация участников по навыкам

## Функциональность

- регистрация и вход по `email`
- публичные страницы пользователей
- редактирование профиля и смена пароля
- автоматическая генерация стартового аватара
- список проектов и детальные страницы проектов
- создание и редактирование проекта
- завершение проекта владельцем
- присоединение к проекту и отказ от участия
- навыки пользователей:
  - просмотр
  - добавление
  - удаление
  - автодополнение
- страница участников с фильтром по навыкам

## Стек технологий

- Python 3.14
- Django 5.2
- PostgreSQL 16
- Docker Compose
- Pillow

## Автор

Выполнил студент ННГУ группы 3822Б1ПР1 Ворошилов Виталий 

GitHub: https://github.com/vitaliyvoroshilov

## Переменные окружения в .env

Необходимо создать файл `.env` на основе `.env_example`:

- `DJANGO_SECRET_KEY` — секретный ключ Django
- `DJANGO_DEBUG` — режим отладки
- `ALLOWED_HOSTS` — список хостов через запятую
- `POSTGRES_DB` — имя базы данных PostgreSQL
- `POSTGRES_USER` — пользователь PostgreSQL
- `POSTGRES_PASSWORD` — пароль PostgreSQL
- `POSTGRES_HOST` — адрес PostgreSQL
- `POSTGRES_PORT` — порт PostgreSQL

Мной использовались значения:

```env
DJANGO_SECRET_KEY=change_for_safety
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5436
```


## Развертывание проекта

### 1. Установить зависимости

```bash
pip install -r requirements.txt
```

### 2. Поднять PostgreSQL

```bash
docker compose up -d
```

После запуска PostgreSQL будет доступен на `localhost:5436`.

Проверить контейнер:

```bash
docker compose ps
```

Остановить контейнер:

```bash
docker compose down
```

### 3. Применить миграции

```bash
python manage.py migrate
```

### 4. Запустить сервер

```bash
python manage.py runserver
```

Приложение будет доступно по адресу:

`http://127.0.0.1:8000`
