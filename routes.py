from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from models.user import User
from models.city import City
from weather_service import fetch_weather
from db import db
from datetime import datetime
import httpx


routes = Blueprint('routes', __name__)

@routes.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@routes.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    users = User.query.all()
    if current_user.is_authenticated:
        return render_template('homepage.html', users=users)
    else:
        return redirect(url_for('log.login'))


@routes.route('/about')
@login_required
def about():
    return render_template('about.html')


@routes.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


# Прогноз погоды по координатам. Есть возможность выбора параметров
@routes.route('/weather', methods=['GET', 'POST'])
@login_required
def get_weather_by_coords():
    forecast_data = None
    current_weather = None

    if request.method == 'POST':
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        params = request.form.get('params', default="temperature_2m,wind_speed_10m,pressure_msl", type=str)
        
        if latitude is None or longitude is None:
            return jsonify({"error": "Latitude and Longitude are required"}), 400
        
        try:
            forecast_data = fetch_weather(
                latitude, 
                longitude, 
                current="temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,pressure_msl", 
                hourly="precipitation")
            
            current_weather = {
                "temperature_2m": forecast_data['current']['temperature_2m'],
                "relative_humidity_2m": forecast_data['current']['relative_humidity_2m'],
                "precipitation": forecast_data['current']['precipitation'],
                "wind_speed_10m": forecast_data['current']['wind_speed_10m'],
                "pressure_msl": forecast_data['current']['pressure_msl']
            }

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template('weather.html', current_weather=current_weather)


# Добавить город, в котором будет отслеживаться текущий прогноз погоды
@routes.route('/add_city', methods=['GET', 'POST'])
@login_required
def add_city():
    if request.method == 'POST':
        name = request.form.get('name')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        if not name or not latitude or not longitude:
            return jsonify({"error": "All fields are required"}), 400

        new_city = City(name=name, latitude=latitude, longitude=longitude, user_id=current_user.id)
        db.session.add(new_city)
        db.session.commit()

        current_weather_data = fetch_weather(
            latitude, 
            longitude, 
            current="temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,pressure_msl")
        new_city.forecast = current_weather_data
        db.session.commit()
        cities = City.query.filter_by(user_id=current_user.id).all()
        return render_template('list_of_cities.html', cities=cities)
    return render_template('add_city.html')


# Список городов, в которых отслеживается прогноз погоды
@routes.route('/cities', methods=['GET'])
@login_required
def get_cities():
    if request.method == 'GET':
        cities = City.query.filter_by(user_id=current_user.id).all()
        cities_with_forecast = [city for city in cities if city.forecast]
        return render_template('list_of_cities.html', cities=cities_with_forecast)


# "Карточка" города, где прописан актуальный прогноз погоды
@routes.route('/cities/<int:city_id>', methods=['GET'])
@login_required
def city_weather(city_id):
    city = City.query.get_or_404(city_id)

    if not city.forecast:
        return jsonify({"error": "No forecast data available for this city"}), 404

    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    # Функция отладки времени
    def parse_time(time_str):
        try:
            return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return datetime.strptime(time_str + ':00', '%Y-%m-%dT%H:%M:%S')

    closest_time = min(city.forecast['hourly']['time'], key=lambda t: abs(parse_time(t) - parse_time(current_time)))

    forecast_data = fetch_weather(
        city.latitude, 
        city.longitude, 
        current="temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,pressure_msl", 
        hourly="precipitation")

    current_weather = {
        "time": closest_time,
        "temperature_2m": forecast_data['current']['temperature_2m'],
        "relative_humidity_2m": forecast_data['current']['relative_humidity_2m'],
        "precipitation": forecast_data['current']['precipitation'],
        "wind_speed_10m": forecast_data['current']['wind_speed_10m'],
        "pressure_msl": forecast_data['current']['pressure_msl']
    }

    if current_weather:
        return render_template('city_weather.html', city=city, current_weather=current_weather)
    else:
        return jsonify({"error": "Weather data not available for this city"}), 404


# Функиция поиска координат города
def get_city_coordinates(city_name):
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=ru"
    response = httpx.get(geocode_url)
    data = response.json()
    if data['results']:
        latitude = data['results'][0]['latitude']
        longitude = data['results'][0]['longitude']
        return latitude, longitude
    return None


# Прогноз погоды в конкретном городе, в конкретное время
@routes.route('/weather_at_time', methods=['GET'])
@login_required
def get_weather_at_time():
    city_name = request.args.get('city_name')
    time_str = request.args.get('time')
    params = request.args.getlist('params') or ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"]

    # Обработка ошибки введенного времени 
    if time_str:
        try:
            user_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        except ValueError:
            return render_template(
                'weather_at_time.html', 
                city_name=city_name, 
                time=time_str, 
                params=params, 
                error_message="Неверный формат времени. Используйте 'YYYY-MM-DD HH:MM'.")
    else:
        return render_template(
            'weather_at_time.html', 
            city_name=city_name, 
            params=params, 
            error_message="Время не указано.")
    
    coordinates = get_city_coordinates(city_name)

    if not coordinates:
        return render_template(
            'weather_at_time.html', 
            city_name=city_name, 
            time=time_str, 
            params=params, 
            error_message="Город не найден.")
    
    latitude, longitude = coordinates

    weather_data = fetch_weather(latitude, longitude, current=params, hourly=params)

    try:
        user_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
    except ValueError:
        return render_template(
            'weather_at_time.html', 
            city_name=city_name, 
            time=time_str, 
            params=params, 
            error_message="Неверный формат времени. Используйте 'YYYY-MM-DD HH:MM'.")

    available_times = weather_data['hourly']['time']
    available_times_parsed = [datetime.strptime(t, '%Y-%m-%dT%H:%M') for t in available_times]
    closest_time = min(available_times_parsed, key=lambda t: abs(t - user_time))
    closest_time_index = available_times_parsed.index(closest_time)
    closest_weather_data = {param: weather_data['hourly'][param][closest_time_index] for param in params}

    if closest_weather_data:
        return render_template(
            'weather_at_time.html', 
            city_name=city_name, 
            time=user_time.strftime('%Y-%m-%d %H:%M'), 
            params=params, 
            weather_data=closest_weather_data)
    else:
        return render_template(
            'weather_at_time.html', 
            city_name=city_name, 
            time=user_time.strftime('%Y-%m-%d %H:%M'), 
            params=params, 
            error_message="Ошибка при получении данных о погоде.")
