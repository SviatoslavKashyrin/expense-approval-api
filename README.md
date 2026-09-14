# Expense Approval API

Асинхронний REST API для управління корпоративними витратами з вбудованою рольовою моделлю та автоматичним AI-аналізом заявок на предмет порушень корпоративних політик. 

## Технологічний стек
* **Backend:** FastAPI, SQLAlchemy, Pydantic
* **База даних:** PostgreSQL
* **Брокер повідомлень:** Redis
* **Фонові завдання:** Celery
* **AI Інтеграція:** Google Gemini API (gemini-3.6-flash)

## Попередні вимоги
Для запуску проєкту на локальній машині необхідно встановити Docker та Docker Compose.

## Налаштування середовища
Створіть файл .env у кореневій директорії проєкту та скопіюйте в нього наступні налаштування конфігурації. Адреси баз даних налаштовані на внутрішні DNS-імена Docker (db та redis):

    DATABASE_URL=postgresql://postgres:postgres@db:5432/expense_db
    REDIS_URL=redis://redis:6379/0

    # Згенеруйте випадковий рядок для локального середовища
    SECRET_KEY=your_secret_key_here
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=60

    # Отримайте API ключ у Google AI Studio
    GEMINI_API_KEY=your_gemini_api_key_here
    GEMINI_MODEL=gemini-3.6-flash

    CATEGORY_APPROVERS={"Office": "approver1@example.com", "Travel": "approver2@example.com", "Client Entertainment": "approver2@example.com", "Software/Subscriptions": "approver1@example.com", "Other": "approver1@example.com"}

## Запуск проєкту

1. Збірка та запуск контейнерів:
У терміналі виконайте команду для підняття всієї інфраструктури (API, PostgreSQL, Redis, Celery Worker):

    docker compose up -d --build

2. Застосування міграцій бази даних:
Після успішного запуску контейнерів накатiть актуальну схему бази даних за допомогою Alembic:

    docker exec -it expense-approval-api-api-1 alembic upgrade head

## Використання API та документація

Після запуску інтерактивна документація Swagger UI буде доступна за адресою:
 http://localhost:8000/docs

### Основний флоу роботи:
* Реєстрація: Створіть користувачів (співробітників та модераторів) через POST /users/.
* Авторизація: Отримайте JWT-токен у POST /auth/login та авторизуйтесь у Swagger.
* Створення заявки: Відправте заявку через POST /expenses/ (доступно для співробітників).
* Модерація: Модератори можуть переглядати доступні їм заявки (GET /expenses/approvals) та приймати рішення (PATCH /expenses/{id}/review).

## AI Інтеграція (Gemini)
Проєкт використовує Celery-воркер для асинхронного аналізу заявок без блокування основного API. 
* При створенні нової заявки її статус ai_status встановлюється в pending. 
* Воркер перехоплює завдання, звертається до Gemini API та аналізує доцільність витрат.
* Результат (прапорець порушення та коментар нейромережі) автоматично зберігається в базу даних. 

Для перегляду логів роботи ШІ в реальному часі використовуйте:

    docker logs -f expense-approval-api-worker-1