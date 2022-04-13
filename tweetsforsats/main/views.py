from django.shortcuts import render, redirect
from main.models import Balances, Tweet
from django.http import JsonResponse
from lnurl import encode
import requests
from main.forms import TweetForm
import tweepy
from tweetsforsats import config
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
        # TODO: Get recent tweets

    get_invoice = request.GET.get('invoice')

    bolt11 = ""
    invoice_id = ""

    form = None
    try:
        if get_invoice:
            inv = invoice()
            bolt11 = inv['BOLT11']
            invoice_id = inv['id']
            form = TweetForm(initial={'invoice_id': invoice_id})
    except KeyError:
        pass

    context = {
        'key': key,
        'balances': balances,
        'store': config.BTCPAY_STORE_ID,
        'invoice': f"lightning:{bolt11}",
        'invoice_id': invoice_id,
        'form': form
    }
    return render(request, 'main/index.html', context)

def invoice():
    host = config.BTCPAY_URL
    token = config.BTCPAY_TOKEN
    store = config.BTCPAY_STORE_ID

    invoice_info = {'amount': "100000", 'description': "Tweet Stake", 'expiry': 90, 'privateRouteHints': True}

    headers = {'Authorization': f"token {token}"}

    r = requests.post(f"{host}/stores/{store}/lightning/BTC/invoices", json=invoice_info, headers=headers)
    
    invoice = r.json()

    return invoice
    
def check_invoice(request, invoice_id):
    host = config.BTCPAY_URL
    token = config.BTCPAY_TOKEN
    store = config.BTCPAY_STORE_ID

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

def tweet(request):

    if request.method == 'POST':
        form = TweetForm(request.POST)

        if form.is_valid():
            key = ""
            try:
                key = request.session['key']
            except KeyError:
                pass

            if key == "":
                return redirect('main:index')

            bearerToken = config.TWITTER_BEARER_TOKEN
            accesstoken = config.TWITTER_ACCESS_TOKEN
            apikey = config.TWITTER_API_KEY
            apikeysecret = config.TWITTER_API_KEY_SECRET
            accesstokensecret = config.TWITTER_ACCESS_TOKEN_SECRET
            
            client = tweepy.Client(
                bearer_token=bearerToken, 
                access_token=accesstoken, 
                access_token_secret=accesstokensecret, 
                consumer_key=apikey, 
                consumer_secret=apikeysecret
            )

            # Check if invoice has been used already
            check_tweet = None
            invoice = ""
            try:
                invoice = form.cleaned_data['invoice_id']
                check_tweet = Tweet.objects.get(invoice_id=invoice)
            except Tweet.DoesNotExist:
                pass
            except KeyError:
                return redirect('main:index')
            
            if check_tweet == None:
                reply_url = ""
                quote_url = ""
                try:
                    reply_url = form.cleaned_data['reply_to']
                    quote_url = form.cleaned_data['quote_tweet']
                except KeyError:
                    pass
                reply_id = None
                quote_id = None
                if reply_url != "":
                    reply_id = reply_url.split("/").pop().split("?")[0]
                if quote_url != "":
                    quote_id = quote_url.split("/").pop().split("?")[0]
                    
                response = client.create_tweet(text=form.cleaned_data['text'], in_reply_to_tweet_id=reply_id, quote_tweet_id=quote_id, user_auth=True)
                try:
                    tweet_id = response.data['id']
                    new_tweet = Tweet(key=key, twitter_id=tweet_id, invoice_id=invoice)
                    new_tweet.save()

                    balance = Balances.objects.get_or_create(key=key)[0]
                    balance.pending = balance.pending + new_tweet.stake
                    balance.save()
                except KeyError:
                    return redirect('main:index')
    return redirect('main:index')