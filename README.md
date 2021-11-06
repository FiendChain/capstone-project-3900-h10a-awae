# Database code

For database system user story
Branch managed by Arthur Sze (z5165205)

## Current functionality

Start up a simple flask server connected to sqlite database and insert sample data

## Startup

1. pip install necessary packages flask, flask_login, etc
2. run python run.py
3. In browser navigate to 127.0.0.1:5002

## File info

- data folder: stores sample data (products, accounts, etc)
- db folder: database and sql schema location
- templates: store web templates in here
- classes folder: classes
- server.py: this is where the server start up code is stored (initialising database from sql schema, filling tables with sample data, etc)
- routes.py: handling routing, GET and POST requests
- run.py: execute server
