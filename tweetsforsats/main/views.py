from django.shortcuts import render
from main.models import Balances, Tweet
from django.http import JsonResponse
import configparser
from django.conf import settings
from lnurl import encode
import requests

config = configparser.ConfigParser()
config.read('tweetsforsats/my_settings.ini')

# Create your views here.
def index(request):
    key = ''
    try:
        key = request.session['key']
    except KeyError:
        pass

    balances = None
    if key != '':
        balances, created = Balances.objects.get_or_create(key=key, defaults={'pending': 0, 'available': 0, 'withdrawn': 0})

    inv = invoice()

    bolt11 = ""
    invoice_id = ""

    try:
        bolt11 = inv['BOLT11']
        invoice_id = inv['id']
    except KeyError:
        pass

    context = {
        'key': key,
        'balances': balances,
        'store': config['BTCPAY']['StoreId'],
        'invoice': f"lightning:{bolt11}",
        'invoice_id': invoice_id
    }
    return render(request, 'main/index.html', context)

def invoice():
    host = config['BTCPAY']['Url']
    token = config['BTCPAY']['Token']
    store = config['BTCPAY']['StoreId']

    invoice_info = {'amount': "100000", 'description': "Tweet Stake", 'expiry': 90, 'privateRouteHints': True}

    headers = {'Authorization': f"token {token}"}

    r = requests.post(f"{host}/stores/{store}/lightning/BTC/invoices", json=invoice_info, headers=headers)
    
    invoice = r.json()

    return invoice
    
def check_invoice(request, id):
    host = config['BTCPAY']['Url']
    token = config['BTCPAY']['Token']
    store = config['BTCPAY']['StoreId']

    headers = {'Authorization': f"token {token}"}

    r = requests.get(f"{host}/stores/{store}/lightning/BTC/invoices/{id}", headers=headers)
    
    invoice = r.json()

    status = "Unpaid"

    try:
        status = invoice['status']
    except KeyError:
        pass

    return JsonResponse({'status': status})