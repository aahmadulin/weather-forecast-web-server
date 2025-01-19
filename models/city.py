from db import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from flask_login import UserMixin

class City(db.Model, UserMixin):
    __tablename__ = 'city'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    forecast = db.Column(JSON, nullable=True)  # Хранит прогноз в формате JSON
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='cities')

    def __init__(self, name, latitude, longitude, user_id):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.user_id = user_id

    def update_forecast(self, forecast_data):
        """Обновляет прогноз погоды и время обновления."""
        self.forecast = forecast_data
        self.last_updated = datetime.utcnow()

    def get_forecast_at_time(self, time, params=None):
        """Возвращает прогноз погоды на конкретное время."""
        print(f"Looking for forecast for time: {time}")  # Добавляем логирование
        if self.forecast and time in self.forecast:
            weather_data = self.forecast[time]
            print(f"Found weather data: {weather_data}")  # Логируем найденные данные
            if params:
                return {param: weather_data.get(param) for param in params}
            return weather_data
        print("No weather data found for this time.")  # Логируем, если данные не найдены
        return None

