# Up Bank to YNAB Transaction Importer

This script automatically imports settled transactions from your Up Bank account into your YNAB budget. Currently the script has to be run manually but can be easily scheduled with minor modifications. (I am currently too lazy)

## Features

* Fetches transactions from the past four weeks from the Up Bank using their API.
* Transforms Up Bank transactions into the YNAB API compatible format.
* Imports transactions into your specified YNAB budget and account.
* Uses environment variables for secure storage of API keys and IDs.

## Requirements

* I used python 3.13 whilst building this. I am sure anything 3.12+ should be fine.
* NOTE: The following are covered in the requirements.txt file:
	* `requests` 1.0.1
	* `python-dotenv` 2.32.3

## Setup
1. Clone this repo to a local folder on a PC with python 3.12+ installed.
2. Create a virtual environment and install requirements from requirements.txt with 'pip install -r requirements.txt'
3. Create a ".env" file in the same directory as the script. The format should be as below with your own values:
	- UP_API_TOKEN=<your_up_bank_personal_access_token>
	- YNAB_API_TOKEN=<your_ynab_api_token>
	- YNAB_BUDGET_ID=<your_ynab_budget_id>
	- YNAB_ACCOUNT_ID=<your_ynab_account_id>
4. Once this is set you should simply be able to run the main.py file and you will see your cleared transactions show in ynab near instantly.

## Things to note:
You can find your Up Bank Personal Access Token at: https://api.up.com.au/getting_started

You can find your YNAB API token via: go to "Account Settings", scroll down and navigate to "Developer Settings" section. From the Developer Settings page, click "New Token" under the Personal Access Tokens section

You can find your YNAB Budget ID and Account ID via the Swagger UI at https://api.ynab.com/v1. Just use your YNAB Personal Access Token to authenticate and then run the 
- GET /budgets (Copy the budget id) 
- GET /budgets/{budget_id}/accounts (insert the budget id into {budget_id})


This program will only import cleared transactions. That is why the retrieval is set to 4 weeks of UP transactions (I know it is excessive but meh, it helped me debug my issues once).

The program will also not handle internal UP transactions into savers. This is something I want to look into as a separate bills account feature should be on the way soon but for now it won't do it.