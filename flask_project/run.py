from livereload import Server
from server import app, login_manager
from routes import user_bp, admin_bp, api_bp
import flask_db
from flask_bootstrap import Bootstrap

if __name__ == "__main__":
    app.jinja_env.auto_reload = True

    # add blueprint for handling user and admin endpoints
    app.register_blueprint(user_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api_v1')

    flask_bs = Bootstrap(app)

    # handle login
    login_manager.init_app(app)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.debug = True

    server = Server(app.wsgi_app)
    server.serve(port=5002, debug=True, liveport=5003)