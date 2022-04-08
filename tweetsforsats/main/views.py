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

    get_invoice = request.GET.get('invoice')

    bolt11 = ""
    invoice_id = ""

    try:
        if get_invoice:
            inv = invoice()
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
    
def check_invoice(request, invoice_id):
    host = config['BTCPAY']['Url']
    token = config['BTCPAY']['Token']
    store = config['BTCPAY']['StoreId']

    headers = {'Authorization': f"token {token}"}

    r = requests.get(f"{host}/stores/{store}/lightning/BTC/invoices/{invoice_id}", headers=headers)
    
    invoice = r.json()

    status = "Unpaid"

    try:
        status = invoice['status']
    except KeyError:
        if invoice != None:
            status = "Expired"
        pass

    return JsonResponse({'status': status})