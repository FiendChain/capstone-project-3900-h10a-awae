from routes import app
from livereload import Server

if __name__ == "__main__":

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    server = Server(app.wsgi_app)
    server.serve(port=5002, debug=True)