from django.shortcuts import render, redirect
from main.models import Balances, Tweet
from django.http import JsonResponse
from lnurl import encode
import requests
from main.forms import TweetForm
import tweepy
from datetime import timedelta, datetime
from tweetsforsats import config
from django.core.cache import cache
import secrets

def index(request):
    # Get the user's public key
    key = ''
    try:
        key = request.session['key']
    except KeyError:
        pass

    balances = None
    tweets = []
    if key != '':
        balances, created = Balances.objects.get_or_create(key=key, defaults={'pending': 0, 'available': 0, 'withdrawn': 0})
        # Update pending and available balances
        if balances != None:
            tweets = Tweet.objects.filter(key=key)
            delta = timedelta(days=2)
            pending = balances.pending
            available = balances.available
            for tweet in tweets:
                if datetime.now(tz=tweet.created.tzinfo) - tweet.created >= delta:
                    pending = pending - tweet.stake
                    available = available + tweet.stake
            if pending != balances.pending:
                balances.pending = pending
                balances.available = available
                balances.save()
        # Get recent tweets
        if len(tweets) > 0:
            tweets.filter(created__gte=datetime.today()).order_by('-created')

    # Should we display an invoice?
    get_invoice = request.GET.get('invoice')

    bolt11 = ""
    invoice_id = ""
    form = None

    if get_invoice:
        try:
            inv = invoice()
            bolt11 = inv['BOLT11']
            invoice_id = inv['id']
            form = TweetForm(initial={'invoice_id': invoice_id})
        except KeyError:
            pass

    # TODO: Withdraw challenge
    # Should we authorize a withdrawal?
    auth_withdrawal = request.GET.get('withdraw')

    wk1 = None
    lnurl = ""
    withdraw_url = ""

    if auth_withdrawal:
        wk1 = secrets.token_hex(32)
        cache.get_or_set(wk1, '', 120)
        lnurl = encode(f"{config.DEBUG_BASE_URL}/lnlogin/auth?tag=login&k1={wk1}&action=auth")
        withdraw_url = encode(f"{config.DEBUG_BASE_URL}/main/withdraw_request?max={balances.available}&k1={wk1}")

    context = {
        'key': key,
        'balances': balances,
        'store': config.BTCPAY_STORE_ID,
        'invoice': f"lightning:{bolt11}",
        'invoice_id': invoice_id,
        'form': form,
        'recent': tweets,
        'auth_url': lnurl,
        'withdraw_url': f"lightning:{withdraw_url}",
        'challenge': wk1
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

def withdraw_request(request):

    max = int(request.GET.get('max'))

    if max == None:
        max = 100
        
    k1 = request.GET.get('k1')
    response = {
        "tag": "withdrawRequest",
        "callback": f'{config.DEBUG_BASE_URL}/main/withdraw',
        "k1": k1,
        "defaultDescription": "Reclaiming tweet stake sats",
        "minWithdrawable": 0,
        "maxWithdrawable": max * 1000
    }
    return JsonResponse(response)

def withdraw(request):
    k1: str = request.GET.get('k1')
    pr: str = request.GET.get('pr')

    # Check k1
    k1_cache = cache.get(k1)
    key = None
    if k1_cache == None or k1_cache.find("auth") < 0:
        return JsonResponse({"status": "ERROR", "reason": "Invalid or expired challenge"})
    else:
        key = k1_cache[5:]

    if key == None or key == '':
        return JsonResponse({"status": "ERROR", "reason": "Invalid pubkey"})


    #Get config values
    host = config.BTCPAY_URL
    token = config.BTCPAY_TOKEN
    store = config.BTCPAY_STORE_ID

    lndUrl = config.LND_URL
    lndMac = config.LND_METADATA_MAC

    # Parse and Check invoice
    lnd_headers = {'Grpc-Metadata-macaroon': lndMac}

    r0 = requests.get(f"{lndUrl}/v1/payreq/{pr}", headers=lnd_headers, verify='tweetsforsats/tls.cert')

    payreq = r0.json()

    invoice_amt = int(payreq['num_satoshis'])
    balances, created = Balances.objects.get_or_create(key=key, defaults={'pending': 0, 'available': 0, 'withdrawn': 0})

    if invoice_amt > balances.available:
        return JsonResponse({"status": "ERROR", "reason": "Withdrawal amount exceeds available amount."})

    # Pay Invoice
    headers = {'Authorization': f"token {token}"}

    invoice_info = {"BOLT11": pr}

    r = requests.post(f"{host}/stores/{store}/lightning/BTC/invoices/pay", json=invoice_info, headers=headers)

    if r.status_code != 200:
        # Check for 400 error
        if r.status_code == 400:
            cache.set(k1, "Error")
            return JsonResponse({"status": "ERROR", "reason": "Could not find route"})

        # Check for 422 error
        if r.status_code == 422:
            cache.set(k1, "Error")
            return JsonResponse({"status": "ERROR", "reason": "Unable to validate request"})

        # Check for 404 error
        if r.status_code == 404:
            cache.set(k1, "Error")
            return JsonResponse({"status": "ERROR", "reason": "Lightning node config not found"})

        # Check for 503 error
        if r.status_code == 503:
            cache.set(k1, "Error")
            return JsonResponse({"status": "ERROR", "reason": "Unable to access lightning node"})

    # Update balance
    balances.available = balances.available - invoice_amt
    balances.withdrawn = balances.withdrawn + invoice_amt
    balances.save()

    cache.set(k1, "Success")

    return JsonResponse({"status": "OK"})

def withdraw_status(request, k1):
    k1_cache = cache.get(k1)

    if k1_cache == None or k1_cache == "Error":
        return JsonResponse({"status": "ERROR"})

    if k1_cache == "Success":
        cache.delete(k1)
        return JsonResponse({"status": "OK"})

    return JsonResponse({"status": "WAIT"})