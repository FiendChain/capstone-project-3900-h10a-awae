def main():
    import argparse 

    parser = argparse.ArgumentParser()
    parser.add_argument("--no-livereload", action="store_true", help="Disable live reload when changes are made to server")
    parser.add_argument("--host", default="127.0.0.1", type=str, help="IP address of server")
    parser.add_argument("--server-port", default=5002, type=int, help="Port of server")
    parser.add_argument("--livereload-port", default=5003, type=int, help="Port of livereload server")
    parser.add_argument("--debug", action="store_true", help="Enable server debugging output")
    args = parser.parse_args()

    from server import app, login_manager
    import routes
    from routes import user_bp, admin_bp, api_bp, admin_api_bp

    app.jinja_env.auto_reload = not args.no_livereload

    # add blueprint for handling user and admin endpoints
    app.register_blueprint(user_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api_v1')
    app.register_blueprint(admin_api_bp, url_prefix='/admin/api_v1')

    # handle login
    login_manager.init_app(app)
    app.config['TEMPLATES_AUTO_RELOAD'] = not args.no_livereload
    app.debug = args.debug

    if args.no_livereload:
        app.run(host=args.host, port=args.port, debug=args.debug)
    else:
        from livereload import Server
        server = Server(app.wsgi_app)
        server.serve(host=args.host, port=args.server_port, debug=args.debug, liveport=args.livereload_port)

if __name__ == "__main__":
    main()