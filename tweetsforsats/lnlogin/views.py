from django.shortcuts import render, redirect
from django.http import JsonResponse
from hashlib import sha256
from django.contrib.sessions.models import Session
from django.core.cache import cache
from lnurl import encode

from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
from django.contrib.sessions.models import Session

import secrets
import ecdsa

from tweetsforsats import config

# LNURL Auth - Authorize
def auth(request):
    k1 = request.GET.get('k1') # Auth challenge
    key = request.GET.get('key') # User's public key
    sig = request.GET.get('sig') # User's signature
    action = request.GET.get('action') # LNURL Auth action

    # Check k1, key, sig
    if k1 is None:
        return JsonResponse({'status': "ERROR", 'reason': "No challenge found."})

    if key is None:
        return JsonResponse({'status': "ERROR", 'reason': "No linking key found."})

    if sig is None:
        return JsonResponse({'status': "ERROR", 'reason': "No signature found."})
        
    # Check cached challenge
    cached_key = cache.get(k1)
    if cached_key is None:
        return JsonResponse({'status': "ERROR", 'reason': "Unrecognized challenge. Please scan a new qr code."})

    # Get veriying key from serialized public key
    vk = ecdsa.VerifyingKey.from_string(bytearray.fromhex(key), curve=ecdsa.SECP256k1)

    try:
        # Verify signature
        if vk.verify_digest(signature=bytearray.fromhex(sig), digest=bytearray.fromhex(k1), sigdecode=ecdsa.util.sigdecode_der):

            # Check action and save action type
            if action == "login" or action == None:
                cache.set(k1, f"login:{key}")
            if action == "auth":
                cache.set(k1, f"auth:{key}")
            if action == "link":
                cache.set(k1, f"link:{key}")
            if action == "register":
                cache.set(k1, f"register:{key}")

            return JsonResponse({'status': "OK"})
    except ecdsa.BadSignatureError as err:
        return JsonResponse({'status': "ERROR", 'reason': err.args[0]})

# Login view
def login(request):
    # Generate login challenge
    k1 = secrets.token_hex(32)

    # Cache login challenge for 2 min
    cache.get_or_set(k1, '', 120)

    url = f"{config.BASE_URL}/lnlogin/auth?tag=login&k1={k1}" # Link to lnurl auth endpoint
    lnurl = encode(url) # Encode lnurl auth endpoint

    context = {
        'lnurl': lnurl,
        'challenge': k1
    }

    return render(request, 'lnlogin/login.html', context)

# Checks if authorization challenge has been passed
def check(request):
    # Get challenge
    k1 = request.GET.get('k1')

    # Get the user's public key
    key = cache.get(k1)

    if key and key != '':
        if key.find('login') > -1: # Login?
            
            # Extract user's public key and login as a new session
            request.session['key'] = key[6:]

            # Delete cached challenge
            cache.delete(k1)

            return JsonResponse({'authenticated': True})

        elif key.find('auth') > -1: # Authorization?
            return JsonResponse({'authenticated': True, 'k1': k1})
            
    return JsonResponse({'authenticated': False})

# Logs out of session
def logout(request):
    try:
        request.session.flush()
    except:
        pass
    return redirect("main:index")