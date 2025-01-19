from app import create_app
from flask_login import LoginManager
from models.user import User

app = create_app()

login_manager = LoginManager()
login_manager.login_view = 'log.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)



