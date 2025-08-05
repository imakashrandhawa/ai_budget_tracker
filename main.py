import os
from dotenv import load_dotenv
from plaid.api import plaid_api
from plaid.model.institutions_get_request import InstitutionsGetRequest
from plaid.model.country_code import CountryCode
from plaid import Configuration, ApiClient

# Load environment variables
load_dotenv()
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = "sandbox"

# Setup Plaid configuration
configuration = Configuration(
    host="https://sandbox.plaid.com",
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
    }
)

api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Call institutions/get
request = InstitutionsGetRequest(
    count=5,
    offset=0,
    country_codes=[CountryCode('US')]
)

response = client.institutions_get(request)
for institution in response['institutions']:
    print(f"{institution['name']} - ID: {institution['institution_id']}")
