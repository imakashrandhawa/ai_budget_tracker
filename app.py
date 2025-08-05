import os
from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_account_filters import LinkTokenAccountFilters
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid import Configuration, ApiClient

# Load .env variables
load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = "sandbox"

# Flask setup
app = Flask(__name__)

# Plaid client setup
configuration = Configuration(
    host="https://sandbox.plaid.com",
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
    }
)
api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

@app.route("/api/create_link_token", methods=["GET"])
def create_link_token():
    request = LinkTokenCreateRequest(
        products=[Products("transactions")],
        client_name="AI Budget Advisor",
        country_codes=[CountryCode("US")],
        language="en",
        user=LinkTokenCreateRequestUser(
            client_user_id="unique_user_id"
        )
    )
    response = client.link_token_create(request)
    return jsonify(response.to_dict())

@app.route("/", methods=["GET"])
def serve_frontend():
    return send_from_directory("frontend", "index.html")

if __name__ == "__main__":
    app.run(debug=True)
