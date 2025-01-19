﻿# Проект: weather-forecast-web-server

Это HTTP-сервер, предназначенный для предоставления информации о погоде с использованием асинхронного фреймворка Flask. Прогнозы погоды получаются через Open-Meteo API. Пользователи могут искать погоду в различных городах по координатам, а также добавлять города в список для отслеживания текущего прогноза.

## Используемые технологии
- **Flask** — для создания веб-приложения.
- **Flask-Login** — для аутентификации пользователей.
- **SQLAlchemy** — для работы с базой данных.
- **Werkzeug** — для хеширования паролей.
- **httpx** — для асинхронных HTTP-запросов.
- **Jinja2** — для шаблонов.
- **Open-Meteo API** — для получения данных о погоде.

## API Эндпоинты

### Пользовательские эндпоинты
- **`POST /signup`**: Регистрация нового пользователя.
- **`POST /login`**: Вход существующего пользователя.
- **`POST /logout`**: Выход из системы.

### Эндпоинты для работы с погодой
- **`POST /weather`**: Получение прогноза погоды по координатам (широта, долгота).
- **`GET /add_city`**: Добавление нового города в список для отслеживания прогноза.
- **`GET /cities`**: Получение списка городов, для которых отслеживается прогноз погоды.
- **`GET /cities/<city_id>`**: Просмотр актуального прогноза погоды для выбранного города.
- **`GET /weather_at_time`**: Получение прогноза погоды в заданный момент времени для конкретного города.

### Дополнительные эндпоинты
- **`GET /home`**: Отображение домашней страницы.
- **`GET /profile`**: Отображение профиля пользователя.
- **`GET /about`**: Отображение информации о проекте.
