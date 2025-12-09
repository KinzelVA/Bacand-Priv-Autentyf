# EM Auth Test — система аутентификации и авторизации

Учебный backend-проект: собственная система аутентификации и авторизации
с роль-based доступом к бизнес-объектам.

Стек:
- Python, Django, Django REST Framework
- JWT (PyJWT)
- БД: PostgreSQL или SQLite (для локального запуска достаточно SQLite)

---

## Архитектура

### 1. Пользователи и аутентификация

**Модель пользователя**: `accounts.User` (наследник `AbstractUser`)

Поля (основные):
- `email` — уникальный логин
- `first_name`, `last_name`, `middle_name` — ФИО
- `is_active` — мягкое удаление пользователя (деактивация)

Особенности:
- Логин происходит по `email` (`USERNAME_FIELD = "email"`)
- Пароль хранится в хэшированном виде (стандартный механизм Django)

**JWT-сессии**: `accounts.AuthToken`  
Отдельная таблица для управления жизненным циклом токенов.

Поля:
- `user` — ссылка на пользователя
- `jti` — UUID токена
- `created_at`
- `expires_at`
- `is_revoked` — токен отозван (logout / деактивация пользователя)

JWT содержит:
- `sub` — id пользователя
- `jti` — идентификатор записи в `AuthToken`
- `exp` — время истечения

Генерация / декодирование — в `accounts/utils.py`.

**Кастомный класс аутентификации**:  
`accounts.authentication.JWTAuthentication`

Работает по заголовку:

```http
Authorization: Bearer <access_token>

Локальный запуск
python -m venv .venv
.\.venv\Scripts\activate  # Windows

pip install -r requirements.txt   # или pip install django djangorestframework PyJWT psycopg2-binary

python manage.py migrate
python manage.py createsuperuser

python manage.py runserver
