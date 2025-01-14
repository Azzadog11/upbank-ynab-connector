import os
import requests
import datetime
import pprint
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetches transactions from a given period in json format
def fetch_up_transactions(token):
    """
    Fetches transactions from the Up Bank API of last two weeks

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
        # Calculate the start and end dates for the four-week period
        end_date = datetime.datetime.now(datetime.timezone.utc)  # Use UTC for consistency
        start_date = end_date - datetime.timedelta(weeks=4)
        print(f"Start date: {start_date.isoformat()}")
        print(f"End Date: {end_date.isoformat()}")
        # Retrieve transactions within the two-week period using both filter[since] and filter[until]
        response = requests.get(
            url=url,
            headers=headers,
            params={
                "filter[since]": start_date.isoformat(),
                "filter[until]": end_date.isoformat()
            }
        )

        response.raise_for_status()
        transactions = response.json()['data']

        # Handle pagination if there are more transactions
        while response.json()['links'].get('next'):
            next_page_url = response.json()['links']['next']
            response = requests.get(url=next_page_url, headers=headers)
            response.raise_for_status()
            transactions.extend(response.json()['data'])

        return transactions

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
        "import_id": f"{up_transaction['id']}",
        "memo": up_transaction['attributes'].get('message', '')
    }
    return ynab_transaction

def add_to_ynab(ynab_token, budget_id, ynab_transactions):
    """
    Imports a dictionary of YNAB formatted transactions into YNAB

    Args:
        ynab_token: API token for ynab taken from the .env file.
        budget_id: The ID of your YNAB budget, taken from the .env file.
        ynab_transactions: a list of formatted ynab_transactions to be imported into YNAB. (List of the return type of transform_to_ynab)

    Returns:
        Will return the reponse code / status from YNAB API.
    """
    headers = {"Authorization": f"Bearer {ynab_token}",
                 "Content-Type": "application/json",
                 "accept": "application/json"}
    
    data = {"transactions": ynab_transactions}  # Uses the transformed transactions (Not raw upbank)
    response = requests.post(
        f"https://api.ynab.com/v1/budgets/{budget_id}/transactions",
        headers=headers,
        json=data
    )
    
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()  # Return the YNAB API response

if __name__ == "__main__":
    # Gets environment variables from .env file that must be created in same directory
    up_token = os.getenv("UP_API_TOKEN")
    ynab_token = os.getenv("YNAB_API_TOKEN")
    budget_id = os.getenv("YNAB_BUDGET_ID")
    ynab_account_id = os.getenv("YNAB_ACCOUNT_ID")
    
    if not up_token or not ynab_token or not budget_id:
        print("Environment variables not set.")
    else:
        # Gets all transaction data from past 2 weeks
        transactions = fetch_up_transactions(up_token)
        if transactions:
            # Collect all settled transactions first
            settled_transactions = []
            for up_transaction in transactions:
                if up_transaction['attributes']['status'] == "SETTLED" and (up_transaction['relationships'].get('transferAccount').get('data'))==None:
                    ynab_transaction = transform_to_ynab(
                        up_transaction, ynab_account_id)
                    settled_transactions.append(ynab_transaction)

            # Import settled transactions to YNAB in a single API call
            if settled_transactions:
                ynab_response = add_to_ynab(ynab_token, budget_id,
                                            settled_transactions)
                pprint.pprint(ynab_response)
input("Press any button to exit....")