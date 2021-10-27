from livereload import Server
from server import app, login_manager

import routes
from routes import user_bp, admin_bp, api_bp, admin_api_bp

from flask_bootstrap import Bootstrap

import argparse 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-livereload", action="store_true")
    args = parser.parse_args()

    app.jinja_env.auto_reload = True

    # add blueprint for handling user and admin endpoints
    app.register_blueprint(user_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api_v1')
    app.register_blueprint(admin_api_bp, url_prefix='/admin/api_v1')

    flask_bs = Bootstrap(app)

    # handle login
    login_manager.init_app(app)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.debug = True

    if args.no_livereload:
        app.run(port=5002, debug=True)
    else:
        server = Server(app.wsgi_app)
        server.serve(port=5002, debug=True, liveport=5002)