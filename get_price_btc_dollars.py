import requests
from decimal import Decimal

RATE_ERROR = '0.98'
FEE = 14000

def get_course_in_dollars():
    bitcoin_api_url = 'https://blockchain.info/ticker'
    response = requests.get(bitcoin_api_url)
    response_json = response.json()
    return float(Decimal(response_json['USD']['sell']) * Decimal(RATE_ERROR))

def convert_dollars_in_btc(value):
    url = 'https://blockchain.info/tobtc?currency=USD&value=%(value)s' % {'value': value}
    response = requests.get(url)
    return response.text
