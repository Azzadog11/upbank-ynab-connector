# Up Bank to YNAB Transaction Importer

This script automatically imports settled transactions from your Up Bank account into your YNAB budget. Currently the script has to be run manually but can be easily scheduled using docker etc.

## Features

* Fetches transactions from the past two weeks from the Up Bank API.
* Transforms Up Bank transactions into the YNAB API format.
* Imports transactions into your specified YNAB budget and account.
* Uses environment variables for secure storage of API keys and IDs.

## Requirements

* I used python 3.13 whilst building this. I am sure anything 3.12+ should be fine.
* NOTE: The following are covered in the requirements.txt file:
	* `requests` 1.0.1
	* `python-dotenv` 2.32.3

## Setup
1. Create a virtual environment and install requirements from requirements.txt
2. Create a .env file in the same directory as the script:
	- UP_API_TOKEN=<your_up_bank_personal_access_token>
	- YNAB_API_TOKEN=<your_ynab_api_token>
	- YNAB_BUDGET_ID=<your_ynab_budget_id>
	- YNAB_ACCOUNT_ID=<your_ynab_account_id> 

You can find your Up Bank Personal Access Token at: https://api.up.com.au/getting_started

You can find your YNAB API token via: go to "Account Settings", scroll down and navigate to "Developer Settings" section. From the Developer Settings page, click "New Token" under the Personal Access Tokens section

You can find your YNAB Budget ID and Account ID via the Swagger UI at https://api.ynab.com/v1. Just use your YNAB PAT to authenticate and then run the GET /budgets and GET /budgets/{budget_id}/accounts
