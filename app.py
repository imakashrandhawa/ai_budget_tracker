import os
from flask import Flask, jsonify, send_from_directory, request
from dotenv import load_dotenv
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_account_filters import LinkTokenAccountFilters
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
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

@app.route("/api/exchange_public_token", methods=["POST"])
def exchange_public_token():
    data = request.get_json()
    public_token = data.get("public_token")

    request_body = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request_body)

    access_token = response['access_token']
    item_id = response['item_id']

    print("Access Token:", access_token)  # You’ll store this securely later
    print("Item ID:", item_id)

    return jsonify({
        "access_token": access_token,
        "item_id": item_id
    })

if __name__ == "__main__":
    app.run(debug=True)
