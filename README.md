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

## Setting up stripe
Stripe is being used to handle our checkout process. 

Although most of it is handled by the stripe python library, we
need to download <code>stripe.exe</code> to setup a listener for stripe's webhook. 

Webhooks are messages sent from stripe, which includes finalized payment information. To connect our flask app to the webhook, the following is required.

Before starting refer to flask_project/stripe_keys_example.py to create your flask_project/stripe_keys.py file.

1. Create an account at stripe.com.
2. Copy your developer secret key into flask_project/stripe_keys.py.

3. Download the [<code>stripe.exe</code>](https://github.com/stripe/stripe-cli/releases/download/v1.7.4/stripe_1.7.4_windows_x86_64.zip) file here.

4. Extract the <code>stripe.exe</code> file.
5. Run <code>stripe.exe login</code> and follow the steps to connect your stripe development account.
6. Run <code>stripe listen --forward-to localhost:5002/api_v1/stripe-webhook</code> to setup event forwarding from your stripe account to the local flask webhook.

7. Copy the secret webhook key from the CLI and copy it into flask_project/stripe_keys.py.

8. Now everything should be setup for stripe.