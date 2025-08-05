import os
from flask import Flask, jsonify, send_from_directory, request
from dotenv import load_dotenv
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid import Configuration, ApiClient
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from datetime import datetime, timedelta

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

@app.route("/api/transactions", methods=["POST"])
def get_transactions():
    data = request.get_json()
    access_token = data.get("access_token")

    # Set the date range (last 30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    request_body = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        options=TransactionsGetRequestOptions(count=10, offset=0)
    )

    response = client.transactions_get(request_body)
    transactions = response['transactions']
    transactions_data = [txn.to_dict() for txn in transactions]

    # Analyze spend by category
    category_summary = {}
    for txn in transactions_data:
        categories = txn.get('category', ['Uncategorized'])
        top_category = categories[0] if categories else 'Uncategorized'
        amount = txn['amount']
        category_summary[top_category] = category_summary.get(top_category, 0) + amount
    print([txn.get('category') for txn in transactions_data])

    return jsonify({
        "transactions": transactions_data,
        "summary": category_summary
    })

if __name__ == "__main__":
    app.run(debug=True)
