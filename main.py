import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fetch_up_transactions(token):
    """
    Fetches transactions from the Up Bank API.

    Args:
        token: Your Up Bank Personal Access Token.

    Returns:
        A list of transaction dictionaries, or None if an error occurs.
    """
    try:
        url = "https://api.up.com.au/api/v1/transactions"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()['data']  # Extract transaction data from the response

    except requests.exceptions.RequestException as e:
        print(f"Error fetching transactions from Up Bank: {e}")
        return None



def transform_to_ynab(up_transaction, ynab_account_id):
    """
    Transforms an Up Bank transaction to the YNAB format.

    Args:
        up_transaction: A dictionary representing a transaction from the Up API.
        ynab_account_id: The ID of the account in your YNAB budget.

    Returns:
        A dictionary in the format required by the YNAB API.
    """
    amount_milliunits = int(up_transaction['attributes']['amount']['valueInBaseUnits']) * 10

    ynab_transaction = {
        "account_id": ynab_account_id,
        "date": up_transaction['attributes']['createdAt'].split('T')[0],
        "amount": amount_milliunits,
        "payee_name": up_transaction['attributes']['description'],
        "cleared": "cleared" if up_transaction['attributes']['status'] == "SETTLED" else "uncleared",
        "approved": up_transaction['attributes']['status'] == "SETTLED",
        "import_id": f"{up_transaction['id']}-{up_transaction['attributes']['createdAt']}"
    }
    return ynab_transaction


def add_to_ynab(ynab_token, budget_id, transactions):
    """Adds transactions to YNAB."""
    headers = {"Authorization": f"Bearer {ynab_token}"}
    data = {"transactions": transactions}
    response = requests.post(
        f"https://api.ynab.com/api/v1/budgets/{budget_id}/transactions",
        headers=headers,
        json=data
    )
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()  # Return the YNAB API response



if __name__ == "__main__":
    up_token = os.getenv("UP_API_TOKEN")
    ynab_token = os.getenv("YNAB_API_TOKEN")  # Get your YNAB API token
    budget_id = os.getenv("YNAB_BUDGET_ID")  # Replace with your YNAB budget ID
    if not up_token or not ynab_token or not budget_id:
        print("Environment variables not set.")
    else:
        transactions = fetch_up_transactions(up_token)
        if transactions:
            ynab_account_id = "YNAB_ACCOUNT_ID"  # Replace with your actual YNAB account ID

            for up_transaction in transactions:
                ynab_transaction = transform_to_ynab(up_transaction, ynab_account_id)

                print("Up Transaction:")
                print(f"  id: {up_transaction['id']}")
                print(f"  createdAt: {up_transaction['attributes']['createdAt']}")
                print(f"  description: {up_transaction['attributes']['description']}")
                print(f"  amount.valueInBaseUnits: {up_transaction['attributes']['amount']['valueInBaseUnits']}")
                print(f"  status: {up_transaction['attributes']['status']}")

                print("\nYNAB Transaction:")
                print(f"  account_id: {ynab_transaction['account_id']}")
                print(f"  date: {ynab_transaction['date']}")
                print(f"  amount: {ynab_transaction['amount']}")
                print(f"  payee_name: {ynab_transaction['payee_name']}")
                print(f"  cleared: {ynab_transaction['cleared']}")
                print(f"  approved: {ynab_transaction['approved']}")
                print(f"  import_id: {ynab_transaction['import_id']}")
                print("-" * 30)

                ynab_response = add_to_ynab(ynab_token, budget_id, transactions)
                print(ynab_response)  # Check the response from the YNAB API

                input()

            
